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
