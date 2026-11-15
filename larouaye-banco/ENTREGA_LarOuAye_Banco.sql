-- LarOuAye - Building Relational Database (FIAP Global Solution 2026/2)
-- Ordem: tabelas -> INSERTs -> consultas -> UPDATE -> DELETE. Rode em conexao limpa (ou 00_reset.sql antes).

-- ======================================================================
-- 1) CRIACAO DAS TABELAS (DDL)
-- ======================================================================
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

-- ======================================================================
-- 2) INSERCAO DOS DADOS (massa de dados)
-- ======================================================================
-- Massa de dados do LarOuAyê. ATENÇÃO: o conteúdo jurídico está PENDENTE de revisão pelo responsável jurídico (ds_revisao).
-- ATENÇÃO 2: as URLs (leis, bancos, defensorias) NÃO foram abertas e conferidas ainda. Abra uma a uma antes da entrega.
-- Os ids de exemplo são menores que 1000; as sequences começam em 1000.

-- tb_cidadao
INSERT INTO tb_cidadao (cd_cidadao, nm_cidadao, ds_email, ds_canal, cd_id_externo, dt_cadastro) VALUES (1, 'Maria Souza', 'maria@exemplo.com', 'WEB', NULL, TIMESTAMP '2026-11-01 09:10:00');
INSERT INTO tb_cidadao (cd_cidadao, nm_cidadao, ds_email, ds_canal, cd_id_externo, dt_cadastro) VALUES (2, 'João Lima', NULL, 'WEB', NULL, TIMESTAMP '2026-11-01 10:20:00');
INSERT INTO tb_cidadao (cd_cidadao, nm_cidadao, ds_email, ds_canal, cd_id_externo, dt_cadastro) VALUES (3, 'Ana Pereira', 'ana@exemplo.com', 'WEB', NULL, TIMESTAMP '2026-11-02 14:05:00');
INSERT INTO tb_cidadao (cd_cidadao, nm_cidadao, ds_email, ds_canal, cd_id_externo, dt_cadastro) VALUES (4, 'Carlos Mendes', NULL, 'TELEGRAM', '100200301', TIMESTAMP '2026-11-03 08:40:00');
INSERT INTO tb_cidadao (cd_cidadao, nm_cidadao, ds_email, ds_canal, cd_id_externo, dt_cadastro) VALUES (5, 'Dona Lúcia', NULL, 'TELEGRAM', '100200302', TIMESTAMP '2026-11-03 19:15:00');
INSERT INTO tb_cidadao (cd_cidadao, nm_cidadao, ds_email, ds_canal, cd_id_externo, dt_cadastro) VALUES (6, 'Pedro Alves', 'pedro@exemplo.com', 'WEB', NULL, TIMESTAMP '2026-11-04 11:00:00');
INSERT INTO tb_cidadao (cd_cidadao, nm_cidadao, ds_email, ds_canal, cd_id_externo, dt_cadastro) VALUES (7, 'Rita Gomes', NULL, 'TELEGRAM', '100200303', TIMESTAMP '2026-11-05 16:30:00');
INSERT INTO tb_cidadao (cd_cidadao, nm_cidadao, ds_email, ds_canal, cd_id_externo, dt_cadastro) VALUES (8, 'Teste Automático', NULL, 'WEB', NULL, TIMESTAMP '2026-11-06 12:00:00');

-- tb_categoria
INSERT INTO tb_categoria (cd_categoria, cd_codigo, nm_categoria, ds_categoria) VALUES (1, 'DOCUMENTACAO', 'Documentação', 'Matrícula, certidões e documentos do vendedor e do imóvel');
INSERT INTO tb_categoria (cd_categoria, cd_codigo, nm_categoria, ds_categoria) VALUES (2, 'CONTRATO', 'Contrato', 'Promessa, sinal e contrato de compra e venda');
INSERT INTO tb_categoria (cd_categoria, cd_codigo, nm_categoria, ds_categoria) VALUES (3, 'FINANCIAMENTO', 'Financiamento e FGTS', 'Crédito imobiliário, FGTS e programas habitacionais');
INSERT INTO tb_categoria (cd_categoria, cd_codigo, nm_categoria, ds_categoria) VALUES (4, 'ESCRITURA', 'Escritura', 'Escritura pública no tabelionato de notas');
INSERT INTO tb_categoria (cd_categoria, cd_codigo, nm_categoria, ds_categoria) VALUES (5, 'REGISTRO', 'Registro', 'Registro da compra no cartório de imóveis');
INSERT INTO tb_categoria (cd_categoria, cd_codigo, nm_categoria, ds_categoria) VALUES (6, 'TRIBUTOS', 'Impostos e taxas', 'ITBI, IPTU e custos de cartório');

