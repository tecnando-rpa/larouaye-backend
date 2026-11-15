# Dicionário de dados — LarOuAyê (Oracle)

> Gerado automaticamente de `01_ddl.sql` por `docs/gerar_docs.py`. Não edite à mão: rode o script de novo.

**11 tabelas** · convenção: `tb_` tabela, `cd_` código/chave, `nm_` nome, `ds_` descrição, `dt_` data, `sg_` sigla, `nr_` número, `vl_` valor, `st_` situação.

## tb_cidadao

Cidadão que usa o LarOuAyê pelo app web ou pelo Telegram. Só dados mínimos.

| Coluna | Tipo | Obrigatório | Padrão | Chave | Descrição |
|---|---|---|---|---|---|
| `cd_cidadao` | NUMBER(10) | sim | — | PK | Identificador da pessoa |
| `nm_cidadao` | VARCHAR2(80) | sim | — | — | Nome (ou apelido) da pessoa; sem CPF |
| `ds_email` | VARCHAR2(120) | não | — | — | E-mail opcional, único sem diferenciar maiúsculas |
| `ds_canal` | VARCHAR2(10) | sim | 'WEB' | — | Canal de origem: WEB ou TELEGRAM |
| `cd_id_externo` | VARCHAR2(40) | não | — | — | Identificador no canal externo (chat_id do Telegram) |
| `dt_cadastro` | TIMESTAMP | sim | SYSTIMESTAMP | — | Quando a pessoa foi cadastrada |

**Únicos:** (ds_email); (ds_canal, cd_id_externo)  
**Regras (CHECK):** ds_canal IN ('WEB', 'TELEGRAM'); ds_canal = 'WEB' OR cd_id_externo IS NOT NULL; LENGTH(TRIM(nm_cidadao)) > 0; ds_email IS NULL OR (INSTR(ds_email, '@') > 1 AND INSTR(ds_email, ' ') = 0)  

## tb_categoria

Categorias jurídicas do banco (6). O Java traduz os 10 rótulos do classificador de ML para estas categorias.

| Coluna | Tipo | Obrigatório | Padrão | Chave | Descrição |
|---|---|---|---|---|---|
| `cd_categoria` | NUMBER(10) | sim | — | PK | Identificador da categoria |
| `cd_codigo` | VARCHAR2(30) | sim | — | — | Código estável usado pelo sistema (ex.: DOCUMENTACAO, ESCRITURA) |
| `nm_categoria` | VARCHAR2(80) | sim | — | — | Nome mostrado à pessoa |
| `ds_categoria` | VARCHAR2(300) | não | — | — | Explicação da categoria |

**Únicos:** (cd_codigo)  
**Regras (CHECK):** cd_codigo = UPPER(cd_codigo) AND LENGTH(TRIM(cd_codigo)) > 0  

## tb_orientacao

Orientação jurídica em linguagem simples. Só vira REVISADO após conferência do responsável jurídico.

| Coluna | Tipo | Obrigatório | Padrão | Chave | Descrição |
|---|---|---|---|---|---|
| `cd_orientacao` | NUMBER(10) | sim | — | PK | Identificador da orientação jurídica |
| `cd_categoria` | NUMBER(10) | sim | — | FK → tb_categoria.cd_categoria | Identificador da categoria |
| `nm_titulo` | VARCHAR2(150) | sim | — | — | Título curto da orientação |
| `ds_pergunta` | VARCHAR2(200) | sim | — | — | Pergunta que a orientação responde (em orientacao) / pergunta feita pela pessoa (em consulta) |
| `ds_conteudo` | VARCHAR2(3000) | sim | — | — | Texto jurídico em linguagem simples |
| `ds_url_video` | VARCHAR2(300) | não | — | — | Link opcional de vídeo explicativo (http/https) |
| `ds_revisao` | VARCHAR2(10) | sim | 'PENDENTE' | — | PENDENTE = ainda não revisado juridicamente; REVISADO = conferido, com data |
| `dt_revisao` | DATE | não | — | — | Data da revisão jurídica; obrigatória se REVISADO |
| `st_ativo` | NUMBER(1) | sim | 1 | — | 1 = pode ser entregue; 0 = desativada |

**Regras (CHECK):** ds_revisao IN ('PENDENTE', 'REVISADO'); st_ativo IN (0, 1); ds_revisao = 'PENDENTE' OR dt_revisao IS NOT NULL; LENGTH(TRIM(nm_titulo)) > 0; ds_url_video IS NULL OR ds_url_video LIKE 'http%'  

## tb_cuidado

Cuidados práticos de cada orientação (lista ordenada).

