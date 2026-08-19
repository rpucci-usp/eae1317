#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Gera os diagramas da aula 06 (Comando e Controle e Imposto sobre Emissoes).

Motivo de existir: no .pptx os quatro slides que carregam o argumento inteiro do
padrao uniforme sao marcados "(LOUSA)" e trazem soltos sete rotulos de area
(a, b, c, d, e, f) que o texto nunca explica. Dois deles, "e" e "f", colidem com
a variavel "e" de emissao, que aparece na mesma frase ("Firma 2 absorve e+f").
Nao ha o que recuperar com shapes2svg.py; ha o que desenhar.

A unica figura recuperavel do bloco e a soma horizontal (slide 31 do .pptx), e
ela e refeita aqui pelo mesmo motivo das outras: era desenho a mao, com a curva
agregada sem o bico que a algebra exige.

A economia desenhada e a MESMA da aula 04 — de proposito. O padrao uniforme
desta aula e, numero por numero, o preset "corte igual" do widget de la, e a
aliquota de Pigou desta aula e o multiplicador mu* de la. Recalibrar quebraria
as duas pontes:

    CMg_1(e1) = 100 - e1          C_1(e1) = (100 - e1)^2 / 2
    CMg_2(e2) =  50 - 0,5 e2      C_2(e2) = (100 - e2)^2 / 4
    D'(E)     = 0,2 E             D(E)    = 0,1 E^2

    otimo:           mu* = 25, e1* = 75, e2* = 50, E* = 125
    padrao uniforme: e-barra = E*/2 = 62,5 nas duas firmas

No padrao uniforme as duas alturas NAO se igualam (37,5 contra 18,75), e a
diferenca de custo de abatimento e 117,2 — que e exatamente a distancia entre
os presets "corte igual" (2.617) e "otimo" (2.500) do widget da aula 04.

O peso morto e desenhado como duas areas entre e-barra e o otimo, e nao como
uma sobra numerica: a Firma 1 emite mais e economiza a area B, a Firma 2 emite
menos e gasta a area C, a emissao total nao muda (logo o dano nao muda) e o
saldo B - C e o desperdicio. As letras sao maiusculas porque as minusculas do
.pptx colidiam com a variavel de emissao.

Depende so da biblioteca padrao, como os outros scripts desta pasta.

    py scripts/figuras06svg.py

