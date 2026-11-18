import json
from unittest import mock

import pandas as pd
import pytest

import app as aplicacao
from larouaye_ia import fontes_publicas, nucleo, servico, telegram_bot

SEM_REDE = mock.Mock()
SEM_REDE.consultar_cep.return_value = None
SEM_REDE.meta_selic.return_value = None


@pytest.fixture()
def cli():
    return aplicacao.create_app().test_client()


# ---------- dados e modelos ----------
def test_dois_conjuntos_de_dados_com_rotulos_diferentes():
    i, e = pd.read_csv(nucleo.DADOS / "intencao_treino.csv"), pd.read_csv(nucleo.DADOS / "etapa_treino.csv")
    assert set(i.rotulo) != set(e.rotulo)
    assert len(set(i.rotulo)) == 10 and len(set(e.rotulo)) == 6


def test_teste_nao_vaza_para_o_treino():
    for nome in ("intencao", "etapa"):
        tr, te = nucleo.carregar(nome)
        assert not set(tr.texto.str.lower().str.rstrip("?")) & set(te.texto.str.lower().str.rstrip("?"))


def test_metricas_minimas_nos_dois_modelos():
    m = json.loads((nucleo.MODELOS / "metricas.json").read_text(encoding="utf-8"))
    assert m["intencao"]["acuracia_teste"] >= 0.80
    assert m["etapa"]["acuracia_teste"] >= 0.85


def test_teste_cego_e_validacao_real_nao_vazam_para_o_treino():
    tr, _ = nucleo.carregar("intencao")
    treino = set(tr.texto.str.lower().str.rstrip("?"))
    for arquivo in ("intencao_teste_cego.csv", "intencao_validacao_real.csv"):
        df = pd.read_csv(nucleo.DADOS / arquivo)
        assert not treino & set(df.texto.str.lower().str.rstrip("?")), arquivo


def test_teste_cego_mantem_acuracia_e_precisao_quando_responde():
    """Mede em frases escritas depois do ajuste final. Se cair, alguem piorou o modelo."""
    from treino import avaliar_intencao
    r = avaliar_intencao.main(nucleo.MODELOS / "modelo_intencao.joblib")["teste_cego"]
    assert r["acuracia"] >= 0.88
    assert r["acerto_quando_responde"] >= 0.95


def test_perguntas_reais_do_instagram_sao_respondidas_direto_e_na_categoria_certa():
    modelo, _ = servico.modelos()
    real = pd.read_csv(nucleo.DADOS / "intencao_validacao_real.csv")
    for texto, esperado in zip(real.texto, real.rotulo):
        c = servico.classificar(texto)
        assert c["categoria"] == esperado, texto
        assert c["confianca"] >= servico.LIMIAR_RESPONDER, (texto, c["confianca"])


def test_modelos_sao_diferentes():
    a, b = servico.modelos()
    assert type(a.named_steps["clf"]) is not type(b.named_steps["clf"])


# ---------- base juridica ----------
def test_toda_categoria_do_modelo_tem_orientacao():
    cats = {o["categoria"] for o in servico.base()["orientacoes"]}
    modelo, _ = servico.modelos()
    assert set(modelo.classes_) - {"FORA_DO_ESCOPO"} == cats


def test_toda_orientacao_tem_base_legal_e_cuidados():
    for o in servico.base()["orientacoes"]:
        assert o["baseLegal"] and o["cuidados"] and o["conteudo"], o["id"]
        assert all(b["url"].startswith("https://www.planalto.gov.br/") for b in o["baseLegal"])


def test_nao_ha_data_de_revisao_sem_revisao():
    for o in servico.base()["orientacoes"]:
        assert o["revisado"] or o["dataRevisao"] is None


def test_etapas_batem_com_o_modelo_de_etapa_e_com_o_front():
    _, m = servico.modelos()
    codigos = {e["codigo"] for e in servico.base()["etapas"]}
    assert codigos == set(m.classes_)


