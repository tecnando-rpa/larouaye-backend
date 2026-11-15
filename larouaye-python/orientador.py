"""LarOuAyê - Orientador de aquisição do primeiro imóvel (terminal).

Disciplina: Computational Thinking Using Python.
Roda sozinho: python orientador.py
Regras da disciplina: SEM classes, SEM list comprehension. Usa menus, input, f-strings, match-case,
if/elif/else, while, for, listas, tuplas, strings, dicionários, sets, funções com retorno e JSON/CSV.
"""
import csv
import json
import os
from datetime import datetime

from conteudo import ASSUNTOS, AVISO, ETAPAS

# Tupla: valores que não mudam durante o programa
UFS = ("AC", "AL", "AP", "AM", "BA", "CE", "DF", "ES", "GO", "MA", "MT", "MS", "MG", "PA", "PB", "PR", "PE", "PI", "RJ",
       "RN", "RS", "RO", "RR", "SC", "SP", "SE", "TO")

# Perguntas do teste de alerta de fraude: (texto, pontos). Tupla de tuplas.
SINAIS_FRAUDE = (
    ("Pediram dinheiro ou PIX antes de você ver a matrícula do imóvel?", 3),
    ("O preço está muito abaixo do que se cobra por imóveis parecidos?", 2),
    ("Alguém sugeriu mudar ou aumentar sua renda ou seu imposto de renda?", 4),
    ("Pediram para assinar papel em branco ou sem ler?", 3),
    ("Estão com muita pressa para você fechar negócio?", 2),
    ("O nome de quem recebe o pagamento é diferente do dono na matrícula?", 4),
)

CABECALHO_HISTORICO = ["data", "assunto", "etapa"]


# ---------------------------------------------------------------- arquivos (JSON e CSV)
def pasta_dados():
    """Pasta onde ficam perfil.json, historico.csv e o resumo. Pode ser trocada pela variável LAROUAYE_PASTA."""
    padrao = os.path.dirname(os.path.abspath(__file__))
    return os.environ.get("LAROUAYE_PASTA", padrao)


def caminho(nome_arquivo):
    """Caminho completo de um arquivo na pasta de dados."""
    return os.path.join(pasta_dados(), nome_arquivo)


def perfil_vazio():
    return {"nome": "", "uf": "", "etapa": "", "docs_ok": []}


def carregar_perfil():
    """Lê o perfil salvo. Se não existir ou estiver quebrado, devolve um perfil vazio."""
    try:
        with open(caminho("perfil.json"), encoding="utf-8") as arq:
            dados = json.load(arq)
    except (FileNotFoundError, json.JSONDecodeError):
        return perfil_vazio()
    perfil = perfil_vazio()
    for chave in perfil:
        if chave in dados:
            perfil[chave] = dados[chave]
    return perfil


def salvar_perfil(perfil):
    with open(caminho("perfil.json"), "w", encoding="utf-8") as arq:
        json.dump(perfil, arq, ensure_ascii=False, indent=2)


def registrar_consulta(assunto, etapa):
    """Acrescenta uma linha no historico.csv (cria o arquivo com cabeçalho se precisar)."""
    novo = not os.path.exists(caminho("historico.csv"))
    with open(caminho("historico.csv"), "a", newline="", encoding="utf-8") as arq:
        escritor = csv.writer(arq)
        if novo:
            escritor.writerow(CABECALHO_HISTORICO)
        escritor.writerow([datetime.now().strftime("%d/%m/%Y %H:%M"), assunto, etapa])


def ler_historico():
    """Devolve uma lista de dicionários, uma por consulta."""
    linhas = []
    try:
        with open(caminho("historico.csv"), newline="", encoding="utf-8") as arq:
            for linha in csv.DictReader(arq):
                linhas.append(linha)
    except FileNotFoundError:
        pass
    return linhas


