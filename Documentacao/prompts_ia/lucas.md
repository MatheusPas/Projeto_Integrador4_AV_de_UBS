# Registro de uso de IA — Lucas Paton (C2)

Exigência do edital, seção 11: todo trabalho feito com auxílio de IA fica registrado com o prompt usado.

**Ferramenta:** Claude Code (modelo Claude Opus 5.5), no app Claude para desktop
**Data:** 26/10/2026
**Parte do projeto:** Função 2 — base de conhecimento e busca (RAG)

## Prompts e resultado

| # | Prompt (resumo fiel do pedido) | O que a IA produziu |
|---|---|---|
| 1 | Revisar o edital e o relatório da C1 e dividir a C2 em 5 funções para 5 pessoas aplicarem e commitarem no projeto. | Documento de divisão de tarefas da C2 (hoje `Documentacao/C2_Instrucoes_da_Equipe.md`). |
| 2 | Redistribuir: programação com o Matheus, base de conhecimento com o Lucas, testes com o João, eval/vídeo com a Gessiele. | Atualização das funções no documento. |
| 3 | Deixar o documento bem explicado para os outros integrantes fazerem suas partes com facilidade. | Guia passo a passo (ambiente, Git, problemas comuns). |
| 4 | Fazer a minha parte sem depender de ninguém, na branch `secaoLucas`. | `backend/app/rag.py` (busca TF-IDF) e `data/kb/ubs_vitoria.md` a partir do site da SEMUS/PMV. |
| 5 | Montar as bulas dos 10 medicamentos. O Bulário da Anvisa bloqueou acesso automatizado; usamos a bula do paciente publicada pelo próprio fabricante (texto aprovado pela Anvisa). | 10 arquivos em `data/kb/` com fonte, link e data de aprovação; sem doses em mg. |
| 6 | Os casos de teste precisam ser bem apurados para um trabalho profissional (apenas conclusões para auxiliar o João, sem fazer a parte dele). | `data/casos_teste_rag.json` com 186 casos. Os testes revelaram falhas na busca, corrigidas em `rag.py`: pistas por seção, nomes comerciais, limiar calibrado. |
| 7 | Verificação geral da minha parte e das branches para trabalho em equipe. | Conferência de estrutura dos arquivos, dos 186 casos num clone limpo e deste registro. |

## Como o resultado foi verificado

- `python -m backend.app.rag` roda os 186 casos de referência: 186/186 passando.
- Conteúdo de cada bula escrito a partir do PDF do fabricante citado na linha `Fonte:` do arquivo.
- Conferido por Lucas (marcar ao revisar):
  - [ ] li as 10 bulas em `data/kb/` e conferi com os PDFs dos links;
  - [ ] conferi `aas.md` com atenção (lido pela tela do navegador, não por extração de texto);
  - [ ] entendi o funcionamento de `rag.py` e sei explicá-lo no vídeo.
