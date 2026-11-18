# LarOuAyê — Back-End (API Java, IA, Banco Oracle e Python)

> **A IA identifica. O Java decide. O conteúdo jurídico fundamenta.**

Global Solution FIAP 2026/2 (CitizenTech). Back-End do **LarOuAyê**, assistente gratuito e acessível que orienta, em linguagem simples,
quem vai comprar o primeiro imóvel. O Front-End está em outro repositório (veja a seção 4).

> **Avaliador(a): antes de testar, acorde as APIs (1 minuto).** Elas rodam no plano gratuito do Render, que “dorme” sem uso. Veja a seção 2.

## 1. O que há em cada pasta
| Pasta | Disciplina | O que é |
|---|---|---|
| `larouaye-java/` | Domain Driven Design Using Java | API REST (Spring Boot, JDBC puro, Oracle). É o ponto central: o React fala só com ela. |
| `larouaye-ia/` | Artificial Intelligence & Chatbot | API Flask com 2 modelos de Machine Learning (intenção da pergunta e etapa da compra) e notebooks. |
| `larouaye-banco/` | Building Relational Database | Scripts Oracle: modelo, dados de exemplo, DML, 10 consultas e verificação. |
| `larouaye-python/` | Computational Thinking Using Python | Orientador de aquisição por terminal, independente do resto. |

Cada pasta tem o seu próprio `README.md` com instruções para rodar.

## 2. Antes de testar: acorde as APIs (plano gratuito do Render)
Depois de ~15 minutos sem acesso, os dois serviços **dormem**, e o primeiro acesso pode levar **cerca de 1 minuto** para acordar. Nesse tempo o site pode mostrar erro de carregamento ou, na primeira pergunta, a mensagem “Ainda não tenho uma orientação segura”. **Não é falha do sistema**: o serviço de IA ainda estava acordando, e o Java usa um classificador reserva por palavras-chave enquanto isso.

Para testar sem espera:
1. Abra **as duas** páginas abaixo e aguarde cada uma responder (a primeira pode demorar):
   - API Java (Render, Docker): https://larouaye-api.onrender.com/api/saude (deve mostrar `"banco":"OK"`)
   - Serviço de IA (Render, Python 3): https://larouaye-ia.onrender.com/api/saude
2. Espere cerca de 1 minuto e abra o site: https://larouaye.vercel.app
3. Se a primeira pergunta ao Assistente ainda voltar “Ainda não tenho uma orientação segura”, repita a pergunta: a IA já estará acordada.

## 3. Como as partes conversam
```
React (Vercel) ──fetch──► API Java (Render) ──JDBC──► Oracle
                              │
                              └──HTTP──► IA Flask (Render): POST /classificar
```
- O Java recebe a pergunta, valida, pede à IA a **categoria** e a **confiança**, e **decide**: confiança ≥ 0,70 responde direto; entre 0,30 e 0,70 pede esclarecimento; abaixo de 0,30 diz que não entendeu.
- O texto jurídico **sempre** vem do catálogo cadastrado no Oracle (com fonte e base legal), nunca da IA.
- Se a IA estiver fora do ar ou demorar, o Java usa um classificador reserva e a API continua respondendo.
- Variáveis do Java: `CLASSIFICADOR_URL` (endereço da IA) e `CLASSIFICADOR_TIMEOUT_MS` (tempo de espera; padrão 3000).

## 4. Links
- Back-End (este repositório, PÚBLICO): https://github.com/tecnando-rpa/larouaye-backend
- Front-End (PÚBLICO): https://github.com/tecnando-rpa/larouaye
- Aplicação (Vercel): https://larouaye.vercel.app
- API Java (Render, Docker): https://larouaye-api.onrender.com
- Serviço de IA (Render, Python 3): https://larouaye-ia.onrender.com
- Vídeo (YouTube, até 3 min): https://www.youtube.com/watch?v=Q6L50fCgGd0

## 5. Integrantes
| Integrante | RM |
|---|---|
| Davi Felix Cunha | 569393 |
| Fernando Oliveira Francelino Sardinha | 570196 |
| Jonatan Vieira Feitosa | 570452 |
| Marcelo Candido da Mata Junior | 569584 |
| Vinicius Liberato dos Anjos | 571480 |

## 6. Limites
O LarOuAyê dá **informação geral** e não substitui advogado, cartório ou Defensoria Pública. Não promete aprovação de crédito nem segurança jurídica absoluta.
As orientações do catálogo estão com revisão **pendente** até a conferência individual pelo responsável. Os conjuntos de treino e de teste da IA foram escritos pela equipe, então as métricas fora da apresentação tendem a ser menores (veja `larouaye-ia/README.md`).

## 7. Uso de IA
Ferramentas de IA generativa foram usadas como apoio (revisão, testes e documentação); código revisado e testado pelo grupo.
