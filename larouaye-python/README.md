# LarOuAyê: Orientador de aquisição (Python, terminal)

Disciplina: **Computational Thinking Using Python** (cards P01 a P03). Roda **sozinho**, sem internet e sem o Java.

```bash
python orientador.py          # precisa de Python 3.10 ou mais (usa match-case)
python -m pytest -q           # 21 testes (pip install pytest)
```

## O que faz (P01)
1. Cadastro mínimo (nome, UF, etapa), salvo em `perfil.json`. Sem CPF nem dado sensível.
2. Ver uma das 6 etapas da compra, com documentos e cuidados.
3. Conferir os documentos da etapa e ver o que **falta**.
4. Tirar dúvida por assunto (matrícula, escritura, contrato, financiamento, FGTS, impostos, leilão, imóvel usado, fraudes) com base legal.
5. **Alerta de fraude**: 6 perguntas de sim/não que somam pontos (inclui "mudaram minha renda ou imposto de renda").
6. Histórico (`historico.csv`) e assunto mais consultado.
7. Resumo de orientações em `resumo_orientacoes.txt`.

## Onde está cada requisito (P02) para mostrar ao professor
| Requisito | Onde ver em `orientador.py` |
|---|---|
| Menus e submenus | `main`/`mostrar_menu`; submenus em `ver_etapa` e `consultar_assunto` |
| `input` | `pedir_texto`, `pedir_numero`, `pedir_sim_nao`, `pedir_uf` |
| f-strings | quase todas as telas (`print(f"...")`) |
| `match-case` | `main` (menu) e `pedir_sim_nao` |
| `if / elif / else` | `avaliar_risco`, `pedir_numero` |
| `while` | todas as funções `pedir_*` e o laço de `main` |
| `for` | `calcular_pendencias`, `contar_assuntos`, telas |
| listas | `documentos`, `faltam`, `docs_ok` |
| tuplas | `UFS`, `SINAIS_FRAUDE` |
| strings | `strip`, `upper`, `lower`, `title`, `join`, `"=" * 40` |
| dicionários | `ETAPAS`, `ASSUNTOS`, `contar_assuntos` |
| sets | `calcular_pendencias` (`set(entregues)`) |
| funções com parâmetros e retorno | `calcular_pendencias`, `avaliar_risco`, `montar_resumo` |
| JSON e CSV | `perfil.json` (`salvar_perfil`) e `historico.csv` (`registrar_consulta`) |
| entradas inválidas | testes `test_pedir_numero_...` e `test_entradas_malucas_...` |

## Regras que dão nota zero ou desconto (conferidas por teste automático)
- **Nenhuma classe** e nenhuma programação orientada a objetos (`test_sem_classes_e_sem_comprehension`).
- **Nenhuma list comprehension** (nem set/dict comprehension nem generator): desconto de 15 pontos por ocorrência.
- Se você editar o código, rode `python -m pytest -q` antes do commit.

## Limites
- `conteudo.py` vem do catálogo do projeto de IA e está **em revisão jurídica**. Informação geral, não é aconselhamento.
- Falta o **PDF do P03** (capa, integrantes, RM, sumário, problema, objetivos, justificativa, funcionalidades, lógica, execução e resultados) e os prints da execução.