-- tb_orientacao
INSERT INTO tb_orientacao (cd_orientacao, cd_categoria, nm_titulo, ds_pergunta, ds_conteudo, ds_url_video, ds_revisao, dt_revisao, st_ativo) VALUES (1, 1, 'O que é a matrícula do imóvel', 'O que é a matrícula do imóvel?', 'A matrícula é o documento do cartório de registro de imóveis que conta a história do imóvel: quem é o dono, se há dívida, penhora ou outro ônus. Peça uma certidão de matrícula atualizada, emitida há poucos dias, antes de pagar qualquer valor. Ela é a base para saber se o imóvel é do vendedor e se está livre.', NULL, 'PENDENTE', NULL, 1);
INSERT INTO tb_orientacao (cd_orientacao, cd_categoria, nm_titulo, ds_pergunta, ds_conteudo, ds_url_video, ds_revisao, dt_revisao, st_ativo) VALUES (2, 1, 'Documentos que o vendedor deve mostrar', 'Quais documentos o vendedor precisa me mostrar?', 'Peça os documentos pessoais do vendedor e do cônjuge, quando houver, a certidão de matrícula atualizada e o comprovante de que o IPTU e o condomínio estão em dia. Também é comum pedir certidões negativas do vendedor, para saber se existem ações ou dívidas que possam atingir o imóvel. Guarde cópia de tudo.', NULL, 'PENDENTE', NULL, 1);
INSERT INTO tb_orientacao (cd_orientacao, cd_categoria, nm_titulo, ds_pergunta, ds_conteudo, ds_url_video, ds_revisao, dt_revisao, st_ativo) VALUES (3, 1, 'Como saber se o imóvel tem dívidas', 'Como descubro se um imóvel tem dívidas?', 'Comece pela certidão de matrícula, que mostra ônus como hipoteca e penhora. Depois consulte na prefeitura se há dívida de IPTU e peça ao condomínio uma declaração de que não há débitos. Pesquise também as certidões do vendedor. Dívida de IPTU e de condomínio pode acompanhar o imóvel, por isso confira antes de fechar.', NULL, 'PENDENTE', NULL, 1);
INSERT INTO tb_orientacao (cd_orientacao, cd_categoria, nm_titulo, ds_pergunta, ds_conteudo, ds_url_video, ds_revisao, dt_revisao, st_ativo) VALUES (4, 2, 'O que conferir no contrato de compra e venda', 'O que preciso conferir no contrato de compra e venda?', 'Confira o nome e os dados de quem compra e de quem vende, a descrição do imóvel igual à da matrícula, o preço, a forma e as datas de pagamento, quem paga cada imposto e custo, o prazo para entregar o imóvel e as multas. Não assine sem entender cada cláusula. Em caso de dúvida, procure um advogado ou a Defensoria Pública.', NULL, 'PENDENTE', NULL, 1);
INSERT INTO tb_orientacao (cd_orientacao, cd_categoria, nm_titulo, ds_pergunta, ds_conteudo, ds_url_video, ds_revisao, dt_revisao, st_ativo) VALUES (5, 2, 'Sinal e promessa de compra e venda', 'O que acontece se eu der um sinal?', 'O sinal, também chamado de arras, é um valor que se paga para confirmar o negócio. Se quem pagou desistir, pode perder o sinal. Se quem recebeu desistir, pode ter de devolver o sinal em dobro. Peça sempre um recibo e escreva por escrito as condições.', NULL, 'PENDENTE', NULL, 1);
INSERT INTO tb_orientacao (cd_orientacao, cd_categoria, nm_titulo, ds_pergunta, ds_conteudo, ds_url_video, ds_revisao, dt_revisao, st_ativo) VALUES (6, 4, 'Quando a escritura pública é necessária', 'Preciso fazer escritura pública?', 'Em regra, a compra de imóvel de valor acima de 30 salários mínimos exige escritura pública, feita no tabelionato de notas. Em financiamento bancário, o contrato do banco pode servir como instrumento da compra. Pergunte ao banco ou ao tabelionato qual é o seu caso.', NULL, 'PENDENTE', NULL, 1);
INSERT INTO tb_orientacao (cd_orientacao, cd_categoria, nm_titulo, ds_pergunta, ds_conteudo, ds_url_video, ds_revisao, dt_revisao, st_ativo) VALUES (7, 4, 'Quanto custa e onde fazer a escritura', 'Quanto custa fazer a escritura?', 'A escritura é feita em um tabelionato de notas de sua escolha. Os valores seguem tabelas de cada estado e dependem do preço do imóvel. Peça um orçamento por escrito e confira a tabela oficial do seu estado. Leve os documentos do vendedor, os seus e o comprovante do ITBI quando exigido.', NULL, 'PENDENTE', NULL, 1);
INSERT INTO tb_orientacao (cd_orientacao, cd_categoria, nm_titulo, ds_pergunta, ds_conteudo, ds_url_video, ds_revisao, dt_revisao, st_ativo) VALUES (8, 5, 'Por que o registro é indispensável', 'Qual a diferença entre escritura e registro?', 'A escritura documenta o negócio, mas é o registro no cartório de registro de imóveis que passa a propriedade para o seu nome. Enquanto não registrar, o imóvel continua no nome do vendedor. Por isso registre logo depois de pagar o ITBI.', NULL, 'PENDENTE', NULL, 1);
INSERT INTO tb_orientacao (cd_orientacao, cd_categoria, nm_titulo, ds_pergunta, ds_conteudo, ds_url_video, ds_revisao, dt_revisao, st_ativo) VALUES (9, 5, 'Como e quando registrar a compra', 'Como registro o imóvel no meu nome?', 'Leve ao cartório de registro de imóveis da região do imóvel a escritura ou o contrato, o comprovante de pagamento do ITBI e seus documentos. O cartório confere tudo e cobra emolumentos conforme a tabela do estado. Guarde a matrícula nova, com o seu nome.', NULL, 'PENDENTE', NULL, 1);
INSERT INTO tb_orientacao (cd_orientacao, cd_categoria, nm_titulo, ds_pergunta, ds_conteudo, ds_url_video, ds_revisao, dt_revisao, st_ativo) VALUES (10, 6, 'O que é o ITBI', 'O que é o ITBI e quem paga?', 'O ITBI é um imposto cobrado pela prefeitura quando um imóvel muda de dono. Normalmente quem compra paga. A alíquota e as isenções variam de cidade para cidade, e algumas prefeituras isentam ou reduzem para programas habitacionais. Consulte o site da prefeitura do imóvel e pague só pela guia oficial.', NULL, 'PENDENTE', NULL, 1);
INSERT INTO tb_orientacao (cd_orientacao, cd_categoria, nm_titulo, ds_pergunta, ds_conteudo, ds_url_video, ds_revisao, dt_revisao, st_ativo) VALUES (11, 6, 'IPTU e a compra do imóvel', 'O IPTU atrasado passa para mim?', 'O IPTU é um imposto municipal anual sobre o imóvel. Dívidas de IPTU podem ser cobradas de quem compra o imóvel, por isso peça a certidão de débitos da prefeitura antes de comprar. Depois da compra, atualize o cadastro na prefeitura.', NULL, 'PENDENTE', NULL, 1);
INSERT INTO tb_orientacao (cd_orientacao, cd_categoria, nm_titulo, ds_pergunta, ds_conteudo, ds_url_video, ds_revisao, dt_revisao, st_ativo) VALUES (12, 3, 'Financiamento e uso do FGTS', 'Posso usar o FGTS na compra do imóvel?', 'O trabalhador pode usar o FGTS na compra da casa própria, desde que cumpra as regras do fundo, como não ter outro imóvel residencial no mesmo município. No financiamento, o imóvel fica como garantia do banco até a quitação. Os bancos costumam limitar a parcela a uma parte da renda. Simule e confirme as regras com o banco, e saiba que não há garantia de aprovação do crédito.', NULL, 'PENDENTE', NULL, 1);

