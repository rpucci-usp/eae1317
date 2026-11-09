#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Gera os diagramas da aula 16 (Acidentes Ambientais).

MOTIVO DE EXISTIR
-----------------
A aula segue o cap. 10 de Phaneuf e Requate (o .pptx 10, "Responsabilizacao
Ambiental"). O .pptx deixava tres passagens na LOUSA (o custo social, a regra
da negligencia e a pergunta "a~ < a*?") e tinha uma figura so, sem numeros.
Aqui as tres saem de UMA calibracao, que atravessa a aula inteira:

    rho(a) = 0,25 / (1 + a)      probabilidade de acidente
    D      = 400                 dano (R$ milhoes); a tambem em R$ milhoes

  1. Otimo social. -rho'(a) D = 100/(1+a)^2 = 1 da a* = 9, rho(a*) = 2,5%,
     dano esperado 10 e custo social 19. Sem prevencao: 25%, 100 e 100.

  2. Regra da negligencia (firma solvente). O autor pediu para simplificar
     (09/11/2026). Em vez dos dois casos com dois subcasos do .pptx, a firma
     compara duas opcoes: cumprir custa a_barra; descumprir custa, no minimo,
     a* + rho(a*) D = 19. Cumpre se a_barra <= 19. Os asserts conferem que
     essa regra unica da a mesma escolha que a maximizacao direta do lucro
     esperado por partes do .pptx, para todo a_barra numa grade fina.

  3. Firma insolvente. A CPO do .pptx, -rho'(a)(y - a) = 1 - rho(a), tem
     solucao fechada com esta rho: (1 + a~)^2 = (y + 1)/4. A tabela de y do
     slide e a regra da negligencia com y = 99 (a_barra = 8) estao nos asserts.

  4. Seguro. Cobertura total com premio fixo: a = 0. Premio que acompanha a
     prevencao (phi = rho(a)): volta a a* = 9.

Depende so da biblioteca padrao, como os outros scripts desta pasta.

    py scripts/figuras16svg.py

