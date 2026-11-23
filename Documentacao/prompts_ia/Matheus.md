# Uso de IA — Matheus Alves Passos (C2)

Registro exigido pelo edital (seção 11). Ferramenta: **Claude Code** (Anthropic, modelo Claude Opus 5.5), usado como assistente de programação. As decisões de arquitetura, a revisão do código e o merge foram meus.

## Pedido inicial

- **Prompt:** "Suba o esqueleto com as funções da seção Contratos devolvendo dados falsos (menos `rag.py`) e um `.gitignore` com `.env`, `.venv/` e `__pycache__/`."
- **Uso da IA:** criação dos arquivos de configuração e das funções falsas com a mesma assinatura dos contratos.
- **Minhas decisões:** marcar cada arquivo falso como "ESQUELETO" com o nome do responsável que vai substituí-lo; incluir `httpx` no `requirements.txt` para o João poder testar a API com o `TestClient`.

## LLM (`backend/app/llm.py`)

- **Prompt:** "Chamada ao Groq (`llama-3.3-70b-versatile`), devolvendo texto + tokens; erro 429 vira mensagem amigável."
- **Uso da IA:** implementação da chamada e do tratamento de erros.
- **Minhas decisões:** temperatura baixa (0,2) para a resposta seguir a bula; o chat nunca mostra erro 500 — falta de chave, limite (429) e falha de conexão viram mensagem para o usuário.

## Pipeline (`backend/app/pipeline.py`)

- **Prompt:** "Triagem → busca → LLM. Se a triagem disser `encaminhar` ou `fora_escopo`, não chama o LLM. Se a busca vier vazia, responde 'a fonte não cobre essa dúvida'. Toda resposta leva o aviso 'não substitui orientação médica ou farmacêutica'."
- **Uso da IA:** implementação e testes com o LLM simulado (mock).
- **Minhas decisões:** a mensagem de encaminhamento sempre cita o SAMU 192; na resposta personalizada, quando a pergunta não cita o remédio ("esqueci de tomar meu remédio"), o nome vem da receita para a busca achar a bula certa — ajuste feito depois de o teste mostrar que a busca trazia bulas de outros remédios.

## API (`backend/app/main.py`) e tela provisória (`frontend/index.html`)

- **Prompt:** "`POST /chat`, `POST /receita`, servir `frontend/`, limite de requisições por IP."
- **Uso da IA:** implementação da API, do limite por IP em memória e de uma tela mínima para testar o chat.
- **Minhas decisões:** limite configurável no `.env` (padrão 20 por minuto) para proteger a cota gratuita do Groq; receita só como imagem ou PDF até 10 MB, lida em memória e nunca salva; a tela é provisória e será substituída pela do Eduardo.

## README

- **Prompt:** "README: como rodar e a regra 'nenhum dado real de paciente'."
- **Uso da IA:** redação do README.

## Revisão

- [x] `uvicorn backend.app.main:app` sobe, a tela abre em `/` e `POST /chat` responde.
- [x] Testado com o LLM simulado: pergunta encaminhada **não** chama o LLM; busca vazia devolve "a fonte não cobre".
- [x] `python -m backend.app.rag` continua com os 186 casos passando.
- [x] Testado com a chave do Groq: resposta geral (losartana) e personalizada (metformina esquecida) corretas e com fonte.
- [x] Sei explicar o pipeline e a API no vídeo.

---

# Uso de IA — Matheus Alves Passos (C3)

Mesma ferramenta da C2: **Claude Code** (Anthropic, modelo Claude Opus 5.5). Parte da C3: deploy no Render e ajustes da API (ver `Documentacao/C3_Instrucoes_da_Equipe.md`). Trabalho feito na branch `secaoMatheus`, atualizada a partir da `main`, com um commit por alteração.

## Rota de saúde (`backend/app/main.py`)

- **Prompt:** "Faça as tarefas do Matheus em `C3_Instrucoes_da_Equipe.md`, na branch `secaoMatheus`, com um commit por alteração e atualizando o `Matheus.md`."
- **Uso da IA:** criação da rota `GET /saude` devolvendo `{"status": "ok"}`, declarada antes de montar o `frontend/` para não ser escondida por ele.
- **Minhas decisões:** a rota é `GET`, então não conta no limite por IP (que só vale para `POST`) — o Render pode checá-la à vontade sem gastar a cota de ninguém.

## Versões fixas (`requirements.txt`)

- **Prompt:** mesmo pedido acima (tarefa "fixar as versões no `requirements.txt`").
- **Uso da IA:** troca dos nomes soltos por versões exatas (`==`), conferindo no PyPI que todas existem.
- **Minhas decisões:** usar as versões da lista das instruções (as que funcionam hoje), para o Render instalar sempre o mesmo ambiente testado e uma versão nova de biblioteca não quebrar o deploy sem aviso.

## Configuração do Render (`render.yaml`)

- **Prompt:** mesmo pedido acima (tarefa "registrar o serviço num `render.yaml` na raiz, sem a chave").
- **Uso da IA:** escrita do `render.yaml` (Web Service Python, plano grátis, branch `main`, build e start das instruções, `healthCheckPath: /saude`, `PYTHON_VERSION=3.12.10`).
- **Minhas decisões:** a `GROQ_API_KEY` entra com `sync: false`, ou seja, o Render pede o valor no painel e ela nunca vai para o repositório. O start usa `--proxy-headers --forwarded-allow-ips="*"`; conferi localmente com `LIMITE_POR_MINUTO=1` e o cabeçalho `X-Forwarded-For`: o mesmo IP recebe 429 na 2ª chamada, mas outro IP continua recebendo 200 — sem a flag, todos dividiriam o limite do IP do proxy.

## Documentação do deploy (`Documentacao/deploy.md`)

- **Prompt:** mesmo pedido acima (tarefa "escrever em `Documentacao/deploy.md` como foi feito").
- **Uso da IA:** redação do passo a passo (Blueprint lendo o `render.yaml`, chave só no painel), da explicação do limite por IP atrás do proxy e da tabela das 3 perguntas de teste.
- **Minhas decisões:** as perguntas de teste foram conferidas na triagem antes de entrar no documento ("Tomei a cartela inteira…" cai em `encaminhar` com o SAMU 192; "Para que serve a losartana?" cai em `responder_geral`). A URL pública e a coluna "Resultado" ficam para preencher depois do deploy, que é feito na minha conta do Render.

## Revisão (C3)

- [x] `GET /saude` devolve `{"status": "ok"}` e a tela continua abrindo em `/`.
- [x] `python -m pytest`: 463 testes passando com as versões fixas.
- [x] Limite por IP conferido localmente com `--proxy-headers`.
- [ ] Serviço criado no Render e URL pública no ar.
- [ ] As 3 perguntas de teste respondidas na URL pública e anotadas em `deploy.md`.
- [ ] URL passada para o grupo.
