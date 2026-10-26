#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Gera os diagramas da aula 13 (Recursos Naturais) a partir das equacoes.

MOTIVO DE EXISTIR
-----------------
A aula junta dois `.pptx` (13, sustentabilidade, e 14, nao-renovaveis). O 13
nao tem figura nenhuma alem das fotos do Mar de Aral e do Pantanal: os seis
pontos em que o argumento vira geometria estao marcados LOUSA. O 14 tem duas
figuras, ambas recortadas de Tietenberg e Lewis (figs. 6.2 e 6.3), em ingles e
em escala de cinza.

Aqui as figuras saem todas da MESMA calibracao, que e a do proprio `.pptx` (e a
do livro):

    P_t = a - b q_t = 8 - 0,4 q_t      CMg = c = 2      r = 0,1

    Sem escassez:          q_t = (a - c)/b = 15 em cada geracao
    Estoque 20, 2 periodos: q1* = 10,238   q2* = 9,762   lambda = 1,905
    Estoque 40, N periodos: lambda = 2,798, extracao zera no periodo 9
    Substituto a d = 6:     transicao no periodo 6, consumo de 5 depois
    CMg = 2 + 0,1 Q_t:      custo de usuario cai a zero; extrai-se 40
    idem + dano de 1:       extrai-se 30, transicao um periodo antes

O caso de custo crescente nao tem tabela no livro (so a figura 6.5): os numeros
sao resolvidos aqui, por gradiente projetado, e conferidos pela condicao de
primeira ordem (custo de usuario = soma descontada do aumento de custo que a
unidade de hoje impoe ao futuro).

O EXERCICIO
-----------
O `.pptx` 14 termina num exercicio de recurso parcialmente renovavel marcado
LOUSA. A versao numerica escolhe estoque 21 e crescimento s = r = 0,1, para
que a resposta caia exata:

    BMgL_1 = (1+s)/(1+r) BMgL_2   e   q2 = (1+s)(21 - q1)
    =>  q1* = q2* = 11,  BMgL = 1,6,  V = 41,8 nas duas geracoes

Ou seja, quando o estoque rende o mesmo que o banco, a alocacao eficiente e
igualitaria, e a tensao entre eficiencia e equidade da primeira metade da aula
desaparece.

Depende so da biblioteca padrao, como os outros scripts desta pasta.

    py scripts/figuras13svg.py

