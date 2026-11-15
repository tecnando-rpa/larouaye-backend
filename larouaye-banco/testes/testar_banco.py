"""Teste automático dos scripts SQL (rodado em SQLite como aproximação). Uso: python3 testes/testar_banco.py
Aviso: o Oracle real é a fonte da verdade; este teste confere lógica, constraints e resultados esperados."""
import re
import sqlite3
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent


def preparar(arquivo):
    t = (RAIZ / arquivo).read_text(encoding="utf-8")
    t = re.sub(r"/\*.*?\*/", "", t, flags=re.S)
    t = re.sub(r"(?m)^\s*--.*$", "", t)
    t = re.sub(r"(?is)CREATE SEQUENCE[^;]*;", "", t)
    t = re.sub(r"(?im)^COMMENT ON .*$", "", t)
    t = re.sub(r"(?im)^\s*COMMIT;", "", t)
    t = t.replace("SYSTIMESTAMP", "CURRENT_TIMESTAMP")
    return re.sub(r"(?:TIMESTAMP|DATE) '", "'", t)


def conferir(nome, condicao):
    print(("OK   " if condicao else "FALHA"), nome)
    if not condicao:
        conferir.falhas += 1


conferir.falhas = 0
con = sqlite3.connect(":memory:")
con.execute("PRAGMA foreign_keys=ON")
con.executescript(preparar("01_ddl.sql"))
con.executescript(preparar("02_seed.sql"))

tabelas = [r[0] for r in con.execute("select name from sqlite_master where type='table'")]
total = sum(con.execute(f"select count(*) from {t}").fetchone()[0] for t in tabelas)
conferir(f"pelo menos 6 tabelas ({len(tabelas)})", len(tabelas) >= 6)
conferir(f"pelo menos 60 registros ({total})", total >= 60)
conferir("todas as tabelas têm dados", all(con.execute(f"select count(*) from {t}").fetchone()[0] > 0 for t in tabelas))

con.executescript(preparar("03_dml.sql"))
conferir("DELETE removeu só as 2 consultas com erro", con.execute("select count(*) from tb_consulta").fetchone()[0] == 18)
conferir("UPDATE marcou a orientação 10 como REVISADO", con.execute("select ds_revisao from tb_orientacao where cd_orientacao=10").fetchone()[0] == "REVISADO")

consultas = [s for s in preparar("04_consultas.sql").split(";") if s.strip()]
conferir("10 consultas", len(consultas) == 10)
resultados = [con.execute(s).fetchall() for s in consultas]
conferir("todas as 10 consultas retornam linhas", all(len(r) > 0 for r in resultados))
conferir("consulta 6 (LEFT JOIN) mostra orientação sem consulta", resultados[5][0][2] == 0)
conferir("consulta 7 (RIGHT JOIN) lista as 6 etapas", len(resultados[6]) == 6)
conferir("consulta 4 (HAVING) só traz categorias com mais de 2", all(r[1] > 2 for r in resultados[3]))

for descricao, sql in [
    ("Telegram sem id externo é rejeitado", "insert into tb_cidadao(cd_cidadao,nm_cidadao,ds_canal) values (99,'x','TELEGRAM')"),
    ("UF minúscula é rejeitada", "insert into tb_consulta(cd_consulta,cd_cidadao,ds_pergunta,sg_uf,ds_status) values (99,1,'x','sp','RESPONDIDA')"),
    ("confiança fora de 0 a 1 é rejeitada", "insert into tb_consulta(cd_consulta,cd_cidadao,ds_pergunta,sg_uf,vl_confianca,ds_status) values (98,1,'x','SP',1.5,'RESPONDIDA')"),
    ("REVISADO sem data é rejeitado", "insert into tb_orientacao values (99,1,'t','p','c',null,'REVISADO',null,1)"),
    ("FK inexistente é rejeitada", "insert into tb_cidadao_etapa(cd_cidadao,cd_etapa,ds_status) values (1,99,'PENDENTE')"),
    ("status inválido é rejeitado", "insert into tb_cidadao_etapa(cd_cidadao,cd_etapa,ds_status) values (1,5,'XYZ')"),
]:
    try:
        con.execute(sql)
        conferir(descricao, False)
    except sqlite3.IntegrityError:
        conferir(descricao, True)

# ---------------------------------------------------------------------------------------------
# Visões e auditoria de integridade (06_verificacao.sql: toda consulta "problema" deve dar ZERO linhas)
# ---------------------------------------------------------------------------------------------
views = preparar("05_views.sql").replace("CREATE OR REPLACE VIEW", "CREATE VIEW")
con.executescript(views)
conferir("v_historico_consulta devolve linhas", con.execute("select count(*) from v_historico_consulta").fetchone()[0] == 18)
conferir("v_progresso_cidadao cruza pessoas x etapas",
         con.execute("select count(*) from v_progresso_cidadao").fetchone()[0] == 8 * 6)
conferir("v_orientacao_auditoria tem as 12 orientações", con.execute("select count(*) from v_orientacao_auditoria").fetchone()[0] == 12)

