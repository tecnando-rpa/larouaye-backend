-- =====================================================================
-- 00_executar_tudo.sql — cria o banco do zero em UM comando, parando no primeiro erro.
-- SQL Developer: abra este arquivo e use "Executar Script" (F5) com a pasta dos scripts como diretório de trabalho
-- SQLcl/SQL*Plus: cd até esta pasta e rode  @00_executar_tudo.sql
-- Ordem: reset → estrutura → dados → atualização/remoção → visões → verificação
-- =====================================================================
WHENEVER SQLERROR EXIT FAILURE ROLLBACK
SET ECHO ON
SET SERVEROUTPUT ON

@00_reset.sql
@01_ddl.sql
@02_seed.sql
@03_dml.sql
@05_views.sql
@06_verificacao.sql

PROMPT === Banco criado. As consultas 'P1'..'P6' acima devem ter retornado ZERO linhas. ===
-- 04_consultas.sql traz as 10 consultas numeradas para os prints (rode à parte).
