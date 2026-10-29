"""Leitura da receita (imagem ou PDF) em memória.

- Imagem (PNG, JPG, WEBP) -> modelo de visão do Groq (`qwen/qwen3.8-27b`, já que
  `meta-llama/llama-4-scout-17b-16e-instruct` foi descontinuado no Groq em jul/2026).
- PDF -> extração de texto em memória com `pypdf` (`io.BytesIO`).
- Devolve apenas `{"medicamentos": [{"nome": str, "posologia": str}]}`:
  nome do paciente, CPF, médico e demais dados pessoais são descartados.
- O arquivo nunca é salvo em disco.
"""
import base64
import io
import json
import os
import re
from functools import lru_cache

from dotenv import load_dotenv
from groq import APIConnectionError, APIError, Groq, RateLimitError
from pypdf import PdfReader

from backend.app import llm

load_dotenv()

# meta-llama/llama-4-scout-17b-16e-instruct saiu do Groq em jul/2026;
# qwen/qwen3.8-27b é o modelo multimodal de visão ativo em console.groq.com/docs/models
MODELO_VISAO = os.getenv("GROQ_MODELO_VISAO", "qwen/qwen3.8-27b")

PROMPT_RECEITA = (
    "Você é um extrator de receitas médicas. Leia a receita e extraia APENAS os "
    "medicamentos prescritos e a posologia de cada um.\n"
    "Regras obrigatórias:\n"
    "1. Ignore e descarte completamente nome do paciente, CPF, endereço, data, "
    "nome do médico, CRM e nome da unidade de saúde.\n"
    "2. No campo 'nome', coloque apenas o princípio ativo ou nome do medicamento "
    "em letras minúsculas (ex.: 'metformina', 'losartana', 'amoxicilina', 'aas').\n"
    "3. No campo 'posologia', inclua a concentração/dosagem seguida do modo de usar "
    "(ex.: '500 mg, 1 comprimido após o almoço').\n"
    "4. Responda EXCLUSIVAMENTE com um objeto JSON válido no formato:\n"
    '{"medicamentos": [{"nome": "...", "posologia": "..."}]}'
)

# Sais e termos farmacêuticos que não fazem parte do nome curto usado na base (data/kb/)
_SAIS_IGNORADOS = (
    r"\b(cloridrato\s+de|pot[aá]ssica|s[oó]dica|monoidratada|"
    r"comprimidos?\s+revestidos?|comprimidos?|c[aá]psulas?\s+duras?|c[aá]psulas?|"
    r"solu[cç][aã]o\s+oral|gotas)\b"
)

_SINONIMOS_KB = {
    "acido acetilsalicilico": "aas",
    "ácido acetilsalicílico": "aas",
    "aspirina": "aas",
    "glifage": "metformina",
    "cozaar": "losartana",
    "amoxil": "amoxicilina",
    "novalgina": "dipirona",
    "tylenol": "paracetamol",
    "losec": "omeprazol",
    "zocor": "sinvastatina",
    "puran t4": "levotiroxina",
    "puran": "levotiroxina",
    "synthroid": "levotiroxina",
    "clorana": "hidroclorotiazida",
}

_PADRAO_CONCENTRACAO = re.compile(
    r"\b(\d+(?:[.,]\d+)?\s*(?:mg/ml|mg|mcg|g|ui|ml|%))\b",
    re.IGNORECASE,
)

_PADRAO_DADOS_PESSOAIS = re.compile(
    r"\b(paciente\s*fict[ií]cio|paciente\s*:|cpf\s*:|crm\s*[-:]|cns\s*:|"
    r"cart[aã]o\s+sus|dr\(a\)\.?|m[eé]dico\(a\)\s*:)",
    re.IGNORECASE,
)


@lru_cache(maxsize=1)
def _cliente() -> Groq:
    return Groq(api_key=os.environ["GROQ_API_KEY"], timeout=30, max_retries=1)


def _limpar_medicamento(nome: str, posologia: str) -> dict | None:
    """Normaliza nome e posologia e descarta qualquer resquício de dado pessoal."""
    nome = (nome or "").strip()
    posologia = (posologia or "").strip()
    if not nome or _PADRAO_DADOS_PESSOAIS.search(nome):
        return None

    # Remove eventuais menções acidentais a paciente/CPF/CRM dentro da posologia
    posologia = re.sub(
        r"(?:paciente|cpf|crm|m[eé]dico)\s*[:\-].*$", "", posologia, flags=re.IGNORECASE
    ).strip(" ,;-")

    # Se a concentração veio junto no nome (ex.: "Metformina 500 mg"), move para a posologia
    m_conc = _PADRAO_CONCENTRACAO.search(nome)
    if m_conc:
        conc = m_conc.group(1).strip()
        nome = (nome[: m_conc.start()] + " " + nome[m_conc.end() :]).strip()
        if conc.lower() not in posologia.lower():
            posologia = f"{conc}, {posologia}" if posologia else conc

    # Limpa forma farmacêutica/sal do nome e padroniza em minúsculas
    nome = re.sub(r"\([^)]*\)", " ", nome)
    nome = re.sub(_SAIS_IGNORADOS, " ", nome, flags=re.IGNORECASE)
    nome = re.sub(r"\s+", " ", nome).strip(" -–—,:;().0123456789").lower()
    nome = _SINONIMOS_KB.get(nome, nome)

    # Remove prefixo "Posologia:" redundante caso exista
    posologia = re.sub(r"\)\s*Tj\s*T\*.*$", "", posologia).strip()
    posologia = re.sub(r"^posologia\s*:\s*", "", posologia, flags=re.IGNORECASE).strip()

    if not nome or len(nome) < 2:
        return None
    return {"nome": nome, "posologia": posologia}