-- tb_cuidado
INSERT INTO tb_cuidado (cd_cuidado, cd_orientacao, nr_ordem, ds_cuidado) VALUES (1, 1, 1, 'Peça certidão de matrícula emitida há poucos dias.');
INSERT INTO tb_cuidado (cd_cuidado, cd_orientacao, nr_ordem, ds_cuidado) VALUES (2, 1, 2, 'Confira se o nome do dono é o mesmo do vendedor.');
INSERT INTO tb_cuidado (cd_cuidado, cd_orientacao, nr_ordem, ds_cuidado) VALUES (3, 2, 1, 'Peça documentos do vendedor e do cônjuge.');
INSERT INTO tb_cuidado (cd_cuidado, cd_orientacao, nr_ordem, ds_cuidado) VALUES (4, 2, 2, 'Peça certidões negativas do vendedor.');
INSERT INTO tb_cuidado (cd_cuidado, cd_orientacao, nr_ordem, ds_cuidado) VALUES (5, 3, 1, 'Veja se a matrícula tem hipoteca ou penhora.');
INSERT INTO tb_cuidado (cd_cuidado, cd_orientacao, nr_ordem, ds_cuidado) VALUES (6, 3, 2, 'Peça certidão de débitos de IPTU na prefeitura.');
INSERT INTO tb_cuidado (cd_cuidado, cd_orientacao, nr_ordem, ds_cuidado) VALUES (7, 3, 3, 'Peça ao condomínio declaração de que não há débito.');
INSERT INTO tb_cuidado (cd_cuidado, cd_orientacao, nr_ordem, ds_cuidado) VALUES (8, 4, 1, 'Compare a descrição do imóvel com a matrícula.');
INSERT INTO tb_cuidado (cd_cuidado, cd_orientacao, nr_ordem, ds_cuidado) VALUES (9, 4, 2, 'Veja quem paga cada imposto e custo.');
INSERT INTO tb_cuidado (cd_cuidado, cd_orientacao, nr_ordem, ds_cuidado) VALUES (10, 4, 3, 'Não assine sem entender todas as cláusulas.');
INSERT INTO tb_cuidado (cd_cuidado, cd_orientacao, nr_ordem, ds_cuidado) VALUES (11, 5, 1, 'Peça recibo do sinal.');
INSERT INTO tb_cuidado (cd_cuidado, cd_orientacao, nr_ordem, ds_cuidado) VALUES (12, 5, 2, 'Escreva as condições por escrito.');
INSERT INTO tb_cuidado (cd_cuidado, cd_orientacao, nr_ordem, ds_cuidado) VALUES (13, 6, 1, 'Pergunte ao banco ou ao tabelionato qual é o seu caso.');
INSERT INTO tb_cuidado (cd_cuidado, cd_orientacao, nr_ordem, ds_cuidado) VALUES (14, 7, 1, 'Peça orçamento por escrito.');
INSERT INTO tb_cuidado (cd_cuidado, cd_orientacao, nr_ordem, ds_cuidado) VALUES (15, 8, 1, 'Registre logo depois de pagar o ITBI.');
INSERT INTO tb_cuidado (cd_cuidado, cd_orientacao, nr_ordem, ds_cuidado) VALUES (16, 9, 1, 'Guarde a matrícula nova com o seu nome.');
INSERT INTO tb_cuidado (cd_cuidado, cd_orientacao, nr_ordem, ds_cuidado) VALUES (17, 10, 1, 'Pague o ITBI só pela guia oficial da prefeitura.');
INSERT INTO tb_cuidado (cd_cuidado, cd_orientacao, nr_ordem, ds_cuidado) VALUES (18, 11, 1, 'Atualize o cadastro do imóvel na prefeitura.');
INSERT INTO tb_cuidado (cd_cuidado, cd_orientacao, nr_ordem, ds_cuidado) VALUES (19, 12, 1, 'Simule o financiamento no banco antes de assinar.');
INSERT INTO tb_cuidado (cd_cuidado, cd_orientacao, nr_ordem, ds_cuidado) VALUES (20, 12, 2, 'Não pague a ninguém para garantir a aprovação do crédito.');

