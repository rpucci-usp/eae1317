#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Gera os diagramas da aula 15 (Recursos Comuns).

MOTIVO DE EXISTIR
-----------------
A aula segue o cap. 7 de Keohane e Olmstead (2016), "Stocks That Grow", e
acrescenta um bloco sobre grilagem. Nenhuma figura e recortada do livro: todas
saem das equacoes, com os numeros do proprio capitulo quando ele os da.

  1. Florestas. A funcao de volume do livro, V(t) = 10t + t^2 - 0,01t^3
     (fig. 7.1), a media anual (fig. 7.2), a regra de Wicksell, a de
     Faustmann (fig. 7.3) e o habitat de aves (fig. 7.4). O livro nao da
     numeros para Faustmann nem para o habitat; a calibracao (preco liquido
     R$ 1 por unidade de volume, juros de 3%, replantio de R$ 200, habitat a
     partir dos 25 anos) e daqui, e os asserts conferem que as tres rotacoes
     ficam na ordem do texto: Faustmann < Wicksell < biologica.

  2. Direitos inseguros. O livro diz que, sem direitos seguros, o incentivo a
     roubar arvores e muito alto, mas nao faz a conta. A conta e daqui: uma
     chance anual theta de perder as arvores entra na regra de Wicksell como
     juros mais altos, (r + theta)/(1 - theta). O acesso livre e o limite
     theta -> 1. A aula nao tem pesca: o autor pediu toda a discussao de
     acesso livre em cima do modelo de florestas (04/11/2026).

  2b. Corrida entre dois vizinhos. O jogo de recursos comuns do .pptx antigo,
     refeito com V(t) e Wicksell a pedido do autor (04/11/2026), sem supor
     um crescimento g(X): quem corta primeiro leva a madeira. Pareto e cortar
     aos 41; a corrida desce ate 2 anos, a regra do risco com theta = 1/2.

  3. Grilagem. Versao simplificada, em tempo discreto e sem incerteza de
     preco, do modelo de opcoes reais do artigo do professor (apendice
     matematico, nao publicado). O valor da posse e a parte constante C do
     apendice, W_G = (pi_G + lambda W_O) / (r + lambda); os asserts conferem
     que a recursao de um ano chega a essa formula e que os limiares saem
     exatos.

Depende so da biblioteca padrao, como os outros scripts desta pasta.

    py scripts/figuras15svg.py

