"""Bot do Telegram. Usa a API HTTP do Telegram direto (requests), sem biblioteca extra.

Dois modos:
  - webhook : o Flask recebe POST /api/telegram/webhook (producao). O Java pode receber o webhook e chamar /api/responder.
  - polling : python -m larouaye_ia.telegram_bot  (desenvolvimento, sem URL publica)

O Telegram nao entrega audio como texto: mensagem de VOZ recebida pede ao cidadao para escrever.
A resposta em AUDIO e opcional (TELEGRAM_VOZ=1, precisa do pacote gTTS e de internet).
"""
from __future__ import annotations

import html
import io
import os
import time

import requests

from . import servico

AJUDA = ("Oi! Eu sou o LarOuAyê, a casinha que explica a compra do primeiro imóvel sem juridiquês.\n\n"
         "Escreva sua dúvida, por exemplo: Como sei se o imóvel tem dívidas?\n\n"
         "Comandos: /etapas (passo a passo), /fontes (sites oficiais), /ajuda")
LIMITE = 4000


def formatar_resposta(resp: dict) -> str:
    """Resposta -> texto HTML do Telegram (tudo escapado)."""
    e = html.escape
    if resp["status"] == "NAO_RECONHECIDA":
        return "Não entendi sua pergunta. Tente falar do imóvel: documentos, contrato, financiamento, FGTS, impostos, leilão ou golpes."
    if resp["status"] == "ESCLARECIMENTO":
        return "Não tenho certeza do assunto. Qual destes é o mais perto da sua dúvida?"
    r = resp["resposta"]
    partes = [f"<b>{e(r['titulo'])}</b>", e(r["conteudo"])]
    if r.get("cuidados"):
        partes.append("<b>Cuidados</b>\n" + "\n".join(f"• {e(c)}" for c in r["cuidados"]))
    if r.get("baseLegal"):
        linhas = []
        for b in r["baseLegal"]:
            nome = e(b["norma"] + (f" ({b['referencia']})" if b.get("referencia") else ""))
            linhas.append(f'• <a href="{e(b["url"], quote=True)}">{nome}</a>' if b.get("url") else f"• {nome}")
        partes.append("<b>Base legal</b>\n" + "\n".join(linhas))
    if resp.get("proximaEtapa"):
        partes.append(f"<b>Próxima etapa:</b> {e(resp['proximaEtapa'])}")
    return "\n\n".join(partes)[:LIMITE]


def texto_etapas() -> str:
    linhas = [f"{x['ordem']}. {x['nome']}: {x['descricao']}" for x in servico.base()["etapas"]]
    return "<b>Passo a passo da compra</b>\n" + "\n".join(html.escape(l) for l in linhas)


def texto_fontes() -> str:
    vistos, linhas = set(), []
    for o in servico.base()["orientacoes"]:
        for f in o.get("fontes", []):
            if f["url"] not in vistos:
                vistos.add(f["url"])
                linhas.append(f'• <a href="{html.escape(f["url"], quote=True)}">{html.escape(f["titulo"])}</a>')
    return "<b>Sites oficiais</b>\n" + "\n".join(linhas)


def _teclado(resp: dict) -> list[list[dict]] | None:
    if resp.get("status") != "ESCLARECIMENTO":
        return None
    return [[{"text": r, "callback_data": f"cat:{c}"}] for r, c in zip(resp["opcoes"], resp["opcoesCodigos"])]


def tratar_update(update: dict, responder=servico.responder) -> list[dict]:
    """Funcao pura: Update do Telegram -> lista de mensagens a enviar {chat_id, texto, teclado, callback_id}."""
    cb = update.get("callback_query")
    if cb:
        chat = cb["message"]["chat"]["id"]
        cod = servico.codigo_da_opcao(cb.get("data", "").removeprefix("cat:"))
        if not cod:
            return [{"chat_id": chat, "texto": "Essa opção não existe mais. Escreva sua dúvida de novo, por favor.", "callback_id": cb["id"]}]
        resp = responder(servico.rotulos()[cod], categoria_escolhida=cod)
        return [{"chat_id": chat, "texto": formatar_resposta(resp), "callback_id": cb["id"]}]
    msg = update.get("message") or {}
    chat = (msg.get("chat") or {}).get("id")
    if chat is None:
        return []
    if "voice" in msg or "audio" in msg:
        return [{"chat_id": chat, "texto": "Ainda não consigo entender áudio. Escreva sua dúvida, por favor."}]
    texto = (msg.get("text") or "").strip()
    if not texto:
        return [{"chat_id": chat, "texto": "Escreva sua dúvida em texto, por favor."}]
    cmd = texto.split()[0].split("@")[0].lower()
    if cmd in ("/start", "/ajuda"):
        return [{"chat_id": chat, "texto": html.escape(AJUDA)}]
    if cmd == "/etapas":
        return [{"chat_id": chat, "texto": texto_etapas()}]
    if cmd == "/fontes":
        return [{"chat_id": chat, "texto": texto_fontes()}]
    if len(texto) > 500:
        return [{"chat_id": chat, "texto": "Sua mensagem ficou grande. Resuma em até 500 letras, por favor."}]
    resp = responder(texto)
    return [{"chat_id": chat, "texto": formatar_resposta(resp), "teclado": _teclado(resp)}]


def sintetizar_voz(texto: str) -> bytes | None:
    """Audio MP3 opcional (gTTS usa a internet). Sem o pacote ou sem rede, devolve None."""
    if os.getenv("TELEGRAM_VOZ") != "1":
        return None
    try:
        from gtts import gTTS  # type: ignore
        buf = io.BytesIO()
        gTTS(html.unescape(_sem_tags(texto))[:900], lang="pt", tld="com.br").write_to_fp(buf)
        return buf.getvalue()
    except Exception:
        return None


def _sem_tags(texto: str) -> str:
    import re
    return re.sub(r"<[^>]+>", "", texto)


def enviar(token: str, m: dict, sessao=requests) -> None:
    url = f"https://api.telegram.org/bot{token}"
    corpo = {"chat_id": m["chat_id"], "text": m["texto"], "parse_mode": "HTML", "disable_web_page_preview": True}
    if m.get("teclado"):
        corpo["reply_markup"] = {"inline_keyboard": m["teclado"]}
    sessao.post(f"{url}/sendMessage", json=corpo, timeout=10)
    if m.get("callback_id"):
        sessao.post(f"{url}/answerCallbackQuery", json={"callback_query_id": m["callback_id"]}, timeout=10)
    audio = sintetizar_voz(m["texto"]) if not m.get("teclado") else None
    if audio:
        sessao.post(f"{url}/sendAudio", data={"chat_id": m["chat_id"], "title": "LarOuAyê"}, files={"audio": ("resposta.mp3", audio)}, timeout=30)


def rodar_polling(token: str) -> None:
    offset = 0
    print("Bot no ar (polling). Ctrl+C para parar.")
    while True:
        try:
            r = requests.get(f"https://api.telegram.org/bot{token}/getUpdates", params={"timeout": 25, "offset": offset}, timeout=35)
            for u in r.json().get("result", []):
                offset = u["update_id"] + 1
                for m in tratar_update(u):
                    enviar(token, m)
        except requests.RequestException:
            time.sleep(3)


if __name__ == "__main__":
    t = os.getenv("TELEGRAM_BOT_TOKEN")
    if not t:
        raise SystemExit("Defina TELEGRAM_BOT_TOKEN (veja .env.example).")
    rodar_polling(t)
