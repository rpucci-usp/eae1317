#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Gera os diagramas da aula 05 (Teorema de Coase) a partir das equacoes.

Motivo de existir: o bloco de Coase do .pptx (slides 26-41 do arquivo 04) nao
tem NENHUM diagrama — as dez imagens dos slides sao capturas de texto com a
palavra "LOUSA", ou seja, o desenho era feito a mao no quadro. Nao ha o que
recuperar com shapes2svg.py; ha o que desenhar.

O argumento da aula e que os dois regimes de direito de propriedade levam ao
MESMO E*, e a figura precisa mostrar exatamente isso: a mesma fronteira,
abordada de dois lados. Por isso as duas primeiras figuras compartilham curvas,
escala e moldura, e mudam so o status quo, a seta e qual triangulo esta aceso.

    CMg(E) = 60 - 0,3 E      C(E) = 6000 - 60 E + 0,15 E^2
    D'(E)  = 0,2 E           D(E) = 0,1 E^2

    CMg(E*) = D'(E*)  =>  E* = 120, mu* = 24

    SC(0) = 6.000     SC(E*) = 2.400     SC(Ê) = 4.000

Os dois ganhos de negociacao sao as duas areas entre as curvas, e sao
DIFERENTES de proposito (3.600 pela esquerda, 1.600 pela direita): o teorema
diz que E* nao depende de quem tem o direito, e nao que o excedente nao depende.
Uma calibracao simetrica desenharia melhor e mentiria nesse ponto.