-- tb_fonte_legal
INSERT INTO tb_fonte_legal (cd_fonte, cd_orientacao, nm_norma, ds_referencia, ds_url) VALUES (1, 1, 'Lei 6.015/1973', 'Lei de Registros Públicos', 'https://www.planalto.gov.br/ccivil_03/leis/l6015compilada.htm');
INSERT INTO tb_fonte_legal (cd_fonte, cd_orientacao, nm_norma, ds_referencia, ds_url) VALUES (2, 2, 'Lei 7.433/1985', 'Requisitos da escritura pública', 'https://www.planalto.gov.br/ccivil_03/leis/l7433.htm');
INSERT INTO tb_fonte_legal (cd_fonte, cd_orientacao, nm_norma, ds_referencia, ds_url) VALUES (3, 3, 'Lei 13.097/2015', 'Concentração de atos na matrícula', 'https://www.planalto.gov.br/ccivil_03/_ato2015-2018/2015/lei/l13097.htm');
INSERT INTO tb_fonte_legal (cd_fonte, cd_orientacao, nm_norma, ds_referencia, ds_url) VALUES (4, 4, 'Código Civil', 'Arts. 481 a 504 (compra e venda)', 'https://www.planalto.gov.br/ccivil_03/leis/2002/l10406compilada.htm');
INSERT INTO tb_fonte_legal (cd_fonte, cd_orientacao, nm_norma, ds_referencia, ds_url) VALUES (5, 5, 'Código Civil', 'Arts. 417 a 420 (arras)', 'https://www.planalto.gov.br/ccivil_03/leis/2002/l10406compilada.htm');
INSERT INTO tb_fonte_legal (cd_fonte, cd_orientacao, nm_norma, ds_referencia, ds_url) VALUES (6, 6, 'Código Civil', 'Art. 108 (escritura pública)', 'https://www.planalto.gov.br/ccivil_03/leis/2002/l10406compilada.htm');
INSERT INTO tb_fonte_legal (cd_fonte, cd_orientacao, nm_norma, ds_referencia, ds_url) VALUES (7, 7, 'Lei 8.935/1994', 'Lei dos cartórios (notários e registradores)', 'https://www.planalto.gov.br/ccivil_03/leis/l8935.htm');
INSERT INTO tb_fonte_legal (cd_fonte, cd_orientacao, nm_norma, ds_referencia, ds_url) VALUES (8, 8, 'Código Civil', 'Art. 1.245 (propriedade pelo registro)', 'https://www.planalto.gov.br/ccivil_03/leis/2002/l10406compilada.htm');
INSERT INTO tb_fonte_legal (cd_fonte, cd_orientacao, nm_norma, ds_referencia, ds_url) VALUES (9, 9, 'Lei 6.015/1973', 'Lei de Registros Públicos', 'https://www.planalto.gov.br/ccivil_03/leis/l6015compilada.htm');
INSERT INTO tb_fonte_legal (cd_fonte, cd_orientacao, nm_norma, ds_referencia, ds_url) VALUES (10, 10, 'Constituição Federal', 'Art. 156, II (ITBI municipal)', 'https://www.planalto.gov.br/ccivil_03/constituicao/constituicao.htm');
INSERT INTO tb_fonte_legal (cd_fonte, cd_orientacao, nm_norma, ds_referencia, ds_url) VALUES (11, 11, 'Código Tributário Nacional', 'Art. 130 (créditos do imóvel)', 'https://www.planalto.gov.br/ccivil_03/leis/l5172compilado.htm');
INSERT INTO tb_fonte_legal (cd_fonte, cd_orientacao, nm_norma, ds_referencia, ds_url) VALUES (12, 12, 'Lei 8.036/1990', 'FGTS', 'https://www.planalto.gov.br/ccivil_03/leis/l8036consol.htm');

-- tb_etapa
INSERT INTO tb_etapa (cd_etapa, cd_codigo, nr_ordem, nm_etapa, ds_etapa) VALUES (1, 'PESQUISA_IMOVEL', 1, 'Pesquisa e escolha do imóvel', 'Escolha o imóvel e confira o que o vendedor mostra.');
INSERT INTO tb_etapa (cd_etapa, cd_codigo, nr_ordem, nm_etapa, ds_etapa) VALUES (2, 'ANALISE_DOCUMENTAL', 2, 'Análise documental', 'Confira a matrícula, as certidões e as dívidas.');
INSERT INTO tb_etapa (cd_etapa, cd_codigo, nr_ordem, nm_etapa, ds_etapa) VALUES (3, 'NEGOCIACAO_CONTRATO', 3, 'Negociação e contrato', 'Negocie e leia o contrato com calma.');
INSERT INTO tb_etapa (cd_etapa, cd_codigo, nr_ordem, nm_etapa, ds_etapa) VALUES (4, 'ESCRITURA', 4, 'Escritura', 'Faça a escritura quando for necessária.');
INSERT INTO tb_etapa (cd_etapa, cd_codigo, nr_ordem, nm_etapa, ds_etapa) VALUES (5, 'ITBI_TRIBUTOS', 5, 'ITBI e tributos', 'Pague o ITBI pela guia oficial.');
INSERT INTO tb_etapa (cd_etapa, cd_codigo, nr_ordem, nm_etapa, ds_etapa) VALUES (6, 'REGISTRO_IMOVEL', 6, 'Registro do imóvel', 'Registre no cartório para ser o dono.');

-- tb_etapa_documento
INSERT INTO tb_etapa_documento (cd_documento, cd_etapa, nm_documento, ds_observacao) VALUES (1, 1, 'Documento de identidade', 'Original e cópia');
INSERT INTO tb_etapa_documento (cd_documento, cd_etapa, nm_documento, ds_observacao) VALUES (2, 1, 'Comprovante de renda', 'Para simular o financiamento');
INSERT INTO tb_etapa_documento (cd_documento, cd_etapa, nm_documento, ds_observacao) VALUES (3, 2, 'Certidão de matrícula atualizada', 'Emitida há poucos dias');
INSERT INTO tb_etapa_documento (cd_documento, cd_etapa, nm_documento, ds_observacao) VALUES (4, 2, 'Certidões negativas do vendedor', 'Ações e dívidas');
INSERT INTO tb_etapa_documento (cd_documento, cd_etapa, nm_documento, ds_observacao) VALUES (5, 3, 'Minuta do contrato', 'Leia antes de assinar');
INSERT INTO tb_etapa_documento (cd_documento, cd_etapa, nm_documento, ds_observacao) VALUES (6, 3, 'Recibo do sinal', 'Guarde a via assinada');
INSERT INTO tb_etapa_documento (cd_documento, cd_etapa, nm_documento, ds_observacao) VALUES (7, 4, 'Documentos do vendedor e do comprador', 'Identidade e estado civil');
INSERT INTO tb_etapa_documento (cd_documento, cd_etapa, nm_documento, ds_observacao) VALUES (8, 4, 'Comprovante do ITBI', 'Quando exigido');
INSERT INTO tb_etapa_documento (cd_documento, cd_etapa, nm_documento, ds_observacao) VALUES (9, 5, 'Guia do ITBI', 'Emitida pela prefeitura');
INSERT INTO tb_etapa_documento (cd_documento, cd_etapa, nm_documento, ds_observacao) VALUES (10, 5, 'Comprovante de pagamento do ITBI', 'Guarde para o cartório');
INSERT INTO tb_etapa_documento (cd_documento, cd_etapa, nm_documento, ds_observacao) VALUES (11, 6, 'Escritura ou contrato do banco', 'Título da compra');
INSERT INTO tb_etapa_documento (cd_documento, cd_etapa, nm_documento, ds_observacao) VALUES (12, 6, 'Matrícula nova', 'Com o seu nome');

