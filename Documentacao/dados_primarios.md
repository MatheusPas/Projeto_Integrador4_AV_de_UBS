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

## 3. DATASUS — equipes e produção (TabNet)

**Equipes de saúde ativas em Vitória**, competência set/2026, consultado em 28/10/2026.
Fonte: TabNet/DATASUS, "CNES - Equipes de Saúde - Espírito Santo" (http://tabnet.datasus.gov.br/cgi/deftohtm.exe?cnes/cnv/equipees.def). Filtro: Município = Vitória; Linha = Tipo da Equipe.

| Tipo de equipe | Quantidade |
|---|---|
| eSF — Saúde da Família (código 70) | 86 |
| eSF nos códigos antigos (01 ESF e 02 ESF com saúde bucal) | 7 |
| eAP — Atenção Primária | 31 |
| eSB — Saúde Bucal | 91 |
| eMulti/NASF — Núcleo Ampliado de Saúde da Família | 27 |
| eCR — Consultório na Rua | 2 |
| EACS — Agentes Comunitários de Saúde | 1 |
| **Total** | **245** |

Somando os códigos novos e os antigos, são 93 equipes de Saúde da Família e 31 de Atenção Primária para 29 UBS: em média, mais de 4 equipes por unidade.

**Produção ambulatorial do SUS realizada em Vitória em 2025** (jan a dez/2025, quantidade aprovada), consultado em 28/10/2026.
Fonte: TabNet/DATASUS, "Produção Ambulatorial do SUS - Espírito Santo - por local de atendimento" (SIA/SUS, http://tabnet.datasus.gov.br/cgi/deftohtm.exe?sia/cnv/qaes.def). Filtro: Município = Vitória; Linha = Complexidade.

| Complexidade | Procedimentos aprovados em 2025 |
|---|---|
| Atenção Básica | 176.129 |
| Média complexidade | 7.658.750 |
| Alta complexidade | 7.015.563 |
| Não se aplica | 6.369 |
| **Total** | **14.856.811** |

Cuidados ao citar:
- "Por local de atendimento" conta tudo o que foi feito em Vitória, incluindo hospitais e serviços estaduais que atendem a Grande Vitória.
- A maior parte da produção das UBS (consultas, visitas) é registrada no SISAB, e não no SIA. Por isso a linha "Atenção Básica" do SIA fica baixa.

**Cobertura potencial da Atenção Primária**, competência jul/2026, consultado em 29/10/2026.
Fonte: e-Gestor APS/Ministério da Saúde, "Cobertura Potencial da APS (2021 - atual)" (https://relatorioaps.saude.gov.br/cobertura/aps). Filtro: Municípios = Vitória-ES; competência CNES ago/2025 a jul/2026.

| Dado (jul/2026) | Valor |
|---|---|
| População usada pelo Ministério | 343.378 |
| Equipes de Saúde da Família (eSF) | 86 |
| Equipes de Atenção Primária (eAP), 20 h e 30 h | 18 (2 + 16) |
| Equipes de Consultório na Rua (eCR) | 2 |
| Capacidade de atendimento das equipes (pessoas) | 346.500 |
| **Cobertura potencial da APS** | **100,90%** |

A cobertura ficou entre 100,03% e 101,30% em todos os meses de ago/2025 a jul/2026. "Potencial" quer dizer que a capacidade instalada das equipes comporta toda a população; não quer dizer que todos são atendidos. O antigo endereço do e-Gestor (egestorab.saude.gov.br) não responde mais; os relatórios públicos passaram para relatorioaps.saude.gov.br.

**Atendimentos individuais na Atenção Primária (SISAB)**, consultado em 29/10/2026.
Fonte: SISAB/Ministério da Saúde, relatório "Saúde: Atendimento/Visita" (https://sisab.saude.gov.br/paginas/acessoRestrito/relatorio/federal/saude/RelSauProducao.xhtml). Filtro: Município = Vitória; Tipo de Produção = Atendimento Individual; Linha = Competência.

| Período | Atendimentos individuais | Média por mês |
|---|---|---|
| jan a set/2026 | 908.031 | **100.892** |
| 2025 (ano inteiro) | 986.773 | 82.231 |

Cuidados ao citar:
- Use o número de **2026 (~101 mil por mês)**, que é estável: todos os meses ficaram entre 87.839 e 115.941.
- Em 2025 a série muda de patamar: cerca de 37 mil por mês de jan a mai/2025, depois cerca de 100 mil por mês a partir de jun/2025, com um pico de 178.444 em jul/2025. O mais provável é uma mudança na forma de envio dos dados ao SISAB, e não no atendimento. Por isso o total de 2025 subestima a produção real.
- "Atendimento individual" conta consultas de médicos, enfermeiros e outros profissionais de nível superior nas equipes da APS. Não inclui atendimento odontológico, procedimentos nem visitas domiciliares (relatados à parte no SISAB).

## 4. Outros dados (fontes secundárias, não oficiais)

| Dado | Fonte |
|---|---|
| A rede municipal faz em média **326 mil consultas por mês** (médicas, odontológicas, multiprofissionais e especializadas). Cerca de 32 mil podem ser agendadas pela internet. | Jornal A Tribuna, 27/03/2025: https://tribunaonline.com.br/_/234889 |
| Em 2022, Vitória tinha **22 farmácias** nas Unidades de Saúde, todas com farmacêutico | Artigo na revista Physis, 2024: https://scielosp.org/pdf/physis/2024.v34/e34002/pt (não conferido: o PDF fica atrás de uma verificação anti-robô; não usar no vídeo sem conferir) |

## 5. Por que esses dados importam para o projeto

- Vitória tem 29 UBS, cobertura potencial da Atenção Primária de 100,9% e cerca de 101 mil atendimentos individuais por mês nas equipes da APS (SISAB, 2026). Com essa demanda, cada dúvida simples sobre medicamento que o chat responde é um atendimento presencial a menos, o que reforça o argumento da C1.
- A lista oficial das 29 UBS é a base das respostas administrativas do chat: horário, endereço e onde retirar remédio.
