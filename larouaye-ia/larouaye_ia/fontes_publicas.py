"""Clientes das APIs PUBLICAS de informacao (sem chave, sem cadastro).

- ViaCEP     : CEP -> cidade/UF/IBGE         https://viacep.com.br
- IBGE       : municipios de uma UF           https://servicodados.ibge.gov.br
- Banco Central (SGS): meta da Selic (serie 432) https://api.bcb.gov.br

Regras: timeout curto, cache em memoria, e QUALQUER falha devolve None. O chatbot nunca fica fora do ar por
causa de uma API externa. As leis em si ficam em dados/base_conhecimento.json (revisadas por advogado).
"""
from __future__ import annotations

import re
import time

import requests

TIMEOUT = 4
TTL = 3600
_cache: dict[str, tuple[float, object]] = {}


def _get_json(url: str, sessao=requests):
    agora = time.time()
    if url in _cache and agora - _cache[url][0] < TTL:
        return _cache[url][1]
    try:
        r = sessao.get(url, timeout=TIMEOUT, headers={"Accept": "application/json", "User-Agent": "larouaye-ia/1.0"})
        r.raise_for_status()
        dados = r.json()
    except Exception:  # rede, timeout, JSON invalido: nunca derrubar a resposta
        return None
    _cache[url] = (agora, dados)
    return dados


def limpar_cache() -> None:
    _cache.clear()


def normalizar_cep(cep: str) -> str | None:
    digitos = re.sub(r"\D", "", cep or "")
    return digitos if len(digitos) == 8 else None


def consultar_cep(cep: str, sessao=requests) -> dict | None:
    """Devolve {cep, cidade, uf, ibge} ou None (CEP invalido, nao encontrado ou API fora do ar)."""
    c = normalizar_cep(cep)
    if not c:
        return None
    d = _get_json(f"https://viacep.com.br/ws/{c}/json/", sessao)
    if not isinstance(d, dict) or d.get("erro"):
        return None
    return {"cep": c, "cidade": d.get("localidade"), "uf": d.get("uf"), "ibge": d.get("ibge")}


def listar_municipios(uf: str, sessao=requests) -> list[str] | None:
    if not re.fullmatch(r"[A-Za-z]{2}", uf or ""):
        return None
    d = _get_json(f"https://servicodados.ibge.gov.br/api/v1/localidades/estados/{uf.upper()}/municipios", sessao)
    if not isinstance(d, list):
        return None
    return sorted(m["nome"] for m in d if isinstance(m, dict) and "nome" in m)


def meta_selic(sessao=requests) -> dict | None:
    """Ultima meta da Selic (% a.a.). Serve de contexto para explicar juros de financiamento."""
    d = _get_json("https://api.bcb.gov.br/dados/serie/bcdata.sgs.432/dados/ultimos/1?formato=json", sessao)
    if not isinstance(d, list) or not d:
        return None
    try:
        return {"data": d[-1]["data"], "valor": float(str(d[-1]["valor"]).replace(",", "."))}
    except (KeyError, ValueError):
        return None