-- tb_etapa_orientacao
INSERT INTO tb_etapa_orientacao (cd_etapa, cd_orientacao) VALUES (1, 1);
INSERT INTO tb_etapa_orientacao (cd_etapa, cd_orientacao) VALUES (1, 12);
INSERT INTO tb_etapa_orientacao (cd_etapa, cd_orientacao) VALUES (2, 1);
INSERT INTO tb_etapa_orientacao (cd_etapa, cd_orientacao) VALUES (2, 2);
INSERT INTO tb_etapa_orientacao (cd_etapa, cd_orientacao) VALUES (2, 3);
INSERT INTO tb_etapa_orientacao (cd_etapa, cd_orientacao) VALUES (3, 4);
INSERT INTO tb_etapa_orientacao (cd_etapa, cd_orientacao) VALUES (3, 5);
INSERT INTO tb_etapa_orientacao (cd_etapa, cd_orientacao) VALUES (4, 6);
INSERT INTO tb_etapa_orientacao (cd_etapa, cd_orientacao) VALUES (4, 7);
INSERT INTO tb_etapa_orientacao (cd_etapa, cd_orientacao) VALUES (5, 10);
INSERT INTO tb_etapa_orientacao (cd_etapa, cd_orientacao) VALUES (5, 11);
INSERT INTO tb_etapa_orientacao (cd_etapa, cd_orientacao) VALUES (6, 8);
INSERT INTO tb_etapa_orientacao (cd_etapa, cd_orientacao) VALUES (6, 9);

-- tb_cidadao_etapa
INSERT INTO tb_cidadao_etapa (cd_cidadao, cd_etapa, ds_status, dt_atualizacao) VALUES (1, 1, 'CONCLUIDA', TIMESTAMP '2026-11-02 10:00:00');
INSERT INTO tb_cidadao_etapa (cd_cidadao, cd_etapa, ds_status, dt_atualizacao) VALUES (1, 2, 'CONCLUIDA', TIMESTAMP '2026-11-03 10:00:00');
INSERT INTO tb_cidadao_etapa (cd_cidadao, cd_etapa, ds_status, dt_atualizacao) VALUES (1, 3, 'EM_ANDAMENTO', TIMESTAMP '2026-11-04 10:00:00');
INSERT INTO tb_cidadao_etapa (cd_cidadao, cd_etapa, ds_status, dt_atualizacao) VALUES (2, 1, 'CONCLUIDA', TIMESTAMP '2026-11-02 11:00:00');
INSERT INTO tb_cidadao_etapa (cd_cidadao, cd_etapa, ds_status, dt_atualizacao) VALUES (2, 2, 'EM_ANDAMENTO', TIMESTAMP '2026-11-03 11:00:00');
INSERT INTO tb_cidadao_etapa (cd_cidadao, cd_etapa, ds_status, dt_atualizacao) VALUES (3, 1, 'EM_ANDAMENTO', TIMESTAMP '2026-11-03 15:00:00');
INSERT INTO tb_cidadao_etapa (cd_cidadao, cd_etapa, ds_status, dt_atualizacao) VALUES (4, 1, 'CONCLUIDA', TIMESTAMP '2026-11-04 09:00:00');
INSERT INTO tb_cidadao_etapa (cd_cidadao, cd_etapa, ds_status, dt_atualizacao) VALUES (4, 2, 'CONCLUIDA', TIMESTAMP '2026-11-05 09:00:00');
INSERT INTO tb_cidadao_etapa (cd_cidadao, cd_etapa, ds_status, dt_atualizacao) VALUES (4, 3, 'CONCLUIDA', TIMESTAMP '2026-11-06 09:00:00');
INSERT INTO tb_cidadao_etapa (cd_cidadao, cd_etapa, ds_status, dt_atualizacao) VALUES (4, 4, 'EM_ANDAMENTO', TIMESTAMP '2026-11-07 09:00:00');
INSERT INTO tb_cidadao_etapa (cd_cidadao, cd_etapa, ds_status, dt_atualizacao) VALUES (5, 1, 'PENDENTE', TIMESTAMP '2026-11-04 20:00:00');
INSERT INTO tb_cidadao_etapa (cd_cidadao, cd_etapa, ds_status, dt_atualizacao) VALUES (6, 1, 'CONCLUIDA', TIMESTAMP '2026-11-05 12:00:00');
INSERT INTO tb_cidadao_etapa (cd_cidadao, cd_etapa, ds_status, dt_atualizacao) VALUES (6, 2, 'CONCLUIDA', TIMESTAMP '2026-11-06 12:00:00');
INSERT INTO tb_cidadao_etapa (cd_cidadao, cd_etapa, ds_status, dt_atualizacao) VALUES (7, 1, 'EM_ANDAMENTO', TIMESTAMP '2026-11-06 17:00:00');