| Coluna | Tipo | Obrigatório | Padrão | Chave | Descrição |
|---|---|---|---|---|---|
| `cd_cuidado` | NUMBER(10) | sim | — | PK | Identificador do cuidado |
| `cd_orientacao` | NUMBER(10) | sim | — | FK → tb_orientacao.cd_orientacao | Identificador da orientação jurídica |
| `nr_ordem` | NUMBER(3) | sim | — | — | Posição na lista (cuidado) ou na jornada (etapa) |
| `ds_cuidado` | VARCHAR2(300) | sim | — | — | Cuidado prático a tomar |

**Únicos:** (cd_orientacao, nr_ordem)  
**Regras (CHECK):** nr_ordem > 0  

## tb_fonte_legal

Base legal e fonte oficial que fundamenta cada orientação.

| Coluna | Tipo | Obrigatório | Padrão | Chave | Descrição |
|---|---|---|---|---|---|
| `cd_fonte` | NUMBER(10) | sim | — | PK | Identificador da fonte legal |
| `cd_orientacao` | NUMBER(10) | sim | — | FK → tb_orientacao.cd_orientacao | Identificador da orientação jurídica |
| `nm_norma` | VARCHAR2(120) | sim | — | — | Lei, norma ou órgão (ex.: Lei 6.015/1973) |
| `ds_referencia` | VARCHAR2(200) | não | — | — | Artigo ou trecho de referência |
| `ds_url` | VARCHAR2(300) | não | — | — | Link oficial (http/https) |

**Regras (CHECK):** ds_url IS NULL OR ds_url LIKE 'http%'  

## tb_etapa

Etapas da jornada de compra do primeiro imóvel, em ordem.

| Coluna | Tipo | Obrigatório | Padrão | Chave | Descrição |
|---|---|---|---|---|---|
| `cd_etapa` | NUMBER(10) | sim | — | PK | Identificador da etapa da compra |
| `cd_codigo` | VARCHAR2(30) | sim | — | — | Código estável usado pelo sistema (ex.: DOCUMENTACAO, ESCRITURA) |
| `nr_ordem` | NUMBER(3) | sim | — | — | Posição na lista (cuidado) ou na jornada (etapa) |
| `nm_etapa` | VARCHAR2(100) | sim | — | — | Nome da etapa |
| `ds_etapa` | VARCHAR2(400) | sim | — | — | O que fazer nesta etapa |

**Únicos:** (cd_codigo); (nr_ordem)  
**Regras (CHECK):** nr_ordem > 0  

## tb_etapa_documento

Documentos necessários em cada etapa (checklist).

| Coluna | Tipo | Obrigatório | Padrão | Chave | Descrição |
|---|---|---|---|---|---|
| `cd_documento` | NUMBER(10) | sim | — | PK | Identificador do documento |
| `cd_etapa` | NUMBER(10) | sim | — | FK → tb_etapa.cd_etapa | Identificador da etapa da compra |
| `nm_documento` | VARCHAR2(120) | sim | — | — | Nome do documento do checklist |
| `ds_observacao` | VARCHAR2(300) | não | — | — | Observação (original, cópia, validade…) |


## tb_etapa_orientacao

Quais orientações ajudam em cada etapa (N:N).

| Coluna | Tipo | Obrigatório | Padrão | Chave | Descrição |
|---|---|---|---|---|---|
| `cd_etapa` | NUMBER(10) | sim | — | PK, FK → tb_etapa.cd_etapa | Identificador da etapa da compra |
| `cd_orientacao` | NUMBER(10) | sim | — | PK, FK → tb_orientacao.cd_orientacao | Identificador da orientação jurídica |


## tb_cidadao_etapa

Progresso de cada pessoa em cada etapa da compra (N:N).

| Coluna | Tipo | Obrigatório | Padrão | Chave | Descrição |
|---|---|---|---|---|---|
| `cd_cidadao` | NUMBER(10) | sim | — | PK, FK → tb_cidadao.cd_cidadao | Identificador da pessoa |
| `cd_etapa` | NUMBER(10) | sim | — | PK, FK → tb_etapa.cd_etapa | Identificador da etapa da compra |
| `ds_status` | VARCHAR2(15) | sim | 'PENDENTE' | — | Situação: progresso (PENDENTE, EM_ANDAMENTO, CONCLUIDA) ou consulta (RESPONDIDA, ESCLARECIMENTO, NAO_RECONHECIDA, ERRO) |
| `dt_atualizacao` | TIMESTAMP | sim | SYSTIMESTAMP | — | Última mudança de status |

**Regras (CHECK):** ds_status IN ('PENDENTE', 'EM_ANDAMENTO', 'CONCLUIDA')  

## tb_consulta

Histórico das perguntas, com a categoria prevista pelo ML, a confiança e a orientação entregue.