Escreve em aulas/_assets/figuras/.
"""

from figuras04svg import (Painel, Tela, COR_EIXO, COR_CMG, COR_DANO, COR_GUIA,
                          COR_APAGADA, COR_DESTAQUE, FONTE, FONTE_EIXO,
                          FONTE_TITULO, FONTE_LEGENDA)
from figuras08svg import fmt
from figuras11svg import COR_Q, COR_PROD, FOLGA, ALTURA_RODAPE, rodape, moldura

# Quinta cor do curso. Ate aqui nao havia "o futuro" em nenhuma figura: toda
# economia desenhada era de um periodo so. A geracao presente fica com o verde
# do mercado do produto (aula 10), porque o recurso extraido E o produto, e a
# geracao futura ganha laranja. Vermelho continua custo de extracao; o azul
# escuro de destaque e o custo marginal da escassez e o custo marginal total,
# que sao o objeto principal da aula. Roxo (bem ambiental, aula 11) passa a
# marcar o recurso RENOVAVEL substituto.
COR_FUT = "#C26A00"
COR_FUT_CLARO = "#E8B57A"
COR_PROD_CLARO = "#9CCB9E"

# --- a calibracao -----------------------------------------------------------

A, B, C, R = 8.0, 0.4, 2.0, 0.1
D_SUB = 6.0                 # custo marginal do substituto renovavel
ALFA = 0.1                  # inclinacao do custo de extracao crescente
DANO = 1.0                  # custo ambiental por unidade extraida
BETA = 1.0 / (1.0 + R)

bmgl = lambda q: A - C - B * q                 # beneficio marginal liquido
v_liq = lambda q: (A - C) * q - B / 2.0 * q * q   # V(q), beneficio liquido


def bissec(f, lo, hi, n=200):
    """Raiz de f decrescente em [lo, hi]."""
    for _ in range(n):
        m = (lo + hi) / 2.0
        if f(m) > 0:
            lo = m
        else:
            hi = m
    return (lo + hi) / 2.0


def dois_periodos(estoque, r=R, s=0.0):
    """Alocacao eficiente em dois periodos; s e o crescimento do estoque."""
    k = (1.0 + s) / (1.0 + r)
    # BMgL_1(q1) = k BMgL_2((1+s)(estoque - q1))
    q1 = bissec(lambda q: bmgl(q) - k * bmgl((1 + s) * (estoque - q)),
                0.0, estoque)
    return q1, (1 + s) * (estoque - q1), bmgl(q1)


Q1, Q2, LAM = dois_periodos(20.0)
LAM2 = LAM * (1 + R)                            # custo de usuario corrente em t=2
V1, V2, V_IGUAL = v_liq(Q1), v_liq(Q2), v_liq(10.0)
SOBRA = V1 - V_IGUAL
V2_COM = V2 + SOBRA * (1 + R)

assert abs(Q1 - 10.238) < 1e-3 and abs(LAM - 1.905) < 1e-3
assert abs(LAM2 / LAM - (1 + R)) < 1e-12        # regra de Hotelling
assert abs(dois_periodos(20.0, r=0.0)[0] - 10.0) < 1e-9
assert abs(dois_periodos(20.0, r=0.5)[0] - 11.0) < 1e-9
# o livro arredonda q1 antes de calcular V: 40,466 e 39,512
assert abs(V1 - 40.466) < 3e-3 and abs(V2 - 39.512) < 3e-3
assert V2_COM > V_IGUAL

# Exercicio: estoque 21, crescimento s = r
EX_Q1, EX_Q2, EX_BMGL = dois_periodos(21.0, s=R)
assert abs(EX_Q1 - 11.0) < 1e-9 and abs(EX_Q2 - 11.0) < 1e-9
assert abs(EX_BMGL - 1.6) < 1e-9


# --- N periodos, custo constante -------------------------------------------

def n_periodos(estoque=40.0, horizonte=30):
    qs = lambda l: [max(0.0, (A - C - l * (1 + R) ** t) / B)
                    for t in range(horizonte)]
    lam = bissec(lambda l: sum(qs(l)) - estoque, 0.01, A - C)
    return lam, qs(lam)


LAM_N, Q_N = n_periodos()
assert abs(LAM_N - 2.7983) < 1e-4
assert Q_N[7] > 1.0 and Q_N[8] < 0.01           # zera no periodo 9


def com_substituto(estoque=40.0):
    """Troca no periodo T em que lambda (1+r)^(T-1) = d - c (ver apendice 6)."""
    for T in range(1, 30):
        lam = (D_SUB - C) / (1 + R) ** (T - 1)
        q = [(A - C - lam * (1 + R) ** t) / B for t in range(T - 1)]
        resto = estoque - sum(q)
        if 0.0 <= resto <= (A - D_SUB) / B:
            return T, lam, q + [resto]
    raise SystemExit("sem ponto de troca")


T_SUB, LAM_SUB, Q_SUB = com_substituto()
assert T_SUB == 6 and abs(LAM_SUB - 2.4837) < 1e-4
Q_RENOV = (A - D_SUB) / B                       # 5: consumo depois da troca


# --- custo de extracao crescente --------------------------------------------

def custo_crescente(c0, horizonte=20, iteracoes=20000, passo=0.5,
                    imposto=lambda t: 0.0):
    """Maximiza o VP do beneficio liquido com CMg_t = c0 + alfa Q_t.

    imposto(t) e o imposto por unidade no periodo t + 1 (paradoxo verde);
    entra como custo de extracao, e o substituto renovavel nao paga.

    O substituto e escolhido periodo a periodo (s_t = max(0, 5 - q_t)), entao
    o preco e a - b max(q_t, 5). O gradiente em q_t e
        beta^(t-1) [P_t - c0 - alfa Q_t] - alfa sum_{k>t} beta^(k-1) q_k
    e o problema e concavo: gradiente projetado em q >= 0 converge.

    Nao ha restricao de estoque: o resultado vale para qualquer estoque
    >= 40. O slide usa 60, para que algo fique no solo (com 40, nao fica).
    """
    q = [1.0] * horizonte
    for _ in range(iteracoes):
        cum, acc = [], 0.0
        for x in q:
            acc += x
            cum.append(acc)
        cauda, g = 0.0, [0.0] * horizonte
        for t in range(horizonte - 1, -1, -1):
            preco = A - B * max(q[t], Q_RENOV)
            g[t] = (BETA ** t * (preco - c0 - imposto(t) - ALFA * cum[t])
                    - cauda)
            cauda += BETA ** t * ALFA * q[t]
        q = [max(0.0, x + passo * gx) for x, gx in zip(q, g)]
    acc, linhas = 0.0, []
    for t, x in enumerate(q):
        acc += x
        preco = A - B * max(x, Q_RENOV)
        linhas.append((t + 1, x, acc, preco, c0 + ALFA * acc))
    return linhas


CC = custo_crescente(C)
CA = custo_crescente(C + DANO)


def troca(linhas):
    return next(t for t, x, _, _, _ in linhas if x < Q_RENOV - 1e-6)


assert abs(CC[-1][2] - 40.0) < 1e-3 and abs(CA[-1][2] - 30.0) < 1e-3
assert troca(CC) == 7 and troca(CA) == 6
# custo de usuario na troca e zero, e decrescente antes dela
muc = [p - m for _, _, _, p, m in CC]
assert abs(muc[troca(CC) - 1]) < 1e-3
assert all(a > b for a, b in zip(muc[:6], muc[1:7]))
# confere a condicao de primeira ordem no periodo 1
cauda1 = sum(BETA ** k * ALFA * CC[k][1] for k in range(1, len(CC)))
assert abs(muc[0] - cauda1) < 1e-3


# --- paradoxo verde (Sinn, 2008) --------------------------------------------
#
# O modelo de N periodos com estoque 40, sem substituto. Cada unidade emite
# uma unidade de CO2, e os donos pagam um imposto por unidade
#     tau_t = 0,5 (1 + g)^(t-1).
# A CPO vira (a - b q_t - c - tau_t)/(1+r)^(t-1) = lambda. Com g = r, o termo
# tau_t/(1+r)^(t-1) e constante (0,5) e o imposto so reduz lambda: a extracao
# nao muda. Com g > r, adiar fica mais caro e a extracao se antecipa.

TAU0 = 0.5
G_SINN = 0.3

def n_periodos_imposto(imposto, estoque=40.0, horizonte=30):
    qs = lambda l: [max(0.0, (A - C - imposto(t) - l * (1 + R) ** t) / B)
                    for t in range(horizonte)]
    lam = bissec(lambda l: sum(qs(l)) - estoque, -5.0, A - C)
    return lam, qs(lam)


def vp(qs):
    """VP do dano, com dano de 1 por unidade extraida."""
    return sum(DANO * q / (1 + R) ** t for t, q in enumerate(qs))


def ultimo(qs):
    return max(t for t, q in enumerate(qs) if q > 0.01) + 1


IMPOSTOS = (("sem imposto", lambda t: 0.0),
            ("constante, 0,5", lambda t: TAU0),
            ("cresce 10% (= r)", lambda t: TAU0 * (1 + R) ** t),
            ("cresce 30%", lambda t: TAU0 * (1 + G_SINN) ** t))
SINN = [(nome,) + n_periodos_imposto(f) for nome, f in IMPOSTOS]
Q_SINN = SINN[3][2]

assert all(abs(sum(q) - 40.0) < 1e-6 for _, _, q in SINN)  # total nao muda
# imposto que cresce a r e neutro: cai todo sobre a renda de escassez
assert abs(SINN[2][1] - (LAM_N - TAU0)) < 1e-6
assert max(abs(x - y) for x, y in zip(SINN[2][2], Q_N)) < 1e-6
assert [ultimo(q) for _, _, q in SINN] == [8, 9, 8, 7]
assert abs(Q_SINN[0] - 9.22) < 5e-3 and abs(sum(Q_SINN[:3]) - 25.0) < 5e-3
assert [round(vp(q), 2) for _, _, q in SINN] == [32.06, 31.60, 32.06, 33.32]

# com custo crescente (sem dano), o mesmo imposto de 30%
CS = custo_crescente(C, iteracoes=40000,
                     imposto=lambda t: TAU0 * (1 + G_SINN) ** t)
assert CS[0][1] > CC[0][1]                       # ainda antecipa
assert abs(CS[-1][2] - 26.78) < 1e-2             # mas deixa mais no solo


# ===========================================================================
# Molduras
# ===========================================================================

class PainelDuplo(Painel):
    """Painel com eixo vertical tambem a direita (a geracao 2 e lida de la)."""
    MARG_DIR = 74


LARG, ALT = 700, 340


def quadro_dois(titulo, estoque, y_max=7.0):
    t = Tela(LARG + FOLGA, ALT + ALTURA_RODAPE)
    p = PainelDuplo(t, 0, LARG, (0, estoque), (0, y_max), ALT)
    p.titulo(titulo)
    x0, x1, y0 = p.px(0), p.px(estoque), p.py(0)
    for xa in (x0, x1):
        t.add('<line x1="{:.1f}" y1="{:.1f}" x2="{:.1f}" y2="{:.1f}"'
              ' stroke="{}" stroke-width="1.2" marker-end="url(#seta)"/>'
              .format(xa, y0, xa, p.py(y_max) - 8, COR_EIXO))
    t.add('<line x1="{:.1f}" y1="{:.1f}" x2="{:.1f}" y2="{:.1f}"'
          ' stroke="{}" stroke-width="1.2"/>'.format(x0, y0, x1, y0, COR_EIXO))
    p.texto(x0 + 8, p.py(y_max) - 8, "benefício marginal líquido (VP)",
            absoluto=True, tam=FONTE_EIXO)
    # Duas fileiras de marcas: q1 cresce da esquerda, q2 da direita. As duas
    # somam o estoque em qualquer ponto do eixo, e e isso que faz o cruzamento
    # ser a alocacao.
    p.texto(x0 - 10, y0 + 20, "q₁ →", absoluto=True, cor=COR_PROD,
            ancora="end", negrito=True)
    p.texto(x1 + 12, y0 + 40, "← q₂", absoluto=True, cor=COR_FUT,
            negrito=True, ancora="start")
    return t, p


def marcas_q(p, estoque, pontos, cor1=COR_PROD, cor2=COR_FUT, fator=1.0):
    for q1 in pontos:
        p.marca_x(q1, fmt(q1, 2), cor=cor1)
        p.texto(p.px(q1), p.py(0) + 40, fmt(fator * (estoque - q1), 2),
                absoluto=True, cor=cor2, ancora="middle", italico=False)


def marca_dir(p, x, y, rotulo, cor):
    p.texto(p.px(x) + 8, p.py(y) + 5, rotulo, absoluto=True, cor=cor,
            italico=False)


# ===========================================================================
# Bloco 1 - dois periodos
# ===========================================================================

def sem_escassez():
    larg_p, alt_p = 363, 300
    t = Tela(2 * larg_p + FOLGA, alt_p + ALTURA_RODAPE)
    for k, tit in enumerate(("Geração 1", "Geração 2")):
        p = Painel(t, k * larg_p, larg_p, (0, 21), (0, 9.2), alt_p)
        p.titulo(tit)
        p.eixos("q", "R$ por unidade")
        p.area([(0, C), (15, C), (0, A)], COR_PROD, 0.18)
        p.reta(0, A, 20, 0, cor=COR_PROD, larg=2.6)
        p.reta(0, C, 20.5, C, cor=COR_CMG, larg=2.6)
        p.guia(15, C)
        p.ponto(15, C)
        p.marca_x(15, "15")
        p.marca_y(C, "2")
        p.marca_y(A, "8")
        p.texto(4.0, 3.6, "45", cor=COR_PROD, negrito=True, italico=False,
                tam=FONTE_EIXO)
        p.texto(9.0, 5.2, "P = 8 − 0,4q", cor=COR_PROD, negrito=True)
        p.texto(20.3, C + 0.45, "CMg = 2", cor=COR_CMG, negrito=True,
                ancora="end")
    rodape(t, 2 * larg_p, alt_p,
           "sem escassez, cada geração extrai 15 e obtém benefício líquido"
           " de 45: são 30 unidades no total")
    t.salvar("13-sem-escassez.svg", "Alocação sem escassez")


def dois_periodos_fig(nome, etapa):
    titulos = {
        1: "Geração presente: benefício marginal líquido",
        2: "Geração futura, lida da direita e trazida a valor presente",
        3: "A alocação eficiente é o cruzamento",
    }
    t, p = quadro_dois(titulos[etapa], 20.0)
    if etapa == 3:
        # As duas areas somam o VP do beneficio liquido. Qualquer outro ponto
        # do eixo perde um triangulo entre as curvas.
        p.area([(0, 0), (0, A - C), (Q1, LAM), (Q1, 0)], COR_PROD, 0.18)
        p.area([(Q1, 0), (Q1, LAM), (20, (A - C) / (1 + R)), (20, 0)],
               COR_FUT, 0.18)
    p.reta(0, A - C, 15, 0, cor=COR_PROD, larg=2.8)
    p.marca_y(A - C, "6")
    p.texto(2.2, 5.6, "BMgL₁ = 6 − 0,4q₁", cor=COR_PROD, negrito=True)
    if etapa >= 2:
        p.reta(5, 0, 20, (A - C) / (1 + R), cor=COR_FUT, larg=2.8)
        marca_dir(p, 20, (A - C) / (1 + R), "5,45", COR_FUT)
        p.texto(19.6, 6.25, "(6 − 0,4q₂)/1,1", cor=COR_FUT, negrito=True,
                ancora="end")
    if etapa == 3:
        p.guia(Q1, LAM, cor=COR_DESTAQUE)
        p.ponto(Q1, LAM, r=6)
        p.marca_y(LAM, "1,905", cor=COR_DESTAQUE)
        p.texto(0.5, LAM + 0.25, "λ", cor=COR_DESTAQUE, negrito=True,
                tam=FONTE_EIXO)
        marcas_q(p, 20.0, [Q1])
    else:
        marcas_q(p, 20.0, [0, 5, 15, 20])
    rodapes = {
        1: "a − c − b q₁: vale 6 na primeira unidade e zera em 15, onde"
           " o preço iguala o custo de extração",
        2: "a curva da geração 2 começa em 6/1,1 = 5,45: o benefício futuro"
           " é descontado",
        3: "no cruzamento, q₁* = 10,24 e q₂* = 9,76; a altura λ = 1,905 é o"
           " custo marginal da escassez",
    }
    rodape(t, LARG, ALT, rodapes[etapa])
    t.salvar(nome, titulos[etapa])


def precos():
    larg_p, alt_p = 363, 310
    t = Tela(2 * larg_p + FOLGA, alt_p + ALTURA_RODAPE)
    for k, (q, lam, sub) in enumerate(((Q1, LAM, "₁"), (Q2, LAM2, "₂"))):
        p = Painel(t, k * larg_p, larg_p, (0, 21), (0, 9.2), alt_p)
        p.titulo("Geração " + str(k + 1))
        p.eixos("q", "R$ por unidade")
        p.reta(0, A, 20, 0, cor=COR_PROD, larg=2.6)
        p.reta(0, C, 20.5, C, cor=COR_CMG, larg=2.6)
        preco = A - B * q
        p.guia(q, preco)
        p.ponto(q, preco)
        p.ponto(15, C, cor=COR_APAGADA, r=4)
        p.marca_x(q, fmt(q, 2))
        p.marca_y(C, "2")
        p.marca_y(preco, fmt(preco, 3))
        # O retangulo entre o custo de extracao e o preco, ate q, e a renda de
        # escassez da geracao; sua ALTURA e o custo de usuario, e e ela que
        # cresce de um painel para o outro. Fica a esquerda do ponto porque ali
        # a demanda esta acima e o retangulo nao cruza curva nenhuma.
        p.area([(0, C), (q, C), (q, preco), (0, preco)], COR_DESTAQUE, 0.14)
        p.texto(q / 2.0, (C + preco) / 2 - 0.3,
                "λ{} = {}".format(sub, fmt(lam, 3)), cor=COR_DESTAQUE,
                negrito=True, italico=False, ancora="middle")
        p.marca_y(A, "8")
        p.texto(20.3, C - 0.8, "CMg = 2", cor=COR_CMG, negrito=True,
                ancora="end")
    rodape(t, 2 * larg_p, alt_p,
           "preço = custo de extração + custo de usuário; o custo de usuário"
           " cresce de 1,905 para 2,095, isto é, 10%")
    t.salvar("13-precos.svg", "Preço e custo de usuário nas duas gerações")


def desconto():
    t, p = quadro_dois("A taxa de desconto gira a curva da geração futura",
                       20.0)
    p.reta(0, A - C, 15, 0, cor=COR_PROD, larg=2.8)
    p.marca_y(A - C, "6")
    p.texto(2.2, 5.6, "BMgL₁", cor=COR_PROD, negrito=True)
    casos = ((0.0, COR_FUT_CLARO, "r = 0"), (0.1, COR_FUT, "r = 0,1"),
             (0.5, "#7A4100", "r = 0,5"))
    for r, cor, rot in casos:
        topo = (A - C) / (1 + r)
        p.reta(5, 0, 20, topo, cor=cor, larg=2.6)
        q1, _, lam = dois_periodos(20.0, r=r)
        p.ponto(q1, lam, cor=cor, r=5)
        marca_dir(p, 20, topo, rot, cor)
    p.ponto(5, 0, cor=COR_EIXO, r=4)
    marcas_q(p, 20.0, [5, 10, 11])
    rodape(t, LARG, ALT,
           "todas giram em torno de q₁ = 5; com r = 0, 0,1 e 0,5 a geração"
           " presente fica com 10, 10,24 e 11")
    t.salvar("13-desconto.svg", "Efeito da taxa de desconto")


def bem_estar(nome, etapa):
    titulo = ("Benefício líquido de cada geração" if etapa == 1 else
              "Com transferência, a geração futura também ganha")
    t = Tela(LARG + FOLGA, ALT + ALTURA_RODAPE)
    p = Painel(t, 0, LARG, (0, 3.3), (39.2, 40.8), ALT)
    p.titulo(titulo)
    p.eixos("", "V(q) por geração")
    for v in (39.5, 40.0, 40.5):
        p.marca_y(v, fmt(v, 1))
    p.reta(0, 40, 3.2, 40, cor=COR_GUIA, larg=1.1, tracejado="4 3")
    grupos = [("eficiente,", "sem transferência", V1, V2),
              ("igualitária", "(10 e 10)", V_IGUAL, V_IGUAL)]
    if etapa == 2:
        grupos.append(("eficiente,", "com transferência", V_IGUAL, V2_COM))
    for k, (l1, l2, a, b) in enumerate(grupos):
        x = 0.55 + 1.05 * k
        for dx, v, cor, ger in ((-0.17, a, COR_PROD, "G1"),
                                (0.17, b, COR_FUT, "G2")):
            p.reta(x + dx, 39.2, x + dx, v, cor=cor, larg=1.4,
                   tracejado="3 3")
            p.ponto(x + dx, v, cor=cor, r=7)
            p.texto(x + dx, v + 0.09, fmt(v, 2), cor=cor, negrito=True,
                    italico=False, ancora="middle")
            p.texto(x + dx, 39.27, ger, cor=cor, italico=False,
                    ancora="middle")
        p.texto(p.px(x), p.py(39.2) + 20, l1, absoluto=True, ancora="middle",
                italico=False)
        p.texto(p.px(x), p.py(39.2) + 38, l2, absoluto=True, ancora="middle",
                italico=False)
    rod = ("o eixo vertical começa em 39,2; a eficiente dá 40,46 à geração 1"
           " e 39,51 à geração 2, abaixo dos 40 da igualitária"
           if etapa == 1 else
           "a geração 1 guarda 40 e aplica a sobra de 0,46 a 10%:"
           " a geração 2 recebe 39,51 + 0,51 = 40,02")
    rodape(t, LARG, ALT, rod)
    t.salvar(nome, titulo)


# ===========================================================================
# Bloco 2 - reservas
# ===========================================================================

def seta_grossa(t, xa, ya, xb, yb, cor=COR_DESTAQUE):
    """Seta de 3px com ponta desenhada: o marker do Tela escala com a
    espessura do traco e, a 3px, sai do tamanho de um polegar."""
    import math
    ang = math.atan2(yb - ya, xb - xa)
    bx, by = xb - 12 * math.cos(ang), yb - 12 * math.sin(ang)
    t.add('<line x1="{:.1f}" y1="{:.1f}" x2="{:.1f}" y2="{:.1f}" stroke="{}"'
          ' stroke-width="3"/>'.format(xa, ya, bx, by, cor))
    pts = [(xb, yb)] + [(bx + 7 * math.cos(ang + s), by + 7 * math.sin(ang + s))
                        for s in (math.pi / 2, -math.pi / 2)]
    t.add('<path d="M {:.1f} {:.1f} L {:.1f} {:.1f} L {:.1f} {:.1f} Z"'
          ' fill="{}"/>'.format(pts[0][0], pts[0][1], pts[1][0], pts[1][1],
                               pts[2][0], pts[2][1], cor))


def mckelvey():
    larg, alt = 700, 330
    t = Tela(larg + FOLGA, alt + ALTURA_RODAPE)
    t.texto((larg + FOLGA) / 2, 17, "Diagrama de McKelvey",
            tam=FONTE_TITULO, negrito=True, ancora="middle")
    x0, x1, xm = 120, 680, 420
    y0, y1, ym = 64, 300, 170
    t.add('<rect x="{}" y="{}" width="{}" height="{}" fill="{}"'
          ' fill-opacity="0.85"/>'.format(x0, y0, xm - x0, ym - y0,
                                          COR_PROD_CLARO))
    t.add('<rect x="{}" y="{}" width="{}" height="{}" fill="none"'
          ' stroke="{}" stroke-width="1.6"/>'.format(x0, y0, x1 - x0,
                                                   y1 - y0, COR_EIXO))
    for a, b, c, d in ((xm, y0, xm, y1), (x0, ym, x1, ym)):
        t.add('<line x1="{}" y1="{}" x2="{}" y2="{}" stroke="{}"'
              ' stroke-width="1.2" stroke-dasharray="6 4"/>'
              .format(a, b, c, d, COR_EIXO))
    t.texto((x0 + xm) / 2, y0 - 10, "identificados", ancora="middle",
            tam=FONTE_EIXO)
    t.texto((xm + x1) / 2, y0 - 10, "não descobertos", ancora="middle",
            tam=FONTE_EIXO)
    t.texto(x0 - 10, (y0 + ym) / 2 + 6, "econômicos", ancora="end",
            tam=FONTE_EIXO)
    t.texto(x0 - 10, (ym + y1) / 2 - 4, "sub-", ancora="end", tam=FONTE_EIXO)
    t.texto(x0 - 10, (ym + y1) / 2 + 18, "econômicos", ancora="end",
            tam=FONTE_EIXO)
    t.texto((x0 + xm) / 2, (y0 + ym) / 2 - 4, "RESERVAS ATUAIS",
            ancora="middle", negrito=True, tam=FONTE_EIXO, cor="#1B5E20")
    t.texto((x0 + xm) / 2, (y0 + ym) / 2 + 20, "lucrativas aos preços atuais",
            ancora="middle", cor="#1B5E20")
    t.texto((xm + x1) / 2, (ym + y1) / 2 - 4,
            "dotação: o retângulo todo,", ancora="middle",
            italico=True, cor=COR_GUIA)
    t.texto((xm + x1) / 2, (ym + y1) / 2 + 18, "conceito geológico",
            ancora="middle", italico=True, cor=COR_GUIA)
    # As duas setas dizem para onde a fronteira das reservas anda: para baixo
    # quando o preco sobe ou a tecnologia barateia a extracao, para a direita
    # quando a exploracao descobre jazidas.
    seta_grossa(t, 210, ym - 14, 210, ym + 56)
    t.texto(222, ym + 30, "preço maior,", cor=COR_DESTAQUE, negrito=True)
    t.texto(222, ym + 50, "tecnologia", cor=COR_DESTAQUE, negrito=True)
    seta_grossa(t, xm - 16, y0 + 30, xm + 74, y0 + 30)
    t.texto(xm + 80, y0 + 36, "exploração", cor=COR_DESTAQUE, negrito=True)
    t.texto(x0, y1 + 24, "certeza geológica decrescente →", cor=COR_GUIA)
    rodape(t, larg, alt,
           "a fronteira das reservas atuais se move com o preço, a tecnologia"
           " e a exploração; a dotação total não")
    t.salvar("13-mckelvey.svg", "Diagrama de McKelvey")


# Keohane e Olmstead (2016), tabela 11.1, calculada pelos autores com dados da
# EIA: reservas provadas de petroleo divididas pela producao anual.
RESERVAS = [(1980, 28), (1985, 32), (1990, 41), (1995, 39), (2000, 36),
            (2005, 41), (2010, 42), (2013, 50)]


def reservas():
    t = Tela(LARG + FOLGA, ALT + ALTURA_RODAPE)
    n = len(RESERVAS)
    p = Painel(t, 0, LARG, (0, n), (0, 60), ALT)
    p.titulo("Reservas provadas de petróleo divididas pela produção anual")
    p.eixos("", "anos de produção")
    for v in (20, 40):
        p.marca_y(v, str(v))
    for k, (ano, anos) in enumerate(RESERVAS):
        x = k + 0.5
        cor = COR_DESTAQUE if k in (0, n - 1) else COR_GUIA
        p.area([(x - 0.32, 0), (x - 0.32, anos), (x + 0.32, anos),
                (x + 0.32, 0)], cor, 0.85)
        p.texto(x, anos + 1.6, str(anos), cor=cor, negrito=True,
                italico=False, ancora="middle")
        p.marca_x(x, str(ano))
        p.texto(p.px(x), p.py(0) + 40, str(ano + anos), absoluto=True,
                cor=COR_CMG, ancora="middle", italico=False, negrito=True)
    p.texto(p.px(0) - 8, p.py(0) + 40, "fim:", absoluto=True, cor=COR_CMG,
            ancora="end", italico=False, negrito=True)
    rodape(t, LARG, ALT,
           "em vermelho, o ano de esgotamento que cada índice indicava")
    t.salvar("13-reservas.svg", "Índice reservas sobre produção")


# Reciclagem (Tietenberg e Lewis, fig. 8.4, com numeros). O eixo e a parcela
# do lixo reciclada; o custo liquido de reciclar (custo menos valor da sucata)
# cresce porque cada ponto percentual a mais exige material mais dificil.
# Com taxa de coleta fixa, a familia so enxerga o proprio incomodo de descartar
# (4 por tonelada); a cidade paga 20 por tonelada aterrada.
CMR = lambda x: 0.4 * x
CMP, CMS = 4.0, 20.0
X_MERC, X_EF = CMP / 0.4, CMS / 0.4
PERDA_REC = 0.5 * (X_EF - X_MERC) * (CMS - CMP)
assert abs(X_MERC - 10) < 1e-9 and abs(X_EF - 50) < 1e-9
assert abs(PERDA_REC - 320) < 1e-9


def reciclagem():
    titulo = "Quanto se recicla: decisão privada e ótimo social"
    t, p = moldura(titulo, LARG, ALT, (0, 80), (0, 26), "x",
                   "R$ por tonelada")
    # a perda: toneladas entre 10% e 50% que a sociedade gostaria de
    # reciclar (o descarte evitado vale mais que o custo) e a familia nao
    p.area([(X_MERC, CMR(X_MERC)), (X_EF, CMS), (X_MERC, CMS)], COR_DANO,
           0.16)
    p.reta(0, 0, 65, CMR(65), cor=COR_CMG, larg=2.8)
    p.reta(0, CMS, 78, CMS, cor=COR_DANO, larg=2.6)
    p.reta(0, CMP, 78, CMP, cor=COR_DANO, larg=2.2, tracejado="7 4")
    p.texto(64, CMR(64) + 0.9, "custo líquido de reciclar", cor=COR_CMG,
            negrito=True, ancora="end")
    p.texto(78, CMS + 0.8, "custo social do descarte", cor=COR_DANO,
            negrito=True, ancora="end")
    p.texto(78, CMP + 0.8, "custo do descarte para a família",
            cor=COR_DANO, negrito=True, ancora="end")
    for x, y in ((X_MERC, CMP), (X_EF, CMS)):
        p.guia(x, y)
        p.ponto(x, y, r=5.5)
    p.marca_x(X_MERC, "10%")
    p.marca_x(X_EF, "50%")
    p.marca_y(CMP, "4")
    p.marca_y(CMS, "20")
    p.texto(22, 15.2, "320", cor=COR_DANO, negrito=True, italico=False,
            tam=FONTE_EIXO)
    rodape(t, LARG, ALT,
           "com taxa fixa, a família recicla 10% do lixo; o ótimo é 50%. A"
           " área sombreada é a perda: 320")
    t.salvar("13-reciclagem.svg", titulo)


# ===========================================================================
# Bloco 3 - N periodos
# ===========================================================================

LARG_P2, ALT_P2 = 363, 320


def par_temporal(titulo_a, titulo_b, t_max, ymax_q=10.0, ymax_c=9.0,
                 ymin_c=0.0):
    t = Tela(2 * LARG_P2 + FOLGA, ALT_P2 + ALTURA_RODAPE)
    pa = Painel(t, 0, LARG_P2, (0, t_max + 0.6), (0, ymax_q), ALT_P2)
    pb = Painel(t, LARG_P2, LARG_P2, (0, t_max + 0.6), (ymin_c, ymax_c),
                ALT_P2)
    pa.titulo(titulo_a)
    pb.titulo(titulo_b)
    pa.eixos("t", "quantidade extraída")
    pb.eixos("t", "R$ por unidade")
    for p in (pa, pb):
        for k in range(1, t_max + 1):
            p.marca_x(k, str(k))
    for v in (2, 4, 6, 8):
        pa.marca_y(v, str(v))
        if ymin_c < v < ymax_c:
            pb.marca_y(v, str(v))
    return t, pa, pb


def serie(p, pts, cor, larg=2.6, tracejado=None, r=4.2, pontos=True):
    for (xa, ya), (xb, yb) in zip(pts, pts[1:]):
        p.reta(xa, ya, xb, yb, cor=cor, larg=larg, tracejado=tracejado)
    if pontos:
        for x, y in pts:
            p.ponto(x, y, cor=cor, r=r)


def n_periodos_fig():
    t, pa, pb = par_temporal("Extração por período", "Custos marginais", 10)
    qs = [(k + 1, q) for k, q in enumerate(Q_N[:9])]
    serie(pa, qs, COR_PROD)
    pa.texto(1.3, Q_N[0] + 0.5, "8,0", cor=COR_PROD, negrito=True,
             italico=False)
    cmt = [(k + 1, C + LAM_N * (1 + R) ** k) for k in range(9)]
    pb.reta(0.4, A, 10.4, A, cor=COR_GUIA, larg=1.2, tracejado="5 4")
    pb.texto(10.4, A + 0.3, "a = 8", cor=COR_GUIA, ancora="end",
             negrito=True)
    pb.reta(1, C, 9, C, cor=COR_CMG, larg=2.6)
    pb.texto(9.2, C + 0.35, "extração", cor=COR_CMG, negrito=True,
             ancora="end")
    serie(pb, cmt, COR_DESTAQUE)
    pb.texto(2.6, 4.1, "custo marginal total", cor=COR_DESTAQUE,
             negrito=True)
    rodape(t, 2 * LARG_P2, ALT_P2,
           "estoque de 40: o custo marginal total sobe de 4,80 a 8 e a"
           " extração zera no período 9")
    t.salvar("13-n-periodos.svg", "Extração com N períodos")


def substituto_fig():
    t, pa, pb = par_temporal("Extração e consumo", "Custos marginais", 10)
    # o caminho sem substituto fica por baixo, apagado, para a comparacao
    serie(pa, [(k + 1, q) for k, q in enumerate(Q_N[:9])], COR_APAGADA,
          larg=2.0, r=3.2)
    serie(pa, [(k + 1, q) for k, q in enumerate(Q_SUB)], COR_PROD)
    serie(pa, [(T_SUB, Q_RENOV - Q_SUB[-1])] +
          [(k, Q_RENOV) for k in range(T_SUB + 1, 11)], COR_Q, r=3.6)
    pa.texto(9.8, Q_RENOV + 0.55, "renovável", cor=COR_Q, negrito=True,
             ancora="end")
    pa.texto(1.3, Q_SUB[0] + 0.55, "não renovável", cor=COR_PROD,
             negrito=True)
    pa.reta(T_SUB, 0, T_SUB, 9.4, cor=COR_GUIA, larg=1.1, tracejado="4 3")
    pb.reta(1, C, T_SUB, C, cor=COR_CMG, larg=2.6)
    pb.texto(1.2, C - 0.6, "extração", cor=COR_CMG, negrito=True)
    serie(pb, [(k + 1, C + LAM_N * (1 + R) ** k) for k in range(9)],
          COR_APAGADA, larg=2.0, r=3.2)
    cmt = [(k + 1, C + LAM_SUB * (1 + R) ** k) for k in range(T_SUB)]
    serie(pb, cmt, COR_DESTAQUE)
    pb.reta(T_SUB, D_SUB, 10.4, D_SUB, cor=COR_Q, larg=2.6)
    pb.texto(10.4, D_SUB + 0.35, "d = 6", cor=COR_Q, negrito=True,
             ancora="end")
    pb.reta(T_SUB, 0, T_SUB, 8.6, cor=COR_GUIA, larg=1.1, tracejado="4 3")
    rodape(t, 2 * LARG_P2, ALT_P2,
           "com substituto a 6, a troca ocorre no período 6 (em cinza, o caso"
           " sem substituto); depois, consumo de 5")
    t.salvar("13-substituto.svg", "Transição para recurso renovável")


def crescente_fig():
    t, pa, pb = par_temporal("Extração e consumo", "Custos marginais", 10)
    tc = troca(CC)
    serie(pa, [(k, x) for k, x, _, _, _ in CC[:tc]], COR_PROD)
    serie(pa, [(k, Q_RENOV - x) for k, x, _, _, _ in CC[tc - 1:10]], COR_Q,
          r=3.6)
    pa.texto(9.8, Q_RENOV + 0.55, "renovável", cor=COR_Q, negrito=True,
             ancora="end")
    pa.texto(1.3, CC[0][1] + 0.55, "não renovável", cor=COR_PROD,
             negrito=True)
    serie(pb, [(k, mec) for k, _, _, _, mec in CC[:tc]], COR_CMG)
    serie(pb, [(k, pr) for k, _, _, pr, _ in CC[:tc]], COR_DESTAQUE)
    pb.reta(tc, D_SUB, 10.4, D_SUB, cor=COR_Q, larg=2.6)
    pb.texto(10.4, D_SUB + 0.35, "d = 6", cor=COR_Q, negrito=True,
             ancora="end")
    pb.texto(1.2, CC[0][4] - 0.65, "extração: 2 + 0,1Qₜ", cor=COR_CMG,
             negrito=True)
    pb.texto(1.2, CC[0][3] + 0.45, "total", cor=COR_DESTAQUE, negrito=True)
    # a chave do custo de usuario no periodo 1, que e o maior
    xc = 1.0
    pb.reta(xc, CC[0][4], xc, CC[0][3], cor=COR_DESTAQUE, larg=1.4,
            tracejado="3 2")
    rodape(t, 2 * LARG_P2, ALT_P2,
           "o custo de usuário cai de 2,43 a zero na troca (período 7);"
           " extraem-se 40; o resto do estoque fica no solo")
    t.salvar("13-custo-crescente.svg", "Custo de extração crescente")


def ambiental_fig():
    # O painel de preco comeca em 4,5: as duas trajetorias diferem em
    # decimos, e com o eixo em zero elas se sobrepoem.
    t, pa, pb = par_temporal("Extração", "Preço", 10, ymax_c=6.6,
                             ymin_c=4.5)
    for v in (5, 5.5):
        pb.marca_y(v, fmt(v, 1))
    # "com o dano" em azul, que e a cor de dano do curso desde a aula 04
    for linhas, tr, cor in ((CC, None, COR_PROD), (CA, "7 4", COR_DANO)):
        tc = troca(linhas)
        serie(pa, [(k, x) for k, x, _, _, _ in linhas[:tc]] + [(tc + 1, 0)],
              cor, tracejado=tr, r=3.6)
        serie(pb, [(k, pr) for k, _, _, pr, _ in linhas[:tc]] +
              [(k, D_SUB) for k in range(tc + 1, 11)], cor, tracejado=tr,
              r=3.6)
    pa.texto(3.0, 8.6, "sem o dano: extrai 40", cor=COR_PROD, negrito=True)
    pa.texto(3.0, 7.8, "com o dano: extrai 30", cor=COR_DANO, negrito=True)
    pb.texto(10.4, D_SUB + 0.15, "d = 6", cor=COR_Q, negrito=True,
             ancora="end")
    rodape(t, 2 * LARG_P2, ALT_P2,
           "com dano de 1 por unidade (custo 3 + 0,1Qₜ), extraem-se 30 em vez"
           " de 40; a troca chega no período 6 (sem o dano, no 7)")
    t.salvar("13-custo-ambiental.svg", "Custo ambiental da extração")


def paradoxo_fig():
    # Mesmo par de paineis das figuras temporais, mas o da direita e a
    # extracao acumulada (as emissoes), que termina em 40 nos dois casos.
    t = Tela(2 * LARG_P2 + FOLGA, ALT_P2 + ALTURA_RODAPE)
    pa = Painel(t, 0, LARG_P2, (0, 10.6), (0, 11.0), ALT_P2)
    pb = Painel(t, LARG_P2, LARG_P2, (0, 10.6), (0, 46.0), ALT_P2)
    pa.titulo("Extração por período")
    pb.titulo("Extração acumulada (emissões)")
    pa.eixos("t", "quantidade extraída")
    pb.eixos("t", "total extraído até t")
    for p in (pa, pb):
        for k in range(1, 11):
            p.marca_x(k, str(k))
    for v in (2, 4, 6, 8, 10):
        pa.marca_y(v, str(v))
    for v in (10, 20, 30, 40):
        pb.marca_y(v, str(v))
    pb.reta(0.4, 40, 10.4, 40, cor=COR_GUIA, larg=1.1, tracejado="4 3")
    pb.texto(10.4, 41.5, "estoque = 40", cor=COR_GUIA, ancora="end",
             negrito=True)
    # "com o imposto" tracejado em azul, como "com o dano" em 13-custo-ambiental
    for qs, tr, cor in ((Q_N, None, COR_PROD), (Q_SINN, "7 4", COR_DANO)):
        fim = ultimo(qs)
        serie(pa, [(k + 1, q) for k, q in enumerate(qs[:fim])] +
              [(fim + 1, 0)], cor, tracejado=tr, r=3.6)
        acc, pts = 0.0, []
        for k, q in enumerate(qs[:fim + 2]):
            acc += q
            pts.append((k + 1, acc))
        serie(pb, pts, cor, tracejado=tr, r=3.6)
    pa.texto(10.4, 10.0, "τ cresce 30%", cor=COR_DANO, negrito=True,
             ancora="end")
    pa.texto(10.4, 9.0, "sem imposto ou τ a 10%", cor=COR_PROD, negrito=True,
             ancora="end")
    pb.reta(3, 0, 3, sum(Q_SINN[:3]), cor=COR_GUIA, larg=1.1,
            tracejado="4 3")
    pb.texto(4.2, 18.0, "até t = 3: 25,0 contra 21,8", cor=COR_DESTAQUE,
             negrito=True)
    rodape(t, 2 * LARG_P2, ALT_P2,
           "imposto de 0,5 que cresce 30% por período: extrai-se mais no"
           " início; o estoque acaba um período antes; o total é 40")
    t.salvar("13-paradoxo-verde.svg", "Paradoxo verde")


# ===========================================================================
# Exercicio
# ===========================================================================

def exercicio():
    t, p = quadro_dois("Recurso parcialmente renovável: s = r = 0,1", 21.0)
    p.reta(0, A - C, 15, 0, cor=COR_PROD, larg=2.8)
    p.marca_y(A - C, "6")
    p.texto(2.2, 5.6, "BMgL₁", cor=COR_PROD, negrito=True)
    # BMgL_2 vista da esquerda: q2 = 1,1 (21 - q1), e o fator (1+s)/(1+r) = 1
    zero = 21.0 - (A - C) / B / (1 + R)
    p.reta(zero, 0, 21.0, A - C, cor=COR_FUT, larg=2.8)
    marca_dir(p, 21.0, A - C, "6", COR_FUT)
    p.texto(20.6, 6.25, "BMgL₂ × (1+s)/(1+r)", cor=COR_FUT, negrito=True,
            ancora="end")
    p.guia(EX_Q1, EX_BMGL, cor=COR_DESTAQUE)
    p.ponto(EX_Q1, EX_BMGL, r=6)
    p.marca_y(EX_BMGL, "1,6", cor=COR_DESTAQUE)
    marcas_q(p, 21.0, [EX_Q1], fator=1 + R)
    rodape(t, LARG, ALT,
           "o crescimento do estoque compensa o desconto: q₁* = q₂* = 11, e as"
           " duas curvas valem 6 na primeira unidade")
    t.salvar("13-exercicio.svg", "Exercício: recurso parcialmente renovável")


def main():
    print("aula 13 - recursos naturais")
    sem_escassez()
    for k in (1, 2, 3):
        dois_periodos_fig("13-dois-periodos-{}.svg".format(k), k)
    precos()
    desconto()
    bem_estar("13-bem-estar-1.svg", 1)
    bem_estar("13-bem-estar-2.svg", 2)
    mckelvey()
    reservas()
    reciclagem()
    n_periodos_fig()
    substituto_fig()
    crescente_fig()
    ambiental_fig()
    paradoxo_fig()
    exercicio()
    print()
    print("  conferencia da calibracao:")
    print("    2 periodos: q1 = {:.3f}, q2 = {:.3f}, lambda = {:.3f},"
          " lambda2 = {:.3f}".format(Q1, Q2, LAM, LAM2))
    print("    VP eficiente = {:.2f}; VP miope (15, 5) = {:.2f}".format(
        V1 + V2 / (1 + R), v_liq(15) + v_liq(5) / (1 + R)))
    print("    V1 = {:.3f}, V2 = {:.3f}, sobra = {:.3f}, V2 com = {:.3f}"
          .format(V1, V2, SOBRA, V2_COM))
    print("    N periodos: lambda = {:.4f}, q = {}".format(
        LAM_N, " ".join(fmt(q, 3) for q in Q_N[:9])))
    print("    substituto: troca em {}, lambda = {:.4f}, q = {}".format(
        T_SUB, LAM_SUB, " ".join(fmt(q, 3) for q in Q_SUB)))
    for nome, linhas in (("custo crescente", CC), ("com dano", CA)):
        print("    {}: troca em {}, extraido {:.2f}".format(
            nome, troca(linhas), linhas[-1][2]))
        for k, x, cum, pr, mec in linhas[:troca(linhas)]:
            print("      t={} q={:.3f} Q={:.2f} P={:.3f} CMg={:.3f}"
                  " usuario={:.3f}".format(k, x, cum, pr, mec, pr - mec))
    for nome, lam, qs in SINN:
        print("    imposto {}: lambda = {:.3f}, ultimo = {}, ate t=3 = {:.2f},"
              " VP dano = {:.2f}, q = {}".format(
                  nome, lam, ultimo(qs), sum(qs[:3]), vp(qs),
                  " ".join(fmt(q, 2) for q in qs[:ultimo(qs)])))
    print("    custo crescente + imposto 30%: q1 = {:.2f} (sem: {:.2f}),"
          " total = {:.2f}, troca em {}, VP dano = {:.2f} (sem: {:.2f})"
          .format(CS[0][1], CC[0][1], CS[-1][2], troca(CS),
                  vp([x for _, x, _, _, _ in CS]),
                  vp([x for _, x, _, _, _ in CC])))
    print("    exercicio: q1 = q2 = {:.3f}, BMgL = {:.3f}, V = {:.2f}".format(
        EX_Q1, EX_BMGL, v_liq(EX_Q1)))


if __name__ == "__main__":
    main()