O dano marginal e o mesmo da aula 04 (D' = 0,2 E) para o aluno reconhecer a
curva azul de um deck para o outro. O CMg aqui e agregado — Coase e bilateral,
uma firma e um consumidor — e por isso nao coincide com CMg_1 nem CMg_2 de la.

Depende so da biblioteca padrao, como os outros scripts desta pasta.

    py scripts/figuras05svg.py

Escreve em aulas/_assets/figuras/.
"""

import os

# Reaproveita a maquinaria da aula 04 em vez de reimplementa-la: as figuras das
# duas aulas aparecem com 15 minutos de intervalo e precisam ler como a mesma
# familia (vermelho = custo de abatimento, azul = dano, halo branco nos
# rotulos, mesma seta de eixo).
from figuras04svg import (Painel, Tela, COR_CMG, COR_DANO, COR_EIXO,
                          COR_GUIA, COR_DESTAQUE)

# --- a economia desenhada ---------------------------------------------------
E_CHAPEU = 200.0     # emissao da firma sem restricao nenhuma; C(Ê) = 0
A = 60.0             # intercepto do custo marginal de abatimento
B = 0.3              # inclinacao (em modulo) do custo marginal de abatimento
D = 0.2              # inclinacao do dano marginal

E_OTIMO = A / (B + D)            # 120
MU = D * E_OTIMO                 # 24

cmg = lambda e: A - B * e
dano_mg = lambda e: D * e
custo = lambda e: A * (E_CHAPEU - e) - B * (E_CHAPEU ** 2 - e ** 2) / 2
dano = lambda e: D * e ** 2 / 2

# Confere a algebra em vez de confiar nos numeros da docstring: se alguem mexer
# num parametro e esquecer de refazer a conta, o script para aqui em vez de
# gerar uma figura bonita e errada.
assert abs(cmg(E_CHAPEU)) < 1e-9, "CMg(Ê) deveria ser zero"
assert abs(cmg(E_OTIMO) - dano_mg(E_OTIMO)) < 1e-9, "E* nao iguala CMg a D'"
assert abs(custo(0) - 6000) < 1e-6, "C(0) mudou"
assert abs(custo(E_OTIMO) + dano(E_OTIMO) - 2400) < 1e-6, "SC(E*) mudou"

# Os dois ganhos sao os dois triangulos entre as curvas. Calculados aqui, e nao
# digitados no rotulo, porque o rotulo e a unica coisa que o leitor confere.
GANHO_ESQ = (custo(0) + dano(0)) - (custo(E_OTIMO) + dano(E_OTIMO))       # 3600
GANHO_DIR = (custo(E_CHAPEU) + dano(E_CHAPEU)) - (custo(E_OTIMO)
                                                 + dano(E_OTIMO))          # 1600
assert abs(GANHO_ESQ - 3600) < 1e-6 and abs(GANHO_DIR - 1600) < 1e-6

# --- geometria da tela ------------------------------------------------------
# Painel unico e largo. Diferente da figura de tres paineis da aula 04, aqui o
# que aperta e a ALTURA (o slide leva figura + dois bullets), entao alargar e
# de graca e esticar para baixo nao e.
LARG = 820
ALT_P = 336
X_MAX = 218
Y_MAX = 70


def fmt(v):
    return "{:,.0f}".format(v).replace(",", ".")


def moldura(titulo_painel):
    """A parte que as tres figuras tem identica: curvas, eixos, E*, mu*."""
    t = Tela(LARG, ALT_P + 32)
    p = Painel(t, 0, LARG, (0, X_MAX), (0, Y_MAX), ALT_P)
    p.titulo(titulo_painel)
    p.eixos("E", "R$/t")

    p.reta(0, cmg(0), E_CHAPEU, 0, cor=COR_CMG)
    p.reta(0, 0, X_MAX, dano_mg(X_MAX), cor=COR_DANO)

    # Rotulos nas pontas, e nao no meio: o meio e onde moram os dois
    # triangulos, e um rotulo la dentro some sob o preenchimento.
    p.texto(9, cmg(0) + 5, "CMg(E)", cor=COR_CMG, negrito=True, ancora="start")
    p.texto(X_MAX - 6, dano_mg(X_MAX) + 5, "D′(E)", cor=COR_DANO, negrito=True,
            ancora="end")

    p.guia(E_OTIMO, MU)
    p.ponto(E_OTIMO, MU)
    p.marca_x(E_OTIMO, "E*", cor=COR_DESTAQUE)
    p.marca_y(MU, "μ*", cor=COR_DESTAQUE)
    p.marca_x(E_CHAPEU, "Ê")
    return t, p


def seta_horizontal(p, xa, xb, y=3.4):
    """A seta que diz de onde a negociacao parte e para onde ela vai.

    Fica colada ao eixo x de proposito: e a unica faixa horizontal que nenhum
    dos dois triangulos ocupa em nenhuma das tres figuras.

    Sem rotulo em cima dela, pela mesma razao registrada em
    total_vs_marginal() na aula 04: a frase repetiria o bullet que vem logo
    abaixo no slide. Aqui havia um motivo a mais — uma legenda de ~230px
    centrada na seta atravessa o triangulo da direita perto de Ê, onde a
    fronteira CMg ja desceu quase ate o eixo.
    """
    pa, pb = p.p(xa, y), p.p(xb, y)
    p.t.add('<line x1="{:.1f}" y1="{:.1f}" x2="{:.1f}" y2="{:.1f}"'
            ' stroke="{}" stroke-width="1.8" marker-end="url(#seta)"/>'
            .format(pa[0], pa[1], pb[0], pb[1], COR_DESTAQUE))


def triangulo_esq(p, opacidade=0.22):
    """Ganhos partindo de E = 0: vertices (0,0), (0, CMg(0)) e (E*, mu*)."""
    p.area([(0, 0), (0, cmg(0)), (E_OTIMO, MU)], COR_DESTAQUE, opacidade)


def triangulo_dir(p, opacidade=0.22):
    """Ganhos partindo de Ê: vertices (E*, mu*), (Ê, D'(Ê)) e (Ê, 0)."""
    p.area([(E_OTIMO, MU), (E_CHAPEU, dano_mg(E_CHAPEU)), (E_CHAPEU, 0)],
           COR_DESTAQUE, opacidade)


def rotulo_area(p, x, y, valor):
    p.texto(x, y, "ganhos = " + fmt(valor), cor=COR_DESTAQUE, negrito=True,
            tam=14, ancora="middle", italico=False)


def figura_consumidor():
    t, p = moldura("O consumidor detém o direito: sem contrato, E = 0")
    triangulo_esq(p)
    rotulo_area(p, 42, 27, GANHO_ESQ)
    p.ponto(0, 0, cor=COR_DESTAQUE, r=5)
    seta_horizontal(p, 5, 114)
    t.texto(LARG / 2, ALT_P + 22,
            "cada tonelada autorizada vale mais para a firma do que custa ao"
            " consumidor — até E*",
            ancora="middle", tam=15, cor=COR_DESTAQUE, negrito=True)
    return t


def figura_firma():
    t, p = moldura("A firma detém o direito: sem contrato, E = Ê")
    triangulo_dir(p)
    rotulo_area(p, 172, 20, GANHO_DIR)
    p.ponto(E_CHAPEU, 0, cor=COR_DESTAQUE, r=5)
    seta_horizontal(p, 196, 126)
    t.texto(LARG / 2, ALT_P + 22,
            "cada tonelada abatida custa menos à firma do que vale ao"
            " consumidor — até E*",
            ancora="middle", tam=15, cor=COR_DESTAQUE, negrito=True)
    return t


def figura_dois_lados():
    t, p = moldura("Os dois caminhos param no mesmo lugar")
    triangulo_esq(p, 0.16)
    triangulo_dir(p, 0.16)
    rotulo_area(p, 42, 27, GANHO_ESQ)
    rotulo_area(p, 172, 20, GANHO_DIR)
    p.ponto(0, 0, cor=COR_DESTAQUE, r=5)
    p.ponto(E_CHAPEU, 0, cor=COR_DESTAQUE, r=5)
    seta_horizontal(p, 5, 114)
    seta_horizontal(p, 196, 126)
    t.texto(LARG / 2, ALT_P + 22,
            "o excedente depende de quem tem o direito; o ponto onde ele acaba,"
            " não",
            ancora="middle", tam=15, cor=COR_DESTAQUE, negrito=True)
    return t


def main():
    # Sem acento nem grego no print: o console do Windows abre em cp1252 e um
    # "mu" solto aqui derruba o script depois de ele ja ter feito tudo certo.
    print("Figuras da aula 05 (E* = {:.0f}, mu* = {:.0f}, ganhos {} e {}):"
          .format(E_OTIMO, MU, fmt(GANHO_ESQ), fmt(GANHO_DIR)))
    figura_consumidor().salvar(
        "05-coase-1.svg", "Ganhos de negociação quando o consumidor detém o"
        " direito de propriedade")
    figura_firma().salvar(
        "05-coase-2.svg", "Ganhos de negociação quando a firma detém o direito"
        " de propriedade")
    figura_dois_lados().salvar(
        "05-coase-3.svg", "Os dois regimes de direito de propriedade levam ao"
        " mesmo nível de emissão")


if __name__ == "__main__":
    main()
