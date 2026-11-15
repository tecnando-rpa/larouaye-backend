"""Gera dados/base_conhecimento.json (conteudo de apoio, EM REVISAO JURIDICA).
Edite aqui e rode: python treino/gerar_base.py. Quando o advogado aprovar um item, troque revisado=True e dataRevisao."""
import json
from pathlib import Path

PL = "https://www.planalto.gov.br/ccivil_03/"
N = {
    "lrp": {"norma": "Lei 6.015/1973", "referencia": "Lei de Registros Públicos", "url": PL + "leis/l6015compilada.htm"},
    "cc": {"norma": "Código Civil (Lei 10.406/2002)", "referencia": "", "url": PL + "leis/2002/l10406compilada.htm"},
    "l13097": {"norma": "Lei 13.097/2015", "referencia": "art. 54 (publicidade da matrícula)", "url": PL + "_ato2015-2018/2015/lei/l13097.htm"},
    "l9514": {"norma": "Lei 9.514/1997", "referencia": "Alienação fiduciária de imóvel", "url": PL + "leis/l9514.htm"},
    "l7492": {"norma": "Lei 7.492/1986", "referencia": "art. 19 (fraude para obter financiamento)", "url": PL + "leis/l7492.htm"},
    "cp": {"norma": "Código Penal (Decreto-Lei 2.848/1940)", "referencia": "arts. 171 e 299", "url": PL + "decreto-lei/del2848compilado.htm"},
    "l8036": {"norma": "Lei 8.036/1990", "referencia": "FGTS", "url": PL + "leis/l8036consol.htm"},
    "l14620": {"norma": "Lei 14.620/2023", "referencia": "Programa Minha Casa, Minha Vida", "url": PL + "_ato2023-2026/2023/lei/L14620.htm"},
    "ctn": {"norma": "Código Tributário Nacional (Lei 5.172/1966)", "referencia": "arts. 35 e 130", "url": PL + "leis/l5172compilado.htm"},
    "l11196": {"norma": "Lei 11.196/2005", "referencia": "art. 39 (ganho de capital na venda de imóvel residencial)", "url": PL + "_ato2004-2006/2005/lei/l11196.htm"},
    "l8935": {"norma": "Lei 8.935/1994", "referencia": "Cartórios (notas e registro)", "url": PL + "leis/l8935.htm"},
    "cpc": {"norma": "Código de Processo Civil (Lei 13.105/2015)", "referencia": "venda em leilão judicial", "url": PL + "_ato2015-2018/2015/lei/l13105.htm"},
    "d21981": {"norma": "Decreto 21.981/1932", "referencia": "Leiloeiros", "url": PL + "decreto/1930-1949/d21981.htm"},
}
ONR = {"titulo": "ONR: certidões de imóveis pela internet", "url": "https://registradores.onr.org.br"}
CNB = {"titulo": "Colégio Notarial do Brasil", "url": "https://www.notariado.org.br"}
CAIXA = {"titulo": "Caixa: habitação", "url": "https://www.caixa.gov.br/voce/habitacao/"}
GOVRF = {"titulo": "Receita Federal", "url": "https://www.gov.br/receitafederal/pt-br"}
GOVC = {"titulo": "Ministério das Cidades", "url": "https://www.gov.br/cidades/pt-br"}


def o(i, cat, tit, perg, conteudo, cuidados, normas, prox, fontes=None):
    return {"id": i, "categoria": cat, "titulo": tit, "perguntaRelacionada": perg, "conteudo": conteudo,
            "cuidados": cuidados, "baseLegal": [N[n] for n in normas], "proximaEtapa": prox,
            "fontes": fontes or [], "revisado": False, "dataRevisao": None}


