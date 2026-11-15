"""Logica do chatbot: classifica (2 modelos de ML) e monta a resposta a partir do catalogo juridico.

A IA so IDENTIFICA a categoria. O texto que o cidadao le vem SEMPRE de dados/base_conhecimento.json.
Decisao pela confianca do modelo de intencao:
  >= LIMIAR_RESPONDER      -> RESPONDIDA (ou FORA_DO_ESCOPO se a categoria for essa)
  >= LIMIAR_ESCLARECER     -> ESCLARECIMENTO (pergunta qual dos 3 assuntos mais provaveis)
  <  LIMIAR_ESCLARECER     -> NAO_RECONHECIDA
"""
from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path

import joblib
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer

from . import fontes_publicas

RAIZ = Path(__file__).resolve().parent.parent
LIMIAR_RESPONDER = 0.70
LIMIAR_ESCLARECER = 0.30
AVISO_GERAL = "Isto é informação geral, não é aconselhamento para o seu caso. Para decidir, procure um advogado ou a Defensoria Pública."
AVISO_REVISAO = "Este texto ainda está em revisão jurídica."


@lru_cache(maxsize=1)
def base() -> dict:
    return json.loads((RAIZ / "dados" / "base_conhecimento.json").read_text(encoding="utf-8"))


@lru_cache(maxsize=1)
def modelos():
    return (joblib.load(RAIZ / "modelos" / "modelo_intencao.joblib"), joblib.load(RAIZ / "modelos" / "modelo_etapa.joblib"))


@lru_cache(maxsize=1)
def _indice():
    """Indice de busca entre as orientacoes da MESMA categoria (escolhe qual texto mostrar)."""
    ors = base()["orientacoes"]
    vet = TfidfVectorizer(strip_accents="unicode", lowercase=True, ngram_range=(1, 2))
    mat = vet.fit_transform([f"{o['titulo']} {o['perguntaRelacionada']} {o['conteudo']}" for o in ors])
    return vet, mat, ors


def rotulos() -> dict[str, str]:
    return {c["codigo"]: c["nome"] for c in base()["categorias"]}


def nome_etapa(codigo: str | None) -> str | None:
    for e in base()["etapas"]:
        if e["codigo"] == codigo:
            return e["nome"]
    return None


def classificar(pergunta: str) -> dict:
    """Roda os DOIS modelos. Devolve categoria, confianca, as 3 mais provaveis e a etapa sugerida."""
    m_int, m_eta = modelos()
    p = m_int.predict_proba([pergunta])[0]
    ordem = np.argsort(p)[::-1]
    pe = m_eta.predict_proba([pergunta])[0]
    ie = int(np.argmax(pe))
    return {
        "categoria": str(m_int.classes_[ordem[0]]),
        "confianca": round(float(p[ordem[0]]), 4),
        "maisProvaveis": [{"categoria": str(m_int.classes_[i]), "confianca": round(float(p[i]), 4)} for i in ordem[:3]],
        "etapaSugerida": str(m_eta.classes_[ie]),
        "confiancaEtapa": round(float(pe[ie]), 4),
    }


def escolher_orientacao(categoria: str, pergunta: str) -> dict | None:
    vet, mat, ors = _indice()
    idx = [i for i, o in enumerate(ors) if o["categoria"] == categoria]
    if not idx:
        return None
    sim = (mat[idx] @ vet.transform([pergunta]).T).toarray().ravel()
    return ors[idx[int(np.argmax(sim))]]


def _montar(orientacao: dict, categoria: str, contexto: list[str]) -> dict:
    cuidados = list(orientacao.get("cuidados", [])) + contexto
    if not orientacao.get("revisado"):
        cuidados.append(AVISO_REVISAO)
    cuidados.append(AVISO_GERAL)
    resposta = {
        "titulo": orientacao["titulo"], "conteudo": orientacao["conteudo"], "cuidados": cuidados,
        "baseLegal": orientacao.get("baseLegal", []),
        "fontes": orientacao.get("fontes", []),
        "orientacaoId": orientacao["id"],
    }
    if orientacao.get("revisado") and orientacao.get("dataRevisao"):
        resposta["dataRevisao"] = orientacao["dataRevisao"]
    return {"status": "RESPONDIDA", "categoria": categoria, "resposta": resposta,
            "proximaEtapa": nome_etapa(orientacao.get("proximaEtapa"))}


def _contexto_local(categoria: str, cep: str | None, fontes=fontes_publicas) -> list[str]:
    """Enriquecimento com APIs publicas (CEP -> cidade; Selic). Falha silenciosa."""
    saida = []
    if cep:
        local = fontes.consultar_cep(cep)
        if local and categoria == "IMPOSTOS_TAXAS":
            saida.append(f"Seu CEP é de {local['cidade']}/{local['uf']}: confira o valor e as isenções do ITBI no site da Prefeitura de {local['cidade']}.")
        elif local and categoria in ("ESCRITURA_REGISTRO", "MATRICULA_ONUS"):
            saida.append(f"Procure o cartório da região de {local['cidade']}/{local['uf']} (o Registro de Imóveis é o da cidade onde o imóvel fica).")
    if categoria == "FINANCIAMENTO":
        selic = fontes.meta_selic()
        if selic:
            saida.append(f"Referência: a meta da Selic em {selic['data']} era {selic['valor']:.2f}% ao ano (Banco Central). Ela influencia os juros, mas cada banco define os seus.")
    return saida


def responder(pergunta: str, uf: str | None = None, etapa: str | None = None, cep: str | None = None,
              categoria_escolhida: str | None = None, fontes=fontes_publicas) -> dict:
    """Devolve o contrato ConsultaResposta (sem consultaId, que quem guarda o historico define)."""
    c = classificar(pergunta)
    cats = rotulos()
    base_resp = {"classificacao": c}
    if categoria_escolhida:
        if categoria_escolhida not in cats:
            return {**base_resp, "status": "NAO_RECONHECIDA"}
        o = escolher_orientacao(categoria_escolhida, pergunta)
        return {**base_resp, **_montar(o, categoria_escolhida, _contexto_local(categoria_escolhida, cep, fontes))}
    if c["categoria"] == "FORA_DO_ESCOPO" and c["confianca"] >= LIMIAR_ESCLARECER:
        return {**base_resp, "status": "FORA_DO_ESCOPO", "categoria": "FORA_DO_ESCOPO",
                "resposta": {"titulo": "Esse assunto não é comigo", "conteudo": base()["fora_do_escopo"], "cuidados": []}}
    if c["confianca"] >= LIMIAR_RESPONDER:
        o = escolher_orientacao(c["categoria"], pergunta)
        if o:
            return {**base_resp, **_montar(o, c["categoria"], _contexto_local(c["categoria"], cep, fontes))}
    if c["confianca"] >= LIMIAR_ESCLARECER:
        cand = [x["categoria"] for x in c["maisProvaveis"] if x["categoria"] in cats][:3]
        return {**base_resp, "status": "ESCLARECIMENTO", "opcoes": [cats[x] for x in cand], "opcoesCodigos": cand}
    return {**base_resp, "status": "NAO_RECONHECIDA"}


def codigo_da_opcao(rotulo_ou_codigo: str) -> str | None:
    cats = rotulos()
    if rotulo_ou_codigo in cats:
        return rotulo_ou_codigo
    for k, v in cats.items():
        if v == rotulo_ou_codigo:
            return k
    return None
