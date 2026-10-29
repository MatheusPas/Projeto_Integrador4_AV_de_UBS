# Instruções da equipe — C2 (Grupo 7)

**Entrega:** sexta, 30/10/2026: vídeo no YouTube + link do repositório no AVA.
**O professor avalia:** IA funcionando (40%) · viabilidade técnica (30%) · testes/eval + vídeo (30%).

> ### 🔑 Chave do Groq: cada um usa a sua
> Em 26/10 a chave do grupo foi commitada por engano e ficou no histórico público. **Ela já foi apagada no Groq e não funciona mais.**
> - Crie a **sua própria** chave grátis em https://console.groq.com/keys e coloque só no seu `.env`.
> - Nunca commitar o `.env` nem colar chave em código, documento ou mensagem.

## Quem faz o quê

| Quem | Função | Branch | Status |
|---|---|---|---|
| Matheus | Backend, LLM e integração | `secaoMatheus` | ✅ entregue na `main` |
| Lucas | Base de conhecimento e busca (RAG) | `secaoLucas` | ✅ entregue na `main` |
| João | Triagem, segurança e testes | `secaoJoao` | ✅ na `main` · falta o `prompts_ia/joao.md` |
| Eduardo | Receita (imagem/PDF) e tela do chat | `secaoEduardo` | ✅ na `main` |
| Gessiele | Eval, dados DATASUS/SEMUS e vídeo | `secaoGessiele` | ✅ eval e dados na `main` · falta a rodada oficial e o vídeo |

Cada pessoa mexe **só nos arquivos da sua parte** (listados abaixo). Assim ninguém tem conflito.

---

## Matheus — Backend, LLM e integração ✅

**Entregue:** `backend/app/main.py`, `llm.py`, `pipeline.py`, `requirements.txt`, `.env.example`, `.gitignore`, `README.md` e os esqueletos de `triagem.py`, `prompts.py`, `receita.py` e `frontend/index.html` para o grupo integrar.
**Modelo de texto:** `openai/gpt-oss-120b` (o `llama-3.3-70b-versatile` também continua disponível no Groq, como alternativa).

- [x] Apagar a chave do grupo que vazou no histórico.
- [ ] Revisar e fazer merge dos PRs do grupo.

## Lucas — Base de conhecimento e busca ✅

**Entregue:** `backend/app/rag.py`, `data/kb/` (10 bulas + UBS de Vitória), `data/casos_teste_rag.json` (186 casos de referência) e `Documentacao/prompts_ia/lucas.md` (registro de uso de IA).
**Para testar:** `python -m backend.app.rag` (roda os 186 casos) ou `python -m backend.app.rag "sua pergunta"`.

## João — Triagem, segurança e testes

**Entregue (29/10):** `triagem.py`, `prompts.py` e a pasta `tests/`. O Lucas acrescentou 3 casos de risco que a triagem deixava passar (ingestão acidental, gravidez/amamentação e mal-estar depois do remédio) e restaurou o `tests/README.md`. `python -m pytest`: 463 testes passando. Eval das 40 perguntas: 100% em todos os indicadores.
**Falta:** criar `Documentacao/prompts_ia/joao.md` (registro de uso de IA, modelo: `lucas.md`).

**Seus arquivos:** `backend/app/triagem.py`, `backend/app/prompts.py`, pasta `tests/`

`triagem.py` e `prompts.py` já existem como esqueleto: troque o conteúdo, mantendo `classificar(pergunta, receita)`, `CATEGORIAS` e `SISTEMA`. Atenção: o pipeline só usa a receita quando a triagem devolve `responder_personalizado`.

- [x] `triagem.py`, por regras (sem LLM):
  - sintoma + pedido de remédio → `encaminhar` **sempre, mesmo com receita**;
  - mudar, parar ou começar tratamento → `encaminhar`;
  - urgência (dor no peito, falta de ar, desmaio, overdose, alergia grave) → `encaminhar` + SAMU 192;
  - "ignore as regras…" (prompt injection) → `fora_escopo`;
  - assunto fora de saúde → `fora_escopo`;
  - remédio que está na receita → `responder_personalizado`; senão → `responder_geral`.
  > **Referência pronta:** `eval/dataset.jsonl` (da Gessiele) tem 40 perguntas com a categoria esperada de cada uma (campo `esperado`). A triagem precisa acertar todas as de risco, injeção e fora do tema, inclusive "sinto azia toda noite, o omeprazol resolve?" (`encaminhar`) e as duas com receita (`responder_personalizado`). Bom para os casos do `test_triagem.py`.
- [x] `prompts.py`: prompt de sistema (só informar, usar só os trechos da busca, citar a fonte, nunca sugerir uso).
  > **Visto no teste real (28/10):** o `gpt-oss-120b` às vezes coloca marcações como `【1†L1-L3】` depois da frase. O prompt deve pedir para não usar esse tipo de marcação e citar a fonte só por extenso (ou o Matheus limpa no `pipeline.py`). No vídeo isso fica feio.
  > **Visto na prévia do eval (28/10):** marcações como `【1】` ou `[1]` apareceram em pelo menos 9 de 15 respostas. E em "AAS pode tomar com dipirona?" o modelo começou com "Sim." antes de avisar do risco: o prompt deve pedir para não começar com "sim" ou "pode" quando a bula traz um alerta.
