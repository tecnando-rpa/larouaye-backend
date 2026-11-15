"""Gera o dicionário de dados (Markdown) e o DER (SVG/PNG) a partir de 01_ddl.sql.
Uso: python3 docs/gerar_docs.py   (precisa do Graphviz 'dot' para o DER)
Assim a documentação nunca fica diferente do banco: é derivada do próprio DDL."""
import re
import subprocess
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
ddl = (RAIZ / "01_ddl.sql").read_text(encoding="utf-8")

PREFIXO = {"cd": "Código", "nm": "Nome", "ds": "Descrição/texto", "dt": "Data/hora", "sg": "Sigla", "nr": "Número", "vl": "Valor", "st": "Situação (0/1)"}
DESCRICAO = {
    "cd_cidadao": "Identificador da pessoa", "nm_cidadao": "Nome (ou apelido) da pessoa; sem CPF", "ds_email": "E-mail opcional, único sem diferenciar maiúsculas",
    "ds_canal": "Por onde a pessoa chegou: WEB ou TELEGRAM", "cd_id_externo": "Id da pessoa no canal (chat_id do Telegram)", "dt_cadastro": "Quando a pessoa foi cadastrada",
    "cd_categoria": "Identificador da categoria", "cd_codigo": "Código estável usado pelo sistema (ex.: DOCUMENTACAO, ESCRITURA)", "nm_categoria": "Nome mostrado à pessoa",
    "ds_categoria": "Explicação da categoria", "cd_orientacao": "Identificador da orientação jurídica", "nm_titulo": "Título curto da orientação",
    "ds_pergunta": "Pergunta que a orientação responde (em orientacao) / pergunta feita pela pessoa (em consulta)", "ds_conteudo": "Texto jurídico em linguagem simples",
    "ds_url_video": "Link opcional de vídeo explicativo (http/https)", "ds_revisao": "PENDENTE ou REVISADO (conferido juridicamente)", "dt_revisao": "Data da revisão jurídica; obrigatória se REVISADO",
    "st_ativo": "1 = pode ser entregue; 0 = desativada", "cd_cuidado": "Identificador do cuidado", "nr_ordem": "Posição na lista (cuidado) ou na jornada (etapa)", "ds_cuidado": "Cuidado prático a tomar",
    "cd_fonte": "Identificador da fonte legal", "nm_norma": "Lei, norma ou órgão (ex.: Lei 6.015/1973)", "ds_referencia": "Artigo ou trecho de referência", "ds_url": "Link oficial (http/https)",
    "cd_etapa": "Identificador da etapa da compra", "nm_etapa": "Nome da etapa", "ds_etapa": "O que fazer nesta etapa", "cd_documento": "Identificador do documento",
    "nm_documento": "Nome do documento do checklist", "ds_observacao": "Observação (original, cópia, validade…)", "ds_status": "Situação: progresso (PENDENTE, EM_ANDAMENTO, CONCLUIDA) ou consulta (RESPONDIDA, ESCLARECIMENTO, NAO_RECONHECIDA, ERRO)",
    "dt_atualizacao": "Última mudança de status", "cd_consulta": "Identificador da consulta", "sg_uf": "Sigla do estado (uma das 27 UFs)", "ds_etapa_atual": "Código da etapa informada pela pessoa",
    "vl_confianca": "Confiança do classificador, de 0 a 1 (informativa)", "dt_consulta": "Quando a pergunta foi feita", "cd_servico": "Identificador do serviço", "nm_servico": "Nome do canal oficial",
    "ds_tipo": "CARTORIO, PREFEITURA, BANCO, DEFENSORIA ou ORGAO", "ds_descricao": "Para que serve o canal",
}

tabelas = {}
for m in re.finditer(r"CREATE TABLE (\w+) \((.*?)\n\);", ddl, flags=re.S):
    nome, corpo = m.group(1), m.group(2)
    cols, cons = [], []
    for linha in corpo.split("\n"):
        l = linha.strip().rstrip(",")
        if not l or l.startswith("--"):
            continue
        if l.upper().startswith("CONSTRAINT"):
            cons.append(l)
        else:
            mm = re.match(r"(\w+)\s+([A-Z0-9_]+(?:\([^)]*\))?)\s*(.*)", l)
            if mm:
                resto = mm.group(3)
                padrao = re.search(r"DEFAULT\s+('[^']*'|\w+)", resto)
                cols.append({"nome": mm.group(1), "tipo": mm.group(2), "nulo": "NOT NULL" not in resto.upper(), "padrao": padrao.group(1) if padrao else ""})
    tabelas[nome] = {"cols": cols, "cons": cons, "desc": ""}

for m in re.finditer(r"COMMENT ON TABLE\s+(\w+)\s+IS\s+'((?:[^']|'')*)'", ddl):
    tabelas[m.group(1)]["desc"] = m.group(2).replace("''", "'")
comentarios = {(m.group(1), m.group(2)): m.group(3).replace("''", "'") for m in re.finditer(r"COMMENT ON COLUMN\s+(\w+)\.(\w+)\s+IS\s+'((?:[^']|'')*)'", ddl)}