Escreve em aulas/_assets/figuras/.
"""

from figuras04svg import (COR_EIXO, COR_CMG, COR_DANO, COR_GUIA, COR_APAGADA,
                          COR_DESTAQUE)
from figuras08svg import fmt
from figuras11svg import COR_PROD, rodape, moldura

LARG, ALT = 700, 340

# ===========================================================================
# Calibracao
# ===========================================================================

P0 = 0.25        # probabilidade de acidente sem prevencao
D = 400.0        # dano (R$ milhoes)


def rho(a):
    return P0 / (1 + a)


def drho(a):
    return -P0 / (1 + a) ** 2


def dano_esp(a):
    return rho(a) * D


def custo_social(a):
    """SC = a + rho(a) D, o custo social esperado do .pptx."""
    return a + dano_esp(a)


def perto(x, y, tol=1e-9):
    return abs(x - y) < tol


# Propriedades que o .pptx exige de rho: decrescente, convexa, tende a zero.
assert all(drho(a) < 0 for a in range(0, 200))
assert all(2 * P0 / (1 + a) ** 3 > 0 for a in range(0, 200))
assert rho(1e9) < 1e-9

# Otimo social: -rho'(a) D = 100/(1+a)^2 = 1  =>  1 + a = 10.
A_EST = 9.0
assert perto(-drho(A_EST) * D, 1.0)
assert perto(P0 * D, 100.0)                    # o "100" da conta no slide
assert perto(rho(A_EST), 0.025)
assert perto(dano_esp(A_EST), 10.0)
SC_EST = custo_social(A_EST)
assert perto(SC_EST, 19.0)
# a* e o minimo do custo social numa grade fina (e nao so um ponto critico).
grade = [k / 100 for k in range(0, 6001)]
assert min(grade, key=custo_social) == A_EST
# Sem prevencao: 25%, dano esperado 100, custo social 100.
assert perto(rho(0), 0.25) and perto(dano_esp(0), 100) and perto(custo_social(0), 100)
# Os pontos da tabela "Custo Social em Numeros".
TAB_SC = {0: (25.0, 100.0, 100.0), 4: (5.0, 20.0, 24.0),
          9: (2.5, 10.0, 19.0), 19: (1.25, 5.0, 24.0)}
for a, (prob, de, sc) in TAB_SC.items():
    assert perto(100 * rho(a), prob) and perto(dano_esp(a), de)
    assert perto(custo_social(a), sc)


# ===========================================================================
# Regra da negligencia, firma solvente
# ===========================================================================

def custo_firma_negligencia(a, a_barra):
    """Custo esperado da firma (o lucro esperado do .pptx e y menos isto)."""
    return a if a >= a_barra else a + dano_esp(a)


def escolha_direta(a_barra, passo=0.01, a_max=60.0):
    """Minimiza o custo por partes do .pptx numa grade (sem atalho nenhum)."""
    n = int(round(a_max / passo))
    cands = [k * passo for k in range(n + 1)] + [a_barra]
    return min(cands, key=lambda a: (custo_firma_negligencia(a, a_barra), a))


LIMIAR = A_EST + dano_esp(A_EST)       # a* + rho(a*) D = 19
assert perto(LIMIAR, 19.0)


def escolha_simples(a_barra):
    """A regra do slide: cumpre (a = a_barra) se a_barra <= a* + rho(a*) D."""
    return a_barra if a_barra <= LIMIAR else A_EST


# A regra de duas opcoes reproduz a maximizacao por partes para todo a_barra
# de 0,5 a 40 (passo 0,5; o empate exato em 19 fica fora: ali as duas opcoes
# custam o mesmo e qualquer uma serve).
for k in range(1, 81):
    ab = k / 2
    if ab == LIMIAR:
        continue
    assert abs(escolha_direta(ab) - escolha_simples(ab)) < 0.011, ab
# "Descumprir custa, no minimo, 19": para qualquer a_barra, o menor custo com
# a < a_barra nunca fica abaixo de 19.
assert all(custo_social(a) >= LIMIAR - 1e-9 for a in grade)

# A tabela "Negligencia em Numeros": a_barra, escolha, custo social.
TAB_NEG = {4: (4, 24.0), 9: (9, 19.0), 15: (15, 21.25), 25: (9, 19.0)}
for ab, (esc, sc) in TAB_NEG.items():
    assert escolha_simples(ab) == esc
    assert perto(custo_social(esc), sc)
# Com a_barra = a*, a firma gasta 9 e as vitimas ficam com o dano esperado 10.
assert perto(custo_firma_negligencia(A_EST, A_EST), 9.0)


# ===========================================================================
# Firma insolvente
# ===========================================================================

def lucro_insolvente(a, y):
    """EV[Pi] = [1 - rho(a)](y - a): no acidente a firma fica com zero."""
    return (1 - rho(a)) * (y - a)


def a_til(y):
    """Solucao da CPO -rho'(a)(y - a) = 1 - rho(a): (1 + a)^2 = (y + 1)/4."""
    return max(0.0, ((y + 1) / 4) ** 0.5 - 1)


TAB_INS = {399: 9.0, 255: 7.0, 99: 4.0, 24: 1.5, 3: 0.0}
for y, at in TAB_INS.items():
    assert perto(a_til(y), at)
    assert y - at - D < 0                         # insolvente de fato
    if at > 0:                                    # a CPO do .pptx vale nele
        assert perto(-drho(at) * (y - at), 1 - rho(at))
    # e e o maximo do lucro esperado numa grade fina
    g = [k / 100 for k in range(0, int(100 * min(y, 60)) + 1)]
    assert abs(max(g, key=lambda a: lucro_insolvente(a, y)) - at) < 0.011
# Custo social e probabilidade de cada linha da tabela.
TAB_INS_SC = {399: (2.5, 19.0), 255: (3.125, 19.5), 99: (5.0, 24.0),
              24: (10.0, 41.5), 3: (25.0, 100.0)}
