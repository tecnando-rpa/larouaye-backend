"""Gera os CSVs de treino e de teste.

IMPORTANTE (honestidade academica): as frases abaixo foram ESCRITAS PELO GRUPO/ASSISTENTE como amostras
sinteticas de perguntas reais. Nao ha coleta de usuarios reais. O conjunto de TESTE e escrito a parte, com
redacao diferente, e NUNCA recebe aumento de dados. Registre isso no relatorio.
"""
import csv
import random
from pathlib import Path

DADOS = Path(__file__).resolve().parent.parent / "dados"

INTENCAO = {
    "MATRICULA_ONUS": [
        "Como descubro se um imovel tem dividas?", "O que e a matricula do imovel?",
        "Como pedir a certidao de onus reais?", "Quero saber se o imovel esta penhorado",
        "Como sei se o apartamento tem alguma pendencia na justica?", "Onde tiro a certidao atualizada da matricula?",
        "O imovel tem hipoteca, e agora?", "Como saber se o dono do imovel tem processos?",
        "O que e alienacao fiduciaria na matricula?", "A casa esta no nome de quem vendeu?",
        "Como ver quem e o verdadeiro dono do imovel?", "O que significa averbacao na matricula?",
        "Posso comprar imovel com penhora?", "Que certidoes preciso pedir sobre o imovel?",
    ],
    "ESCRITURA_REGISTRO": [
        "Como checar se o imovel possui escritura?", "O que e escritura publica?",
        "Preciso registrar a escritura no cartorio de imoveis?", "Qual a diferenca entre escritura e registro?",
        "Quanto custa fazer a escritura?", "Casa sem escritura posso comprar?",
        "Onde fica o cartorio mais proximo para fazer a escritura?", "So tenho contrato de gaveta, isso vale?",
        "Quanto tempo demora para registrar o imovel?", "Quais documentos levo ao cartorio para escriturar?",
        "Escritura e registro sao a mesma coisa?", "Como dar entrada no registro de imoveis?",
        "O imovel so e meu depois do registro?", "Preciso de advogado para fazer a escritura?",
    ],
    "CONTRATO": [
        "Como funciona o contrato de compra e venda?", "O que e o sinal ou arras?",
        "Posso desistir da compra depois de assinar?", "Quais clausulas devo olhar no contrato?",
        "O que e promessa de compra e venda?", "O corretor mandou assinar um contrato, devo assinar?",
        "Se eu desistir perco o sinal?", "Contrato de gaveta e seguro?",
        "Quem paga a comissao do corretor?", "O que e distrato?",
        "Preciso reconhecer firma no contrato?", "Posso assinar o contrato sem advogado?",
        "Qual o prazo para entregar o imovel no contrato?", "O contrato diz multa por atraso, esta certo?",
    ],
    "FINANCIAMENTO": [
        "Como funciona o financiamento habitacional?", "Quanto de entrada preciso dar?",
        "A parcela pode passar de 30% da renda?", "Quais documentos pedem no financiamento?",
        "Qual a diferenca entre SAC e Price?", "Meu nome esta sujo, consigo financiar?",
        "Quanto tempo leva para aprovar o financiamento?", "Posso financiar 100% do imovel?",
        "Quais bancos financiam a casa propria?", "Como funciona a avaliacao do imovel pelo banco?",
        "Posso usar a renda do meu marido para financiar?", "Qual o prazo maximo para pagar o financiamento?",
        "O que e taxa de juros efetiva no financiamento?", "Posso quitar o financiamento antes do prazo?",
    ],
    "FGTS_SUBSIDIOS": [
        "Posso usar o FGTS para comprar a casa?", "Como funciona o Minha Casa Minha Vida?",
        "Quem tem direito a subsidio para comprar imovel?", "Quanto tempo de FGTS preciso ter?",
        "Posso usar o FGTS na entrada?", "O FGTS paga parcela do financiamento?",
        "Qual a renda maxima para o Minha Casa Minha Vida?", "Como pedir o subsidio do governo?",
        "Ja tive imovel, ainda posso usar o FGTS?", "O FGTS vale para imovel usado?",
        "O que e a Faixa 1 do programa de moradia?", "Tem ajuda do governo para primeira casa?",
        "Como consultar meu saldo do FGTS para comprar casa?", "Posso usar FGTS de outra pessoa?",
    ],
    "IMPOSTOS_TAXAS": [
        "O que e ITBI e quem paga?", "Quais impostos pago ao comprar um imovel?",
        "Quanto custa o ITBI?", "Tenho que pagar IPTU atrasado do vendedor?",
        "Existe isencao de ITBI para primeiro imovel?", "Quais taxas de cartorio vou pagar?",
        "Pago imposto de renda quando vendo imovel?", "O que e ganho de capital?",
        "Quem paga o ITBI, comprador ou vendedor?", "Quando vence o ITBI?",
        "Preciso declarar o imovel no imposto de renda?", "Quais custos alem do valor do imovel?",
        "O que e o laudemio e a taxa de transferencia?", "Como pagar o ITBI na prefeitura?",
    ],
    "LEILAO": [
        "Como funciona comprar imovel em leilao?", "Imovel de leilao da Caixa e seguro?",
        "Quais os riscos do leilao de imoveis?", "Posso financiar imovel de leilao?",
        "Quem paga as dividas do imovel leiloado?", "O que e leilao judicial?",
        "Como saber se o leilao e confiavel?", "Se tiver gente morando no imovel do leilao, e agora?",
        "Tem comissao do leiloeiro?", "Posso desistir da arrematacao?",
        "Qual a diferenca entre primeiro e segundo leilao?", "Preciso de advogado para comprar em leilao?",
        "Da para visitar o imovel antes do leilao?", "O que e venda direta de imovel retomado pelo banco?",
    ],
    "IMOVEL_USADO": [
        "Quais documentos o vendedor precisa me entregar?", "Como comprar um imovel usado com seguranca?",
        "O que conferir antes de comprar apartamento usado?", "Como saber se o condominio tem dividas?",
        "Preciso pedir certidao negativa do condominio?", "Vale a pena fazer vistoria antes da compra?",
        "A casa tem construcao sem averbacao, posso comprar?", "O vendedor e casado, a esposa tem que assinar?",
        "O imovel esta em nome de pessoa falecida, posso comprar?", "Como confirmar se o vendedor e o dono mesmo?",
        "Que problemas aparecem em imovel antigo?", "Posso comprar casa de heranca ainda em inventario?",
        "Tem que ver o habite-se do imovel?", "Como checar a area do terreno e da casa?",
    ],
    "FRAUDE_GOLPES": [
        "O corretor alterou meu imposto de renda para conseguir o financiamento, o que acontece?",
        "Corretor pediu para colocar minha esposa como dependente no IR, posso?",
        "E crime aumentar a renda para aprovar financiamento?", "Como saber se o anuncio do imovel e golpe?",
        "Pediram um sinal por PIX antes de ver o imovel, e seguro?", "O boleto do imovel veio com outro nome, e golpe?",
        "O que e simulacao financeira?", "O vendedor nao quer mostrar a matricula, e golpe?",
        "Quais sinais de fraude em financiamento?", "Alguem pode usar meu nome para financiar imovel?",
        "O corretor disse que faz acontecer com a renda, devo confiar?", "Ja assinei documento com renda falsa, o que fazer?",
        "Preco muito abaixo do mercado e golpe?", "Como denunciar fraude em compra de imovel?",
        "O corretor mudou meu IRRF para o banco aprovar, e agora?", "Alteraram minha declaracao de imposto de renda sem eu saber",
        "O corretor colocou minha esposa como dependente para aumentar a renda", "Inflaram a minha renda no pedido de financiamento",
        "Corretor disse para declarar uma renda maior, tem problema?", "Posso ser punido se o corretor falsificou meus documentos?",
    ],
    "FORA_DO_ESCOPO": [
        "Quero financiar um carro", "Qual a receita de bolo de cenoura?", "Quem ganhou o jogo ontem?",
        "Como esta o tempo hoje?", "Me conta uma piada", "Como tirar carteira de motorista?",
        "Qual o melhor celular para comprar?", "Como investir em acoes?",
        "Como declarar imposto de renda do trabalho?", "Quero alugar um apartamento",
        "Como emagrecer rapido?", "Qual a capital da Franca?", "Como abrir uma empresa?",
        "Me ajuda com meu dever de casa de matematica",
    ],
}

