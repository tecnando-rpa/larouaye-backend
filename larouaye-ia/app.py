"""API Flask: classificador de ML + backend de DESENVOLVIMENTO no mesmo contrato que o front usa.

Producao: o Java (Spring/JDBC/Oracle) e o ponto central e chama POST /classificar daqui.
Desenvolvimento: este app tambem responde as rotas /api/... do front, guardando historico em MEMORIA
(some ao reiniciar), para o grupo testar front + IA + Telegram antes do Java ficar pronto.
"""
from __future__ import annotations

import os
from datetime import date
from itertools import count

from flask import Flask, jsonify, request
from flask_cors import CORS

from larouaye_ia import fontes_publicas, servico, telegram_bot

UFS = {"AC", "AL", "AP", "AM", "BA", "CE", "DF", "ES", "GO", "MA", "MT", "MS", "MG", "PA", "PB", "PR", "PE", "PI", "RJ",
       "RN", "RS", "RO", "RR", "SC", "SP", "SE", "TO"}
SERVICOS_NACIONAIS = [
    ("ONR: certidões de imóveis pela internet", "REGISTRO_IMOVEIS", "Peça matrícula e certidões de qualquer cartório do país.", "https://registradores.onr.org.br"),
    ("Colégio Notarial do Brasil", "TABELIONATO", "Informações sobre escrituras e tabelionatos de notas.", "https://www.notariado.org.br"),
    ("Caixa: habitação", "FINANCIAMENTO", "Financiamento, FGTS e Minha Casa, Minha Vida.", "https://www.caixa.gov.br/voce/habitacao/"),
    ("Receita Federal", "IMPOSTO_DE_RENDA", "Imposto de renda e ganho de capital.", "https://www.gov.br/receitafederal/pt-br"),
    ("Ministério das Cidades", "HABITACAO", "Programas de moradia do governo federal.", "https://www.gov.br/cidades/pt-br"),
]


def erro(codigo: int, mensagem: str, **extra):
    return jsonify({"mensagem": mensagem, **extra}), codigo