# ---------- decisao ----------
def test_corretor_alterou_ir_vira_fraude():
    r = servico.responder("O corretor alterou meu IRRF e colocou minha esposa como dependente", fontes=SEM_REDE)
    assert r["status"] == "RESPONDIDA" and r["categoria"] == "FRAUDE_GOLPES"
    assert any("Lei 7.492" in b["norma"] for b in r["resposta"]["baseLegal"])


def test_escritura_e_registro():
    r = servico.responder("Como checar se o imóvel possui escritura?", fontes=SEM_REDE)
    assert r["categoria"] == "ESCRITURA_REGISTRO"


def test_fora_do_escopo_nao_inventa_resposta_juridica():
    r = servico.responder("Quero comprar um tênis novo", fontes=SEM_REDE)
    assert r["status"] == "FORA_DO_ESCOPO" and not r["resposta"]["baseLegal"] if "baseLegal" in r["resposta"] else True


def test_texto_sem_sentido_nunca_vira_orientacao_juridica():
    """Texto sem sentido pode cair em fora do escopo, nao reconhecida ou esclarecimento. Nunca em RESPONDIDA."""
    for texto in ("asdf qwer", "kkkk", "??? ???", "xyz abc 123"):
        assert servico.responder(texto, fontes=SEM_REDE)["status"] in ("NAO_RECONHECIDA", "ESCLARECIMENTO", "FORA_DO_ESCOPO"), texto


def test_toda_resposta_traz_aviso_de_informacao_geral_e_de_revisao():
    r = servico.responder("O que é ITBI?", fontes=SEM_REDE)["resposta"]
    assert servico.AVISO_GERAL in r["cuidados"] and servico.AVISO_REVISAO in r["cuidados"]
    assert "dataRevisao" not in r


def test_esclarecimento_devolve_opcoes_e_escolha_responde():
    f = mock.Mock(); f.consultar_cep.return_value = None; f.meta_selic.return_value = None
    with mock.patch.object(servico, "classificar", return_value={"categoria": "CONTRATO", "confianca": 0.5, "etapaSugerida": "X", "confiancaEtapa": 0.5,
            "maisProvaveis": [{"categoria": "CONTRATO", "confianca": 0.5}, {"categoria": "FINANCIAMENTO", "confianca": 0.3}]}):
        r = servico.responder("pergunta confusa", fontes=f)
        assert r["status"] == "ESCLARECIMENTO" and r["opcoes"] == ["Contrato de compra e venda", "Financiamento"]
        r2 = servico.responder("pergunta confusa", categoria_escolhida="FINANCIAMENTO", fontes=f)
        assert r2["status"] == "RESPONDIDA" and r2["categoria"] == "FINANCIAMENTO"


# ---------- APIs publicas (simuladas) ----------
class RespostaFalsa:
    def __init__(self, dados): self.dados = dados
    def raise_for_status(self): pass
    def json(self): return self.dados


class SessaoFalsa:
    def __init__(self, dados=None, falha=False): self.dados, self.falha, self.chamadas = dados, falha, []
    def get(self, url, **kw):
        self.chamadas.append(url)
        if self.falha: raise ConnectionError("sem rede")
        return RespostaFalsa(self.dados)


def test_cep_valido_invalido_e_falha_de_rede():
    fontes_publicas.limpar_cache()
    s = SessaoFalsa({"localidade": "São Paulo", "uf": "SP", "ibge": "3550308"})
    assert fontes_publicas.consultar_cep("01001-000", s) == {"cep": "01001000", "cidade": "São Paulo", "uf": "SP", "ibge": "3550308"}
    assert fontes_publicas.consultar_cep("123", s) is None
    fontes_publicas.limpar_cache()
    assert fontes_publicas.consultar_cep("01001000", SessaoFalsa(falha=True)) is None
    fontes_publicas.limpar_cache()
    assert fontes_publicas.consultar_cep("99999999", SessaoFalsa({"erro": True})) is None