INTENCAO_TESTE = {
    "MATRICULA_ONUS": ["Preciso ver se o apartamento tem alguma divida no cartorio", "Como e a certidao de matricula atualizada?",
                       "O imovel pode estar com penhora ou hipoteca?", "Como consultar os onus que pesam sobre a casa?"],
    "ESCRITURA_REGISTRO": ["A casa tem escritura registrada em cartorio?", "Qual o custo para escriturar e registrar?",
                           "Quem so tem contrato de gaveta e dono do imovel?", "Como funciona o registro no cartorio de imoveis?"],
    "CONTRATO": ["Quais cuidados antes de assinar a compra e venda?", "Se eu der sinal e desistir, perco o dinheiro?",
                 "Como e uma promessa de compra e venda?", "Quais pontos olhar no contrato do corretor?"],
    "FINANCIAMENTO": ["Como o banco financia a compra da casa?", "Quanto precisa dar de entrada no financiamento?",
                      "Qual a parcela maxima em relacao ao salario?", "Que papeis o banco pede para financiar?"],
    "FGTS_SUBSIDIOS": ["Como usar o saldo do FGTS na compra do imovel?", "Quem pode participar do Minha Casa Minha Vida?",
                       "Existe subsidio do governo para quem compra a primeira casa?", "O FGTS pode entrar como entrada?"],
    "IMPOSTOS_TAXAS": ["Que impostos incidem na compra de um imovel?", "Quem arca com o ITBI?",
                       "Preciso pagar imposto se vender minha casa com lucro?", "Quanto se paga de taxas no cartorio?"],
    "LEILAO": ["E seguro arrematar imovel em leilao?", "Quais cuidados antes de dar lance em leilao de imovel?",
               "Como funciona a compra de casa retomada pelo banco?", "Imovel de leilao vem com dividas?"],
    "IMOVEL_USADO": ["Que documentos o dono do apartamento usado deve apresentar?", "Como conferir um imovel antigo antes de comprar?",
                     "A esposa do vendedor precisa assinar a venda?", "O condominio pode ter debitos que passam para mim?"],
    "FRAUDE_GOLPES": ["O corretor mexeu na minha declaracao de renda para aprovar o credito, isso e crime?",
                      "Como perceber um golpe na venda de imovel?", "Pediram PIX adiantado de um imovel que nem visitei",
                      "Informar renda falsa no financiamento tem consequencia?"],
    "FORA_DO_ESCOPO": ["Qual o melhor time de futebol do Brasil?", "Como fazer um bolo de chocolate?",
                       "Quero comprar um celular novo", "Quanto custa uma passagem de aviao?"],
}