ver = preparar("06_verificacao.sql")
blocos = [b.strip() for b in ver.split(";") if b.strip().upper().startswith("SELECT")]
problemas = [b for b in blocos if "AS problema" in b]
conferir(f"06_verificacao tem {len(problemas)} auditorias de problema", len(problemas) == 6)
for b in problemas:
    nome = b.split("'")[1]
    linhas = con.execute(b).fetchall()
    conferir(f"auditoria '{nome}' retorna zero linhas", len(linhas) == 0)

# a auditoria PEGA o problema quando ele existe (prova de que não é teste "que sempre passa")
con.execute("insert into tb_orientacao values (500,1,'Sem fonte','p','conteudo',null,'REVISADO','2026-11-12',1)")
achou = con.execute(problemas[0]).fetchall()
conferir("auditoria P1 detecta REVISADO sem fonte", len(achou) == 1 and achou[0][1] == 500)
con.execute("delete from tb_orientacao where cd_orientacao=500")

# ---------------------------------------------------------------------------------------------
# Scripts de reset e de execução única
# ---------------------------------------------------------------------------------------------
ddl_txt = (RAIZ / "01_ddl.sql").read_text(encoding="utf-8")
reset_txt = (RAIZ / "00_reset.sql").read_text(encoding="utf-8").upper()
tabs_ddl = set(re.findall(r"CREATE TABLE (\w+)", ddl_txt, flags=re.I))
seqs_ddl = set(re.findall(r"CREATE SEQUENCE (\w+)", ddl_txt, flags=re.I))
views_ddl = set(re.findall(r"CREATE OR REPLACE VIEW (\w+)", (RAIZ / "05_views.sql").read_text(encoding="utf-8"), flags=re.I))
conferir("reset apaga todas as tabelas do DDL", all(f"'{t.upper()}'" in reset_txt for t in tabs_ddl))
conferir("reset apaga todas as sequences do DDL", all(f"'{t.upper()}'" in reset_txt for t in seqs_ddl))
conferir("reset apaga todas as views", all(f"'{t.upper()}'" in reset_txt for t in views_ddl))
conferir("reset ignora 'não existe' (-942 e -2289)", "-942" in reset_txt and "-2289" in reset_txt)
tudo = (RAIZ / "00_executar_tudo.sql").read_text(encoding="utf-8")
conferir("executar_tudo para no primeiro erro", "WHENEVER SQLERROR EXIT FAILURE ROLLBACK" in tudo)
conferir("executar_tudo chama todos os scripts na ordem",
         [m for m in re.findall(r"^@(\S+)", tudo, flags=re.M)] == ["00_reset.sql", "01_ddl.sql", "02_seed.sql", "03_dml.sql", "05_views.sql", "06_verificacao.sql"])

# ---------------------------------------------------------------------------------------------
# Endurecimento do DDL: dado ruim é barrado NO BANCO
# ---------------------------------------------------------------------------------------------
def barrado(descricao, sql):
    try:
        con.execute(sql)
        conferir(descricao, False)
    except sqlite3.IntegrityError:
        conferir(descricao, True)

barrado("e-mail repetido com outra caixa (MARIA@...) é barrado", "insert into tb_cidadao(cd_cidadao,nm_cidadao,ds_email) values (90,'x','MARIA@EXEMPLO.COM')")
barrado("e-mail sem @ é barrado", "insert into tb_cidadao(cd_cidadao,nm_cidadao,ds_email) values (91,'x','semarroba')")
barrado("nome só com espaços é barrado", "insert into tb_cidadao(cd_cidadao,nm_cidadao) values (92,'   ')")
barrado("UF inexistente (ZZ) é barrada na consulta", "insert into tb_consulta(cd_consulta,cd_cidadao,ds_pergunta,sg_uf,ds_status) values (93,1,'x','ZZ','NAO_RECONHECIDA')")
barrado("UF inexistente (ZZ) é barrada no serviço", "insert into tb_servico(cd_servico,nm_servico,ds_tipo,sg_uf) values (94,'x','BANCO','ZZ')")
barrado("RESPONDIDA sem orientação é barrada", "insert into tb_consulta(cd_consulta,cd_cidadao,ds_pergunta,sg_uf,ds_status) values (95,1,'x','SP','RESPONDIDA')")
barrado("NAO_RECONHECIDA com orientação é barrada", "insert into tb_consulta(cd_consulta,cd_cidadao,cd_orientacao,ds_pergunta,sg_uf,ds_status) values (96,1,1,'x','SP','NAO_RECONHECIDA')")
barrado("pergunta em branco é barrada", "insert into tb_consulta(cd_consulta,cd_cidadao,ds_pergunta,sg_uf,ds_status) values (97,1,'  ','SP','NAO_RECONHECIDA')")
barrado("link sem http é barrado (serviço)", "insert into tb_servico(cd_servico,nm_servico,ds_tipo,sg_uf,ds_url) values (98,'x','BANCO','SP','ftp://x')")
barrado("link sem http é barrado (fonte legal)", "insert into tb_fonte_legal(cd_fonte,cd_orientacao,nm_norma,ds_url) values (98,1,'x','javascript:alert(1)')")
barrado("código de categoria em minúscula é barrado", "insert into tb_categoria(cd_categoria,cd_codigo,nm_categoria) values (98,'abc','x')")
barrado("duas etapas com a mesma ordem são barradas", "insert into tb_etapa(cd_etapa,cd_codigo,nr_ordem,nm_etapa,ds_etapa) values (98,'OUTRA',1,'x','y')")
barrado("cuidado repetido na mesma posição é barrado", "insert into tb_cuidado(cd_cuidado,cd_orientacao,nr_ordem,ds_cuidado) values (998,1,1,'x')")
barrado("apagar orientação já usada em consulta é barrado (FK sem cascata)", "delete from tb_orientacao where cd_orientacao in (select cd_orientacao from tb_consulta where cd_orientacao is not null limit 1)")
barrado("apagar cidadão com consulta é barrado", "delete from tb_cidadao where cd_cidadao=1")
barrado("apagar categoria com orientação é barrado", "delete from tb_categoria where cd_categoria=1")

