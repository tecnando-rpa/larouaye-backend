# Gera ENTREGA_LarOuAye_BuildingRelationalDatabase.sql na ordem exigida pelo edital:
# tabelas -> INSERTs -> 10 consultas -> UPDATE -> DELETE.
from pathlib import Path
r = Path(__file__).parent
def ler(n): return (r / n).read_text(encoding="utf-8").strip()
partes = [
 ("1) CRIACAO DAS TABELAS (DDL)", "01_ddl.sql"),
 ("2) INSERCAO DOS DADOS (massa de dados)", "02_seed.sql"),
 ("3) CONSULTAS (10, numeradas)", "04_consultas.sql"),
 ("4) UPDATE e DELETE (com WHERE)", "03_dml.sql"),
]
out = ["-- LarOuAye - Building Relational Database (FIAP Global Solution 2026/2)",
       "-- Ordem: tabelas -> INSERTs -> consultas -> UPDATE -> DELETE. Rode em conexao limpa (ou 00_reset.sql antes).\n"]
for t, n in partes:
    out.append("-- " + "=" * 70 + f"\n-- {t}\n-- " + "=" * 70 + "\n" + ler(n) + "\n")
(r / "ENTREGA_LarOuAye_Banco.sql").write_text("\n".join(out), encoding="utf-8")