| Coluna | Tipo | Obrigatório | Padrão | Chave | Descrição |
|---|---|---|---|---|---|
| `cd_consulta` | NUMBER(10) | sim | — | PK | Identificador da consulta |
| `cd_cidadao` | NUMBER(10) | sim | — | FK → tb_cidadao.cd_cidadao | Identificador da pessoa |
| `cd_categoria` | NUMBER(10) | não | — | FK → tb_categoria.cd_categoria | Identificador da categoria |
| `cd_orientacao` | NUMBER(10) | não | — | FK → tb_orientacao.cd_orientacao | Identificador da orientação jurídica |
| `ds_pergunta` | VARCHAR2(1000) | sim | — | — | Pergunta que a orientação responde (em orientacao) / pergunta feita pela pessoa (em consulta) |
| `sg_uf` | CHAR(2) | sim | — | — | Sigla do estado (uma das 27 UFs) |
| `ds_etapa_atual` | VARCHAR2(30) | não | — | — | Código da etapa informada pela pessoa |
| `vl_confianca` | NUMBER(3,2) | não | — | — | Confiança do classificador (0 a 1). Informativa: quem decide é o Java. |
| `ds_status` | VARCHAR2(20) | sim | — | — | Situação: progresso (PENDENTE, EM_ANDAMENTO, CONCLUIDA) ou consulta (RESPONDIDA, ESCLARECIMENTO, NAO_RECONHECIDA, ERRO) |
| `ds_canal` | VARCHAR2(10) | sim | 'WEB' | — | Por onde a pessoa chegou: WEB ou TELEGRAM |
| `dt_consulta` | TIMESTAMP | sim | SYSTIMESTAMP | — | Quando a pergunta foi feita |

**Regras (CHECK):** vl_confianca BETWEEN 0 AND 1; ds_status IN ('RESPONDIDA', 'ESCLARECIMENTO', 'NAO_RECONHECIDA', 'ERRO'); ds_canal IN ('WEB', 'TELEGRAM'); sg_uf IN ('AC','AL','AP','AM','BA','CE','DF','ES','GO','MA','MT','MS','MG','PA','PB','PR','PE','PI','RJ','RN','RS','RO','RR','SC','SP','SE','TO'); (ds_status = 'RESPONDIDA' AND cd_orientacao IS NOT NULL) OR (ds_status <> 'RESPONDIDA' AND cd_orientacao IS NULL); LENGTH(TRIM(ds_pergunta)) > 0  

## tb_servico

Canais oficiais por estado (links, sem prometer listagem completa).

| Coluna | Tipo | Obrigatório | Padrão | Chave | Descrição |
|---|---|---|---|---|---|
| `cd_servico` | NUMBER(10) | sim | — | PK | Identificador do serviço |
| `nm_servico` | VARCHAR2(120) | sim | — | — | Nome do canal oficial |
| `ds_tipo` | VARCHAR2(15) | sim | — | — | CARTORIO, PREFEITURA, BANCO, DEFENSORIA ou ORGAO |
| `sg_uf` | CHAR(2) | sim | — | — | Sigla do estado (uma das 27 UFs) |
| `ds_url` | VARCHAR2(300) | não | — | — | Link oficial (http/https) |
| `ds_descricao` | VARCHAR2(300) | não | — | — | Para que serve o canal |

**Regras (CHECK):** ds_tipo IN ('CARTORIO', 'PREFEITURA', 'BANCO', 'DEFENSORIA', 'ORGAO'); sg_uf IN ('AC','AL','AP','AM','BA','CE','DF','ES','GO','MA','MT','MS','MG','PA','PB','PR','PE','PI','RJ','RN','RS','RO','RR','SC','SP','SE','TO'); ds_url IS NULL OR ds_url LIKE 'http%'  

## Relacionamentos

| Filha (N) | Chave | Pai (1) | Ao apagar o pai |
|---|---|---|---|
| tb_orientacao | cd_categoria | tb_categoria | BLOQUEIA (restrição) |
| tb_cuidado | cd_orientacao | tb_orientacao | apaga os filhos (CASCADE) |
| tb_fonte_legal | cd_orientacao | tb_orientacao | apaga os filhos (CASCADE) |
| tb_etapa_documento | cd_etapa | tb_etapa | apaga os filhos (CASCADE) |
| tb_etapa_orientacao | cd_etapa | tb_etapa | apaga os filhos (CASCADE) |
| tb_etapa_orientacao | cd_orientacao | tb_orientacao | apaga os filhos (CASCADE) |
| tb_cidadao_etapa | cd_cidadao | tb_cidadao | BLOQUEIA (restrição) |
| tb_cidadao_etapa | cd_etapa | tb_etapa | BLOQUEIA (restrição) |
| tb_consulta | cd_cidadao | tb_cidadao | BLOQUEIA (restrição) |
| tb_consulta | cd_categoria | tb_categoria | BLOQUEIA (restrição) |
| tb_consulta | cd_orientacao | tb_orientacao | BLOQUEIA (restrição) |

N:N por tabela associativa: `tb_cidadao_etapa` (com status) e `tb_etapa_orientacao`.
