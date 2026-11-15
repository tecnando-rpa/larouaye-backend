-- =====================================================================
-- 06_verificacao.sql — auditoria de integridade. TODA consulta "PROBLEMA" deve voltar ZERO linhas.
-- Rode depois de qualquer carga ou correção manual. Cada linha devolvida é um problema real.
-- =====================================================================

-- P1. REVISADO sem nenhuma fonte legal (regra do Java que o CHECK não consegue expressar)
SELECT 'P1 revisado sem fonte' AS problema, o.cd_orientacao AS referencia
  FROM tb_orientacao o
 WHERE o.ds_revisao = 'REVISADO'
   AND NOT EXISTS (SELECT 1 FROM tb_fonte_legal f WHERE f.cd_orientacao = o.cd_orientacao);

-- P2. Orientação ativa sem nenhum cuidado cadastrado
SELECT 'P2 ativa sem cuidado' AS problema, o.cd_orientacao AS referencia
  FROM tb_orientacao o
 WHERE o.st_ativo = 1
   AND NOT EXISTS (SELECT 1 FROM tb_cuidado u WHERE u.cd_orientacao = o.cd_orientacao);

-- P3. Etapa sem documento no checklist
SELECT 'P3 etapa sem documento' AS problema, e.cd_etapa AS referencia
  FROM tb_etapa e
 WHERE NOT EXISTS (SELECT 1 FROM tb_etapa_documento d WHERE d.cd_etapa = e.cd_etapa);

-- P4. Etapas com ordem falhando (devem ser 1..N sem buracos)
SELECT 'P4 ordem de etapa com buraco' AS problema, COUNT(*) AS referencia
  FROM tb_etapa
HAVING MAX(nr_ordem) <> COUNT(*);

-- P5. Categoria sem nenhuma orientação ativa (o sistema só encaminharia, nunca responderia)
SELECT 'P5 categoria sem orientacao ativa' AS problema, g.cd_categoria AS referencia
  FROM tb_categoria g
 WHERE NOT EXISTS (SELECT 1 FROM tb_orientacao o WHERE o.cd_categoria = g.cd_categoria AND o.st_ativo = 1);

-- P6. Consulta RESPONDIDA cuja orientação foi desativada depois (histórico aponta para conteúdo inativo)
SELECT 'P6 respondida com orientacao inativa' AS problema, q.cd_consulta AS referencia
  FROM tb_consulta q
  INNER JOIN tb_orientacao o ON o.cd_orientacao = q.cd_orientacao
 WHERE o.st_ativo = 0;

-- ---------------------------------------------------------------------
-- Resumo de contagens (conferir contra o esperado: 11 tabelas, 133 registros no seed)
-- ---------------------------------------------------------------------
SELECT 'tb_cidadao' AS tabela, COUNT(*) AS qt FROM tb_cidadao
UNION ALL SELECT 'tb_categoria', COUNT(*) FROM tb_categoria
UNION ALL SELECT 'tb_orientacao', COUNT(*) FROM tb_orientacao
UNION ALL SELECT 'tb_cuidado', COUNT(*) FROM tb_cuidado
UNION ALL SELECT 'tb_fonte_legal', COUNT(*) FROM tb_fonte_legal
UNION ALL SELECT 'tb_etapa', COUNT(*) FROM tb_etapa
UNION ALL SELECT 'tb_etapa_documento', COUNT(*) FROM tb_etapa_documento
UNION ALL SELECT 'tb_etapa_orientacao', COUNT(*) FROM tb_etapa_orientacao
UNION ALL SELECT 'tb_cidadao_etapa', COUNT(*) FROM tb_cidadao_etapa
UNION ALL SELECT 'tb_consulta', COUNT(*) FROM tb_consulta
UNION ALL SELECT 'tb_servico', COUNT(*) FROM tb_servico;

-- Objetos inválidos no esquema (deve voltar zero linhas)
-- Somente Oracle (user_objects não existe em SQLite):
-- SELECT object_name, object_type FROM user_objects WHERE status = 'INVALID';