fks = []
for t, d in tabelas.items():
    pk, uks, cks = [], [], []
    fk_cols = {}
    for c in d["cons"]:
        if " PRIMARY KEY" in c.upper():
            pk = [x.strip() for x in re.search(r"PRIMARY KEY \(([^)]*)\)", c, flags=re.I).group(1).split(",")]
        elif " UNIQUE" in c.upper():
            uks.append(re.search(r"UNIQUE \(([^)]*)\)", c, flags=re.I).group(1))
        elif " FOREIGN KEY" in c.upper():
            mm = re.search(r"FOREIGN KEY \((\w+)\) REFERENCES (\w+) \((\w+)\)(\s+ON DELETE CASCADE)?", c, flags=re.I)
            fk_cols[mm.group(1)] = f"{mm.group(2)}.{mm.group(3)}"
            fks.append((t, mm.group(1), mm.group(2), bool(mm.group(4))))
        elif " CHECK" in c.upper():
            cks.append(c)
    d["pk"], d["uks"], d["fk"], d["cks"] = pk, uks, fk_cols, cks

linhas = ["# Dicionário de dados — LarOuAyê (Oracle)", "",
          "> Gerado automaticamente de `01_ddl.sql` por `docs/gerar_docs.py`. Não edite à mão: rode o script de novo.", "",
          f"**{len(tabelas)} tabelas** · convenção: `tb_` tabela, `cd_` código/chave, `nm_` nome, `ds_` descrição, `dt_` data, `sg_` sigla, `nr_` número, `vl_` valor, `st_` situação.", ""]
for t, d in tabelas.items():
    linhas += [f"## {t}", "", d["desc"], "", "| Coluna | Tipo | Obrigatório | Padrão | Chave | Descrição |", "|---|---|---|---|---|---|"]
    for c in d["cols"]:
        chave = []
        if c["nome"] in d["pk"]:
            chave.append("PK")
        if c["nome"] in d["fk"]:
            chave.append("FK → " + d["fk"][c["nome"]])
        desc = comentarios.get((t, c["nome"])) or DESCRICAO.get(c["nome"]) or PREFIXO.get(c["nome"].split("_")[0], "")
        linhas.append(f"| `{c['nome']}` | {c['tipo']} | {'não' if c['nulo'] else 'sim'} | {c['padrao'] or '—'} | {', '.join(chave) or '—'} | {desc} |")
    extra = []
    if d["uks"]:
        extra.append("**Únicos:** " + "; ".join(f"({u})" for u in d["uks"]))
    if d["cks"]:
        extra.append("**Regras (CHECK):** " + "; ".join(re.search(r"CHECK \((.*)\)$", c, flags=re.I).group(1) if re.search(r"CHECK \((.*)\)$", c, flags=re.I) else c for c in d["cks"]))
    linhas += [""] + [e + "  " for e in extra] + [""]
linhas += ["## Relacionamentos", "", "| Filha (N) | Chave | Pai (1) | Ao apagar o pai |", "|---|---|---|---|"]
for t, c, pai, casc in fks:
    linhas.append(f"| {t} | {c} | {pai} | {'apaga os filhos (CASCADE)' if casc else 'BLOQUEIA (restrição)'} |")
linhas += ["", "N:N por tabela associativa: `tb_cidadao_etapa` (com status) e `tb_etapa_orientacao`.", ""]
(RAIZ / "docs" / "DICIONARIO-DADOS.md").write_text("\n".join(linhas), encoding="utf-8")

# ---------------- DER (Graphviz, notação pé-de-galinha) ----------------
cor = {"tb_cidadao": "#E8F1F2", "tb_consulta": "#E8F1F2", "tb_cidadao_etapa": "#FBE9E4", "tb_etapa_orientacao": "#FBE9E4"}
dot = ['digraph DER {', 'rankdir=LR; splines=polyline; nodesep=0.5; ranksep=1.3; fontname="Helvetica";',
       'node [shape=plain, fontname="Helvetica", fontsize=10]; edge [fontname="Helvetica", fontsize=9, arrowhead=crow, arrowtail=tee, dir=both, headlabel="N", taillabel="1", labeldistance=1.6, color="#145A5E"];']
for t, d in tabelas.items():
    fundo = cor.get(t, "#F7F5EF")
    rows = [f'<TR><TD BGCOLOR="#145A5E" ALIGN="LEFT"><FONT COLOR="white"><B>{t}</B></FONT></TD></TR>']
    for c in d["cols"]:
        marca = "PK " if c["nome"] in d["pk"] else ("FK " if c["nome"] in d["fk"] else "   ")
        rows.append(f'<TR><TD ALIGN="LEFT" PORT="{c["nome"]}" BGCOLOR="{fundo}">{marca}{c["nome"]} <FONT COLOR="#666666">{c["tipo"]}</FONT></TD></TR>')
    dot.append(f'{t} [label=<<TABLE BORDER="1" CELLBORDER="0" CELLSPACING="0" CELLPADDING="3">{"".join(rows)}</TABLE>>];')
for t, c, pai, casc in fks:
    dot.append(f'{pai} -> {t} [headport="{c}", tailport=e, headlabel="N", taillabel="1"];' if False else f'{pai} -> {t};')
dot.append("}")
(RAIZ / "docs" / "der.dot").write_text("\n".join(dot), encoding="utf-8")
for fmt in ("svg", "png"):
    subprocess.run(["dot", f"-T{fmt}", "-Gdpi=130", str(RAIZ / "docs" / "der.dot"), "-o", str(RAIZ / "docs" / f"der.{fmt}")], check=True)
print("gerado: docs/DICIONARIO-DADOS.md, docs/der.svg, docs/der.png")
