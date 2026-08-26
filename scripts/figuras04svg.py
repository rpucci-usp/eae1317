#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Gera os diagramas da aula 04 (Custos e Danos) a partir das equacoes.

Motivo de existir: no .pptx a aula inteira termina numa figura unica com CINCO
paineis, repetida em quatro slides com esmaecimento — ou seja, o aluno recebe o
desenho pronto e depois assiste partes dele acenderem. Recortada para SVG pelo
conversor, ela sai como um bloco de ~900x575px com sete rotulos soltos (a..g)
que o texto do slide nunca explica.

Aqui a figura e refeita em quatro etapas que constroem o argumento na ordem em
que ele e falado, e nao na ordem em que foi desenhado:

    1. laissez-faire: as firmas param onde CMg = 0, e o dano marginal la e alto
    2. o nivel comum mu* atravessa os tres paineis e devolve e1*, e2*, E*
    3. o custo de abatimento e a area sob CMg entre e* e e-chapeu
    4. o dano total e a area sob D' ate E* — soma das tres areas = custo social

A economia desenhada e exatamente a mesma do widget interativo do slide
seguinte (aulas/_assets/_widget-abatimento.qmd), de proposito: o widget e esta
figura destravada, e os numeros tem que bater quando alguem conferir.

    CMg_1(e1) = 100 - e1          C_1(e1) = (100 - e1)^2 / 2
    CMg_2(e2) =  50 - 0,5 e2      C_2(e2) = (100 - e2)^2 / 4
    D'(E)     = 0,2 E             D(E)    = 0,1 E^2

    CMg_1 = CMg_2 = D'  =>  mu* = 25, e1* = 75, e2* = 50, E* = 125

Depende so da biblioteca padrao, como os outros scripts desta pasta.

    py scripts/figuras04svg.py