-- tb_consulta
INSERT INTO tb_consulta (cd_consulta, cd_cidadao, cd_categoria, cd_orientacao, ds_pergunta, sg_uf, ds_etapa_atual, vl_confianca, ds_status, ds_canal, dt_consulta) VALUES (1, 1, 1, 3, 'Como descubro se um imóvel tem dívidas?', 'SP', 'ANALISE_DOCUMENTAL', 0.93, 'RESPONDIDA', 'WEB', TIMESTAMP '2026-11-03 10:15:00');
INSERT INTO tb_consulta (cd_consulta, cd_cidadao, cd_categoria, cd_orientacao, ds_pergunta, sg_uf, ds_etapa_atual, vl_confianca, ds_status, ds_canal, dt_consulta) VALUES (2, 1, 1, 1, 'O que é a matrícula do imóvel?', 'SP', 'ANALISE_DOCUMENTAL', 0.95, 'RESPONDIDA', 'WEB', TIMESTAMP '2026-11-03 10:20:00');
INSERT INTO tb_consulta (cd_consulta, cd_cidadao, cd_categoria, cd_orientacao, ds_pergunta, sg_uf, ds_etapa_atual, vl_confianca, ds_status, ds_canal, dt_consulta) VALUES (3, 1, 6, 10, 'O que é o ITBI e quem paga?', 'SP', 'ITBI_TRIBUTOS', 0.9, 'RESPONDIDA', 'WEB', TIMESTAMP '2026-11-04 09:00:00');
INSERT INTO tb_consulta (cd_consulta, cd_cidadao, cd_categoria, cd_orientacao, ds_pergunta, sg_uf, ds_etapa_atual, vl_confianca, ds_status, ds_canal, dt_consulta) VALUES (4, 2, 4, 6, 'Preciso fazer escritura pública?', 'RJ', 'ESCRITURA', 0.88, 'RESPONDIDA', 'WEB', TIMESTAMP '2026-11-04 10:00:00');
INSERT INTO tb_consulta (cd_consulta, cd_cidadao, cd_categoria, cd_orientacao, ds_pergunta, sg_uf, ds_etapa_atual, vl_confianca, ds_status, ds_canal, dt_consulta) VALUES (5, 2, 3, 12, 'Posso usar o FGTS na compra?', 'RJ', 'PESQUISA_IMOVEL', 0.91, 'RESPONDIDA', 'WEB', TIMESTAMP '2026-11-04 10:30:00');
INSERT INTO tb_consulta (cd_consulta, cd_cidadao, cd_categoria, cd_orientacao, ds_pergunta, sg_uf, ds_etapa_atual, vl_confianca, ds_status, ds_canal, dt_consulta) VALUES (6, 3, NULL, NULL, 'quero saber se posso comprar sem entrada', 'MG', 'PESQUISA_IMOVEL', 0.72, 'ESCLARECIMENTO', 'WEB', TIMESTAMP '2026-11-05 15:00:00');
INSERT INTO tb_consulta (cd_consulta, cd_cidadao, cd_categoria, cd_orientacao, ds_pergunta, sg_uf, ds_etapa_atual, vl_confianca, ds_status, ds_canal, dt_consulta) VALUES (7, 3, 3, 12, 'Posso usar o FGTS na compra?', 'MG', 'PESQUISA_IMOVEL', 0.89, 'RESPONDIDA', 'WEB', TIMESTAMP '2026-11-05 15:05:00');
INSERT INTO tb_consulta (cd_consulta, cd_cidadao, cd_categoria, cd_orientacao, ds_pergunta, sg_uf, ds_etapa_atual, vl_confianca, ds_status, ds_canal, dt_consulta) VALUES (8, 4, 5, 9, 'Como registro o imóvel no meu nome?', 'SP', 'REGISTRO_IMOVEL', 0.94, 'RESPONDIDA', 'TELEGRAM', TIMESTAMP '2026-11-06 08:00:00');
INSERT INTO tb_consulta (cd_consulta, cd_cidadao, cd_categoria, cd_orientacao, ds_pergunta, sg_uf, ds_etapa_atual, vl_confianca, ds_status, ds_canal, dt_consulta) VALUES (9, 4, 1, 3, 'Como descubro se um imóvel tem dívidas?', 'SP', 'ANALISE_DOCUMENTAL', 0.92, 'RESPONDIDA', 'TELEGRAM', TIMESTAMP '2026-11-06 08:10:00');
INSERT INTO tb_consulta (cd_consulta, cd_cidadao, cd_categoria, cd_orientacao, ds_pergunta, sg_uf, ds_etapa_atual, vl_confianca, ds_status, ds_canal, dt_consulta) VALUES (10, 4, 6, 11, 'O IPTU atrasado passa para mim?', 'SP', 'ANALISE_DOCUMENTAL', 0.87, 'RESPONDIDA', 'TELEGRAM', TIMESTAMP '2026-11-06 08:20:00');
INSERT INTO tb_consulta (cd_consulta, cd_cidadao, cd_categoria, cd_orientacao, ds_pergunta, sg_uf, ds_etapa_atual, vl_confianca, ds_status, ds_canal, dt_consulta) VALUES (11, 5, NULL, NULL, 'qual a previsão do tempo', 'BA', 'PESQUISA_IMOVEL', 0.31, 'NAO_RECONHECIDA', 'TELEGRAM', TIMESTAMP '2026-11-06 20:00:00');
INSERT INTO tb_consulta (cd_consulta, cd_cidadao, cd_categoria, cd_orientacao, ds_pergunta, sg_uf, ds_etapa_atual, vl_confianca, ds_status, ds_canal, dt_consulta) VALUES (12, 5, 1, 2, 'Quais documentos o vendedor precisa me mostrar?', 'BA', 'ANALISE_DOCUMENTAL', 0.86, 'RESPONDIDA', 'TELEGRAM', TIMESTAMP '2026-11-06 20:05:00');
INSERT INTO tb_consulta (cd_consulta, cd_cidadao, cd_categoria, cd_orientacao, ds_pergunta, sg_uf, ds_etapa_atual, vl_confianca, ds_status, ds_canal, dt_consulta) VALUES (13, 6, 2, 4, 'O que preciso conferir no contrato de compra e venda?', 'PR', 'NEGOCIACAO_CONTRATO', 0.9, 'RESPONDIDA', 'WEB', TIMESTAMP '2026-11-07 11:00:00');
INSERT INTO tb_consulta (cd_consulta, cd_cidadao, cd_categoria, cd_orientacao, ds_pergunta, sg_uf, ds_etapa_atual, vl_confianca, ds_status, ds_canal, dt_consulta) VALUES (14, 6, 2, 5, 'O que acontece se eu der um sinal?', 'PR', 'NEGOCIACAO_CONTRATO', 0.85, 'RESPONDIDA', 'WEB', TIMESTAMP '2026-11-07 11:10:00');
INSERT INTO tb_consulta (cd_consulta, cd_cidadao, cd_categoria, cd_orientacao, ds_pergunta, sg_uf, ds_etapa_atual, vl_confianca, ds_status, ds_canal, dt_consulta) VALUES (15, 6, 6, 10, 'O que é o ITBI e quem paga?', 'PR', 'ITBI_TRIBUTOS', 0.93, 'RESPONDIDA', 'WEB', TIMESTAMP '2026-11-07 11:20:00');
INSERT INTO tb_consulta (cd_consulta, cd_cidadao, cd_categoria, cd_orientacao, ds_pergunta, sg_uf, ds_etapa_atual, vl_confianca, ds_status, ds_canal, dt_consulta) VALUES (16, 7, 5, 8, 'Qual a diferença entre escritura e registro?', 'SC', 'ESCRITURA', 0.88, 'RESPONDIDA', 'TELEGRAM', TIMESTAMP '2026-11-08 09:00:00');
INSERT INTO tb_consulta (cd_consulta, cd_cidadao, cd_categoria, cd_orientacao, ds_pergunta, sg_uf, ds_etapa_atual, vl_confianca, ds_status, ds_canal, dt_consulta) VALUES (17, 7, 4, NULL, 'Quanto custa fazer a escritura?', 'SC', 'ESCRITURA', 0.84, 'ESCLARECIMENTO', 'TELEGRAM', TIMESTAMP '2026-11-08 09:05:00');
INSERT INTO tb_consulta (cd_consulta, cd_cidadao, cd_categoria, cd_orientacao, ds_pergunta, sg_uf, ds_etapa_atual, vl_confianca, ds_status, ds_canal, dt_consulta) VALUES (18, 7, NULL, NULL, 'asdf qwer', 'SC', 'ESCRITURA', 0.12, 'NAO_RECONHECIDA', 'TELEGRAM', TIMESTAMP '2026-11-08 09:10:00');
INSERT INTO tb_consulta (cd_consulta, cd_cidadao, cd_categoria, cd_orientacao, ds_pergunta, sg_uf, ds_etapa_atual, vl_confianca, ds_status, ds_canal, dt_consulta) VALUES (19, 8, NULL, NULL, 'teste de erro interno', 'SP', 'PESQUISA_IMOVEL', NULL, 'ERRO', 'WEB', TIMESTAMP '2026-11-09 12:00:00');
INSERT INTO tb_consulta (cd_consulta, cd_cidadao, cd_categoria, cd_orientacao, ds_pergunta, sg_uf, ds_etapa_atual, vl_confianca, ds_status, ds_canal, dt_consulta) VALUES (20, 8, NULL, NULL, 'teste de erro interno 2', 'SP', 'PESQUISA_IMOVEL', NULL, 'ERRO', 'WEB', TIMESTAMP '2026-11-09 12:05:00');

