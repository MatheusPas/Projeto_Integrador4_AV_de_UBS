# Instruções da equipe — C3 (Grupo 7)

**Entrega:** sexta, 04/12/2026: vídeo do MVP no YouTube + link do repositório no AVA.
**O edital pede:** vídeo do MVP, documentação, código-fonte, testes + eval, **URL pública do deploy** e **análise de impacto**.
**O professor avalia (6,0):** funcionalidade/usabilidade/inovação (35%) · qualidade da IA e eval (25%) · testes automatizados (15%) · deploy + documentação/código (15%) · impacto e IA responsável (10%).

> **Chave do Groq:** continua valendo a regra da C2. Cada um usa a sua, só no `.env`, nunca em código, documento ou mensagem. No deploy, a chave vai **só no painel do Render** (variável de ambiente).

## Quem faz o quê

| Quem | Função na C3 | Branch | Status |
|---|---|---|---|
| Matheus | Deploy no Render e ajustes da API | `secaoMatheus` | a fazer |
| João | Testes da API, CI no GitHub e ajustes do prompt | `secaoJoao` | a fazer |
| Eduardo | Usabilidade da tela e voz (ouvir e falar) | `secaoEduardo` | a fazer |
| Gessiele | Eval da C3, análise de impacto e vídeo | `secaoGessiele` | a fazer |
| Lucas | IA responsável, README final e integração | `secaoLucas` | a fazer |

Cada pessoa mexe **só nos arquivos da sua parte** (listados abaixo). Antes de começar: `git switch main`, `git pull` e depois `git switch secao<SeuNome>` + `git merge main`.

---

## Matheus — Deploy no Render e API

**Seus arquivos:** `render.yaml` (novo), `requirements.txt`, `backend/app/main.py`, `backend/app/llm.py`

- [ ] Criar o serviço no Render (plano grátis, Web Service, Python) ligado ao repositório, branch `main`.
  - Build: `pip install -r requirements.txt`
  - Start: `uvicorn backend.app.main:app --host 0.0.0.0 --port $PORT --proxy-headers --forwarded-allow-ips="*"`
  - Variáveis no painel: `GROQ_API_KEY` (a sua chave), `PYTHON_VERSION=3.12.10`.
  - Registrar isso num `render.yaml` na raiz, **sem a chave**.
- [ ] **Atenção ao limite por IP:** o `main.py` usa `request.client.host`. Atrás do proxy do Render, sem `--proxy-headers`, esse é o IP do Render, e **todos os usuários dividem o mesmo limite de 20/min**. Com a flag acima, passa a ser o IP real. Confira depois do deploy.
- [ ] Rota `GET /saude` devolvendo `{"status": "ok"}`, para o Render checar se o serviço está no ar.
- [ ] Fixar as versões no `requirements.txt` (as que funcionam hoje: fastapi 0.162.0, uvicorn 0.54.0, groq 1.7.0, scikit-learn 1.9.1, pypdf 6.21.3, python-multipart 0.0.32, python-dotenv 1.2.4, pytest 9.2.0, httpx 0.28.1).
- [ ] Testar a URL pública: pergunta simples, receita fictícia e pergunta de risco.
- [ ] Passar a URL pública para o grupo e escrever em `Documentacao/deploy.md` (novo) como foi feito.

> O plano grátis do Render "dorme" depois de 15 min sem uso e leva ~1 min para acordar. Antes de gravar o vídeo, abra a URL e espere carregar.

**Pronto quando:** a URL pública abre a tela e responde as 3 perguntas de teste.

## João — Testes da API, CI e prompt

**Seus arquivos:** `tests/test_api.py` (novo), `.github/workflows/testes.yml` (novo), `backend/app/prompts.py`, `backend/app/triagem.py`

- [ ] `tests/test_api.py` com o `TestClient` do FastAPI (LLM simulado, como nos outros testes):
  - `POST /chat` devolve o formato certo; pergunta vazia ou com mais de 1000 caracteres dá erro 422;
  - `POST /receita` aceita PNG/JPG/PDF, recusa outro tipo e recusa arquivo maior que 10 MB;
  - o limite por IP devolve 429 depois de `LIMITE_POR_MINUTO` chamadas;
  - `GET /saude` (depois do PR do Matheus).
- [ ] GitHub Actions rodando `python -m pytest` a cada push e PR (sem chave do Groq: os testes não chamam a API).
- [ ] `prompts.py`, os dois problemas que o eval da C2 achou:
  - o modelo **acrescentou informação que não está na bula** (pergunta do AAS com dipirona);
  - o modelo **inventou horários de exemplo** ("8 h, 16 h e 24 h") numa resposta com receita.
- [ ] Coloque um teste para cada regra nova da triagem, se mexer nela.

**Pronto quando:** `python -m pytest` passa inteiro e o check verde aparece nos PRs do GitHub.

## Eduardo — Usabilidade e voz

**Seus arquivos:** `frontend/index.html`

