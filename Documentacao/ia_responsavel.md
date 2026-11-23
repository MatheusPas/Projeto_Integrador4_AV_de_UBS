# IA responsável e governança — C3

Seção 7 do edital: privacidade e LGPD, segurança, ética e viés, custo e sustentabilidade.
Cada afirmação aponta o arquivo do código que a implementa, para poder ser conferida.
Itens marcados *(em andamento)* dependem de partes da C3 ainda em desenvolvimento e serão atualizados antes da entrega.

## 1. Privacidade e LGPD

### Que dados o sistema usa

| Dado | Origem | Pessoal? | Onde fica |
|---|---|---|---|
| Bulas do paciente dos 10 medicamentos | Fabricantes, conforme bula aprovada pela Anvisa | Não | `data/kb/*.md`, com fonte e data de acesso |
| Lista e horários das 29 UBS de Vitória | Prefeitura de Vitória/SEMUS | Não | `data/kb/ubs_vitoria.md` |
| Indicadores do DATASUS e e-Gestor APS | Ministério da Saúde (dados agregados por município) | Não | `Documentacao/dados_primarios.md` |
| Pergunta digitada pelo usuário | Usuário | Pode conter dado de saúde | Só em memória, durante a resposta |
| Receita enviada (imagem ou PDF) | Usuário | **Sim: dado de saúde (sensível)** | Só em memória, durante a leitura |
| IP de quem acessa | Conexão | Sim | Só em memória, por 60 s, para o limite de uso |

### Caminho dos dados e o que é descartado

- **O servidor não guarda nada.** Não há banco de dados nem log do conteúdo das perguntas (`backend/app/main.py`, `pipeline.py`). A receita lida volta para o navegador, que a mantém numa variável da página e a reenvia a cada pergunta (`frontend/index.html`). Ao recarregar a página, ela some.
- **O arquivo da receita nunca é gravado em disco**: é lido em memória (`backend/app/receita.py`). Há teste que confere que nenhum arquivo é criado (`tests/test_receita.py`).
- **Minimização na saída:** da receita, só voltam o nome do remédio e a posologia. Nome do paciente, CPF, médico e CRM são descartados (`_PADRAO_DADOS_PESSOAIS` em `receita.py`), e a API recusa qualquer campo além de `medicamentos` (`Receita` em `main.py`). Há testes para os dois (`tests/test_receita.py`, `tests/test_pipeline.py`).
- **Minimização no envio ao modelo de texto:** o LLM recebe só a pergunta, os trechos da bula e, apenas quando a triagem identifica que a pergunta é sobre a receita, a lista de remédios com a posologia. Nunca recebe o nome do paciente (`_montar_pergunta` em `pipeline.py`; teste `test_nome_do_paciente_e_dados_extras_nao_chegam_ao_llm`).

### Limite que precisa ficar claro

**A imagem da receita é enviada inteira ao modelo de visão do Groq** (`_chamar_visao_groq` em `receita.py`), e o texto de um PDF também, quando a leitura local não reconhece o formato. O descarte do nome do paciente acontece **depois**, na resposta. Ou seja, um terceiro (o Groq, com servidores fora do Brasil) processa a receita completa.

Por isso:

- o MVP é demonstrado **só com receitas fictícias** ("Paciente Fictício", sem CPF), e a tela avisa para não enviar dados reais;
- para uso com pacientes reais seria necessário: consentimento específico e destacado do titular (LGPD, art. 11, I, por ser dado de saúde), contrato de tratamento de dados com o provedor (ou um modelo de visão rodando localmente) e um aviso de privacidade completo.

### Base legal (cenário de uso real)

- **Pergunta sem dado pessoal:** não há tratamento de dado pessoal.
- **Receita e perguntas com dado de saúde:** consentimento do titular (art. 11, I), restrito à finalidade de explicar a posologia, sem guardar nada.
- **IP para limite de uso:** legítimo interesse de proteger o serviço contra abuso (art. 7º, IX), guardado só por 60 segundos.

## 2. Segurança

| Risco (OWASP Top 10 para LLM) | O que o sistema faz | Onde |
|---|---|---|
| **Prompt injection** ("ignore as regras…") | A triagem por regras bloqueia tentativas antes de chegarem ao LLM, inclusive com caracteres invisíveis no meio da palavra. O prompt de sistema manda tratar pergunta, receita e trechos como dados, nunca como instruções. | `INJECOES` em `triagem.py`; `prompts.py`; 10 casos em `tests/test_triagem.py` |
| **Pedido de diagnóstico ou receita** (uso indevido) | Sintoma + pedido de remédio, mudança de tratamento e urgência são encaminhados à UBS ou ao SAMU 192 com resposta fixa. **O LLM nem é chamado.** | `triagem.py`, `pipeline.py`; teste `test_encaminhamento_nunca_chama_llm_ou_busca` |
| **Alucinação / informação errada** | O LLM responde só com trechos da base. Se a busca não acha nada, a resposta é "a fonte não cobre essa dúvida", sem chamar o modelo. Toda resposta mostra a fonte e o aviso legal. | `MSG_SEM_FONTE` em `pipeline.py`; `rag.py`; `frontend/index.html` |
| **Saída insegura (XSS)** | O texto do modelo entra na tela como texto puro (`textContent`), nunca como HTML. Só o negrito `**…**` vira `<strong>`, também sem HTML. | `frontend/index.html` |
| **Abuso / esgotar a cota** | Limite de mensagens por IP por minuto, pergunta de até 1.000 caracteres, receita de até 10 MB e só nos tipos PNG, JPG, WEBP ou PDF. | `main.py` |
| **Vazamento de chave** | A chave do Groq fica só no `.env` (fora do Git) e, no deploy, na variável de ambiente do servidor. | `.gitignore`, `.env.example` |

