"""Gera os 2 notebooks (nbformat). Execute depois: jupyter nbconvert --to notebook --execute --inplace notebooks/*.ipynb"""
from pathlib import Path

import nbformat as nbf

SAIDA = Path(__file__).resolve().parent.parent / "notebooks"
M, C = nbf.v4.new_markdown_cell, nbf.v4.new_code_cell

PREPARO = """import sys
from pathlib import Path
sys.path.insert(0, str(Path.cwd().parent))   # permite importar larouaye_ia
import warnings; warnings.filterwarnings('ignore')
import pandas as pd, numpy as np
import matplotlib.pyplot as plt
from larouaye_ia import nucleo
pd.set_option('display.max_colwidth', 90)"""

AVISO_DADOS = """> **Origem e limites dos dados (registrar no relatório).** As frases foram **escritas pelo grupo/assistente** como amostras sintéticas
> de perguntas reais sobre compra do primeiro imóvel. **Não houve coleta de usuários.** O conjunto de **teste** foi escrito à parte,
> com redação diferente, e **nunca recebe aumento de dados**. Por serem poucas frases, a acurácia é uma **estimativa otimista**:
> perguntas reais de cidadãos terão mais variação, erros de digitação e gírias."""


def nb(celulas, nome):
    n = nbf.v4.new_notebook(cells=celulas)
    n.metadata["kernelspec"] = {"display_name": "Python 3", "language": "python", "name": "python3"}
    nbf.write(n, SAIDA / nome)


def intencao():
    nb([
        M("# Modelo 1: Intenção da pergunta (LarOuAyê)\n**Disciplina:** Artificial Intelligence & Chatbot\n\n**Objetivo:** dizer em qual assunto jurídico cai a dúvida do cidadão "
          "(matrícula, escritura, contrato, financiamento, FGTS, impostos, leilão, imóvel usado, fraude) ou se está **fora do escopo**.\n\n"
          "**Regra do projeto:** *a IA identifica, o Java decide, o conteúdo jurídico fundamenta.* Este modelo **nunca escreve a resposta**."),
        M(AVISO_DADOS), C(PREPARO),
        M("## 1. Análise exploratória"),
        C("treino, teste = nucleo.carregar('intencao')\nprint('treino:', treino.shape, '| teste:', teste.shape)\ntreino.sample(6, random_state=1)"),
        C("contagem = treino.rotulo.value_counts()\ncontagem.sort_values().plot(kind='barh', figsize=(7,4), color='#102b35')\nplt.title('Amostras de treino por categoria'); plt.tight_layout(); plt.show()\ncontagem"),
        C("print('Tamanho médio da pergunta (letras):', round(treino.texto.str.len().mean(), 1))\nprint('Categorias:', treino.rotulo.nunique())\nprint('Nulos:', int(treino.isna().sum().sum()), '| duplicadas:', int(treino.texto.duplicated().sum()))"),
        M("## 2. Pré-processamento e modelo\n- **TF-IDF de caracteres (2 a 5)**: aguenta erro de digitação e variações (ex.: *imovel* / *imóvel*), e `strip_accents` ignora acentos.\n"
          "- **Regressão Logística**: dá **probabilidade** por categoria, que usamos como confiança."),
        C("pipe = nucleo.pipeline_intencao()\npipe"),
        C("res = nucleo.treinar_e_avaliar('intencao', pipe)\nprint('Acurácia no TESTE :', res['acuracia_teste'])\nprint('F1 macro no TESTE:', res['f1_macro_teste'])"),
        M("## 3. Avaliação detalhada"),
        C("from sklearn.metrics import classification_report, ConfusionMatrixDisplay\nprevisto = pipe.predict(teste.texto)\nprint(classification_report(teste.rotulo, previsto, zero_division=0))"),
        C("fig, ax = plt.subplots(figsize=(8,7))\nConfusionMatrixDisplay.from_predictions(teste.rotulo, previsto, xticks_rotation=75, cmap='Blues', ax=ax, colorbar=False)\nplt.tight_layout(); plt.show()"),
        C("erros = teste.assign(previsto=previsto, confianca=pipe.predict_proba(teste.texto).max(axis=1).round(2))\nerros[erros.rotulo != erros.previsto]"),
        M("## 4. Limiares de confiança (regra de decisão)\nO modelo só **responde** com confiança alta. Entre os limiares, o sistema **pergunta** qual assunto a pessoa quer. Abaixo, diz que **não entendeu**."),
        C("from larouaye_ia import servico\nprob = pipe.predict_proba(teste.texto); conf = prob.max(axis=1); acertou = (pipe.classes_[prob.argmax(axis=1)] == teste.rotulo.values)\n"
          "print(f'Limiar de resposta direta: {servico.LIMIAR_RESPONDER} | de esclarecimento: {servico.LIMIAR_ESCLARECER}')\n"
          "resp = conf >= servico.LIMIAR_RESPONDER\n"
          "print('Respondidas direto:', int(resp.sum()), 'de', len(conf))\n"
          "print('Acertos entre as respondidas direto:', round(float(acertou[resp].mean()), 3))\n"
          "print('Erros que ficaram abaixo do limiar (seguros):', int((~acertou & ~resp).sum()), 'de', int((~acertou).sum()))"),
        M("## 5. Teste cego e perguntas reais do Instagram\n"
          "O teste de desenvolvimento (seção 2) **guiou ajustes** do treino, então já não é independente (por isso chega perto de 100%). "
          "Os dois conjuntos abaixo são as medidas mais honestas:\n"
          "- **Teste cego**: 55 frases escritas **depois** do ajuste final e usadas para medir.\n"
          "- **Validação real**: 11 perguntas **reais** de pessoas do Instagram do projeto, que **nunca entram no treino**. "
          "Atenção: o autor das frases de treino já conhecia essas perguntas, então o resultado é otimista."),
        C("import sys; sys.path.insert(0, str(Path.cwd().parent / 'treino'))\nfrom treino import avaliar_intencao\nresultado = avaliar_intencao.main(nucleo.MODELOS / 'modelo_intencao.joblib')\npd.DataFrame(resultado).T"),
        C("cego = pd.read_csv(nucleo.DADOS / 'intencao_teste_cego.csv')\nprev = pipe.predict(cego.texto); conf_c = pipe.predict_proba(cego.texto).max(axis=1).round(2)\n"
          "cego.assign(previsto=prev, confianca=conf_c)[prev != cego.rotulo.values]"),
        M("## 6. Exemplos reais (incluindo o caso de fraude do corretor)"),
        C("exemplos = ['O corretor alterou meu IRRF e colocou minha esposa como dependente', 'Como sei se o imóvel tem escritura?', 'Posso usar FGTS na entrada?', 'Quero comprar um tênis', 'oi']\n"
          "linhas = []\nfor q in exemplos:\n    p = pipe.predict_proba([q])[0]; i = p.argmax(); linhas.append((q, pipe.classes_[i], round(float(p[i]), 2)))\n"
          "pd.DataFrame(linhas, columns=['pergunta','categoria','confianca'])"),
        M("## 7. Exportação\nO modelo é salvo em `.joblib` e carregado pela API Flask (`app.py`)."),
        C("caminho = nucleo.exportar(pipe, 'intencao'); print('salvo em', caminho.name, '|', round(caminho.stat().st_size/1024), 'KB')"),
        M("## 7. Limitações e riscos\n- Poucas frases sintéticas: reavaliar com perguntas reais antes de usar fora da apresentação.\n"
          "- Confiança alta **não** significa resposta jurídica correta: o texto vem do catálogo revisado.\n"
          "- O assunto *fora do escopo* é uma categoria treinada, mas assuntos muito diferentes podem escapar: o limiar protege.\n"
          "- Não há dados pessoais no conjunto de treino."),
    ], "01_modelo_intencao.ipynb")


