# LarOuAyê — Banco de dados Oracle (Building Relational Database)

## Criar tudo do zero em um comando
SQL Developer: abra `00_executar_tudo.sql` e use **Executar Script (F5)**, com a pasta dos scripts como diretório de trabalho.
SQLcl/SQL*Plus: `cd` até esta pasta e `@00_executar_tudo.sql`.
O script **para no primeiro erro e desfaz** (`WHENEVER SQLERROR EXIT FAILURE ROLLBACK`) e pode ser rodado quantas vezes quiser.

| Arquivo | O que faz |
|---|---|
| `00_reset.sql` | Apaga tabelas, sequences e views, **sem erro se não existirem** (ignora ORA-00942/02289). Só em desenvolvimento. |
| `01_ddl.sql` | 9 sequences, 11 tabelas, constraints, comentários, índices. |
| `02_seed.sql` | **133 registros** de exemplo (ids < 1000; sequences começam em 1000). |
| `03_dml.sql` | 1 `UPDATE` e 1 `DELETE`, ambos com `WHERE`. |
| `04_consultas.sql` | As **10 consultas numeradas** (rode à parte e tire print de cada uma). |
| `05_views.sql` | 3 views de leitura: histórico, progresso e auditoria do conteúdo jurídico. |
| `06_verificacao.sql` | 6 auditorias de integridade: **todas devem retornar zero linhas**, mais contagem por tabela. |
| `docs/DICIONARIO-DADOS.md` | Dicionário de dados (gerado do DDL). |
| `docs/der.png` / `der.svg` | DER em pé-de-galinha (gerado do DDL). |
| `testes/testar_banco.py` | 52 verificações automáticas (ver abaixo). |

## O que torna o banco "à prova de falhas"
As regras valem **no banco**, não só no Java. Dado ruim é barrado mesmo se alguém gravar direto no SQL Developer.
- **Duplicidade:** e-mail único sem diferenciar maiúsculas (índice sobre `LOWER`), par (canal, id externo), código de categoria/etapa, ordem da etapa, ordem do cuidado.
- **Domínio:** as 27 UFs (`CHECK ... IN`), status e canais válidos, confiança de 0 a 1, links só `http`, código de categoria em maiúsculas, nomes/perguntas não podem ser só espaços, e-mail precisa de `@`.
- **Coerência:** `RESPONDIDA` sempre aponta uma orientação; as demais nunca apontam. `REVISADO` exige data. Telegram exige id externo.
- **Chaves estrangeiras:** pais com filhos de negócio (cidadão, categoria, orientação usada em consulta, etapa com progresso) **não podem ser apagados** (restrição). Filhos puros (cuidado, fonte legal, documento, ligação etapa×orientação) saem junto com o pai (`ON DELETE CASCADE`).
- **Auditoria (`06_verificacao.sql`):** pega o que `CHECK` não alcança, como `REVISADO` sem fonte legal, orientação ativa sem cuidado, etapa sem documento, buraco na ordem das etapas, categoria sem orientação ativa.

## Como foi testado (e o que NÃO foi)
`python3 testes/testar_banco.py` roda **52 verificações em SQLite** (aproximação do Oracle): estrutura, seed, DML, as 10 consultas, views, as 6 auditorias (inclusive provando que detectam o problema quando ele existe), 16 tentativas de gravar dado ruim que devem ser **barradas**, cascata, o reset e o script único, e que **todos os 9 INSERTs dos DAOs Java** batem com o DDL (colunas, `NOT NULL`, nº de valores).
**Não foi executado num Oracle real.** O `00_reset.sql` usa PL/SQL (`sys.odcivarchar2list`) que só roda no Oracle. Rodem `00_executar_tudo.sql` na conexão da FIAP e corrijam qualquer diferença de sintaxe (por exemplo, limite de `VARCHAR2`).

## Escopo do banco x exigências da disciplina
| Exigência | Atendido por |
|---|---|
| ≥ 6 tabelas | 11 tabelas |
| 2 relacionamentos 1:N | 7 (ex.: categoria→orientação, cidadão→consulta) |
| 1 relacionamento N:N com tabela associativa | `tb_cidadao_etapa` e `tb_etapa_orientacao` |
| PK, FK, NOT NULL, UNIQUE, CHECK, comentários | `01_ddl.sql` |
| 60 registros (o edital cita 50 e 60) | 133 |
| UPDATE e DELETE com WHERE | `03_dml.sql` |
| 10 consultas (filtro, ordenação, cálculo, COUNT/SUM/AVG/MAX/MIN, GROUP BY, HAVING, subconsulta, 3 JOINs) | `04_consultas.sql` |
| DER e dicionário de dados | `docs/` |
| 3 modelos no Oracle Data Modeler (conceitual, lógico, relacional) | **a gerar no Data Modeler** (ver abaixo) |

## Pendências antes da entrega
1. **Oracle Data Modeler:** *File → Import → Data Dictionary* (ou *DDL File*) com `01_ddl.sql`, gere o modelo lógico e exporte conceitual, lógico e relacional em PDF. Não dá para gerar esses arquivos fora da ferramenta.
2. Rodar `00_executar_tudo.sql` no Oracle da FIAP e conferir que as auditorias `P1..P6` voltam vazias; tirar print das 10 consultas.
3. O conteúdo jurídico do seed está **PENDENTE de revisão** pelo responsável jurídico (Jonatan). Ao revisar, passe `ds_revisao` para `REVISADO` **com data e ao menos uma fonte legal** (a auditoria P1 cobra isso).
4. As URLs do seed (leis, Caixa, defensorias) **não foram abertas**; abra uma a uma.
5. Se mudar o `01_ddl.sql`, rode `python3 docs/gerar_docs.py` (dicionário e DER) e `python3 testes/testar_banco.py`.