-- tb_servico
INSERT INTO tb_servico (cd_servico, nm_servico, ds_tipo, sg_uf, ds_url, ds_descricao) VALUES (1, 'Cartório de Registro de Imóveis (consulta oficial)', 'CARTORIO', 'SP', 'https://registradores.org.br', 'Pedido de certidão de matrícula pela internet (Registro de Imóveis do Brasil)');
INSERT INTO tb_servico (cd_servico, nm_servico, ds_tipo, sg_uf, ds_url, ds_descricao) VALUES (2, 'Prefeitura de São Paulo: ITBI', 'PREFEITURA', 'SP', 'https://www.prefeitura.sp.gov.br/itbi', 'Guia e regras do ITBI em São Paulo');
INSERT INTO tb_servico (cd_servico, nm_servico, ds_tipo, sg_uf, ds_url, ds_descricao) VALUES (3, 'Prefeitura de Belo Horizonte: ITBI', 'PREFEITURA', 'MG', 'https://prefeitura.pbh.gov.br/fazenda/tributos/ITBI', 'ITBI em Belo Horizonte');
INSERT INTO tb_servico (cd_servico, nm_servico, ds_tipo, sg_uf, ds_url, ds_descricao) VALUES (4, 'Prefeitura de Porto Alegre: Fazenda', 'PREFEITURA', 'RS', 'https://prefeitura.poa.br/smf', 'Secretaria da Fazenda de Porto Alegre');
INSERT INTO tb_servico (cd_servico, nm_servico, ds_tipo, sg_uf, ds_url, ds_descricao) VALUES (5, 'Caixa Econômica Federal: habitação', 'BANCO', 'SP', 'https://www.caixa.gov.br/voce/habitacao', 'Financiamento habitacional e simulador');
INSERT INTO tb_servico (cd_servico, nm_servico, ds_tipo, sg_uf, ds_url, ds_descricao) VALUES (6, 'FGTS: consulta de saldo', 'ORGAO', 'SP', 'https://www.caixa.gov.br/beneficios-trabalhador/fgts', 'Informações oficiais do FGTS');
INSERT INTO tb_servico (cd_servico, nm_servico, ds_tipo, sg_uf, ds_url, ds_descricao) VALUES (7, 'Defensoria Pública de São Paulo', 'DEFENSORIA', 'SP', 'https://www.defensoria.sp.def.br', 'Orientação jurídica gratuita');
INSERT INTO tb_servico (cd_servico, nm_servico, ds_tipo, sg_uf, ds_url, ds_descricao) VALUES (8, 'Defensoria Pública do Rio de Janeiro', 'DEFENSORIA', 'RJ', 'https://defensoria.rj.def.br', 'Orientação jurídica gratuita');
INSERT INTO tb_servico (cd_servico, nm_servico, ds_tipo, sg_uf, ds_url, ds_descricao) VALUES (9, 'Defensoria Pública de Minas Gerais', 'DEFENSORIA', 'MG', 'https://defensoria.mg.def.br', 'Orientação jurídica gratuita');
INSERT INTO tb_servico (cd_servico, nm_servico, ds_tipo, sg_uf, ds_url, ds_descricao) VALUES (10, 'Receita Federal: ganho de capital (GCAP)', 'ORGAO', 'SP', 'https://www.gov.br/receitafederal', 'Programa de apuração de ganho de capital na venda de imóveis');

COMMIT;

-- ======================================================================
-- 3) CONSULTAS (10, numeradas)
-- ======================================================================
-- 10 consultas numeradas, ligadas a perguntas reais do LarOuAyê.