# ---------------------------------------------------------------- entradas seguras
def pedir_texto(mensagem, minimo=2):
    """Repete a pergunta até a pessoa digitar pelo menos `minimo` letras."""
    while True:
        texto = input(mensagem).strip()
        if len(texto) >= minimo:
            return texto
        print(f"  Escreva pelo menos {minimo} letras, por favor.")


def pedir_numero(mensagem, menor, maior):
    """Repete até a pessoa digitar um número inteiro entre `menor` e `maior`."""
    while True:
        valor = input(mensagem).strip()
        if not valor.isdigit():
            print("  Digite só o número da opção.")
        elif int(valor) < menor or int(valor) > maior:
            print(f"  Escolha um número de {menor} a {maior}.")
        else:
            return int(valor)


def pedir_sim_nao(mensagem):
    """Devolve True para sim e False para não."""
    while True:
        resposta = input(mensagem + " (s/n): ").strip().lower()
        match resposta:
            case "s" | "sim":
                return True
            case "n" | "nao" | "não":
                return False
            case _:
                print("  Responda s para sim ou n para não.")


def pedir_uf():
    """Repete até a pessoa digitar uma sigla de UF válida."""
    while True:
        uf = input("Sua UF (ex.: SP): ").strip().upper()
        if uf in UFS:
            return uf
        print("  UF inválida. Use a sigla com 2 letras, por exemplo SP.")


# ---------------------------------------------------------------- regras (funções com retorno)
def etapas_ordenadas():
    """Lista de (codigo, dados) na ordem da jornada."""
    itens = list(ETAPAS.items())
    itens.sort(key=lambda par: par[1]["ordem"])
    return itens


def documentos_da_etapa(codigo):
    return list(ETAPAS[codigo]["documentos"])


def calcular_pendencias(documentos, entregues):
    """Documentos que ainda faltam, mantendo a ordem original. Usa set para comparar."""
    prontos = set(entregues)
    faltam = []
    for doc in documentos:
        if doc not in prontos:
            faltam.append(doc)
    return faltam


def avaliar_risco(respostas):
    """respostas: lista de True/False na mesma ordem de SINAIS_FRAUDE. Devolve (nivel, pontos)."""
    pontos = 0
    for indice in range(len(SINAIS_FRAUDE)):
        if respostas[indice]:
            pontos += SINAIS_FRAUDE[indice][1]
    if pontos >= 7:
        nivel = "ALTO"
    elif pontos >= 3:
        nivel = "MÉDIO"
    else:
        nivel = "BAIXO"
    return nivel, pontos


def contar_assuntos(historico):
    """Dicionário assunto -> quantas vezes foi consultado."""
    contagem = {}
    for linha in historico:
        assunto = linha["assunto"]
        contagem[assunto] = contagem.get(assunto, 0) + 1
    return contagem


def assunto_mais_consultado(contagem):
    """Devolve (assunto, vezes) ou None se não houver consultas."""
    if not contagem:
        return None
    melhor = None
    for assunto, vezes in contagem.items():
        if melhor is None or vezes > melhor[1]:
            melhor = (assunto, vezes)
    return melhor


def nome_da_etapa(codigo):
    if codigo in ETAPAS:
        return ETAPAS[codigo]["nome"]
    return "ainda não escolhida"


def montar_resumo(perfil, historico):
    """Texto do resumo de orientações (string). Usa join e f-strings."""
    linhas = []
    linhas.append("RESUMO DE ORIENTAÇÕES - LarOuAyê")
    linhas.append("=" * 40)
    nome = perfil["nome"] or "(sem nome)"
    linhas.append(f"Nome: {nome.title()}   UF: {perfil['uf'] or '-'}")
    linhas.append(f"Etapa atual: {nome_da_etapa(perfil['etapa'])}")
    linhas.append("")
    if perfil["etapa"] in ETAPAS:
        etapa = ETAPAS[perfil["etapa"]]
        faltam = calcular_pendencias(etapa["documentos"], perfil["docs_ok"])
        linhas.append("Documentos que faltam nesta etapa:")
        if faltam:
            for doc in faltam:
                linhas.append(f"  [ ] {doc}")
        else:
            linhas.append("  Nenhum. Você marcou todos como prontos.")
        linhas.append("Cuidados da etapa:")
        for cuidado in etapa["cuidados"]:
            linhas.append(f"  - {cuidado}")
    linhas.append("")
    linhas.append(f"Consultas feitas: {len(historico)}")
    for assunto, vezes in contar_assuntos(historico).items():
        linhas.append(f"  - {assunto}: {vezes}x")
    linhas.append("")
    linhas.append(AVISO)
    return "\n".join(linhas) + "\n"


