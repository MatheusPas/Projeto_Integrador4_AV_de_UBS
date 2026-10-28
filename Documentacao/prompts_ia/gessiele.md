# Uso de IA — Gessiele Lima (C2)

Registro exigido pelo edital (seção 11). Ferramenta: **Claude Code** (Anthropic), usado como assistente de programação e pesquisa. As decisões de escopo, as fontes aceitas e a revisão final foram minhas.

## Planejamento

- **Prompt:** "Siga as instruções de `Documentacao/C2_Instrucoes_da_Equipe.md` e verifique se eu já posso fazer a minha parte (eval, dados DATASUS/SEMUS e vídeo) ou se dependo de alguém."
- **Uso da IA:** leitura das instruções e do repositório. A conclusão foi que só a rodada oficial do eval depende da triagem e do prompt do João.

## Eval (`eval/`)

- **Prompt:** "Faça o que é possível sem termos a parte do João, sem dar commit e sem o roteiro do vídeo."
- **Uso da IA:** criação das 40 perguntas de `eval/dataset.jsonl` (com termos esperados e termos que contradizem a bula, tirados de `data/kb/`), do `eval/run_eval.py` (indicadores da C1, pausa entre perguntas, nova tentativa no erro 429), do teste `eval/test_run_eval.py` (com o LLM simulado) e do modelo de `eval/resultados_c2.md`.
- **Minhas decisões:** <!-- ex.: revisar as perguntas, os termos esperados e as metas --> 

## Dados primários (`Documentacao/dados_primarios.md`)

- **Prompt:** pesquisa de dados do DATASUS (CNES, e-Gestor, SISAB) e da SEMUS sobre Vitória, com fonte e data, sem inventar números.
- **Uso da IA:** busca na web e organização das fontes. Os dados que dependem de formulário do DATASUS ficaram marcados para consulta manual.
- **Minhas decisões:** <!-- ex.: quais fontes aceitar e conferência dos números --> 

## Commits e Pull Request

- **Prompt:** regras de trabalho com o git (só os meus arquivos, `git add` por arquivo, commits no meu nome e sem assinatura de IA, nunca commitar `.env` ou chave).
- **Uso da IA:** commits pequenos na branch `secaoGessiele`, push e texto do Pull Request.
- **Minhas decisões:** aprovar cada etapa antes do commit e abrir o PR eu mesma.

## Revisão

- [ ] Li as 40 perguntas e os termos esperados de cada uma.
- [ ] Preenchi os dados do DATASUS que faltavam e conferi as fontes.
- [ ] Rodei `python -m eval.run_eval` com a triagem do João e preenchi `eval/resultados_c2.md`.
- [ ] Sei explicar o eval no vídeo.