**Incidente real e lição aprendida:** em 26/10/2026 a chave do grupo foi commitada por engano e ficou no histórico público do GitHub. Ela foi revogada no Groq no mesmo período, cada integrante passou a usar a sua chave, e o procedimento ("apagar o arquivo não basta: revogar a chave na hora") entrou nas instruções da equipe.

## 3. Ética e viés

**O assistente só informa.** Ele não diagnostica, não indica remédio, não muda tratamento e não substitui o farmacêutico ou o médico. Isso aparece no aviso fixo da tela, em toda resposta e no prompt de sistema.

Limitações conhecidas e como são tratadas:

| Limitação | Efeito possível | Cuidado adotado |
|---|---|---|
| Base com **10 medicamentos** | Dúvidas sobre outros remédios ficam sem resposta | O sistema diz que a fonte não cobre e orienta a procurar a UBS, em vez de inventar |
| Triagem por **regras de palavras** | Uma forma de escrever não prevista pode escapar (falso negativo) | Regras conservadoras (na dúvida, encaminha) e 208 testes de triagem; perguntas de robustez no eval da C3 *(em andamento)* |
| **Português padrão** | Gírias, regionalismos e erros de digitação podem confundir a busca e a triagem | Eval da C3 com perguntas escritas de outros jeitos e com erros de digitação *(em andamento)* |
| **O LLM pode acrescentar o que não está na bula** | Visto no eval da C2 (pergunta do AAS com dipirona) e numa resposta com receita que inventou horários de exemplo | Registrado em `eval/resultados_c2.md`; leitura manual das respostas do eval; reforço do prompt na C3 *(em andamento)* |
| **Público com pouca leitura ou idoso** | Dificuldade de usar um chat só de texto | Ouvir a resposta e perguntar por voz, na C3 *(em andamento)* |
| **Leitura da receita por visão** | O modelo pode errar um nome ou uma dose em foto ruim | A tela mostra os remédios lidos para a pessoa conferir, e o prompt de resposta proíbe completar dose, horário ou palavra ilegível (`prompts.py`) |

## 4. Custo e sustentabilidade

| Item | Valor medido | Fonte |
|---|---|---|
| Tokens por resposta do LLM | ~1.630 (média), 2.044 (máximo) | `eval/resultados_c2.md` |
| Limite do plano gratuito do Groq (`openai/gpt-oss-120b`) | 30 req/min · 8.000 tokens/min · 200.000 tokens/dia | Documentação do Groq, consultada em 28/10/2026 (`eval/run_eval.py`) |
| Respostas do LLM por dia no plano gratuito | ~122 | 200.000 ÷ 1.630 |
| Custo de pergunta encaminhada ou bloqueada | **0 tokens** (o LLM não é chamado) | `pipeline.py` |
| Busca na base | Local (TF-IDF), sem custo por consulta e sem API de embeddings | `rag.py` |
| Hospedagem | Plano gratuito do Render | `Documentacao/deploy.md` *(em andamento)* |

**Consequência para o uso real:** ~122 respostas por dia cobrem um piloto numa UBS, mas não a rede inteira (cerca de 101 mil atendimentos individuais por mês, segundo `dados_primarios.md`). Escalar exigiria um plano pago, ou um modelo menor para as perguntas simples, ou cache das dúvidas mais frequentes. O limite por IP impede que um único usuário esgote a cota do dia.

## 5. Governança

- **Atualização da base:** cada bula traz a data de aprovação pela Anvisa e a data de acesso. Bulas mudam: a base deve ser revisada a cada semestre ou quando o fabricante publicar uma versão nova.
- **Mudanças no código:** toda alteração entra por Pull Request revisado, e os testes automatizados rodam antes do merge.
- **Uso de IA no desenvolvimento:** registrado por integrante em `Documentacao/prompts_ia/` (edital, seção 11).
- **Responsabilidade:** o sistema é um protótipo acadêmico. Uso com pacientes reais dependeria de validação por farmacêuticos da rede municipal e das medidas de LGPD da seção 1.
