"""Frases ESCRITAS para ampliar o modelo de INTENCAO (sinteticas, como as de gerar_dataset.py).

Cobrem as duvidas reais que apareceram no Instagram do projeto: consorcio, quanto cabe no bolso, amortizacao,
melhores bancos, avaliacao menor que o contrato, compra de imovel da familia (herdeiros), certidoes, documentacao,
custos para regularizar e subsidio. As 11 perguntas REAIS ficam so em dados/intencao_validacao_real.csv:
elas validam o modelo e NAO entram no treino (nao ha vazamento).

Honestidade academica: treino e teste foram escritos pela mesma equipe/assistente. Para uma medida mais forte,
cada integrante deve acrescentar em EXTRA_TESTE frases escritas do jeito que ele mesmo perguntaria.
"""

EXTRA_TREINO = {
    "FINANCIAMENTO": [
        # consorcio
        "O que e consorcio de imovel?", "Vale a pena fazer consorcio para comprar casa?", "Como funciona a contemplacao no consorcio?",
        "Como dar lance em consorcio imobiliario?", "Consorcio ou financiamento, qual compensa mais?",
        "Quanto e a taxa de administracao do consorcio?", "Posso usar a carta de credito do consorcio para comprar apartamento?",
        "O que acontece se eu desistir do consorcio?", "Consorcio tem juros?", "Quanto tempo demora para ser contemplado no consorcio?",
        "Como funciona sorteio e lance no consorcio de casa?", "A administradora de consorcio e confiavel?",
        "Quero entrar num grupo de consorcio de imovel", "Consorcio imobiliario e uma boa opcao para quem nao tem entrada?",
        # quanto cabe no bolso
        "Quanto de imovel eu consigo pagar com a minha renda?", "Como calcular o valor maximo de imovel que cabe no bolso?",
        "Qual parcela posso pagar sem apertar o orcamento?", "Qual o valor ideal do imovel para o meu salario?",
        "Quanto da renda posso comprometer com a parcela da casa?", "Ganho quatro mil reais, que imovel consigo comprar?",
        "Como saber se consigo financiar um apartamento?", "Dicas para nao se apertar na compra da casa propria",
        "Qual a renda minima para financiar um imovel?", "Preciso ganhar quanto para comprar uma casa de trezentos mil?",
        "Como fazer a conta para saber quanto posso gastar numa casa?",
        # amortizacao
        "Como amortizar o financiamento?", "Quando posso comecar a amortizar o financiamento da casa?",
        "Existe valor minimo para amortizar a divida do imovel?", "Amortizar reduzindo o prazo ou a parcela, o que e melhor?",
        "Posso quitar o financiamento antes do prazo?", "Como adiantar parcelas do financiamento da casa?",
        "Compensa amortizar o financiamento imobiliario?", "Posso usar FGTS para amortizar a divida?",
        "Como funciona a amortizacao extraordinaria?", "Quero pagar mais e diminuir o saldo devedor, como faco?",
        # bancos
        "Qual o melhor banco para financiar imovel?", "Quais bancos financiam casa?",
        "Qual banco tem os juros menores para financiamento imobiliario?", "Como comparar bancos para financiar apartamento?",
        "O que e CET no financiamento?", "Como escolher o banco para financiar a casa?",
        "Da para levar o financiamento para outro banco com juros menores?", "Caixa ou banco privado, qual financia melhor?",
        # avaliacao
        "O banco avaliou o imovel por menos que o preco do contrato", "A avaliacao do banco veio menor que o valor combinado",
        "E se o laudo de avaliacao for menor que o preco do imovel?", "O banco avaliou mais barato, o que eu faco?",
        "A construtora vendeu mais caro do que o banco avaliou", "Como funciona o laudo de avaliacao do banco no financiamento?",
        # como financiar
        "Tenho duvidas sobre financiamento, como faco?", "Como faco para financiar um imovel?",
        "Passo a passo do financiamento imobiliario", "Por onde comeco para financiar minha casa?",
        "Como pedir financiamento da casa propria?", "Primeira vez financiando, o que preciso saber?",
        "Como simular um financiamento de imovel?", "Qual o juros do financiamento imobiliario hoje?",
    ],
    "FGTS_SUBSIDIOS": [
        "Com subsidio posso amortizar antes de cinco anos?", "Posso quitar o financiamento com subsidio antes do prazo?",
        "Se eu vender antes de cinco anos perco o subsidio?", "Tenho subsidio da Caixa, posso adiantar parcelas?",
        "Preciso devolver o subsidio se quitar antes do prazo?", "Subsidio e amortizacao antes de sessenta meses",
        "Quem recebeu subsidio pode vender a casa?", "O subsidio do governo precisa ser devolvido em algum caso?",
        "Posso usar o FGTS para pagar parte da divida do imovel?", "Existe prazo minimo para vender imovel comprado com subsidio?",
    ],
    "IMOVEL_USADO": [
        "Posso comprar imovel da familia do meu marido?", "Casal comprando imovel do pai de um dos dois, qual o cuidado?",
        "Como evitar que os herdeiros questionem a compra?", "Comprar casa dos meus sogros, os irmaos precisam autorizar?",
        "Venda de pai para filho precisa da assinatura dos outros filhos?", "Vendi o imovel para um filho, os outros herdeiros podem anular?",
        "Comprar imovel de parente, quais cuidados juridicos?", "Quero comprar o apartamento da minha mae, como fazer?",
        "Os herdeiros podem contestar a compra do imovel?", "O que e venda de ascendente para descendente?",
        "Comprei casa de familia e nao fizeram inventario, e agora?", "Posso comprar o imovel de um tio sem problema com primos?",
        # reforco (lacunas achadas na primeira rodada de medicao)
        "Que papeis o proprietario do apartamento usado precisa mostrar?",
        "Quais documentos o dono do imovel antigo deve apresentar?",
    ],
    "MATRICULA_ONUS": [
        "Quais certidoes pedir antes de comprar um imovel?", "Que certidoes do vendedor devo conferir?",
        "O que a certidao negativa de debitos do imovel mostra?", "O que observar na certidao de onus reais?",
        "Quais documentos pedir ao vendedor e o que olhar em cada um?", "Que certidoes forense e de protesto devo pedir?",
        "O que olhar na matricula antes de comprar?", "Lista de certidoes para comprar apartamento",
        "Qual a documentacao legal para comprar imovel?", "Quais sao os documentos mais importantes na compra de casa?",
        "Documentacao e minha maior duvida na compra do imovel", "Como garantir que a documentacao do imovel esta correta?",
        "Como identificar riscos na documentacao do imovel?", "Que acoes judiciais posso encontrar nas certidoes do vendedor?",
        # reforco (lacunas achadas na primeira rodada de medicao)
        "Como ver os onus que existem sobre o imovel?",
        "Que documento eu peco para saber se a casa tem problema juridico?",
        "Como consultar pendencias do imovel no cartorio?",
    ],
    "IMPOSTOS_TAXAS": [
        "Quanto pago de imposto e cartorio para colocar o imovel no meu nome?", "Quais os valores de ITBI, escritura e registro?",
        "Quanto custa passar o imovel para o meu nome?", "Quanto custam emolumentos e certidoes?",
        "Quais custos tenho ao regularizar o imovel no nome do comprador?", "Qual o valor dos emolumentos do cartorio?",
        "Quanto pago de taxas para escriturar e registrar o imovel?", "Alem do preco, que custos tem a compra do imovel?",
    ],
    "ESCRITURA_REGISTRO": [
        "Como regularizar o imovel no nome do comprador?", "Como passo o imovel para o meu nome?",
        "Comprei e o imovel ainda esta no nome do vendedor, o que faco?", "Quais os passos para transferir o imovel para o meu nome?",
        # reforco (lacunas achadas na primeira rodada de medicao)
        "Pagando tudo, o que falta para o imovel ser meu no papel?",
        "Contrato de gaveta me faz dono do imovel?",
        "Depois de escriturar tenho que ir ao registro de imoveis?",
    ],
    "CONTRATO": [
        "Posso desistir do contrato de compra do imovel?", "O que preciso conferir antes de assinar o contrato da casa?",
        "O vendedor pediu sinal, como fica se der errado?", "Contrato de compra e venda precisa de testemunha?",
        # reforco (lacunas achadas na primeira rodada de medicao)
        "Quais cuidados tomar antes de assinar o contrato de compra e venda?",
        "Assinei a promessa de compra e dei sinal, posso me arrepender?",
        "Me arrependi da compra depois de dar o sinal, e agora?",
        "O que acontece com o sinal se o vendedor desistir?",
        "Quais clausulas do contrato de imovel sao abusivas?",
        "O contrato de compra e venda precisa ser registrado?",
    ],
    "LEILAO": [
        "Leilao de imovel da Caixa vale a pena?", "Comprei em leilao e tem gente morando, o que fazer?",
        "Como participar de leilao de imoveis?", "Quais riscos comprar casa leiloada?",
        # reforco (lacunas achadas na primeira rodada de medicao)
        "Imovel que o banco retomou e vendido como?",
        "Como comprar casa retomada pela Caixa?",
        "Comprar imovel retomado pelo banco e seguro?",
    ],
    "FRAUDE_GOLPES": [
        "Como saber se o anuncio de imovel e falso?", "Me pediram dinheiro adiantado para segurar o imovel, e golpe?",
        "O vendedor sumiu depois do sinal, o que fazer?", "Como me proteger de golpe na compra da casa?",
        # reforco (lacunas achadas na primeira rodada de medicao)
        "Informar renda que nao tenho no financiamento e crime?",
        "Quais as consequencias de declarar renda falsa para o banco?",
        "O banco descobriu que a renda do financiamento nao era verdadeira",
        "Fui enganado por um corretor na compra do imovel, o que faco?",
        "Documento falso na venda do imovel, como identificar?",
    ],
    "FORA_DO_ESCOPO": [
        "Como funciona consorcio de carro?", "Quero fazer consorcio de moto", "Quanto custa financiar um veiculo?",
        "Como pedir emprestimo pessoal?", "Qual o melhor cartao de credito?", "Quanto custa alugar um apartamento?",
        "Como investir em fundos imobiliarios?", "Como abrir uma conta no banco?", "Qual a taxa do cheque especial?",
        "Quero comprar um terreno para plantar", "Como pintar a parede da sala?", "Qual o melhor plano de saude?",
        "Como declarar imposto de renda do aluguel?", "Preciso de ajuda com minha dieta",
        # reforco (lacunas achadas na primeira rodada de medicao)
        "Quanto custa uma viagem de aviao para o Nordeste?",
        "Qual o horario do jogo do meu time?",
        "Quem vai ganhar o campeonato brasileiro?",
        "Qual a previsao do tempo para amanha?",
        "Como faco para trocar o oleo do carro?",
        "Qual o melhor filme para assistir hoje?",
        "Como instalar um aplicativo no celular?",
        "Quais sao os sintomas da gripe?",
        "Como funciona o bitcoin?",
        "Qual o preco do dolar hoje?",
        "Como tirar passaporte?",
        "Onde posso fazer um curso de ingles?",
        "Me indica uma musica boa",
        "Como fazer uma reserva de hotel?",
    ],
}

