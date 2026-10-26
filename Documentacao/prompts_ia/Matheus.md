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
- [ ] Sei explicar o pipeline e a API no vídeo.
