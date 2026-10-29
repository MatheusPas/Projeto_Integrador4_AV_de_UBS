"""Triagem determinística: riscos são avaliados antes de qualquer receita.

As regras cobrem expressões conhecidas, não fazem diagnóstico e não substituem
avaliação clínica. Novas formas de escrever devem entrar como casos de teste.
"""
import re
import unicodedata

CATEGORIAS = ("responder_personalizado", "responder_geral", "encaminhar", "fora_escopo")

# Nomes comerciais presentes na base do Lucas; nenhum dado de dose é usado.
NOMES_MEDICAMENTOS = (
    ("aas", "acido acetilsalicilico", "aspirina"),
    ("amoxicilina", "amoxil"),
    ("dipirona", "novalgina"),
    ("hidroclorotiazida", "clorana"),
    ("levotiroxina", "puran t4", "euthyrox", "synthroid", "levoid"),
    ("losartana", "cozaar"),
    ("metformina", "glifage", "glifage xr"),
    ("omeprazol", "losec"),
    ("paracetamol", "tylenol"),
    ("sinvastatina", "zocor"),
)

# Reconhece dúvidas sobre remédios além da base, sem prometer que o RAG terá
# fonte para eles. O pipeline já trata a ausência de fonte sem chamar o LLM.
OUTROS_MEDICAMENTOS = (
    "ibuprofeno", "diclofenaco", "nimesulida", "enalapril", "captopril",
    "atenolol", "insulina", "sertralina", "fluoxetina", "loratadina",
)

URGENCIAS = (
    r"\bdor (?:forte )?(?:no|em meu) peito\b",
    r"\b(?:falta de ar|nao consigo respirar|dificuldade (?:para|de) respirar)\b",
    r"\b(?:desmaio|desmaiei|desmaiou|desmaiando|desmaiar|inconsciente|perdeu a consciencia)\b",
    r"\b(?:overdose|superdose|superdosagem)\b",
    r"\b(?:tomei|tomou|ingeri|ingeriu)\b.{0,65}\b(?:demais|a mais|dose maior|dose extra|muitos comprimidos|varios comprimidos)\b",
    r"\b(?:tomei|tomou|ingeri|ingeriu)\b.{0,45}\b(?:cartela|caixa|frasco) (?:inteir\w*|tod\w*)\b",
    r"\b(?:alergia|reacao alergica) (?:muito )?(?:grave|severa)\b",
    r"\b(?:anafilaxia|choque anafilatico|garganta (?:esta )?fechando)\b",
    r"\b(?:lingua|garganta|rosto|boca|labios)\b.{0,35}\b(?:inchad\w*|inchou|incharam|inchando)\b",
)
INJECOES = (
    r"\b(?:ignore|ignorar|desconsidere|esqueca|burl\w*)\b.{0,70}\b(?:regras|instrucoes|restricoes|sistema|prompt|seguranca)\b",
    r"\b(?:ignore|disregard|forget)\b.{0,70}\b(?:instructions|rules|prompt|system)\b",
    r"\b(?:mostre|revele|exiba|imprima)\b.{0,50}\b(?:prompt|instrucoes internas|mensagem de sistema)\b",
    r"\b(?:finja|aja|atue)\b.{0,45}\b(?:medico|sem restricoes|sem regras|outro assistente)\b",
    r"\b(?:esqueca|ignore|desconsidere)\b.{0,70}\b(?:assistente|seu papel|sua funcao)\b",
    r"\b(?:finja|invente|altere)\b.{0,60}\b(?:bula|fonte|trechos|evidencias)\b",
    r"\b(?:modo desenvolvedor|developer mode|jailbreak)\b",
    r"<\s*/?\s*(?:system|developer)\b|\[\s*(?:inst|system)\s*\]",
)
SINTOMAS = (
    r"\b(?:dor(?:es)?|febre|tosse|tontura|enjoo|nausea\w*|vomit\w*|diarreia|coceira|ardencia|"
    r"queimacao|azia|gripe|resfriado|mal estar|malestar|pressao alta|pressao baixa|"
    r"insonia|ansiedade|enxaqueca|constipacao|alergia|cansaco)\b"
)
PEDIDOS_REMEDIO = (
    r"\b(?:o que|oq|que|qual|quais)\b.{0,35}\b(?:tomar|tomo|usar|uso|remedio\w*|medicamento\w*|antibiotico\w*|analgesico\w*|comprimido\w*|dose|posologia)\b",
    r"\b(?:posso|devo|preciso|quero)\b.{0,25}\b(?:tomar|usar|medicar)\b",
    r"\b(?:indique|indica|indicar|recomende|recomenda|recomendar|receite|prescreva|prescrever)\b",
    r"\b(?:remedio\w*|medicamento\w*)\b.{0,25}\b(?:bom|boa|melhor|para|pra)\b",
    r"\b(?:me ajuda|ajuda|resolve|alivia|serve para|serve pra)\b",
    r"\b(?:e|seria) (?:bom|boa|indicado|indicada|seguro|segura)\b",
)
ALTERACOES = (
    r"\b(?:parar|paro|parei|suspender|suspendo|suspendi|interromper|interrompo|trocar|troco|mudar|mudo|"
    r"substituir|alterar|aumentar|aumento|aumentei|reduzir|reduzo|reduzi|diminuir|diminuo|"
    r"dobrar|dobro|iniciar|inicio|comecar|comeco|retomar|retomo|deixar de (?:tomar|usar)|"
    r"nao (?:tomar|usar) mais)\b",
)
CONTEXTO_SAUDE = (
    r"\b(?:saude|ubs|sus|unidade basica|posto de saude|bula\w*|remedio\w*|medicamento\w*|"
    r"tratamento\w*|receita\w*|prescricao|posologia|dose\w*|comprimido\w*|capsula\w*|"
    r"farmaci\w*|medico\w*|enferm\w*|vacina\w*|diabetes|hipertensao|colesterol|"
    r"antibiotico\w*|analgesico\w*|gestante\w*|gravidez|amament\w*)\b"
)
FORA_TEMA = (
    r"\b(?:futebol|flamengo|palmeiras|horoscopo|loteria|bitcoin|criptomoeda\w*|"
    r"eleicoes|videogame|minecraft|roblox)\b",
    r"\b(?:escreva|crie|faca)\b.{0,30}\b(?:codigo|programa|poema|redacao)\b",
)