# ---------------------------------------------------------------- telas
def cadastrar_perfil(perfil):
    """Pergunta nome, UF e etapa e salva no perfil.json."""
    print("\n--- Seus dados (só ficam neste computador) ---")
    perfil["nome"] = pedir_texto("Como podemos te chamar? ")
    perfil["uf"] = pedir_uf()
    mostrar_etapas_numeradas()
    ordem = etapas_ordenadas()
    escolha = pedir_numero("Em qual etapa você está? ", 1, len(ordem))
    perfil["etapa"] = ordem[escolha - 1][0]
    perfil["docs_ok"] = []
    salvar_perfil(perfil)
    print(f"\nPronto, {perfil['nome'].title()}! Etapa: {nome_da_etapa(perfil['etapa'])}.")


def mostrar_etapas_numeradas():
    """Lista as etapas com número para a pessoa escolher."""
    print("\nEtapas da compra:")
    for posicao, (_, dados) in enumerate(etapas_ordenadas(), start=1):
        print(f"  {posicao}. {dados['nome']}")


def ver_etapa(perfil):
    """Submenu: escolhe uma etapa e mostra descrição, documentos e cuidados."""
    ordem = etapas_ordenadas()
    mostrar_etapas_numeradas()
    escolha = pedir_numero("Qual etapa você quer ver? (0 para voltar) ", 0, len(ordem))
    if escolha == 0:
        return
    codigo, dados = ordem[escolha - 1]
    print(f"\n== {dados['nome']} ==")
    print(dados["descricao"])
    print("Documentos:")
    for doc in dados["documentos"]:
        print(f"  - {doc}")
    print("Cuidados:")
    for cuidado in dados["cuidados"]:
        print(f"  - {cuidado}")
    registrar_consulta(f"Etapa: {dados['nome']}", codigo)


def conferir_documentos(perfil):
    """Marca documentos prontos da etapa atual e mostra o que falta."""
    if perfil["etapa"] not in ETAPAS:
        print("\nPrimeiro escolha sua etapa na opção 1.")
        return
    documentos = documentos_da_etapa(perfil["etapa"])
    print(f"\n--- Documentos da etapa: {nome_da_etapa(perfil['etapa'])} ---")
    for doc in documentos:
        ja_tem = doc in perfil["docs_ok"]
        if ja_tem:
            print(f"  [x] {doc} (já marcado)")
            continue
        if pedir_sim_nao(f"Você já tem: {doc}?"):
            perfil["docs_ok"].append(doc)
    salvar_perfil(perfil)
    faltam = calcular_pendencias(documentos, perfil["docs_ok"])
    if faltam:
        print("\nAinda faltam:")
        for doc in faltam:
            print(f"  [ ] {doc}")
    else:
        print("\nTudo pronto nesta etapa! Veja a próxima etapa na opção 2.")


