-- =====================================================================
-- LarOuAyê — Banco Oracle (Building Relational Database)
-- Convenção: tb_ tabela | cd_ código | nm_ nome | ds_ descrição | dt_ data
--            sg_ sigla | nr_ número | vl_ valor | st_ situação (0/1)
-- Executar como o usuário dono do esquema. Reexecutável: 00_reset.sql apaga o que existir (sem erro se não existir).
-- Regras de integridade ficam NO BANCO (CHECK/UNIQUE/FK), não só no Java: o dado ruim é barrado mesmo se alguém
-- gravar direto pelo SQL Developer ou por outro sistema.
-- =====================================================================

-- ---------- SEQUENCES (começam em 1000: os dados de exemplo usam ids menores) ----------
CREATE SEQUENCE sq_tb_cidadao    START WITH 1000 INCREMENT BY 1 NOCACHE;
CREATE SEQUENCE sq_tb_categoria  START WITH 1000 INCREMENT BY 1 NOCACHE;
CREATE SEQUENCE sq_tb_orientacao START WITH 1000 INCREMENT BY 1 NOCACHE;
CREATE SEQUENCE sq_tb_cuidado    START WITH 1000 INCREMENT BY 1 NOCACHE;
CREATE SEQUENCE sq_tb_fonte_legal      START WITH 1000 INCREMENT BY 1 NOCACHE;
CREATE SEQUENCE sq_tb_etapa      START WITH 1000 INCREMENT BY 1 NOCACHE;
CREATE SEQUENCE sq_tb_etapa_documento  START WITH 1000 INCREMENT BY 1 NOCACHE;
CREATE SEQUENCE sq_tb_consulta   START WITH 1000 INCREMENT BY 1 NOCACHE;
CREATE SEQUENCE sq_tb_servico    START WITH 1000 INCREMENT BY 1 NOCACHE;

-- ---------- 1. USUÁRIO (web ou Telegram; sem CPF nem dado sensível) ----------
CREATE TABLE tb_cidadao (
    cd_cidadao     NUMBER(10)    NOT NULL,
    nm_cidadao     VARCHAR2(80)  NOT NULL,
    ds_email       VARCHAR2(120),
    ds_canal       VARCHAR2(10)  DEFAULT 'WEB' NOT NULL,
    cd_id_externo  VARCHAR2(40),
    dt_cadastro    TIMESTAMP     DEFAULT SYSTIMESTAMP NOT NULL,
    CONSTRAINT pk_cidadao PRIMARY KEY (cd_cidadao),
    CONSTRAINT uk_cidadao_email UNIQUE (ds_email),
    CONSTRAINT ck_cidadao_canal CHECK (ds_canal IN ('WEB', 'TELEGRAM')),
    CONSTRAINT ck_cidadao_externo CHECK (ds_canal = 'WEB' OR cd_id_externo IS NOT NULL),
    CONSTRAINT ck_cidadao_nome CHECK (LENGTH(TRIM(nm_cidadao)) > 0),
    CONSTRAINT ck_cidadao_email CHECK (ds_email IS NULL OR (INSTR(ds_email, '@') > 1 AND INSTR(ds_email, ' ') = 0))
);
-- E-mail único sem diferenciar maiúsculas de minúsculas (o Java também compara com LOWER).
CREATE UNIQUE INDEX ux_cidadao_email_lower ON tb_cidadao (LOWER(ds_email));
-- Um chat externo (ex.: Telegram) só pode virar UM cidadão. Cidadãos WEB sem id externo podem ser vários.
-- Por que não UNIQUE (ds_canal, cd_id_externo)? No Oracle, chave composta com UM valor preenchido ('WEB') e outro nulo
-- conta como valor e colidiria. O CASE zera as duas colunas quando não há id externo, e o Oracle ignora chave toda nula.
CREATE UNIQUE INDEX ux_cidadao_canal_externo ON tb_cidadao (CASE WHEN cd_id_externo IS NOT NULL THEN ds_canal END, cd_id_externo);
COMMENT ON TABLE  tb_cidadao IS 'Cidadão que usa o LarOuAyê pelo app web ou pelo Telegram. Só dados mínimos.';
COMMENT ON COLUMN tb_cidadao.ds_canal IS 'Canal de origem: WEB ou TELEGRAM';
COMMENT ON COLUMN tb_cidadao.cd_id_externo IS 'Identificador no canal externo (chat_id do Telegram)';