Escreve em aulas/_assets/figuras/.
"""

from figuras04svg import (Tela, COR_EIXO, COR_CMG, COR_DANO, COR_GUIA,
                          COR_APAGADA, COR_DESTAQUE)
from figuras08svg import fmt
from figuras11svg import COR_PROD, rodape, moldura

LARG, ALT = 700, 340
COR_HAB = "#B8860B"        # habitat (ouro escuro): nem custo nem beneficio "de mercado"


def pct(v, casas=1):
    return fmt(100 * v, casas) + "%"


# ===========================================================================
# 1. Florestas
# ===========================================================================

def V(t):
    """Volume do talhao com t anos (fig. 7.1 do livro)."""
    return 10 * t + t * t - 0.01 * t ** 3


def dV(t):
    """Crescimento entre este ano e o proximo: o custo marginal de cortar."""
    return V(t + 1) - V(t)


def mai(t):
    return V(t) / t


# Os tres numeros que o livro da para V(t): a taxa de crescimento comeca a cair
# depois de ~33 anos (V'' = 2 - 0,06t = 0), o volume cai depois de ~71 anos
# (V' = 0) e a media anual e maxima aos 50 (d(V/t)/dt = 1 - 0,02t = 0).
T_INFLEXAO = 2 / 0.06
T_MAX_VOL = (2 + (4 + 4 * 0.03 * 10) ** 0.5) / 0.06
T_BIO = 50
assert abs(T_INFLEXAO - 33.3) < 0.1
assert abs(T_MAX_VOL - 71.3) < 0.1
assert max(range(1, 100), key=mai) == T_BIO
assert abs(V(T_BIO) - 1750) < 1e-9 and abs(mai(T_BIO) - 35) < 1e-9


def wicksell(r):
    """Primeiro ano em que cortar rende mais que esperar: r V(t) >= dV(t)."""
    return next(t for t in range(1, 200) if r * V(t) >= dV(t))


# "Com juros acima de 2%, a rotacao de Wicksell e mais curta que a biologica":
# aos 50 anos, dV/V = 34,49/1750 < 2%, e aos 49 ainda passa de 2%.
assert wicksell(0.02) == T_BIO
assert all(wicksell(r) < T_BIO for r in (0.025, 0.03, 0.04, 0.05))
TAXAS = (0.02, 0.03, 0.05)
T_W = {r: wicksell(r) for r in TAXAS}
assert T_W == {0.02: 50, 0.03: 41, 0.05: 29}

R = 0.03        # juros da calibracao de Faustmann
D = 200.0       # custo de replantio (R$), preco liquido (p - c) = R$ 1


def valor_terreno(T, h=lambda a: 0.0):
    """Valor do terreno logo apos o replantio, com rotacao T para sempre.

    Sem habitat: S = (V(T) - D) / ((1+r)^T - 1), que e a equacao do livro
    resolvida para S. Com habitat, soma-se o valor presente do fluxo h(a)
    recebido em cada ano a de idade do talhao.
    """
    vp_hab = sum(h(a) / (1 + R) ** a for a in range(1, T + 1))
    return (vp_hab + (V(T) - D) / (1 + R) ** T) / (1 - (1 + R) ** (-T))


T_F = max(range(5, 150), key=valor_terreno)
S_F = valor_terreno(T_F)
T_W3 = T_W[R]
assert T_F == 35 and T_W3 == 41
assert T_F < T_W3 < T_BIO            # a ordem do livro
assert abs(S_F - 521.7) < 0.1
assert abs(R * (S_F - D) - 9.65) < 0.01     # o "R$ 9,65" do slide


def bm_faustmann(t, S=S_F):
    """Beneficio marginal de cortar agora: r[V(t) - D] + rS."""
    return R * (V(t) - D + S)


# A regra marginal do livro escolhe o mesmo ano que maximiza S.
assert bm_faustmann(T_F) >= dV(T_F) and bm_faustmann(T_F - 1) < dV(T_F - 1)
assert R * V(T_W3) >= dV(T_W3) and R * V(T_W3 - 1) < dV(T_W3 - 1)

# Os numeros que os slides mostram, um por um (pedido do autor em 04/11: "de
# onde vem o S = 522?"). S e o ponto fixo de um ciclo de T anos:
# S = (V(T) - D + S)/(1+r)^T, donde S = (V(T) - D)/((1+r)^T - 1).
assert abs((V(T_F) - D + S_F) / (1 + R) ** T_F - S_F) < 1e-9
assert abs(V(T_F) - 1146.25) < 1e-9 and abs((1 + R) ** T_F - 2.8139) < 1e-4
assert round((V(T_F) - D) / 1.8139) == 522        # a conta com 4 casas do slide
TABELA_S = {25: 474, 30: 511, 35: 522, 41: 509, 50: 458}   # slide "Quanto Vale o Terreno?"
assert {T: round(valor_terreno(T)) for T in TABELA_S} == TABELA_S
assert [round(V(T)) for T in TABELA_S] == [719, 930, 1146, 1402, 1750]
assert round(S_F - D, 1) == 321.7 and round(R * 321.7, 2) == 9.65
# fragmentos: Wicksell aos 41 (rV contra dV) e Faustmann aos 35
assert (round(R * V(41), 1), round(dV(41), 1)) == (42.1, 41.3)
assert (round(bm_faustmann(35), 1), round(dV(35), 1)) == (44.0, 43.2)

# Habitat de aves que preferem talhoes velhos: vale R$ ETA por ano para cada
# ano de idade acima de A_HAB. Entra como custo a mais de cortar (fig. 7.4).
A_HAB, ETA = 25, 1.0


def hab(a, eta=ETA):
    return eta * max(0.0, a - A_HAB)


T_AVE = max(range(5, 150), key=lambda T: valor_terreno(T, hab))
S_AVE = valor_terreno(T_AVE, hab)
assert T_AVE == 47
assert R * (V(T_AVE) - D + S_AVE) >= dV(T_AVE) + hab(T_AVE + 1)
assert R * (V(T_AVE - 1) - D + S_AVE) < dV(T_AVE - 1) + hab(T_AVE)
# Com o dobro do valor do habitat, S so cresce com T: nunca cortar.
_S2 = [valor_terreno(T, lambda a: hab(a, 2 * ETA)) for T in range(5, 300)]
assert all(b > a for a, b in zip(_S2[60:], _S2[61:]))
assert max(range(len(_S2)), key=_S2.__getitem__) == len(_S2) - 1

# Direitos inseguros: a cada ano, chance THETA de perder as arvores (roubo,
# invasao, fogo). Esperar rende (1 - theta) V(t+1); corta-se quando
# (1 + r) V(t) >= (1 - theta) V(t+1), isto e, dV/V <= (r + theta)/(1 - theta).
# Com theta = 0 e a regra de Wicksell; com theta perto de 1, acesso livre.
THETA = 0.02


def rotacao_risco(theta, r=R):
    return next(t for t in range(1, 200)
                if (1 + r) * V(t) >= (1 - theta) * V(t + 1))


T_RISCO = rotacao_risco(THETA)
TAXA_RISCO = (R + THETA) / (1 - THETA)
assert rotacao_risco(0) == T_W3 == 41
assert T_RISCO == 28 and abs(TAXA_RISCO - 0.0510) < 1e-4
# a mesma regra escrita como taxa de crescimento
assert dV(T_RISCO) / V(T_RISCO) <= TAXA_RISCO < dV(T_RISCO - 1) / V(T_RISCO - 1)
# a tabela do slide "Acesso Livre na Floresta"
TABELA_RISCO = {0: 41, 0.02: 28, 0.10: 11, 0.50: 2}
assert {th: rotacao_risco(th) for th in TABELA_RISCO} == TABELA_RISCO


def volume():
    titulo = "Volume de madeira de um talhão"
    t, p = moldura(titulo, LARG, ALT, (0, 85), (0, 2400), "t", "V(t)")
    for v in (1000, 2000):
        p.marca_y(v, fmt(v, 0))
    p.curva(V, 0, 85, cor=COR_PROD, larg=2.8)
    for x, rot in ((T_INFLEXAO, "33"), (T_MAX_VOL, "71")):
        p.guia(x, V(x))
        p.ponto(x, V(x), r=5.5)
        p.marca_x(x, rot)
    p.texto(T_INFLEXAO + 1.5, V(T_INFLEXAO) - 120, "crescimento desacelera",
            cor=COR_DESTAQUE, negrito=True)
    p.texto(T_MAX_VOL - 1.5, V(T_MAX_VOL) + 110, "volume começa a cair",
            cor=COR_DESTAQUE, negrito=True, ancora="end")
    rodape(t, LARG, ALT, "V(t) = 10t + t² − 0,01t³: rápido no começo, mais"
           " lento depois dos 33 anos, em queda depois dos 71")
    t.salvar("15-volume.svg", titulo)


def media_anual():
    titulo = "Média anual de volume, V(t)/t"
    t, p = moldura(titulo, LARG, ALT, (0, 85), (0, 42), "t", "V(t)/t")
    for v in (10, 20, 30):
        p.marca_y(v, str(v))
    p.curva(mai, 1, 85, cor=COR_PROD, larg=2.8)
    p.guia(T_BIO, mai(T_BIO))
    p.ponto(T_BIO, mai(T_BIO), r=5.5)
    p.marca_x(T_BIO, "50")
    p.marca_y(mai(T_BIO), "35")
    p.texto(T_BIO, mai(T_BIO) + 2.5, "rotação biológica", cor=COR_DESTAQUE,
            negrito=True, ancora="middle")
    rodape(t, LARG, ALT, "nenhuma outra idade de corte dá mais madeira por ano"
           " em média: 1.750 unidades em 50 anos")
    t.salvar("15-mai.svg", titulo)


def taxa_crescimento():
    titulo = "Taxa de crescimento do volume, ΔV/V"
    # Eixo de 20 a 60 anos e de 0 a 8%: com 0 a 10% as tres retas de juros
    # ficavam a 10px uma da outra e os rotulos se encostavam.
    t, p = moldura(titulo, LARG, ALT, (20, 60), (0, 0.08), "t", "ΔV/V")
    for v in (0.02, 0.03, 0.05):
        p.marca_y(v, pct(v, 0))
    assert dV(20) / V(20) < 0.08
    p.curva(lambda x: dV(x) / V(x), 20, 60, cor=COR_PROD, larg=2.8)
    for r in TAXAS:
        T = T_W[r]
        p.reta(20, r, 60, r, cor=COR_DANO, larg=1.6, tracejado="6 4")
        p.reta(T, 0, T, r, cor=COR_GUIA, larg=1.1, tracejado="4 3")
        p.ponto(T, dV(T) / V(T), r=5.5)
        p.marca_x(T, str(T))
    p.texto(59, 0.053, "r = 5%", cor=COR_DANO, ancora="end")
    p.texto(59, 0.033, "r = 3%", cor=COR_DANO, ancora="end")
    p.texto(59, 0.023, "r = 2%", cor=COR_DANO, ancora="end")
    rodape(t, LARG, ALT, "corta-se quando o volume passa a crescer menos que"
           " os juros: 29, 41 e 50 anos com juros de 5%, 3% e 2%")
    t.salvar("15-wicksell.svg", titulo)


def risco():
    """Mesmos eixos de 15-wicksell: o risco entra como juros mais altos."""
    titulo = "Taxa de crescimento do volume, ΔV/V"
    t, p = moldura(titulo, LARG, ALT, (20, 60), (0, 0.08), "t", "ΔV/V")
    p.marca_y(R, pct(R, 0))
    p.marca_y(TAXA_RISCO, pct(TAXA_RISCO, 1))
    p.curva(lambda x: dV(x) / V(x), 20, 60, cor=COR_PROD, larg=2.8)
    p.reta(20, R, 60, R, cor=COR_APAGADA, larg=1.6, tracejado="6 4")
    p.reta(T_W3, 0, T_W3, R, cor=COR_GUIA, larg=1.1, tracejado="4 3")
    p.ponto(T_W3, dV(T_W3) / V(T_W3), r=5.5, cor=COR_APAGADA)
    p.marca_x(T_W3, str(T_W3), cor=COR_APAGADA)
    p.texto(59, 0.033, "sem risco: r = 3%", cor=COR_APAGADA, ancora="end",
            negrito=True)
    p.reta(20, TAXA_RISCO, 60, TAXA_RISCO, cor=COR_DANO, larg=1.8,
           tracejado="6 4")
    p.reta(T_RISCO, 0, T_RISCO, TAXA_RISCO, cor=COR_GUIA, larg=1.1,
           tracejado="4 3")
    p.ponto(T_RISCO, dV(T_RISCO) / V(T_RISCO), r=5.5)
    p.marca_x(T_RISCO, str(T_RISCO))
    # depois dos 45 anos a curva fica abaixo de 3%: os rotulos passam por cima
    assert all(dV(x) / V(x) < 0.03 for x in range(45, 60))
    p.texto(59, TAXA_RISCO + 0.003, "com risco: (r + θ)/(1 − θ)",
            cor=COR_DANO, ancora="end", negrito=True)
    rodape(t, LARG, ALT, "chance de 2% ao ano de perder as árvores: o corte"
           " vem aos 28 anos, não aos 41")
    t.salvar("15-risco.svg", titulo)


X_ROT, Y_ROT = (0, 62), (0, 80)
TIT_ROT = "Cortar agora ou esperar mais um ano?"


def _base_rotacao():
    t, p = moldura(TIT_ROT, LARG, ALT, X_ROT, Y_ROT, "t", "R$")
    for v in (20, 40, 60):
        p.marca_y(v, str(v))
    return t, p


def faustmann(etapa):
    """Etapa 1: so Wicksell. Etapa 2: entra o valor do terreno."""
    t, p = _base_rotacao()
    p.curva(dV, 1, 62, cor=COR_PROD, larg=2.8)
    # No canto de cima a esquerda nenhuma curva passa: embaixo da curva de
    # Delta V, o rotulo era cortado pela reta rV e encostava na vermelha.
    p.texto(2, 56, "ΔV: o que se perde cortando agora", cor=COR_PROD,
            negrito=True)
    assert all(R * (V(x) - D + S_F) < 50 and dV(x) < 50 for x in range(0, 30))
    cor_w = COR_DANO if etapa == 1 else COR_APAGADA
    p.curva(lambda x: R * V(x), 1, 62, cor=cor_w, larg=2.4)
    p.texto(61, R * V(61) + 3, "rV", cor=cor_w, ancora="end", negrito=True)
    if etapa == 1:
        p.guia(T_W3, R * V(T_W3))
        p.ponto(T_W3, R * V(T_W3), r=5.5)
        p.marca_x(T_W3, str(T_W3))
        texto = ("Wicksell: corta-se aos 41 anos, quando o ganho de esperar"
                 " cai ao rendimento da madeira vendida (juros de 3%)")
        nome = "15-faustmann-1.svg"
    else:
        p.marca_x(T_W3, str(T_W3), cor=COR_APAGADA)
        p.curva(bm_faustmann, 1, 62, cor=COR_CMG, larg=2.8)
        p.texto(61, bm_faustmann(61) + 3, "r(V − D + S)", cor=COR_CMG,
                ancora="end", negrito=True)
        p.guia(T_F, bm_faustmann(T_F))
        p.ponto(T_F, bm_faustmann(T_F), r=5.5)
        p.marca_x(T_F, str(T_F))
        texto = ("Faustmann: o terreno replantado também rende (S = R$ 522);"
                 " o corte vem antes, aos 35 anos")
        nome = "15-faustmann-2.svg"
    rodape(t, LARG, ALT, texto)
    t.salvar(nome, TIT_ROT)


def habitat():
    t, p = _base_rotacao()
    p.curva(dV, 1, 62, cor=COR_APAGADA, larg=2.2)
    p.curva(bm_faustmann, 1, 62, cor=COR_APAGADA, larg=2.2)
    p.marca_x(T_F, str(T_F), cor=COR_APAGADA)
    p.curva(lambda x: dV(x) + hab(x + 1), 1, 62, cor=COR_HAB, larg=2.8)
    p.texto(60, dV(60) + hab(61) - 7, "ΔV + habitat", cor=COR_HAB,
            ancora="end", negrito=True)
    bm = lambda x: R * (V(x) - D + S_AVE)
    p.curva(bm, 1, 62, cor=COR_CMG, larg=2.8)
    p.texto(61, bm(61) + 3, "r(V − D + S)", cor=COR_CMG, ancora="end",
            negrito=True)
    p.guia(T_AVE, bm(T_AVE))
    p.ponto(T_AVE, bm(T_AVE), r=5.5)
    p.marca_x(T_AVE, str(T_AVE))
    rodape(t, LARG, ALT, "o habitat perdido é custo a mais de cortar: a rotação"
           " vai de 35 para 47 anos")
    t.salvar("15-habitat.svg", TIT_ROT)


# ===========================================================================
# 2. Corrida entre dois vizinhos: o jogo de recursos comuns com V(t)
# ===========================================================================
# Pedido do autor (04/11/2026): discutir o jogo de quem extrai da mesma
# floresta com o que a turma ja sabe de rotacao, sem supor g(X). Dois
# vizinhos tem acesso ao mesmo talhao; quem corta primeiro leva toda a
# madeira; se os dois cortam no mesmo ano, dividem. Um corte so, preco
# liquido R$ 1, juros R (3%).
#
#   Pareto: maximizar o valor conjunto e a rotacao de Wicksell (41 anos).
#   Melhor resposta a "o outro corta aos T": cortar aos T - 1 e levar tudo,
#   pois V(T-1)(1+r) > V(T)/2 para todo T de 3 a 41.
#   Nash: a corrida desce de 41 ate 2 anos.
#   A condicao de antecipar e a regra do risco com theta = 1/2.


def vp(x, t):
    return x / (1 + R) ** t


def melhor_resposta_corte(T, N=2):
    """O outro corta aos T. s < T leva tudo; s = T divide por N; s > T nada."""
    op = {s: vp(V(s), s) for s in range(0, T)}
    op[T] = vp(V(T) / N, T)
    return max(op, key=op.get)


def fim_da_corrida(N=2, T=None):
    T = T_W3 if T is None else T
    while melhor_resposta_corte(T, N) != T:
        T = melhor_resposta_corte(T, N)
    return T


T_PARETO = max(range(0, 120), key=lambda t: vp(V(t), t))
T_NASH = fim_da_corrida()
assert T_PARETO == T_W3 == 41 and T_NASH == 2
assert round(V(41)) == 1402 and round(V(41) / 2, 1) == 700.9
assert round(vp(V(41) / 2, 41), 1) == 208.6 and round(vp(V(41), 41)) == 417
assert round(V(2), 1) == 23.9 and round(V(2) / 2, 2) == 11.96
assert round(vp(V(2) / 2, 2), 1) == 11.3 and round(vp(V(2), 2), 1) == 22.5
# melhor resposta: um ano antes, de 3 a 41; aos 2, esperar e dividir;
# depois de 41, cortar aos 41 (Wicksell) antes do outro.
assert all(melhor_resposta_corte(T) == T - 1 for T in range(3, 42))
assert melhor_resposta_corte(2) == 2
assert all(melhor_resposta_corte(T) == 41 for T in range(42, 80))
# tabela do slide "A Corrida": T -> (cortar um ano antes, esperar e dividir)
TABELA_CORRIDA = {41: (1400.8, 700.9), 28: (826.2, 422.2), 10: (168.6, 95.0),
                  3: (24.6, 19.4), 2: (11.3, 12.0)}
for _T, (_antes, _divide) in TABELA_CORRIDA.items():
    assert round(V(_T - 1) * (1 + R), 1) == _antes
    assert round(V(_T) / 2, 1) == _divide
assert round(V(40)) == 1360
# a condicao de antecipar e a regra do risco com theta = 1/2
for _T in range(1, 80):
    assert ((1 + R) * V(_T - 1) >= V(_T) / 2) == \
           ((1 + R) * V(_T - 1) >= (1 - 0.5) * V(_T))
assert rotacao_risco(0.5) == T_NASH
# com tres ou mais vizinhos, a corrida termina com 1 ano
assert fim_da_corrida(3) == 1 and fim_da_corrida(5) == 1
# nota de orador: cortar com 1 ano tambem e equilibrio (pior)
_EQ = [t for t in range(1, 80) if vp(V(t - 1), t - 1) <= vp(V(t) / 2, t)]
assert _EQ == [1, 2]
PASSOS_CORRIDA = (35, 28, 20, 10, 3)


def corrida():
    titulo = "Valor presente da madeira, por idade de corte"
    t, p = moldura(titulo, LARG, ALT, (0, 62), (0, 480), "t", "R$")
    for v in (100, 200, 300, 400):
        p.marca_y(v, str(v))
    f = lambda x: vp(V(x), x)
    p.curva(f, 0, 62, cor=COR_PROD, larg=2.8)
    for s in PASSOS_CORRIDA:
        p.ponto(s, f(s), r=3.5, cor=COR_APAGADA)
    # Pareto no topo: o texto fica acima do maximo (417) e abaixo de 480
    p.guia(T_PARETO, f(T_PARETO))
    p.ponto(T_PARETO, f(T_PARETO), r=5.5)
    p.marca_x(T_PARETO, "41")
    p.texto(T_PARETO, 440, "Pareto: 417 (208,6 cada)", cor=COR_DESTAQUE,
            negrito=True, ancora="middle")
    # Nash: ponto em t = 2; o rotulo a direita, abaixo da curva
    assert all(f(x) > 80 for x in range(8, 62))
    p.ponto(T_NASH, f(T_NASH), r=5.5, cor=COR_DANO)
    p.marca_x(T_NASH, "2")
    p.texto(8, 40, "Nash: 22,5 (11,3 cada)", cor=COR_DANO, negrito=True)
    # a corrida, acima da curva (que fica abaixo de 340 ate t = 24) e abaixo
    # da guia horizontal do Pareto (417), que cortava o rotulo em 395
    assert all(f(x) < 340 for x in range(0, 25)) and 345 + 35 < f(T_PARETO)
    p.texto(1.5, 345, "corrida: 41 → 40 → 39 → … → 2", cor=COR_DANO,
            negrito=True)
    rodape(t, LARG, ALT, "juntos, cortam aos 41; na corrida, aos 2. O valor"
           " da floresta cai de 417 para 22,5")
    t.salvar("15-corrida.svg", titulo)


# ===========================================================================
# 3. Grilagem: o valor de uma posse
# ===========================================================================
# Recursao de um ano, com o lucro e o titulo chegando no fim do ano:
#   W_G = [pi_G + lambda W_O + (1 - lambda) W_G] / (1 + r)
#   => W_G (r + lambda) = pi_G + lambda W_O
# Grila-se quando W_G >= I (custo de ocupar: desmatar a area minima).

R_G = 0.05            # juros
LAMBDA = 0.05         # chance anual de obter o titulo (espera media 20 anos)
W_O = 4000.0          # terra titulada (renda de R$ 200/ha/ano a 5%)
PI_G = -50.0          # lucro anual da ocupacao ilegal (negativo)
I_OCUP = 1000.0       # custo de ocupar
PSA = 100.0           # pagamento por hectare de floresta, por ano


def W_G(lam, pi=PI_G, wo=W_O):
    return (pi + lam * wo) / (R_G + lam)


def limiar(pi=PI_G, wo=W_O):
    """lambda a partir do qual W_G >= I."""
    return (I_OCUP * R_G - pi) / (wo - I_OCUP)


# a recursao de um ano tem W_G como ponto fixo
_w = W_G(LAMBDA)
assert abs((PI_G + LAMBDA * W_O + (1 - LAMBDA) * _w) / (1 + R_G) - _w) < 1e-9
assert abs(W_O - 200 / R_G) < 1e-9
assert abs(W_G(LAMBDA) - 1500) < 1e-9 and W_G(LAMBDA) > I_OCUP
assert abs(W_G(0) - PI_G / R_G) < 1e-9 and W_G(0) == -1000
LAM_BASE = limiar()
# PSA pago so a quem tem titulo. (O "canal 2", PSA a quem so declara a terra,
# saiu da aula a pedido do autor em 04/11/2026, com a figura 15-grilagem-3.)
W_O_PSA = W_O + PSA / R_G
LAM_PSA_TIT = limiar(wo=W_O_PSA)
assert W_O_PSA == 6000
assert abs(LAM_BASE - 1 / 30) < 1e-12           # espera media de 30 anos
assert abs(LAM_PSA_TIT - 1 / 50) < 1e-12        # 50 anos
assert abs(W_G(LAMBDA, wo=W_O_PSA) - 2500) < 1e-9


# Ate 4.000: o rotulo "PSA ao titulado" fica acima do fim da curva azul
# (3.667 em lambda = 10%) sem encostar no titulo.
X_G, Y_G = (0, 0.105), (-1200, 4000)
assert W_G(0.10, wo=W_O_PSA) + 150 < Y_G[1]
TIT_G = "Quanto vale ocupar um hectare de terra pública?"


def grilagem(etapa):
    t, p = moldura(TIT_G, LARG, ALT, X_G, Y_G, "λ", "R$/ha")
    for v in (-1000, 0, 1000, 2000, 3000):
        p.marca_y(v, fmt(v, 0))
    p.reta(0, 0, 0.10, 0, cor=COR_GUIA, larg=1.0)
    p.reta(0, I_OCUP, 0.10, I_OCUP, cor=COR_EIXO, larg=1.6, tracejado="7 4")
    p.texto(0.10, I_OCUP - 420, "custo de ocupar (I)", cor=COR_EIXO,
            ancora="end", italico=False)
    cor_b = COR_PROD if etapa == 1 else COR_APAGADA
    p.curva(W_G, 0, 0.10, cor=cor_b, larg=2.8)
    p.texto(0.10, W_G(0.10) + 150, "sem PSA", cor=cor_b, ancora="end",
            negrito=True)
    if etapa == 1:
        p.reta(LAM_BASE, Y_G[0], LAM_BASE, I_OCUP, cor=COR_GUIA, larg=1.1,
               tracejado="4 3")
        p.ponto(LAM_BASE, I_OCUP, r=5.5)
        p.marca_x(LAM_BASE, "1/30")
        p.ponto(LAMBDA, W_G(LAMBDA), r=5.5, cor=COR_CMG)
        p.texto(LAMBDA - 0.002, W_G(LAMBDA) + 250, "λ = 5%: R$ 1.500",
                cor=COR_CMG, negrito=True, ancora="end")
        p.marca_x(0.05, "5%")
        p.marca_x(0.10, "10%")
        texto = ("grila-se quando a chance anual do título passa de 1/30:"
                 " espera média de até 30 anos")
        nome = "15-grilagem-1.svg"
    else:
        p.marca_x(LAM_BASE, "1/30", cor=COR_APAGADA)
        p.curva(lambda x: W_G(x, wo=W_O_PSA), 0, 0.10, cor=COR_DANO, larg=2.8)
        p.texto(0.10, W_G(0.10, wo=W_O_PSA) + 150, "PSA ao titulado",
                cor=COR_DANO, ancora="end", negrito=True)
        p.reta(LAM_PSA_TIT, Y_G[0], LAM_PSA_TIT, I_OCUP, cor=COR_GUIA,
               larg=1.1, tracejado="4 3")
        p.ponto(LAM_PSA_TIT, I_OCUP, r=5.5)
        p.marca_x(LAM_PSA_TIT, "1/50")
        texto = ("PSA de R$ 100/ha só para quem tem título: a terra titulada"
                 " vale R$ 6.000 e basta λ = 1/50")
        nome = "15-grilagem-2.svg"
    rodape(t, LARG, ALT, texto)
    t.salvar(nome, TIT_G)


def main():
    print("aula 15 - recursos comuns")
    volume()
    media_anual()
    taxa_crescimento()
    faustmann(1)
    faustmann(2)
    habitat()
    risco()
    corrida()
    for k in (1, 2):
        grilagem(k)
    print()
    print("  conferencia:")
    print("    florestas: inflexao {:.1f}, maximo {:.1f}, biologica {}".format(
        T_INFLEXAO, T_MAX_VOL, T_BIO))
    print("    Wicksell: {}".format(", ".join(
        "r={} -> {}".format(pct(r, 0), T) for r, T in sorted(T_W.items()))))
    print("    Faustmann (r=3%, D=200): T={}, S={:.1f}; com habitat T={},"
          " S={:.1f}".format(T_F, S_F, T_AVE, S_AVE))
    print("    risco: theta={} -> T={} (taxa {}); tabela {}".format(
        pct(THETA, 0), T_RISCO, pct(TAXA_RISCO, 2), TABELA_RISCO))
    print("    corrida: Pareto {} (VP {:.1f} cada), Nash {} (VP {:.1f} cada);"
          " N=3 -> {}".format(T_PARETO, vp(V(T_PARETO) / 2, T_PARETO), T_NASH,
                              vp(V(T_NASH) / 2, T_NASH), fim_da_corrida(3)))
    print("    grilagem: W_G(5%)={:.0f}, limiar 1/{:.0f}; PSA titulado"
          " 1/{:.0f}".format(W_G(LAMBDA), 1 / LAM_BASE, 1 / LAM_PSA_TIT))


if __name__ == "__main__":
    main()