def test_municipios_e_selic():
    fontes_publicas.limpar_cache()
    assert fontes_publicas.listar_municipios("SP", SessaoFalsa([{"nome": "Santos"}, {"nome": "Bauru"}])) == ["Bauru", "Santos"]
    assert fontes_publicas.listar_municipios("S1") is None
    fontes_publicas.limpar_cache()
    assert fontes_publicas.meta_selic(SessaoFalsa([{"data": "01/01/2026", "valor": "14,50"}])) == {"data": "01/01/2026", "valor": 14.5}


def test_cep_enriquece_resposta_de_impostos():
    f = mock.Mock(); f.consultar_cep.return_value = {"cidade": "Santos", "uf": "SP"}; f.meta_selic.return_value = None
    r = servico.responder("Quais impostos pago ao comprar um imóvel?", cep="11010000", fontes=f)
    assert any("Prefeitura de Santos" in c for c in r["resposta"]["cuidados"])


# ---------- API no contrato do front ----------
def test_saude_e_conteudo(cli):
    assert cli.get("/api/saude").json == {"status": "UP"}
    assert len(cli.get("/api/orientacoes").json) == 12
    assert [e["codigo"] for e in cli.get("/api/etapas").json][0] == "PESQUISA_IMOVEL"
    assert cli.get("/api/categorias/1/orientacoes").status_code == 200
    assert cli.get("/api/categorias/999/orientacoes").status_code == 404


def test_fluxo_completo_usuario_consulta_historico_progresso(cli):
    u = cli.post("/api/usuarios", json={"nome": "Ana"})
    assert u.status_code == 201
    uid = u.json["id"]
    c = cli.post(f"/api/usuarios/{uid}/consultas", json={"pergunta": "Como descubro se um imóvel tem dívidas?", "uf": "SP", "etapa": "ANALISE_DOCUMENTAL"})
    assert c.status_code == 201 and c.json["status"] == "RESPONDIDA" and c.json["resposta"]["baseLegal"]
    assert "classificacao" not in c.json
    h = cli.get(f"/api/usuarios/{uid}/consultas").json
    assert h[0]["consultaId"] == c.json["consultaId"]
    assert cli.post(f"/api/usuarios/{uid}/etapas", json={"etapaId": 2, "status": "CONCLUIDA"}).status_code == 200
    assert cli.get(f"/api/usuarios/{uid}/etapas").json == [{"etapaId": 2, "status": "CONCLUIDA"}]


def test_validacao_e_erros_em_json_sem_stack_trace(cli):
    assert cli.post("/api/usuarios", json={"nome": "A"}).status_code == 400
    uid = cli.post("/api/usuarios", json={"nome": "Ana"}).json["id"]
    r = cli.post(f"/api/usuarios/{uid}/consultas", json={"pergunta": "x"})
    assert r.status_code == 400 and "pergunta" in r.json
    assert cli.post(f"/api/usuarios/{uid}/consultas", json={"pergunta": "Como funciona o FGTS?", "uf": "XX"}).status_code == 400
    assert cli.post("/api/usuarios/999/consultas", json={"pergunta": "Como funciona o FGTS?"}).status_code == 404
    assert cli.post(f"/api/usuarios/{uid}/etapas", json={"etapaId": 99, "status": "CONCLUIDA"}).status_code == 400
    assert cli.get("/api/xyz").status_code == 404 and cli.post("/api/saude").status_code == 405
    assert "Traceback" not in cli.get("/api/xyz").get_data(as_text=True)


def test_classificar_devolve_os_dois_modelos(cli):
    for rota in ("/classificar", "/api/classificar"):
        d = cli.post(rota, json={"pergunta": "Quero registrar a escritura em cartório"}).json
        assert {"categoria", "confianca", "etapaSugerida", "confiancaEtapa", "maisProvaveis"} <= set(d)


def test_servicos_exigem_uf_valida(cli):
    assert cli.get("/api/servicos").status_code == 400
    lista = cli.get("/api/servicos?uf=sp").json
    assert len(lista) >= 5 and all(s["uf"] == "SP" for s in lista)