def _normalizar(texto: str) -> str:
    texto = unicodedata.normalize("NFKD", texto.casefold())
    texto = "".join(c for c in texto if not unicodedata.combining(c)
                    and unicodedata.category(c) != "Cf")
    texto = re.sub(r"[-‐‑‒–—]", " ", texto)
    return " ".join(texto.split())


def _contem(texto: str, padroes) -> bool:
    return any(re.search(padrao, texto) for padrao in padroes)


def _nome_presente(texto: str, nome: str) -> bool:
    # Limites evitam que 'AAS' corresponda a parte de outra palavra.
    return bool(nome and re.search(r"(?<!\w)" + re.escape(nome) + r"(?!\w)", texto))


def _nomes_receita(receita: dict | None) -> list[str]:
    medicamentos = (receita or {}).get("medicamentos") or []
    nomes = []
    for medicamento in medicamentos:
        nome = _normalizar(medicamento.get("nome", ""))
        # A receita pode trazer 'Metformina 500 mg' como nome.
        nome = re.sub(r"\s+\d+(?:[.,]\d+)?\s*(?:mg|mcg|g|ml|ui)\b.*$", "", nome)
        if nome:
            nomes.append(nome)
    return nomes


def _mesmo_medicamento(texto: str, nome: str) -> bool:
    if _nome_presente(texto, nome):
        return True
    for grupo in NOMES_MEDICAMENTOS:
        if any(_nome_presente(nome, alias) for alias in grupo):
            return any(_nome_presente(texto, alias) for alias in grupo)
    return False


def classificar(pergunta: str, receita: dict | None = None) -> dict:
    """Retorna {categoria, motivo}, sem chamar modelo nem serviço externo."""
    texto = _normalizar(pergunta)

    def resultado(categoria, motivo):
        return {"categoria": categoria, "motivo": motivo}

    if _contem(texto, URGENCIAS):
        return resultado("encaminhar", "Possível urgência: procure atendimento imediato e ligue para o SAMU 192.")
    if _contem(texto, INJECOES):
        return resultado("fora_escopo", "Tentativa de modificar ou revelar as instruções do assistente.")
    if not texto:
        return resultado("fora_escopo", "Envie uma dúvida sobre medicamentos ou saúde na atenção básica.")

    nomes = _nomes_receita(receita)
    cita_receita = any(_mesmo_medicamento(texto, nome) for nome in nomes)
    cita_medicamento = cita_receita or any(
        _nome_presente(texto, nome) for grupo in NOMES_MEDICAMENTOS for nome in grupo
    ) or any(_nome_presente(texto, nome) for nome in OUTROS_MEDICAMENTOS)
    tem_sintoma = bool(re.search(SINTOMAS, texto))
    contexto_saude = bool(re.search(CONTEXTO_SAUDE, texto)) or cita_medicamento or tem_sintoma

    if contexto_saude and _contem(texto, ALTERACOES):
        return resultado("encaminhar", "Iniciar, suspender ou alterar tratamento exige avaliação de um profissional de saúde.")
    if tem_sintoma and _contem(texto, PEDIDOS_REMEDIO):
        return resultado("encaminhar", "Sintoma com pedido de medicamento: procure um médico ou farmacêutico, mesmo tendo receita.")
    if re.search(r"\b(?:indique|indicar|recomende|recomendar|receite|prescreva|prescrever)\b", texto) and contexto_saude:
        return resultado("encaminhar", "O assistente não indica medicamentos; procure um profissional de saúde.")
    if re.search(r"\b(?:qual|que) (?:o )?(?:remedio|medicamento)\b.{0,30}\b(?:tomar|tomo|usar|uso)\b", texto):
        return resultado("encaminhar", "A escolha de um medicamento precisa de avaliação profissional.")
    pedido_de_uso = re.search(r"^(?:eu )?(?:posso|devo|quero|preciso) (?:tomar|usar)\b", texto)
    # Interações são dúvidas sobre a bula, não autorização para iniciar uso.
    # Risco, urgência e alteração de tratamento já foram avaliados acima.
    contexto_informativo = re.search(
        r"\b(?:bula|jejum|refeicao|comida|comer|agua|horario|manha|noite|"
        r"alcool|alcoolic\w*|cerveja|vinho|interacao|interacoes|junto com)\b", texto)
    if pedido_de_uso and contexto_saude and not contexto_informativo:
        return resultado("encaminhar", "Decidir se deve usar um medicamento exige avaliação profissional.")
    if _contem(texto, FORA_TEMA) or not contexto_saude:
        return resultado("fora_escopo", "Assunto fora de medicamentos e saúde na atenção básica.")
    if cita_receita:
        return resultado("responder_personalizado", "A pergunta cita um medicamento presente na receita enviada.")
    if len(nomes) == 1 and re.search(r"\b(?:meu remedio|minha medicacao|minha receita)\b", texto):
        return resultado("responder_personalizado", "Referência à receita enviada, que contém um único medicamento.")
    return resultado("responder_geral", "Dúvida informativa, sem necessidade de usar a receita enviada.")
