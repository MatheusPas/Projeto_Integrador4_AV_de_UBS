"""Fluxo de uma pergunta: triagem -> busca -> LLM.

O LLM só é chamado quando a triagem libera a resposta e a busca encontra
trechos na base. Encaminhamento e fora do escopo têm resposta fixa, sem
passar pelo modelo (a decisão de segurança não depende do LLM).
"""
import time

from backend.app import llm, prompts, rag, triagem

AVISO = ("⚠️ Esta resposta é apenas informativa e não substitui orientação médica "
         "ou farmacêutica.")

MSG_ENCAMINHAR = ("Essa dúvida precisa ser avaliada por um profissional de saúde. Procure a sua "
                  "UBS ou converse com o médico ou farmacêutico antes de tomar, parar ou mudar "
                  "qualquer remédio. Em caso de urgência (dor no peito, falta de ar, desmaio, "
                  "alergia grave ou dose a mais), ligue para o SAMU: 192.")
MSG_FORA_ESCOPO = ("Só consigo ajudar com dúvidas sobre os medicamentos da atenção básica "
                   "e sobre as UBS de Vitória.")
MSG_SEM_FONTE = ("A fonte que eu uso (bulas oficiais e dados das UBS de Vitória) não cobre "
                 "essa dúvida. Pergunte ao farmacêutico da sua UBS.")


def _medicamentos(receita: dict | None) -> list[dict]:
    return (receita or {}).get("medicamentos") or []


def _montar_pergunta(pergunta: str, trechos: list[dict], receita: dict | None) -> str:
    partes = [f"Pergunta do usuário: {pergunta}"]
    meds = _medicamentos(receita)
    if meds:
        partes.append("Receita do usuário:\n" + "\n".join(
            f"- {m.get('nome', '')}: {m.get('posologia', '')}" for m in meds))
    partes.append("Trechos da base (use só estes):\n" + "\n\n".join(
        f"[{i}] {t['texto']}\nFonte: {t['fonte']}" for i, t in enumerate(trechos, 1)))
    return "\n\n".join(partes)


def responder(pergunta: str, receita: dict | None = None) -> dict:
    """-> {"resposta", "categoria", "fontes", "tokens", "latencia_ms"}"""
    inicio = time.perf_counter()
    categoria = triagem.classificar(pergunta, receita)["categoria"]
    texto, fontes, tokens = None, [], 0

    if categoria == "encaminhar":
        texto = MSG_ENCAMINHAR
    elif categoria == "fora_escopo":
        texto = MSG_FORA_ESCOPO
    else:
        # a receita só entra na resposta quando a triagem viu que a pergunta é sobre ela
        receita_usada = receita if categoria == "responder_personalizado" else None
        trechos = rag.buscar(pergunta)
        nomes = [m.get("nome", "").lower() for m in _medicamentos(receita_usada)]
        if nomes and not any(t["medicamento"] and t["medicamento"] in n
                             for t in trechos for n in nomes):
            # "esqueci de tomar meu remédio" não cita o nome; o nome vem da receita
            trechos = rag.buscar(f"{pergunta} {' '.join(nomes)}") or trechos
        if not trechos:
            texto = MSG_SEM_FONTE
        else:
            saida = llm.gerar(prompts.SISTEMA, _montar_pergunta(pergunta, trechos, receita_usada))
            texto, tokens = saida["texto"], saida["tokens"]
            if not saida["erro"]:
                fontes = list(dict.fromkeys(t["fonte"] for t in trechos if t["fonte"]))

    return {
        "resposta": f"{texto}\n\n{AVISO}",
        "categoria": categoria,
        "fontes": fontes,
        "tokens": tokens,
        "latencia_ms": round((time.perf_counter() - inicio) * 1000),
    }
