import ast
import csv
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))
import orientador as o  # noqa: E402


@pytest.fixture(autouse=True)
def pasta(tmp_path, monkeypatch):
    monkeypatch.setenv("LAROUAYE_PASTA", str(tmp_path))
    return tmp_path


def digitar(monkeypatch, respostas):
    fila = iter(respostas)
    monkeypatch.setattr("builtins.input", lambda _="": next(fila))


# ---------- regras da disciplina (o edital dá NOTA ZERO para classes e -15 por list comprehension) ----------
def arvore(nome):
    return ast.parse((RAIZ / nome).read_text(encoding="utf-8"))


@pytest.mark.parametrize("arquivo", ["orientador.py", "conteudo.py"])
def test_sem_classes_e_sem_comprehension(arquivo):
    proibidos = (ast.ClassDef, ast.ListComp, ast.SetComp, ast.DictComp, ast.GeneratorExp)
    achados = [type(n).__name__ for n in ast.walk(arvore(arquivo)) if isinstance(n, proibidos)]
    assert achados == []


def test_sem_modulos_de_oo():
    fonte = (RAIZ / "orientador.py").read_text(encoding="utf-8")
    for proibido in ("dataclass", "NamedTuple", "namedtuple", "__init__", "self."):
        assert proibido not in fonte


def test_todos_os_conceitos_exigidos_aparecem():
    t = arvore("orientador.py")
    nos = {type(n) for n in ast.walk(t)}
    assert ast.Match in nos and ast.While in nos and ast.For in nos and ast.If in nos
    assert ast.JoinedStr in nos and ast.Tuple in nos and ast.Dict in nos and ast.Return in nos
    fonte = (RAIZ / "orientador.py").read_text(encoding="utf-8")
    assert "elif" in fonte and "set(" in fonte and "json.dump" in fonte and "csv.writer" in fonte and "input(" in fonte
    funcoes = [n for n in ast.walk(t) if isinstance(n, ast.FunctionDef)]
    assert any(f.args.args for f in funcoes) and len(funcoes) >= 15


def test_funcoes_tem_docstring_ou_comentario():
    sem = [n.name for n in ast.walk(arvore("orientador.py")) if isinstance(n, ast.FunctionDef) and n.name != "main" and not ast.get_docstring(n)]
    # funcoes sem docstring precisam ser curtas (ate 6 linhas)
    t = arvore("orientador.py")
    for n in ast.walk(t):
        if isinstance(n, ast.FunctionDef) and n.name in sem:
            assert n.end_lineno - n.lineno <= 7, n.name


# ---------- regras de negocio ----------
def test_pendencias_mantem_ordem():
    assert o.calcular_pendencias(["a", "b", "c"], ["b"]) == ["a", "c"]
    assert o.calcular_pendencias(["a"], ["a", "x"]) == []


def test_risco_baixo_medio_alto():
    n = len(o.SINAIS_FRAUDE)
    assert o.avaliar_risco([False] * n) == ("BAIXO", 0)
    nivel, _ = o.avaliar_risco([True, False, False, False, False, False])
    assert nivel == "MÉDIO"
    assert o.avaliar_risco([True] * n)[0] == "ALTO"


def test_renda_alterada_sozinha_ja_e_alerta_medio_ou_mais():
    resp = [False] * len(o.SINAIS_FRAUDE)
    resp[2] = True  # alterar renda ou IR
    assert o.avaliar_risco(resp)[0] in ("MÉDIO", "ALTO")


def test_contagem_e_mais_consultado():
    h = [{"assunto": "A"}, {"assunto": "B"}, {"assunto": "A"}]
    assert o.contar_assuntos(h) == {"A": 2, "B": 1}
    assert o.assunto_mais_consultado({"A": 2, "B": 1}) == ("A", 2)
    assert o.assunto_mais_consultado({}) is None


def test_etapas_em_ordem_e_com_documentos():
    ordem = [c for c, _ in o.etapas_ordenadas()]
    assert ordem[0] == "PESQUISA_IMOVEL" and ordem[-1] == "REGISTRO_IMOVEL" and len(ordem) == 6
    assert all(o.documentos_da_etapa(c) for c in ordem)


