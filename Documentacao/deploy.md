# Deploy no Render

**URL pública:** _a preencher depois do primeiro deploy_ (ex.: `https://assistente-ubs-vitoria.onrender.com`)

O assistente roda como um único **Web Service** do Render (plano grátis): a mesma aplicação FastAPI serve a API (`/chat`, `/receita`, `/saude`) e a tela (`frontend/`). A configuração está em [`render.yaml`](../render.yaml), na raiz.

## Configuração

| Item | Valor |
|---|---|
| Tipo | Web Service, runtime Python, plano Free |
| Repositório / branch | este repositório, branch `main` (deploy automático a cada merge) |
| Build | `pip install -r requirements.txt` (versões fixas) |
| Start | `uvicorn backend.app.main:app --host 0.0.0.0 --port $PORT --proxy-headers --forwarded-allow-ips="*"` |
| Health check | `GET /saude` → `{"status": "ok"}` |
| Variáveis | `PYTHON_VERSION=3.12.10` e `GROQ_API_KEY` (**só no painel**, nunca no repositório) |

## Como foi feito

1. No [Render](https://dashboard.render.com), **New → Blueprint**, ligado ao repositório do GitHub. O Render lê o `render.yaml` e cria o serviço com build, start, health check e `PYTHON_VERSION`.
2. Na criação, o Render pede o valor da `GROQ_API_KEY` (declarada com `sync: false` no `render.yaml`). A chave foi colada **só ali**.
3. Primeiro deploy: acompanhar os logs até aparecer `Uvicorn running on http://0.0.0.0:...` e o health check ficar verde.
4. Abrir a URL pública e fazer os testes abaixo.

> Alternativa sem Blueprint: **New → Web Service**, escolher o repositório e preencher à mão os campos da tabela acima.

## Limite por IP atrás do proxy

O `main.py` limita a 20 chamadas `POST` por minuto por IP (`request.client.host`). No Render, as requisições chegam pelo proxy dele; sem `--proxy-headers`, esse IP seria o do proxy e **todos os usuários dividiriam o mesmo limite**. Com `--proxy-headers --forwarded-allow-ips="*"`, o uvicorn usa o IP real do cabeçalho `X-Forwarded-For`.

Conferido localmente com `LIMITE_POR_MINUTO=1`: duas chamadas com o mesmo `X-Forwarded-For` → 200 e depois 429; uma terceira com outro IP → 200. Depois do deploy, conferir com duas pessoas (ou celular no 4G + computador) mandando mensagens ao mesmo tempo.

## Testes na URL pública

| Teste | Pergunta / ação | Esperado | Resultado |
|---|---|---|---|
| Saúde | abrir `<URL>/saude` | `{"status": "ok"}` | _a preencher_ |
| Pergunta simples | "Para que serve a losartana?" | resposta com a fonte (bula) e o aviso | _a preencher_ |
| Receita fictícia | enviar `data/receitas_ficticias/receita_01_diabetes_hipertensao.png` e perguntar "Como devo tomar meus remédios?" | nomes e posologia lidos, resposta personalizada | _a preencher_ |
| Pergunta de risco | "Tomei a cartela inteira de remédio, o que faço?" | não chama o LLM; encaminha para atendimento e cita o SAMU 192 | _a preencher_ |

## Plano grátis: cuidados

- O serviço **dorme depois de 15 min sem uso** e leva ~1 min para acordar. Antes de gravar o vídeo, abra a URL e espere carregar.
- O limite por IP fica em memória e zera quando o serviço reinicia ou dorme.
- Se a chave vazar: apagar no Groq, gerar outra e trocar só no painel do Render (**Environment → GROQ_API_KEY**); o Render refaz o deploy sozinho.
