"""JSON, privacidade e leitura de receitas reais do corpus fictício da equipe.

O caminho offline das imagens lê os metadados; não é validação de OCR.
O caminho de visão é testado separadamente com a resposta do SDK simulada.
"""
import io
import json
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock

import pytest
from pypdf import PdfReader, PdfWriter
from pypdf.generic import DictionaryObject, NameObject, DecodedStreamObject

from backend.app import receita
from backend.app.main import Receita


def test_json_recebido_pela_api_preserva_medicamentos_e_posologias():
    esperado = {"medicamentos": [
        {"nome": "Losartana", "posologia": "Prescrição fictícia A"},
        {"nome": "Omeprazol", "posologia": "Prescrição fictícia B"},
    ]}
    resultado = Receita.model_validate_json(json.dumps(esperado)).model_dump()
    assert resultado == esperado


def test_json_recebido_pela_api_descarta_nome_do_paciente():
    bruto = {"paciente": "Paciente Fictício Sigiloso", "medicamentos": [
        {"nome": "Losartana", "posologia": "Prescrição fictícia", "paciente": "Outro nome fictício"},
    ]}
    resultado = Receita.model_validate_json(json.dumps(bruto)).model_dump()
    assert resultado == {"medicamentos": [
        {"nome": "Losartana", "posologia": "Prescrição fictícia"},
    ]}
    assert bruto["paciente"] not in json.dumps(resultado, ensure_ascii=False)


@pytest.mark.parametrize("bruto", [
    {"medicamentos": [{"posologia": "Fictícia"}]},
    {"medicamentos": "não é uma lista"},
])
def test_api_rejeita_json_com_medicamentos_invalidos(bruto):
    from pydantic import ValidationError
    with pytest.raises(ValidationError):
        Receita.model_validate_json(json.dumps(bruto))

def _pdf_ficticio(linhas):
    """PDF de texto em memória, sem gravação de dados de paciente."""
    writer = PdfWriter()
    pagina = writer.add_blank_page(width=595, height=842)
    fonte = DictionaryObject({NameObject("/Type"): NameObject("/Font"),
                              NameObject("/Subtype"): NameObject("/Type1"),
                              NameObject("/BaseFont"): NameObject("/Helvetica")})
    pagina[NameObject("/Resources")] = DictionaryObject({
        NameObject("/Font"): DictionaryObject({NameObject("/F1"): writer._add_object(fonte)})})
    conteudo = DecodedStreamObject()
    comandos = ["BT /F1 12 Tf 50 780 Td"]
    for linha in linhas:
        escapada = linha.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")
        comandos.append(f"({escapada}) Tj 0 -20 Td")
    comandos.append("ET")
    conteudo.set_data("\n".join(comandos).encode("ascii"))
    pagina[NameObject("/Contents")] = writer._add_object(conteudo)
    saida = io.BytesIO()
    writer.write(saida)
    return saida.getvalue()


@pytest.fixture
def receita_ficticia(llm_simulado):
    medicamentos = [
        {"nome": "losartana", "posologia": "Conforme prescricao ficticia A"},
        {"nome": "omeprazol", "posologia": "Conforme prescricao ficticia B"},
    ]
    bruto = {"paciente": "Paciente Ficticio Teste", "medicamentos": medicamentos}
    llm_simulado.return_value = {"texto": json.dumps(bruto), "tokens": 25, "erro": False}
    pdf = _pdf_ficticio(["Paciente: " + bruto["paciente"]] + [
        m["nome"] + ": " + m["posologia"] for m in medicamentos])
    return pdf, bruto


def test_fixture_pdf_tem_texto_esperado(receita_ficticia):
    pdf, bruto = receita_ficticia
    texto = PdfReader(io.BytesIO(pdf)).pages[0].extract_text()
    assert bruto["paciente"] in texto
    assert all(m["nome"] in texto and m["posologia"] in texto for m in bruto["medicamentos"])


def test_extrair_retorna_contrato_json(receita_ficticia):
    pdf, _ = receita_ficticia
    resultado = receita.extrair(pdf, "application/pdf")
    assert set(resultado) == {"medicamentos"}
    assert isinstance(resultado["medicamentos"], list)
    for medicamento in resultado["medicamentos"]:
        assert set(medicamento) == {"nome", "posologia"}
        assert isinstance(medicamento["nome"], str) and medicamento["nome"]
        assert isinstance(medicamento["posologia"], str)
    assert json.loads(json.dumps(resultado)) == resultado


