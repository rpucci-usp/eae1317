#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Gera os diagramas da aula 07 (Permissoes Negociaveis e Subsidios).

Como figuras05svg.py e figuras06svg.py, este script IMPORTA Painel, Tela e as
cores de figuras04svg.py. A razao e a mesma da aula 06, e aqui ela e ainda mais
forte: a economia desenhada e literalmente a mesma desde a aula 04, e o assunto
da aula e que tres instrumentos diferentes devolvem a MESMA alocacao.

    CMg_1(e1) = 100 - e1          C_1(e1) = (100 - e1)^2 / 2
    CMg_2(e2) =  50 - 0,5 e2      C_2(e2) = (100 - e2)^2 / 4
    D'(E)     = 0,2 E             D(E)    = 0,1 E^2

    otimo:            mu* = 25, e1* = 75, e2* = 50, E* = 125
    dotacao inicial:  e-barra = E*/2 = 62,5 nas duas firmas (o padrao uniforme
                      da aula 06, agora com direito de venda)
    preco da permissao: sigma* = tau* = mu* = 25

O que a aula 06 desenhou como uma realocacao HIPOTETICA (as areas B e C de
06-padrao-3, cujo saldo de 117,2 era peso morto) esta aula desenha como troca
REALIZADA: a firma 1 compra 12,5 permissoes da firma 2 por 312,5, e os dois
ganhos somam os mesmos 117,2. O assert no fim da secao de parametros existe
para que esse numero nao possa sair de sincronia em silencio.

O bloco de subsidios acrescenta um parametro novo, e so um: o nivel de
referencia comum E_REF, usado nas duas ultimas figuras. Ele nao e escolhido por
gosto — a faixa em que a firma 2 fica no programa e a firma 1 sai e calculada
abaixo, e o assert confere que 80 cai dentro dela.

Depende so da biblioteca padrao, como os outros scripts desta pasta.

    py scripts/figuras07svg.py

