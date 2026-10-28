# Receitas Fictícias e Resultado Esperado (`test_receita.py`)

Todas as receitas desta pasta são **100% inventadas**, emitidas em nome de **"Paciente Fictício"** e **sem CPF** (nem dados reais de pacientes ou médicos).

O arquivo `esperado.json` traz o dicionário exato esperado de `receita.extrair(conteudo, mime)` para cada arquivo, para uso direto nos testes automatizados (`tests/test_receita.py` — João).

## Tabela de referência para o João (`test_receita.py`)

| Arquivo | Tipo (`mime`) | Observação | Retorno esperado de `receita.extrair(conteudo, mime)` |
|---|---|---|---|
| `receita_01_diabetes_hipertensao.png` | `image/png` | Imagem nítida (UBS Jardim Camburi) | `{"medicamentos": [{"nome": "metformina", "posologia": "500 mg, 1 comprimido após o almoço e 1 comprimido após o jantar"}, {"nome": "losartana", "posologia": "50 mg, 1 comprimido pela manhã"}]}` |
| `receita_02_infeccao.jpg` | `image/jpeg` | Imagem nítida (UBS Maruípe) | `{"medicamentos": [{"nome": "amoxicilina", "posologia": "500 mg, 1 cápsula de 8 em 8 horas por 7 dias"}, {"nome": "paracetamol", "posologia": "500 mg, 1 comprimido de 6 em 6 horas se dor ou febre"}]}` |
| `receita_03_gastrite_colesterol_torta.jpg` | `image/jpeg` | **Foto torta** (~8,5° de inclinação) | `{"medicamentos": [{"nome": "omeprazol", "posologia": "20 mg, 1 cápsula em jejum, 30 minutos antes do café da manhã"}, {"nome": "sinvastatina", "posologia": "20 mg, 1 comprimido à noite"}]}` |
| `receita_04_tireoide_pressao.png` | `image/png` | Imagem nítida (UBS Jardim da Penha) | `{"medicamentos": [{"nome": "levotiroxina", "posologia": "50 mcg, 1 comprimido em jejum, 30 minutos antes do café da manhã"}, {"nome": "hidroclorotiazida", "posologia": "25 mg, 1 comprimido pela manhã"}]}` |
| `receita_05_cardiovascular.pdf` | `application/pdf` | PDF digital lido com `pypdf` | `{"medicamentos": [{"nome": "aas", "posologia": "100 mg, 1 comprimido uma vez ao dia, 30 minutos antes do almoço"}, {"nome": "dipirona", "posologia": "500 mg/mL, 20 gotas de 6 em 6 horas se dor ou febre"}]}` |

## Garantias de privacidade verificáveis em `test_receita.py`

1. **Descarte de dados pessoais**: todas as receitas contêm `"Paciente: Paciente Fictício"`, nome de médico e CRM fictício, mas `receita.extrair()` devolve **exclusivamente** `{"medicamentos": [{"nome": str, "posologia": str}]}` — `"Paciente Fictício"` nunca aparece no JSON retornado.
2. **Processamento em memória**: `receita.extrair()` recebe `bytes` e processa imagens (via base64 em memória) e PDFs (via `io.BytesIO` + `pypdf.PdfReader`) sem criar arquivos no disco.