-- ---------- 2. CATEGORIA jurídica das dúvidas ----------
CREATE TABLE tb_categoria (
    cd_categoria  NUMBER(10)    NOT NULL,
    cd_codigo     VARCHAR2(30)  NOT NULL,
    nm_categoria  VARCHAR2(80)  NOT NULL,
    ds_categoria  VARCHAR2(300),
    CONSTRAINT pk_categoria PRIMARY KEY (cd_categoria),
    CONSTRAINT uk_categoria_codigo UNIQUE (cd_codigo),
    CONSTRAINT ck_categoria_codigo CHECK (cd_codigo = UPPER(cd_codigo) AND LENGTH(TRIM(cd_codigo)) > 0)
);
COMMENT ON TABLE tb_categoria IS 'Categorias jurídicas do banco (6). O Java traduz os 10 rótulos do classificador de ML para estas categorias.';

-- ---------- 3. ORIENTAÇÃO jurídica (conteúdo aprovado; o React nunca escreve esse texto) ----------
CREATE TABLE tb_orientacao (
    cd_orientacao  NUMBER(10)     NOT NULL,
    cd_categoria   NUMBER(10)     NOT NULL,
    nm_titulo      VARCHAR2(150)  NOT NULL,
    ds_pergunta    VARCHAR2(200)  NOT NULL,
    ds_conteudo    VARCHAR2(3000) NOT NULL,
    ds_url_video   VARCHAR2(300),
    ds_revisao     VARCHAR2(10)   DEFAULT 'PENDENTE' NOT NULL,
    dt_revisao     DATE,
    st_ativo       NUMBER(1)      DEFAULT 1 NOT NULL,
    CONSTRAINT pk_orientacao PRIMARY KEY (cd_orientacao),
    CONSTRAINT fk_orientacao_categoria FOREIGN KEY (cd_categoria) REFERENCES tb_categoria (cd_categoria),
    CONSTRAINT ck_orientacao_revisao CHECK (ds_revisao IN ('PENDENTE', 'REVISADO')),
    CONSTRAINT ck_orientacao_ativo CHECK (st_ativo IN (0, 1)),
    CONSTRAINT ck_orientacao_data_revisao CHECK (ds_revisao = 'PENDENTE' OR dt_revisao IS NOT NULL),
    CONSTRAINT ck_orientacao_titulo CHECK (LENGTH(TRIM(nm_titulo)) > 0),
    CONSTRAINT ck_orientacao_video CHECK (ds_url_video IS NULL OR ds_url_video LIKE 'http%')
);
COMMENT ON TABLE  tb_orientacao IS 'Orientação jurídica em linguagem simples. Só vira REVISADO após conferência do responsável jurídico.';
COMMENT ON COLUMN tb_orientacao.ds_revisao IS 'PENDENTE = ainda não revisado juridicamente; REVISADO = conferido, com data';

-- ---------- 4. CUIDADO (1:N com orientação) ----------
CREATE TABLE tb_cuidado (
    cd_cuidado     NUMBER(10)     NOT NULL,
    cd_orientacao  NUMBER(10)     NOT NULL,
    nr_ordem       NUMBER(3)      NOT NULL,
    ds_cuidado     VARCHAR2(300)  NOT NULL,
    CONSTRAINT pk_cuidado PRIMARY KEY (cd_cuidado),
    CONSTRAINT fk_cuidado_orientacao FOREIGN KEY (cd_orientacao) REFERENCES tb_orientacao (cd_orientacao) ON DELETE CASCADE,
    CONSTRAINT uk_cuidado_ordem UNIQUE (cd_orientacao, nr_ordem),
    CONSTRAINT ck_cuidado_ordem CHECK (nr_ordem > 0)
);
COMMENT ON TABLE tb_cuidado IS 'Cuidados práticos de cada orientação (lista ordenada).';

-- ---------- 5. FONTE LEGAL (1:N com orientação) ----------
CREATE TABLE tb_fonte_legal (
    cd_fonte       NUMBER(10)     NOT NULL,
    cd_orientacao  NUMBER(10)     NOT NULL,
    nm_norma       VARCHAR2(120)  NOT NULL,
    ds_referencia  VARCHAR2(200),
    ds_url         VARCHAR2(300),
    CONSTRAINT pk_fonte_legal PRIMARY KEY (cd_fonte),
    CONSTRAINT fk_fonte_orientacao FOREIGN KEY (cd_orientacao) REFERENCES tb_orientacao (cd_orientacao) ON DELETE CASCADE,
    CONSTRAINT ck_fonte_url CHECK (ds_url IS NULL OR ds_url LIKE 'http%')
);
COMMENT ON TABLE tb_fonte_legal IS 'Base legal e fonte oficial que fundamenta cada orientação.';

