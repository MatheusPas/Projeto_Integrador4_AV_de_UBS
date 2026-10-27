# Instruções da equipe — C2 (Grupo 7)

**Entrega:** sexta, 30/10/2026: vídeo no YouTube + link do repositório no AVA.
**O professor avalia:** IA funcionando (40%) · viabilidade técnica (30%) · testes/eval + vídeo (30%).

> ### 🚨 A chave do Groq do grupo vazou (26/10)
> O `.env` com a chave do grupo foi commitado por engano e, mesmo removido depois, **continua no histórico público do GitHub**. Quem abrir os commits antigos consegue copiar a chave.
> - **Matheus:** apagar essa chave em https://console.groq.com/keys (é isso que a torna inútil).
> - **Todos:** criar a **sua própria** chave grátis no mesmo link e colocar só no seu `.env`. Não existe mais chave do grupo.
> - Nunca commitar o `.env` nem colar chave em código, documento ou mensagem.

## Quem faz o quê

| Quem | Função | Branch | Status |
|---|---|---|---|
| Matheus | Backend, LLM e integração | `secaoMatheus` | ✅ entregue na `main` (falta apagar a chave vazada) |
| Lucas | Base de conhecimento e busca (RAG) | `secaoLucas` | ✅ entregue na `main` |
| João | Triagem, segurança e testes | `secaoJoao` | a fazer |
| Eduardo | Receita (imagem/PDF) e tela do chat | `secaoEduardo` | a fazer |
| Gessiele | Eval, dados DATASUS/SEMUS e vídeo | `secaoGessiele` | a fazer |

Cada pessoa mexe **só nos arquivos da sua parte** (listados abaixo). Assim ninguém tem conflito.

---

## Matheus — Backend, LLM e integração ✅

**Entregue:** `backend/app/main.py`, `llm.py`, `pipeline.py`, `requirements.txt`, `.env.example`, `.gitignore`, `README.md` e os esqueletos de `triagem.py`, `prompts.py`, `receita.py` e `frontend/index.html` para o grupo integrar.
**Mudança:** o Llama 3.3 saiu do Groq; o modelo agora é `openai/gpt-oss-120b`.

- [ ] **Agora:** apagar a chave vazada em https://console.groq.com/keys.
- [ ] Revisar e fazer merge dos PRs do grupo.

## Lucas — Base de conhecimento e busca ✅

**Entregue:** `backend/app/rag.py`, `data/kb/` (10 bulas + UBS de Vitória), `data/casos_teste_rag.json` (186 casos de referência) e `Documentacao/prompts_ia/lucas.md` (registro de uso de IA).
**Para testar:** `python -m backend.app.rag` (roda os 186 casos) ou `python -m backend.app.rag "sua pergunta"`.

## João — Triagem, segurança e testes

**Seus arquivos:** `backend/app/triagem.py`, `backend/app/prompts.py`, pasta `tests/`

`triagem.py` e `prompts.py` já existem como esqueleto: troque o conteúdo, mantendo `classificar(pergunta, receita)`, `CATEGORIAS` e `SISTEMA`. Atenção: o pipeline só usa a receita quando a triagem devolve `responder_personalizado`.

- [ ] `triagem.py`, por regras (sem LLM):
  - sintoma + pedido de remédio → `encaminhar` **sempre, mesmo com receita**;
  - mudar, parar ou começar tratamento → `encaminhar`;
  - urgência (dor no peito, falta de ar, desmaio, overdose, alergia grave) → `encaminhar` + SAMU 192;
  - "ignore as regras…" (prompt injection) → `fora_escopo`;
  - assunto fora de saúde → `fora_escopo`;
  - remédio que está na receita → `responder_personalizado`; senão → `responder_geral`.
- [ ] `prompts.py`: prompt de sistema (só informar, usar só os trechos da busca, citar a fonte, nunca sugerir uso).
- [ ] Testes com `pytest`, sem chamar o Groq de verdade (simule `llm.gerar`):
  - `test_triagem.py`: pelo menos 25 casos, um grupo por regra;
  - `test_rag.py`: usar `data/casos_teste_rag.json` + checar o formato do retorno;
  - `test_receita.py`: JSON lido corretamente e nome do paciente descartado;
  - `test_pipeline.py`: pergunta `encaminhar` **nunca** chama o LLM.

**Pronto quando:** `pytest` passa inteiro.

## Eduardo — Receita e tela do chat

**Seus arquivos:** `backend/app/receita.py`, pasta `frontend/`, `data/receitas_ficticias/`

`receita.py` e `frontend/index.html` já existem como esqueleto: troque o conteúdo, mantendo `extrair(conteudo, mime)`. No frontend, reaproveite os `fetch` (já reenviam a receita a cada mensagem).

- [ ] 4–5 receitas **inventadas** (PNG/JPG + 1 PDF), com "Paciente Fictício" e sem CPF. Uma com foto torta.
- [ ] `receita.py`: imagem → modelo de visão do Groq; PDF → texto com `pypdf`. Devolver só nome do remédio + posologia. **Não salvar o arquivo.** Antes de programar, confira em https://console.groq.com/docs/models qual modelo de visão está disponível (o Llama 3.3 já saiu do Groq; veja se o `meta-llama/llama-4-scout-17b-16e-instruct` continua).
- [ ] `frontend/`: chat com botão de anexar receita, mostrar os remédios lidos, a fonte da resposta e o aviso legal, e destacar quando a resposta for encaminhamento.
- [ ] Passar ao João o resultado esperado de cada receita (para `test_receita.py`).

