# Uso de IA — Eduardo Guedes (C2)

Registro exigido pelo edital (seção 11). Ferramenta: **Antigravity (Google DeepMind)**, usado como assistente de programação e pesquisa. As decisões de escopo, privacidade, escolha do modelo de visão e revisão final foram minhas.

## Verificação do modelo de visão do Groq (`backend/app/receita.py`)

- **Prompt:** "Confira na documentação do Groq (`console.groq.com/docs/models` e `deprecations`) se o modelo `meta-llama/llama-4-scout-17b-16e-instruct` continua ativo ou qual modelo de visão o substituiu."
- **Uso da IA:** consulta à documentação oficial do Groq, verificando que o `meta-llama/llama-4-scout-17b-16e-instruct` foi descontinuado em 17/07/2026 e que o modelo multimodal de visão ativo na plataforma é o `qwen/qwen3.8-27b`.
- **Minhas decisões:** configurar `MODELO_VISAO = os.getenv("GROQ_MODELO_VISAO", "qwen/qwen3.8-27b")` em `backend/app/receita.py`, permitindo sobrescrita via `.env`.

## Extração de receitas em memória (`backend/app/receita.py`)

- **Prompt:** "Implemente `extrair(conteudo: bytes, mime: str)` mantendo o contrato `{'medicamentos': [{'nome': str, 'posologia': str}]}`, usando o modelo de visão do Groq para imagens e `pypdf` em memória para PDF, descartando o nome do paciente e sem salvar arquivos no disco."
- **Uso da IA:** implementação da leitura de PDF com `pypdf.PdfReader(io.BytesIO(conteudo))`, envio de imagens em base64 para o Groq Vision e sanitização do JSON para remover dados pessoais (`Paciente Fictício`, CPF, CRM) e padronizar os nomes dos medicamentos de acordo com a base `data/kb/`.
- **Minhas decisões:** garantir que nenhum arquivo temporário seja gravado em disco e suportar simulação (`mock`) nos testes automatizados do `pytest`.

## Receitas fictícias (`data/receitas_ficticias/`)

- **Prompt:** "Gere 5 receitas médicas inventadas (4 imagens PNG/JPG, sendo uma foto torta, e 1 PDF) com 'Paciente Fictício', sem CPF, cobrindo os medicamentos da base `data/kb/`, junto com o resultado esperado para os testes do João (`test_receita.py`)."
- **Uso da IA:** geração das 4 imagens (incluindo `receita_03_gastrite_colesterol_torta.jpg` rotacionada simulando foto inclinada) e do PDF `receita_05_cardiovascular.pdf`, além da tabela e do `esperado.json`.
- **Minhas decisões:** usar exclusivamente dados fictícios ("Paciente Fictício", sem CPF) e medicamentos presentes nas bulas do projeto.

## Tela do chat (`frontend/index.html`)

- **Prompt:** "Substitua o esqueleto do `frontend/index.html` por uma interface completa para usuários das UBS de Vitória, reaproveitando os `fetch('/receita')` e `fetch('/chat')`, exibindo os remédios lidos, a fonte da resposta, o aviso legal e destacando respostas de encaminhamento."
- **Uso da IA:** construção do layout responsivo, cards de medicamentos lidos da receita, destaque visual de encaminhamento (SAMU 192 / UBS), exibição separada da fonte e do aviso legal.
- **Minhas decisões:** manter a compatibilidade com os endpoints `/receita` e `/chat` e reenviar a receita em memória a cada mensagem.

## Revisão

- [x] Conferi as 5 receitas geradas em `data/receitas_ficticias/` (nenhum dado real, todas com "Paciente Fictício" e sem CPF, incluindo 1 PDF e 1 foto torta).
- [x] Verifiquei que `receita.extrair(conteudo, mime)` retorna apenas `{"medicamentos": [{"nome", "posologia"}]}` e descarta o nome do paciente.
- [x] Testei a tela do chat (`frontend/index.html`) com anexo de receita, exibição dos remédios lidos, perguntas seguintes usando a posologia, fonte, aviso legal e destaque de encaminhamento.
- [x] Documentei o resultado esperado de cada receita em `data/receitas_ficticias/README.md` e `data/receitas_ficticias/esperado.json` para o João (`test_receita.py`).

