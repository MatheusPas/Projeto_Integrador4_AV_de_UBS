# Uso de IA — João (C2)

Registro exigido pelo edital (seção 11). Ferramenta: **ChatGPT / Codex (OpenAI)**, usada como assistente de programação. Seleção dos principais prompts, resumidos por atividade.

## Triagem (`backend/app/triagem.py`)

- **Prompt:** "Implemente a triagem por regras conforme os contratos da equipe, sem usar LLM, cobrindo encaminhamento, urgências, injeção de prompt e classificação com ou sem receita."
- **Uso da IA:** implementação das regras de classificação e ajustes de compatibilidade com os casos do eval.
- **Minhas decisões:** manter a prioridade dos encaminhamentos mesmo com receita; preservar como informativas as perguntas sobre metformina com álcool e esquecimento de sinvastatina, conforme o dataset da Gessiele. Manter `classificar(pergunta, receita)` e `CATEGORIAS` compatíveis com o pipeline.

## Prompt de sistema (`backend/app/prompts.py`)

- **Prompt:** "Ajuste o prompt para responder somente com os trechos recuperados, sem sugerir tratamento. Evite marcações de citação e apresente os alertas da bula antes de qualquer resposta afirmativa."
- **Uso da IA:** redação e ajuste das instruções de segurança e do formato das respostas.
- **Minhas decisões:** deixar as fontes na interface, sem 'Fonte:' ou marcadores como `【1】` no texto; impedir respostas iniciadas com 'Sim' quando houver alerta na bula; manter o caráter informativo do assistente.

## Testes (`tests/`)

- **Prompt:** "Crie testes com pytest para triagem, RAG, receita e pipeline, simulando as chamadas ao Groq e verificando que encaminhamentos nunca chamam o LLM."
- **Uso da IA:** criação e ajuste dos testes automatizados, incluindo regressões das categorias do eval.
- **Minhas decisões:** aproveitar os casos de referência do Lucas e as receitas fictícias do Eduardo; verificar os contratos de retorno e o descarte do nome do paciente; manter os testes independentes de chamadas reais à API.
