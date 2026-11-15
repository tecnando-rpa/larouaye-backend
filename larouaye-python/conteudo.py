"""Conteudo do orientador (dicionarios). EM REVISAO JURIDICA: informacao geral, nao e aconselhamento.
Gerado a partir de dados/base_conhecimento.json do projeto LarOuAye. Atualize aqui apos a revisao do advogado."""

AVISO = "Informação geral, não é aconselhamento para o seu caso. Para decidir, procure um advogado ou a Defensoria Pública. Conteúdo em revisão jurídica."

ASSUNTOS = {'MATRICULA_ONUS': {'nome': 'Matrícula e dívidas do imóvel',
                    'itens': [{'titulo': 'Como saber se o imóvel tem dívidas ou restrições',
                               'resumo': 'Peça a matrícula atualizada do imóvel no Cartório de Registro de '
                                         'Imóveis da região onde ele fica. Nela aparecem o dono, as '
                                         'hipotecas, as penhoras e outras restrições. Peça também a certidão '
                                         'de ônus reais. Depois, confira as certidões do vendedor (ações na '
                                         'justiça e protestos) e se o IPTU e o condomínio estão em dia.',
                               'cuidados': ['Use matrícula e certidões emitidas nos últimos dias, porque '
                                            'elas mudam com o tempo.',
                                            'Pergunte ao cartório o prazo de validade que ele aceita.',
                                            'Não pague sinal antes de ver a matrícula.',
                                            'Se aparecer algo que você não entende, leve a um advogado ou à '
                                            'Defensoria.'],
                               'leis': ['Lei 6.015/1973 (Lei de Registros Públicos)',
                                        'Lei 13.097/2015 (art. 54 (publicidade da matrícula))',
                                        'Código Civil (Lei 10.406/2002)'],
                               'etapa': 'ANALISE_DOCUMENTAL'},
                              {'titulo': 'O que é a matrícula do imóvel',
                               'resumo': 'A matrícula é a ficha do imóvel no Cartório de Registro de '
                                         'Imóveis. Ela conta a história dele: quem é o dono, se existe '
                                         'financiamento, hipoteca ou penhora e se houve mudanças na '
                                         'construção. Cada imóvel tem um número de matrícula só dele.',
                               'cuidados': ['Procure o nome do vendedor como dono na matrícula.',
                                            'Veja se existe alienação fiduciária: significa que o imóvel '
                                            'está como garantia de um financiamento.',
                                            'Mudanças na construção precisam estar anotadas (averbadas) na '
                                            'matrícula.'],
                               'leis': ['Lei 6.015/1973 (Lei de Registros Públicos)',
                                        'Lei 9.514/1997 (Alienação fiduciária de imóvel)'],
                               'etapa': 'ANALISE_DOCUMENTAL'}]},
 'ESCRITURA_REGISTRO': {'nome': 'Escritura e registro',
                        'itens': [{'titulo': 'Como saber se o imóvel tem escritura e registro',
                                   'resumo': 'Escritura e registro são coisas diferentes. A escritura é '
                                             'feita no Tabelionato de Notas. O registro é feito no Cartório '
                                             'de Registro de Imóveis, e é o registro que passa a propriedade '
                                             'para o seu nome. Para saber se existe registro, peça a '
                                             'matrícula atualizada e veja se o vendedor aparece como dono.',
                                   'cuidados': ['Contrato de gaveta ou recibo não transferem a propriedade.',
                                                'Se o vendedor não aparece como dono na matrícula, pare e '
                                                'procure orientação antes de pagar.',
                                                'A escritura sozinha não prova que você é o dono: falta o '
                                                'registro.'],
                                   'leis': ['Código Civil (Lei 10.406/2002)',
                                            'Lei 6.015/1973 (Lei de Registros Públicos)',
                                            'Lei 8.935/1994 (Cartórios (notas e registro))'],
                                   'etapa': 'ESCRITURA'},
                                  {'titulo': 'Passos e custos da escritura e do registro',
                                   'resumo': 'Em geral os passos são: pagar o ITBI na prefeitura, reunir os '
                                             'documentos e as certidões, fazer a escritura no Tabelionato de '
                                             'Notas e levar a escritura ao Registro de Imóveis. As taxas de '
                                             'cartório (emolumentos) são tabeladas por cada estado e mudam '
                                             'conforme o valor do imóvel. Em alguns financiamentos o próprio '
                                             'contrato do banco substitui a escritura.',
                                   'cuidados': ['Consulte a tabela de emolumentos do Tribunal de Justiça do '
                                                'seu estado.',
                                                'Peça ao cartório uma lista de documentos antes de ir.',
                                                'Guarde todos os comprovantes de pagamento.'],
                                   'leis': ['Código Civil (Lei 10.406/2002)',
                                            'Lei 6.015/1973 (Lei de Registros Públicos)',
                                            'Lei 9.514/1997 (Alienação fiduciária de imóvel)'],
                                   'etapa': 'ESCRITURA'}]},
 'CONTRATO': {'nome': 'Contrato de compra e venda',
              'itens': [{'titulo': 'Contrato de compra e venda, sinal e desistência',
                         'resumo': 'Antes de assinar, leia o contrato inteiro. Confira os nomes, o número da '
                                   'matrícula, o preço, a forma de pagamento, o prazo, as multas e quem paga '
                                   'cada custo. O sinal (arras) é um adiantamento: pelo Código Civil, quem '
                                   'dá o sinal e desiste costuma perdê-lo, e quem recebe e desiste costuma '
                                   'devolver em dobro, salvo o que o contrato disser. A desistência depende '
                                   'do que está escrito no contrato.',
                         'cuidados': ['Não assine com pressa nem com páginas em branco.',
                                      'Peça cópia de tudo e guarde recibos de qualquer pagamento.',
                                      'Leve o contrato a um advogado ou à Defensoria antes de assinar.'],
                         'leis': ['Código Civil (Lei 10.406/2002)'],
                         'etapa': 'NEGOCIACAO_CONTRATO'}]},
 'FINANCIAMENTO': {'nome': 'Financiamento',
                   'itens': [{'titulo': 'Como funciona o financiamento habitacional',
                              'resumo': 'Você paga uma entrada e o banco financia o resto, em parcelas. O '
                                        'banco analisa sua renda, seu histórico de crédito e o imóvel. '
                                        'Muitos bancos limitam a parcela a cerca de 30% da renda, mas isso é '
                                        'regra do banco, não da lei. Nos financiamentos o próprio imóvel '
                                        'fica como garantia (alienação fiduciária): se as parcelas pararem, '
                                        'o imóvel pode ser retomado e leiloado.',
                              'cuidados': ['Simule em mais de um banco e compare o custo total (CET), não só '
                                           'a parcela.',
                                           'Informe só a renda real e comprovada.',
                                           'Pergunte sobre seguros e taxas.',
                                           'Confira se pode amortizar ou quitar antes do prazo.'],
                              'leis': ['Lei 9.514/1997 (Alienação fiduciária de imóvel)'],
                              'etapa': 'NEGOCIACAO_CONTRATO'}]},
 'FGTS_SUBSIDIOS': {'nome': 'FGTS e subsídios',
                    'itens': [{'titulo': 'FGTS e subsídios para a casa própria',
                               'resumo': 'O FGTS pode ajudar na entrada, nas parcelas ou na amortização, '
                                         'desde que as regras sejam cumpridas, por exemplo tempo de trabalho '
                                         'com FGTS e não ter outro financiamento ativo. O programa Minha '
                                         'Casa, Minha Vida tem faixas de renda e subsídio que mudam com o '
                                         'tempo. Confira as regras de hoje no banco que vai financiar.',
                               'cuidados': ['Confirme no app do FGTS e no banco se você atende aos '
                                            'requisitos.',
                                            'Faixas de renda e valores de subsídio mudam: não confie em '
                                            'informação antiga.',
                                            'Desconfie de quem cobra para liberar subsídio ou FGTS.'],
                               'leis': ['Lei 8.036/1990 (FGTS)',
                                        'Lei 14.620/2023 (Programa Minha Casa, Minha Vida)'],
                               'etapa': 'PESQUISA_IMOVEL'}]},
 'IMPOSTOS_TAXAS': {'nome': 'Impostos e taxas',
                    'itens': [{'titulo': 'ITBI, IPTU, ganho de capital e outros custos',
                               'resumo': 'O ITBI é o imposto da compra: é cobrado pela prefeitura, e a '
                                         'alíquota e as isenções mudam de cidade para cidade. Em geral quem '
                                         'compra paga, mas confira o contrato. IPTU e condomínio atrasados '
                                         'ficam ligados ao imóvel e podem ser cobrados do novo dono. Quem '
                                         'vende com lucro pode ter imposto de renda sobre o ganho de '
                                         'capital, e existem regras de isenção. Some também escritura, '
                                         'registro, avaliação do banco e seguros.',
                               'cuidados': ['Pergunte na prefeitura da cidade do imóvel o valor e as '
                                            'isenções do ITBI.',
                                            'Peça certidão negativa de IPTU e declaração do condomínio.',
                                            'Nunca confie em promessa de isenção sem conferir na fonte '
                                            'oficial.'],
                               'leis': ['Código Tributário Nacional (Lei 5.172/1966) (arts. 35 e 130)',
                                        'Lei 11.196/2005 (art. 39 (ganho de capital na venda de imóvel '
                                        'residencial))',
                                        'Código Civil (Lei 10.406/2002)'],
                               'etapa': 'ITBI_TRIBUTOS'}]},
 'LEILAO': {'nome': 'Leilão',
            'itens': [{'titulo': 'Comprar imóvel em leilão',
                       'resumo': 'Imóvel de leilão pode ter preço menor, mas tem riscos: pode estar ocupado, '
                                 'ter dívidas e ter regras de pagamento rígidas. As regras mudam conforme o '
                                 'tipo: leilão judicial, leilão do banco (alienação fiduciária) ou venda '
                                 'direta. Tudo vem no edital, que precisa ser lido por inteiro junto com a '
                                 'matrícula.',
                       'cuidados': ['Leia o edital e a matrícula antes de dar qualquer lance.',
                                    'Veja se o imóvel está ocupado e quem paga as dívidas.',
                                    'Pague só pelos canais oficiais do edital.',
                                    'Desconfie de leilão em site desconhecido ou com preço bom demais.'],
                       'leis': ['Lei 9.514/1997 (Alienação fiduciária de imóvel)',
                                'Código de Processo Civil (Lei 13.105/2015) (venda em leilão judicial)',
                                'Decreto 21.981/1932 (Leiloeiros)'],
                       'etapa': 'PESQUISA_IMOVEL'}]},
 'IMOVEL_USADO': {'nome': 'Imóvel usado',
                  'itens': [{'titulo': 'Checklist para comprar imóvel usado',
                             'resumo': 'Peça do vendedor documento de identidade, CPF, certidão de estado '
                                       'civil, certidões negativas, comprovante de IPTU em dia e declaração '
                                       'do condomínio. Peça a matrícula atualizada e confira se a construção '
                                       'está registrada. Se o vendedor é casado, em regra o cônjuge também '
                                       'precisa assinar. Se o dono faleceu, a venda depende do inventário.',
                             'cuidados': ['Visite o imóvel com calma e, se possível, leve alguém de '
                                          'confiança.',
                                          'Confira se a área real bate com a da matrícula.',
                                          'Pergunte sobre dívidas de condomínio.',
                                          'Em caso de inventário ou herança, procure um advogado antes de '
                                          'pagar.'],
                             'leis': ['Código Civil (Lei 10.406/2002)',
                                      'Lei 6.015/1973 (Lei de Registros Públicos)'],
                             'etapa': 'ANALISE_DOCUMENTAL'}]},
 'FRAUDE_GOLPES': {'nome': 'Fraudes e golpes',
                   'itens': [{'titulo': 'Fraude no financiamento: renda ou imposto de renda alterados',
                              'resumo': 'Informar renda falsa ou alterar o imposto de renda para conseguir '
                                        'financiamento pode ser crime, mesmo quando a ideia veio do '
                                        'corretor. Pode haver responsabilidade de quem assina e também '
                                        'consequências com a Receita Federal e com o banco. Desconfie de '
                                        'quem diz que faz acontecer com a sua renda.',
                              'cuidados': ['Não assine documento que você não entende ou com campo em '
                                           'branco.',
                                           'Se algo assim já aconteceu, procure um advogado ou a Defensoria '
                                           'antes de qualquer iniciativa por conta própria.',
                                           'Guarde mensagens e documentos que mostram o que foi combinado.',
                                           'Use sempre a renda real.'],
                              'leis': ['Lei 7.492/1986 (art. 19 (fraude para obter financiamento))',
                                       'Código Penal (Decreto-Lei 2.848/1940) (arts. 171 e 299)'],
                              'etapa': 'NEGOCIACAO_CONTRATO'},
                             {'titulo': 'Golpes na compra: anúncio, PIX e boleto',
                              'resumo': 'Sinais de golpe: preço muito abaixo do mercado, pressa para pagar, '
                                        'sinal por PIX antes de ver o imóvel e o contrato, vendedor que não '
                                        'mostra a matrícula e boleto com nome diferente do vendedor. Para se '
                                        'proteger, confira a matrícula e a identidade do dono e pague '
                                        'somente depois de conferir tudo.',
                              'cuidados': ['Não pague nada antes de ver o imóvel e a matrícula.',
                                           'Confira o nome do dono na matrícula e no pagamento.',
                                           'Em caso de golpe, registre boletim de ocorrência e avise o '
                                           'banco.'],
                              'leis': ['Código Penal (Decreto-Lei 2.848/1940) (arts. 171 e 299)',
                                       'Lei 6.015/1973 (Lei de Registros Públicos)'],
                              'etapa': 'ANALISE_DOCUMENTAL'}]}}