# cascata nos filhos puros: apagar a etapa leva junto os documentos e a ligação com orientações
etapa_livre = con.execute("select cd_etapa from tb_etapa where cd_etapa not in (select cd_etapa from tb_cidadao_etapa) limit 1").fetchone()[0]
docs_antes = con.execute("select count(*) from tb_etapa_documento where cd_etapa=?", (etapa_livre,)).fetchone()[0]
con.execute("delete from tb_etapa where cd_etapa=?", (etapa_livre,))
conferir(f"apagar etapa leva junto os {docs_antes} documentos (cascata)",
         docs_antes > 0 and con.execute("select count(*) from tb_etapa_documento where cd_etapa=?", (etapa_livre,)).fetchone()[0] == 0)
conferir("apagar etapa leva junto a ligação com orientações",
         con.execute("select count(*) from tb_etapa_orientacao where cd_etapa=?", (etapa_livre,)).fetchone()[0] == 0)

# ---------------------------------------------------------------------------------------------
# DAOs Java x DDL: toda coluna usada existe na tabela e todo NOT NULL sem DEFAULT é preenchido no INSERT
# ---------------------------------------------------------------------------------------------
import glob
JAVA = RAIZ.parent / "larouaye-java" / "src" / "main" / "java" / "br" / "com" / "fiap" / "larouaye" / "dao"
if JAVA.exists():
    colunas = {}
    obrigatorias = {}
    for t in tabs_ddl:
        info = con.execute(f"pragma table_info({t})").fetchall()
        colunas[t.lower()] = {r[1].lower() for r in info}
        obrigatorias[t.lower()] = {r[1].lower() for r in info if r[3] == 1 and r[4] is None}
    erros = []
    inserts = 0
    for f in glob.glob(str(JAVA / "Jdbc*Dao.java")):
        fonte = open(f, encoding="utf-8").read()
        # junta literais Java adjacentes ("..." + "...") para reconstruir cada comando SQL
        for bloco in re.findall(r'"(INSERT INTO .*?)"\s*;', fonte, flags=re.S):
            sql = re.sub(r'"\s*\+\s*"', "", bloco)
            m = re.match(r"INSERT INTO (\w+) \(([^)]*)\) VALUES \(([^)]*)\)", sql)
            if not m:
                erros.append(f"INSERT não reconhecido em {Path(f).name}")
                continue
            inserts += 1
            tabela, cols, vals = m.group(1).lower(), [c.strip().lower() for c in m.group(2).split(",")], m.group(3).split(",")
            if tabela not in colunas:
                erros.append(f"tabela {tabela} não existe")
                continue
            desconhecidas = [c for c in cols if c not in colunas[tabela]]
            faltando = obrigatorias[tabela] - set(cols)
            if desconhecidas:
                erros.append(f"{tabela}: colunas inexistentes {desconhecidas}")
            if faltando:
                erros.append(f"{tabela}: NOT NULL sem valor no INSERT {sorted(faltando)}")
            if len(cols) != len(vals):
                erros.append(f"{tabela}: {len(cols)} colunas e {len(vals)} valores")
        for bloco in re.findall(r'"(UPDATE (\w+) SET .*?)"', fonte, flags=re.S):
            tabela = bloco[1].lower()
            alvo = re.findall(r"(\w+) = \?", re.sub(r'"\s*\+\s*"', "", bloco[0]))
            desconhecidas = [c for c in alvo if c.lower() not in colunas.get(tabela, set())]
            if desconhecidas:
                erros.append(f"UPDATE {tabela}: colunas inexistentes {desconhecidas}")
    conferir(f"{inserts} INSERTs dos DAOs Java batem com o DDL (colunas, NOT NULL, nº de valores)", inserts == 9 and not erros)
    for e in erros:
        print("      ->", e)
else:
    print("(projeto Java não encontrado ao lado: verificação DAO x DDL pulada)")

print("\nRESULTADO:", "FALHOU" if conferir.falhas else "tudo certo")
sys.exit(1 if conferir.falhas else 0)
