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
