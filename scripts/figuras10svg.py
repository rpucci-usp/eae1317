#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Gera os diagramas da aula 10 (Mercado Nao Competitivo) a partir das equacoes.

A aula junta `07_eae1317_mercadoCompetitivo.pptx` (so o bloco de funcao-custo,
demanda e otimo social, que e o andaime) com `08_eae1317_mercadoNaoCompetitivo`
inteiro. Nenhum dos dois tem figura: os pontos em que o argumento vira desenho
estao marcados "(LOUSA)" ou "Representacao Grafica".

Importa `Painel`, `Tela` e as cores de figuras04svg.py, e `fmt`, `reta_clip` e
`escada` de figuras08svg.py.

A CALIBRACAO, E POR QUE ELA E ESTA
----------------------------------
O curso inteiro roda sobre um ponto conhecido:

    -C'(E) = (200 - E)/3     D'(E) = 0,2 E     E* = 125, preco 25

Esta aula acrescenta o produto X, e a promessa e que a curva de abatimento das
aulas 04 a 09 continue valendo. Ela vale, e nao por acaso:

    C(X, E) = c X + (a/2) (delta X - E)^2,   c = 10, a = 1/3, delta = 2
    P(X)    = 160 - X

    -C_E(X, E) = a (delta X - E)              => com X = 100, e (200 - E)/3
    C_X(X, E)  = c + a delta (delta X - E)

Ou seja, a curva de abatimento agregada do curso e a curva de abatimento DESTA
tecnologia no nivel de producao eficiente. A aula passa a ter duas dimensoes
sem trocar um numero dos slides anteriores.

O OTIMO DE PARETO
-----------------
    P(X) = C_X   e   D'(E) = -C_E   =>   X* = 100, E* = 125, p* = 60, tau* = 25

O TRUQUE QUE TORNA AS FIGURAS DESENHAVEIS
-----------------------------------------
Dado tau, a firma escolhe E pela CPO de emissao: delta X - E = tau/a = 3 tau.
Substituindo em C_X, o custo marginal de produzir X vira CONSTANTE:

    C_X = c + delta tau = 10 + 2 tau

Com tau* = 25 isso da 60, que e exatamente P(100). Entao o painel (X, R$) e o
diagrama de monopolio de qualquer curso de micro: demanda, receita marginal e
uma horizontal. Nada aqui e aproximacao.

    concorrencia com tau:  X = 150 - 2 tau      E = 2X - 3 tau
    monopolio com tau:     X =  75 -   tau      E = 150 - 5 tau

Com tau* = 25 o monopolista para em X = 50 e E = 25: ele abate DEMAIS, porque
ja produzia de menos. E o resultado central da aula.

A PERDA COMO FUNCAO DO IMPOSTO
------------------------------
    W(tau) = 6.187,5 + 75 tau - 4,5 tau^2      (primeiro melhor: 7.500)

    tau = 0        W = 6.187,5   perda 1.312,5
    tau = 25/3     W = 6.500     perda 1.000    <- o melhor imposto sozinho
    tau = 50/3     W = 6.187,5   perda 1.312,5  <- daqui em diante e pior que nada
    tau = tau* =25 W = 5.250     perda 2.250

O imposto eficiente do mundo competitivo gera a MAIOR perda dos quatro. A
figura `10-imposto.svg` e essa parabola, e ela e a aula em um desenho.

O SUBSIDIO QUE FECHA
--------------------
    psi = -P'(X*) X* = 100   =>   monopolista escolhe X = 100 e E = 125

O EXERCICIO
-----------
Versao discreta do mesmo resultado, com a hipotese do bloco nao-separavel
(e = delta x, abater e produzir menos), que e o que permite uma unica variavel
de escolha:

    disposicao a pagar do lote k: 105 - 10k   (95, 85, 75, 65, 55, 45, 35, 25)
    receita marginal do lote k:   115 - 20k   (95, 75, 55, 35, 15, ...)
    custo de producao 30/lote, 2 t por lote, dano 15/t  => 30/lote de dano

    eficiente             4 lotes   bem-estar 80
    concorrencia sem nada 7 lotes   bem-estar 35
    monopolio sem nada    4 lotes   bem-estar 80
    monopolio com tau=30  2 lotes   bem-estar 60
    monopolio com tau=30 e psi=40   4 lotes   bem-estar 80

Depende so da biblioteca padrao, como os outros scripts desta pasta.

    py scripts/figuras10svg.py

