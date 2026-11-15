-- =====================================================================
-- 00_reset.sql — apaga TODOS os objetos do LarOuAyê, sem erro se algum não existir.
-- Use só em desenvolvimento/teste: apaga dados. Pode ser executado quantas vezes quiser.
-- (ORA-00942 = tabela não existe | ORA-02289 = sequence não existe | ORA-01418 = índice não existe)
-- =====================================================================
BEGIN
    FOR t IN (SELECT column_value AS nome FROM TABLE(sys.odcivarchar2list(
              'TB_SERVICO', 'TB_CONSULTA', 'TB_CIDADAO_ETAPA', 'TB_ETAPA_ORIENTACAO', 'TB_ETAPA_DOCUMENTO',
              'TB_ETAPA', 'TB_FONTE_LEGAL', 'TB_CUIDADO', 'TB_ORIENTACAO', 'TB_CATEGORIA', 'TB_CIDADAO'))) LOOP
        BEGIN
            EXECUTE IMMEDIATE 'DROP TABLE ' || t.nome || ' CASCADE CONSTRAINTS PURGE';
        EXCEPTION
            WHEN OTHERS THEN
                IF SQLCODE <> -942 THEN
                    RAISE;
                END IF;
        END;
    END LOOP;

    FOR s IN (SELECT column_value AS nome FROM TABLE(sys.odcivarchar2list(
              'SQ_TB_SERVICO', 'SQ_TB_CONSULTA', 'SQ_TB_ETAPA_DOCUMENTO', 'SQ_TB_ETAPA', 'SQ_TB_FONTE_LEGAL',
              'SQ_TB_CUIDADO', 'SQ_TB_ORIENTACAO', 'SQ_TB_CATEGORIA', 'SQ_TB_CIDADAO'))) LOOP
        BEGIN
            EXECUTE IMMEDIATE 'DROP SEQUENCE ' || s.nome;
        EXCEPTION
            WHEN OTHERS THEN
                IF SQLCODE <> -2289 THEN
                    RAISE;
                END IF;
        END;
    END LOOP;

    FOR v IN (SELECT column_value AS nome FROM TABLE(sys.odcivarchar2list(
              'V_HISTORICO_CONSULTA', 'V_PROGRESSO_CIDADAO', 'V_ORIENTACAO_AUDITORIA'))) LOOP
        BEGIN
            EXECUTE IMMEDIATE 'DROP VIEW ' || v.nome;
        EXCEPTION
            WHEN OTHERS THEN
                IF SQLCODE <> -942 THEN
                    RAISE;
                END IF;
        END;
    END LOOP;
END;
/