Escreve em aulas/_assets/figuras/.
"""

from figuras04svg import (Painel, Tela, COR_CMG, COR_DANO, COR_EIXO,
                          COR_GUIA, COR_APAGADA, COR_DESTAQUE, SUB1, SUB2,
                          FONTE, FONTE_LEGENDA)

# --- a economia desenhada (identica a das aulas 04 e 06) --------------------
E_CHAPEU = 100.0
C1 = 1.0
C2 = 0.5
D = 0.2

SIGMA = 25.0                     # o preco da permissao, que e o tau* da aula 06
E1 = E_CHAPEU - SIGMA / C1       # 75
E2 = E_CHAPEU - SIGMA / C2       # 50
E_TOT = E1 + E2                  # 125 — a oferta L de permissoes
E_BARRA = E_TOT / 2              # 62,5 — a dotacao inicial, igual para as duas

cmg1 = lambda e: C1 * (E_CHAPEU - e)
cmg2 = lambda e: C2 * (E_CHAPEU - e)
dano_mg = lambda e: D * e
custo1 = lambda e: (E_CHAPEU - e) ** 2 / 2
custo2 = lambda e: (E_CHAPEU - e) ** 2 / 4

QTD = E1 - E_BARRA               # 12,5 permissoes trocadas
PAGO = SIGMA * QTD               # 312,5 — o que a firma 1 paga e a firma 2 recebe

# A decomposicao das areas, com as letras do .pptx em maiuscula (as minusculas
# de la colidem com a variavel de emissao, o mesmo motivo ja registrado na
# aula 06). A = abatimento da firma 1 sob o preco; B = o retangulo que ela paga
# pelas permissoes; C = o que sobra do que ela estaria disposta a pagar, ou
# seja, o ganho dela. Do outro lado, D_ = abatimento que a firma 2 faria de
# qualquer jeito, E_ = abatimento extra que ela assume ao vender, F = o ganho.
A_ = custo1(E1)                                  # 312,5
B_ = PAGO                                        # 312,5
C_ = custo1(E_BARRA) - custo1(E1) - PAGO         # 78,125
D_ = custo2(E_BARRA)                             # 351,5625
E_ = custo2(E2) - custo2(E_BARRA)                # 273,4375
F_ = PAGO - E_                                   # 39,0625

GANHO = C_ + F_                                  # 117,1875

# Confere a algebra em vez de confiar nos numeros dos comentarios.
assert abs(D * E_TOT - SIGMA) < 1e-9, "sigma* nao satisfaz D'(E*) = sigma*"
assert abs(cmg1(E1) - cmg2(E2)) < 1e-9, "as duas firmas nao igualam CMg no otimo"
# O que a firma 1 compra e o que a firma 2 vende: o mercado tem que fechar.
assert abs((E1 - E_BARRA) - (E_BARRA - E2)) < 1e-9, "o mercado de permissoes nao fecha"
# A identidade que o .pptx enuncia como "sabendo que b = e + f".
assert abs(B_ - (E_ + F_)) < 1e-9, "B nao e igual a E + F"
# A ponte com a aula 06: o ganho da troca e o peso morto do padrao uniforme, e
# os dois presets do widget da aula 04 continuam valendo.
SC_UNIF = custo1(E_BARRA) + custo2(E_BARRA) + 0.1 * E_TOT ** 2
SC_OTIMO = custo1(E1) + custo2(E2) + 0.1 * E_TOT ** 2
assert abs(GANHO - 117.1875) < 1e-6, "o ganho da troca mudou"
assert abs(SC_UNIF - SC_OTIMO - GANHO) < 1e-6, "o ganho nao fecha com o custo social"
assert round(SC_UNIF) == 2617 and round(SC_OTIMO) == 2500, \
    "os presets do widget da aula 04 sairam de sincronia"
# A arrecadacao do leilao das mesmas L permissoes e a do imposto da aula 06.
assert abs(SIGMA * E_TOT - 3125.0) < 1e-9, "a arrecadacao do leilao mudou"

# --- o bloco de subsidios ---------------------------------------------------
# Com referencia individual, a firma recebe psi por unidade abatida abaixo do
# proprio nivel nao regulado. A alocacao e a mesma do imposto (a CPO e a mesma),
# e o que muda e o sinal do fluxo de dinheiro.
PSI = SIGMA
SUB1_IND = PSI * (E_CHAPEU - E1)                 # 625 — recebido pela firma 1
SUB2_IND = PSI * (E_CHAPEU - E2)                 # 1.250 — recebido pela firma 2

# Com referencia COMUM, participar deixa de ser vantajoso para quem teria de
# abater muito para chegar la. A firma j participa se o subsidio liquido no
# proprio otimo for positivo:  psi * (E_REF - e_j*) - C_j(e_j*) >= 0, ou seja
#     E_REF >= e_j* + C_j(e_j*) / psi
# Abaixo, os dois limiares. Entre eles, a firma 2 fica e a firma 1 sai — que e
# exatamente o caso que o .pptx desenha.
LIMIAR_1 = E1 + custo1(E1) / PSI                 # 87,5
LIMIAR_2 = E2 + custo2(E2) / PSI                 # 75,0
E_REF = 80.0

assert LIMIAR_2 < E_REF < LIMIAR_1, \
    "E_REF precisa ficar entre os dois limiares, senao as duas firmas decidem igual"

SUB2_COM = PSI * (E_REF - E2)                    # 750 — recebido pela firma 2
LIQ_2_COM = SUB2_COM - custo2(E2)                # 125 — ganho liquido dela
E_TOT_COM = E_CHAPEU + E2                        # 150 — a firma 1 volta a ê

assert LIQ_2_COM > 0, "a firma 2 deveria continuar no programa"
assert E_TOT_COM > E_TOT, "a referencia comum deveria estragar a alocacao"

# --- geometria (a mesma da aula 06) ----------------------------------------
LARG_2P = 440
X_MAX = 115
X_MAX_AGR = 215
Y_MAX = 108
FOLGA_DIR = 16
Y_SETA = 46          # altura unica das setas, pelo motivo registrado na aula 06

# A familia de dois paineis do bloco de leilao e mais larga porque cada painel
# carrega a curva agregada inteira (ate E-chapeu = 200), e nao uma firma so.
LARG_LEILAO = 470
ALT_LEILAO = 340


def fmt(v):
    """Numero em portugues, sem casa decimal sobrando."""
    inteiro, _, dec = "{:.4f}".format(v).partition(".")
    dec = dec.rstrip("0")
    milhar = "{:,}".format(int(inteiro)).replace(",", ".")
    return milhar + ("," + dec if dec else "")


def duas_firmas():
    """A moldura comum das figuras de duas firmas, identica a da aula 06.

    Os dois paineis dividem a MESMA escala vertical, o que aqui e o proprio
    assunto: sob o preco unico da permissao as duas alturas coincidem, e e por
    isso que a horizontal de sigma* pode atravessar a figura inteira.
    """
    t = Tela(2 * LARG_2P + FOLGA_DIR, Painel.ALT + 30)
    p1 = Painel(t, 0, LARG_2P, (0, X_MAX), (0, Y_MAX))
    p2 = Painel(t, LARG_2P, LARG_2P, (0, X_MAX), (0, Y_MAX))

    p1.titulo("Firma 1 (custo alto)")
    p2.titulo("Firma 2 (custo baixo)")
    p1.eixos("e" + SUB1, "CMg" + SUB1)
    p2.eixos("e" + SUB2, "CMg" + SUB2)

    p1.reta(0, cmg1(0), E_CHAPEU, 0, cor=COR_CMG)
    p2.reta(0, cmg2(0), E_CHAPEU, 0, cor=COR_CMG)
    p1.marca_x(E_CHAPEU, "ê" + SUB1)
    p2.marca_x(E_CHAPEU, "ê" + SUB2)
    return t, p1, p2


def rodape(t, texto, cor=COR_DESTAQUE, larg=None):
    larg = larg if larg is not None else 2 * LARG_2P + FOLGA_DIR
    t.texto(larg / 2, Painel.ALT + 20, texto, ancora="middle", tam=FONTE_LEGENDA,
            cor=cor, negrito=True)


def dotacao(p):
    """A vertical tracejada na dotacao inicial, identica nos dois paineis."""
    p.reta(E_BARRA, 0, E_BARRA, Y_MAX - 12, cor=COR_GUIA, larg=1.1,
           tracejado="4 3")
    p.marca_x(E_BARRA, "ē", cor=COR_DESTAQUE)


def linha_sigma(t, p_esq, p_dir, rotulo="σ*"):
    """A horizontal de sigma* atravessando os dois paineis.

    E honesta pelo mesmo motivo da figura do imposto da aula 06: sob o preco
    unico as duas alturas SAO o mesmo numero, e a escala vertical e comum.
    """
    y = p_esq.py(SIGMA)
    t.add('<line x1="{:.1f}" y1="{:.1f}" x2="{:.1f}" y2="{:.1f}"'
          ' stroke="{}" stroke-width="1.6" stroke-dasharray="7 4"/>'
          .format(p_esq.px(0) - 4, y, p_dir.px(X_MAX), y, COR_DESTAQUE))
    p_esq.marca_y(SIGMA, rotulo, cor=COR_DESTAQUE)


def seta(p, xa, xb, y, cor=COR_DESTAQUE):
    pa, pb = p.p(xa, y), p.p(xb, y)
    p.t.add('<line x1="{:.1f}" y1="{:.1f}" x2="{:.1f}" y2="{:.1f}"'
            ' stroke="{}" stroke-width="1.8" marker-end="url(#seta)"/>'
            .format(pa[0], pa[1], pb[0], pb[1], cor))


# ---------------------------------------------------------------------------
# 1. o leilao: escolher o preco e escolher a quantidade sao o mesmo ato
# ---------------------------------------------------------------------------

def cmg_agregado(E):
    """Inversa da soma horizontal e_1(sigma) + e_2(sigma).

    A mesma funcao de 06-agregado, com o bico em (50, 50): acima de 50 a firma
    2 ja zerou a emissao e so a firma 1 responde. Repetida aqui em vez de
    importada porque a aula 06 a define no proprio arquivo, e a aula 07 precisa
    dela para desenhar o mesmo ponto por outro caminho.
    """
    return 100.0 - E if E <= 50.0 else (200.0 - E) / 3.0


assert abs(cmg_agregado(E_TOT) - SIGMA) < 1e-9, "a agregada nao passa por (E*, sigma*)"


def painel_agregado(t, x_off, titulo):
    p = Painel(t, x_off, LARG_LEILAO, (0, X_MAX_AGR), (0, Y_MAX), ALT_LEILAO)
    p.titulo(titulo)
    p.eixos("E", "preço da poluição")
    p.curva(cmg_agregado, 0, 2 * E_CHAPEU, cor=COR_CMG, n=200)
    p.texto(2 * E_CHAPEU - 30, cmg_agregado(2 * E_CHAPEU - 30) + 9, "E(σ)",
            cor=COR_CMG, negrito=True, ancora="end")
    p.reta(0, 0, X_MAX_AGR, dano_mg(X_MAX_AGR), cor=COR_DANO)
    p.texto(X_MAX_AGR - 6, dano_mg(X_MAX_AGR) + 6, "D′(E)", cor=COR_DANO,
            negrito=True, ancora="end")
    p.marca_x(2 * E_CHAPEU, "Ê")
    return p


def figura_leilao():
    """Os dois paineis mostram a MESMA curva e o MESMO ponto.

    A diferenca esta em qual eixo o regulador toca: no da esquerda ele fixa a
    altura e le a quantidade; no da direita ele fixa a quantidade e le a
    altura. As setas comecam no que e escolhido e terminam no que e obtido, e
    e so isso que separa imposto de leilao neste modelo.
    """
    t = Tela(2 * LARG_LEILAO + FOLGA_DIR, ALT_LEILAO + 44)
    p_tau = painel_agregado(t, 0, "Imposto: o regulador escolhe a altura")
    p_lei = painel_agregado(t, LARG_LEILAO, "Leilão: o regulador escolhe a largura")

    # Esquerda: a aliquota entra pelo eixo vertical e a emissao sai no fim.
    p_tau.reta(0, SIGMA, E_TOT, SIGMA, cor=COR_DESTAQUE, larg=1.6,
               tracejado="7 4")
    p_tau.marca_y(SIGMA, "τ*", cor=COR_DESTAQUE)
    p_tau.reta(E_TOT, 0, E_TOT, SIGMA, cor=COR_GUIA, larg=1.1, tracejado="4 3")
    p_tau.ponto(E_TOT, SIGMA)
    p_tau.marca_x(E_TOT, "E(τ*)", cor=COR_DESTAQUE)
    seta(p_tau, 6, E_TOT - 8, SIGMA + 13)

    # Direita: a oferta entra pelo eixo horizontal e o preco sai no fim.
    p_lei.reta(E_TOT, 0, E_TOT, Y_MAX - 12, cor=COR_DESTAQUE, larg=2.0)
    p_lei.texto(E_TOT + 6, Y_MAX - 16, "oferta L", cor=COR_DESTAQUE,
                negrito=True, italico=False, tam=FONTE)
    p_lei.reta(0, SIGMA, E_TOT, SIGMA, cor=COR_GUIA, larg=1.1, tracejado="4 3")
    p_lei.marca_y(SIGMA, "σ*", cor=COR_DESTAQUE)
    p_lei.ponto(E_TOT, SIGMA)
    p_lei.marca_x(E_TOT, "L", cor=COR_DESTAQUE)

    t.texto((2 * LARG_LEILAO + FOLGA_DIR) / 2, ALT_LEILAO + 30,
            "com L = E* = 125, o leilão devolve σ* = 25, que é a alíquota da"
            " aula passada", ancora="middle", tam=FONTE_LEGENDA, cor=COR_DESTAQUE,
            negrito=True)
    return t


# ---------------------------------------------------------------------------
# 2. quem compra e quem vende
# ---------------------------------------------------------------------------

def figura_permissoes_1():
    t, p1, p2 = duas_firmas()
    for p in (p1, p2):
        dotacao(p)
    linha_sigma(t, p1, p2)

    for p, e_est, sub in ((p1, E1, SUB1), (p2, E2, SUB2)):
        p.reta(e_est, 0, e_est, SIGMA, cor=COR_GUIA, larg=1.1, tracejado="4 3")
        p.ponto(e_est, SIGMA)
        p.marca_x(e_est, "e" + sub + "*", cor=COR_DESTAQUE)

    # A firma 1 anda para a direita (emite mais do que a dotacao: compra) e a
    # firma 2 para a esquerda (emite menos: vende). As duas setas na mesma
    # altura, pelo motivo ja registrado na aula 06.
    seta(p1, E_BARRA, E1, Y_SETA)
    seta(p2, E_BARRA, E2, Y_SETA)
    p1.texto(0.5 * (E_BARRA + E1), Y_SETA + 12, "compra 12,5", cor=COR_DESTAQUE,
             negrito=True, italico=False, tam=FONTE, ancora="middle")
    p2.texto(0.5 * (E2 + E_BARRA), Y_SETA + 12, "vende 12,5", cor=COR_DESTAQUE,
             negrito=True, italico=False, tam=FONTE, ancora="middle")

    rodape(t, "ninguém disse quanto cada uma corta: as duas param onde"
              " CMg = σ*, e a emissão total continua L = 125")
    return t


# ---------------------------------------------------------------------------
# 3. as areas: o que cada uma gasta, paga e recebe
# ---------------------------------------------------------------------------

def _areas_permissoes(p1, p2, apagar=False):
    """As seis areas do slide 47 do .pptx, com as letras em maiuscula.

    Quando `apagar` esta ligado, tudo o que nao e ganho sai em cinza: a figura
    seguinte e esta mesma, com C e F acesos.
    """
    cor_ab = COR_APAGADA if apagar else COR_CMG
    cor_pg = COR_APAGADA if apagar else COR_DANO
    op = 0.55 if apagar else 0.80

    # Firma 1: A = abatimento que ela ainda faz; B = o retangulo que ela paga
    # pelas 12,5 permissoes; C = o que sobra da disposicao a pagar, o ganho.
    p1.area([(E1, 0), (E_CHAPEU, 0), (E1, cmg1(E1))], cor_ab, op)
    p1.area([(E_BARRA, 0), (E1, 0), (E1, SIGMA), (E_BARRA, SIGMA)], cor_pg, 0.45)
    p1.area([(E_BARRA, SIGMA), (E1, SIGMA), (E_BARRA, cmg1(E_BARRA))],
            COR_DESTAQUE, 0.30 if not apagar else 0.55)

    # Firma 2: D = o abatimento que ela faria de qualquer jeito sob a dotacao;
    # E = o abatimento extra que ela assume para poder vender; F = o ganho.
    p2.area([(E_BARRA, 0), (E_CHAPEU, 0), (E_BARRA, cmg2(E_BARRA))], cor_ab, op)
    p2.area([(E2, 0), (E_BARRA, 0), (E_BARRA, cmg2(E_BARRA)), (E2, cmg2(E2))],
            cor_ab, 0.45 if not apagar else 0.35)
    p2.area([(E2, cmg2(E2)), (E_BARRA, cmg2(E_BARRA)), (E_BARRA, SIGMA)],
            COR_DESTAQUE, 0.30 if not apagar else 0.55)


def figura_permissoes_2():
    t, p1, p2 = duas_firmas()
    for p in (p1, p2):
        dotacao(p)
    _areas_permissoes(p1, p2)
    linha_sigma(t, p1, p2)

    for p, e_est, sub in ((p1, E1, SUB1), (p2, E2, SUB2)):
        p.reta(e_est, 0, e_est, SIGMA, cor=COR_GUIA, larg=1.1, tracejado="4 3")
        p.marca_x(e_est, "e" + sub + "*", cor=COR_DESTAQUE)

    # A e D vao no centroide do proprio triangulo, com ancora "middle": posto
    # a partir da borda esquerda, o rotulo branco escorrega para fora da
    # hipotenusa pela direita e some (branco sobre branco, sem aviso). E o
    # mesmo erro ja registrado em figuras04svg.py, e ele reapareceu aqui.
    p1.texto(82, 5.5, "A", cor="#ffffff", negrito=True, tam=16, halo=False,
             ancora="middle")
    p1.texto(0.5 * (E_BARRA + E1), SIGMA * 0.42, "B", cor=COR_EIXO,
             negrito=True, tam=16)
    p1.texto(E_BARRA + 3.4, SIGMA + 6.5, "C", cor=COR_DESTAQUE, negrito=True,
             tam=FONTE, ancora="middle")
    p2.texto(71, 4.5, "D", cor="#ffffff", negrito=True, tam=16, halo=False,
             ancora="middle")
    p2.texto(0.5 * (E2 + E_BARRA), cmg2(E_BARRA) * 0.40, "E", cor="#ffffff",
             negrito=True, tam=16, halo=False)
    p2.texto(0.5 * (E2 + E_BARRA), SIGMA + 3.2, "F", cor=COR_DESTAQUE,
             negrito=True, tam=FONTE, ancora="middle")

    rodape(t, "a firma 1 paga B = 312,5 e a firma 2 recebe E + F = 312,5:"
              " é a mesma quantia, e nada disso vai para o governo")
    return t


def figura_permissoes_3():
    t, p1, p2 = duas_firmas()
    for p in (p1, p2):
        dotacao(p)
    _areas_permissoes(p1, p2, apagar=True)
    linha_sigma(t, p1, p2)

    for p, e_est, sub in ((p1, E1, SUB1), (p2, E2, SUB2)):
        p.marca_x(e_est, "e" + sub + "*", cor=COR_DESTAQUE)

    p1.texto(E_BARRA + 3.4, SIGMA + 6.5, "C", cor=COR_DESTAQUE, negrito=True,
             tam=FONTE, ancora="middle")
    p2.texto(0.5 * (E2 + E_BARRA), SIGMA + 3.2, "F", cor=COR_DESTAQUE,
             negrito=True, tam=FONTE, ancora="middle")

    rodape(t, "C + F = {} é o que a troca poupa, e é o peso morto que o padrão"
              " uniforme deixava na mesa".format(fmt(round(GANHO, 1))))
    return t


# ---------------------------------------------------------------------------
# 4. subsidio com referencia individual: a mesma alocacao do imposto
# ---------------------------------------------------------------------------

def figura_subsidio_1():
    t, p1, p2 = duas_firmas()
    linha_sigma(t, p1, p2, rotulo="ψ")

    for p, e_est, cmg, sub in ((p1, E1, cmg1, SUB1), (p2, E2, cmg2, SUB2)):
        # O retangulo inteiro e o que a firma recebe; a parte sob a curva e o
        # que ela gasta abatendo, e a de cima e o que sobra no bolso dela.
        p.area([(e_est, 0), (E_CHAPEU, 0), (E_CHAPEU, PSI), (e_est, PSI)],
               COR_DANO, 0.30)
        p.area([(e_est, 0), (E_CHAPEU, 0), (e_est, cmg(e_est))], COR_CMG, 0.80)
        p.reta(e_est, 0, e_est, PSI, cor=COR_GUIA, larg=1.1, tracejado="4 3")
        p.ponto(e_est, PSI)
        p.marca_x(e_est, "e" + sub + "*", cor=COR_DESTAQUE)

    p1.texto(E1 + 11, cmg1(E1) * 0.28, "abate", cor="#ffffff", negrito=True,
             tam=FONTE, halo=False, italico=False)
    p2.texto(E2 + 15, cmg2(E2) * 0.30, "abate", cor="#ffffff", negrito=True,
             tam=FONTE, halo=False, italico=False)
    p1.texto(0.5 * (E1 + E_CHAPEU), PSI + 7, "recebe 625", cor=COR_DESTAQUE,
             negrito=True, tam=FONTE, ancora="middle", italico=False)
    p2.texto(0.5 * (E2 + E_CHAPEU), PSI + 7, "recebe 1.250", cor=COR_DESTAQUE,
             negrito=True, tam=FONTE, ancora="middle", italico=False)

    rodape(t, "com ψ = 25 e referência ê, as duas param em e* de novo:"
              " o dinheiro é que anda ao contrário")
    return t


# ---------------------------------------------------------------------------
# 5. subsidio com referencia comum: a firma 1 sai do programa
# ---------------------------------------------------------------------------

def figura_subsidio_2():
    t, p1, p2 = duas_firmas()
    linha_sigma(t, p1, p2, rotulo="ψ")

    for p in (p1, p2):
        p.reta(E_REF, 0, E_REF, Y_MAX - 12, cor=COR_GUIA, larg=1.1,
               tracejado="4 3")
        p.marca_x(E_REF, "ē", cor=COR_DESTAQUE)

    # Firma 1: para receber alguma coisa teria de abater ate abaixo de e-barra,
    # e o triangulo de custo que isso exige e maior que o retangulo oferecido.
    # Ela fica fora, e volta a emitir e-chapeu.
    p1.area([(E_REF, 0), (E_CHAPEU, 0), (E_REF, cmg1(E_REF))], COR_CMG, 0.80)
    p1.ponto(E_CHAPEU, 0, cor=COR_CMG)
    p1.texto(E_CHAPEU - 4, 9, "fica em ê" + SUB1, cor=COR_CMG, negrito=True,
             tam=FONTE, ancora="end", italico=False)

    # Firma 2: a referencia comum ainda esta acima do otimo dela, entao ela
    # continua no programa e recebe o retangulo maior.
    p2.area([(E2, 0), (E_REF, 0), (E_REF, PSI), (E2, PSI)], COR_DANO, 0.30)
    p2.area([(E2, 0), (E_CHAPEU, 0), (E2, cmg2(E2))], COR_CMG, 0.80)
    p2.reta(E2, 0, E2, PSI, cor=COR_GUIA, larg=1.1, tracejado="4 3")
    p2.ponto(E2, PSI)
    p2.marca_x(E2, "e" + SUB2 + "*", cor=COR_DESTAQUE)
    p2.texto(0.5 * (E2 + E_REF), PSI + 7, "recebe 750", cor=COR_DESTAQUE,
             negrito=True, tam=FONTE, ancora="middle", italico=False)

    rodape(t, "referência comum ē = 80: a firma 1 sai do programa e a emissão"
              " total sobe de 125 para 150", cor=COR_CMG)
    return t


# ---------------------------------------------------------------------------
# 6. o leilao do exercicio: o preco sai das ofertas, e nao do regulador
# ---------------------------------------------------------------------------
# As duas usinas do exercicio em duplas, com os mesmos blocos das aulas 04 e 06.
# A disposicao a pagar pela k-esima permissao e o custo do bloco que ela
# dispensa, do mais caro para o mais barato: com k permissoes a usina emite 10k
# e corta os (5 - k) blocos mais baratos.
BLOCOS_A = [10, 20, 30, 40, 50]
BLOCOS_B = [20, 40, 60, 80, 100]
L_EX = 4                                  # permissoes leiloadas
DANO_MG_EX = 45                           # por bloco de 10 t emitido

# ordenadas da maior para a menor, que e como o leiloeiro as ve
LANCES = sorted([(v, "A") for v in BLOCOS_A] + [(v, "B") for v in BLOCOS_B],
                reverse=True)

# O preco nao e um numero: e a faixa entre a maior oferta perdedora e a menor
# vencedora. Com blocos discretos essa faixa tem largura, e e justamente isso
# que a figura precisa mostrar.
P_MIN = LANCES[L_EX][0]                   # 40, a maior oferta que perde
P_MAX = LANCES[L_EX - 1][0]               # 50, a menor oferta que ganha

VENCE_A = sum(1 for _, d in LANCES[:L_EX] if d == "A")
VENCE_B = L_EX - VENCE_A

assert (VENCE_A, VENCE_B) == (1, 3), "o leilao deixou de dar 1 para A e 3 para B"
assert P_MIN < DANO_MG_EX < P_MAX, \
    "o dano marginal deveria cair dentro da faixa que o leilao produz"
# A alocacao do leilao tem que ser a mesma do corte eficiente das aulas 04 e 06:
# A corta 4 blocos (100) e B corta 2 (60), somando 160.
assert sum(BLOCOS_A[:5 - VENCE_A]) + sum(BLOCOS_B[:5 - VENCE_B]) == 160, \
    "o leilao deixou de reproduzir o corte eficiente"

LARG_EX = 780
ALT_EX = 344
# O rotulo do eixo horizontal aqui e "permissoes", que tem ~85px na fonte da
# figura, contra os ~14px do "E" da aula 04. O Painel.eixos() o escreve 16px
# depois do fim do eixo com ancora "start", entao sem folga ele sai cortado
# pela borda do viewBox. Mesmo problema que FOLGA_DIR resolve na aula 06, com
# uma folga bem maior porque a palavra e bem mais larga.
FOLGA_EX = 92


def figura_exercicio():
    """A escada de ofertas cruzando a oferta fixa de permissoes.

    Existe para desfazer uma leitura errada: o governo NAO escolhe o preco do
    leilao. Ele escolhe L, que e a vertical; o preco e onde a escada cruza essa
    vertical, e sai do lance das proprias usinas.

    Com lances discretos a escada tem um degrau exatamente em L, entao o
    cruzamento e um SEGMENTO e nao um ponto: qualquer valor entre a maior
    oferta perdedora e a menor vencedora limpa o mercado. Desenhar um ponto ali
    seria desenhar uma precisao que o modelo nao tem.
    """
    t = Tela(LARG_EX + FOLGA_EX, ALT_EX + 46)
    p = Painel(t, 0, LARG_EX, (0, 10.6), (0, 112), ALT_EX)
    p.titulo("As dez ofertas, da maior para a menor")
    p.eixos("permissões", "R$ mil por permissão")

    # a escada de demanda
    for k, (v, _) in enumerate(LANCES):
        p.reta(k, v, k + 1, v, cor=COR_CMG, larg=2.4)
        if k + 1 < len(LANCES):
            p.reta(k + 1, v, k + 1, LANCES[k + 1][0], cor=COR_CMG, larg=1.2)

    # de quem e cada oferta vencedora
    for k in range(L_EX):
        v, dono = LANCES[k]
        p.texto(k + 0.5, v + 4.5, dono, cor=COR_CMG, negrito=True, tam=FONTE,
                ancora="middle")

    # o dano marginal, que e o que diz ao governo quantas permissoes emitir.
    # Fica atras da escada, em azul de dano, e o rodape avisa que ele nao e o
    # preco: e o criterio que escolheu L.
    p.reta(0, DANO_MG_EX, 10.6, DANO_MG_EX, cor=COR_DANO, larg=1.4,
           tracejado="6 4")
    p.texto(10.4, DANO_MG_EX + 5, "D′ = 45", cor=COR_DANO, negrito=True,
            tam=FONTE, ancora="end")

    # a oferta: a unica coisa que o governo escolhe
    p.reta(L_EX, 0, L_EX, 106, cor=COR_DESTAQUE, larg=2.0)
    p.texto(L_EX + 0.15, 102, "oferta L = 4", cor=COR_DESTAQUE, negrito=True,
            tam=FONTE, italico=False)

    # o cruzamento, que e um segmento
    p.area([(3.86, P_MIN), (4.14, P_MIN), (4.14, P_MAX), (3.86, P_MAX)],
           COR_DESTAQUE, 0.55)
    p.marca_y(P_MAX, fmt(P_MAX), cor=COR_DESTAQUE)
    p.marca_y(P_MIN, fmt(P_MIN), cor=COR_DESTAQUE)
    p.texto(4.35, 0.5 * (P_MIN + P_MAX), "o preço fecha aqui",
            cor=COR_DESTAQUE, negrito=True, tam=FONTE, italico=False)

    t.texto(LARG_EX / 2, ALT_EX + 32,
            "o governo escolheu a vertical; a altura veio dos lances das duas"
            " usinas", ancora="middle", tam=FONTE_LEGENDA, cor=COR_DESTAQUE, negrito=True)
    return t


# ---------------------------------------------------------------------------
# 7. custo de transacao: por que a dotacao volta a importar
# ---------------------------------------------------------------------------
# Serve ao bloco de discussao que segue o exemplo do EU ETS. O resultado de
# Zaklan (2023) e que a independencia vale para os grandes emissores e falha
# para os pequenos, e a hipotese dele e custo de transacao. Esta figura mostra
# o mecanismo dentro do modelo da aula.
#
# Com custo k por unidade transacionada, o preco relevante deixa de ser um so:
# quem compra paga sigma + k, quem vende recebe sigma - k, e entre os dois ha
# uma FAIXA de dotacoes em que nao vale a pena fazer nem uma coisa nem outra.
# Dentro dessa faixa a emissao E a dotacao, ou seja, a dotacao volta para
# dentro da condicao de primeira ordem.
#
# Os dois paineis usam a MESMA curva de abatimento de proposito: a unica coisa
# diferente entre eles e k, senao a figura mediria duas coisas ao mesmo tempo.
A_CT = 50.0          # CMg(e) = A_CT - B_CT * e, a mesma curva da firma 2
B_CT = 0.5
K_GRANDE = 1.0       # emissor grande: custo de transacao baixo
K_PEQUENO = 5.0      # emissor pequeno: custo de transacao alto
E_DOT_CT = 56.0      # a dotacao gratuita, igual nos dois paineis

cmg_ct = lambda e: A_CT - B_CT * e
# quem compra para em CMg = sigma + k; quem vende para em CMg = sigma - k
e_compra = lambda k: (A_CT - (SIGMA + k)) / B_CT
e_vende = lambda k: (A_CT - (SIGMA - k)) / B_CT

# Sem atrito a faixa colapsa num ponto e a dotacao some, que e o resultado do
# resto da aula.
assert abs(e_compra(0.0) - e_vende(0.0)) < 1e-9, "sem k a faixa deveria ser um ponto"
assert abs(e_compra(0.0) - 50.0) < 1e-9, "o otimo sem atrito saiu do lugar"
# O contraste que a figura precisa mostrar: a mesma dotacao cai FORA da faixa
# estreita e DENTRO da faixa larga.
assert E_DOT_CT > e_vende(K_GRANDE), \
    "a dotacao deveria cair fora da faixa do emissor grande"
assert e_compra(K_PEQUENO) <= E_DOT_CT <= e_vende(K_PEQUENO), \
    "a dotacao deveria cair dentro da faixa do emissor pequeno"

# Distancia vertical minima, em px, entre DOIS rotulos vizinhos do eixo. Os tres
# rotulos em jogo sao "sigma+k", "sigma" e "sigma-k", e os vizinhos ficam a
# k * sy um do outro (nao 2k: 2k e a faixa inteira, que cobre dois intervalos).
# Uma caixa de texto de 15px tem ~11px de altura, entao 13 da folga de dois.
FOLGA_ROTULO_Y = 13
X_MAX_CT = 115
Y_MAX_CT = 58        # escala propria: aqui a curva vai so ate 50, e usar o
                     # Y_MAX = 108 das outras figuras jogaria metade do painel
                     # fora. Os DOIS paineis compartilham esta escala, que e o
                     # que a comparacao exige.


def _painel_transacao(t, x_off, titulo, k):
    p = Painel(t, x_off, LARG_2P, (0, X_MAX_CT), (0, Y_MAX_CT))
    p.titulo(titulo)
    p.eixos("e", "CMg")
    p.reta(0, cmg_ct(0), A_CT / B_CT, 0, cor=COR_CMG)

    ec, ev = e_compra(k), e_vende(k)
    # a faixa de dotacoes em que a firma nao negocia
    p.area([(ec, 0), (ev, 0), (ev, SIGMA - k), (ec, SIGMA + k)],
           COR_DESTAQUE, 0.16)
    # As duas horizontais existem nos dois paineis, mas so recebem rotulo onde
    # ha altura para os dois textos mais o de sigma entre eles. Com k = 1 a
    # distancia e de ~4px e os tres rotulos se empilham num borrao ilegivel; a
    # faixa estreita e justamente o assunto do painel, entao quem sai e o
    # rotulo, e nao a faixa. O painel da direita nomeia as duas linhas, e a
    # construcao e a mesma nos dois.
    rotular = k * p.sy >= FOLGA_ROTULO_Y
    for y, rot in ((SIGMA + k, "σ+k"), (SIGMA - k, "σ−k")):
        p.reta(0, y, A_CT / B_CT, y, cor=COR_GUIA, larg=1.0, tracejado="3 3")
        if rotular:
            p.marca_y(y, rot, cor=COR_GUIA)
    p.texto(0.5 * (ec + ev), -7.5, "não negocia", cor=COR_DESTAQUE,
            negrito=True, tam=FONTE, italico=False, ancora="middle")

    # a dotacao gratuita, identica nos dois paineis
    p.reta(E_DOT_CT, 0, E_DOT_CT, Y_MAX_CT - 4, cor=COR_GUIA, larg=1.1,
           tracejado="4 3")
    p.texto(E_DOT_CT, Y_MAX_CT - 2, "ē", cor=COR_DESTAQUE, negrito=True,
            tam=FONTE, ancora="middle")

    # onde a firma para: na borda da faixa se a dotacao cair fora dela, na
    # propria dotacao se cair dentro
    e_fim = min(max(E_DOT_CT, ec), ev)
    p.ponto(e_fim, cmg_ct(e_fim))
    return p


def figura_custo_transacao():
    t = Tela(2 * LARG_2P + FOLGA_DIR, Painel.ALT + 30)
    p1 = _painel_transacao(t, 0, "Emissor grande (k = 1)", K_GRANDE)
    _painel_transacao(t, LARG_2P, "Emissor pequeno (k = 5)", K_PEQUENO)

    # sigma atravessa os dois paineis: e o mesmo preco de mercado para todo
    # mundo, e e justamente por isso que a diferenca so pode vir de k
    y = p1.py(SIGMA)
    t.add('<line x1="{:.1f}" y1="{:.1f}" x2="{:.1f}" y2="{:.1f}"'
          ' stroke="{}" stroke-width="1.6" stroke-dasharray="7 4"/>'
          .format(p1.px(0) - 4, y, p1.px(X_MAX_CT) + LARG_2P, y, COR_DESTAQUE))
    p1.marca_y(SIGMA, "σ", cor=COR_DESTAQUE)

    rodape(t, "com k pequeno a firma negocia e para em 52; com k grande ela"
              " fica na dotação e emite 56")
    return t


def main():
    # Sem acento nem grego no print: o console do Windows abre em cp1252.
    print("Figuras da aula 07 (sigma* = {:.0f}, {:.1f} permissoes trocadas por"
          " {:.1f}, ganho {:.4f}):"
          .format(SIGMA, QTD, PAGO, GANHO))
    figura_leilao().salvar(
        "07-leilao.svg",
        "Escolher a alíquota e escolher a oferta de permissões levam ao mesmo"
        " ponto")
    figura_permissoes_1().salvar(
        "07-permissoes-1.svg",
        "Com dotação igual e direito de venda, a firma de custo alto compra"
        " permissões da de custo baixo")
    figura_permissoes_2().salvar(
        "07-permissoes-2.svg",
        "O que cada firma gasta abatendo, paga e recebe no mercado de"
        " permissões")
    figura_permissoes_3().salvar(
        "07-permissoes-3.svg",
        "O ganho da troca é o peso morto que o padrão uniforme deixava na mesa")
    figura_subsidio_1().salvar(
        "07-subsidio-1.svg",
        "Subsídio com referência individual devolve a mesma alocação do"
        " imposto")
    figura_subsidio_2().salvar(
        "07-subsidio-2.svg",
        "Com referência comum, a firma de custo alto sai do programa de"
        " subsídio")
    print("  leilao do exercicio: A leva {}, B leva {}, preco entre {} e {}"
          .format(VENCE_A, VENCE_B, P_MIN, P_MAX))
    figura_exercicio().salvar(
        "07-exercicio-leilao.svg",
        "O preço do leilão sai das ofertas das usinas, e não do regulador")
    print("  custo de transacao: faixa estreita [{:.0f}, {:.0f}], faixa larga"
          " [{:.0f}, {:.0f}], dotacao {:.0f}"
          .format(e_compra(K_GRANDE), e_vende(K_GRANDE),
                  e_compra(K_PEQUENO), e_vende(K_PEQUENO), E_DOT_CT))
    figura_custo_transacao().salvar(
        "07-custo-transacao.svg",
        "Com custo de transação, a dotação volta a decidir a emissão")


if __name__ == "__main__":
    main()