def _parsear_resposta(texto: str) -> list[dict]:
    """Extrai a lista de medicamentos de uma resposta JSON do LLM, descartando outros campos."""
    if not texto:
        return []
    # Remove blocos <think>...</think> (modelos de raciocínio como Qwen) e cercas markdown
    limpo = re.sub(r"<think>.*?</think>", "", texto, flags=re.DOTALL)
    limpo = re.sub(r"```(?:json)?", "", limpo, flags=re.IGNORECASE).strip()

    decoder = json.JSONDecoder()
    dados = None
    for match in re.finditer(r"[\{\[]", limpo):
        try:
            dados, _ = decoder.raw_decode(limpo[match.start() :])
            break
        except json.JSONDecodeError:
            continue

    if isinstance(dados, dict):
        itens = dados.get("medicamentos")
        if not isinstance(itens, list):
            itens = []
    elif isinstance(dados, list):
        itens = dados
    else:
        return []

    medicamentos = []
    for item in itens:
        if not isinstance(item, dict):
            continue
        nome_bruto = str(item.get("nome") or item.get("medicamento") or item.get("remedio") or "")
        pos_bruta = str(item.get("posologia") or item.get("dose") or item.get("como_tomar") or "")
        med = _limpar_medicamento(nome_bruto, pos_bruta)
        if med:
            medicamentos.append(med)
    return medicamentos


def _extrair_por_regex(texto: str) -> list[dict]:
    """Extrai medicamentos e posologias de texto estruturado de receita em PDF."""
    if not texto:
        return []

    medicamentos = []
    linhas = [ln.strip() for ln in texto.splitlines() if ln.strip()]

    # Padrão 1: "Medicamento: <nome> | Posologia: <posologia>"
    padrao_pipe = re.compile(
        r"(?:\d+[\)\.\-]\s*)?medicamento\s*:\s*([^|\n]+?)\s*\|\s*posologia\s*:\s*(.+)",
        re.IGNORECASE,
    )
    for ln in linhas:
        m = padrao_pipe.search(ln)
        if m:
            med = _limpar_medicamento(m.group(1), m.group(2))
            if med:
                medicamentos.append(med)
    if medicamentos:
        return medicamentos

    # Padrão 2: linha numerada "1) Nome 500 mg" seguida de "Posologia: ..." ou "— ..."
    padrao_item = re.compile(
        r"^(?:\d+[\)\.\-]|[-•])\s*(.+?)(?:\s*[-–—:]\s*(.+))?$"
    )
    i = 0
    while i < len(linhas):
        ln = linhas[i]
        if _PADRAO_DADOS_PESSOAIS.search(ln) or ln.startswith("---"):
            i += 1
            continue
        m = padrao_item.match(ln)
        if m:
            nome_cand = m.group(1).strip()
            pos_cand = (m.group(2) or "").strip()
            if i + 1 < len(linhas) and re.match(r"^posologia\s*:", linhas[i + 1], re.IGNORECASE):
                pos_cand = linhas[i + 1]
                i += 1
            med = _limpar_medicamento(nome_cand, pos_cand)
            if med:
                medicamentos.append(med)
        i += 1

    return medicamentos


def _extrair_texto_pdf(conteudo: bytes) -> str:
    """Lê o texto de um PDF em memória usando pypdf, sem salvar arquivo."""
    # PDF escaneado (só imagem) ou corrompido devolve texto vazio: melhor
    # "nenhum medicamento" do que tentar ler bytes crus e inventar remédio.
    try:
        leitor = PdfReader(io.BytesIO(conteudo))
        return "\n".join(p.extract_text() or "" for p in leitor.pages).strip()
    except Exception:
        return ""


def _chamar_visao_groq(conteudo: bytes, mime: str) -> list[dict]:
    """Envia a imagem em base64 (em memória) ao modelo de visão do Groq."""
    if not os.getenv("GROQ_API_KEY"):
        return []
    b64 = base64.b64encode(conteudo).decode("ascii")
    try:
        resposta = _cliente().chat.completions.create(
            model=MODELO_VISAO,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": PROMPT_RECEITA},
                        {
                            "type": "image_url",
                            "image_url": {"url": f"data:{mime};base64,{b64}"},
                        },
                    ],
                }
            ],
            temperature=0.0,
            max_tokens=1024,
        )
        texto = resposta.choices[0].message.content or ""
        return _parsear_resposta(texto)
    except (RateLimitError, APIConnectionError, APIError):
        return []


def extrair(conteudo: bytes, mime: str) -> dict:
    """-> {"medicamentos": [{"nome": str, "posologia": str}]}"""
    if not conteudo or not mime:
        return {"medicamentos": []}

    mime_limpo = mime.lower().strip()

    if mime_limpo == "application/pdf":
        texto_pdf = _extrair_texto_pdf(conteudo)
        if not texto_pdf:
            return {"medicamentos": []}
        # Tenta extração estruturada por regex primeiro (rápida e determinística) e via LLM se necessário
        meds = _extrair_por_regex(texto_pdf)
        if not meds:
            saida = llm.gerar(PROMPT_RECEITA, f"Texto da receita:\n{texto_pdf}")
            if not saida.get("erro"):
                meds = _parsear_resposta(saida.get("texto", ""))
        return {"medicamentos": meds}

    if mime_limpo.startswith("image/"):
        # Só o modelo de visão lê imagem; se ele falhar, a tela mostra
        # "nenhum medicamento identificado" em vez de um remédio inventado.
        return {"medicamentos": _chamar_visao_groq(conteudo, mime_limpo)}

    return {"medicamentos": []}