for y, (prob, sc) in TAB_INS_SC.items():
    assert perto(100 * rho(a_til(y)), prob) and perto(custo_social(a_til(y)), sc)

# Regra da negligencia com a firma insolvente de y = 99.
Y_N = 99.0
A_TIL_N = a_til(Y_N)
assert perto(A_TIL_N, 4.0)
DESCUMPRIR_N = lucro_insolvente(A_TIL_N, Y_N)
assert perto(DESCUMPRIR_N, 90.25)                 # 0,95 x 95
assert perto(Y_N - 8, 91.0) and Y_N - 8 > DESCUMPRIR_N      # a_barra = 8: cumpre
assert perto(Y_N - 9, 90.0) and Y_N - 9 < DESCUMPRIR_N      # a_barra = 9: nao
# O maior a_barra que a firma aceita: y - a_barra = 90,25 => a_barra = 8,75.
assert perto(Y_N - DESCUMPRIR_N, 8.75)
assert abs(custo_social(8) - 19.11) < 0.005       # 8 + 100/9
assert perto(custo_social(A_TIL_N), 24.0)
# Com a_barra = 8, descumprir de verdade e escolher a~ = 4 (o maximo com a < 8).
g = [k / 100 for k in range(0, 800)]
assert abs(max(g, key=lambda a: lucro_insolvente(a, Y_N)) - 4.0) < 0.011


# As duas CPOs com o mesmo lado esquerdo (slide reescrito em 09/11/2026, a
# pedido do autor: "em que ajuda reescrever a equacao daquela forma?").
#   solvente:   -rho'(a) = 1/D
#   insolvente: -rho'(a) = (1 - rho(a))/(y - a)
# -rho'(a) e decrescente; o lado direito maior leva a um a menor.
def lado_dir_insolvente(a, y=Y_N):
    return (1 - rho(a)) / (y - a)


LADO_DIR_SOLV = 1 / D
assert perto(LADO_DIR_SOLV, 0.0025)
assert perto(-drho(A_EST), LADO_DIR_SOLV)                    # cruza 1/D em 9
assert perto(-drho(4), 0.01) and perto(0.25 / 25, 0.01)       # 0,25/25
assert perto(lado_dir_insolvente(4), 0.95 / 95)               # 0,95/95
assert perto(lado_dir_insolvente(4), 0.01)
# -rho' decrescente e o lado direito da insolvente crescente: um cruzamento so.
assert all(-drho(k / 10) > -drho(k / 10 + 0.1) for k in range(0, 300))
assert all(lado_dir_insolvente(k / 10) < lado_dir_insolvente(k / 10 + 0.1)
           for k in range(0, 300))
# O dano D nao entra na CPO da insolvente: com D = 800, a~ continua 4 (a firma
# continua insolvente, y - a - D < 0).
assert Y_N - 4 - 800 < 0 and perto(a_til(Y_N), 4.0)
# Condicao geral: a~ < a* se, em a*, o lado direito da insolvente passa de 1/D,
# isto e, y - a* < (1 - rho(a*)) D, ou y < a* + D - rho(a*) D = 9 + 390 = 399.
Y_LIMIAR = A_EST + D - dano_esp(A_EST)
assert perto(Y_LIMIAR, 399.0) and perto((1 - rho(A_EST)) * D, 390.0)
for y in (24, 99, 255, 398):
    assert lado_dir_insolvente(A_EST, y) > LADO_DIR_SOLV and a_til(y) < A_EST
for y in (399.5, 405, 408):
    assert lado_dir_insolvente(A_EST, y) < LADO_DIR_SOLV and a_til(y) > A_EST


# ===========================================================================
# Seguro
# ===========================================================================

# Premio que acompanha a prevencao (phi = rho(a)): o lucro vira y - a - rho(a)D,
# o mesmo da responsabilizacao total, e a escolha volta a a* = 9; premio 10.
assert min(grade, key=lambda a: a + rho(a) * D) == A_EST
assert perto(rho(A_EST) * D, 10.0)


