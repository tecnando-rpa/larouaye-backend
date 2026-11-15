-- =====================================================================
-- 05_views.sql — visões de leitura (relatórios e auditoria). Não alteram dados.
-- =====================================================================

-- Histórico legível: quem perguntou o quê, a categoria e a orientação entregue.
CREATE OR REPLACE VIEW v_historico_consulta AS
SELECT q.cd_consulta,
       c.nm_cidadao,
       q.ds_canal,
       q.ds_pergunta,
       q.sg_uf,
       q.ds_status,
       q.vl_confianca,
       g.nm_categoria,
       o.nm_titulo AS nm_orientacao,
       q.dt_consulta
  FROM tb_consulta q
  INNER JOIN tb_cidadao   c ON c.cd_cidadao   = q.cd_cidadao
  LEFT  JOIN tb_categoria g ON g.cd_categoria = q.cd_categoria
  LEFT  JOIN tb_orientacao o ON o.cd_orientacao = q.cd_orientacao;

-- Progresso: todas as etapas para cada pessoa (as sem registro contam como PENDENTE).
CREATE OR REPLACE VIEW v_progresso_cidadao AS
SELECT c.cd_cidadao,
       c.nm_cidadao,
       e.cd_etapa,
       e.nr_ordem,
       e.nm_etapa,
       COALESCE(p.ds_status, 'PENDENTE') AS ds_status,
       p.dt_atualizacao
  FROM tb_cidadao c
  CROSS JOIN tb_etapa e
  LEFT JOIN tb_cidadao_etapa p ON p.cd_cidadao = c.cd_cidadao AND p.cd_etapa = e.cd_etapa;

-- Auditoria do conteúdo jurídico: orientação, quantas fontes e cuidados, e se está revisada.
CREATE OR REPLACE VIEW v_orientacao_auditoria AS
SELECT o.cd_orientacao,
       o.nm_titulo,
       g.cd_codigo AS cd_categoria_codigo,
       o.ds_revisao,
       o.dt_revisao,
       o.st_ativo,
       (SELECT COUNT(*) FROM tb_fonte_legal f WHERE f.cd_orientacao = o.cd_orientacao) AS qt_fontes,
       (SELECT COUNT(*) FROM tb_cuidado     u WHERE u.cd_orientacao = o.cd_orientacao) AS qt_cuidados
  FROM tb_orientacao o
  INNER JOIN tb_categoria g ON g.cd_categoria = o.cd_categoria;