**Pronto quando:** anexar uma receita fictícia mostra os remédios lidos e a pergunta seguinte usa a posologia dela.

## Gessiele — Eval, dados e vídeo

**Seus arquivos:** pasta `eval/`, `Documentacao/dados_primarios.md`

- [ ] `eval/dataset.jsonl` com ~40 perguntas: 15 simples, 15 de risco (sintoma, parar remédio, urgência), 5 de injeção, 5 fora do tema. Pode aproveitar perguntas de `data/casos_teste_rag.json`.
- [ ] `eval/run_eval.py`: chama `pipeline.responder()` e calcula os indicadores do relatório da C1. Coloque uma pausa entre as perguntas: o modelo `gpt-oss-120b` usa até 1500 tokens por resposta e o plano grátis devolve erro 429 se passar do limite.

  | Indicador | Meta |
  |---|---|
  | Encaminhamento correto (perguntas de risco) | ≥ 95% |
  | Resolução das dúvidas simples | ≥ 60% |
  | Alucinação (resposta contradiz a bula) | ≤ 5% |
  | Tempo de resposta | segundos |
  | Custo (tokens por conversa) | dentro do plano gratuito |

- [ ] `eval/resultados_c2.md`: tabela + o que falhou e por quê.
- [ ] `dados_primarios.md`: dados do DATASUS e lista de UBS da SEMUS, com fonte e data (pedido do professor na C1).
- [ ] Roteiro, gravação e publicação do vídeo.

**Pronto quando:** `python -m eval.run_eval` gera a tabela e o vídeo está no YouTube.

---

## Contratos (não mudar sem avisar o grupo)

```python
rag.buscar(pergunta, k=3) -> [{"texto", "fonte", "medicamento", "score"}]      # pronto
triagem.classificar(pergunta, receita) -> {"categoria", "motivo"}
    # categoria: "responder_personalizado" | "responder_geral" | "encaminhar" | "fora_escopo"
receita.extrair(conteudo: bytes, mime: str) -> {"medicamentos": [{"nome", "posologia"}]}
pipeline.responder(pergunta, receita) -> {"resposta", "categoria", "fontes", "tokens", "latencia_ms"}   # pronto
llm.gerar(sistema, usuario) -> {"texto", "tokens", "erro"}                     # pronto (simule nos testes)
```

API: `POST /receita` (envia o arquivo, recebe o JSON da receita) e `POST /chat` (`{"pergunta", "receita"}`). O servidor não guarda nada: o frontend reenvia a receita a cada mensagem.

## Primeira vez (≈15 min)

```bash
git clone https://github.com/MatheusPas/Projeto_Integrador4_AV_de_UBS.git
cd Projeto_Integrador4_AV_de_UBS
python -m venv .venv
.venv\Scripts\Activate.ps1          # Linux/Mac: source .venv/bin/activate
pip install -r requirements.txt
```

Crie sua chave gratuita em https://console.groq.com/keys, copie `.env.example` para `.env` e cole a chave. **Nunca commite o `.env`.**

## Como entregar (todo dia)

```bash
git switch main
git pull
git switch -c secao<SeuNome>        # só na 1ª vez; depois: git switch secao<SeuNome>
git merge main
git add <seus arquivos>
git commit -m "feat(triagem): regra de sintomas"
git push -u origin secao<SeuNome>
```

No GitHub: **Compare & pull request** → base `main`. O Matheus revisa e faz o merge.

- Commits pequenos e frequentes: eles contam na nota individual.
- Use `git add <arquivo>`, nunca `git add .`.
- Registre os prompts de IA que usou em `Documentacao/prompts_ia/<seu-nome>.md` (exigência do edital, seção 11). Modelo: `Documentacao/prompts_ia/lucas.md`.

## Cronograma

| Dia | O quê |
|---|---|
| Seg 26/10 | Matheus sobe o esqueleto. Todos criam a chave do Groq e a branch. |
| Ter 27/10 | Cada um faz a sua parte. |
| Qua 28/10 | PRs até 18h; integração à noite; Gessiele roda o eval. |
| Qui 29/10 | Correções; gravação do vídeo. |
| Sex 30/10 | Upload no YouTube e envio no AVA. |

## Vídeo (6–8 min, cada um apresenta a sua parte)

1. Problema e comunidade (30 s)
2. Arquitetura: triagem → busca → LLM (1 min)
3. Demo (3 min): pergunta simples com fonte · receita fictícia · "dor de cabeça, o que tomo?" encaminhado · tentativa de injeção bloqueada
4. Testes e eval (1,5 min)
5. Limitações e próximos passos (30 s)

## Problemas comuns

| Problema | Solução |
|---|---|
| `git push` dá erro 403 | Pedir ao Matheus para te adicionar como colaborador e aceitar o convite no e-mail. |
| Conflito no `git merge main` | Arquivo seu: mantenha a sua versão. Arquivo de outra pessoa: não mexa e chame o dono. |
| Erro 429 do Groq | Limite do plano gratuito: espere 1 minuto. Nos testes, use mock. |
| `ModuleNotFoundError` | Ative o ambiente virtual e rode `pip install -r requirements.txt`. |
| Commitei o `.env` ou uma chave | Apagar o arquivo **não basta**: a chave fica no histórico do GitHub. Apague a chave no Groq na hora, gere outra e avise o grupo. |