def test_json_lido_preserva_medicamentos_e_posologias(receita_ficticia):
    pdf, bruto = receita_ficticia
    assert receita.extrair(pdf, "application/pdf") == {"medicamentos": bruto["medicamentos"]}


def test_nome_do_paciente_descartado_sem_perder_medicamentos(receita_ficticia):
    pdf, bruto = receita_ficticia
    resultado = receita.extrair(pdf, "application/pdf")
    assert resultado["medicamentos"] == bruto["medicamentos"]
    assert set(resultado) == {"medicamentos"}
    assert bruto["paciente"] not in json.dumps(resultado, ensure_ascii=False)
    assert all(set(m) == {"nome", "posologia"} for m in resultado["medicamentos"])


PASTA_RECEITAS = Path(__file__).resolve().parents[1] / "data" / "receitas_ficticias"
CASOS_RECEITA = json.loads((PASTA_RECEITAS / "esperado.json").read_text(encoding="utf-8"))


@pytest.mark.parametrize("arquivo,caso", CASOS_RECEITA.items(), ids=list(CASOS_RECEITA))
def test_corpus_ficticio_offline(arquivo, caso, llm_simulado, monkeypatch, tmp_path):
    conteudo = (PASTA_RECEITAS / arquivo).read_bytes()
    # Não devolve a resposta esperada pelo mock: exige leitura local do arquivo.
    llm_simulado.return_value = {"texto": "", "tokens": 0, "erro": True}
    monkeypatch.chdir(tmp_path)
    resultado = receita.extrair(conteudo, caso["mime"])
    assert resultado == caso["esperado"]
    assert caso["paciente_descartado"] not in json.dumps(resultado, ensure_ascii=False)
    assert list(tmp_path.rglob("*")) == []


@pytest.mark.parametrize("arquivo", [
    "receita_01_diabetes_hipertensao.png",
    "receita_03_gastrite_colesterol_torta.jpg",
])
def test_visao_envia_imagem_e_parseia_json_sem_chamar_groq(arquivo, monkeypatch, llm_simulado):
    import base64

    caso = CASOS_RECEITA[arquivo]
    conteudo = (PASTA_RECEITAS / arquivo).read_bytes()
    bruto = dict(caso["esperado"], paciente="Paciente Fictício", medico="Médico Fictício")
    resposta = SimpleNamespace(choices=[SimpleNamespace(
        message=SimpleNamespace(content=json.dumps(bruto, ensure_ascii=False)))])
    cliente = Mock()
    cliente.chat.completions.create.return_value = resposta
    monkeypatch.setenv("GROQ_API_KEY", "chave-ficticia-para-teste")
    monkeypatch.setattr(receita, "_cliente", Mock(return_value=cliente))
    llm_simulado.return_value = {"texto": "", "tokens": 0, "erro": True}
    resultado = receita.extrair(conteudo, caso["mime"])
    assert resultado == caso["esperado"]
    cliente.chat.completions.create.assert_called_once()
    parametros = cliente.chat.completions.create.call_args.kwargs
    partes = parametros["messages"][0]["content"]
    imagem = next(p["image_url"]["url"] for p in partes if p["type"] == "image_url")
    cabecalho, dados = imagem.split(",", 1)
    assert cabecalho == f"data:{caso['mime']};base64"
    assert base64.b64decode(dados) == conteudo


@pytest.mark.parametrize("formato", ["json", "cerca", "raciocinio"])
def test_parser_do_leitor_descarta_dados_pessoais_do_json(formato):
    dados = {"paciente": "Paciente Fictício", "medicamentos": [
        {"nome": "Metformina 500 mg", "posologia": "1 comprimido; Paciente: Paciente Fictício",
         "paciente": "Outro nome fictício"},
    ]}
    texto = json.dumps(dados, ensure_ascii=False)
    if formato == "cerca":
        texto = "```json\n" + texto + "\n```"
    elif formato == "raciocinio":
        texto = "<think>Texto fictício</think>\n" + texto
    resultado = receita._parsear_resposta(texto)
    assert resultado == [{"nome": "metformina", "posologia": "500 mg, 1 comprimido"}]
    assert "Fictício" not in json.dumps(resultado, ensure_ascii=False)


@pytest.mark.parametrize("texto", ["", "resposta sem JSON", '{"medicamentos": "invalido"}'])
def test_parser_nao_inventa_medicamentos(texto):
    assert receita._parsear_resposta(texto) == []
