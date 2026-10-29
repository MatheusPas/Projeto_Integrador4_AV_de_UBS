# Uso de IA — Gessiele Lima (C2)

Registro exigido pelo edital (seção 11). Ferramenta: **Claude Code** (Anthropic), usado como assistente de programação e pesquisa. As decisões de escopo, as fontes aceitas e a revisão final foram minhas.

## Planejamento

- **Prompt:** "Siga as instruções de `Documentacao/C2_Instrucoes_da_Equipe.md` e verifique se eu já posso fazer a minha parte (eval, dados DATASUS/SEMUS e vídeo) ou se dependo de alguém."
- **Uso da IA:** leitura das instruções e do repositório. A conclusão foi que só a rodada oficial do eval depende da triagem e do prompt do João.

## Eval (`eval/`)

- **Prompt:** "Faça o que é possível sem termos a parte do João, sem dar commit e sem o roteiro do vídeo."
- **Uso da IA:** criação das 40 perguntas de `eval/dataset.jsonl` (com termos esperados e termos que contradizem a bula, tirados de `data/kb/`), do `eval/run_eval.py` (indicadores da C1, pausa entre perguntas, nova tentativa no erro 429), do teste `eval/test_run_eval.py` (com o LLM simulado) e do modelo de `eval/resultados_c2.md`.
- **Minhas decisões:** seguir a divisão de 40 perguntas e as metas da C1; usar só receitas fictícias; fazer agora o que não depende da triagem do João e deixar a rodada oficial para depois do merge dela; não usar a IA para o roteiro do vídeo, que será feito no fim, com o grupo.

## Dados primários (`Documentacao/dados_primarios.md`)

- **Prompt:** pesquisa de dados do DATASUS (CNES, e-Gestor, SISAB) e da SEMUS sobre Vitória, com fonte e data, sem inventar números.
- **Uso da IA:** busca na web, consultas ao CNES e ao TabNet/DATASUS (equipes de saúde e produção ambulatorial de Vitória) e organização das fontes. A cobertura da APS e o SISAB ficaram marcados para consulta manual.
- **Minhas decisões:** priorizar fontes oficiais (DATASUS e Prefeitura) com competência e data de consulta; separar como "fontes secundárias" os números de jornal e de artigo; não usar números sem fonte confirmada.

## Commits e Pull Request

- **Prompt:** regras de trabalho com o git (só os meus arquivos, `git add` por arquivo, commits no meu nome e sem assinatura de IA, nunca commitar `.env` ou chave).
- **Uso da IA:** commits pequenos na branch `secaoGessiele`, push e texto do Pull Request.
- **Minhas decisões:** aprovar cada etapa antes do commit e abrir o PR eu mesma.

## Revisão

- [x] Li as 40 perguntas e os termos esperados de cada uma.
- [x] Conferi no TabNet os números de equipes e de produção e completei a cobertura da APS e o SISAB.
- [x] Rodei `python -m eval.run_eval` com a triagem do João e preenchi `eval/resultados_c2.md`.
- [x] Sei explicar o eval no vídeo.