ETAPA = {
    "PESQUISA_IMOVEL": [
        "Estou procurando apartamento para comprar", "Ainda estou visitando casas", "Quero comecar a ver imoveis na minha cidade",
        "Como escolher um bairro para morar?", "Estou comparando precos de apartamentos", "Vi um anuncio e quero visitar o imovel",
        "Quanto de imovel posso pagar pelo meu salario?", "Ainda nao escolhi o imovel", "Estou olhando sites de imoveis",
        "Quero saber o que olhar na visita ao imovel", "Vou ver uma casa no sabado", "Como saber se o preco do imovel esta justo?",
        "Quero simular um financiamento para saber quanto posso pagar",
    ],
    "ANALISE_DOCUMENTAL": [
        "Ja escolhi o imovel e quero conferir os documentos", "Preciso pedir a matricula e certidoes",
        "Quero saber se o imovel tem dividas antes de fechar", "O vendedor me entregou uns papeis, como conferir?",
        "Vou pedir certidao negativa do vendedor", "Estou checando se o dono e o dono mesmo", "Quero ver se tem penhora",
        "Peguei a matricula e nao entendi nada", "Antes de pagar sinal quero conferir tudo", "Falta algum documento do vendedor?",
        "Como ler a matricula que recebi?", "Preciso conferir a situacao do imovel", "Quero a certidao de onus do imovel",
    ],
    "NEGOCIACAO_CONTRATO": [
        "Ja combinei o preco com o vendedor", "Recebi o contrato para assinar", "O corretor quer que eu pague o sinal",
        "Vou assinar a promessa de compra e venda", "Quero negociar o desconto e as clausulas", "Tem multa se eu desistir depois de assinar?",
        "O vendedor mandou a minuta do contrato", "Vamos fechar negocio amanha", "Quanto dar de sinal?",
        "Preciso de ajuda para entender o contrato", "O banco aprovou meu financiamento e agora vou assinar o contrato",
        "Quero saber se posso desistir do negocio", "O corretor disse para assinar hoje",
    ],
    "ESCRITURA": [
        "Ja assinei o contrato e preciso fazer a escritura", "Vou ao cartorio de notas amanha", "Quanto custa a escritura publica?",
        "Quais documentos levar ao tabelionato?", "Comprador e vendedor precisam ir juntos ao cartorio?", "Quero marcar a escritura",
        "Como funciona a lavratura da escritura?", "O banco pediu a escritura", "Estou escolhendo o cartorio de notas",
        "Preciso de procuracao para escriturar?", "Ja paguei tudo e falta a escritura", "Como pedir a escritura do imovel?",
        "A escritura pode ser feita por instrumento particular?",
    ],
    "ITBI_TRIBUTOS": [
        "Preciso pagar o ITBI antes da escritura", "Como emitir a guia do ITBI?", "Quanto e o ITBI na minha cidade?",
        "Tenho direito a isencao de imposto?", "Estou com IPTU atrasado do imovel", "Quais impostos faltam pagar?",
        "A prefeitura calculou o ITBI sobre o valor errado", "Onde pago o imposto de transmissao?",
        "Preciso do comprovante de ITBI para o cartorio", "Como pedir desconto no ITBI?", "Quem paga o imposto, eu ou o vendedor?",
        "Como funciona o imposto sobre ganho de capital?", "Quero emitir a guia de imposto da compra",
    ],
    "REGISTRO_IMOVEL": [
        "Ja tenho a escritura e quero registrar", "Como dar entrada no registro de imoveis?", "Quanto custa o registro?",
        "Quanto tempo o cartorio leva para registrar?", "Recebi a nota devolutiva do cartorio", "O registro foi negado, e agora?",
        "Como pedir a matricula atualizada com meu nome?", "Ja registrei, o que fazer agora?", "O imovel ja esta no meu nome?",
        "Preciso averbar algo depois do registro?", "Falta registrar o financiamento", "Qual o prazo do registro depois da escritura?",
        "Quero levar a escritura ao registro de imoveis",
    ],
}

