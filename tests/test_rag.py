import json
import math
from pathlib import Path

import pytest

from backend.app import rag

CASOS = json.loads((Path(__file__).resolve().parents[1] / "data" / "casos_teste_rag.json").read_text(encoding="utf-8"))


@pytest.mark.parametrize("caso", CASOS, ids=[f"{i:03d}-{c['categoria']}" for i, c in enumerate(CASOS)])
def test_casos_de_referencia(caso):
    resultado = rag.buscar(caso["pergunta"])
    assert isinstance(resultado, list)
    assert len(resultado) <= 3
    for trecho in resultado:
        assert set(trecho) == {"texto", "fonte", "medicamento", "score"}
        assert isinstance(trecho["texto"], str) and trecho["texto"]
        assert isinstance(trecho["fonte"], str) and trecho["fonte"]
        assert trecho["medicamento"] is None or isinstance(trecho["medicamento"], str)
        assert isinstance(trecho["score"], (int, float))
        assert math.isfinite(trecho["score"]) and trecho["score"] >= 0
    if caso.get("vazio"):
        assert resultado == []
    else:
        assert resultado, caso["pergunta"]
        assert resultado[0]["medicamento"] == caso["medicamento"]
        assert caso["secao"] in resultado[0]["texto"].splitlines()[0]


@pytest.mark.parametrize("k", [1, 2, 5])
def test_limite_de_resultados(k):
    assert 0 < len(rag.buscar("Para que serve metformina?", k=k)) <= k


def test_pergunta_vazia():
    assert rag.buscar("   ") == []