-- ---------- 6. ETAPA da compra ----------
CREATE TABLE tb_etapa (
    cd_etapa    NUMBER(10)     NOT NULL,
    cd_codigo   VARCHAR2(30)   NOT NULL,
    nr_ordem    NUMBER(3)      NOT NULL,
    nm_etapa    VARCHAR2(100)  NOT NULL,
    ds_etapa    VARCHAR2(400)  NOT NULL,
    CONSTRAINT pk_etapa PRIMARY KEY (cd_etapa),
    CONSTRAINT uk_etapa_codigo UNIQUE (cd_codigo),
    CONSTRAINT uk_etapa_ordem UNIQUE (nr_ordem),
    CONSTRAINT ck_etapa_ordem CHECK (nr_ordem > 0)
);
COMMENT ON TABLE tb_etapa IS 'Etapas da jornada de compra do primeiro imóvel, em ordem.';

-- ---------- 7. DOCUMENTO por etapa (1:N) ----------
CREATE TABLE tb_etapa_documento (
    cd_documento   NUMBER(10)     NOT NULL,
    cd_etapa       NUMBER(10)     NOT NULL,
    nm_documento   VARCHAR2(120)  NOT NULL,
    ds_observacao  VARCHAR2(300),
    CONSTRAINT pk_etapa_documento PRIMARY KEY (cd_documento),
    CONSTRAINT fk_documento_etapa FOREIGN KEY (cd_etapa) REFERENCES tb_etapa (cd_etapa) ON DELETE CASCADE
);
COMMENT ON TABLE tb_etapa_documento IS 'Documentos necessários em cada etapa (checklist).';

-- ---------- 8. ETAPA x ORIENTAÇÃO (N:N, tabela associativa) ----------
CREATE TABLE tb_etapa_orientacao (
    cd_etapa       NUMBER(10) NOT NULL,
    cd_orientacao  NUMBER(10) NOT NULL,
    CONSTRAINT pk_etapa_orientacao PRIMARY KEY (cd_etapa, cd_orientacao),
    CONSTRAINT fk_eo_etapa FOREIGN KEY (cd_etapa) REFERENCES tb_etapa (cd_etapa) ON DELETE CASCADE,
    CONSTRAINT fk_eo_orientacao FOREIGN KEY (cd_orientacao) REFERENCES tb_orientacao (cd_orientacao) ON DELETE CASCADE
);
COMMENT ON TABLE tb_etapa_orientacao IS 'Quais orientações ajudam em cada etapa (N:N).';

-- ---------- 9. USUÁRIO x ETAPA (N:N com progresso) ----------
CREATE TABLE tb_cidadao_etapa (
    cd_cidadao       NUMBER(10)    NOT NULL,
    cd_etapa         NUMBER(10)    NOT NULL,
    ds_status        VARCHAR2(15)  DEFAULT 'PENDENTE' NOT NULL,
    dt_atualizacao   TIMESTAMP     DEFAULT SYSTIMESTAMP NOT NULL,
    CONSTRAINT pk_cidadao_etapa PRIMARY KEY (cd_cidadao, cd_etapa),
    CONSTRAINT fk_ue_cidadao FOREIGN KEY (cd_cidadao) REFERENCES tb_cidadao (cd_cidadao),
    CONSTRAINT fk_ue_etapa FOREIGN KEY (cd_etapa) REFERENCES tb_etapa (cd_etapa),
    CONSTRAINT ck_ue_status CHECK (ds_status IN ('PENDENTE', 'EM_ANDAMENTO', 'CONCLUIDA'))
);
COMMENT ON TABLE tb_cidadao_etapa IS 'Progresso de cada pessoa em cada etapa da compra (N:N).';