ETAPAS = {'PESQUISA_IMOVEL': {'ordem': 1,
                     'nome': 'Pesquisa e escolha do imóvel',
                     'descricao': 'Defina quanto pode pagar, simule o financiamento e visite os imóveis.',
                     'documentos': ['Documento de identidade e CPF', 'Comprovante de renda'],
                     'cuidados': ['Compare preços', 'Não pague nada antes de conferir os documentos']},
 'ANALISE_DOCUMENTAL': {'ordem': 2,
                        'nome': 'Análise documental',
                        'descricao': 'Confira a matrícula, as certidões e as dívidas antes de fechar '
                                     'negócio.',
                        'documentos': ['Matrícula atualizada',
                                       'Certidão de ônus reais',
                                       'Certidões do vendedor',
                                       'IPTU e condomínio em dia'],
                        'cuidados': ['Documentos recentes', 'Nome do dono igual ao do vendedor']},
 'NEGOCIACAO_CONTRATO': {'ordem': 3,
                         'nome': 'Negociação e contrato',
                         'descricao': 'Combine preço e forma de pagamento e leia o contrato inteiro antes de '
                                      'assinar.',
                         'documentos': ['Minuta do contrato', 'Comprovantes de sinal'],
                         'cuidados': ['Não assine com pressa', 'Guarde cópia de tudo']},
 'ESCRITURA': {'ordem': 4,
               'nome': 'Escritura ou instrumento aplicável',
               'descricao': 'Feita no Tabelionato de Notas, ou pelo contrato do banco quando o financiamento '
                            'permitir.',
               'documentos': ['Documentos pessoais', 'Certidões', 'Comprovante de ITBI'],
               'cuidados': ['Veja a tabela de emolumentos do estado']},
 'ITBI_TRIBUTOS': {'ordem': 5,
                   'nome': 'ITBI e tributos',
                   'descricao': 'Pague o ITBI na prefeitura e confira IPTU e condomínio.',
                   'documentos': ['Guia de ITBI paga'],
                   'cuidados': ['Valor e isenções mudam por cidade']},
 'REGISTRO_IMOVEL': {'ordem': 6,
                     'nome': 'Registro imobiliário',
                     'descricao': 'Leve a escritura ao Registro de Imóveis: o registro passa o imóvel para o '
                                  'seu nome.',
                     'documentos': ['Escritura', 'Comprovante de ITBI'],
                     'cuidados': ['Acompanhe o pedido e atenda a nota devolutiva, se houver']}}
