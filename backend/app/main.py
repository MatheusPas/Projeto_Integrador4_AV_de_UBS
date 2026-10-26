"""API do assistente.

Rodar: uvicorn backend.app.main:app --reload  ->  http://localhost:8000

O servidor não guarda nada: a receita lida volta para o frontend, que a
reenvia a cada mensagem do chat.
"""
import os
import time
from collections import defaultdict, deque
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request, UploadFile
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from backend.app import pipeline, receita

load_dotenv()

FRONTEND_DIR = Path(__file__).resolve().parents[2] / "frontend"
LIMITE_POR_MINUTO = int(os.getenv("LIMITE_POR_MINUTO", "20"))
TAMANHO_MAXIMO = 10 * 1024 * 1024  # 10 MB
TIPOS_RECEITA = {"image/png", "image/jpeg", "image/webp", "application/pdf"}

app = FastAPI(title="Assistente de medicamentos — UBS Vitória")

# horários das últimas requisições de cada IP (em memória; zera ao reiniciar)
_requisicoes: dict[str, deque] = defaultdict(deque)


@app.middleware("http")
async def limitar_por_ip(request: Request, call_next):
    """Protege a cota gratuita do Groq: no máximo LIMITE_POR_MINUTO chamadas por IP."""
    if request.method == "POST":
        ip = request.client.host if request.client else "desconhecido"
        agora, janela = time.monotonic(), _requisicoes[ip]
        while janela and agora - janela[0] > 60:
            janela.popleft()
        if len(janela) >= LIMITE_POR_MINUTO:
            return JSONResponse(status_code=429, content={
                "detail": "Muitas mensagens em pouco tempo. Aguarde 1 minuto e tente de novo."})
        janela.append(agora)
    return await call_next(request)


class Medicamento(BaseModel):
    nome: str
    posologia: str = ""


class Receita(BaseModel):
    medicamentos: list[Medicamento] = []


class Pergunta(BaseModel):
    pergunta: str = Field(min_length=1, max_length=1000)
    receita: Receita | None = None


@app.post("/chat")
def chat(dados: Pergunta) -> dict:
    receita_dict = dados.receita.model_dump() if dados.receita else None
    return pipeline.responder(dados.pergunta.strip(), receita_dict)


@app.post("/receita")
async def ler_receita(arquivo: UploadFile) -> dict:
    if arquivo.content_type not in TIPOS_RECEITA:
        raise HTTPException(415, "Envie a receita como imagem (PNG, JPG, WEBP) ou PDF.")
    conteudo = await arquivo.read(TAMANHO_MAXIMO + 1)
    if len(conteudo) > TAMANHO_MAXIMO:
        raise HTTPException(413, "Arquivo maior que 10 MB.")
    # o arquivo só existe em memória durante a leitura; nada é salvo
    return receita.extrair(conteudo, arquivo.content_type)


# montado por último para não esconder as rotas da API
if FRONTEND_DIR.is_dir():
    app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")