EXTRA_TESTE = {
    "FINANCIAMENTO": [
        "consorcio de casa e uma boa?", "Como e que funciona esse negocio de consorcio para imovel?",
        "Qual valor de apartamento cabe no meu salario de cinco mil?", "Como descubro o quanto posso gastar numa casa sem me enforcar?",
        "Quero pagar parcelas extras do financiamento, como faco?", "Da pra amortizar a divida do imovel quando eu quiser?",
        "Qual banco e melhor pra pegar financiamento de casa?", "Comparar juros de bancos para financiar a casa propria",
        "A avaliacao do banco deu menos do que a construtora pediu", "Meu imovel foi avaliado abaixo do preco, como fica a entrada?",
        "Quero financiar minha primeira casa, por onde comeco?", "Como e o processo todo de financiar um apartamento?",
        "Posso entrar em um consorcio para pagar a entrada do imovel?", "Qual e a parcela que cabe no meu orcamento para comprar casa?",
    ],
    "FGTS_SUBSIDIOS": [
        "Se eu pegar subsidio posso quitar antes de 5 anos?", "Vendi a casa do Minha Casa Minha Vida antes do prazo, perco o beneficio?",
        "O FGTS pode ser usado pra abater o saldo devedor?", "Preciso devolver o desconto do subsidio se terminar de pagar antes?",
        "Quem pode pedir subsidio para comprar casa?", "Como usar meu FGTS na compra da casa propria?",
    ],
    "IMOVEL_USADO": [
        "Vou comprar a casa da familia da minha esposa, como me proteger de heranca?", "Comprando imovel de parente, os outros herdeiros podem reclamar?",
        "Pai vendeu o apartamento pra mim, meus irmaos precisam concordar?", "Imovel de heranca com inventario aberto pode ser vendido?",
        "O que verificar numa casa antiga antes de fechar?", "O vendedor e casado, a mulher precisa assinar tambem?",
    ],
    "MATRICULA_ONUS": [
        "Quais certidoes devo exigir do dono do imovel?", "Que papel eu peço no cartorio pra ver se o imovel tem problema?",
        "Que documentos pedir pra ter seguranca na compra?", "O que significa cada item da matricula?",
        "Como ver se existe processo contra o vendedor?", "Quero saber se a casa tem penhora, hipoteca ou acao na justica",
    ],
    "IMPOSTOS_TAXAS": [
        "Quanto vou gastar de cartorio e imposto para ficar com o imovel no meu nome?", "Qual o custo do ITBI mais escritura e registro?",
        "Tem taxa de cartorio pra regularizar o imovel?", "Preciso pagar algum imposto antes de registrar a compra?",
    ],
    "ESCRITURA_REGISTRO": [
        "Como faco para o imovel ficar registrado no meu nome?", "Depois de pagar, o que preciso fazer para ser o dono no papel?",
        "Quanto tempo demora para o cartorio registrar a compra?", "A escritura sozinha ja me torna dono?",
    ],
    "CONTRATO": [
        "O que tem que constar no contrato de compra da casa?", "Dei sinal e me arrependi, o que acontece?",
        "Posso assinar contrato de compra e venda sem advogado?", "Quais clausulas abusivas olhar no contrato do imovel?",
    ],
    "LEILAO": [
        "Imovel de leilao vem com divida?", "Como dar lance em leilao de casa?",
        "Comprar casa que o banco retomou e seguro?", "Quais cuidados no leilao de apartamento?",
    ],
    "FRAUDE_GOLPES": [
        "Alteraram minha renda no financiamento sem eu pedir", "O anuncio da casa parece golpe, como confirmar?",
        "Me pediram PIX pra reservar o apartamento, devo pagar?", "O corretor aumentou meu salario no papel para o banco aprovar",
    ],
    "FORA_DO_ESCOPO": [
        "Como fazer consorcio de carro?", "Quero alugar uma casa, quanto custa?", "Qual a melhor receita de lasanha?",
        "Como emprestar dinheiro no banco para abrir um negocio?", "Quem vai ganhar o campeonato?", "Como renovar a carteira de motorista?",
    ],
}
