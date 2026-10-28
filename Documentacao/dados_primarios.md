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

**Ainda não obtido.** Os painéis abaixo só abrem por formulário interativo no navegador:

| Dado | Como obter |
|---|---|
| Cobertura da Atenção Primária (%) | https://egestorab.saude.gov.br → Relatórios públicos → Cobertura da APS → ES / Vitória |
| Atendimentos individuais nas UBS (SISAB) | https://sisab.saude.gov.br → Relatórios → Saúde/Produção → Município Vitória-ES → competências de 2025 → "Atendimento individual" |

## 4. Outros dados (fontes secundárias, não oficiais)

| Dado | Fonte |
|---|---|
| A rede municipal faz em média **326 mil consultas por mês** (médicas, odontológicas, multiprofissionais e especializadas). Cerca de 32 mil podem ser agendadas pela internet. | Jornal A Tribuna, 27/03/2025: https://tribunaonline.com.br/_/234889 |
| Em 2022, Vitória tinha **22 farmácias** nas Unidades de Saúde, todas com farmacêutico | Artigo na revista Physis, 2024: https://scielosp.org/pdf/physis/2024.v34/e34002/pt (conferir no PDF antes de citar) |

## 5. Por que esses dados importam para o projeto

- Vitória tem 29 UBS, 124 equipes de Saúde da Família e de Atenção Primária, centenas de milhares de consultas por mês e um farmacêutico em cada farmácia municipal. Isso reforça o argumento da C1: um chat que responde às dúvidas simples sobre medicamentos alivia o atendimento presencial.
- A lista oficial das 29 UBS é a base das respostas administrativas do chat: horário, endereço e onde retirar remédio.