# ===========================================================================
# Figuras
# ===========================================================================

def curva_clip(p, f, xa, xb, cor, larg=2.6, n=400):
    """Desenha f so onde ela cabe no painel: o dano esperado e o custo social
    valem 100 em a = 0 e sairiam pelo topo de um eixo que vai ate 50."""
    xs = [xa + (xb - xa) * i / n for i in range(n + 1)]
    dentro = [x for x in xs if p.y0 <= f(x) <= p.y1]
    if dentro:
        p.curva(f, dentro[0], dentro[-1], cor=cor, larg=larg)


def probabilidade():
    titulo = "Probabilidade de acidente, ρ(a)"
    t, p = moldura(titulo, LARG, ALT, (0, 30), (0, 0.30), "a", "ρ(a)")
    for v in (0.05, 0.10, 0.25):
        p.marca_y(v, fmt(100 * v, 0) + "%")
    p.curva(rho, 0, 30, cor=COR_DANO, larg=2.8)
    for a in (0, 4):
        p.guia(a, rho(a))
        p.ponto(a, rho(a), r=5.5)
    p.marca_x(0, "0")
    p.marca_x(4, "4")
    for x in (10, 20, 30):
        p.marca_x(x, str(x))
    # rotulo da curva no trecho plano, acima dela
    assert rho(14) < 0.02
    p.texto(14, 0.045, "ρ(a) = 0,25/(1 + a)", cor=COR_DANO, negrito=True,
            italico=False)
    rodape(t, LARG, ALT, "sem prevenção, 25%; com R$ 4 milhões de prevenção,"
           " 5%; a chance tende a zero, mas cada milhão rende menos")
    t.salvar("16-probabilidade.svg", titulo)


X_SC, Y_SC = (0, 30), (0, 50)


def _base_custo(t, p, marcas_x=(20, 30)):
    for v in (10, 19, 30, 40, 50):
        p.marca_y(v, fmt(v, 0))
    for x in marcas_x:
        p.marca_x(x, str(x))


def custo():
    titulo = "Custo social esperado, SC = a + ρ(a)D"
    t, p = moldura(titulo, LARG, ALT, X_SC, Y_SC, "a", "R$ mi")
    _base_custo(t, p)
    p.reta(0, 0, 30, 30, cor=COR_CMG, larg=2.2)
    curva_clip(p, dano_esp, 0, 30, COR_DANO, larg=2.4)
    curva_clip(p, custo_social, 0, 30, COR_DESTAQUE, larg=3.0)
    p.reta(A_EST, 0, A_EST, SC_EST, cor=COR_GUIA, larg=1.1, tracejado="4 3")
    p.reta(0, SC_EST, A_EST, SC_EST, cor=COR_GUIA, larg=1.1, tracejado="4 3")
    p.ponto(A_EST, dano_esp(A_EST), r=5, cor=COR_DANO)
    p.ponto(A_EST, SC_EST, r=6)
    p.marca_x(A_EST, "a* = 9")
    # rotulos: "prevencao, a" acima da reta, a direita; "dano esperado" abaixo
    # da curva azul, na ponta direita; "custo social" acima da curva, a direita.
    assert custo_social(26) < 30 and dano_esp(26) < 4
    p.texto(29.5, 35, "custo social", cor=COR_DESTAQUE, ancora="end",
            negrito=True, italico=False)
    p.texto(23.5, 18, "prevenção, a", cor=COR_CMG, ancora="end",
            negrito=True, italico=False)
    p.texto(29.5, 8, "dano esperado, ρ(a)D", cor=COR_DANO, ancora="end",
            negrito=True, italico=False)
    rodape(t, LARG, ALT, "o mínimo está em a* = 9: gastar mais um milhão"
           " reduz o dano esperado em menos de um milhão")
    t.salvar("16-custo-social.svg", titulo)


