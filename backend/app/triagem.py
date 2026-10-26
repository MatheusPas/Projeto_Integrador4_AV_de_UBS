"""Triagem da pergunta antes da busca e do LLM.

ESQUELETO (Matheus): devolve sempre "responder_geral" só para o resto do
grupo poder integrar. O João substitui pelas regras de verdade, mantendo o
contrato abaixo.
"""

CATEGORIAS = ("responder_personalizado", "responder_geral", "encaminhar", "fora_escopo")


def classificar(pergunta: str, receita: dict | None = None) -> dict:
    """-> {"categoria": uma de CATEGORIAS, "motivo": str}"""
    return {"categoria": "responder_geral", "motivo": "esqueleto: triagem ainda não implementada"}
