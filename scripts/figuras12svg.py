#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Gera os diagramas da aula 12 (Precos Hedonicos).

MOTIVO DE EXISTIR
-----------------
O `.pptx` 12 tem quatro figuras, todas desenhadas como formas nativas do
PowerPoint, e todas a mesma figura de Rosen (1974): uma curva `P(x,q)` com
curvas de lance encostando por baixo e curvas de oferta encostando por cima.
Nenhuma delas tem um numero.

O pedido do autor foi especifico: **"a intuicao do price schedule ainda esta
ruim"**. O diagnostico e que, sem numeros, `P(x,q)` parece uma curva de
demanda, e a inclinacao crescente parece dizer que as pessoas pagam MAIS por
unidade quanto MAIS qualidade tem, que e o contrario de tudo o que o curso
ensinou ate aqui. Ela nao e demanda de ninguem: e o cardapio do mercado, e a
inclinacao dele em cada ponto e a disposicao marginal a pagar DE QUEM ESCOLHEU
AQUELE PONTO.

Entao aqui o cardapio e construido a partir de seis apartamentos com preco, e
a figura que fecha a aula (`12-implicito.svg`) poe lado a lado o cardapio e a
sua inclinacao, com a disposicao marginal a pagar de cada comprador marcada em
cima dela.

A CALIBRACAO, E POR QUE ELA E ESTA
----------------------------------
Um bem diferenciado por um unico atributo ambiental q (indice de qualidade do
ar do quarteirao, de 0 a 10), com preco em R$ mil:

    P(q) = 300 + q^2        P'(q) = 2 q

    q       0     2     4     6     8    10
    P     300   304   316   336   364   400
    passo        +4   +12   +20   +28   +36

Compradores: preferencias quase-lineares em q, `U = s q + z`. A curva de lance
e entao uma RETA de inclinacao s, e o comprador quer a reta mais BAIXA que
ainda encosta no cardapio:

    b(q; s) = 300 - s^2/4 + s q       tangente em q* = s / 2

    s = 4  ->  q* = 2        s = 12 ->  q* = 6
    s = 8  ->  q* = 4        s = 16 ->  q* = 8

E a diferenca entre o cardapio e a reta de lance e um quadrado perfeito:

    P(q) - b(q; s) = (q - s/2)^2  >= 0,  com igualdade so em q*

Ou seja, **o cardapio e a envoltoria das retas de lance**, e isso se ve no
desenho porque a reta encosta e nao cruza.

Vendedores: custo C(q, v) = 300 + q^2 + (q - v)^2, com v o tipo da firma. A
curva de oferta com lucro Pi e theta(q) = Pi + C(q, v); com livre entrada,
Pi = 0 e

    theta(q; v) - P(q) = (q - v)^2 >= 0,  com igualdade so em q = v

A firma de tipo v entrega exatamente q = v, e a curva de oferta encosta no
cardapio POR CIMA. O lado da oferta e a imagem espelhada do lado da demanda,
com o mesmo quadrado perfeito, e e por isso que o mesmo P(q) serve aos dois.

A REGRESSAO, QUE E O PONTO DA SEGUNDA METADE DA AULA
----------------------------------------------------
Com os seis apartamentos acima, o MQO de P contra q da inclinacao

    Cov(q, q^2) / Var(q) = 116,666... / 11,666... = 10   exatamente

Dez nao e a disposicao marginal a pagar de nenhum dos quatro compradores
(4, 8, 12 e 16): e a media, e so vale como preco implicito no MEIO da amostra,
onde P'(5) = 10. Esse numero e a ponte para Greenstone e Gallagher, cujo efeito
de RDD e local por exatamente a mesma razao.

O EXERCICIO
-----------
A versao discreta e o proprio cardapio de seis apartamentos. Cada comprador
escolhe o q que maximiza s q - P(q), e a conta fecha nos mesmos pontos da
tangencia continua:

    s =  4:  q = 2  (excedente 4)     s = 12:  q = 6  (excedente 36)
    s =  8:  q = 4  (excedente 16)    s = 16:  q = 8  (excedente 64)

Depende so da biblioteca padrao, como os outros scripts desta pasta.

    py scripts/figuras12svg.py