def negligencia():
    titulo = "Cumprir o padrão ou descumprir?"
    t, p = moldura(titulo, LARG, ALT, X_SC, Y_SC, "ā", "R$ mi")
    _base_custo(t, p, marcas_x=(30,))   # 20 encostava no 19
    # faixa do eixo onde a firma cumpre (a_barra <= 19)
    p.area([(0, 0), (LIMIAR, 0), (LIMIAR, 1.4), (0, 1.4)], COR_PROD, 0.35)
    p.area([(LIMIAR, 0), (30, 0), (30, 1.4), (LIMIAR, 1.4)], COR_CMG, 0.25)
    curva_clip(p, custo_social, 0, 30, COR_APAGADA, larg=2.6)
    p.reta(0, 0, 30, 30, cor=COR_CMG, larg=2.6)
    p.reta(0, LIMIAR, 30, LIMIAR, cor=COR_DESTAQUE, larg=2.2, tracejado="7 4")
    p.reta(LIMIAR, 0, LIMIAR, LIMIAR, cor=COR_GUIA, larg=1.1, tracejado="4 3")
    p.reta(A_EST, 0, A_EST, SC_EST, cor=COR_GUIA, larg=1.1, tracejado="4 3")
    p.ponto(A_EST, SC_EST, r=5, cor=COR_APAGADA)
    p.ponto(LIMIAR, LIMIAR, r=6)
    p.marca_x(A_EST, "a* = 9")
    p.marca_x(LIMIAR, "19")
    # "cumprir" fica no canto de baixo a esquerda, entre a reta vermelha (no
    # maximo 7,5 ate a = 7,5) e a curva cinza (acima de 19 ate a = 9).
    p.texto(0.8, 10.5, "cumprir: custa ā", cor=COR_CMG, ancora="start",
            negrito=True, italico=False)
    assert all(custo_social(x / 10) > 10.5 + 3.5 for x in range(8, 76))
    p.texto(29.5, LIMIAR - 3.2, "descumprir: no mínimo 19", cor=COR_DESTAQUE,
            ancora="end", negrito=True, italico=False)
    # o rotulo de "descumprir" vai de ~19 a 29,5 em a, entre y 15,8 e 19:
    # a reta vermelha ja passou de 19 ali
    assert 19.0 >= LIMIAR - 3.2 + 3.0
    p.texto(14, 3.2, "cumpre", cor=COR_PROD, ancora="middle", negrito=True,
            italico=False)
    p.texto(24.5, 3.2, "descumpre", cor=COR_CMG, ancora="middle", negrito=True,
            italico=False)
    p.texto(2.6, 42, "SC = a + ρ(a)D", cor=COR_GUIA, ancora="start",
            italico=False)
    assert all(custo_social(x / 10) < 42 - 1 for x in range(26, 300))
    rodape(t, LARG, ALT, "a firma cumpre enquanto ā ≤ 19; com padrão mais"
           " alto, escolhe a* = 9 e paga os danos")
    t.salvar("16-negligencia.svg", titulo)


def insolvente():
    titulo = "Prevenção da firma insolvente, ã"
    t, p = moldura(titulo, LARG, ALT, (0, 420), (0, 11), "y", "ã")
    for v in (0, 4, 9):
        p.marca_y(v, fmt(v, 0))
    p.reta(0, A_EST, 420, A_EST, cor=COR_DESTAQUE, larg=1.8, tracejado="7 4")
    p.texto(12, A_EST + 0.55, "ótimo social: a* = 9", cor=COR_DESTAQUE,
            negrito=True, italico=False)
    assert a_til(12) < A_EST - 2
    p.curva(a_til, 0, 399, cor=COR_CMG, larg=2.8, n=400)
    for y, at in sorted(TAB_INS.items()):
        p.ponto(y, at, r=5.5)
        if y > 3:
            p.marca_x(y, fmt(y, 0))
    p.marca_x(0, "0")
    p.texto(300, 4.0, "(1 + ã)² = (y + 1)/4", cor=COR_CMG, negrito=True,
            italico=False)
    assert a_til(300) > 4.0 + 3.5            # rotulo bem abaixo da curva
    rodape(t, LARG, ALT, "com dano de R$ 400 milhões, quanto menor a riqueza"
           " y, menor a prevenção: a falência limita a perda da firma")
    t.salvar("16-insolvente.svg", titulo)