Escreve em aulas/_assets/figuras/.
"""

import os

# Reaproveita a maquinaria da aula 04 em vez de reimplementa-la, como
# figuras05svg.py ja faz: as tres familias aparecem no mesmo bloco de aulas e
# precisam ler como a mesma coisa (vermelho = custo de abatimento, azul = dano,
# azul-escuro = ganho, halo branco nos rotulos, mesma seta de eixo).
from figuras04svg import (Painel, Tela, COR_CMG, COR_DANO, COR_EIXO,
                          COR_GUIA, COR_DESTAQUE, SUB1, SUB2)

# --- a economia desenhada (identica a da aula 04) ---------------------------
E_CHAPEU = 100.0     # emissao de cada firma sem regulacao (as duas iguais)
C1 = 1.0             # inclinacao do CMg da firma 1 (custo alto)
C2 = 0.5             # inclinacao do CMg da firma 2 (custo baixo)
D = 0.2              # inclinacao do dano marginal

MU = 25.0                        # nivel comum de custo marginal no otimo
E1 = E_CHAPEU - MU / C1          # 75
E2 = E_CHAPEU - MU / C2          # 50
E_TOT = E1 + E2                  # 125
E_BARRA = E_TOT / 2              # 62,5 — o padrao uniforme e-barra = E*/J

cmg1 = lambda e: C1 * (E_CHAPEU - e)
cmg2 = lambda e: C2 * (E_CHAPEU - e)
dano_mg = lambda e: D * e
custo1 = lambda e: (E_CHAPEU - e) ** 2 / 2
custo2 = lambda e: (E_CHAPEU - e) ** 2 / 4

# As duas alturas sob o padrao uniforme. Sao o assunto da primeira figura, e
# por isso saem da funcao em vez de virem digitadas no rotulo.
H1 = cmg1(E_BARRA)               # 37,5
H2 = cmg2(E_BARRA)               # 18,75

# O que a Firma 1 economiza indo de e-barra a e1*, e o que a Firma 2 gasta indo
# de e-barra a e2*. A emissao total nao muda (as duas se deslocam 12,5 em
# sentidos opostos), logo o dano nao entra na conta e o saldo e o peso morto.
GANHO_1 = custo1(E_BARRA) - custo1(E1)      # 390,625
CUSTO_2 = custo2(E2) - custo2(E_BARRA)      # 273,4375
PESO_MORTO = GANHO_1 - CUSTO_2              # 117,1875

# Confere a algebra em vez de confiar nos numeros da docstring: se alguem mexer
# num parametro e esquecer de refazer a conta, o script para aqui em vez de
# gerar uma figura bonita e errada.
assert abs(D * E_TOT - MU) < 1e-9, "mu* nao satisfaz D'(E*) = mu*"
assert abs(cmg1(E1) - cmg2(E2)) < 1e-9, "as duas firmas nao igualam CMg no otimo"
assert H1 > H2, "o padrao uniforme deveria deixar CMg_1 ACIMA de CMg_2"
assert abs((E1 - E_BARRA) + (E2 - E_BARRA)) < 1e-9, "a emissao total mudou"
assert abs(PESO_MORTO - 117.1875) < 1e-6, "o peso morto mudou"
# A ponte com o widget da aula 04: custo social do padrao uniforme menos o do
# otimo tem que dar o mesmo peso morto, e os dois presets de la (2.617 e 2.500)
# tem que continuar sendo estes numeros.
SC_UNIF = custo1(E_BARRA) + custo2(E_BARRA) + 0.1 * E_TOT ** 2
SC_OTIMO = custo1(E1) + custo2(E2) + 0.1 * E_TOT ** 2
assert abs(SC_UNIF - SC_OTIMO - PESO_MORTO) < 1e-6
assert round(SC_UNIF) == 2617 and round(SC_OTIMO) == 2500, \
    "os presets do widget da aula 04 sairam de sincronia"

# A aliquota de Pigou e o mesmo numero: tau* = D'(E*) = mu*.
TAU = MU

# --- geometria --------------------------------------------------------------
# Duas familias, limitadas por lados diferentes no slide (a mesma distincao ja
# registrada em figuras04svg.py): a de dois paineis bate no max-height do
# .diagram e pode alargar de graca; a de tres bate no max-width e pode esticar
# para baixo.
LARG_2P = 440
LARG_3P = 340
ALT_3P = 380
X_MAX = 115          # os dois paineis de firma, com e-chapeu = 100
X_MAX_AGR = 215      # o painel agregado, com E-chapeu = 200
Y_MAX = 108          # escala vertical COMPARTILHADA — ver Painel.__doc__
FOLGA_DIR = 16       # espaco para o rotulo do eixo x do painel mais a direita
# Altura das duas setas de realocacao da figura 3. As duas na MESMA altura, e
# acima das duas areas (a mais alta tem 37,5): numa figura cujo assunto e a
# comparacao de alturas, duas setas em alturas diferentes seriam lidas como
# informacao. Dentro das areas elas ficavam navy sobre vermelho solido.
Y_SETA = 46


def fmt(v):
    """Numero em portugues, sem casa decimal sobrando.

    "18,8" no rotulo do eixo com "18,75" no rodape da mesma figura e o tipo de
    divergencia que a turma nota e o autor nao.
    """
    inteiro, _, dec = "{:.4f}".format(v).partition(".")
    dec = dec.rstrip("0")
    milhar = "{:,}".format(int(inteiro)).replace(",", ".")
    return milhar + ("," + dec if dec else "")


def duas_firmas(titulo_extra=""):
    """A moldura comum das quatro figuras de dois paineis.

    Os dois paineis dividem a MESMA escala vertical. Aqui isso importa ainda
    mais do que na aula 04: o assunto das figuras 1 a 3 e justamente que as
    duas alturas NAO coincidem sob o padrao uniforme, e com escalas
    independentes as duas alturas apareceriam iguais.
    """
    # +FOLGA_DIR na largura: o rotulo do eixo horizontal do painel da direita
    # e escrito a 16px depois do fim do eixo, com ancora "start", e sem a folga
    # ele fica cortado pela borda do viewBox. Na aula 04 isso passou porque o
    # rotulo de la ("E") e mais estreito que "e₂"; medido, aqui sobrava 4px.
    t = Tela(2 * LARG_2P + FOLGA_DIR, Painel.ALT + 30)
    p1 = Painel(t, 0, LARG_2P, (0, X_MAX), (0, Y_MAX))
    p2 = Painel(t, LARG_2P, LARG_2P, (0, X_MAX), (0, Y_MAX))

    p1.titulo("Firma 1 (custo alto)" + titulo_extra)
    p2.titulo("Firma 2 (custo baixo)" + titulo_extra)
    p1.eixos("e" + SUB1, "CMg" + SUB1)
    p2.eixos("e" + SUB2, "CMg" + SUB2)

    p1.reta(0, cmg1(0), E_CHAPEU, 0, cor=COR_CMG)
    p2.reta(0, cmg2(0), E_CHAPEU, 0, cor=COR_CMG)
    p1.marca_x(E_CHAPEU, "ê" + SUB1)
    p2.marca_x(E_CHAPEU, "ê" + SUB2)
    return t, p1, p2


def rodape(t, texto, cor=COR_DESTAQUE):
    t.texto((2 * LARG_2P + FOLGA_DIR) / 2, Painel.ALT + 20, texto,
            ancora="middle", tam=15, cor=cor, negrito=True)


def barra_uniforme(p):
    """A vertical tracejada em e-barra, identica nos dois paineis."""
    p.reta(E_BARRA, 0, E_BARRA, Y_MAX - 12, cor=COR_GUIA, larg=1.1,
           tracejado="4 3")
    p.marca_x(E_BARRA, "ē", cor=COR_DESTAQUE)


# ---------------------------------------------------------------------------
# 1. o padrao uniforme deixa as duas alturas diferentes
# ---------------------------------------------------------------------------

def figura_padrao_1():
    t, p1, p2 = duas_firmas()
    for p in (p1, p2):
        barra_uniforme(p)

    # A horizontal na altura da Firma 1 atravessa os DOIS paineis, e e ela que
    # faz o argumento: no painel da direita o ponto cai visivelmente abaixo
    # dela. E honesto atravessar porque a escala vertical e a mesma; o que
    # seria desonesto e desenhar cada painel na sua propria escala.
    y_h1 = p1.py(H1)
    t.add('<line x1="{:.1f}" y1="{:.1f}" x2="{:.1f}" y2="{:.1f}"'
          ' stroke="{}" stroke-width="1.4" stroke-dasharray="7 4"/>'
          .format(p1.px(0) - 4, y_h1, p2.px(X_MAX), y_h1, COR_GUIA))

    p1.ponto(E_BARRA, H1)
    p2.ponto(E_BARRA, H2)
    p1.marca_y(H1, fmt(H1))
    p2.marca_y(H2, fmt(H2))
    p2.reta(0, H2, E_BARRA, H2, cor=COR_GUIA, larg=1.1, tracejado="4 3")

    rodape(t, "com o mesmo limite nas duas, CMg₁ = 37,5 e CMg₂ = 18,75:"
              " as alturas não se igualam", cor=COR_CMG)
    return t


# ---------------------------------------------------------------------------
# 2. os dois custos de abatimento sob o padrao uniforme
# ---------------------------------------------------------------------------

def figura_padrao_2():
    t, p1, p2 = duas_firmas()
    for p in (p1, p2):
        barra_uniforme(p)

    p1.area([(E_BARRA, 0), (E_CHAPEU, 0), (E_BARRA, H1)], COR_CMG, 0.80)
    p2.area([(E_BARRA, 0), (E_CHAPEU, 0), (E_BARRA, H2)], COR_CMG, 0.80)
    # Rotulo dentro do triangulo so quando o triangulo comporta: aqui os dois
    # tem 37,5 de 115 unidades de largura, entao cabe (na aula 04 nao cabia, e
    # o rotulo branco caia fora da area preenchida — branco sobre branco).
    p1.texto(E_BARRA + 12, H1 * 0.30, "A", cor="#ffffff", negrito=True,
             tam=16, halo=False)
    p2.texto(E_BARRA + 12, H2 * 0.30, "D", cor="#ffffff", negrito=True,
             tam=16, halo=False)
    p1.ponto(E_BARRA, H1)
    p2.ponto(E_BARRA, H2)

    rodape(t, "A e D são os custos de abatimento de cada firma sob o padrão"
              " uniforme", cor=COR_CMG)
    return t


# ---------------------------------------------------------------------------
# 3. a realocacao e o peso morto
# ---------------------------------------------------------------------------

def figura_padrao_3():
    t, p1, p2 = duas_firmas()
    for p in (p1, p2):
        barra_uniforme(p)

    # B: o que a Firma 1 economiza indo de e-barra ate e1* (emite MAIS).
    # Azul-escuro porque na aula 05 essa cor ja e "ganho de negociacao", e e a
    # mesma ideia: area entre duas disposicoes a pagar.
    p1.area([(E_BARRA, 0), (E1, 0), (E1, cmg1(E1)), (E_BARRA, H1)],
            COR_DESTAQUE, 0.30)
    # C: o que a Firma 2 gasta indo de e-barra ate e2* (emite MENOS).
    p2.area([(E2, 0), (E_BARRA, 0), (E_BARRA, H2), (E2, cmg2(E2))],
            COR_CMG, 0.80)

    p1.texto(0.5 * (E_BARRA + E1), H1 * 0.34, "B", cor=COR_DESTAQUE,
             negrito=True, tam=16)
    p2.texto(0.5 * (E2 + E_BARRA), H2 * 0.30, "C", cor="#ffffff",
             negrito=True, tam=16, halo=False)

    for p, e_est in ((p1, E1), (p2, E2)):
        p.reta(e_est, 0, e_est, Y_MAX - 12, cor=COR_GUIA, larg=1.1,
               tracejado="4 3")
    p1.marca_x(E1, "e" + SUB1 + "*", cor=COR_DESTAQUE)
    p2.marca_x(E2, "e" + SUB2 + "*", cor=COR_DESTAQUE)

    # As setas dizem para que lado cada firma se move (ver Y_SETA).
    for p, xa, xb in ((p1, E_BARRA, E1), (p2, E_BARRA, E2)):
        pa, pb = p.p(xa, Y_SETA), p.p(xb, Y_SETA)
        p.t.add('<line x1="{:.1f}" y1="{:.1f}" x2="{:.1f}" y2="{:.1f}"'
                ' stroke="{}" stroke-width="1.8" marker-end="url(#seta)"/>'
                .format(pa[0], pa[1], pb[0], pb[1], COR_DESTAQUE))

    rodape(t, "a emissão total não muda, logo o dano não muda:"
              " B − C = {} é puro desperdício"
              .format(fmt(round(PESO_MORTO, 1))))
    return t


# ---------------------------------------------------------------------------
# 4. o imposto: uma altura so, escolhida por cada firma
# ---------------------------------------------------------------------------

def figura_imposto():
    t, p1, p2 = duas_firmas()

    # Uma unica linha em pixels atravessando os dois paineis. Aqui ela e
    # honesta pelo motivo que a figura 1 nao tinha: sob o imposto as duas
    # alturas SAO o mesmo numero.
    y_tau = p1.py(TAU)
    t.add('<line x1="{:.1f}" y1="{:.1f}" x2="{:.1f}" y2="{:.1f}"'
          ' stroke="{}" stroke-width="1.6" stroke-dasharray="7 4"/>'
          .format(p1.px(0) - 4, y_tau, p2.px(X_MAX), y_tau, COR_DESTAQUE))
    p1.marca_y(TAU, "τ*", cor=COR_DESTAQUE)

    for p, e_est, sub in ((p1, E1, SUB1), (p2, E2, SUB2)):
        p.reta(e_est, 0, e_est, TAU, cor=COR_GUIA, larg=1.1, tracejado="4 3")
        p.ponto(e_est, TAU)
        p.marca_x(e_est, "e" + sub + "*", cor=COR_DESTAQUE)

    # e-barra fica na figura, apagado, para a comparacao com as tres anteriores
    # ficar disponivel sem trocar de slide.
    for p in (p1, p2):
        p.marca_x(E_BARRA, "ē", cor=COR_GUIA)

    rodape(t, "ninguém precisou dizer a cada firma quanto cortar:"
              " as duas param onde CMg = τ*")
    return t


# ---------------------------------------------------------------------------
# 5. a soma horizontal (refaz o slide 31 do .pptx)
# ---------------------------------------------------------------------------

def cmg_agregado(E):
    """Inversa da soma horizontal e_1(tau) + e_2(tau).

    e_1(tau) = 100 - tau  e  e_2(tau) = max(0, 100 - 2 tau), entao

        tau >= 50  ->  so a firma 1 emite:  E = 100 - tau
        tau <= 50  ->  as duas emitem:      E = 200 - 3 tau

    O bico em (E, tau) = (50, 50) e o ponto em que a firma 2 zera a emissao, e
    e o rotulo "tau_2" do slide original. Desenhar a agregada como uma reta so
    — que e o que o desenho a mao do .pptx faz — apaga esse bico.
    """
    return 100.0 - E if E <= 50.0 else (200.0 - E) / 3.0


assert abs(cmg_agregado(E_TOT) - TAU) < 1e-9, "a agregada nao passa por (E*, tau*)"
assert abs(cmg_agregado(50.0) - 50.0) < 1e-9, "o bico saiu do lugar"


def figura_agregado():
    t = Tela(3 * LARG_3P, ALT_3P + 40)
    p1 = Painel(t, 0 * LARG_3P, LARG_3P, (0, X_MAX), (0, Y_MAX), ALT_3P)
    p2 = Painel(t, 1 * LARG_3P, LARG_3P, (0, X_MAX), (0, Y_MAX), ALT_3P)
    p3 = Painel(t, 2 * LARG_3P, LARG_3P, (0, X_MAX_AGR), (0, Y_MAX), ALT_3P)

    p1.titulo("Firma 1")
    p2.titulo("Firma 2")
    p3.titulo("Soma horizontal: E(τ)")
    p1.eixos("e" + SUB1, "τ")
    p2.eixos("e" + SUB2, "τ")
    p3.eixos("E", "τ")

    p1.reta(0, cmg1(0), E_CHAPEU, 0, cor=COR_CMG)
    p2.reta(0, cmg2(0), E_CHAPEU, 0, cor=COR_CMG)
    p3.curva(cmg_agregado, 0, 2 * E_CHAPEU, cor=COR_CMG, n=200)
    p3.reta(0, 0, X_MAX_AGR, dano_mg(X_MAX_AGR), cor=COR_DANO)
    p3.texto(X_MAX_AGR - 6, dano_mg(X_MAX_AGR) + 6, "D′(E)", cor=COR_DANO,
             negrito=True, ancora="end")

    p1.marca_x(E_CHAPEU, "ê" + SUB1)
    p2.marca_x(E_CHAPEU, "ê" + SUB2)
    p3.marca_x(2 * E_CHAPEU, "Ê")

    # O bico da agregada, que e onde a firma 2 para de emitir.
    p3.ponto(50, 50, cor=COR_CMG, r=3.5)
    p3.marca_y(50, "τ" + SUB2)
    p2.marca_y(cmg2(0), "τ" + SUB2)

    # tau* atravessa os tres paineis: mesma escala vertical, mesmo numero.
    y_tau = p1.py(TAU)
    t.add('<line x1="{:.1f}" y1="{:.1f}" x2="{:.1f}" y2="{:.1f}"'
          ' stroke="{}" stroke-width="1.6" stroke-dasharray="7 4"/>'
          .format(p1.px(0) - 4, y_tau, p3.px(X_MAX_AGR), y_tau, COR_DESTAQUE))
    p1.marca_y(TAU, "τ*", cor=COR_DESTAQUE)

    for p, e_est, rot in ((p1, E1, "e" + SUB1 + "(τ*)"),
                          (p2, E2, "e" + SUB2 + "(τ*)"),
                          (p3, E_TOT, "E*")):
        p.reta(e_est, 0, e_est, TAU, cor=COR_GUIA, larg=1.1, tracejado="4 3")
        p.ponto(e_est, TAU)
        p.marca_x(e_est, rot, cor=COR_DESTAQUE)

    t.texto(1.5 * LARG_3P, ALT_3P + 28,
            "E(τ*) = e₁(τ*) + e₂(τ*) = 125, e é onde a agregada cruza D′(E)",
            ancora="middle", tam=15, cor=COR_DESTAQUE, negrito=True)
    return t


def main():
    # Sem acento nem grego no print: o console do Windows abre em cp1252 e um
    # "tau" solto aqui derruba o script depois de ele ja ter feito tudo certo.
    print("Figuras da aula 06 (e-barra = {:.1f}, alturas {:.1f} e {:.2f},"
          " peso morto {:.4f}, tau* = {:.0f}):"
          .format(E_BARRA, H1, H2, PESO_MORTO, TAU))
    figura_padrao_1().salvar(
        "06-padrao-1.svg",
        "Padrão uniforme: os custos marginais de abatimento não se igualam")
    figura_padrao_2().salvar(
        "06-padrao-2.svg",
        "Custo de abatimento de cada firma sob o padrão uniforme")
    figura_padrao_3().salvar(
        "06-padrao-3.svg",
        "Peso morto do padrão uniforme: o que uma firma economiza supera o que"
        " a outra gasta")
    figura_imposto().salvar(
        "06-imposto.svg",
        "Com o imposto, as duas firmas igualam o custo marginal de abatimento"
        " à alíquota")
    figura_agregado().salvar(
        "06-agregado.svg",
        "Soma horizontal das demandas por emissão e a alíquota ótima")


if __name__ == "__main__":
    main()