- [ ] **Ouvir a resposta:** botão "🔊 Ouvir" em cada resposta, usando o `speechSynthesis` do navegador (voz pt-BR). Ajuda idosos e quem tem pouca leitura.
- [ ] **Perguntar falando:** botão de microfone usando o `SpeechRecognition` do navegador (pt-BR). Se o navegador não tiver suporte, o botão some.
- [ ] Aviso "Acordando o servidor, aguarde…" quando a primeira resposta demorar (o Render grátis dorme).
- [ ] Tela boa no celular (testar com 375 px de largura) e fonte confortável.
- [ ] Nada de `innerHTML` com texto do modelo: continue usando `textContent`, como já está.

**Pronto quando:** dá para fazer uma pergunta por voz, ouvir a resposta e usar tudo no celular.

## Gessiele — Eval da C3, impacto e vídeo

**Seus arquivos:** pasta `eval/`, `Documentacao/analise_impacto.md` (novo), roteiro e vídeo

- [ ] Corrigir o critério da s04 (`"deve_conter": ["dobr|duas doses"]`).
- [ ] Ampliar o `eval/dataset.jsonl` para ~70 perguntas, com perguntas novas de **robustez**:
  - a mesma dúvida escrita de outro jeito ("dá pra tomar…", "pode misturar…");
  - erros de digitação ("metformia", "losartan");
  - perguntas sem acento e em caixa alta.
- [ ] Eval da **leitura de receita**: as 5 receitas de `data/receitas_ficticias/` comparadas com o `esperado.json` (acerto de nome e posologia).
- [ ] **Rodada oficial da C3** depois dos PRs do João e do Matheus, com a tabela em `eval/resultados_c3.md` e comparação com a C2.
- [ ] `analise_impacto.md`: os indicadores previstos na C1 × o que medimos (eval, custo, tempo) + os dados de `dados_primarios.md` (29 UBS, ~101 mil atendimentos/mês). Ex.: quantas respostas por dia cabem no plano grátis; o que o assistente resolve sem ida à UBS; o que ele encaminha.
- [ ] Roteiro e edição do vídeo da C3 (o da C2 serve de base).

**Pronto quando:** `eval/resultados_c3.md` tem a tabela da rodada oficial e o vídeo está no YouTube.

## Lucas — IA responsável, README e integração

**Seus arquivos:** `Documentacao/ia_responsavel.md` (novo), `README.md`, `data/kb/`, este documento

- [ ] `ia_responsavel.md`: LGPD (dados usados, base legal, minimização), segurança (prompt injection e mitigação), ética e viés (limites do modelo), custo (tokens e limites do plano grátis).
- [ ] README final: URL do deploy, link do vídeo, resumo da C3 e links para os documentos.
- [ ] Revisar e fazer o merge dos PRs do grupo; testar tudo junto antes da gravação.

**Pronto quando:** o README tem a URL pública e o vídeo, e a `main` tem todas as partes.

---

## Para todos

- Registrar o uso de IA da C3 no seu `Documentacao/prompts_ia/<seu-nome>.md`, numa seção "C3" (exigência do edital, seção 11).
- Avaliação 360 da C3 em `Avaliacao360/C3/`.
- Commits pequenos, `git add <arquivo>` (nunca `git add .`), e PR para a `main` (nunca push direto na `main`).

## Cronograma

| Dia | O quê |
|---|---|
| Seg 23/11 | Instruções no ar. Cada um atualiza a branch com a `main`. |
| **Qua 25/11** | **Matheus: URL pública no ar** (o resto do grupo testa nela). |
| **Qui 26/11** | **João: PR do prompt** (o eval oficial depende dele). |
| **Dom 29/11, até 18h** | **Prazo final dos PRs de todos.** |
| Seg 30/11 | Lucas junta tudo e testa no deploy; Gessiele roda o eval oficial da C3. |
| Ter 01/12 – Qua 02/12 | Gravação das falas e das telas. |
| Qui 03/12 | Edição e upload no YouTube. |
| **Sex 04/12** | **Envio no AVA** (link do vídeo + repositório). |

## Vídeo (6–8 min)

1. Problema e comunidade, com os dados oficiais (30 s)
2. O que mudou da C2 para a C3: deploy, voz, eval ampliado (1 min)
3. Demo **na URL pública** (3 min): pergunta simples com fonte · pergunta por voz e resposta ouvida · receita fictícia · pergunta de risco encaminhada · tentativa de manipulação bloqueada
4. Testes (CI verde) e eval da C3 comparado com a C2 (1,5 min)
5. Impacto e IA responsável (1 min)
6. Limitações e próximos passos (30 s)

## Problemas comuns

| Problema | Solução |
|---|---|
| URL do Render demora a abrir | O plano grátis dorme: espere ~1 min na primeira vez. |
| Todo mundo recebe erro 429 no deploy | Falta o `--proxy-headers` no comando de start (ver a parte do Matheus). |
| Conflito no `git merge main` | Arquivo seu: mantenha a sua versão. Arquivo de outra pessoa: não mexa e chame o dono. |
| Erro 429 do Groq | Limite do plano gratuito: espere 1 minuto. Nos testes, use o LLM simulado. |
| Commitei o `.env` ou uma chave | Apague a chave no Groq na hora, gere outra e avise o grupo. |