Escreve em aulas/_assets/figuras/.
"""

import math
import os

# Mesma linguagem visual das figuras herdadas do .pptx: vermelho para custo de
# abatimento, azul para dano. Trocar isso quebraria a leitura das duas areas na
# etapa 4, que e o unico lugar onde as duas cores aparecem juntas.
COR_CMG = "#C00000"
COR_DANO = "#0070C0"
COR_EIXO = "#000000"
COR_GUIA = "#8a94a0"
COR_APAGADA = "#c8d0d8"
COR_DESTAQUE = "#1b3a5c"
FONTE = 15
# Os rotulos dos eixos (o nome da variavel em cada ponta) sao maiores que o
# resto do texto da figura porque sao os unicos que o aluno precisa ler do
# fundo da sala: sem eles o desenho nao diz de que grandeza esta falando. Os
# rotulos de marca (marca_x/marca_y) continuam em FONTE — sao muitos, e
# aumenta-los junto encheria o eixo.
FONTE_EIXO = 19
# Folga a direita da tela para o rotulo do eixo horizontal do painel mais a
# direita, que o Painel.eixos() escreve FORA da largura do painel. Serve para
# rotulo curto ("E", "e₁"); rotulo longo, como o "permissoes" da aula 07, pede
# folga propria e maior.
FOLGA_ROTULO_X = 16
SUB1 = "₁"
SUB2 = "₂"

DEST = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                    "..", "aulas", "_assets", "figuras")

# --- a economia desenhada ---------------------------------------------------
E_CHAPEU = 100.0     # emissao de cada firma sem regulacao (as duas iguais)
C1 = 1.0             # inclinacao do CMg da firma 1
C2 = 0.5             # inclinacao do CMg da firma 2 (abate mais barato)
D = 0.2              # inclinacao do dano marginal

MU = 25.0            # nivel comum de custo marginal no otimo
E1 = E_CHAPEU - MU / C1          # 75
E2 = E_CHAPEU - MU / C2          # 50
E_TOT = E1 + E2                  # 125

# Confere a algebra em vez de confiar nos numeros digitados acima: se alguem
# mexer num parametro e esquecer de refazer a conta, o script para aqui em vez
# de gerar uma figura bonita e errada.
assert abs(D * E_TOT - MU) < 1e-9, "mu* nao satisfaz D'(E*) = mu*"

cmg1 = lambda e: C1 * (E_CHAPEU - e)
cmg2 = lambda e: C2 * (E_CHAPEU - e)
dano_mg = lambda e: D * e


def esc(s):
    """Um '<' solto num rotulo derruba o XML inteiro, e nem o Quarto nem o
    revealjs reclamam — a figura simplesmente nao aparece."""
    return str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


class Painel:
    """Um sistema de eixos dentro da tela compartilhada.

    Os tres paineis dividem a MESMA escala vertical e as mesmas bordas de cima
    e de baixo. Isso nao e detalhe de estilo: e o que torna honesta a linha
    horizontal de mu*, que atravessa a figura inteira dizendo "este e o mesmo
    numero nos tres graficos". Com escalas diferentes por painel, a linha
    continuaria bonita e passaria a mentir.
    """

    # TOPO reserva DUAS linhas acima da area de plotagem: o titulo do painel na
    # primeira e o rotulo do eixo vertical na segunda. Com uma linha so, o
    # titulo "Danos sofridos pelos consumidores" passava por cima de "D′(E)".
    #
    # O valor subiu de 46 para 54 quando FONTE_EIXO passou a 19: o rotulo do
    # eixo vertical e escrito a partir da base, entao fonte maior cresce PARA
    # CIMA, e a 46 a caixa dele (24px de altura) encostava na do titulo (que
    # termina em y=20). Medido: com 54 sobram 8px entre as duas.
    ALT = 312
    TOPO = 54
    BASE = 48
    MARG_ESQ = 58
    MARG_DIR = 26

    def __init__(self, tela, x_off, larg, xlim, ylim, alt=None):
        self.t = tela
        self.x_off = x_off
        self.larg = larg
        # A altura e por instancia porque as duas familias de figura sao
        # limitadas por lados diferentes no slide: a de tres paineis bate no
        # max-width (92%) e pode crescer para baixo; a de dois bate no
        # max-height e nao pode.
        if alt is not None:
            self.ALT = alt
        self.x0, self.x1 = xlim
        self.y0, self.y1 = ylim
        self.sx = (larg - self.MARG_ESQ - self.MARG_DIR) / (self.x1 - self.x0)
        self.sy = (self.ALT - self.TOPO - self.BASE) / (self.y1 - self.y0)

    def px(self, x):
        return self.x_off + self.MARG_ESQ + (x - self.x0) * self.sx

    def py(self, y):
        return self.ALT - self.BASE - (y - self.y0) * self.sy

    def p(self, x, y):
        return (self.px(x), self.py(y))

    # -- primitivas ---------------------------------------------------------

    def eixos(self, rot_x, rot_y, apagado=False):
        cor = COR_APAGADA if apagado else COR_EIXO
        seta = "url(#seta-apagada)" if apagado else "url(#seta)"
        self.t.add('<line x1="{:.1f}" y1="{:.1f}" x2="{:.1f}" y2="{:.1f}"'
                   ' stroke="{}" stroke-width="1.2" marker-end="{}"/>'
                   .format(self.px(self.x0), self.py(self.y0),
                           self.px(self.x0), self.py(self.y1) - 8, cor, seta))
        self.t.add('<line x1="{:.1f}" y1="{:.1f}" x2="{:.1f}" y2="{:.1f}"'
                   ' stroke="{}" stroke-width="1.2" marker-end="{}"/>'
                   .format(self.px(self.x0), self.py(self.y0),
                           self.px(self.x1) + 8, self.py(self.y0), cor, seta))
        self.texto(self.px(self.x1) + 16, self.py(self.y0) + 6, rot_x,
                   absoluto=True, cor=cor, tam=FONTE_EIXO)
        self.texto(self.px(self.x0) + 8, self.py(self.y1) - 8, rot_y,
                   absoluto=True, cor=cor, ancora="start", tam=FONTE_EIXO)

    def reta(self, xa, ya, xb, yb, cor=COR_CMG, larg=2.2, tracejado=None):
        pa, pb = self.p(xa, ya), self.p(xb, yb)
        tr = ' stroke-dasharray="{}"'.format(tracejado) if tracejado else ""
        self.t.add('<line x1="{:.1f}" y1="{:.1f}" x2="{:.1f}" y2="{:.1f}"'
                   ' stroke="{}" stroke-width="{:.1f}"{}/>'
                   .format(pa[0], pa[1], pb[0], pb[1], cor, larg, tr))

    def curva(self, f, xa, xb, cor=COR_CMG, larg=2.2, n=120):
        pts = [self.p(xa + (xb - xa) * i / n, f(xa + (xb - xa) * i / n))
               for i in range(n + 1)]
        d = "M {:.1f} {:.1f} ".format(*pts[0])
        d += " ".join("L {:.1f} {:.1f}".format(a, b) for a, b in pts[1:])
        self.t.add('<path d="{}" fill="none" stroke="{}" stroke-width="{:.1f}"'
                   ' stroke-linecap="round"/>'.format(d, cor, larg))

    def area(self, pts, cor, opacidade=1.0):
        d = "M {:.1f} {:.1f} ".format(*self.p(*pts[0]))
        d += " ".join("L {:.1f} {:.1f}".format(*self.p(x, y)) for x, y in pts[1:])
        d += " Z"
        self.t.add('<path d="{}" fill="{}" fill-opacity="{}" stroke="none"/>'
                   .format(d, cor, opacidade))

    def guia(self, x, y, cor=COR_GUIA):
        """As duas tracejadas que levam do eixo ate o ponto (x, y)."""
        self.reta(self.x0, y, x, y, cor=cor, larg=1.1, tracejado="4 3")
        self.reta(x, self.y0, x, y, cor=cor, larg=1.1, tracejado="4 3")

    def marca_x(self, x, rotulo, cor=COR_EIXO):
        cx = self.px(x)
        self.texto(cx, self.py(self.y0) + 20, rotulo, absoluto=True, cor=cor,
                   ancora="middle")

    def marca_y(self, y, rotulo, cor=COR_EIXO):
        cy = self.py(y)
        self.texto(self.px(self.x0) - 8, cy + 5, rotulo, absoluto=True, cor=cor,
                   ancora="end")

    def ponto(self, x, y, cor=COR_DESTAQUE, r=4.5):
        cx, cy = self.p(x, y)
        self.t.add('<circle cx="{:.1f}" cy="{:.1f}" r="{}" fill="{}"'
                   ' stroke="#ffffff" stroke-width="1.5"/>'.format(cx, cy, r, cor))

    def texto(self, x, y, s, absoluto=False, cor=COR_EIXO, italico=True,
              negrito=False, tam=FONTE, ancora="start", halo=True):
        # halo: contorno branco por baixo do glifo. Rotulo posicionado "no
        # vazio" nao sobrevive a mudanca de parametro; o contorno resolve a
        # colisao com curva de uma vez.
        cx, cy = (x, y) if absoluto else self.p(x, y)
        est = ' font-style="italic"' if italico else ""
        peso = ' font-weight="600"' if negrito else ""
        aro = (' stroke="#ffffff" stroke-width="3.5" stroke-linejoin="round"'
               ' paint-order="stroke"') if halo else ""
        self.t.add('<text x="{:.1f}" y="{:.1f}" font-size="{}" fill="{}"'
                   ' text-anchor="{}"{}{}{}>{}</text>'
                   .format(cx, cy, tam, cor, ancora, est, peso, aro, esc(s)))

    def titulo(self, s, cor=COR_EIXO):
        self.texto(self.x_off + self.larg / 2, 15, s, absoluto=True, cor=cor,
                   ancora="middle", italico=False, negrito=True, tam=14)


class Tela:
    def __init__(self, larg, alt):
        self.larg, self.alt = larg, alt
        self.partes = []

    def add(self, s):
        self.partes.append("  " + s)

    def texto(self, x, y, s, cor=COR_EIXO, tam=FONTE, ancora="start",
              italico=False, negrito=False, halo=True):
        est = ' font-style="italic"' if italico else ""
        peso = ' font-weight="600"' if negrito else ""
        aro = (' stroke="#ffffff" stroke-width="3.5" stroke-linejoin="round"'
               ' paint-order="stroke"') if halo else ""
        self.add('<text x="{:.1f}" y="{:.1f}" font-size="{}" fill="{}"'
                 ' text-anchor="{}"{}{}{}>{}</text>'
                 .format(x, y, tam, cor, ancora, est, peso, aro, esc(s)))

    def salvar(self, nome, titulo):
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
            '    <marker id="seta-apagada" markerWidth="9" markerHeight="9"'
            ' refX="5" refY="4.5" orient="auto">\n'
            '      <path d="M0,0 L9,4.5 L0,9 Z" fill="{ca}"/>\n'
            '    </marker>\n'
            '  </defs>\n'
            '{b}\n'
            '</svg>\n'
        ).format(w=self.larg, h=self.alt, t=esc(titulo), c=COR_EIXO,
                 ca=COR_APAGADA, b="\n".join(self.partes))
        if not os.path.isdir(DEST):
            os.makedirs(DEST)
        caminho = os.path.join(DEST, nome)
        with open(caminho, "w", encoding="utf-8") as fh:
            fh.write(svg)
        # Conferir aqui, e nao depois: SVG malformado nao da erro no Quarto nem
        # no revealjs, a figura so nao aparece.
        try:
            import xml.etree.ElementTree as ET
            ET.parse(caminho)
        except Exception as e:
            raise SystemExit("XML invalido em {}: {}".format(nome, e))
        print("  {}  ({} elementos, XML ok)".format(nome, len(self.partes)))


# ---------------------------------------------------------------------------
# As tres etapas do argumento — uma funcao que monta os tres paineis e recebe
# o que acender em cada etapa.
# ---------------------------------------------------------------------------

LARG_P = 340
Y_MAX = 108
# A figura de tres paineis e limitada pela LARGURA no slide (max-width 92%
# do .diagram), nao pela altura: esticar o desenho para baixo e de graca e
# rendeu ~80px de area de plotagem por painel.
ALT_3P = 380


def montar(etapa):
    """etapa 1..4; ver docstring do modulo."""
    # +FOLGA_ROTULO_X pelo mesmo motivo do par total/marginal: o "E" do painel
    # da direita e escrito fora da largura do painel e, com FONTE_EIXO em 19,
    # encostava na borda do viewBox.
    t = Tela(3 * LARG_P + FOLGA_ROTULO_X, ALT_3P + 40)
    p1 = Painel(t, 0 * LARG_P, LARG_P, (0, 115), (0, Y_MAX), ALT_3P)
    p2 = Painel(t, 1 * LARG_P, LARG_P, (0, 115), (0, Y_MAX), ALT_3P)
    p3 = Painel(t, 2 * LARG_P, LARG_P, (0, 215), (0, Y_MAX), ALT_3P)

    p1.titulo("Firma 1 (custo alto)")
    p2.titulo("Firma 2 (custo baixo)")
    p3.titulo("Danos sofridos pelos consumidores")

    p1.eixos("e" + SUB1, "CMg" + SUB1)
    p2.eixos("e" + SUB2, "CMg" + SUB2)
    p3.eixos("E", "D′(E)")

    # curvas
    p1.reta(0, cmg1(0), E_CHAPEU, 0, cor=COR_CMG)
    p2.reta(0, cmg2(0), E_CHAPEU, 0, cor=COR_CMG)
    p3.reta(0, 0, 205, dano_mg(205), cor=COR_DANO)

    p1.marca_x(E_CHAPEU, "ê" + SUB1)
    p2.marca_x(E_CHAPEU, "ê" + SUB2)

    if etapa == 1:
        # Sem regulacao cada firma emite e-chapeu, onde CMg = 0. O dano
        # marginal nesse ponto nao e zero — e a figura inteira do problema.
        e_lf = 2 * E_CHAPEU
        p3.guia(e_lf, dano_mg(e_lf), cor=COR_DANO)
        p3.ponto(e_lf, dano_mg(e_lf), cor=COR_DANO)
        p3.marca_x(e_lf, "ê" + SUB1 + "+ê" + SUB2)
        p3.marca_y(dano_mg(e_lf), "D′")
        p1.ponto(E_CHAPEU, 0)
        p2.ponto(E_CHAPEU, 0)
        t.texto(1.5 * LARG_P, ALT_3P + 28,
                "sem regulação: CMg₁ = CMg₂ = 0, mas o dano marginal é alto",
                ancora="middle", tam=15, cor=COR_DESTAQUE, negrito=True)
        return t

    # etapas 2-4: o nivel comum mu* atravessa os tres paineis --------------
    # Uma unica linha em pixels, porque os tres paineis compartilham a escala
    # vertical (ver docstring de Painel).
    y_mu = p1.py(MU)
    t.add('<line x1="{:.1f}" y1="{:.1f}" x2="{:.1f}" y2="{:.1f}"'
          ' stroke="{}" stroke-width="1.6" stroke-dasharray="7 4"/>'
          .format(p1.px(0) - 4, y_mu, p3.px(215), y_mu, COR_DESTAQUE))

    for p, e_est in ((p1, E1), (p2, E2)):
        p.reta(e_est, 0, e_est, MU, cor=COR_GUIA, larg=1.1, tracejado="4 3")
    p3.reta(E_TOT, 0, E_TOT, MU, cor=COR_GUIA, larg=1.1, tracejado="4 3")

    if etapa >= 3:
        # custo de abatimento = area sob CMg entre e* e e-chapeu
        p1.area([(E1, 0), (E_CHAPEU, 0), (E1, cmg1(E1))], COR_CMG, 0.80)
        p2.area([(E2, 0), (E_CHAPEU, 0), (E2, cmg2(E2))], COR_CMG, 0.80)
    if etapa >= 4:
        # dano total = area sob D' ate E*
        p3.area([(0, 0), (E_TOT, 0), (E_TOT, MU)], COR_DANO, 0.80)

    p1.ponto(E1, MU)
    p2.ponto(E2, MU)
    p3.ponto(E_TOT, MU, cor=COR_DANO)
    p1.marca_x(E1, "e" + SUB1 + "*", cor=COR_DESTAQUE)
    p2.marca_x(E2, "e" + SUB2 + "*", cor=COR_DESTAQUE)
    p3.marca_x(E_TOT, "E*", cor=COR_DESTAQUE)
    p1.marca_y(MU, "μ*", cor=COR_DESTAQUE)

    def rotular_custo(p, e_est, sub):
        """Rotulo do triangulo de custo ACIMA da linha de mu*, e nao dentro do
        triangulo. Dentro so cabe quando o corte e grande: na firma 1 o
        triangulo tem 25 de 115 unidades de largura, e o texto branco caia fora
        da area preenchida — ou seja, branco sobre branco, invisivel."""
        p.texto(0.5 * (e_est + E_CHAPEU), MU + 13,
                "C" + sub + "(e" + sub + "*)", cor=COR_CMG, negrito=True,
                tam=13, ancora="middle")

    if etapa == 2:
        t.texto(1.5 * LARG_P, ALT_3P + 28,
                "no ótimo as três alturas se igualam: CMg₁ ="
                " CMg₂ = D′(E*) = μ*",
                ancora="middle", tam=15, cor=COR_DESTAQUE, negrito=True)
    elif etapa == 3:
        rotular_custo(p1, E1, SUB1)
        rotular_custo(p2, E2, SUB2)
        t.texto(LARG_P, ALT_3P + 28, "custo de abatimento = área sob CMg entre"
                " e* e ê", ancora="middle", tam=15, cor=COR_CMG,
                negrito=True)
    elif etapa == 4:
        rotular_custo(p1, E1, SUB1)
        rotular_custo(p2, E2, SUB2)
        p3.texto(E_TOT * 0.55, MU * 0.28, "D(E*)", cor="#ffffff", negrito=True,
                 tam=13, halo=False)
        t.texto(1.5 * LARG_P, ALT_3P + 28,
                "custo social = C₁(e₁*) + C₂(e₂*) + D(E*)",
                ancora="middle", tam=15, cor=COR_DESTAQUE, negrito=True)
    return t


# ---------------------------------------------------------------------------
# Duas figuras de apoio, para os blocos que hoje sao so texto
# ---------------------------------------------------------------------------

def total_vs_marginal(nome, titulo, f_total, f_marg, xlab, tot_lab, mg_lab,
                      cor, xmax, x_marca, marca_lab, fim_lab=None):
    """C_j(e_j) ao lado de CMg_j(e_j) — ou D(E) ao lado de D'(E).

    O ponto do par e que a curva da direita e a inclinacao da esquerda, e que a
    AREA da direita e a ALTURA da esquerda. O .pptx desenha as duas mas nunca
    liga uma a outra; e onde a turma trava.
    """
    # Paineis mais largos que os de tres colunas: com dois deles, o limite que
    # aperta a figura no slide e a ALTURA (max-height do .diagram), entao
    # alargar e de graca. Com LARG_P a figura saia a 593px de largura num palco
    # de 1075 e parecia perdida no meio do slide.
    larg_p = 440
    # +FOLGA_ROTULO_X: o rotulo do eixo horizontal do painel da direita e
    # escrito 16px depois do fim do eixo, com ancora "start", e fica fora da
    # largura do painel. Com FONTE_EIXO em 19 o "e₁" passou a exceder o viewBox
    # em 6px e saia cortado. Mesma folga que a aula 06 (FOLGA_DIR) e a 07
    # (FOLGA_EX) ja reservam pelo mesmo motivo.
    t = Tela(2 * larg_p + FOLGA_ROTULO_X, Painel.ALT + 6)
    # D(E) cresce e C_j(e_j) decresce, entao o topo da escala esta em pontas
    # opostas — usar f_total(0) fixo daria ylim (0, 0) para o dano e o Painel
    # dividiria por zero.
    pa = Painel(t, 0, larg_p, (0, xmax * 1.06),
                (0, max(f_total(0), f_total(xmax)) * 1.10))
    pb = Painel(t, larg_p, larg_p, (0, xmax * 1.06), (0, max(f_marg(0),
                                                             f_marg(xmax)) * 1.14))
    pa.titulo("Total: " + tot_lab)
    pb.titulo("Marginal: " + mg_lab)
    pa.eixos(xlab, tot_lab)
    pb.eixos(xlab, mg_lab)
    pa.curva(f_total, 0, xmax, cor=cor)
    pb.curva(f_marg, 0, xmax, cor=cor)

    pa.guia(x_marca, f_total(x_marca))
    pa.ponto(x_marca, f_total(x_marca), cor=cor)
    pa.marca_x(x_marca, marca_lab)

    # a area sob a marginal e o nivel da total
    n = 60
    pts = [(x_marca + (xmax - x_marca) * i / n,
            f_marg(x_marca + (xmax - x_marca) * i / n)) for i in range(n + 1)]
    if f_marg(0) > f_marg(xmax):        # custo de abatimento: area a direita
        pb.area([(x_marca, 0)] + pts + [(xmax, 0)], cor, 0.30)
    else:                                # dano: area a esquerda
        pts = [(x_marca * i / n, f_marg(x_marca * i / n)) for i in range(n + 1)]
        pb.area([(0, 0)] + pts + [(x_marca, 0)], cor, 0.30)
    pb.reta(x_marca, 0, x_marca, f_marg(x_marca), cor=COR_GUIA, larg=1.1,
            tracejado="4 3")
    pb.marca_x(x_marca, marca_lab)

    # No par do custo de abatimento, e-chapeu precisa aparecer: e nele que as
    # duas curvas zeram, e e a definicao que o slide anterior acabou de dar.
    # No par do dano nao existe ponto equivalente, por isso o rotulo e opcional.
    if fim_lab:
        pa.marca_x(xmax, fim_lab)
        pb.marca_x(xmax, fim_lab)

    # Sem legenda dentro da figura: ela repetiria palavra por palavra o bullet
    # que vem logo abaixo no slide, e o espaco que ela ocupava vale mais como
    # desenho — a altura e o que aperta estas duas figuras.
    t.salvar(nome, titulo)


def main():
    print("Figuras da aula 04 em {}:".format(os.path.normpath(DEST)))
    for k in (1, 2, 3, 4):
        montar(k).salvar(
            "04-otimo-{}.svg".format(k),
            "Alocação eficiente de emissões, etapa {}".format(k))

    # O texto vira o <title> do SVG — leitor de tela, não legenda na tela.
    total_vs_marginal(
        "04-custo-abatimento.svg",
        "Custo de abatimento total e marginal da firma 1",
        lambda e: (E_CHAPEU - e) ** 2 / 2,
        cmg1, "e" + SUB1, "C" + SUB1 + "(e" + SUB1 + ")",
        "CMg" + SUB1 + "(e" + SUB1 + ")", COR_CMG, E_CHAPEU, E1,
        "e" + SUB1 + "*", "ê" + SUB1)

    total_vs_marginal(
        "04-danos.svg",
        "Dano total e dano marginal da poluição agregada",
        lambda e: 0.1 * e ** 2, dano_mg, "E", "D(E)", "D′(E)",
        COR_DANO, 2 * E_CHAPEU, E_TOT, "E*")


if __name__ == "__main__":
    main()