def etapa():
    nb([
        M("# Modelo 2: Etapa da compra em que a pessoa está (LarOuAyê)\n**Disciplina:** Artificial Intelligence & Chatbot\n\n**Objetivo:** a partir do texto da dúvida, sugerir a **etapa da jornada** "
          "(pesquisa, análise documental, negociação e contrato, escritura, ITBI e tributos, registro). Serve para **encaminhar** a pessoa e sugerir o próximo passo.\n\n"
          "É um modelo **diferente** do 1: outro conjunto de dados, outros rótulos e outro algoritmo (Naive Bayes)."),
        M(AVISO_DADOS), C(PREPARO),
        M("## 1. Análise exploratória"),
        C("treino, teste = nucleo.carregar('etapa')\nprint('treino:', treino.shape, '| teste:', teste.shape)\ntreino.sample(6, random_state=1)"),
        C("contagem = treino.rotulo.value_counts()\ncontagem.sort_values().plot(kind='barh', figsize=(7,3.5), color='#d8b875')\nplt.title('Amostras de treino por etapa'); plt.tight_layout(); plt.show()\ncontagem"),
        M("## 2. Modelo\n- **TF-IDF de palavras (1 e 2 gramas)** sem acentos.\n- **Naive Bayes multinomial**: simples, rápido e bom para poucos dados."),
        C("pipe = nucleo.pipeline_etapa()\nres = nucleo.treinar_e_avaliar('etapa', pipe)\nprint('Acurácia no TESTE :', res['acuracia_teste'])\nprint('F1 macro no TESTE:', res['f1_macro_teste'])"),
        M("## 3. Avaliação"),
        C("from sklearn.metrics import classification_report, ConfusionMatrixDisplay\nprevisto = pipe.predict(teste.texto)\nprint(classification_report(teste.rotulo, previsto, zero_division=0))"),
        C("fig, ax = plt.subplots(figsize=(7,6))\nConfusionMatrixDisplay.from_predictions(teste.rotulo, previsto, xticks_rotation=60, cmap='Oranges', ax=ax, colorbar=False)\nplt.tight_layout(); plt.show()"),
        C("teste.assign(previsto=previsto)[teste.rotulo != previsto]"),
        M("## 4. Exemplos"),
        C("for q in ['Já escolhi o apartamento e vou pedir a matrícula', 'Recebi o contrato do corretor', 'Como pago o ITBI?', 'O cartório devolveu o registro']:\n    p = pipe.predict_proba([q])[0]; print(f'{q!r:55} -> {pipe.classes_[p.argmax()]} ({p.max():.2f})')"),
        M("## 5. Exportação"),
        C("caminho = nucleo.exportar(pipe, 'etapa'); print('salvo em', caminho.name)"),
        M("## 6. Limitações\n- Amostras sintéticas e poucas: a pessoa pode estar em duas etapas ao mesmo tempo.\n- A etapa sugerida **não substitui** a etapa escolhida pelo cidadão: o front envia a etapa que ele marcou.\n"
          "- Perguntas curtas e ambíguas (ex.: *quanto custa?*) tendem a errar a etapa."),
    ], "02_modelo_etapa.ipynb")


if __name__ == "__main__":
    SAIDA.mkdir(exist_ok=True)
    intencao()
    etapa()
    print("notebooks gerados")
