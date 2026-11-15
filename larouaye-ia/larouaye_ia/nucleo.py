"""Treino e avaliacao dos DOIS modelos de Machine Learning (disciplina de Chatbot).

Modelo 1 - INTENCAO : em qual assunto juridico cai a pergunta (TF-IDF de caracteres + Regressao Logistica).
Modelo 2 - ETAPA    : em qual etapa da compra a pessoa esta (TF-IDF de palavras + Naive Bayes).
Sao dois conjuntos de dados, dois rotulos e dois algoritmos diferentes.

Regra do projeto: a IA IDENTIFICA, o Java DECIDE, o conteudo juridico FUNDAMENTA.
"""
from __future__ import annotations

import json
from datetime import date
from pathlib import Path

import joblib
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report, f1_score
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline

RAIZ = Path(__file__).resolve().parent.parent
DADOS = RAIZ / "dados"
MODELOS = RAIZ / "modelos"


def carregar(nome: str) -> tuple[pd.DataFrame, pd.DataFrame]:
    treino = pd.read_csv(DADOS / f"{nome}_treino.csv")
    teste = pd.read_csv(DADOS / f"{nome}_teste.csv")
    return treino, teste


def pipeline_intencao() -> Pipeline:
    return Pipeline([
        ("tfidf", TfidfVectorizer(analyzer="char_wb", ngram_range=(2, 5), strip_accents="unicode", lowercase=True, sublinear_tf=True)),
        ("clf", LogisticRegression(C=20, max_iter=3000)),
    ])


def pipeline_etapa() -> Pipeline:
    return Pipeline([
        ("tfidf", TfidfVectorizer(analyzer="word", ngram_range=(1, 2), strip_accents="unicode", lowercase=True)),
        ("clf", MultinomialNB(alpha=0.3)),
    ])


def treinar_e_avaliar(nome: str, pipe: Pipeline) -> dict:
    """Treina no CSV de treino e mede no CSV de TESTE (frases escritas a parte, sem aumento de dados)."""
    treino, teste = carregar(nome)
    pipe.fit(treino["texto"], treino["rotulo"])
    previsto = pipe.predict(teste["texto"])
    rel = classification_report(teste["rotulo"], previsto, output_dict=True, zero_division=0)
    return {
        "modelo": nome,
        "amostras_treino": int(len(treino)),
        "amostras_teste": int(len(teste)),
        "acuracia_teste": round(float(accuracy_score(teste["rotulo"], previsto)), 4),
        "f1_macro_teste": round(float(f1_score(teste["rotulo"], previsto, average="macro")), 4),
        "por_classe": {k: {m: round(v, 3) for m, v in d.items() if m != "support"} for k, d in rel.items() if k in pipe.classes_},
        "classes": list(pipe.classes_),
        "treinado_em": date.today().isoformat(),
    }


def exportar(pipe: Pipeline, nome: str) -> Path:
    MODELOS.mkdir(exist_ok=True)
    caminho = MODELOS / f"modelo_{nome}.joblib"
    joblib.dump(pipe, caminho)
    return caminho


def treinar_tudo() -> dict:
    metricas = {}
    for nome, fabrica in (("intencao", pipeline_intencao), ("etapa", pipeline_etapa)):
        pipe = fabrica()
        metricas[nome] = treinar_e_avaliar(nome, pipe)
        exportar(pipe, nome)
    (MODELOS / "metricas.json").write_text(json.dumps(metricas, ensure_ascii=False, indent=2), encoding="utf-8")
    return metricas


if __name__ == "__main__":
    for k, v in treinar_tudo().items():
        print(k, "acuracia:", v["acuracia_teste"], "f1_macro:", v["f1_macro_teste"])