Escreve em aulas/_assets/figuras/.
"""

from figuras04svg import (Painel, Tela, COR_CMG, COR_DANO, COR_EIXO,
                          COR_GUIA, COR_APAGADA, COR_DESTAQUE,
                          FONTE, FONTE_LEGENDA, FOLGA_ROTULO_X)
from figuras08svg import fmt, reta_clip, escada, rodape

# Terceira cor, e ela e necessaria. Vermelho e custo e azul e dano em todas as
# figuras do curso; o MERCADO DO PRODUTO nao existia ate esta aula e nao tem
# cor. Pintar a demanda de azul funcionaria em `10-monopolio.svg`, que so tem um
# painel, e mentiria no trio do otimo, onde a demanda fica ao lado do dano.
COR_PROD = "#2E7D32"
# O mesmo vermelho, mais claro, para a curva do nivel de producao MENOR. Nao e
# COR_APAGADA: as duas curvas sao igualmente o assunto da figura, o que muda e
# qual delas acabou de entrar.
COR_CMG_CLARO = "#E38080"

# --- a tecnologia -----------------------------------------------------------
C0 = 10.0                        # custo marginal "limpo" de produzir
A_CUSTO = 1.0 / 3                # inclinacao de -C_E, a mesma das aulas 04-09
DELTA = 2.0                      # e-chapeu(X) = DELTA * X

custo = lambda X, E: C0 * X + (A_CUSTO / 2) * (DELTA * X - E) ** 2
mac = lambda X, E: A_CUSTO * (DELTA * X - E)          # -C_E(X, E)
cmg_x = lambda X, E: C0 + A_CUSTO * DELTA * (DELTA * X - E)   # C_X(X, E)
e_chapeu = lambda X: DELTA * X

# --- o mercado do produto e o dano ------------------------------------------
A_DEM = 160.0                    # P(X) = A_DEM - B_DEM X
B_DEM = 1.0
ETA = 0.2                        # D'(E) = ETA E, como nas aulas 04 a 09

demanda = lambda X: A_DEM - B_DEM * X
rec_mg = lambda X: A_DEM - 2 * B_DEM * X
dano_mg = lambda E: ETA * E

# --- o otimo de Pareto ------------------------------------------------------
X_OTIMO = 100.0
E_OTIMO = 125.0
P_OTIMO = 60.0
TAU_OTIMO = 25.0

assert abs(mac(X_OTIMO, E_OTIMO) - dano_mg(E_OTIMO)) < 1e-9, "E* deixou de ser 125"
assert abs(dano_mg(E_OTIMO) - TAU_OTIMO) < 1e-9, "tau* mudou"
assert abs(demanda(X_OTIMO) - cmg_x(X_OTIMO, E_OTIMO)) < 1e-9, "X* deixou de ser 100"
assert abs(demanda(X_OTIMO) - P_OTIMO) < 1e-9, "o preco no otimo mudou"
# A ponte com as aulas 04 a 09: no nivel eficiente de producao, a curva de
# abatimento desta tecnologia E a curva agregada do curso.
assert abs(e_chapeu(X_OTIMO) - 200.0) < 1e-9, "e-chapeu(X*) deixou de ser 200"
assert abs(mac(X_OTIMO, 125.0) - (200.0 - 125.0) / 3) < 1e-9, "a ponte quebrou"

# --- o que cada mercado faz com um imposto tau ------------------------------
# Dada a CPO de emissao (delta X - E = tau / a), C_X vira constante:
cmg_reduzido = lambda tau: C0 + DELTA * tau

x_conc = lambda tau: (A_DEM - cmg_reduzido(tau)) / B_DEM
x_mon = lambda tau: (A_DEM - cmg_reduzido(tau)) / (2 * B_DEM)
e_de = lambda X, tau: DELTA * X - tau / A_CUSTO

assert abs(cmg_reduzido(TAU_OTIMO) - P_OTIMO) < 1e-9, "o CMg reduzido mudou"
assert abs(x_conc(TAU_OTIMO) - X_OTIMO) < 1e-9, "a concorrencia com tau* saiu do otimo"
assert abs(e_de(x_conc(TAU_OTIMO), TAU_OTIMO) - E_OTIMO) < 1e-9, "E* nao sai mais"
assert abs(x_mon(TAU_OTIMO) - 50.0) < 1e-9, "o monopolista com tau* mudou de lugar"
assert abs(e_de(x_mon(TAU_OTIMO), TAU_OTIMO) - 25.0) < 1e-9, "E do monopolio mudou"
# X = 75 - tau e E = 150 - 5 tau, as duas retas citadas na docstring
assert abs(x_mon(0.0) - 75.0) < 1e-9 and abs(e_de(x_mon(0.0), 0.0) - 150.0) < 1e-9

# --- o mercado competitivo SEM imposto --------------------------------------
# Com tau = 0 a firma para onde abater deixa de custar, ou seja, em e-chapeu(X),
# e o custo marginal de produzir e o "limpo": C_X = c. A demanda faz o resto.
X_LIVRE = x_conc(0.0)                     # 150
E_LIVRE = e_de(X_LIVRE, 0.0)              # 300
assert abs(cmg_reduzido(0.0) - C0) < 1e-9, "sem imposto o CMg deixou de ser c"
assert abs(X_LIVRE - 150.0) < 1e-9, "a producao sem imposto mudou"
assert abs(E_LIVRE - e_chapeu(X_LIVRE)) < 1e-9, "sem imposto a firma deveria nao abater"
assert abs(E_LIVRE - 300.0) < 1e-9, "a emissao sem imposto mudou"
assert abs(mac(X_LIVRE, E_LIVRE)) < 1e-9, "abater a ultima tonelada deveria custar zero"
assert abs(dano_mg(E_LIVRE) - 60.0) < 1e-9, "o dano marginal em e-chapeu mudou"

# --- bem-estar como funcao do imposto ---------------------------------------


def bem_estar(X, E):
    """Integral da demanda menos custo menos dano."""
    beneficio = A_DEM * X - B_DEM * X * X / 2
    return beneficio - custo(X, E) - (ETA / 2) * E * E


W_PRIMEIRO = bem_estar(X_OTIMO, E_OTIMO)
assert abs(W_PRIMEIRO - 7500.0) < 1e-9, "o primeiro melhor mudou"


def w_mon(tau):
    X = x_mon(tau)
    return bem_estar(X, e_de(X, tau))


# A forma fechada da docstring, conferida ponto a ponto.
assert all(abs(w_mon(t / 4.0) - (6187.5 + 75 * (t / 4.0) - 4.5 * (t / 4.0) ** 2))
           < 1e-7 for t in range(0, 121)), "W(tau) nao e mais a parabola"

TAU_SEGUNDO = 75.0 / 9            # 25/3, o vertice da parabola
assert abs(w_mon(TAU_SEGUNDO) - 6500.0) < 1e-9, "o segundo melhor mudou"
assert w_mon(TAU_SEGUNDO) > w_mon(0.0) > w_mon(TAU_OTIMO), "a ordem das tres perdas mudou"
assert TAU_SEGUNDO < TAU_OTIMO, "o imposto de segundo melhor deveria ser menor"
# O imposto eficiente do mundo competitivo e PIOR que nao fazer nada, e o ponto
# em que ele passa a ser vale um rotulo na figura.
TAU_EMPATE = 75.0 / 4.5           # 50/3, onde W(tau) volta a W(0)
assert abs(w_mon(TAU_EMPATE) - w_mon(0.0)) < 1e-9, "o empate mudou de lugar"

perda = lambda tau: W_PRIMEIRO - w_mon(tau)

# O ponto de partida do trio do otimo: sem politica nenhuma, o mercado
# competitivo perde 5.250 dos 7.500. E a maior perda da aula inteira, e vale ter
# o numero a mao para responder "e se nao fizermos nada?".
W_LIVRE = bem_estar(X_LIVRE, E_LIVRE)
assert abs(W_LIVRE - 2250.0) < 1e-9, "o bem-estar sem imposto mudou"
assert abs(W_PRIMEIRO - W_LIVRE - 5250.0) < 1e-9, "a perda sem imposto mudou"
assert abs(perda(TAU_SEGUNDO) - 1000.0) < 1e-9
assert abs(perda(0.0) - 1312.5) < 1e-9
assert abs(perda(TAU_OTIMO) - 2250.0) < 1e-9

# --- o subsidio que fecha ---------------------------------------------------
PSI = B_DEM * X_OTIMO             # -P'(X*) X* = 100
x_mon_psi = lambda tau, psi: (A_DEM + psi - cmg_reduzido(tau)) / (2 * B_DEM)
assert abs(x_mon_psi(TAU_OTIMO, PSI) - X_OTIMO) < 1e-9, "o subsidio deixou de fechar"
assert abs(e_de(x_mon_psi(TAU_OTIMO, PSI), TAU_OTIMO) - E_OTIMO) < 1e-9

# --- o bloco nao-separavel --------------------------------------------------
# Firma tomadora de preco, e = x, C(x) = x^2/4 e p = 50. Numeros proprios: o
# ponto aqui e a FORMA (lucro com pico, perda de lucro como area), e amarrar
# este exemplo a calibracao principal exigiria um p quebrado.
P_NS = 50.0
lucro_ns = lambda e: P_NS * e - e * e / 4
lucro_mg_ns = lambda e: P_NS - e / 2
E_CHAPEU_NS = 100.0
E_META_NS = 60.0
assert abs(lucro_mg_ns(E_CHAPEU_NS)) < 1e-9, "e-chapeu do bloco nao-separavel mudou"
PERDA_NS = lucro_ns(E_CHAPEU_NS) - lucro_ns(E_META_NS)
assert abs(PERDA_NS - 400.0) < 1e-9, "a perda de lucro mudou"
# A area do triangulo sob a marginal e a mesma coisa, e e o que a figura mostra.
assert abs(0.5 * (E_CHAPEU_NS - E_META_NS) * lucro_mg_ns(E_META_NS) - PERDA_NS) < 1e-9

# --- o exercicio ------------------------------------------------------------
LOTES = 8
DAP = [105 - 10 * k for k in range(1, LOTES + 1)]       # 95, 85, ..., 25
RMG = [115 - 20 * k for k in range(1, LOTES + 1)]       # 95, 75, 55, 35, 15, ...
CUSTO_LOTE = 30.0
T_POR_LOTE = 2.0
DANO_T = 15.0
DANO_LOTE = T_POR_LOTE * DANO_T                          # 30
CMG_SOCIAL = CUSTO_LOTE + DANO_LOTE                      # 60
TAU_EX = DANO_LOTE                                       # o imposto pigouviano
PSI_EX = 40.0                                            # -P'(X*) X* = 10 * 4

conta = lambda passos, limite: sum(1 for v in passos if v >= limite)

X_EFIC_EX = conta(DAP, CMG_SOCIAL)                       # 4
X_CONC_EX = conta(DAP, CUSTO_LOTE)                       # 7
X_MON_EX = conta(RMG, CUSTO_LOTE)                        # 4
X_MON_TAU_EX = conta(RMG, CUSTO_LOTE + TAU_EX)           # 2
X_MON_PSI_EX = conta([v + PSI_EX for v in RMG], CUSTO_LOTE + TAU_EX)   # 4

assert (X_EFIC_EX, X_CONC_EX, X_MON_EX, X_MON_TAU_EX, X_MON_PSI_EX) == (4, 7, 4, 2, 4), \
    "o exercicio mudou de resposta"

bem_estar_ex = lambda X: sum(DAP[:X]) - CMG_SOCIAL * X

assert [bem_estar_ex(k) for k in range(1, 8)] == [35, 60, 75, 80, 75, 60, 35], \
    "a escada de bem-estar do exercicio mudou"
assert bem_estar_ex(X_EFIC_EX) == 80 and bem_estar_ex(X_MON_TAU_EX) == 60
# O imposto pigouviano custa 20 de bem-estar AQUI, e e o par discreto dos 1.250
# que a parabola mostra la. O sinal e o que importa, nao a escala.
assert bem_estar_ex(X_MON_TAU_EX) < bem_estar_ex(X_MON_EX), \
    "o imposto pigouviano deveria piorar o bem-estar neste exercicio"

# --- enquadramentos ---------------------------------------------------------
LARG_AG = 760                    # painel unico, como na aula 08
ALT_AG = 330
FOLGA_AG = 26

LARG_PAR = 440                   # os pares, como em total_vs_marginal
ALT_PAR = 336

X_MAX_C = 262                    # e-chapeu(X2) = 200 precisa sobrar margem
Y_MAX_CT = 8200                  # C(100, 0) = 7.666,7
Y_MAX_CM = 72                    # -C_E(100, 0) = 66,7

X_MAX_P = 172                    # o mercado do produto: X* = 100, livre = 150
Y_MAX_P = 176                    # P(0) = 160

X_MAX_E = 215                    # o mercado de emissao, igual ao da aula 08
Y_MAX_E = 72

# O trio do otimo precisa de um eixo de emissao MAIS LARGO que os demais: a
# etapa sem imposto para em e-chapeu(150) = 300, e 215 cortaria a figura no meio
# do argumento. As tres etapas dividem o mesmo enquadramento, que e o que
# permite ler o deslocamento. `10-monopolio.svg` e `10-subsidio.svg` ficam nos
# 215, porque la o assunto e a distancia entre 125 e 25, que 312 espremeria.
X_MAX_EO = 312

SUB_X1 = "x" + chr(0x2081)
SUB_X2 = "x" + chr(0x2082)

# e-chapeu com EXPOENTE x1 / x2. Unicode nao tem subscrito dentro de
# sobrescrito, entao o "x" e o digito vao os dois sobrescritos: e^(x1). Um
# subscrito solto depois do sobrescrito, que foi a primeira tentativa, saia
# lido como "e elevado a x, indice 1", que e outra coisa.
EHAT_X1 = "ê" + chr(0x02E3) + chr(0x00B9)
EHAT_X2 = "ê" + chr(0x02E3) + chr(0x00B2)
EHAT_X = "ê" + chr(0x02E3)
CX = "C" + chr(0x2093)
MEN_CE = "−C" + chr(0x2091)


# ---------------------------------------------------------------------------
# 1 e 2. A funcao-custo com produto e poluicao
# ---------------------------------------------------------------------------
X1, X2 = 75.0, 100.0


def _painel_custo_total(t, x_off, larg, alt, so_x1):
    p = Painel(t, x_off, larg, (0, X_MAX_C), (0, Y_MAX_CT), alt)
    p.titulo("Custo total de produzir x, para cada e")
    p.eixos("e", "C(x, e)")

    if not so_x1:
        p.curva(lambda E: custo(X2, E), 0, X_MAX_C, cor=COR_CMG, larg=2.2)
        p.guia(e_chapeu(X2), custo(X2, e_chapeu(X2)))
        p.ponto(e_chapeu(X2), custo(X2, e_chapeu(X2)), cor=COR_CMG)
        p.marca_x(e_chapeu(X2), EHAT_X2, cor=COR_CMG)
        p.texto(118, custo(X2, 118) + 700, "C(" + SUB_X2 + ", e)", cor=COR_CMG,
                tam=FONTE_LEGENDA, negrito=True)

    cor1 = COR_CMG if so_x1 else COR_CMG_CLARO
    p.curva(lambda E: custo(X1, E), 0, X_MAX_C, cor=cor1, larg=2.2)
    p.guia(e_chapeu(X1), custo(X1, e_chapeu(X1)))
    p.ponto(e_chapeu(X1), custo(X1, e_chapeu(X1)), cor=cor1)
    p.marca_x(e_chapeu(X1), EHAT_X1, cor=cor1)
    # Acima do ramo que SOBE, que e o unico pedaco de tela vazio da figura: o
    # ramo que desce e longo e raso, e qualquer rotulo perto dele acaba
    # encostando na curva alguns pixels adiante.
    p.texto(222, custo(X1, 222) + 1150, "C(" + SUB_X1 + ", e)", cor=cor1,
            tam=FONTE_LEGENDA, negrito=True)
    return p


def _painel_custo_marginal(t, x_off, larg, alt):
    p = Painel(t, x_off, larg, (0, X_MAX_C), (0, Y_MAX_CM), alt)
    p.titulo("Custo marginal de abater, para cada e")
    p.eixos("e", "−C" + chr(0x2091) + "(x, e)")

    for X, sub, cor, rot, x_rot in ((X2, SUB_X2, COR_CMG, EHAT_X2, 132),
                                    (X1, SUB_X1, COR_CMG_CLARO, EHAT_X1, 40)):
        # A reta acaba exatamente no eixo: e a definicao de e-chapeu, e passar
        # dali seria desenhar custo marginal de abatimento negativo.
        p.reta(0, mac(X, 0), e_chapeu(X), 0, cor=cor, larg=2.4)
        p.ponto(e_chapeu(X), 0, cor=cor)
        p.marca_x(e_chapeu(X), rot, cor=cor)
        # x_rot bem separado nas duas: a 52% de cada reta os dois rotulos
        # caiam a 26px um do outro e o halo de um comia a primeira letra do
        # outro.
        p.texto(x_rot, mac(X, x_rot) + 4.6,
                "−C" + chr(0x2091) + "(" + sub + ", e)", cor=cor,
                tam=FONTE_LEGENDA, negrito=True)
    return p


def custo_figura(nome, titulo, so_total):
    if so_total:
        t = Tela(LARG_PAR + FOLGA_ROTULO_X, ALT_PAR + 6)
        _painel_custo_total(t, 0, LARG_PAR, ALT_PAR, so_x1=True)
    else:
        t = Tela(2 * LARG_PAR + FOLGA_ROTULO_X, ALT_PAR + 6)
        _painel_custo_total(t, 0, LARG_PAR, ALT_PAR, so_x1=False)
        _painel_custo_marginal(t, LARG_PAR, LARG_PAR, ALT_PAR)
    t.salvar(nome, titulo)


# ---------------------------------------------------------------------------
# 3. O otimo de Pareto, em tres etapas
# ---------------------------------------------------------------------------
# A primeira versao era UMA figura, ja com o imposto dentro da horizontal do
# custo marginal ("C_x = c + delta tau*"). A pedido do autor em 21/09: o imposto
# aparecia antes de ter sido apresentado, e o slide pedia que a turma aceitasse
# de uma vez o equilibrio, o instrumento e o otimo. As tres etapas separam isso:
#
#   1. sem imposto   C_x = c = 10, X = 150, e a firma nao abate: E = 300
#   2. entra o imposto   a horizontal sobe para 60, X cai para 100, E para 125
#   3. o otimo   as duas condicoes do slide anterior, uma em cada painel
#
# As tres dividem eixos, para que o deslocamento seja legivel de uma etapa para
# a seguinte. E por isso que o eixo de emissao vai a X_MAX_EO, e nao a X_MAX_E.


def _otimo_produto(t, etapa):
    p = Painel(t, 0, LARG_PAR, (0, X_MAX_P), (0, Y_MAX_P), ALT_PAR)
    p.titulo("Mercado do produto")
    p.eixos("X", "R$ por unidade")
    p.curva(demanda, 0, X_MAX_P, cor=COR_PROD, larg=2.4)
    p.texto(18, demanda(18) + 7, "P(X)", cor=COR_PROD, tam=FONTE_LEGENDA,
            negrito=True)

    if etapa == 1:
        p.reta(0, C0, X_MAX_P, C0, cor=COR_CMG, larg=2.4)
        # No mesmo lugar do rotulo da etapa 2, para que a turma veja a MESMA
        # horizontal subir. A direita, a 140, ele caia em cima da demanda, que
        # so cruza 10 em X = 150.
        p.texto(14, C0 + 10, CX + " = c = 10", cor=COR_CMG,
                tam=FONTE_LEGENDA, negrito=True)
        p.guia(X_LIVRE, C0)
        p.ponto(X_LIVRE, C0)
        p.marca_x(X_LIVRE, "X = 150")
        p.marca_y(C0, "10")
        return p

    if etapa == 2:
        # A horizontal de antes fica apagada por tras, com o ponto dela: sem
        # isso, "o custo marginal sobe" e uma afirmacao do bullet.
        p.reta(0, C0, X_MAX_P, C0, cor=COR_APAGADA, larg=2.2)
        p.ponto(X_LIVRE, C0, cor=COR_APAGADA)
        p.marca_x(X_LIVRE, "sem τ", cor=COR_APAGADA)
        p.marca_y(C0, "10", cor=COR_APAGADA)

    p.reta(0, P_OTIMO, X_MAX_P, P_OTIMO, cor=COR_CMG, larg=2.4)
    p.texto(14, P_OTIMO + 8, CX + " = c + δτ*", cor=COR_CMG,
            tam=FONTE_LEGENDA, negrito=True)
    p.guia(X_OTIMO, P_OTIMO)
    p.ponto(X_OTIMO, P_OTIMO)
    p.marca_x(X_OTIMO, "X* = 100")
    p.marca_y(P_OTIMO, "60")
    return p


def _otimo_emissao(t, etapa):
    p = Painel(t, LARG_PAR, LARG_PAR, (0, X_MAX_EO), (0, Y_MAX_E), ALT_PAR)
    p.titulo("Mercado de emissão")
    p.eixos("E", "R$ por tonelada")
    reta_clip(p, dano_mg, COR_DANO, larg=2.4)
    # ABAIXO da propria reta, e ancorado a direita: acima dela, na etapa 1, o
    # rotulo caia em cima do ponto azul de (300, 60), que e o numero a apontar.
    p.texto(290, dano_mg(290) - 6, "D′(E)", cor=COR_DANO,
            tam=FONTE_LEGENDA, negrito=True, ancora="end")

    if etapa == 1:
        reta_clip(p, lambda E: mac(X_LIVRE, E), COR_CMG, larg=2.4)
        # A 150 o rotulo passava rente a tracejada do dano em 60, e a 200 caia
        # em cima do cruzamento das duas curvas.
        p.texto(125, mac(X_LIVRE, 125) + 6, MEN_CE + "(X, E)", cor=COR_CMG,
                tam=FONTE_LEGENDA, negrito=True)
        # O imposto e zero, entao a firma desce a curva ate o proprio eixo. Nao
        # ha horizontal a desenhar, e e esse o ponto.
        p.ponto(E_LIVRE, 0.0)
        p.marca_x(E_LIVRE, EHAT_X + " = 300")
        p.reta(E_LIVRE, 0, E_LIVRE, dano_mg(E_LIVRE), cor=COR_GUIA, larg=1.1,
               tracejado="4 3")
        p.reta(0, dano_mg(E_LIVRE), E_LIVRE, dano_mg(E_LIVRE), cor=COR_GUIA,
               larg=1.1, tracejado="4 3")
        # A tonelada que ninguem abate: custa zero abater e evita 60 de dano.
        p.ponto(E_LIVRE, dano_mg(E_LIVRE), cor=COR_DANO)
        p.marca_y(dano_mg(E_LIVRE), "60", cor=COR_DANO)
        return p

    if etapa == 2:
        reta_clip(p, lambda E: mac(X_LIVRE, E), COR_APAGADA, larg=2.2)
        p.ponto(E_LIVRE, 0.0, cor=COR_APAGADA)
        p.marca_x(E_LIVRE, "sem τ", cor=COR_APAGADA)
        # A horizontal do imposto atravessa o painel: ela e a novidade da etapa,
        # e a curva e que veio ao encontro dela.
        p.reta(0, TAU_OTIMO, X_MAX_EO, TAU_OTIMO, cor=COR_GUIA, larg=1.4,
               tracejado="5 4")
        p.reta(E_OTIMO, 0, E_OTIMO, TAU_OTIMO, cor=COR_GUIA, larg=1.1,
               tracejado="4 3")
        p.marca_y(TAU_OTIMO, "τ* = 25")
    else:
        p.guia(E_OTIMO, TAU_OTIMO)
        p.marca_y(TAU_OTIMO, "25")

    reta_clip(p, lambda E: mac(X_OTIMO, E), COR_CMG, larg=2.4)
    p.texto(24, mac(X_OTIMO, 24) + 5, MEN_CE + "(X*, E)", cor=COR_CMG,
            tam=FONTE_LEGENDA, negrito=True)
    p.ponto(E_OTIMO, TAU_OTIMO)
    p.marca_x(E_OTIMO, "E* = 125")
    return p


def figura_otimo(etapa):
    t = Tela(2 * LARG_PAR + FOLGA_ROTULO_X, ALT_PAR + 6)
    _otimo_produto(t, etapa)
    _otimo_emissao(t, etapa)
    titulo = {
        1: "O mercado competitivo sem imposto: produção e "
           "emissão demais",
        2: "O imposto sobe o custo marginal de produzir, e os dois mercados "
           "se movem",
        3: "As duas condições do ótimo de Pareto com produto "
           "e poluição",
    }[etapa]
    t.salvar("10-otimo-{}.svg".format(etapa), titulo)


# ---------------------------------------------------------------------------
# 4 e 6. O monopolio, e o subsidio que o corrige
# ---------------------------------------------------------------------------

# As duas figuras de monopolio sao de DOIS paineis, e nao de um.
#
# A primeira versao mostrava so o mercado do produto, e escrevia "e emite E = 25
# contra E* = 125" no rodape. A pedido do autor em 16/09, o mercado de emissao
# passou a ser desenhado: sem ele, o deslocamento da curva de abatimento e uma
# afirmacao do rodape, e a aula inteira e sobre as DUAS margens se moverem
# juntas. Com ele, da para ver que o monopolista iguala -C_E ao MESMO tau e
# ainda assim para em outro lugar, porque a curva dele e outra.
LARG_MP = 470
ALT_MP = 340


def _painel_produto(t, x_off, titulo):
    p = Painel(t, x_off, LARG_MP, (0, X_MAX_P), (0, Y_MAX_P), ALT_MP)
    p.titulo(titulo)
    p.eixos("X", "R$ por unidade")
    p.curva(demanda, 0, X_MAX_P, cor=COR_PROD, larg=2.4)
    reta_clip(p, rec_mg, COR_PROD, larg=2.2, tracejado="7 4")
    p.reta(0, P_OTIMO, X_MAX_P, P_OTIMO, cor=COR_CMG, larg=2.4)
    p.texto(136, demanda(136) + 9, "P(X)", cor=COR_PROD, tam=FONTE_LEGENDA,
            negrito=True)
    # ABAIXO da propria reta, e na metade direita dela. Acima, o rotulo caia ou
    # na horizontal do custo marginal (que passa em 60) ou em cima do ponto do
    # monopolista, que fica em (50, 110) nas duas figuras.
    p.texto(66, rec_mg(66) - 11, "RMg(X)", cor=COR_PROD, tam=FONTE_LEGENDA,
            negrito=True)
    # Ancorado a direita, no trecho em que a demanda ja passou por baixo de 60 e
    # nao ha mais nada desenhado acima da horizontal.
    p.texto(170, P_OTIMO + 10, "C" + chr(0x2093) + " = c + δτ* = 60",
            cor=COR_CMG, tam=FONTE_LEGENDA, negrito=True, ancora="end")
    return p


def _painel_emissao(t, x_off, titulo, x_firma, x_antes=None):
    """O mercado de emissao, com a curva de abatimento DO NIVEL DE PRODUCAO.

    -C_E(X, E) = (2X - E)/3 anda com X: e a premissa -C_ex > 0 da primeira
    metade da aula, aqui em funcionamento. `x_firma` e o nivel que a firma
    escolhe; `x_antes`, quando dado, deixa a curva anterior apagada por tras,
    para que o deslocamento seja visivel.
    """
    p = Painel(t, x_off, LARG_MP, (0, X_MAX_E), (0, Y_MAX_E), ALT_MP)
    p.titulo(titulo)
    p.eixos("E", "R$ por tonelada")

    if x_antes is not None:
        reta_clip(p, lambda E: mac(x_antes, E), COR_APAGADA, larg=2.2)
        p.ponto(e_de(x_antes, TAU_OTIMO), TAU_OTIMO, cor=COR_APAGADA)

    reta_clip(p, dano_mg, COR_DANO, larg=2.4)
    # A curva de referencia: a do nivel eficiente de producao, que e a curva das
    # aulas 04 a 09. Sempre desenhada, para que o deslocamento tenha contra o
    # que ser medido.
    if abs(x_firma - X_OTIMO) > 1e-9:
        reta_clip(p, lambda E: mac(X_OTIMO, E), COR_CMG_CLARO, larg=2.2)
        # A 150 o rotulo caia em cima da tracejada de tau*, que passa em 25.
        p.texto(72, mac(X_OTIMO, 72) + 6, "−C" + chr(0x2091) + "(X*, E)",
                cor=COR_CMG_CLARO, tam=FONTE_LEGENDA, negrito=True)
        p.ponto(E_OTIMO, TAU_OTIMO, cor=COR_CMG_CLARO)
        p.marca_x(E_OTIMO, "E* = 125", cor=COR_CMG_CLARO)

    # A horizontal do imposto: as duas firmas igualam -C_E a ela, e e por isso
    # que o ponto so pode mudar se a curva mudar.
    p.reta(0, TAU_OTIMO, X_MAX_E, TAU_OTIMO, cor=COR_GUIA, larg=1.4,
           tracejado="5 4")
    p.marca_y(TAU_OTIMO, "τ* = 25")

    reta_clip(p, lambda E: mac(x_firma, E), COR_CMG, larg=2.6)
    e_f = e_de(x_firma, TAU_OTIMO)
    p.reta(e_f, 0, e_f, TAU_OTIMO, cor=COR_GUIA, larg=1.1, tracejado="4 3")
    p.ponto(e_f, TAU_OTIMO)
    return p, e_f


def figura_monopolio():
    t = Tela(2 * LARG_MP + FOLGA_ROTULO_X, ALT_MP + 46)
    p = _painel_produto(t, 0, "Mercado do produto")

    x_m = x_mon(TAU_OTIMO)
    # O triangulo entre a demanda e o custo marginal, do X do monopolista ate o
    # X eficiente: e o que a sociedade perde por o vendedor ser um so.
    n = 40
    borda = [(x_m + (X_OTIMO - x_m) * i / n, demanda(x_m + (X_OTIMO - x_m) * i / n))
             for i in range(n + 1)]
    p.area([(x_m, P_OTIMO)] + borda + [(X_OTIMO, P_OTIMO)], COR_DESTAQUE, 0.16)

    p.guia(X_OTIMO, P_OTIMO)
    p.ponto(X_OTIMO, P_OTIMO, cor=COR_CMG_CLARO)
    p.marca_x(X_OTIMO, "X* = 100", cor=COR_CMG_CLARO)

    p.guia(x_m, demanda(x_m))
    p.ponto(x_m, demanda(x_m))
    p.marca_x(x_m, "X" + chr(0x1D50) + " = 50")
    p.marca_y(demanda(x_m), "110")
    p.marca_y(P_OTIMO, "60")

    q, e_m = _painel_emissao(t, LARG_MP, "Mercado de emissão", x_m)
    q.texto(30, mac(x_m, 30) + 5, "−C" + chr(0x2091) + "(X" + chr(0x1D50) + ", E)",
            cor=COR_CMG, tam=FONTE_LEGENDA, negrito=True)
    q.texto(168, dano_mg(168) + 5, "D′(E)", cor=COR_DANO, tam=FONTE_LEGENDA,
            negrito=True)
    q.marca_x(e_m, "E" + chr(0x1D50) + " = 25")
    # O dano marginal na emissao do monopolista: a ultima tonelada abatida custa
    # 25 e evita 5. E a sobre-abatimento em um numero.
    q.ponto(e_m, dano_mg(e_m), cor=COR_DANO, r=3.6)
    q.marca_y(dano_mg(e_m), "5", cor=COR_DANO)

    rodape(t, "produzir 50 em vez de 100 puxa a curva de abatimento para a "
           "esquerda, e o mesmo τ* para em E = 25",
           larg=2 * LARG_MP, alt=ALT_MP)
    t.salvar("10-monopolio.svg",
             "Monopólio com o imposto eficiente do mundo competitivo")


def figura_subsidio():
    t = Tela(2 * LARG_MP + FOLGA_ROTULO_X, ALT_MP + 46)
    p = _painel_produto(t, 0, "Mercado do produto")

    reta_clip(p, lambda X: rec_mg(X) + PSI, COR_DESTAQUE, larg=2.4,
              tracejado="7 4")
    # A 116 o rotulo caia em cima do "P(X)", porque e ali que a reta subsidiada
    # cruza a demanda.
    p.texto(62, rec_mg(62) + PSI + 11, "RMg(X) + ψ", cor=COR_DESTAQUE,
            tam=FONTE_LEGENDA, negrito=True)

    x_m = x_mon(TAU_OTIMO)
    p.ponto(x_m, demanda(x_m), cor=COR_APAGADA)
    p.marca_x(x_m, "sem ψ", cor=COR_APAGADA)

    p.guia(X_OTIMO, P_OTIMO)
    p.ponto(X_OTIMO, P_OTIMO)
    p.marca_x(X_OTIMO, "X* = 100")
    p.marca_y(P_OTIMO, "60")

    q, e_f = _painel_emissao(t, LARG_MP, "Mercado de emissão", X_OTIMO,
                             x_antes=x_m)
    q.texto(28, mac(X_OTIMO, 28) + 5, "−C" + chr(0x2091) + "(X*, E)",
            cor=COR_CMG, tam=FONTE_LEGENDA, negrito=True)
    q.texto(168, dano_mg(168) + 5, "D′(E)", cor=COR_DANO, tam=FONTE_LEGENDA,
            negrito=True)
    q.marca_x(e_f, "E* = 125")
    q.marca_x(e_de(x_m, TAU_OTIMO), "sem ψ", cor=COR_APAGADA)
    assert abs(e_f - E_OTIMO) < 1e-9, "o subsidio deixou de devolver E*"

    rodape(t, "com a produção de volta em 100, a curva de abatimento volta e o "
           "mesmo τ* entrega E* = 125",
           larg=2 * LARG_MP, alt=ALT_MP)
    t.salvar("10-subsidio.svg",
             "Imposto e subsídio juntos recuperam o ótimo de Pareto")


# ---------------------------------------------------------------------------
# 5. A perda como funcao do imposto
# ---------------------------------------------------------------------------
# perda(27) = 2.568, e o ultimo valor que cabe em Y_MAX_L. Com o 30 da primeira
# versao a parabola saia pelo topo do painel, que nao da erro nenhum e so
# estraga o desenho.
TAU_MAX_FIG = 27.0
Y_MAX_L = 2600


def figura_imposto():
    t = Tela(LARG_AG + FOLGA_AG, ALT_AG + 46)
    p = Painel(t, 0, LARG_AG, (0, TAU_MAX_FIG * 1.04), (0, Y_MAX_L), ALT_AG)
    p.titulo("Perda de bem-estar sob monopólio, para cada alíquota τ")
    p.eixos("τ", "perda")
    p.curva(perda, 0, TAU_MAX_FIG, cor=COR_CMG, larg=2.6)

    # A horizontal do "nao fazer nada" corta a parabola duas vezes, e o segundo
    # cruzamento e o recado: passado 50/3, taxar e pior que nao taxar.
    p.reta(0, perda(0.0), TAU_MAX_FIG, perda(0.0), cor=COR_GUIA, larg=1.4,
           tracejado="5 4")
    p.texto(TAU_MAX_FIG * 0.62, perda(0.0) + 88,
            "perda sem imposto nenhum: 1.312,5", cor=COR_GUIA,
            tam=FONTE_LEGENDA, italico=False)

    for tau, rot, cor in ((TAU_SEGUNDO, "τ" + chr(0x1D50) + " = 8,3", COR_DESTAQUE),
                          (TAU_OTIMO, "τ* = 25", COR_DANO)):
        p.guia(tau, perda(tau))
        p.ponto(tau, perda(tau), cor=cor)
        p.marca_x(tau, rot, cor=cor)
        p.marca_y(perda(tau), fmt(perda(tau)), cor=cor)

    p.ponto(TAU_EMPATE, perda(TAU_EMPATE), cor=COR_GUIA, r=3.6)
    p.marca_x(TAU_EMPATE, "16,7", cor=COR_GUIA)

    rodape(t, "a perda nunca chega a zero, e a alíquota do mundo competitivo "
           "é a pior das três")
    t.salvar("10-imposto.svg",
             "Perda de bem-estar sob monopólio em função da alíquota")


# ---------------------------------------------------------------------------
# 7. O bloco nao-separavel: abater e produzir menos
# ---------------------------------------------------------------------------

def figura_nao_separavel():
    t = Tela(2 * LARG_PAR + FOLGA_ROTULO_X, ALT_PAR + 6)

    pa = Painel(t, 0, LARG_PAR, (0, 118), (0, 2900), ALT_PAR)
    pa.titulo("Lucro da firma, para cada e")
    pa.eixos("e", "Π(e)")
    pa.curva(lucro_ns, 0, 118, cor=COR_PROD, larg=2.4)
    pa.guia(E_CHAPEU_NS, lucro_ns(E_CHAPEU_NS))
    pa.ponto(E_CHAPEU_NS, lucro_ns(E_CHAPEU_NS), cor=COR_PROD)
    pa.marca_x(E_CHAPEU_NS, "ê")
    pa.marca_y(lucro_ns(E_CHAPEU_NS), "2.500")
    pa.guia(E_META_NS, lucro_ns(E_META_NS))
    pa.ponto(E_META_NS, lucro_ns(E_META_NS), cor=COR_CMG)
    pa.marca_x(E_META_NS, "e = 60", cor=COR_CMG)
    pa.marca_y(lucro_ns(E_META_NS), "2.100", cor=COR_CMG)
    # A chave que diz que os 400 da direita sao esta diferenca aqui. Vai a
    # ESQUERDA do pico e nao a direita: a curva so desce depois de e-chapeu, e
    # uma barra vertical entre 2.100 e 2.500 la atravessa a propria curva.
    xb = 17
    pa.reta(xb, lucro_ns(E_META_NS), xb, lucro_ns(E_CHAPEU_NS), cor=COR_CMG,
            larg=2.0)
    pa.texto(xb + 4, (lucro_ns(E_META_NS) + lucro_ns(E_CHAPEU_NS)) / 2 - 40,
             "400", cor=COR_CMG, tam=FONTE_LEGENDA, negrito=True)

    pb = Painel(t, LARG_PAR, LARG_PAR, (0, 118), (0, 58), ALT_PAR)
    pb.titulo("Lucro marginal, que é o custo marginal de abater")
    pb.eixos("e", "dΠ/de")
    pb.reta(0, lucro_mg_ns(0), E_CHAPEU_NS, 0, cor=COR_CMG, larg=2.4)
    pb.area([(E_META_NS, 0), (E_META_NS, lucro_mg_ns(E_META_NS)),
             (E_CHAPEU_NS, 0)], COR_CMG, 0.30)
    pb.ponto(E_CHAPEU_NS, 0, cor=COR_CMG)
    pb.marca_x(E_CHAPEU_NS, "ê")
    pb.reta(E_META_NS, 0, E_META_NS, lucro_mg_ns(E_META_NS), cor=COR_GUIA,
            larg=1.1, tracejado="4 3")
    pb.marca_x(E_META_NS, "e = 60", cor=COR_CMG)
    pb.marca_y(lucro_mg_ns(E_META_NS), "20")
    pb.texto(72, 7.5, "400", cor=COR_CMG, tam=FONTE_LEGENDA, negrito=True)

    t.salvar("10-nao-separavel.svg",
             "Quando abater é produzir menos, o custo de abatimento é lucro perdido")


# ---------------------------------------------------------------------------
# 8. O exercicio
# ---------------------------------------------------------------------------
LARG_EX = 780
ALT_EX = 336
FOLGA_EX = 60


def figura_exercicio():
    t = Tela(LARG_EX + FOLGA_EX, ALT_EX + 46)
    p = Painel(t, 0, LARG_EX, (0, LOTES + 0.4), (0, 108), ALT_EX)
    p.titulo("As duas escadas do mercado, e as duas horizontais do regulador")
    p.eixos("lotes", "R$ mil por lote")

    escada(p, DAP, COR_PROD, larg=2.6)
    escada(p, [v for v in RMG if v > 0], COR_PROD, tracejado="7 4", larg=2.4)
    p.reta(0, CUSTO_LOTE, LOTES + 0.4, CUSTO_LOTE, cor=COR_CMG, larg=2.4)
    p.reta(0, CMG_SOCIAL, LOTES + 0.4, CMG_SOCIAL, cor=COR_DANO, larg=2.4)

    p.texto(6.1, DAP[5] + 6, "disposição a pagar", cor=COR_PROD,
            tam=FONTE_LEGENDA, negrito=True, italico=False)
    # A 3,1 o rotulo caia exatamente sobre a horizontal do custo social (60),
    # que e onde a receita marginal passa entre o terceiro e o quarto lote.
    p.texto(4.12, RMG[3] + 8, "receita marginal", cor=COR_PROD,
            tam=FONTE_LEGENDA, negrito=True, italico=False)
    p.texto(0.15, CUSTO_LOTE + 5.5, "custo de produção: 30", cor=COR_CMG,
            tam=FONTE_LEGENDA, negrito=True, italico=False)
    p.texto(0.15, CMG_SOCIAL + 5.5, "custo social: 30 + 30 = 60", cor=COR_DANO,
            tam=FONTE_LEGENDA, negrito=True, italico=False)

    for x, rot, cor in ((X_MON_TAU_EX, "2", COR_CMG),
                        (X_EFIC_EX, "4", COR_DESTAQUE),
                        (X_CONC_EX, "7", COR_PROD)):
        p.reta(x, 0, x, 96, cor=cor, larg=1.2, tracejado="3 4")
        p.marca_x(x, rot, cor=cor)

    rodape(t, "4 é onde a disposição a pagar cruza o custo social, e onde a "
           "receita marginal cruza 30", larg=LARG_EX, alt=ALT_EX)
    t.salvar("10-exercicio.svg", "O exercício do monopolista em lotes")


def main():
    import os
    from figuras04svg import DEST
    print("Figuras da aula 10 em {}:".format(os.path.normpath(DEST)))
    custo_figura("10-custo-1.svg",
                 "Custo total de produzir x em função da emissão", True)
    custo_figura("10-custo-2.svg",
                 "Custo total e custo marginal de abatimento, para dois níveis de produção",
                 False)
    for etapa in (1, 2, 3):
        figura_otimo(etapa)
    figura_monopolio()
    figura_imposto()
    figura_subsidio()
    figura_nao_separavel()
    figura_exercicio()
    print("\nSem imposto: X = {}, E = {}, bem-estar {}".format(
        fmt(X_LIVRE, 0), fmt(E_LIVRE, 0), fmt(W_LIVRE)))
    print("O otimo: X* = {}, E* = {}, p* = {}, tau* = {}".format(
        fmt(X_OTIMO, 0), fmt(E_OTIMO, 0), fmt(P_OTIMO, 0), fmt(TAU_OTIMO, 0)))
    print("Monopolio com tau*: X = {}, E = {}".format(
        fmt(x_mon(TAU_OTIMO), 0), fmt(e_de(x_mon(TAU_OTIMO), TAU_OTIMO), 0)))
    print("Perdas: sem imposto {}, tau^m {}, tau* {}".format(
        fmt(perda(0.0)), fmt(perda(TAU_SEGUNDO)), fmt(perda(TAU_OTIMO))))
    print("Exercicio: eficiente {}, concorrencia {}, monopolio {}, "
          "com tau {}, com tau e psi {}".format(
              X_EFIC_EX, X_CONC_EX, X_MON_EX, X_MON_TAU_EX, X_MON_PSI_EX))


if __name__ == "__main__":
    main()
