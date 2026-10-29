"""Testes locais: nenhuma execução pode chegar ao cliente real do Groq."""
import sys
from pathlib import Path
from unittest.mock import Mock

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from backend.app import llm


@pytest.fixture(autouse=True)
def llm_simulado(monkeypatch):
    monkeypatch.delenv("GROQ_API_KEY", raising=False)

    def cliente_proibido(*args, **kwargs):
        pytest.fail("Os testes não podem chamar o cliente real do Groq")

    monkeypatch.setattr(llm, "_cliente", cliente_proibido)
    # Também impede clientes instanciados diretamente pelo leitor de receitas.
    monkeypatch.setattr("groq.Groq.__init__", cliente_proibido)
    gerar = Mock(return_value={"texto": "Informação fictícia baseada nos trechos fornecidos.", "tokens": 12, "erro": False})
    monkeypatch.setattr(llm, "gerar", gerar)
    return gerar


@pytest.fixture
def receita_exemplo():
    return {"medicamentos": [{"nome": "Metformina 500 mg", "posologia": "Conforme prescrição fictícia"}]}