-- 1) "Quais orientações sobre impostos eu posso ler, em ordem alfabética?"  (filtro + ordenação)
SELECT cd_orientacao, nm_titulo, ds_revisao
  FROM tb_orientacao
 WHERE cd_categoria = (SELECT cd_categoria FROM tb_categoria WHERE cd_codigo = 'TRIBUTOS')
   AND st_ativo = 1
 ORDER BY nm_titulo;

-- 2) "Quantas perguntas cada categoria recebeu?"  (COUNT + GROUP BY + INNER JOIN)
SELECT ca.nm_categoria, COUNT(*) AS qt_consultas
  FROM tb_consulta co
  INNER JOIN tb_categoria ca ON ca.cd_categoria = co.cd_categoria
 GROUP BY ca.nm_categoria
 ORDER BY qt_consultas DESC, ca.nm_categoria;

-- 3) "Quão confiável é o classificador em cada situação da resposta?"  (AVG, MAX, MIN, GROUP BY)
SELECT ds_status,
       COUNT(vl_confianca)           AS qt_com_confianca,
       ROUND(AVG(vl_confianca), 2)   AS media_confianca,
       MAX(vl_confianca)             AS maior_confianca,
       MIN(vl_confianca)             AS menor_confianca
  FROM tb_consulta
 GROUP BY ds_status
 ORDER BY ds_status;

-- 4) "Quais categorias são as mais procuradas (mais de 2 perguntas)?"  (HAVING)
SELECT ca.nm_categoria, COUNT(*) AS qt_consultas
  FROM tb_consulta co
  INNER JOIN tb_categoria ca ON ca.cd_categoria = co.cd_categoria
 GROUP BY ca.nm_categoria
HAVING COUNT(*) > 2
 ORDER BY qt_consultas DESC;

-- 5) "Que respostas o Carlos e a Dona Lúcia receberam no Telegram?"  (INNER JOIN, filtros LIKE, IN e BETWEEN)
SELECT u.nm_cidadao, co.ds_pergunta, o.nm_titulo, co.vl_confianca
  FROM tb_consulta co
  INNER JOIN tb_cidadao u    ON u.cd_cidadao = co.cd_cidadao
  INNER JOIN tb_orientacao o ON o.cd_orientacao = co.cd_orientacao
 WHERE co.ds_canal = 'TELEGRAM'
   AND u.nm_cidadao IN ('Carlos Mendes', 'Dona Lúcia')
   AND co.vl_confianca BETWEEN 0.80 AND 1
   AND co.ds_pergunta LIKE '%?'
 ORDER BY u.nm_cidadao, co.dt_consulta;

-- 6) "Há orientações que ninguém consultou ainda?"  (LEFT JOIN + COUNT: mostra também quem tem zero)
SELECT o.cd_orientacao, o.nm_titulo, COUNT(co.cd_consulta) AS qt_consultas
  FROM tb_orientacao o
  LEFT JOIN tb_consulta co ON co.cd_orientacao = o.cd_orientacao
 GROUP BY o.cd_orientacao, o.nm_titulo
 ORDER BY qt_consultas, o.nm_titulo;

-- 7) "Em cada etapa da compra, quantas pessoas já concluíram?"  (RIGHT JOIN: todas as etapas, mesmo sem progresso)
SELECT e.nr_ordem, e.nm_etapa,
       COUNT(CASE WHEN ue.ds_status = 'CONCLUIDA' THEN 1 END) AS qt_concluidas
  FROM tb_cidadao_etapa ue
  RIGHT JOIN tb_etapa e ON e.cd_etapa = ue.cd_etapa
 GROUP BY e.nr_ordem, e.nm_etapa
 ORDER BY e.nr_ordem;

-- 8) "Quem recebeu respostas com confiança acima da média geral?"  (subconsulta)
SELECT u.nm_cidadao, ROUND(AVG(co.vl_confianca), 2) AS media_pessoal
  FROM tb_consulta co
  INNER JOIN tb_cidadao u ON u.cd_cidadao = co.cd_cidadao
 WHERE co.vl_confianca IS NOT NULL
 GROUP BY u.nm_cidadao
HAVING AVG(co.vl_confianca) > (SELECT AVG(vl_confianca) FROM tb_consulta)
 ORDER BY media_pessoal DESC, u.nm_cidadao;

-- 9) "De onde vêm as perguntas? Quanto cada estado representa?"  (COUNT, cálculo de percentual, subconsulta)
SELECT sg_uf,
       COUNT(*) AS qt_consultas,
       ROUND(COUNT(*) * 100 / (SELECT COUNT(*) FROM tb_consulta), 1) AS pc_do_total
  FROM tb_consulta
 GROUP BY sg_uf
 ORDER BY qt_consultas DESC, sg_uf;

-- 10) "Quanto de cada jornada já foi concluído?"  (SUM, cálculo, JOIN e subconsulta)
SELECT u.nm_cidadao,
       SUM(CASE WHEN ue.ds_status = 'CONCLUIDA' THEN 1 ELSE 0 END) AS etapas_concluidas,
       (SELECT COUNT(*) FROM tb_etapa) AS etapas_total,
       ROUND(SUM(CASE WHEN ue.ds_status = 'CONCLUIDA' THEN 1 ELSE 0 END) * 100 / (SELECT COUNT(*) FROM tb_etapa), 0) AS pc_jornada
  FROM tb_cidadao u
  INNER JOIN tb_cidadao_etapa ue ON ue.cd_cidadao = u.cd_cidadao
 GROUP BY u.nm_cidadao
 ORDER BY pc_jornada DESC, u.nm_cidadao;

-- ======================================================================
-- 4) UPDATE e DELETE (com WHERE)
-- ======================================================================
-- Operações de atualização e exclusão (ambas com WHERE).

-- UPDATE: o responsável jurídico revisou a orientação 10 (ITBI). Só então ela passa a REVISADO, com a data.
UPDATE tb_orientacao
   SET ds_revisao = 'REVISADO',
       dt_revisao = DATE '2026-11-12'
 WHERE cd_orientacao = 10;

-- DELETE: remove as consultas de teste automático com erro interno (usuário de teste 8).
DELETE FROM tb_consulta
 WHERE cd_cidadao = 8
   AND ds_status = 'ERRO';

COMMIT;
