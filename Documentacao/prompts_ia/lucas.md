# Uso de IA — Lucas Paton (C2)

Registro exigido pelo edital (seção 11). Ferramenta: **Claude Code** (Anthropic), usado como assistente de programação e pesquisa. As decisões de escopo, as fontes aceitas e a revisão final foram minhas.

## Base de conhecimento (`data/kb/`)

- **Prompt:** "Monte as bulas dos 10 medicamentos mais usados na atenção básica a partir da bula do paciente oficial, em linguagem simples, sem doses, citando a fonte."
- **Uso da IA:** extração e resumo do texto das bulas e pesquisa dos dados das UBS no site da SEMUS.
- **Minhas decisões:** quais medicamentos entram; usar a bula publicada pelo fabricante quando o Bulário da Anvisa bloqueou o acesso; manter só informação educativa, sem dose.

## Busca RAG (`backend/app/rag.py`)

- **Prompt:** "Implemente `buscar(pergunta, k)` conforme o contrato da equipe, retornando vazio quando a base não cobrir a pergunta."
- **Uso da IA:** implementação da busca TF-IDF e ajustes guiados pelos testes (pistas por seção, nomes comerciais, limiar).
- **Minhas decisões:** exigir que a busca não invente resposta fora da base e que funcione pelo nome comercial do remédio.

## Casos de teste (`data/casos_teste_rag.json`)

- **Prompt:** "Crie casos de teste completos da busca para apoiar os testes do João, sem fazer a parte dele."
- **Uso da IA:** geração e execução dos 186 casos.
- **Minhas decisões:** cobrir todas as seções, marcas, UBS, interações e perguntas fora do tema; deixar os testes automatizados com o responsável (João).

## Organização da equipe (`Documentacao/C2_Instrucoes_da_Equipe.md`)

- **Prompt:** "Com base no edital e no relatório da C1, divida a C2 em 5 funções e escreva instruções práticas para cada integrante."
- **Uso da IA:** redação do documento.
- **Minhas decisões:** quem faz cada função, nomes das branches e o formato final das instruções.

## Revisão

- [ ] Li as 10 bulas e conferi com os PDFs citados na linha `Fonte:` de cada arquivo (atenção ao `aas.md`).
- [ ] Rodei `python -m backend.app.rag` e os 186 casos passaram.
- [ ] Sei explicar o funcionamento da busca no vídeo.