O = [
    o(1, "MATRICULA_ONUS", "Como saber se o imóvel tem dívidas ou restrições", "Como descubro se um imóvel tem dívidas?",
      "Peça a matrícula atualizada do imóvel no Cartório de Registro de Imóveis da região onde ele fica. Nela aparecem o dono, as hipotecas, as penhoras e outras restrições. Peça também a certidão de ônus reais. Depois, confira as certidões do vendedor (ações na justiça e protestos) e se o IPTU e o condomínio estão em dia.",
      ["Use matrícula e certidões emitidas nos últimos dias, porque elas mudam com o tempo.", "Pergunte ao cartório o prazo de validade que ele aceita.", "Não pague sinal antes de ver a matrícula.", "Se aparecer algo que você não entende, leve a um advogado ou à Defensoria."],
      ["lrp", "l13097", "cc"], "ANALISE_DOCUMENTAL", [ONR]),
    o(2, "MATRICULA_ONUS", "O que é a matrícula do imóvel", "O que é a matrícula do imóvel?",
      "A matrícula é a ficha do imóvel no Cartório de Registro de Imóveis. Ela conta a história dele: quem é o dono, se existe financiamento, hipoteca ou penhora e se houve mudanças na construção. Cada imóvel tem um número de matrícula só dele.",
      ["Procure o nome do vendedor como dono na matrícula.", "Veja se existe alienação fiduciária: significa que o imóvel está como garantia de um financiamento.", "Mudanças na construção precisam estar anotadas (averbadas) na matrícula."],
      ["lrp", "l9514"], "ANALISE_DOCUMENTAL", [ONR]),
    o(3, "ESCRITURA_REGISTRO", "Como saber se o imóvel tem escritura e registro", "Como checar se o imóvel possui escritura?",
      "Escritura e registro são coisas diferentes. A escritura é feita no Tabelionato de Notas. O registro é feito no Cartório de Registro de Imóveis, e é o registro que passa a propriedade para o seu nome. Para saber se existe registro, peça a matrícula atualizada e veja se o vendedor aparece como dono.",
      ["Contrato de gaveta ou recibo não transferem a propriedade.", "Se o vendedor não aparece como dono na matrícula, pare e procure orientação antes de pagar.", "A escritura sozinha não prova que você é o dono: falta o registro."],
      ["cc", "lrp", "l8935"], "ESCRITURA", [ONR, CNB]),
    o(4, "ESCRITURA_REGISTRO", "Passos e custos da escritura e do registro", "Quanto custa fazer a escritura?",
      "Em geral os passos são: pagar o ITBI na prefeitura, reunir os documentos e as certidões, fazer a escritura no Tabelionato de Notas e levar a escritura ao Registro de Imóveis. As taxas de cartório (emolumentos) são tabeladas por cada estado e mudam conforme o valor do imóvel. Em alguns financiamentos o próprio contrato do banco substitui a escritura.",
      ["Consulte a tabela de emolumentos do Tribunal de Justiça do seu estado.", "Peça ao cartório uma lista de documentos antes de ir.", "Guarde todos os comprovantes de pagamento."],
      ["cc", "lrp", "l9514"], "ESCRITURA", [CNB]),
    o(5, "CONTRATO", "Contrato de compra e venda, sinal e desistência", "Posso desistir da compra depois de assinar?",
      "Antes de assinar, leia o contrato inteiro. Confira os nomes, o número da matrícula, o preço, a forma de pagamento, o prazo, as multas e quem paga cada custo. O sinal (arras) é um adiantamento: pelo Código Civil, quem dá o sinal e desiste costuma perdê-lo, e quem recebe e desiste costuma devolver em dobro, salvo o que o contrato disser. A desistência depende do que está escrito no contrato.",
      ["Não assine com pressa nem com páginas em branco.", "Peça cópia de tudo e guarde recibos de qualquer pagamento.", "Leve o contrato a um advogado ou à Defensoria antes de assinar."],
      ["cc"], "NEGOCIACAO_CONTRATO", []),
    o(6, "FINANCIAMENTO", "Como funciona o financiamento habitacional", "Como funciona o financiamento habitacional?",
      "Você paga uma entrada e o banco financia o resto, em parcelas. O banco analisa sua renda, seu histórico de crédito e o imóvel. Muitos bancos limitam a parcela a cerca de 30% da renda, mas isso é regra do banco, não da lei. Nos financiamentos o próprio imóvel fica como garantia (alienação fiduciária): se as parcelas pararem, o imóvel pode ser retomado e leiloado.",
      ["Simule em mais de um banco e compare o custo total (CET), não só a parcela.", "Informe só a renda real e comprovada.", "Pergunte sobre seguros e taxas.", "Confira se pode amortizar ou quitar antes do prazo."],
      ["l9514"], "NEGOCIACAO_CONTRATO", [CAIXA]),
    o(7, "FGTS_SUBSIDIOS", "FGTS e subsídios para a casa própria", "Posso usar o FGTS para comprar a casa?",
      "O FGTS pode ajudar na entrada, nas parcelas ou na amortização, desde que as regras sejam cumpridas, por exemplo tempo de trabalho com FGTS e não ter outro financiamento ativo. O programa Minha Casa, Minha Vida tem faixas de renda e subsídio que mudam com o tempo. Confira as regras de hoje no banco que vai financiar.",
      ["Confirme no app do FGTS e no banco se você atende aos requisitos.", "Faixas de renda e valores de subsídio mudam: não confie em informação antiga.", "Desconfie de quem cobra para liberar subsídio ou FGTS."],
      ["l8036", "l14620"], "PESQUISA_IMOVEL", [CAIXA, GOVC]),
    o(8, "IMPOSTOS_TAXAS", "ITBI, IPTU, ganho de capital e outros custos", "Quais impostos pago ao comprar um imóvel?",
      "O ITBI é o imposto da compra: é cobrado pela prefeitura, e a alíquota e as isenções mudam de cidade para cidade. Em geral quem compra paga, mas confira o contrato. IPTU e condomínio atrasados ficam ligados ao imóvel e podem ser cobrados do novo dono. Quem vende com lucro pode ter imposto de renda sobre o ganho de capital, e existem regras de isenção. Some também escritura, registro, avaliação do banco e seguros.",
      ["Pergunte na prefeitura da cidade do imóvel o valor e as isenções do ITBI.", "Peça certidão negativa de IPTU e declaração do condomínio.", "Nunca confie em promessa de isenção sem conferir na fonte oficial."],
      ["ctn", "l11196", "cc"], "ITBI_TRIBUTOS", [GOVRF]),
    o(9, "LEILAO", "Comprar imóvel em leilão", "Como funciona comprar imóvel em leilão?",
      "Imóvel de leilão pode ter preço menor, mas tem riscos: pode estar ocupado, ter dívidas e ter regras de pagamento rígidas. As regras mudam conforme o tipo: leilão judicial, leilão do banco (alienação fiduciária) ou venda direta. Tudo vem no edital, que precisa ser lido por inteiro junto com a matrícula.",
      ["Leia o edital e a matrícula antes de dar qualquer lance.", "Veja se o imóvel está ocupado e quem paga as dívidas.", "Pague só pelos canais oficiais do edital.", "Desconfie de leilão em site desconhecido ou com preço bom demais."],
      ["l9514", "cpc", "d21981"], "PESQUISA_IMOVEL", [CAIXA]),
    o(10, "IMOVEL_USADO", "Checklist para comprar imóvel usado", "Quais documentos o vendedor precisa me entregar?",
      "Peça do vendedor documento de identidade, CPF, certidão de estado civil, certidões negativas, comprovante de IPTU em dia e declaração do condomínio. Peça a matrícula atualizada e confira se a construção está registrada. Se o vendedor é casado, em regra o cônjuge também precisa assinar. Se o dono faleceu, a venda depende do inventário.",
      ["Visite o imóvel com calma e, se possível, leve alguém de confiança.", "Confira se a área real bate com a da matrícula.", "Pergunte sobre dívidas de condomínio.", "Em caso de inventário ou herança, procure um advogado antes de pagar."],
      ["cc", "lrp"], "ANALISE_DOCUMENTAL", []),
    o(11, "FRAUDE_GOLPES", "Fraude no financiamento: renda ou imposto de renda alterados", "O corretor alterou meu imposto de renda para conseguir o financiamento, o que acontece?",
      "Informar renda falsa ou alterar o imposto de renda para conseguir financiamento pode ser crime, mesmo quando a ideia veio do corretor. Pode haver responsabilidade de quem assina e também consequências com a Receita Federal e com o banco. Desconfie de quem diz que faz acontecer com a sua renda.",
      ["Não assine documento que você não entende ou com campo em branco.", "Se algo assim já aconteceu, procure um advogado ou a Defensoria antes de qualquer iniciativa por conta própria.", "Guarde mensagens e documentos que mostram o que foi combinado.", "Use sempre a renda real."],
      ["l7492", "cp"], "NEGOCIACAO_CONTRATO", [GOVRF]),
    o(12, "FRAUDE_GOLPES", "Golpes na compra: anúncio, PIX e boleto", "Como saber se o anúncio do imóvel é golpe?",
      "Sinais de golpe: preço muito abaixo do mercado, pressa para pagar, sinal por PIX antes de ver o imóvel e o contrato, vendedor que não mostra a matrícula e boleto com nome diferente do vendedor. Para se proteger, confira a matrícula e a identidade do dono e pague somente depois de conferir tudo.",
      ["Não pague nada antes de ver o imóvel e a matrícula.", "Confira o nome do dono na matrícula e no pagamento.", "Em caso de golpe, registre boletim de ocorrência e avise o banco."],
      ["cp", "lrp"], "ANALISE_DOCUMENTAL", [ONR]),
]
ETAPAS = [
    {"id": 1, "codigo": "PESQUISA_IMOVEL", "ordem": 1, "nome": "Pesquisa e escolha do imóvel", "descricao": "Defina quanto pode pagar, simule o financiamento e visite os imóveis.", "documentos": ["Documento de identidade e CPF", "Comprovante de renda"], "cuidados": ["Compare preços", "Não pague nada antes de conferir os documentos"]},
    {"id": 2, "codigo": "ANALISE_DOCUMENTAL", "ordem": 2, "nome": "Análise documental", "descricao": "Confira a matrícula, as certidões e as dívidas antes de fechar negócio.", "documentos": ["Matrícula atualizada", "Certidão de ônus reais", "Certidões do vendedor", "IPTU e condomínio em dia"], "cuidados": ["Documentos recentes", "Nome do dono igual ao do vendedor"]},
    {"id": 3, "codigo": "NEGOCIACAO_CONTRATO", "ordem": 3, "nome": "Negociação e contrato", "descricao": "Combine preço e forma de pagamento e leia o contrato inteiro antes de assinar.", "documentos": ["Minuta do contrato", "Comprovantes de sinal"], "cuidados": ["Não assine com pressa", "Guarde cópia de tudo"]},
    {"id": 4, "codigo": "ESCRITURA", "ordem": 4, "nome": "Escritura ou instrumento aplicável", "descricao": "Feita no Tabelionato de Notas, ou pelo contrato do banco quando o financiamento permitir.", "documentos": ["Documentos pessoais", "Certidões", "Comprovante de ITBI"], "cuidados": ["Veja a tabela de emolumentos do estado"]},
    {"id": 5, "codigo": "ITBI_TRIBUTOS", "ordem": 5, "nome": "ITBI e tributos", "descricao": "Pague o ITBI na prefeitura e confira IPTU e condomínio.", "documentos": ["Guia de ITBI paga"], "cuidados": ["Valor e isenções mudam por cidade"]},
    {"id": 6, "codigo": "REGISTRO_IMOVEL", "ordem": 6, "nome": "Registro imobiliário", "descricao": "Leve a escritura ao Registro de Imóveis: o registro passa o imóvel para o seu nome.", "documentos": ["Escritura", "Comprovante de ITBI"], "cuidados": ["Acompanhe o pedido e atenda a nota devolutiva, se houver"]},
]
ROTULOS = {
    "MATRICULA_ONUS": "Matrícula e dívidas do imóvel", "ESCRITURA_REGISTRO": "Escritura e registro", "CONTRATO": "Contrato de compra e venda",
    "FINANCIAMENTO": "Financiamento", "FGTS_SUBSIDIOS": "FGTS e subsídios", "IMPOSTOS_TAXAS": "Impostos e taxas", "LEILAO": "Leilão",
    "IMOVEL_USADO": "Imóvel usado", "FRAUDE_GOLPES": "Fraudes e golpes",
}
KB = {
    "aviso": "CONTEÚDO EM REVISÃO JURÍDICA: texto de apoio escrito para o projeto, ainda NÃO aprovado por advogado. Só mostre dataRevisao depois da aprovação (campo revisado).",
    "categorias": [{"id": i + 1, "codigo": c, "nome": ROTULOS[c]} for i, c in enumerate(ROTULOS)],
    "orientacoes": O, "etapas": ETAPAS,
    "fora_do_escopo": "Eu só ajudo com a compra do primeiro imóvel. Posso explicar documentos, contrato, financiamento, FGTS, impostos, leilão e golpes. Tente perguntar sobre um desses assuntos.",
}
if __name__ == "__main__":
    destino = Path(__file__).resolve().parent.parent / "dados" / "base_conhecimento.json"
    destino.write_text(json.dumps(KB, ensure_ascii=False, indent=2), encoding="utf-8")
    print("ok", len(O), "orientações")