def create_app() -> Flask:
    app = Flask(__name__)
    CORS(app, origins=[o for o in os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",") if o])
    usuarios: dict[int, dict] = {}
    historico: dict[int, list] = {}
    progresso: dict[int, dict[int, str]] = {}
    ids_usuario, ids_consulta = count(1), count(101)

    @app.errorhandler(404)
    def _404(_):
        return erro(404, "Recurso não encontrado.")

    @app.errorhandler(405)
    def _405(_):
        return erro(405, "Método não permitido.")

    @app.errorhandler(Exception)
    def _500(_e):  # nunca devolver stack trace
        return erro(500, "Erro interno. Tente de novo em instantes.")

    def corpo() -> dict:
        d = request.get_json(silent=True)
        return d if isinstance(d, dict) else {}

    # ---------- saúde e conteúdo ----------
    @app.get("/api/saude")
    def saude():
        servico.modelos()
        return jsonify({"status": "UP"})

    @app.get("/api/categorias")
    def categorias():
        return jsonify([{"id": c["id"], "nome": c["nome"]} for c in servico.base()["categorias"]])

    def _orientacao_publica(o: dict) -> dict:
        saida = {k: o[k] for k in ("id", "titulo", "categoria", "perguntaRelacionada", "conteudo", "cuidados", "baseLegal")}
        if o.get("revisado") and o.get("dataRevisao"):
            saida["dataRevisao"] = o["dataRevisao"]
        return saida

    @app.get("/api/orientacoes")
    def orientacoes():
        return jsonify([_orientacao_publica(o) for o in servico.base()["orientacoes"]])

    @app.get("/api/orientacoes/<int:oid>")
    def orientacao(oid: int):
        for o in servico.base()["orientacoes"]:
            if o["id"] == oid:
                return jsonify(_orientacao_publica(o))
        return erro(404, "Orientação não encontrada.")

    @app.get("/api/categorias/<int:cid>/orientacoes")  # rota aninhada 1:N
    def orientacoes_da_categoria(cid: int):
        cat = next((c for c in servico.base()["categorias"] if c["id"] == cid), None)
        if not cat:
            return erro(404, "Categoria não encontrada.")
        return jsonify([_orientacao_publica(o) for o in servico.base()["orientacoes"] if o["categoria"] == cat["codigo"]])

    @app.get("/api/etapas")
    def etapas():
        return jsonify(servico.base()["etapas"])

    @app.get("/api/servicos")
    def servicos():
        uf = request.args.get("uf", "").upper()
        if uf not in UFS:
            return erro(400, "Informe uma UF válida, por exemplo SP.")
        lista = [{"id": i + 1, "nome": n, "tipo": t, "descricao": d, "url": u, "uf": uf} for i, (n, t, d, u) in enumerate(SERVICOS_NACIONAIS)]
        lista.append({"id": len(lista) + 1, "nome": f"Prefeitura do município do imóvel ({uf})", "tipo": "ITBI_IPTU",
                      "descricao": "ITBI e IPTU são cobrados pela prefeitura da cidade do imóvel. Procure o site oficial dela.", "uf": uf})
        lista.append({"id": len(lista) + 1, "nome": f"Tribunal de Justiça do estado ({uf})", "tipo": "EMOLUMENTOS",
                      "descricao": "A tabela de taxas de cartório (emolumentos) é definida por cada estado.", "uf": uf})
        return jsonify(lista)

    # ---------- APIs públicas de informação ----------
    @app.get("/api/fontes/cep/<cep>")
    def fonte_cep(cep: str):
        r = fontes_publicas.consultar_cep(cep)
        return jsonify(r) if r else erro(404, "CEP não encontrado ou serviço fora do ar.")

    @app.get("/api/fontes/municipios/<uf>")
    def fonte_municipios(uf: str):
        r = fontes_publicas.listar_municipios(uf)
        return jsonify(r) if r is not None else erro(404, "UF inválida ou serviço fora do ar.")

    @app.get("/api/fontes/selic")
    def fonte_selic():
        r = fontes_publicas.meta_selic()
        return jsonify(r) if r else erro(404, "Serviço do Banco Central fora do ar.")

    # ---------- IA ----------
    def _pergunta(d: dict):
        p = d.get("pergunta")
        if not isinstance(p, str) or not (3 <= len(p.strip()) <= 500):
            return None, erro(400, "Dados inválidos.", pergunta="Escreva sua dúvida com 3 a 500 letras.")
        return p.strip(), None

    @app.post("/classificar")
    @app.post("/api/classificar")
    def classificar():
        p, e = _pergunta(corpo())
        return e or jsonify(servico.classificar(p))

    @app.post("/api/responder")
    def responder():
        d = corpo()
        p, e = _pergunta(d)
        if e:
            return e
        return jsonify(servico.responder(p, d.get("uf"), d.get("etapa"), d.get("cep"), servico.codigo_da_opcao(d.get("categoria", "") or "")))

    # ---------- backend de desenvolvimento (contrato do front) ----------
    @app.post("/api/usuarios")
    def criar_usuario():
        d = corpo()
        nome = d.get("nome")
        if not isinstance(nome, str) or len(nome.strip()) < 2:
            return erro(400, "Dados inválidos.", nome="Escreva seu nome (mínimo 2 letras).")
        uid = next(ids_usuario)
        usuarios[uid] = {"id": uid, "nome": nome.strip(), "canal": "WEB"}
        historico[uid], progresso[uid] = [], {}
        return jsonify({"id": uid, "nome": usuarios[uid]["nome"]}), 201

    def _usuario(uid: int):
        return None if uid in usuarios else erro(404, "Usuário não encontrado.")

    @app.post("/api/usuarios/<int:uid>/consultas")
    def criar_consulta(uid: int):
        if (e := _usuario(uid)):
            return e
        d = corpo()
        p, e = _pergunta(d)
        if e:
            return e
        uf = d.get("uf")
        if uf is not None and uf not in UFS:
            return erro(400, "Dados inválidos.", uf="Escolha uma UF da lista.")
        r = servico.responder(p, uf, d.get("etapa"), d.get("cep"), servico.codigo_da_opcao(d.get("categoria", "") or ""))
        r.pop("classificacao", None)
        cid = next(ids_consulta)
        historico[uid].append({"consultaId": cid, "pergunta": p, "categoria": r.get("categoria"), "dataConsulta": date.today().isoformat()})
        return jsonify({"consultaId": cid, **r}), 201

    @app.get("/api/usuarios/<int:uid>/consultas")
    def listar_consultas(uid: int):
        return _usuario(uid) or jsonify(historico[uid])

    @app.get("/api/usuarios/<int:uid>/etapas")
    def listar_progresso(uid: int):
        return _usuario(uid) or jsonify([{"etapaId": k, "status": v} for k, v in progresso[uid].items()])

    @app.post("/api/usuarios/<int:uid>/etapas")
    def salvar_progresso(uid: int):
        if (e := _usuario(uid)):
            return e
        d = corpo()
        ids = {x["id"] for x in servico.base()["etapas"]}
        if d.get("etapaId") not in ids or d.get("status") not in ("PENDENTE", "EM_ANDAMENTO", "CONCLUIDA"):
            return erro(400, "Dados inválidos.", status="Informe etapaId existente e status PENDENTE, EM_ANDAMENTO ou CONCLUIDA.")
        progresso[uid][d["etapaId"]] = d["status"]
        return jsonify({"etapaId": d["etapaId"], "status": d["status"]})

    # ---------- Telegram ----------
    @app.post("/api/telegram/webhook")
    def telegram_webhook():
        segredo = os.getenv("TELEGRAM_WEBHOOK_SECRET")
        if not segredo or request.headers.get("X-Telegram-Bot-Api-Secret-Token") != segredo:
            return erro(403, "Não autorizado.")
        token = os.getenv("TELEGRAM_BOT_TOKEN")
        for m in telegram_bot.tratar_update(corpo()):
            if token:
                telegram_bot.enviar(token, m)
        return jsonify({"ok": True})

    return app


app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "5000")), debug=False)
