# LarOuAyê: IA, API Flask e bot do Telegram

> "A IA identifica. O Java decide. O conteúdo jurídico fundamenta."

| Parte | O que é | Cards |
|---|---|---|
| `treino/` + `dados/` | dataset, base jurídica e geradores | A01, A03 |
| `notebooks/` | 2 notebooks executados (EDA, treino, métricas, exportação) | A01 a A03 |
| `modelos/` | `modelo_intencao.joblib`, `modelo_etapa.joblib`, `metricas.json` | A02 |
| `app.py` | API Flask: `/classificar` e backend de DESENVOLVIMENTO no contrato do front | A04 |
| `larouaye_ia/telegram_bot.py` | bot do Telegram (webhook ou polling) | extra |
| `tests/` | 30 testes (pytest) | |

## Rodar (5 comandos)
```bash
python -m venv .venv && source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt pytest
python -m pytest -q                                      # 30 testes
python app.py                                            # API em http://localhost:5000
```
Front junto: no projeto React, crie `.env` com `VITE_PROXY_TARGET=http://localhost:5000` e rode `npm run dev`.
O front fala com `/api/...`, o Vite repassa para o Flask. **Nenhuma linha do front muda.**

## Os 2 modelos (disciplina de Chatbot)
| | Modelo 1: intenção | Modelo 2: etapa da compra |
|---|---|---|
| Pergunta que responde | Qual assunto jurídico? (9 + fora do escopo) | Em que etapa a pessoa está? (6 etapas do front) |
| Algoritmo | TF-IDF de caracteres + Regressão Logística | TF-IDF de palavras + Naive Bayes |
| Dados | `dados/intencao_*.csv` | `dados/etapa_*.csv` |
| Métricas | `modelos/metricas.json` e notebook 01 | `modelos/metricas.json` e notebook 02 |

Retreinar: `python treino/gerar_dataset.py && python -m larouaye_ia.nucleo` (e reexecutar os notebooks:
`cd notebooks && jupyter nbconvert --to notebook --execute --inplace *.ipynb`).

**Decisão pela confiança** (`larouaye_ia/servico.py`): `>= 0,70` responde; `0,30 a 0,70` pergunta qual dos 3 assuntos mais prováveis
(`ESCLARECIMENTO`); `< 0,30` diz que não entendeu. Assunto fora do tema recebe aviso, sem texto jurídico.

## Fontes de informação
- **Leis e orientações**: `dados/base_conhecimento.json` (gerado por `treino/gerar_base.py`), com links do Planalto. É o **único** lugar de onde sai texto jurídico.
- **APIs públicas** (`larouaye_ia/fontes_publicas.py`, sem chave, com cache e falha silenciosa): ViaCEP (CEP → cidade/UF), IBGE (municípios) e Banco Central (meta da Selic).
  Se a pessoa informar `cep`, a resposta de impostos cita a prefeitura da cidade dela. Rotas: `/api/fontes/cep/<cep>`, `/api/fontes/municipios/<uf>`, `/api/fontes/selic`.

## Telegram
1. No Telegram, fale com **@BotFather**, `/newbot`, e guarde o **token**.
2. Copie `.env.example` para `.env` e preencha `TELEGRAM_BOT_TOKEN` (nunca comite o `.env`).
3. **Desenvolvimento (sem URL pública):** `python -m larouaye_ia.telegram_bot` (polling).
4. **Produção (Render):** defina `TELEGRAM_BOT_TOKEN` e `TELEGRAM_WEBHOOK_SECRET` e registre:
   `https://api.telegram.org/bot<TOKEN>/setWebhook?url=https://SEU-APP.onrender.com/api/telegram/webhook&secret_token=<SEGREDO>`
5. Comandos: `/start`, `/ajuda`, `/etapas`, `/fontes`. Dúvida solta vira resposta com cuidados e base legal; se houver dúvida de assunto, aparecem **botões**.
6. Áudio: mensagem de **voz recebida** pede texto (sem transcrição). **Resposta em áudio** opcional: `pip install gTTS` e `TELEGRAM_VOZ=1`.

## Integração com o Java (produção)
O Java é o ponto central. Ele chama `POST /classificar` `{"pergunta": "..."}` e recebe `categoria`, `confianca`, `maisProvaveis`, `etapaSugerida`, `confiancaEtapa`.
Quem decide e busca o texto no Oracle é o Java. As rotas `/api/usuarios/...` deste app guardam dados **em memória** e são só para testar sem o Java.
Categorias retornadas: `MATRICULA_ONUS, ESCRITURA_REGISTRO, CONTRATO, FINANCIAMENTO, FGTS_SUBSIDIOS, IMPOSTOS_TAXAS, LEILAO, IMOVEL_USADO, FRAUDE_GOLPES, FORA_DO_ESCOPO`
(a tabela `tb_categoria` do Oracle deve usar esses códigos).

## Deploy no Render
Web Service Python, build `pip install -r requirements.txt`, start `gunicorn app:app`. Variáveis: `CORS_ORIGINS` (URL da Vercel), `TELEGRAM_*`.
Os `.joblib` vão no repositório (são pequenos); retreine na mesma versão do scikit-learn do `requirements.txt`.

## Limites honestos (colocar no relatório)
1. **Dados sintéticos**: poucas frases escritas pelo grupo, sem usuários reais. Acurácia = estimativa otimista.
2. **Conteúdo jurídico NÃO revisado por advogado**: cada orientação tem `revisado: false` e a resposta avisa isso. Jonatan revisa e troca para `true` + `dataRevisao`.
3. **Links do Planalto e dos sites oficiais não foram abertos um a um**: conferir antes de entregar.
4. Os serviços e as APIs públicas dependem de internet; sem rede o chatbot continua respondendo (só sem o enriquecimento).
5. Confiança alta do modelo **não** prova que a resposta jurídica está certa.
