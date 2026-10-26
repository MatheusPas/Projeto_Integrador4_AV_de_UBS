"""Busca na base de conhecimento (data/kb) com TF-IDF.

Cada arquivo .md da base vira vários trechos, um por seção "## ".
Arquivos com nome de medicamento (ex.: metformina.md) marcam o trecho com
esse medicamento; arquivos de UBS (ubs_*.md) ficam com medicamento = None.
"""
import re
import unicodedata
from functools import lru_cache
from pathlib import Path

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

KB_DIR = Path(__file__).resolve().parents[2] / "data" / "kb"

# ponytail: limiar calibrado à mão; recalibrar com os resultados do eval
SCORE_MINIMO = 0.1

# Palavras vazias saem antes da busca: sem isso, "qual", "de", "uma" fazem
# perguntas fora do tema parecerem próximas de qualquer trecho.
# "como", "quando" e "onde" ficam de fora da lista porque aparecem nos
# títulos das seções ("Como tomar", "Quando procurar atendimento").
PALAVRAS_VAZIAS = set("""
a o as os um uma uns umas ao aos de da do das dos em na no nas nos num numa
por pra pro para com sem e ou que qual quais quem porque se nao sim
eu voce ele ela me te meu minha seu sua isso esse essa este esta ja mais
muito tem ter ser estar foi sao vou posso pode ta to
""".split())


def _preparar(texto: str) -> str:
    """Minúsculas, sem acento e sem palavras vazias."""
    texto = unicodedata.normalize("NFKD", texto.lower())
    texto = "".join(c for c in texto if not unicodedata.combining(c))
    return " ".join(p for p in re.findall(r"\w+", texto) if p not in PALAVRAS_VAZIAS)


def _carregar_trechos(kb_dir: Path = KB_DIR) -> list[dict]:
    trechos = []
    for arquivo in sorted(kb_dir.glob("*.md")):
        titulo, fonte, secao, corpo = arquivo.stem, "", None, []
        medicamento = None if arquivo.stem.startswith("ubs") else arquivo.stem

        def fechar_secao():
            if secao and corpo:
                trechos.append({
                    "texto": f"{titulo} — {secao}\n" + "\n".join(corpo).strip(),
                    "fonte": fonte,
                    "medicamento": medicamento,
                })

        for linha in arquivo.read_text(encoding="utf-8").splitlines():
            if linha.startswith("# "):
                titulo = linha[2:].strip()
            elif linha.startswith("Fonte:"):
                fonte = linha[len("Fonte:"):].strip()
            elif linha.startswith("## "):
                fechar_secao()
                secao, corpo = linha[3:].strip(), []
            elif secao:
                corpo.append(linha)
        fechar_secao()
    return trechos


@lru_cache(maxsize=1)
def _indice():
    trechos = _carregar_trechos()
    if not trechos:
        return None, None, []
    # n-gramas de caracteres pegam variações do português
    # ("esqueci" ~ "esquecimento", "álcool" ~ "alcoólica") sem precisar de stemmer
    vetorizador = TfidfVectorizer(analyzer="char_wb", ngram_range=(3, 5),
                                  preprocessor=_preparar, sublinear_tf=True)
    matriz = vetorizador.fit_transform(t["texto"] for t in trechos)
    return vetorizador, matriz, trechos


def buscar(pergunta: str, k: int = 3) -> list[dict]:
    """Retorna até k trechos mais parecidos com a pergunta.

    Lista vazia quando nada passa do SCORE_MINIMO: o pipeline deve então
    responder que a fonte não cobre a dúvida (OWASP LLM09), em vez de deixar
    o modelo inventar.
    """
    vetorizador, matriz, trechos = _indice()
    if not trechos or not pergunta.strip():
        return []
    scores = cosine_similarity(vetorizador.transform([pergunta]), matriz)[0]
    melhores = scores.argsort()[::-1][:k]
    return [{**trechos[i], "score": round(float(scores[i]), 3)}
            for i in melhores if scores[i] >= SCORE_MINIMO]


if __name__ == "__main__":
    # Autoverificação rápida: python -m backend.app.rag
    import sys

    if len(sys.argv) > 1:
        for r in buscar(" ".join(sys.argv[1:])):
            print(f"[{r['score']}] {r['texto'].splitlines()[0]}  ({r['fonte']})")
        sys.exit()

    casos = {
        "posso tomar metformina com álcool?": ("metformina", "Álcool"),
        "esqueci de tomar a losartana, e agora?": ("losartana", "Esqueci"),
        "omeprazol é antes ou depois do café?": ("omeprazol", "Como tomar"),
        "pra que serve a sinvastatina?": ("sinvastatina", "Para que serve"),
        "qual o horário da unidade de saúde?": (None, ""),
    }
    for pergunta, (medicamento, secao) in casos.items():
        resultado = buscar(pergunta)
        assert resultado, f"sem resultado: {pergunta}"
        primeiro = resultado[0]
        assert primeiro["medicamento"] == medicamento, (pergunta, primeiro["texto"][:60])
        assert secao in primeiro["texto"].splitlines()[0], (pergunta, primeiro["texto"][:60])
    for fora_do_tema in ("quem ganhou a copa do mundo de 2002?", "qual a capital da França?"):
        assert buscar(fora_do_tema) == [], f"deveria vir vazio: {fora_do_tema}"
    print(f"OK — {len(_indice()[2])} trechos indexados, {len(casos) + 1} casos passaram")