Escreve em aulas/_assets/figuras/.
"""

import random

from figuras04svg import (Painel, Tela, COR_EIXO, COR_CMG, COR_DANO,
                          COR_GUIA, COR_APAGADA, COR_DESTAQUE,
                          FONTE_LEGENDA)
from figuras08svg import fmt
from figuras11svg import (COR_Q, COR_Q_CLARO, FOLGA, ALTURA_RODAPE,
                          moldura, rodape)

# A aula tem dois lados, e cada lado herda uma familia de cor do curso:
# COMPRADORES em roxo (a cor do bem ambiental, estreada na aula 11) e
# VENDEDORES em vermelho (a cor de custo desde a aula 04, e a curva de oferta e
# a funcao-custo mais o lucro). Dentro de cada familia, mais escuro e quem se
# move mais longe na qualidade. Azul de dano nao aparece aqui: nao ha dano
# nesta aula, e usa-lo para a reta de MQO confundiria o codigo de cor do curso.
COR_V_CLARO = "#E38080"
RAMPA = ["#C4ADD8", "#A47CC4", "#7B4FA8", "#4E2A73"]

# --- o cardapio -------------------------------------------------------------

preco = lambda q: 300.0 + q * q
preco_mg = lambda q: 2.0 * q
QS = [0, 2, 4, 6, 8, 10]
COMPRADORES = [4, 8, 12, 16]          # o tipo s de cada comprador
lance = lambda q, s: 300.0 - s * s / 4.0 + s * q
oferta = lambda q, v: 300.0 + q * q + (q - v) ** 2

LARG, ALT = 700, 340
Q_MAX = 10.8
Y_MIN, Y_MAX = 262.0, 432.0
JANELA = 3.5                           # meia-largura dos arcos de lance/oferta


def cardapio(titulo, larg=LARG, alt=ALT):
    t, p = moldura(titulo, larg, alt, (0, Q_MAX), (Y_MIN, Y_MAX),
                   "q", "preço do apartamento (R$ mil)")
    p.marca_y(300, "300")
    p.marca_y(400, "400")
    for q in QS:
        p.marca_x(q, str(q))
    return t, p


def curva_cardapio(p, cor=COR_EIXO, larg=2.8):
    p.curva(preco, 0, Q_MAX, cor=cor, larg=larg)


def pontos_cardapio(p, cor=COR_DESTAQUE, r=5.0, rotular=True):
    for q in QS:
        p.ponto(q, preco(q), cor=cor, r=r)
        if rotular:
            # O primeiro ponto esta em cima do eixo vertical, e centralizar o
            # rotulo dele o joga por cima da marca "300" do eixo.
            p.texto(q + (0.35 if q == QS[0] else 0), preco(q) + 11,
                    fmt(preco(q), 0), cor=cor, negrito=True, italico=False,
                    ancora="start" if q == QS[0] else "middle")


def menu(nome, etapa):
    """etapa 1: so os seis apartamentos. etapa 2: a curva e os degraus."""
    titulos = {
        1: "Seis apartamentos, iguais em tudo menos na qualidade do ar",
        2: "A função de preços hedônicos é o cardápio do mercado",
    }
    t, p = cardapio(titulos[etapa])
    if etapa == 2:
        curva_cardapio(p)
        p.texto(9.9, preco(9.9) - 26, "P(q)", cor=COR_EIXO, negrito=True,
                ancora="end")
        # O degrau entre dois apartamentos vizinhos e o que o mercado cobra
        # por dois pontos a mais de qualidade. Ele CRESCE, e e essa a coisa
        # que o aluno precisa estranhar antes de a aula explicar.
        for a, b in zip(QS, QS[1:]):
            p.texto((a + b) / 2.0, preco(b) - 18,
                    "+{}".format(fmt(preco(b) - preco(a), 0)),
                    cor=COR_CMG, negrito=True, italico=False, ancora="middle")
    pontos_cardapio(p)
    rod = ("q é um índice de qualidade do ar do quarteirão, de 0 a 10"
           if etapa == 1 else
           "dois pontos a mais de qualidade custam R$ 4 mil na base da tabela"
           " e R$ 36 mil no topo")
    rodape(t, LARG, ALT, rod)
    t.salvar(nome, titulos[etapa])


def _reta_lance(p, s, deslocamento=0.0, cor=COR_Q, larg=2.4, tracejado=None,
                q0=None, q1=None):
    a = max(0.0, (s / 2.0 - JANELA) if q0 is None else q0)
    b = min(Q_MAX, (s / 2.0 + JANELA) if q1 is None else q1)
    p.reta(a, lance(a, s) + deslocamento, b, lance(b, s) + deslocamento,
           cor=cor, larg=larg, tracejado=tracejado)


def lance_fig(nome, etapa):
    """1: a familia de curvas de lance. 2: a tangencia. 3: dois consumidores."""
    titulos = {
        1: "As curvas de lance do consumidor 1, e por que ele quer a de baixo",
        2: "Ele para onde o lance encosta no cardápio",
        3: "Dois consumidores, dois pontos, o mesmo cardápio",
    }
    t, p = cardapio(titulos[etapa])
    curva_cardapio(p)
    p.texto(9.9, preco(9.9) - 26, "P(q)", cor=COR_EIXO, negrito=True,
            ancora="end")

    if etapa == 1:
        for d, tr in ((12, "6 4"), (0, None), (-12, "6 4")):
            _reta_lance(p, 8, d, cor=COR_Q if d == 0 else COR_Q_CLARO,
                        tracejado=tr, larg=2.8 if d == 0 else 1.8)
        # A seta do "melhor" e o unico jeito de a figura dizer que a ordem das
        # curvas de lance esta invertida em relacao a toda curva de indiferenca
        # que o curso desenhou ate aqui: aqui o eixo vertical e GASTO.
        p.reta(0.75, 324, 0.75, 294, cor=COR_DESTAQUE, larg=2.2)
        p.t.add('<path d="{} {} {} {} {} {}" fill="{}"/>'.format(
            "M", "{:.1f},{:.1f}".format(*p.p(0.75, 289)), "L",
            "{:.1f},{:.1f}".format(*p.p(0.50, 297)), "L",
            "{:.1f},{:.1f}".format(*p.p(1.00, 297)), COR_DESTAQUE))
        p.texto(1.15, 318, "gasta menos no", cor=COR_DESTAQUE, italico=False)
        p.texto(1.15, 308, "apartamento, sobra", cor=COR_DESTAQUE,
                italico=False)
        p.texto(1.15, 298, "mais para o resto", cor=COR_DESTAQUE,
                italico=False)
        p.texto(7.4, lance(7.4, 8) - 13, "b(q, s₁)", cor=COR_Q,
                negrito=True, ancora="end")
        rod = ("a curva de lance liga as combinações de q e gasto que deixam"
               " o consumidor 1 na mesma utilidade")
    else:
        alvos = ([(8, COR_Q_CLARO)] if etapa == 2
                 else [(8, COR_Q_CLARO), (12, COR_Q)])
        for s, cor in alvos:
            _reta_lance(p, s, cor=cor, larg=2.6)
            q_est = s / 2.0
            p.ponto(q_est, preco(q_est), cor=cor)
            p.guia(q_est, preco(q_est), cor=COR_GUIA)
            p.marca_y(preco(q_est), fmt(preco(q_est), 0), cor=cor)
            p.texto(q_est + JANELA - 0.1, lance(q_est + JANELA, s) + 14,
                    "b(q, s{})".format("₁" if s == 8 else "₂"), cor=cor,
                    negrito=True, ancora="end")
            p.texto(q_est, preco(q_est) - 22,
                    "inclinação {}".format(s), cor=cor, negrito=True,
                    italico=False, ancora="middle")
        if etapa == 2:
            rod = ("no ponto de tangência a inclinação do cardápio é a"
                   " disposição marginal a pagar do consumidor 1: 8")
        else:
            rod = ("o consumidor 2 valoriza mais a qualidade, compra q = 6 e"
                   " paga R$ 336 mil; o cardápio é o mesmo para os dois")
    pontos_cardapio(p, cor=COR_APAGADA, r=3.6, rotular=False)
    rodape(t, LARG, ALT, rod)
    t.salvar(nome, titulos[etapa])


def oferta_fig(nome, com_lance):
    titulo = ("O cardápio é o que sobra quando as duas tangências valem"
              if com_lance else
              "Do lado da oferta, as curvas encostam por cima")
    t, p = cardapio(titulo)
    curva_cardapio(p)
    p.texto(10.7, preco(10.5) + 12, "P(q)", cor=COR_EIXO, negrito=True,
            ancora="end")

    for v, cor, sub in ((4, COR_V_CLARO, "₁"), (6, COR_CMG, "₂")):
        a, b = max(0.0, v - JANELA), min(Q_MAX, v + JANELA)
        p.curva(lambda q, v=v: oferta(q, v), a, b, cor=cor, larg=2.6)
        p.ponto(v, preco(v), cor=cor)
        p.texto(b - 0.1, oferta(b, v) + 14, "θ(q, v{})".format(sub), cor=cor,
                negrito=True, ancora="end")
    if com_lance:
        for s, cor, sub in ((8, COR_Q_CLARO, "₁"), (12, COR_Q, "₂")):
            _reta_lance(p, s, cor=cor, larg=2.4)
            p.texto(s / 2.0 + JANELA - 0.1, lance(s / 2.0 + JANELA, s) - 10,
                    "b(q, s{})".format(sub), cor=cor, negrito=True,
                    ancora="end")
        rod = ("o comprador 1 fecha com a firma 1 em q = 4 e o comprador 2 com"
               " a firma 2 em q = 6: nenhum dos quatro escolheu P(q)")
    else:
        rod = ("θ é o que a firma precisa receber para manter o lucro:"
               " quanto mais alta a curva, melhor para ela")
    pontos_cardapio(p, cor=COR_APAGADA, r=3.6, rotular=False)
    rodape(t, LARG, ALT, rod)
    t.salvar(nome, titulo)


def implicito():
    """A figura que fecha a primeira metade da aula.

    A esquerda o cardapio com as duas tangencias; a direita a INCLINACAO dele.
    Os dois compradores aparecem nos dois paineis, e e assim que fica visivel
    que a reta crescente da direita nao e a demanda de ninguem: cada comprador
    esta num ponto so dela, e a demanda de cada um por qualidade e horizontal,
    porque a utilidade e quase-linear.
    """
    larg_p, alt_p = 356, 336
    t = Tela(2 * larg_p + FOLGA, alt_p + ALTURA_RODAPE)

    pe = Painel(t, 0, larg_p, (0, Q_MAX), (Y_MIN, Y_MAX), alt_p)
    pe.titulo("O cardápio: P(q)")
    pe.eixos("q", "R$ mil")
    pe.curva(preco, 0, Q_MAX, cor=COR_EIXO, larg=2.8)
    pe.marca_y(300, "300")
    pe.marca_y(400, "400")

    pd = Painel(t, larg_p, larg_p, (0, Q_MAX), (0, 23.0), alt_p)
    pd.titulo("A inclinação dele: P′(q)")
    pd.eixos("q", "R$ mil por ponto de q")
    pd.reta(0, 0, Q_MAX, preco_mg(Q_MAX), cor=COR_EIXO, larg=2.8)

    for s, cor, sub in ((8, COR_Q_CLARO, "₁"), (12, COR_Q, "₂")):
        q_est = s / 2.0
        _reta_lance(pe, s, cor=cor, larg=2.4)
        pe.ponto(q_est, preco(q_est), cor=cor)
        pe.marca_x(q_est, fmt(q_est, 0), cor=cor)
        pe.texto(q_est - 0.5, preco(q_est) + (14 if s == 8 else -26),
                 "inclinação {}".format(s), cor=cor, negrito=True,
                 italico=False, ancora="end")

        pd.ponto(q_est, s, cor=cor)
        pd.guia(q_est, s, cor=COR_GUIA)
        pd.marca_x(q_est, fmt(q_est, 0), cor=cor)
        pd.marca_y(s, str(s), cor=cor)
        pd.texto(q_est + 0.3, s - 2.6, "consumidor {}".format(sub), cor=cor,
                 negrito=True)

    pd.texto(9.4, preco_mg(9.4) - 2.4, "P′(q) = 2q", cor=COR_EIXO,
             negrito=True, ancora="end")

    rodape(t, 2 * larg_p, alt_p,
           "a reta da direita sobe, mas ninguém anda sobre ela: cada"
           " consumidor ocupa um ponto só, e é o dele")
    t.salvar("12-implicito.svg", "O cardápio e o preço implícito")


def regressao():
    """O que uma regressao linear devolve, e o que ela nao devolve.

    A inclinacao de MQO dos seis apartamentos e exatamente 10, que nao e a
    disposicao marginal a pagar de nenhum dos quatro compradores. Ela e o preco
    implicito no MEIO da amostra, e e por isso que estimativa hedonica e uma
    medida local.
    """
    titulo = "A regressão linear devolve uma inclinação média"
    t, p = cardapio(titulo)
    p.curva(preco, 0, Q_MAX, cor=COR_APAGADA, larg=2.4)

    media_q = sum(QS) / float(len(QS))
    media_p = sum(preco(q) for q in QS) / float(len(QS))
    cov = sum((q - media_q) * (preco(q) - media_p) for q in QS)
    var = sum((q - media_q) ** 2 for q in QS)
    beta = cov / var
    alfa = media_p - beta * media_q
    p.reta(0, alfa, Q_MAX, alfa + beta * Q_MAX, cor=COR_DESTAQUE, larg=3.0)
    p.texto(9.9, alfa + beta * 9.9 + 16, "MQO: inclinação {}".format(
        fmt(beta, 0)), cor=COR_DESTAQUE, negrito=True, ancora="end")

    pontos_cardapio(p, cor=COR_EIXO, rotular=False)
    p.ponto(media_q, preco(media_q), cor=COR_CMG, r=5.5)
    p.guia(media_q, preco(media_q), cor=COR_GUIA)
    p.marca_x(media_q, "5", cor=COR_CMG)
    p.texto(5.3, preco(5) - 22, "P′(5) = 10", cor=COR_CMG, negrito=True,
            italico=False)

    for a, b in zip(QS, QS[1:]):
        p.texto((a + b) / 2.0, Y_MIN + 8,
                fmt((preco(b) - preco(a)) / (b - a), 0), cor=COR_APAGADA,
                negrito=True, italico=False, ancora="middle")
    p.texto(0.2, Y_MIN + 20, "preço por ponto em cada trecho:",
            cor=COR_APAGADA)

    rodape(t, LARG, ALT,
           "o preço por ponto vai de 2 a 18 ao longo da tabela, e o"
           " coeficiente único de 10 só vale perto do meio")
    t.salvar("12-regressao.svg", titulo)


def exercicio():
    titulo = "Solução do exercício: cada comprador para onde a inclinação bate"
    t, p = cardapio(titulo)
    p.curva(preco, 0, Q_MAX, cor=COR_EIXO, larg=2.6)
    pontos_cardapio(p, cor=COR_APAGADA, r=4.0, rotular=False)

    cores = dict(zip(COMPRADORES, RAMPA))
    for s in COMPRADORES:
        q_est = s / 2.0
        _reta_lance(p, s, cor=cores[s], larg=2.2, q0=max(0.0, q_est - 2.6),
                    q1=min(Q_MAX, q_est + 2.6))
        p.ponto(q_est, preco(q_est), cor=cores[s], r=5.0)
        p.texto(q_est, preco(q_est) + 13, "s = {}".format(s), cor=cores[s],
                negrito=True, italico=False, ancora="middle")
        p.marca_x(q_est, fmt(q_est, 0), cor=cores[s])

    rodape(t, LARG, ALT,
           "quem valoriza mais a qualidade compra mais qualidade, e paga por"
           " ela o que o cardápio pedir: 304, 316, 336 e 364")
    t.salvar("12-exercicio.svg", titulo)


def rdd():
    """Esquema do desenho de descontinuidade, em dois cenarios.

    NAO sao os dados de Greenstone e Gallagher: sao dois cenarios desenhados
    para que a turma veja o que o desenho procura e o que ele encontrou. O
    rodape diz isso, e as notas de orador mandam repetir em voz alta.
    """
    larg_p, alt_p = 356, 336
    t = Tela(2 * larg_p + 52, alt_p + ALTURA_RODAPE)
    rng = random.Random(1974)          # Rosen (1974), para nao esquecer
    corte = 28.5
    nuvem = [12 + 44 * k / 59.0 for k in range(60)]
    ruido = [rng.uniform(-3.4, 3.4) for _ in nuvem]

    for k, (tit, salto) in enumerate([
            ("O que o desenho procura", 7.0),
            ("O que Greenstone e Gallagher acham", 0.0)]):
        p = Painel(t, k * larg_p, larg_p, (10, 58), (-12, 22), alt_p)
        p.titulo(tit)
        p.eixos("HRS", "variação do preço (%)")
        p.reta(10, 0, 58, 0, cor=COR_GUIA, larg=1.1)
        p.marca_y(0, "0")
        p.marca_x(corte, "28,5", cor=COR_DESTAQUE)

        base = lambda h: 0.10 * (h - corte)
        for h, e in zip(nuvem, ruido):
            y = base(h) + e + (salto if h > corte else 0.0)
            p.ponto(h, max(-11.5, min(21.0, y)),
                    cor=COR_Q if h > corte else COR_APAGADA, r=2.8)
        p.reta(10, base(10), corte, base(corte), cor=COR_EIXO, larg=2.4)
        p.reta(corte, base(corte) + salto, 58, base(58) + salto, cor=COR_Q,
               larg=2.4)
        p.reta(corte, -12, corte, 22, cor=COR_DESTAQUE, larg=1.6,
               tracejado="6 4")
        if salto:
            # A chave vertical no corte e o que a figura tem a dizer: sem ela,
            # o salto e uma coisa que o professor aponta e o aluno nao ve.
            for dx in (-0.7, 0.7):
                p.reta(corte + dx - 0.7, 0, corte + dx + 0.7, 0,
                       cor=COR_DESTAQUE, larg=1.8)
            p.reta(corte + 0.7, 0, corte + 0.7, salto, cor=COR_DESTAQUE,
                   larg=2.2)
            p.reta(corte, salto, corte + 1.4, salto, cor=COR_DESTAQUE,
                   larg=1.8)
            p.texto(corte + 2.0, salto / 2.0 - 1.5, "salto", cor=COR_DESTAQUE,
                    negrito=True)
        p.texto(corte - 1.0, 18, "não limpa", cor=COR_APAGADA, negrito=True,
                ancora="end")
        p.texto(corte + 1.0, 18, "limpa", cor=COR_Q, negrito=True)

    rodape(t, 2 * larg_p + 52 - FOLGA, alt_p,
           "esquema, e não os dados do paper: os dois painéis mostram o que o"
           " desenho encontraria em cada caso")
    t.salvar("12-rdd.svg", "Esquema do desenho de descontinuidade")


def main():
    print("aula 12 - precos hedonicos")
    menu("12-menu-1.svg", 1)
    menu("12-menu-2.svg", 2)
    lance_fig("12-lance-1.svg", 1)
    lance_fig("12-lance-2.svg", 2)
    lance_fig("12-lance-3.svg", 3)
    oferta_fig("12-oferta.svg", False)
    oferta_fig("12-equilibrio.svg", True)
    implicito()
    regressao()
    exercicio()
    rdd()
    print()
    print("  conferencia da calibracao:")
    print("    cardapio: " + "  ".join(
        "{}->{}".format(q, fmt(preco(q), 0)) for q in QS))
    for s in COMPRADORES:
        melhor = max(QS, key=lambda q: s * q - preco(q))
        print("    s = {:2d}: tangencia em {}, escolha discreta {},"
              " excedente {}".format(s, fmt(s / 2.0, 0), melhor,
                                     fmt(s * melhor - preco(melhor) + 300, 0)))
    mq = sum(QS) / float(len(QS))
    mp = sum(preco(q) for q in QS) / float(len(QS))
    beta = (sum((q - mq) * (preco(q) - mp) for q in QS)
            / sum((q - mq) ** 2 for q in QS))
    print("    MQO: inclinacao {} (e P'(5) = {})".format(fmt(beta, 4),
                                                         fmt(preco_mg(5), 0)))


if __name__ == "__main__":
    main()