# ---------- entradas invalidas ----------
def test_pedir_numero_repete_ate_ser_valido(monkeypatch, capsys):
    digitar(monkeypatch, ["abc", "9", "-1", "", "3"])
    assert o.pedir_numero("n: ", 1, 5) == 3
    saida = capsys.readouterr().out
    assert "Digite só o número" in saida and "Escolha um número de 1 a 5" in saida


def test_pedir_sim_nao_e_uf(monkeypatch):
    digitar(monkeypatch, ["talvez", "SIM"])
    assert o.pedir_sim_nao("ok?") is True
    digitar(monkeypatch, ["não"])
    assert o.pedir_sim_nao("ok?") is False
    digitar(monkeypatch, ["XX", "sp"])
    assert o.pedir_uf() == "SP"


def test_pedir_texto_exige_minimo(monkeypatch):
    digitar(monkeypatch, [" ", "a", "Ana"])
    assert o.pedir_texto("nome: ") == "Ana"


# ---------- persistencia ----------
def test_perfil_salva_e_recupera(pasta):
    p = o.perfil_vazio()
    p.update({"nome": "ana", "uf": "SP", "etapa": "ESCRITURA", "docs_ok": ["x"]})
    o.salvar_perfil(p)
    assert o.carregar_perfil() == p
    assert json.loads((pasta / "perfil.json").read_text(encoding="utf-8"))["nome"] == "ana"


def test_perfil_quebrado_nao_derruba_o_programa(pasta):
    (pasta / "perfil.json").write_text("{quebrado", encoding="utf-8")
    assert o.carregar_perfil() == o.perfil_vazio()


def test_historico_csv_com_cabecalho_e_acentos(pasta):
    assert o.ler_historico() == []
    o.registrar_consulta("Fraudes e golpes", "-")
    o.registrar_consulta("Leilão", "ESCRITURA")
    linhas = list(csv.reader((pasta / "historico.csv").open(encoding="utf-8")))
    assert linhas[0] == o.CABECALHO_HISTORICO and len(linhas) == 3
    assert o.ler_historico()[1]["assunto"] == "Leilão"


# ---------- telas ----------
def test_conferir_documentos_marca_e_mostra_pendencias(monkeypatch, capsys):
    p = o.perfil_vazio(); p["etapa"] = "ANALISE_DOCUMENTAL"
    docs = o.documentos_da_etapa("ANALISE_DOCUMENTAL")
    digitar(monkeypatch, ["s", "n", "s", "n"][:len(docs)])
    o.conferir_documentos(p)
    assert p["docs_ok"] == [docs[0], docs[2]]
    assert docs[1] in capsys.readouterr().out
    assert o.carregar_perfil()["docs_ok"] == p["docs_ok"]


def test_conferir_sem_etapa_orienta(capsys):
    o.conferir_documentos(o.perfil_vazio())
    assert "Primeiro escolha sua etapa" in capsys.readouterr().out


def test_resumo_traz_nome_pendencias_e_aviso():
    p = o.perfil_vazio(); p.update({"nome": "ana maria", "uf": "SP", "etapa": "ESCRITURA"})
    r = o.montar_resumo(p, [{"assunto": "Leilão"}])
    assert "Ana Maria" in r and "[ ]" in r and "Leilão: 1x" in r and o.AVISO in r


# ---------- programa completo pelo terminal (stdin real) ----------
def rodar(entrada, pasta):
    env = {**os.environ, "LAROUAYE_PASTA": str(pasta), "PYTHONIOENCODING": "utf-8"}
    return subprocess.run([sys.executable, str(RAIZ / "orientador.py")], input=entrada, capture_output=True, text=True, env=env, cwd=RAIZ, timeout=30)


def test_sessao_completa_e_dados_voltam_na_proxima_execucao(pasta):
    r = rodar("1\nana\nsp\n2\n4\n1\n6\n7\n0\n", pasta)
    assert r.returncode == 0 and "Pronto, Ana!" in r.stdout and "RESUMO DE ORIENTAÇÕES" in r.stdout
    r2 = rodar("0\n", pasta)
    assert "Olá, Ana" in r2.stdout


def test_entradas_malucas_nao_quebram(pasta):
    r = rodar("abc\n99\n\n5\n" + "s\n" * 6 + "6\n0\n", pasta)
    assert r.returncode == 0 and "Traceback" not in r.stderr
    assert "Nível de alerta: ALTO" in r.stdout and "PARE" in r.stdout
