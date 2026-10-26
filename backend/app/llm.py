"""Chamada ao LLM no Groq.

gerar() nunca levanta exceção para o pipeline: erros da API viram uma
mensagem amigável, para o usuário não ver um erro 500 no chat.
"""
import os
from functools import lru_cache

from dotenv import load_dotenv
from groq import APIConnectionError, APIError, Groq, RateLimitError

load_dotenv()

# llama-3.3-70b-versatile saiu do Groq; gpt-oss-120b é o maior modelo de texto disponível
MODELO = os.getenv("GROQ_MODELO", "openai/gpt-oss-120b")

MSG_LIMITE = ("Muitas perguntas ao mesmo tempo no serviço de IA (limite do plano gratuito). "
              "Aguarde cerca de 1 minuto e tente de novo.")
MSG_SEM_CHAVE = "O serviço de IA não está configurado (falta GROQ_API_KEY no .env)."
MSG_INDISPONIVEL = "O serviço de IA está indisponível no momento. Tente de novo em instantes."


@lru_cache(maxsize=1)
def _cliente() -> Groq:
    return Groq(api_key=os.environ["GROQ_API_KEY"], timeout=30, max_retries=1)


def gerar(sistema: str, usuario: str) -> dict:
    """-> {"texto": str, "tokens": int, "erro": bool}"""
    if not os.getenv("GROQ_API_KEY"):
        return {"texto": MSG_SEM_CHAVE, "tokens": 0, "erro": True}
    try:
        resposta = _cliente().chat.completions.create(
            model=MODELO,
            messages=[{"role": "system", "content": sistema},
                      {"role": "user", "content": usuario}],
            # baixa: a resposta deve seguir a bula, não variar
            temperature=0.2,
            # o gpt-oss raciocina antes de responder e o raciocínio conta aqui
            max_tokens=1500,
        )
    except RateLimitError:
        return {"texto": MSG_LIMITE, "tokens": 0, "erro": True}
    except (APIConnectionError, APIError):
        return {"texto": MSG_INDISPONIVEL, "tokens": 0, "erro": True}
    uso = resposta.usage
    return {"texto": resposta.choices[0].message.content.strip(),
            "tokens": uso.total_tokens if uso else 0, "erro": False}