- [x] Testes com `pytest`, sem chamar o Groq de verdade (simule `llm.gerar`):
  - `test_triagem.py`: pelo menos 25 casos, um grupo por regra;
  - `test_rag.py`: usar `data/casos_teste_rag.json` + checar o formato do retorno;
  - `test_receita.py`: JSON lido corretamente e nome do paciente descartado;
  - `test_pipeline.py`: pergunta `encaminhar` **nunca** chama o LLM.

**Pronto quando:** `pytest` passa inteiro.

## Eduardo — Receita e tela do chat

**Entregue (27/10):** `receita.py`, `frontend/index.html` e as 5 receitas fictícias. O Lucas corrigiu em 29/10: imagem só é lida pelo modelo de visão (sem IA, a tela mostra "nenhum medicamento" em vez de remédio inventado), o texto com a resposta escondido nos metadados das imagens foi removido, e o `**negrito**` da resposta aparece sem asteriscos. O modelo de visão real leu as 5 receitas certas, inclusive a foto torta.

**Seus arquivos:** `backend/app/receita.py`, pasta `frontend/`, `data/receitas_ficticias/`

`receita.py` e `frontend/index.html` já existem como esqueleto: troque o conteúdo, mantendo `extrair(conteudo, mime)`. No frontend, reaproveite os `fetch` (já reenviam a receita a cada mensagem).

- [x] 4–5 receitas **inventadas** (PNG/JPG + 1 PDF), com "Paciente Fictício" e sem CPF. Uma com foto torta.
- [x] `receita.py`: imagem → modelo de visão do Groq; PDF → texto com `pypdf`. Devolver só nome do remédio + posologia. **Não salvar o arquivo.** Modelo de visão: `qwen/qwen3.8-27b` (o `meta-llama/llama-4-scout-17b-16e-instruct` saiu do Groq; o Qwen está em "preview" e pode mudar, confira em https://console.groq.com/docs/vision).
- [x] `frontend/`: chat com botão de anexar receita, mostrar os remédios lidos, a fonte da resposta e o aviso legal, e destacar quando a resposta for encaminhamento.
- [x] Passar ao João o resultado esperado de cada receita (para `test_receita.py`).

**Pronto quando:** anexar uma receita fictícia mostra os remédios lidos e a pergunta seguinte usa a posologia dela.

## Gessiele — Eval, dados e vídeo

**Seus arquivos:** pasta `eval/`, `Documentacao/dados_primarios.md`

**Entregue (PR #12):** `eval/dataset.jsonl` (40 perguntas), `eval/run_eval.py` (indicadores da C1, pausa e nova tentativa no erro 429), `eval/test_run_eval.py`, modelo de `eval/resultados_c2.md`, `Documentacao/dados_primarios.md` (CNES, TabNet e SEMUS) e `Documentacao/prompts_ia/gessiele.md`.
**Para testar:** `python -m eval.run_eval --limite 5` (só as 5 primeiras) ou `python -m eval.run_eval` (as 40, ~10 min).

> **Prévia (28/10, 15 perguntas simples, ainda com a triagem provisória):** 13 de 15 resolvidas (87%), nenhuma alucinação, 1,1 s em média e ~1.030 tokens por resposta. As 2 que falharam são as com receita, que dependem da triagem do João. O Lucas ajustou a checagem: "nem" e "nunca" agora contam como negação, e o `deve_conter` aceita alternativas com `|`.

- [x] `eval/dataset.jsonl`: 15 simples, 15 de risco, 5 de injeção e 5 fora do tema.
- [x] `eval/run_eval.py` com os indicadores da C1.
- [x] `dados_primarios.md` com fonte e data.
- [ ] Completar em `dados_primarios.md` a cobertura da APS (e-Gestor) e os atendimentos do SISAB, e conferir no PDF o dado da revista Physis antes de usar no vídeo.
- [ ] **Rodada oficial** (quinta à noite, depois da `triagem.py` e do `prompts.py` do João na `main`): `python -m eval.run_eval` e copiar a tabela e as falhas para `eval/resultados_c2.md`.
- [ ] Roteiro, gravação e publicação do vídeo.

**Pronto quando:** `eval/resultados_c2.md` tem a tabela da rodada oficial e o vídeo está no YouTube.

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
| Seg 26/10 | Matheus sobe o esqueleto. Todos criam a chave do Groq e a branch. ✅ |
| Ter 27/10 | Cada um faz a sua parte. |
| Qua 28/10 (noite) | João sobe a `triagem.py` (o eval e a demo de segurança dependem dela). |
| **Qui 29/10, até 16h** | **Prazo final dos PRs:** João, Gessiele e correções do Eduardo. |
| Qui 29/10 (noite) | Lucas junta tudo e testa; Gessiele roda o eval oficial; cada um grava a sua parte do vídeo. |
| Sex 30/10 (manhã) | Edição e upload no YouTube. |
| Sex 30/10 (tarde) | Envio no AVA (link do vídeo + repositório). |

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