def duas_cpos():
    """As duas CPOs com o mesmo lado esquerdo, -rho'(a), e y = 99."""
    titulo = "Quanto cada real de prevenção precisa reduzir ρ?"
    t, p = moldura(titulo, LARG, ALT, (0, 20), (0, 0.02), "a", "")
    p.marca_y(0.0025, "0,0025")
    p.marca_y(0.01, "0,01")
    p.marca_y(0.02, "0,02")
    p.reta(0, LADO_DIR_SOLV, 20, LADO_DIR_SOLV, cor=COR_DESTAQUE, larg=2.2,
           tracejado="7 4")
    p.curva(lado_dir_insolvente, 0, 20, cor=COR_CMG, larg=2.8)
    curva_clip(p, lambda a: -drho(a), 0, 20, COR_DANO, larg=2.8)
    p.reta(A_EST, 0, A_EST, LADO_DIR_SOLV, cor=COR_GUIA, larg=1.1,
           tracejado="4 3")
    p.reta(4, 0, 4, 0.01, cor=COR_GUIA, larg=1.1, tracejado="4 3")
    p.ponto(A_EST, LADO_DIR_SOLV, r=6)
    p.ponto(4, 0.01, r=6)
    p.marca_x(4, "ã = 4")
    p.marca_x(A_EST, "a* = 9")
    p.marca_x(20, "20")
    # Rotulos. -rho'(a): logo a direita de onde a curva sai pelo topo (a curva
    # vale 0,0156 em a = 3, abaixo do texto, que comeca em 0,0185).
    assert -drho(3.0) < 0.0185 - 0.002 and -drho(2.5) > 0.02
    p.texto(3.0, 0.0185, "−ρ′(a)", cor=COR_DANO, negrito=True, italico=False)
    # insolvente: acima da curva vermelha (no maximo 0,0125 ate a = 20) e
    # longe da azul (abaixo de 0,0023 a partir de a = 9,5).
    assert lado_dir_insolvente(20) < 0.0145 - 0.0015 and -drho(9.5) < 0.0023
    p.texto(19.5, 0.0145, "insolvente, y = 99: (1 − ρ(a))/(y − a)",
            cor=COR_CMG, ancora="end", negrito=True, italico=False)
    # solvente: acima da tracejada, a direita, onde a azul ja esta abaixo dela
    assert -drho(13) < LADO_DIR_SOLV - 0.0008
    p.texto(19.5, LADO_DIR_SOLV + 0.0006, "solvente: 1/D = 1/400",
            cor=COR_DESTAQUE, ancora="end", negrito=True, italico=False)
    rodape(t, LARG, ALT, "a firma insolvente exige mais de cada real gasto em"
           " prevenção e para antes: ã = 4, contra a* = 9")
    t.salvar("16-duas-cpos.svg", titulo)


def main():
    print("aula 16 - acidentes ambientais")
    probabilidade()
    custo()
    negligencia()
    insolvente()
    duas_cpos()
    print()
    print("  conferencia:")
    print("    otimo: a* = {:.0f}, rho = {:.1%}, dano esperado {:.0f}, SC {:.0f}"
          .format(A_EST, rho(A_EST), dano_esp(A_EST), SC_EST))
    print("    negligencia: limiar {:.0f}; tabela {}".format(LIMIAR, TAB_NEG))
    print("    insolvente: {}".format({y: a_til(y) for y in TAB_INS}))
    print("    y = 99: descumprir {:.2f}, a_barra max {:.2f}".format(
        DESCUMPRIR_N, Y_N - DESCUMPRIR_N))


if __name__ == "__main__":
    main()
