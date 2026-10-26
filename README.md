# Assistente de medicamentos para usuários de UBS — Vitória-ES

Projeto Integrador IV (Grupo 7). Chat que tira dúvidas sobre os medicamentos mais usados na
atenção básica, com base nas bulas oficiais e nos dados das UBS de Vitória. Ele **só informa**:
pergunta com sintoma, pedido de remédio ou mudança de tratamento é encaminhada à UBS
(ou ao SAMU 192, em urgência).

## ⚠️ Regra: nenhum dado real de paciente

- Use só receitas **inventadas**, com "Paciente Fictício" e sem CPF (`data/receitas_ficticias/`).
- Não cole nome, CPF, cartão do SUS ou receita de pessoa real no chat, nos testes ou no repositório.
- O servidor não guarda nada: a receita é lida em memória e o arquivo é descartado.

## Como rodar

```bash
python -m venv .venv
.venv\Scripts\Activate.ps1          # Linux/Mac: source .venv/bin/activate
pip install -r requirements.txt
```

O `.env` com a chave do Groq do grupo já vem no repositório. Para usar uma chave sua
(gratuita em https://console.groq.com/keys), troque o `GROQ_API_KEY` no `.env`.

```bash
uvicorn backend.app.main:app --reload
```

Abra http://localhost:8000.

## Como funciona

```
pergunta ─► triagem ─► busca (RAG) ─► LLM (Groq) ─► resposta + fonte + aviso
              │             │
              │             └─ nada na base: "a fonte não cobre essa dúvida"
              └─ encaminhar / fora do escopo: resposta fixa, sem chamar o LLM
```

| Arquivo | O que faz |
|---|---|
| `backend/app/main.py` | API: `POST /chat`, `POST /receita`, serve `frontend/`, limite de requisições por IP |
| `backend/app/pipeline.py` | `responder(pergunta, receita)`: triagem → busca → LLM |
| `backend/app/llm.py` | Chamada ao Groq (`openai/gpt-oss-120b`); erro 429 vira mensagem amigável |
| `backend/app/triagem.py` | Classifica a pergunta: responder, encaminhar ou fora do escopo |
| `backend/app/rag.py` | Busca TF-IDF nas bulas de `data/kb/` |
| `backend/app/receita.py` | Lê a receita (imagem ou PDF) e devolve remédio + posologia |
| `backend/app/prompts.py` | Prompt de sistema do LLM |
| `frontend/` | Tela do chat |

### API

- `POST /chat` — corpo `{"pergunta": "...", "receita": {"medicamentos": [{"nome", "posologia"}]} | null}`;
  devolve `{"resposta", "categoria", "fontes", "tokens", "latencia_ms"}`.
- `POST /receita` — formulário com o campo `arquivo` (PNG, JPG, WEBP ou PDF, até 10 MB);
  devolve `{"medicamentos": [{"nome", "posologia"}]}`. O frontend reenvia esse JSON a cada `/chat`.

Cada IP pode fazer até `LIMITE_POR_MINUTO` (padrão 20) requisições por minuto.

## Testes

```bash
pytest                       # testes automatizados (sem chamar o Groq de verdade)
python -m backend.app.rag    # 186 casos de referência da busca
```

## Equipe

Veja `Documentacao/C2_Instrucoes_da_Equipe.md`. Uso de IA registrado em `Documentacao/prompts_ia/`.
