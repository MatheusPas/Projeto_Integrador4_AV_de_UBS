# Dados primários — UBS de Vitória-ES (C2)

Pedido do professor na C1 (seção 4.2): dados do DATASUS e lista de UBS da SEMUS, com fonte e data.
Município: Vitória-ES (código IBGE 3205309; código no DATASUS 320530). População: 322.869 habitantes (Censo IBGE 2022).

## 1. Lista de UBS (SEMUS)

- **29 Unidades Básicas de Saúde**, com endereço, telefone e horário de cada uma, em `data/kb/ubs_vitoria.md` (é a mesma base que o chat usa para responder).
- Seis unidades têm **horário ampliado** (noite, fim de semana e feriado): Jardim Camburi, Maruípe, Maria Ortiz, Praia do Suá, Santo Antônio e São Pedro V.
- Há **2 Prontos Atendimentos 24 h**: Praia do Suá e São Pedro.
- **Fonte:** Prefeitura de Vitória/SEMUS, https://www.vitoria.es.gov.br/semus/unidades-basicas-de-saude. A lista foi atualizada pela SEMUS em 20/05/2024 e acessada em 26/10/2026.

## 2. DATASUS — CNES

| Dado | Valor | Fonte e data |
|---|---|---|
| Estabelecimentos do tipo "Centro de Saúde/Unidade Básica" em Vitória | **30**: 28 "Unidade Básica de Saúde", a Unidade de Saúde do Quadro e o Serviço de Orientação ao Exercício (SOE, que não é UBS) | CNES/DATASUS, https://cnes2.datasus.gov.br/Mod_Ind_Unidade_Listar.asp?VTipo=02&VListar=1&VEstado=32&VMun=320530. Consultado em 28/10/2026; a página não informa a competência. |

Sem contar o SOE, o CNES registra 29 unidades, o mesmo número da lista da SEMUS. A fonte federal confirma a municipal.

## 3. Dados a completar no DATASUS (consulta manual)

Os painéis abaixo só abrem por formulário. Preencha o valor, a competência e a data da consulta.

| Dado | Como obter | Valor | Competência | Consultado em |
|---|---|---|---|---|
| Equipes de Saúde da Família (eSF) e de Atenção Primária (eAP) | https://cnes2.datasus.gov.br/Mod_Ind_Equipes.asp → Estado: Espírito Santo → Município: Vitória → competência mais recente → Consultar | | | |
| Cobertura da Atenção Primária (%) | https://egestorab.saude.gov.br → Relatórios públicos → Cobertura da APS → ES / Vitória | | | |
| Atendimentos individuais na APS | https://sisab.saude.gov.br → Relatórios → Saúde/Produção → Município Vitória-ES → competências de 2025 → "Atendimento individual" | | | |

## 4. Outros dados (fontes secundárias, não oficiais)

| Dado | Fonte |
|---|---|
| A rede municipal faz em média **326 mil consultas por mês** (médicas, odontológicas, multiprofissionais e especializadas). Cerca de 32 mil podem ser agendadas pela internet. | Jornal A Tribuna, 27/03/2025: https://tribunaonline.com.br/_/234889 |
| Em 2022, Vitória tinha **22 farmácias** nas Unidades de Saúde, todas com farmacêutico | Artigo na revista Physis, 2024: https://scielosp.org/pdf/physis/2024.v34/e34002/pt (conferir no PDF antes de citar) |

## 5. Por que esses dados importam para o projeto

- As UBS fazem centenas de milhares de consultas por mês e cada farmácia municipal tem um farmacêutico. Isso reforça o argumento da C1: um chat que responde às dúvidas simples sobre medicamentos alivia o atendimento presencial.
- A lista oficial das 29 UBS é a base das respostas administrativas do chat: horário, endereço e onde retirar remédio.