def test_cors_libera_o_front_local(cli):
    r = cli.get("/api/saude", headers={"Origin": "http://localhost:5173"})
    assert r.headers.get("Access-Control-Allow-Origin") == "http://localhost:5173"


# ---------- Telegram ----------
def upd(texto, chat=7):
    return {"update_id": 1, "message": {"chat": {"id": chat}, "text": texto}}


def test_telegram_comandos(cli):
    assert "LarOuAyê" in telegram_bot.tratar_update(upd("/start"))[0]["texto"]
    assert "Passo a passo" in telegram_bot.tratar_update(upd("/etapas"))[0]["texto"]
    assert "Sites oficiais" in telegram_bot.tratar_update(upd("/fontes@meubot"))[0]["texto"]


def test_telegram_pergunta_responde_com_base_legal_em_html():
    m = telegram_bot.tratar_update(upd("O corretor alterou meu imposto de renda para financiar"), responder=lambda t: servico.responder(t, fontes=SEM_REDE))[0]
    assert "<b>" in m["texto"] and "Base legal" in m["texto"] and len(m["texto"]) <= 4000


def test_telegram_escapa_html_e_trata_voz_e_vazio():
    resp = {"status": "RESPONDIDA", "resposta": {"titulo": "<script>", "conteudo": "a & b", "cuidados": []}}
    t = telegram_bot.formatar_resposta(resp)
    assert "<script>" not in t and "&lt;script&gt;" in t and "a &amp; b" in t
    assert "áudio" in telegram_bot.tratar_update({"message": {"chat": {"id": 1}, "voice": {}}})[0]["texto"]
    assert telegram_bot.tratar_update({"foo": 1}) == []


def test_telegram_esclarecimento_gera_botoes_e_callback_responde():
    falso = {"status": "ESCLARECIMENTO", "opcoes": ["Contrato de compra e venda", "Financiamento"], "opcoesCodigos": ["CONTRATO", "FINANCIAMENTO"]}
    m = telegram_bot.tratar_update(upd("confuso"), responder=lambda t: falso)[0]
    assert m["teclado"][0][0]["callback_data"] == "cat:CONTRATO"
    cb = {"callback_query": {"id": "9", "data": "cat:FINANCIAMENTO", "message": {"chat": {"id": 7}}}}
    r = telegram_bot.tratar_update(cb, responder=lambda t, categoria_escolhida=None: servico.responder(t, categoria_escolhida=categoria_escolhida, fontes=SEM_REDE))[0]
    assert "financiamento" in r["texto"].lower() and r["callback_id"] == "9"


def test_telegram_mensagem_enorme_e_recusada():
    assert "resuma" in telegram_bot.tratar_update(upd("a" * 600))[0]["texto"].lower()


def test_webhook_exige_segredo(cli, monkeypatch):
    monkeypatch.setenv("TELEGRAM_WEBHOOK_SECRET", "abc123")
    monkeypatch.delenv("TELEGRAM_BOT_TOKEN", raising=False)
    assert cli.post("/api/telegram/webhook", json=upd("/start")).status_code == 403
    assert cli.post("/api/telegram/webhook", json=upd("/start"), headers={"X-Telegram-Bot-Api-Secret-Token": "errado"}).status_code == 403
    assert cli.post("/api/telegram/webhook", json=upd("/start"), headers={"X-Telegram-Bot-Api-Secret-Token": "abc123"}).status_code == 200


def test_enviar_chama_sendmessage_com_html_e_teclado():
    s = mock.Mock()
    telegram_bot.enviar("TOKEN", {"chat_id": 7, "texto": "oi", "teclado": [[{"text": "a", "callback_data": "cat:X"}]], "callback_id": "1"}, s)
    urls = [c.args[0] for c in s.post.call_args_list]
    assert urls[0].endswith("/botTOKEN/sendMessage") and urls[1].endswith("/answerCallbackQuery")
    assert s.post.call_args_list[0].kwargs["json"]["parse_mode"] == "HTML"
