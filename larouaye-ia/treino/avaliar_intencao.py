"""Mede o modelo de INTENCAO em tres conjuntos e mostra o efeito do limiar de resposta.

  python treino/avaliar_intencao.py

- intencao_teste.csv        : teste usado durante o desenvolvimento (guiou ajustes, ja NAO e independente)
- intencao_teste_cego.csv   : frases escritas DEPOIS do ajuste final e usadas uma vez para medir (mais honesto)
- intencao_validacao_real.csv: perguntas REAIS do Instagram do projeto (nunca entram no treino)
"""
import sys
import warnings
from pathlib import Path

import joblib
import pandas as pd

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))
warnings.filterwarnings("ignore")

LIMIAR_RESPONDER = 0.70
LIMIAR_ESCLARECER = 0.30


def avaliar(modelo, df: pd.DataFrame) -> dict:
    p = modelo.predict_proba(df.texto)
    y = modelo.classes_[p.argmax(1)]
    c = p.max(1)
    certo = y == df.rotulo.values
    direto = c >= LIMIAR_RESPONDER
    return {
        "n": len(df),
        "acuracia": round(float(certo.mean()), 3),
        "responde_direto": round(float(direto.mean()), 3),
        "acerto_quando_responde": round(float(certo[direto].mean()), 3) if direto.any() else None,
        "erros_com_confianca_alta": int((~certo & direto).sum()),
        "pede_esclarecimento": int(((c >= LIMIAR_ESCLARECER) & ~direto).sum()),
        "nao_reconhecidas": int((c < LIMIAR_ESCLARECER).sum()),
    }


def main(caminho_modelo: Path = RAIZ / "modelos" / "modelo_intencao.joblib") -> dict:
    modelo = joblib.load(caminho_modelo)
    conjuntos = {
        "teste_desenvolvimento": "intencao_teste.csv",
        "teste_cego": "intencao_teste_cego.csv",
        "validacao_real_instagram": "intencao_validacao_real.csv",
    }
    resultado = {nome: avaliar(modelo, pd.read_csv(RAIZ / "dados" / arq)) for nome, arq in conjuntos.items()}
    for nome, r in resultado.items():
        print(f"{nome:28} {r}")
    return resultado


if __name__ == "__main__":
    main(Path(sys.argv[1]) if len(sys.argv) > 1 else RAIZ / "modelos" / "modelo_intencao.joblib")