def consultar_assunto(perfil):
    """Submenu de assuntos jurídicos. Mostra resumo, cuidados e leis."""
    chaves = list(ASSUNTOS.keys())
    print("\nAssuntos:")
    for posicao, chave in enumerate(chaves, start=1):
        print(f"  {posicao}. {ASSUNTOS[chave]['nome']}")
    escolha = pedir_numero("Sobre qual assunto? (0 para voltar) ", 0, len(chaves))
    if escolha == 0:
        return
    assunto = ASSUNTOS[chaves[escolha - 1]]
    for item in assunto["itens"]:
        print(f"\n== {item['titulo']} ==")
        print(item["resumo"])
        print("Cuidados:")
        for cuidado in item["cuidados"]:
            print(f"  - {cuidado}")
        print("Base legal: " + "; ".join(item["leis"]))
        print(f"Próxima etapa sugerida: {nome_da_etapa(item['etapa'])}")
    print("\n" + AVISO)
    registrar_consulta(assunto["nome"], perfil["etapa"] or "-")


def teste_de_fraude(perfil):
    """Perguntas de sim ou não. Soma pontos e mostra o nível de alerta."""
    print("\n--- Alerta de fraude: responda com sinceridade ---")
    respostas = []
    for texto, _ in SINAIS_FRAUDE:
        respostas.append(pedir_sim_nao(texto))
    nivel, pontos = avaliar_risco(respostas)
    print(f"\nNível de alerta: {nivel} ({pontos} pontos)")
    if nivel == "ALTO":
        print("PARE. Não pague nem assine nada. Procure um advogado ou a Defensoria Pública antes de continuar.")
        print("Informar renda falsa para conseguir financiamento pode ser crime, mesmo que a ideia venha do corretor.")
    elif nivel == "MÉDIO":
        print("Cuidado. Confira a matrícula atualizada e peça tudo por escrito antes de pagar.")
    else:
        print("Nenhum sinal forte agora, mas continue conferindo a matrícula e o contrato.")
    registrar_consulta(f"Alerta de fraude: {nivel}", perfil["etapa"] or "-")


def ver_historico():
    """Mostra as consultas feitas e o assunto mais consultado."""
    historico = ler_historico()
    if not historico:
        print("\nVocê ainda não fez consultas.")
        return
    print(f"\n--- Suas {len(historico)} consultas ---")
    for linha in historico:
        print(f"  {linha['data']}  {linha['assunto']}")
    contagem = contar_assuntos(historico)
    destaque = assunto_mais_consultado(contagem)
    print(f"\nAssuntos diferentes: {len(contagem)}")
    print(f"Mais consultado: {destaque[0]} ({destaque[1]}x)")


def gerar_resumo(perfil):
    texto = montar_resumo(perfil, ler_historico())
    with open(caminho("resumo_orientacoes.txt"), "w", encoding="utf-8") as arq:
        arq.write(texto)
    print("\n" + texto)
    print(f"Resumo salvo em: {caminho('resumo_orientacoes.txt')}")


def mostrar_menu(perfil):
    """Desenha o menu principal."""
    nome = perfil["nome"].title() if perfil["nome"] else "visitante"
    print(f"\n=========== LarOuAyê | Olá, {nome} ===========")
    print("1. Meus dados e etapa")
    print("2. Ver uma etapa da compra")
    print("3. Conferir documentos da minha etapa")
    print("4. Tirar dúvida por assunto")
    print("5. Alerta de fraude")
    print("6. Meu histórico")
    print("7. Gerar resumo de orientações")
    print("0. Sair")


def main():
    perfil = carregar_perfil()
    print("Bem-vindo(a) ao LarOuAyê: seu primeiro imóvel, sem juridiquês.")
    print(AVISO)
    while True:
        mostrar_menu(perfil)
        opcao = pedir_numero("Escolha uma opção: ", 0, 7)
        match opcao:
            case 1:
                cadastrar_perfil(perfil)
            case 2:
                ver_etapa(perfil)
            case 3:
                conferir_documentos(perfil)
            case 4:
                consultar_assunto(perfil)
            case 5:
                teste_de_fraude(perfil)
            case 6:
                ver_historico()
            case 7:
                gerar_resumo(perfil)
            case 0:
                print("\nAté logo! Seus dados ficaram salvos.")
                break


if __name__ == "__main__":
    main()