ETAPA_TESTE = {
    "PESQUISA_IMOVEL": ["Estou vendo apartamentos para comprar", "Como escolher uma casa para o primeiro imovel?", "Quero visitar um imovel no fim de semana"],
    "ANALISE_DOCUMENTAL": ["Quero conferir a matricula antes de fechar negocio", "Preciso das certidoes do vendedor", "Como verificar se ha dividas na casa que escolhi?"],
    "NEGOCIACAO_CONTRATO": ["O vendedor me passou o contrato de compra e venda", "Posso desistir depois de dar o sinal?", "Estou negociando o preco e as clausulas"],
    "ESCRITURA": ["Preciso marcar a escritura no cartorio de notas", "Que documentos levo para lavrar a escritura?", "Qual o valor para lavrar a escritura no tabelionato?"],
    "ITBI_TRIBUTOS": ["Como pago o ITBI da compra?", "A guia do imposto de transmissao esta cara", "Tenho IPTU atrasado e preciso regularizar"],
    "REGISTRO_IMOVEL": ["Quero registrar a escritura em cartorio", "O cartorio devolveu meu pedido de registro", "Quanto demora o registro do imovel?"],
}

PREFIXOS = ["", "", "Oi, ", "Boa tarde, ", "Bom dia! ", "Ola, ", "Por favor, ", "Preciso saber: ", "Pode me ajudar? ", "Minha duvida: "]
SUFIXOS = ["", "", "", " por favor", " obrigado", " me explica", " pode explicar?"]


def aumentar(frases, rotulo, fator, rnd):
    """Aumento simples (so no TREINO): cumprimentos, caixa baixa e sem pontuacao."""
    saida = []
    for f in frases:
        saida.append((f, rotulo))
        for _ in range(fator):
            t = rnd.choice(PREFIXOS) + f + rnd.choice(SUFIXOS)
            if rnd.random() < 0.4:
                t = t.lower().replace("?", "")
            saida.append((t, rotulo))
    vistos, unicos = set(), []
    for t, r in saida:
        if t not in vistos:
            vistos.add(t)
            unicos.append((t, r))
    return unicos


def gravar(nome, linhas):
    with open(DADOS / nome, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["texto", "rotulo"])
        w.writerows(linhas)


def main():
    rnd = random.Random(42)
    for nome, base, teste in (("intencao", INTENCAO, INTENCAO_TESTE), ("etapa", ETAPA, ETAPA_TESTE)):
        treino = [x for r, fs in base.items() for x in aumentar(fs, r, 4, rnd)]
        rnd.shuffle(treino)
        gravar(f"{nome}_treino.csv", treino)
        gravar(f"{nome}_teste.csv", [(f, r) for r, fs in teste.items() for f in fs])
        print(nome, "treino:", len(treino), "teste:", sum(len(v) for v in teste.values()))


if __name__ == "__main__":
    main()
