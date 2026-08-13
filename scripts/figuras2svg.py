#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Gera os diagramas da aula 02 a partir das equacoes, nao a mao.

Motivo de existir: os SVG recuperados do .pptx foram desenhados a mao no
PowerPoint, e a conferencia da geometria mostrou dois defeitos tipicos disso —
no diagrama de equilibrio a curva de indiferenca *cruzava* a reta de preco em
vez de tangencia-la (inclinacoes 1,51 contra 1,07), e a curva de contrato da
Caixa de Edgeworth era um rabisco de sessenta segmentos Bezier tremendo.

Aqui a tangencia sai da algebra: escolhe-se a tecnologia e as preferencias, e o
ponto de tangencia, a inclinacao comum e o preco relativo sao *consequencia*.
Refazer uma figura com outra inclinacao custa mudar um parametro.

Depende so da biblioteca padrao, como os outros scripts desta pasta.

    py scripts/figuras2svg.py

Escreve em aulas/_assets/figuras/. Os arquivos `02-eficiencia-slideNN.svg` sao os
originais vindos do .pptx e nao sao tocados nem referenciados pelo .qmd.
"""

import math
import os

# Linguagem visual herdada dos SVG do .pptx, para as figuras novas nao
# destoarem das que continuam vindo de la.
COR_CURVA = "#0A111D"      # curvas de indiferenca, fronteiras
COR_LOCUS = "#C00000"      # o lugar geometrico em destaque (FPP, curva de contrato)
COR_PRECO = "#0070C0"      # retas de preco / iso-lucro
COR_EIXO = "#000000"
COR_APAGADA = "#b9c4cf"    # etapa anterior, ainda visivel mas fora de foco
COR_SOMBRA = "#dce8f2"     # preenchimento da lente
COR_INVIAVEL = "#8a94a0"
FONTE = 15

# aulas/_assets/figuras, e nao aulas/figuras: os recursos compartilhados foram
# para _assets quando cada aula virou uma pasta com index.qmd dentro. Ficou um
# tempo apontando para o caminho antigo, e como o script so falha na hora de
# escrever, isso so aparece quando alguem tenta regerar as figuras.
DEST = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                    "..", "aulas", "_assets", "figuras")


def esc(s):
    """SVG e XML: um '<' solto num rotulo ('y < 0') derruba o arquivo inteiro, e
    o navegador nao mostra nada — sem erro visivel, so a figura ausente."""
    return (str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))


class Tela:
    """Mapeia coordenadas matematicas (y para cima) em pixels (y para baixo)."""

    def __init__(self, larg, alt, xlim, ylim, margem=(58, 26, 34, 46)):
        # margem: esquerda, direita, cima, baixo
        self.larg, self.alt = larg, alt
        self.x0, self.x1 = xlim
        self.y0, self.y1 = ylim
        me, md, mc, mb = margem
        self.sx = (larg - me - md) / (self.x1 - self.x0)
        self.sy = (alt - mc - mb) / (self.y1 - self.y0)
        self.ox = me - self.x0 * self.sx
        self.oy = alt - mb + self.y0 * self.sy
        self.partes = []

    def px(self, x):
        return self.ox + x * self.sx

    def py(self, y):
        return self.oy - y * self.sy

    def p(self, x, y):
        return (self.px(x), self.py(y))

    # -- primitivas ---------------------------------------------------------

    def add(self, s):
        self.partes.append("  " + s)

    def curva(self, f, xa, xb, cor=COR_CURVA, larg=1.6, n=140, tracejado=None,
              clip_y=None):
        """Amostra y=f(x) e emite como path. Densidade alta o bastante para o
        traco poligonal ser invisivel no tamanho de projecao."""
        pts = []
        for i in range(n + 1):
            x = xa + (xb - xa) * i / n
            try:
                y = f(x)
            except (ValueError, ZeroDivisionError, OverflowError):
                continue
            if not math.isfinite(y):
                continue
            if clip_y and not (clip_y[0] <= y <= clip_y[1]):
                continue
            pts.append(self.p(x, y))
        if len(pts) < 2:
            return
        d = "M {:.2f} {:.2f} ".format(*pts[0])
        d += " ".join("L {:.2f} {:.2f}".format(px, py) for px, py in pts[1:])
        tr = ' stroke-dasharray="{}"'.format(tracejado) if tracejado else ""
        self.add('<path d="{}" fill="none" stroke="{}" stroke-width="{:.2f}"'
                 ' stroke-linecap="round"{}/>'.format(d, cor, larg, tr))

    def reta(self, xa, ya, xb, yb, cor=COR_PRECO, larg=2.2, tracejado=None,
             seta=False):
        pa, pb = self.p(xa, ya), self.p(xb, yb)
        tr = ' stroke-dasharray="{}"'.format(tracejado) if tracejado else ""
        mk = ' marker-end="url(#seta)"' if seta else ""
        self.add('<line x1="{:.2f}" y1="{:.2f}" x2="{:.2f}" y2="{:.2f}"'
                 ' stroke="{}" stroke-width="{:.2f}"{}{}/>'
                 .format(pa[0], pa[1], pb[0], pb[1], cor, larg, tr, mk))

    def area(self, pts, cor=COR_SOMBRA, opacidade=0.85):
        if len(pts) < 3:
            return
        d = "M {:.2f} {:.2f} ".format(*self.p(*pts[0]))
        d += " ".join("L {:.2f} {:.2f}".format(*self.p(x, y)) for x, y in pts[1:])
        d += " Z"
        self.add('<path d="{}" fill="{}" fill-opacity="{}" stroke="none"/>'
                 .format(d, cor, opacidade))

    def ponto(self, x, y, rotulo=None, dx=-14, dy=-9, cor=COR_EIXO):
        cx, cy = self.p(x, y)
        self.add('<circle cx="{:.2f}" cy="{:.2f}" r="4" fill="{}"/>'
                 .format(cx, cy, cor))
        if rotulo:
            self.texto(cx + dx, cy + dy, rotulo, absoluto=True, negrito=True,
                       halo=True)

    def texto(self, x, y, s, absoluto=False, cor=COR_EIXO, italico=True,
              negrito=False, tam=FONTE, ancora="start", halo=False):
        # halo: contorno branco por baixo do glifo. Resolve de uma vez a colisao
        # de rotulo com curva, que e o que mais suja este tipo de diagrama —
        # posicionar rotulo "no vazio" nao sobrevive a mudanca de parametro.
        cx, cy = (x, y) if absoluto else self.p(x, y)
        est = ' font-style="italic"' if italico else ""
        peso = ' font-weight="600"' if negrito else ""
        aro = (' stroke="#ffffff" stroke-width="4" stroke-linejoin="round"'
               ' paint-order="stroke"') if halo else ""
        self.add('<text x="{:.2f}" y="{:.2f}" font-size="{}" fill="{}"'
                 ' text-anchor="{}"{}{}{}>{}</text>'
                 .format(cx, cy, tam, cor, ancora, est, peso, aro, esc(s)))

    def eixos(self, rot_x="x", rot_y="y", y_eixo=0.0):
        """Eixos com seta. y_eixo permite o eixo horizontal nao ficar no fundo
        da tela (necessario quando a figura mostra y negativo)."""
        self.add('<line x1="{:.2f}" y1="{:.2f}" x2="{:.2f}" y2="{:.2f}"'
                 ' stroke="{}" stroke-width="1.2" marker-end="url(#seta)"/>'
                 .format(self.px(self.x0), self.py(self.y0),
                         self.px(self.x0), self.py(self.y1), COR_EIXO))
        self.add('<line x1="{:.2f}" y1="{:.2f}" x2="{:.2f}" y2="{:.2f}"'
                 ' stroke="{}" stroke-width="1.2" marker-end="url(#seta)"/>'
                 .format(self.px(self.x0), self.py(y_eixo),
                         self.px(self.x1), self.py(y_eixo), COR_EIXO))
        self.texto(self.px(self.x1) + 6, self.py(y_eixo) + 5, rot_x, absoluto=True)
        self.texto(self.px(self.x0) - 16, self.py(self.y1) + 4, rot_y, absoluto=True)

    def salvar(self, nome, titulo):
        corpo = "\n".join(self.partes)
        svg = (
            '<svg width="{w}" height="{h}" viewBox="0 0 {w} {h}"\n'
            '     xmlns="http://www.w3.org/2000/svg" role="img"'
            ' font-family="Source Sans Pro, Helvetica, Arial, sans-serif">\n'
            '  <title>{t}</title>\n'
            '  <defs>\n'
            '    <marker id="seta" markerWidth="9" markerHeight="9" refX="5"'
            ' refY="4.5" orient="auto">\n'
            '      <path d="M0,0 L9,4.5 L0,9 Z" fill="{c}"/>\n'
            '    </marker>\n'
            '  </defs>\n'
            '{b}\n'
            '</svg>\n'
        ).format(w=self.larg, h=self.alt, t=esc(titulo), c=COR_EIXO, b=corpo)
        caminho = os.path.join(DEST, nome)
        with open(caminho, "w", encoding="utf-8") as fh:
            fh.write(svg)
        # Conferir aqui, e nao depois: um SVG malformado nao da erro no Quarto
        # nem no revealjs — a figura simplesmente nao aparece.
        try:
            import xml.etree.ElementTree as ET
            ET.parse(caminho)
        except Exception as e:
            raise SystemExit("XML invalido em {}: {}".format(nome, e))
        print("  {}  ({} elementos, XML ok)".format(nome, len(self.partes)))


def raiz(f, a, b, n=80):
    """Bissecao simples. Exige troca de sinal — sem isso ela converge para um
    dos extremos e devolve um numero plausivel e errado, que foi exatamente
    como a reta de preco da etapa 4 acabou comecando no meio da caixa."""
    fa, fb = f(a), f(b)
    if (fa < 0) == (fb < 0):
        raise ValueError("sem troca de sinal em [{}, {}]".format(a, b))
    for _ in range(n):
        m = (a + b) / 2
        fm = f(m)
        if (fa < 0) == (fm < 0):
            a, fa = m, fm
        else:
            b = m
    return (a + b) / 2


def clipar_reta(x0, y0, m, xlim, ylim):
    """Extremos do segmento da reta y = y0 + m(x - x0) dentro da moldura."""
    xs = []
    for x in xlim:
        y = y0 + m * (x - x0)
        if ylim[0] <= y <= ylim[1]:
            xs.append(x)
    for y in ylim:
        if m != 0:
            x = x0 + (y - y0) / m
            if xlim[0] <= x <= xlim[1]:
                xs.append(x)
    xa, xb = min(xs), max(xs)
    return (xa, y0 + m * (xa - x0)), (xb, y0 + m * (xb - x0))


# ---------------------------------------------------------------------------
# 1. Equilibrio de mercado: TMS = px/py = TMT
# ---------------------------------------------------------------------------
# FPP:  (x/a)^2 + (y/b)^2 = 1        inclinacao  -(b^2 x)/(a^2 y)
# Ind.: x^alpha y^(1-alpha) = u      inclinacao  -(alpha/(1-alpha))(y/x)
#
# Igualando as duas, a tangencia cai em  x* = a*sqrt(alpha),  y* = b*sqrt(1-alpha)
# — ponto que satisfaz a FPP por construcao, e cuja inclinacao comum e o preco
# relativo. Nada aqui e ajustado a olho.

def equilibrio():
    a, b, alpha = 1.20, 0.90, 0.55
    xs = a * math.sqrt(alpha)
    ys = b * math.sqrt(1 - alpha)
    m = -(alpha / (1 - alpha)) * (ys / xs)          # inclinacao comum
    k = ys * xs ** (-m_expo(alpha))                  # constante da curva

    t = Tela(480, 380, (0, 1.42), (0, 1.06))
    t.eixos("x", "y")

    # FPP como arco de elipse — exato, sem amostragem
    p0, p1 = t.p(0, b), t.p(a, 0)
    t.add('<path d="M {:.2f} {:.2f} A {:.2f} {:.2f} 0 0 1 {:.2f} {:.2f}"'
          ' fill="none" stroke="{}" stroke-width="2.4"/>'
          .format(p0[0], p0[1], a * t.sx, b * t.sy, p1[0], p1[1], COR_LOCUS))

    ind = lambda x: k * x ** (-m_expo(alpha))
    xa = raiz(lambda x: ind(x) - 1.02, 0.30, xs)
    t.curva(ind, xa, 1.38, clip_y=(0, 1.04))

    # reta de preco: passa pela tangencia com a inclinacao comum
    pa, pb = clipar_reta(xs, ys, m, (0.02, 1.40), (0.02, 1.02))
    t.reta(pa[0], pa[1], pb[0], pb[1])
    x_esq = pa[0]
    y_reta = lambda x: ys + m * (x - xs)

    t.ponto(xs, ys, "E", dx=-28, dy=20)
    t.texto(a * 0.28, b * 0.58, "FPP", cor=COR_LOCUS, negrito=True, italico=False,
            halo=True)
    t.texto(1.16, ind(1.16) + 0.09, "curva de", italico=False, tam=13, halo=True)
    t.texto(1.16, ind(1.16) + 0.04, "indiferença", italico=False, tam=13, halo=True)
    px_, py_ = t.p(x_esq, y_reta(x_esq))
    t.texto(px_ + 10, py_ - 8, "inclinação = −p" + chr(0x2093) + "/p" + chr(0x1D67),
            absoluto=True, tam=13, cor=COR_PRECO, halo=True)
    t.salvar("02-equilibrio-mercado.svg",
             "Equilíbrio de mercado: a reta de preço tangencia a fronteira de "
             "produção e a curva de indiferença no mesmo ponto")


def m_expo(alpha):
    """Expoente da curva de indiferenca escrita como y = k * x^(-e)."""
    return alpha / (1 - alpha)


# ---------------------------------------------------------------------------
# 2. Caixa de Edgeworth, em tres etapas
# ---------------------------------------------------------------------------
# Duas Cobb-Douglas. A curva de contrato sai em forma fechada (igualando as
# TMS), entao e uma curva de verdade e nao um rabisco. O ponto C e o equilibrio
# competitivo a partir da dotacao — calculado, nao escolhido.

A1, A2 = 0.55, 0.45          # expoentes de x para os individuos 1 e 2
# A dotacao precisa estar bem longe da curva de contrato: com ela perto, A, B e
# o equilibrio saem amontoados num canto e a lente da etapa 2 fica invisivel.
DOT = (0.18, 0.70)           # dotacao do individuo 1
PB = (0.32, 0.55)            # ponto intermediario, dentro da lente


def _r(al):
    return al / (1 - al)


def curva1(x0, y0):
    """Curva de indiferenca do individuo 1 por (x0,y0), em coordenadas de 1."""
    k = y0 * x0 ** _r(A1)
    return lambda x: k * x ** (-_r(A1))


def curva2(x0, y0):
    """Idem para o individuo 2, ja convertida para coordenadas de 1."""
    k = (1 - y0) * (1 - x0) ** _r(A2)
    return lambda x: 1 - k * (1 - x) ** (-_r(A2))


def contrato(x):
    a, b = _r(A1), _r(A2)
    return b * x / (a - (a - b) * x)


def equilibrio_competitivo():
    ex, ey = DOT
    # mercado de x: alpha1*m1/p + alpha2*m2/p = 1, com py = 1
    # => A1*(ex*p+ey) + A2*((1-ex)*p+(1-ey)) = p
    num = A1 * ey + A2 * (1 - ey)
    den = 1 - (A1 * ex + A2 * (1 - ex))
    p = num / den
    m1 = ex * p + ey
    return (A1 * m1 / p, (1 - A1) * m1, p)


def lente(f1, f2, xa, xb):
    """Poligono entre as duas curvas, entre seus dois cruzamentos."""
    dif = lambda x: f1(x) - f2(x)
    xs = raiz(dif, xa + 1e-4, xb)
    cima = [(xa + (xs - xa) * i / 60, f2(xa + (xs - xa) * i / 60)) for i in range(61)]
    baixo = [(xs - (xs - xa) * i / 60, f1(xs - (xs - xa) * i / 60)) for i in range(61)]
    return cima + baixo


def edgeworth():
    cx, cy, preco = equilibrio_competitivo()
    etapas = [
        ("02-edgeworth-1.svg", 1, "dotação e ganhos de troca"),
        ("02-edgeworth-2.svg", 2, "um ponto melhor para os dois, ainda ineficiente"),
        ("02-edgeworth-3.svg", 3, "tangência e curva de contrato"),
        # A etapa 4 nasceu de uma incompatibilidade: a figura herdada do .pptx
        # para "Preços Relativos e TMS" chamava o equilíbrio de D e carregava um
        # ponto C orfao, sem curva passando por ele. Com a caixa redesenhada, os
        # dois slides passariam a usar letras diferentes para o mesmo ponto.
        # Aqui a reta de preco entra na mesma caixa das etapas anteriores, e o
        # equilibrio continua sendo C.
        ("02-edgeworth-4.svg", 4, "reta de preço pela dotação, tangente em C"),
    ]
    for nome, etapa, sub in etapas:
        t = Tela(660, 392, (0, 1), (0, 1), margem=(52, 52, 30, 40))
        borda = [(0, 0), (1, 0), (1, 1), (0, 1)]
        d = "M {:.2f} {:.2f} ".format(*t.p(*borda[0]))
        d += " ".join("L {:.2f} {:.2f}".format(*t.p(x, y)) for x, y in borda[1:])
        t.add('<path d="{} Z" fill="none" stroke="{}" stroke-width="1.4"/>'
              .format(d, COR_CURVA))

        # lente da etapa corrente, por baixo de tudo
        if etapa == 1:
            t.area(lente(curva1(*DOT), curva2(*DOT), DOT[0], 0.99))
        elif etapa == 2:
            t.area(lente(curva1(*PB), curva2(*PB), PB[0], 0.99))

        # etapas anteriores, apagadas
        if etapa in (2, 3):
            for f in (curva1(*DOT), curva2(*DOT)):
                t.curva(f, 0.14, 0.97, cor=COR_APAGADA, larg=1.3, clip_y=(0.01, 0.99))
        # Na etapa 3 as curvas de B ficam de fora: com a curva de contrato
        # entrando, seis tracos na mesma caixa viram emaranhado.

        # etapa corrente
        if etapa == 1:
            for f in (curva1(*DOT), curva2(*DOT)):
                t.curva(f, 0.14, 0.97, clip_y=(0.01, 0.99))
        elif etapa == 2:
            for f in (curva1(*PB), curva2(*PB)):
                t.curva(f, 0.16, 0.97, clip_y=(0.01, 0.99))
        else:
            t.curva(contrato, 0.0, 1.0, cor=COR_LOCUS, larg=2.4)
            for f in (curva1(cx, cy), curva2(cx, cy)):
                t.curva(f, 0.18, 0.97, clip_y=(0.01, 0.99))

        # etapa 4: a reta de preco passa pela dotacao e tangencia as duas
        # curvas em C — as duas coisas saem do mesmo preco calculado acima
        if etapa == 4:
            pa, pb = clipar_reta(DOT[0], DOT[1], -preco, (0.01, 0.99), (0.01, 0.99))
            t.reta(pa[0], pa[1], pb[0], pb[1], cor=COR_PRECO, larg=2.4)
            # rotulo no extremo inferior direito, que e a parte vazia da caixa
            px_, py_ = t.p(*pb)
            t.texto(px_ - 8, py_ + 20, "inclinação = −p" + chr(0x2093) + "/p"
                    + chr(0x1D67), absoluto=True, tam=13, cor=COR_PRECO,
                    ancora="end", halo=True)

        # pontos
        t.ponto(*DOT, rotulo="A", dx=-20, dy=-10)
        if etapa in (2, 3):
            t.ponto(*PB, rotulo="B", dx=-20, dy=-10)
        if etapa >= 3:
            t.ponto(cx, cy, rotulo="C", dx=12, dy=20)
            t.texto(0.66, contrato(0.66) - 0.13, "curva de contrato",
                    cor=COR_LOCUS, italico=False, tam=13, negrito=True, halo=True)

        # origens e eixos das duas pessoas
        t.texto(t.px(0) - 16, t.py(0) + 16, "1", absoluto=True, negrito=True)
        t.texto(t.px(1) + 8, t.py(1) - 6, "2", absoluto=True, negrito=True)
        t.texto(t.px(0) - 16, t.py(0.5), "y", absoluto=True)
        t.texto(t.px(0.5), t.py(0) + 26, "x", absoluto=True)
        t.texto(t.px(1) + 10, t.py(0.5), "y", absoluto=True)
        t.texto(t.px(0.5), t.py(1) - 12, "x", absoluto=True)
        t.salvar(nome, "Caixa de Edgeworth — " + sub)
    print("     equilíbrio competitivo em ({:.4f}, {:.4f}), px/py = {:.4f}"
          .format(cx, cy, preco))


# ---------------------------------------------------------------------------
# 3. Curvas de iso-lucro: dois bens, e depois y como "mal"
# ---------------------------------------------------------------------------
# y = (pi + C)/py - (px/py) x. O segundo painel muda *so o sinal de py*: a
# inclinacao vira positiva e o intercepto vira negativo. E o trecho com y < 0
# fica visivel, porque e dele que fala o ultimo bullet do slide.

def isolucro():
    xlim, ylim = (0, 0.98), (-0.46, 1.0)

    def moldura(mal):
        t = Tela(560, 392, xlim, ylim, margem=(54, 40, 30, 34))
        if mal:
            p = [(0, ylim[0]), (xlim[1], ylim[0]), (xlim[1], 0), (0, 0)]
            t.area(p, cor="#f2f4f6", opacidade=1.0)
        t.eixos("x", "y", y_eixo=0.0)
        return t

    # painel 1: dois bens, px/py = 0.5, inclinacao negativa
    t = moldura(False)
    for c, rot in zip((0.55, 0.72, 0.89), ("π₁", "π₂", "π₃")):
        t.reta(0, c, xlim[1], c - 0.5 * xlim[1], cor=COR_PRECO, larg=2.0)
        t.texto(t.px(xlim[1]) + 6, t.py(c - 0.5 * xlim[1]) + 5, rot,
                absoluto=True, cor=COR_PRECO, tam=14)
    t.reta(0.30, 0.30, 0.52, 0.56, cor=COR_LOCUS, larg=2.0, seta=True)
    t.texto(t.px(0.53), t.py(0.60), "lucro maior", absoluto=True,
            cor=COR_LOCUS, italico=False, tam=14, negrito=True, halo=True)
    t.texto(t.px(0.02), t.py(-0.30), "p" + chr(0x1D67) + " > 0  →  reta desce,"
            " melhor para nordeste", absoluto=True, italico=False, tam=14,
            halo=True)
    t.salvar("02-isolucro-bens.svg",
             "Curvas de iso-lucro com dois bens: inclinação negativa")

    # painel 2: y e um mal, py < 0 — mesma moldura, so o sinal muda
    t = moldura(True)
    for c, rot in zip((-0.35, -0.18, -0.01), ("π₃", "π₂", "π₁")):
        x_zero = -c / 0.5
        t.reta(0, c, x_zero, 0.0, cor=COR_PRECO, larg=2.0, tracejado="5,4")
        t.reta(x_zero, 0.0, xlim[1], c + 0.5 * xlim[1], cor=COR_PRECO, larg=2.0)
        t.texto(t.px(xlim[1]) + 6, t.py(c + 0.5 * xlim[1]) + 5, rot,
                absoluto=True, cor=COR_PRECO, tam=14)
    t.reta(0.34, 0.42, 0.56, 0.18, cor=COR_LOCUS, larg=2.0, seta=True)
    t.texto(t.px(0.40), t.py(0.52), "lucro maior", absoluto=True,
            cor=COR_LOCUS, italico=False, tam=14, negrito=True, halo=True)
    t.texto(t.px(0.46), t.py(-0.30), "y < 0: sem sentido", absoluto=True,
            cor=COR_INVIAVEL, italico=False, tam=14, halo=True)
    t.texto(t.px(0.02), t.py(-0.40), "p" + chr(0x1D67) + " < 0  →  reta sobe,"
            " melhor para sudeste", absoluto=True, italico=False, tam=14,
            halo=True)
    t.salvar("02-isolucro-mal.svg",
             "Curvas de iso-lucro com y sendo um mal: inclinação positiva e "
             "intercepto negativo")


if __name__ == "__main__":
    print("gerando em aulas/_assets/figuras/:")
    equilibrio()
    edgeworth()
    isolucro()
