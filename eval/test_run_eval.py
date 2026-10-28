"""Confere o eval sem chamar o Groq (o LLM é simulado)."""
from backend.app import llm
from eval import run_eval


def test_contradiz_ignora_frase_negada():
    assert run_eval.contradiz("Não tome dose dobrada.", ["tome dose dobrada"]) == []
    assert run_eval.contradiz("Pode beber à vontade.", ["pode beber"]) == ["pode beber"]


def test_eval_roda_com_llm_simulado(monkeypatch):
    monkeypatch.setattr(llm, "gerar", lambda sistema, usuario: {
        "texto": "Evite álcool: aumenta o risco de acidose láctica.", "tokens": 1000, "erro": False})
    casos = run_eval.carregar()
    assert len(casos) == 40
    res = run_eval.executar([casos[0], casos[1]], pausa=0)
    assert res[0]["resolvida"]  # s01 pede "acidose"
    assert not res[1]["resolvida"] and "pressao" in res[1]["motivo"]
    assert "| Encaminhamento correto" in run_eval.relatorio(res)