-- ---------- 10. CONSULTA (a pergunta, a classificação e a resposta dada) ----------
CREATE TABLE tb_consulta (
    cd_consulta     NUMBER(10)      NOT NULL,
    cd_cidadao      NUMBER(10)      NOT NULL,
    cd_categoria    NUMBER(10),
    cd_orientacao   NUMBER(10),
    ds_pergunta     VARCHAR2(1000)  NOT NULL,
    sg_uf           CHAR(2)         NOT NULL,
    ds_etapa_atual  VARCHAR2(30),
    vl_confianca    NUMBER(3,2),
    ds_status       VARCHAR2(20)    NOT NULL,
    ds_canal        VARCHAR2(10)    DEFAULT 'WEB' NOT NULL,
    dt_consulta     TIMESTAMP       DEFAULT SYSTIMESTAMP NOT NULL,
    CONSTRAINT pk_consulta PRIMARY KEY (cd_consulta),
    CONSTRAINT fk_consulta_cidadao FOREIGN KEY (cd_cidadao) REFERENCES tb_cidadao (cd_cidadao),
    CONSTRAINT fk_consulta_categoria FOREIGN KEY (cd_categoria) REFERENCES tb_categoria (cd_categoria),
    CONSTRAINT fk_consulta_orientacao FOREIGN KEY (cd_orientacao) REFERENCES tb_orientacao (cd_orientacao),
    CONSTRAINT ck_consulta_confianca CHECK (vl_confianca BETWEEN 0 AND 1),
    CONSTRAINT ck_consulta_status CHECK (ds_status IN ('RESPONDIDA', 'ESCLARECIMENTO', 'NAO_RECONHECIDA', 'ERRO')),
    CONSTRAINT ck_consulta_canal CHECK (ds_canal IN ('WEB', 'TELEGRAM')),
    CONSTRAINT ck_consulta_uf CHECK (sg_uf IN ('AC','AL','AP','AM','BA','CE','DF','ES','GO','MA','MT','MS','MG','PA','PB','PR','PE','PI','RJ','RN','RS','RO','RR','SC','SP','SE','TO')),
    -- RESPONDIDA sempre aponta a orientação entregue; as demais nunca apontam.
    CONSTRAINT ck_consulta_orientacao CHECK ((ds_status = 'RESPONDIDA' AND cd_orientacao IS NOT NULL) OR (ds_status <> 'RESPONDIDA' AND cd_orientacao IS NULL)),
    CONSTRAINT ck_consulta_pergunta CHECK (LENGTH(TRIM(ds_pergunta)) > 0)
);
COMMENT ON TABLE tb_consulta IS 'Histórico das perguntas, com a categoria prevista pelo ML, a confiança e a orientação entregue.';
COMMENT ON COLUMN tb_consulta.vl_confianca IS 'Confiança do classificador (0 a 1). Informativa: quem decide é o Java.';

-- ---------- 11. SERVIÇO (cartório, prefeitura, banco, defensoria) ----------
CREATE TABLE tb_servico (
    cd_servico     NUMBER(10)     NOT NULL,
    nm_servico     VARCHAR2(120)  NOT NULL,
    ds_tipo        VARCHAR2(15)   NOT NULL,
    sg_uf          CHAR(2)        NOT NULL,
    ds_url         VARCHAR2(300),
    ds_descricao   VARCHAR2(300),
    CONSTRAINT pk_servico PRIMARY KEY (cd_servico),
    CONSTRAINT ck_servico_tipo CHECK (ds_tipo IN ('CARTORIO', 'PREFEITURA', 'BANCO', 'DEFENSORIA', 'ORGAO')),
    CONSTRAINT ck_servico_uf CHECK (sg_uf IN ('AC','AL','AP','AM','BA','CE','DF','ES','GO','MA','MT','MS','MG','PA','PB','PR','PE','PI','RJ','RN','RS','RO','RR','SC','SP','SE','TO')),
    CONSTRAINT ck_servico_url CHECK (ds_url IS NULL OR ds_url LIKE 'http%')
);
COMMENT ON TABLE tb_servico IS 'Canais oficiais por estado (links, sem prometer listagem completa).';

-- ---------- ÍNDICES nas chaves estrangeiras (desempenho das consultas e joins) ----------
CREATE INDEX ix_orientacao_categoria ON tb_orientacao (cd_categoria);
CREATE INDEX ix_cuidado_orientacao   ON tb_cuidado (cd_orientacao);
CREATE INDEX ix_fonte_orientacao     ON tb_fonte_legal (cd_orientacao);
CREATE INDEX ix_documento_etapa      ON tb_etapa_documento (cd_etapa);
CREATE INDEX ix_eo_orientacao        ON tb_etapa_orientacao (cd_orientacao);
CREATE INDEX ix_ue_etapa             ON tb_cidadao_etapa (cd_etapa);
CREATE INDEX ix_consulta_cidadao     ON tb_consulta (cd_cidadao);
CREATE INDEX ix_consulta_categoria   ON tb_consulta (cd_categoria);
CREATE INDEX ix_consulta_orientacao  ON tb_consulta (cd_orientacao);
CREATE INDEX ix_servico_uf_tipo      ON tb_servico (sg_uf, ds_tipo);
