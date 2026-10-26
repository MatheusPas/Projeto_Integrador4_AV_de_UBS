"""Leitura da receita (imagem ou PDF).

ESQUELETO (Matheus): devolve uma receita falsa fixa para o resto do grupo
poder integrar. O Eduardo substitui pela leitura de verdade, mantendo o
contrato abaixo. O arquivo nunca é salvo.
"""


def extrair(conteudo: bytes, mime: str) -> dict:
    """-> {"medicamentos": [{"nome": str, "posologia": str}]}"""
    return {"medicamentos": [{"nome": "metformina", "posologia": "500 mg, 1 comprimido após o almoço"}]}
