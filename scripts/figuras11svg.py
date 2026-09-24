#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Gera os diagramas da aula 11 (Valoracao de Bens Ambientais).

MOTIVO DE EXISTIR
-----------------
O `.pptx` 11 e a aula mais arida do curso: 54 slides, cinco figuras recortadas
de formas nativas do PowerPoint e NENHUM numero. As curvas sao rotuladas
"h(p,u0,q)" e "x(p,y,q)", as areas nao tem tamanho, e VC, VE e excedente do
consumidor aparecem como tres desenhos parecidos que o aluno nao consegue
ordenar. O pedido do autor foi exatamente esse: "gráficos ilustrativos, com
números simples".

Entao aqui tudo tem numero, e os numeros de TODAS as figuras saem de UMA
calibracao so.

A CALIBRACAO, E POR QUE ELA E ESTA
----------------------------------
Bloco de revisao (VC, VE, excedente). Cobb-Douglas com alpha = 1/2:

    U(x, z) = sqrt(x z)      p_z = 1      y = 100      p0 = 4 -> p1 = 1

    Marshalliana   x(p, y) = y / (2p)
    Indireta       V(p, y) = y / (2 sqrt(p))
    Dispendio      E(p, u) = 2 u sqrt(p)
    Hicksiana      h(p, u) = u / sqrt(p)

    u0 = V(4, 100) = 25        u1 = V(1, 100) = 50

    VC = y - E(p1, u0) = 100 - 50  =  50
    VE = E(p0, u1) - y = 200 - 100 = 100
    EC = integral de 50/p entre 1 e 4 = 50 ln 4 = 69,3

Ou seja: VC = 50 < EC = 69,3 < VE = 100, que e a ordem do livro, e os dois
extremos sao numeros redondos. No plano (x, z) os quatro pontos tambem sao
redondos:

    A (p0, y)        = (12,5 ; 50)   sobre u0 = 25
    B (p1, y)        = (50   ; 50)   sobre u1 = 50
    C (p1, y - VC)   = (25   ; 25)   sobre u0   <- a compensacao de VC
    D (p0, y + VE)   = (25   ; 100)  sobre u1   <- a compensacao de VE

As duas figuras do plano (x, z) e as tres do plano (p, x) descrevem EXATAMENTE
os mesmos quatro pontos. Conferir uma contra a outra tem que fechar, e fecha.

O contraste de participacao no orcamento (a tabela do slide "Excedente do
Consumidor") usa a mesma familia com alpha = 1/20, mesma variacao de preco. Os
tres numeros ficam 6,69 / 6,93 / 7,18: o erro do excedente cai de ~40% para
~3,5%. E o argumento de Willig em duas colunas, e e por isso que a literatura
aplicada usa excedente sem pedir desculpas.

Bloco de complementaridade fraca (os "choke prices", que o autor destacou):

    x(p, q0) = (60  - p)/10     preco de esgotamento  60
    x(p, q1) = (100 - p)/10     preco de esgotamento 100
    custo da viagem p0 = 20  ->  4 viagens na praia suja, 8 na limpa

    A(q0) = (60-20) * 4 / 2 =  80
    A(q1) = (100-20)* 8 / 2 = 320
    A     = 320 - 80        = 240   por pessoa por ano

Dois triangulos, tres numeros, e o resultado do `.pptx` inteiro.

Bloco de bens substitutos. A sacada da figura e usar DUAS tecnologias que
passam pelos MESMOS dois pontos e gastam o MESMO tanto:

    perfeitos    f(x, q) = x + q,  H = 10     x = 10 - q
    imperfeitos  f(x, q) = x q,    H = 21     x = 21/q

    q = 3 -> x = 7 -> gasto 35        q = 7 -> x = 3 -> gasto 15
    (com p = 5 nos dois casos)

    economia total: 20, nos dois casos.

    MWTP = -dC/dq:   perfeitos  p        = 5          (constante)
                     imperfeitos p H/q^2 = 105/q^2    (11,67 -> 2,14)

    integral de 105/q^2 entre 3 e 7 = 105 (1/3 - 1/7) = 20   <- fecha

Ou seja: a disposicao TOTAL a pagar pelos quatro pontos de qualidade e a mesma
nas duas tecnologias; a MARGINAL nao e. Essa e a unica figura do curso em que
total e margem sao separados com numeros iguais dos dois lados.

O EXERCICIO
-----------
Versao discreta da complementaridade fraca, com calibracao propria (como nas
aulas 07 a 10, o exercicio nao herda os numeros da figura):

    valor da k-esima viagem, praia suja  = 50 - 10k   (40, 30, 20, 10)
    valor da k-esima viagem, praia limpa = 90 - 10k   (80, 70, ..., 10)
    custo da viagem p = 20

    suja:  3 viagens, excedente  20 + 10 + 0            =  30
    limpa: 7 viagens, excedente  60 + 50 + ... + 10 + 0 = 210
    A = 180 por pessoa por ano

Os precos de esgotamento discretos sao 40 e 80, que sao os dois numeros que o
aluno le direto da escada.

Depende so da biblioteca padrao, como os outros scripts desta pasta.

    py scripts/figuras11svg.py

Escreve em aulas/_assets/figuras/.
"""

import math

from figuras04svg import (Painel, Tela, COR_EIXO, COR_CMG, COR_DANO,
                          COR_GUIA, COR_APAGADA, COR_DESTAQUE,
                          FONTE_LEGENDA)
from figuras08svg import fmt, escada

# Quarta cor do curso. Vermelho e custo, azul e dano, verde e mercado do
# produto (aula 10). O BEM AMBIENTAL q nao tinha cor: ate a aula 10 ele era a
# emissao E, que e o eixo, nunca uma curva. Aqui ele e o assunto, e ganha roxo.
COR_Q = "#6A3D9A"
# O mesmo roxo, mais claro, para o cenario de qualidade BAIXA nas figuras que
# mostram os dois cenarios juntos. Nao e COR_APAGADA: as duas curvas sao
# igualmente o assunto, o que muda e qual delas e o "antes".
COR_Q_CLARO = "#B294CC"
# Verde do mercado do produto (aula 10), reaproveitado para o bem PRIVADO x,
# que aqui e a viagem, o filtro, a garrafa.
COR_PROD = "#2E7D32"

# O rotulo do eixo horizontal e escrito FORA da largura do painel (em
# px(x1) + 16), entao a tela precisa de folga a direita. Como em todas as
# figuras desta aula o rotulo e um simbolo unico ("x" ou "q"), 26px bastam: o
# nome da grandeza vai no rotulo do eixo vertical, que e escrito para dentro.
FOLGA = 26


# A tela reserva DUAS linhas abaixo da area de plotagem, e nao uma. As legendas
# desta aula e da seguinte sao frases inteiras com numeros dentro, e varias
# passam de 90 caracteres: numa linha so elas vazavam pelos dois lados do SVG,
# sem erro nenhum e sem aviso.
ALTURA_RODAPE = 66


def moldura(titulo, larg, alt, xlim, ylim, rot_x, rot_y):
    t = Tela(larg + FOLGA, alt + ALTURA_RODAPE)
    p = Painel(t, 0, larg, xlim, ylim, alt)
    p.titulo(titulo)
    p.eixos(rot_x, rot_y)
    return t, p


def rodape(t, larg, alt, texto):
    """A legenda sob a figura, quebrada em duas linhas quando nao couber.

    O limite sai da largura da tela: a FONTE_LEGENDA em negrito mede cerca de
    8,3px por caractere. A quebra procura o espaco mais proximo do meio, para
    que as duas linhas fiquem parecidas.
    """
    largura = larg + FOLGA
    limite = int(largura / 8.3)
    linhas = [texto]
    if len(texto) > limite:
        meio = len(texto) // 2
        corte = min((abs(i - meio), i) for i, c in enumerate(texto)
                    if c == " ")[1]
        linhas = [texto[:corte], texto[corte + 1:]]
    base = alt + (32 if len(linhas) == 1 else 26)
    for k, linha in enumerate(linhas):
        t.texto(largura / 2, base + 20 * k, linha, ancora="middle",
                tam=FONTE_LEGENDA, cor=COR_DESTAQUE, negrito=True)


# ===========================================================================
# Bloco 1 - VC, VE e excedente, com a Cobb-Douglas calibrada
# ===========================================================================

RENDA = 100.0
P0, P1 = 4.0, 1.0

marsh = lambda p: RENDA / (2 * p)              # x(p, y)
v_ind = lambda p, y: y / (2 * math.sqrt(p))    # V(p, y)
disp = lambda p, u: 2 * u * math.sqrt(p)       # E(p, u)
hicks = lambda p, u: u / math.sqrt(p)          # h(p, u)

U0 = v_ind(P0, RENDA)                          # 25
U1 = v_ind(P1, RENDA)                          # 50
VC = RENDA - disp(P1, U0)                      # 50
VE = disp(P0, U1) - RENDA                      # 100
EC = RENDA / 2 * math.log(P0 / P1)             # 69,31

PT_A = (marsh(P0), RENDA / 2)                        # (12,5 ; 50)
PT_B = (marsh(P1), RENDA / 2)                        # (50   ; 50)
PT_C = ((RENDA - VC) / (2 * P1), (RENDA - VC) / 2)   # (25   ; 25)
PT_D = ((RENDA + VE) / (2 * P0), (RENDA + VE) / 2)   # (25   ; 100)

LARG_XZ, ALT_XZ = 700, 340
# A escala HORIZONTAL e a mesma nas duas figuras, e a vertical nao. Isso e
# deliberado e e o unico lugar do curso em que duas figuras irmas nao
# compartilham os dois eixos. A razao: VC vive todo abaixo de 100 e VE vai ate
# 200; com um enquadramento so, a figura de VC gasta metade da altura vazia e
# amontoa A, B e C num quarto do painel. Como a escala de x e identica, A, B, C
# e D ficam na MESMA posicao horizontal nos dois slides, e o que muda de um
# para o outro e so a marcacao do eixo vertical, que esta escrita na figura.
X_MAX_XZ = 56.0
Z_MAX = {"VC": 115.0, "VE": 215.0}


def _orcamento(p, preco, renda, cor, larg=2.2):
    """A reta z = renda - preco * x, cortada na borda direita do painel."""
    x_fim = min(renda / preco, p.x1)
    p.reta(0, renda, x_fim, renda - preco * x_fim, cor=cor, larg=larg)


def _indiferenca(p, u, cor, larg=2.2):
    """A curva z = u^2 / x, so no trecho que cabe no enquadramento."""
    p.curva(lambda x: u * u / x, u * u / p.y1, p.x1, cor=cor, larg=larg)


def variacao(nome, qual):
    """qual = 'VC' ou 'VE'.

    As duas figuras compartilham o enquadramento e as duas retas de orcamento
    de proposito: o slide seguinte e o mesmo desenho com a outra medida acesa,
    e o aluno precisa ver que nada mais mudou. A de VC usa so a metade de baixo
    do enquadramento, e isso tambem e proposital: a de VE preenche a de cima,
    e a diferenca de altura entre as duas chaves E a diferenca entre as duas
    medidas.
    """
    titulo = {"VC": "Variação Compensada: tirar renda até voltar a u⁰",
              "VE": "Variação Equivalente: dar renda até chegar a u¹"}[qual]
    t, p = moldura(titulo, LARG_XZ, ALT_XZ, (0, X_MAX_XZ), (0, Z_MAX[qual]),
                   "x", "z (R$ gastos em outros bens)")

    # So a curva de indiferenca da medida em questao e desenhada. Com as duas,
    # a de u1 (que sobe ate 200 perto do eixo) atravessa o canto superior da
    # figura de VC e disputa espaco com as duas retas de orcamento, sem ter
    # nada a dizer ali: em VC a utilidade de referencia e u0.
    _orcamento(p, P0, RENDA, COR_APAGADA)
    _orcamento(p, P1, RENDA, COR_APAGADA)

    p.ponto(*PT_A, cor=COR_EIXO, r=4.0)
    p.ponto(*PT_B, cor=COR_EIXO, r=4.0)

    if qual == "VC":
        _indiferenca(p, U0, COR_Q, larg=2.8)
        _orcamento(p, P1, RENDA - VC, COR_DESTAQUE)
        p.ponto(*PT_C, cor=COR_DESTAQUE)
        p.texto(PT_A[0], PT_A[1] + 12, "A", cor=COR_EIXO, negrito=True,
                ancora="middle")
        p.texto(PT_B[0] + 1.5, PT_B[1] + 8, "B", cor=COR_EIXO, negrito=True)
        p.texto(PT_C[0] + 1.6, PT_C[1] + 7, "C", cor=COR_DESTAQUE,
                negrito=True)
        # Rotulos de duas letras, e nao "reta de orcamento a p⁰": as quatro
        # retas convergem para o mesmo ponto (0, 100) e qualquer legenda mais
        # longa atravessa uma delas. Quem sao as retas esta no slide.
        p.texto(44, 60, "p¹", cor=COR_APAGADA, negrito=True)
        p.texto(23.5, 13, "p⁰", cor=COR_APAGADA, negrito=True)
        p.texto(46, 20, "u⁰ = 25", cor=COR_Q, negrito=True)
        p.texto(20, 45, "p¹ com VC", cor=COR_DESTAQUE, negrito=True)
        y_alto, y_baixo, rot = RENDA, RENDA - VC, "VC = 50"
        p.marca_y(RENDA, "100")
        p.marca_y(RENDA - VC, "50")
        p.marca_x(PT_A[0], "12,5")
        p.marca_x(PT_C[0], "25", cor=COR_DESTAQUE)
        p.marca_x(PT_B[0], "50")
        rod = ("ao preço novo, tirar R$ 50 da renda devolve o consumidor à"
               " curva u⁰: VC = 100 − 50 = 50")
    else:
        _indiferenca(p, U1, COR_Q, larg=2.8)
        _orcamento(p, P0, RENDA + VE, COR_DESTAQUE)
        p.ponto(*PT_D, cor=COR_DESTAQUE)
        p.texto(PT_A[0], PT_A[1] - 16, "A", cor=COR_EIXO, negrito=True,
                ancora="middle")
        p.texto(PT_B[0] + 1.5, PT_B[1] + 12, "B", cor=COR_EIXO, negrito=True)
        p.texto(PT_D[0] + 1.6, PT_D[1] + 13, "D", cor=COR_DESTAQUE,
                negrito=True)
        p.texto(33, 78, "p¹", cor=COR_APAGADA, negrito=True)
        p.texto(17, 30, "p⁰", cor=COR_APAGADA, negrito=True)
        p.texto(43, 70, "u¹ = 50", cor=COR_Q, negrito=True)
        p.texto(14, 130, "p⁰ com VE", cor=COR_DESTAQUE, negrito=True)
        y_alto, y_baixo, rot = RENDA + VE, RENDA, "VE = 100"
        p.marca_y(RENDA + VE, "200")
        p.marca_y(RENDA, "100")
        p.marca_x(PT_A[0], "12,5")
        p.marca_x(PT_D[0], "25", cor=COR_DESTAQUE)
        p.marca_x(PT_B[0], "50")
        rod = ("ao preço antigo, dar R$ 100 de renda leva o consumidor à"
               " curva u¹: VE = 200 − 100 = 100")

    # A chave vertical fica colada no eixo z porque e LA que a medida mora: as
    # duas figuras do .pptx marcavam VC e VE no meio do desenho, longe do eixo,
    # e assim o aluno nao ve que a resposta e uma quantia em dinheiro.
    xa = 2.6
    p.reta(xa, y_baixo, xa, y_alto, cor=COR_DESTAQUE, larg=2.2)
    for yy in (y_alto, y_baixo):
        p.reta(xa - 1.1, yy, xa + 1.1, yy, cor=COR_DESTAQUE, larg=2.2)
    p.texto(xa + 2.2, (y_alto + y_baixo) / 2 + 5, rot, cor=COR_DESTAQUE,
            negrito=True, italico=False)

    rodape(t, LARG_XZ, ALT_XZ, rod)
    t.salvar(nome, titulo)


# --- as tres areas no plano (p, x) -----------------------------------------

LARG_PX, ALT_PX = 700, 330
X_MAX_PX, P_MAX_PX = 58.0, 5.6

CURVAS = (
    ("m", marsh, COR_PROD, "x(p, y)"),
    ("h0", lambda pp: hicks(pp, U0), COR_CMG, "h(p, u⁰)"),
    ("h1", lambda pp: hicks(pp, U1), COR_DANO, "h(p, u¹)"),
)


def _traco(p, f, cor, larg=2.4):
    """A curva x = f(p), desenhada so onde ela cabe.

    As tres explodem perto de p = 0 (a marshalliana e 50/p), entao o inicio nao
    pode ser fixo: e o primeiro preco em que a quantidade ja cabe dentro do
    enquadramento.
    """
    pp = 0.40
    while pp < P_MAX_PX and f(pp) > p.x1:
        pp += 0.01
    pts = [(f(pp + (P_MAX_PX - pp) * k / 90.0),
            pp + (P_MAX_PX - pp) * k / 90.0) for k in range(91)]
    d = "M {:.1f} {:.1f} ".format(*p.p(*pts[0]))
    d += " ".join("L {:.1f} {:.1f}".format(*p.p(a, b)) for a, b in pts[1:])
    p.t.add('<path d="{}" fill="none" stroke="{}" stroke-width="{:.1f}"'
            ' stroke-linecap="round"/>'.format(d, cor, larg))


def _faixa(p, f, cor, opac):
    """A area A ESQUERDA da curva, entre p1 e p0.

    A integral da aula e em PRECO e nao em quantidade, entao a area e uma faixa
    horizontal. Pintar a area SOB a curva (a vertical) e o erro classico neste
    slide, e daria o excedente do produtor.
    """
    pts = [(0, P1)]
    pts += [(f(P1 + (P0 - P1) * k / 60.0), P1 + (P0 - P1) * k / 60.0)
            for k in range(61)]
    pts.append((0, P0))
    p.area(pts, cor, opac)


def areas(nome, qual):
    """qual = 'VC', 'VE' ou 'EC'."""
    cfg = {
        "VC": ("Variação Compensada é a área à esquerda de h(p, u⁰)", "h0",
               "VC = 50: a área à esquerda da Hicksiana que passa por A"),
        "VE": ("Variação Equivalente é a área à esquerda de h(p, u¹)", "h1",
               "VE = 100: a mesma conta, na Hicksiana que passa por B"),
        "EC": ("Excedente do Consumidor fica entre as duas", "m",
               "EC ≈ 69,3 está entre VC = 50 e VE = 100, e não é nenhum"
               " dos dois"),
    }
    titulo, acesa, rod = cfg[qual]
    t, p = moldura(titulo, LARG_PX, ALT_PX, (0, X_MAX_PX), (0, P_MAX_PX),
                   "x", "p (R$ por viagem)")

    for chave, f, cor, _ in CURVAS:
        if chave == acesa:
            _faixa(p, f, cor, 0.26)

    p.reta(0, P0, X_MAX_PX, P0, cor=COR_GUIA, larg=1.1, tracejado="4 3")
    p.reta(0, P1, X_MAX_PX, P1, cor=COR_GUIA, larg=1.1, tracejado="4 3")

    for chave, f, cor, rot in CURVAS:
        viva = chave == acesa
        # No slide do excedente as tres curvas ficam acesas: o recado e o
        # SANDUICHE, e com as Hicksianas apagadas a area do meio nao diz nada.
        c = cor if (viva or qual == "EC") else COR_APAGADA
        _traco(p, f, c, larg=2.6 if viva else 2.0)
        if viva:
            p.texto(f(P_MAX_PX - 0.5) + 2, P_MAX_PX - 0.45, rot, cor=c,
                    negrito=True)

    p.marca_y(P0, "4")
    p.marca_y(P1, "1")
    p.texto(p.px(0) - 8, p.py(P0) - 12, "p⁰", absoluto=True, ancora="end",
            cor=COR_EIXO)
    p.texto(p.px(0) - 8, p.py(P1) - 12, "p¹", absoluto=True, ancora="end",
            cor=COR_EIXO)

    if qual == "VC":
        p.texto(8.5, 2.45, "VC = 50", cor=COR_CMG, negrito=True,
                italico=False, ancora="middle")
    elif qual == "VE":
        p.texto(17.0, 2.45, "VE = 100", cor=COR_DANO, negrito=True,
                italico=False, ancora="middle")
    else:
        p.texto(9.0, 3.3, "EC ≈ 69,3", cor=COR_PROD, negrito=True,
                italico=False, ancora="middle")
        p.texto(hicks(1.45, U0) - 1.5, 1.45, "VC = 50", cor=COR_CMG,
                negrito=True, italico=False, ancora="end")
        p.texto(hicks(1.45, U1) + 1.5, 1.45, "VE = 100", cor=COR_DANO,
                negrito=True, italico=False)

    rodape(t, LARG_PX, ALT_PX, rod)
    t.salvar(nome, titulo)


# --- a mesma melhora, agora medida em q ------------------------------------
#
# A transicao do bloco de preco para o bloco de bem ambiental dizia "e a mesma
# conta, com q no lugar de p". Nao e: no mundo do preco VC e VE sao AREAS, e do
# jeito como estava a area sumia, bem depois de dez slides ensinando a ve-la.
#
# A analogia certa de integral de h dp nao e "nada", e integral de MWTP dq. A
# disposicao marginal a pagar por q e a demanda inversa compensada por q, e a
# area dela entre q0 e q1 E a VC.
#
# A calibracao nao inventa um segundo consumidor. E a mesma Cobb-Douglas, com q
# entrando multiplicativo:
#
#     U(x, z, q) = q sqrt(x z)      y = 100      p PARADO em p0 = 4
#     q: 1 -> 2
#
#     V(p, y, q) = q y / (2 sqrt(p))        E(p, u, q) = 2 sqrt(p) u / q
#
# Com isso u0 = 25 e u1 = 50, que sao os MESMOS do exemplo de preco, e dai
# VC = 50 e VE = 100, tambem os mesmos. Nao e coincidencia: com preferencias
# homoteticas E e linear em u, entao VC = y(1 - u0/u1) e VE = y(u1/u0 - 1). As
# duas mudancas dobram a utilidade, logo valem o mesmo. A medida nao se importa
# com o que se moveu, e sim com quanto o consumidor melhorou.
#
#     MWTP(q, u) = -dE/dq = 2 sqrt(p) u / q^2   ->   100/q^2 em u0, 200/q^2 em u1
#
# E O PONTO CEGO, que e o assunto do slide seguinte: com essa U a demanda por x
# nao depende de q. O consumidor fica em x = 12,5 antes e depois, ou seja, no
# ponto A das tres figuras anteriores. Ele dobrou de bem-estar e nenhum mercado
# viu. E o caso polar, e existe para motivar os dois blocos que vem depois.

Q0, Q1 = 1.0, 2.0

v_ind_q = lambda p, y, q: q * y / (2 * math.sqrt(p))
disp_q = lambda p, u, q: 2 * math.sqrt(p) * u / q
mwtp_q = lambda q, u: 2 * math.sqrt(P0) * u / (q * q)

assert abs(v_ind_q(P0, RENDA, Q0) - U0) < 1e-9, "u0 do caso q saiu dos 25"
assert abs(v_ind_q(P0, RENDA, Q1) - U1) < 1e-9, "u1 do caso q saiu dos 50"

VC_Q = RENDA - disp_q(P0, U0, Q1)
VE_Q = disp_q(P0, U1, Q0) - RENDA
assert abs(VC_Q - VC) < 1e-9, "a VC do caso q deixou de bater com a do preco"
assert abs(VE_Q - VE) < 1e-9, "a VE do caso q deixou de bater com a do preco"

# A area sob a MWTP entre q0 e q1 E a medida. Conferida por soma de Riemann,
# porque e exatamente isso que a figura desenha.
def _area_mwtp(u, n=200000):
    passo = (Q1 - Q0) / n
    return sum(mwtp_q(Q0 + (k + 0.5) * passo, u) for k in range(n)) * passo

assert abs(_area_mwtp(U0) - VC) < 1e-4, "a area sob MWTP(., u0) nao e mais VC"
assert abs(_area_mwtp(U1) - VE) < 1e-4, "a area sob MWTP(., u1) nao e mais VE"
# O ponto cego, em numero: a demanda por x nao se mexe.
assert abs(marsh(P0) - 12.5) < 1e-9

# O enquadramento e RECORTADO em torno de [1, 2], e nao comeca em q = 0.
# Primeira versao ia de 0 a 2,45 e a faixa que interessa virava uma fatia de um
# terco da largura, com o resto ocupado pela cauda plana da hiperbole, que nao
# diz nada. Com 0,75 a 2,25 a faixa fica nos dois tercos do meio. O eixo nao
# comecar em zero e aceitavel aqui porque q e um indice de qualidade e os dois
# valores que importam estao marcados.
# ATENCAO ao nome: `Q_MAX` ja existe neste arquivo, no bloco de substitutos, e
# e definido DEPOIS daqui. Como a funcao so le a variavel na hora da chamada,
# usar `Q_MAX` aqui pegava o 10,6 de la e a figura saia com o eixo esticado,
# sem erro nenhum. Prefixo AQ = area-q.
AQ_MIN, AQ_MAX, AQ_Y_MAX = 0.75, 2.25, 215.0


def _curva_q(p, u, cor, larg=2.6):
    """MWTP = 2 sqrt(p0) u / q^2, do ponto em que ela entra no quadro ate o fim.

    Ela explode perto de q = 0, como as tres do plano (p, x), entao o inicio
    nao pode ser fixo.
    """
    qq = AQ_MIN
    while qq < AQ_MAX and mwtp_q(qq, u) > p.y1:
        qq += 0.005
    pts = [(qq + (AQ_MAX - qq) * k / 120.0, mwtp_q(qq + (AQ_MAX - qq) * k / 120.0, u))
           for k in range(121)]
    d = "M {:.1f} {:.1f} ".format(*p.p(*pts[0]))
    d += " ".join("L {:.1f} {:.1f}".format(*p.p(a, b)) for a, b in pts[1:])
    p.t.add('<path d="{}" fill="none" stroke="{}" stroke-width="{:.1f}"'
            ' stroke-linecap="round"/>'.format(d, cor, larg))


def _area_q(p, u, cor, opac):
    """A area SOB a curva, entre q0 e q1.

    No bloco de preco a area era uma faixa HORIZONTAL, a esquerda da curva,
    porque a integral era em preco. Aqui a integral e em q, entao a area e a
    vertical, sob a curva. A figura existe em boa parte para mostrar essa
    troca de eixo.
    """
    pts = [(Q0, 0.0)]
    pts += [(Q0 + (Q1 - Q0) * k / 60.0, mwtp_q(Q0 + (Q1 - Q0) * k / 60.0, u))
            for k in range(61)]
    pts.append((Q1, 0.0))
    p.area(pts, cor, opac)


def area_q():
    t, p = moldura("Duas curvas, e nenhuma delas observável",
                   LARG_PX, ALT_PX, (AQ_MIN, AQ_MAX), (0, AQ_Y_MAX),
                   "q", "R$ por unidade de q")

    # Vermelho e a regua u0 e azul e a regua u1, exatamente como em
    # 11-area-vc e 11-area-ve. O roxo de q fica de fora de proposito: o
    # assunto desta figura e QUAL curva de indiferenca serve de regua, que e o
    # mesmo assunto das tres anteriores, e a rima visual vale mais.
    _area_q(p, U1, COR_DANO, 0.16)
    _area_q(p, U0, COR_CMG, 0.30)

    p.reta(Q0, 0, Q0, mwtp_q(Q0, U1), cor=COR_GUIA, larg=1.1, tracejado="4 3")
    p.reta(Q1, 0, Q1, mwtp_q(Q1, U1), cor=COR_GUIA, larg=1.1, tracejado="4 3")

    _curva_q(p, U1, COR_DANO)
    _curva_q(p, U0, COR_CMG)

    # Os dois rotulos de curva ficam no MESMO q, a esquerda, onde as duas
    # curvas estao a 80 unidades uma da outra. Postos a direita, onde a
    # hiperbole ja achatou, eles caiam a 25px um do outro e os halos se comiam.
    p.texto(1.12, mwtp_q(1.12, U1) + 12, "MWTP(q, u¹)", cor=COR_DANO,
            negrito=True)
    p.texto(1.12, mwtp_q(1.12, U0) + 12, "MWTP(q, u⁰)", cor=COR_CMG,
            negrito=True)

    p.marca_x(Q0, "q⁰ = 1")
    p.marca_x(Q1, "q¹ = 2")
    p.marca_y(mwtp_q(Q0, U0), "100")
    p.marca_y(mwtp_q(Q0, U1), "200")

    p.texto(1.55, 20, "VC = 50", cor=COR_CMG, negrito=True, italico=False,
            ancora="middle")
    # A 1,85 e 44 o rotulo encostava na propria curva azul, que passa em 58
    # ali. Em 1,7 as duas curvas estao a 35 unidades uma da outra e ele cabe
    # no meio, com folga parecida dos dois lados.
    p.texto(1.7, 50, "VE = 100", cor=COR_DANO, negrito=True, italico=False,
            ancora="middle")

    rodape(t, LARG_PX, ALT_PX,
           "a integral agora é em q, então a área é SOB a curva, e não à"
           " esquerda dela")
    t.salvar("11-area-q.svg",
             "As duas curvas de disposição marginal a pagar por q")


# ===========================================================================
# Bloco 2 - complementaridade fraca e os precos de esgotamento
# ===========================================================================

P_VIAGEM = 20.0
CHOKE_0, CHOKE_1 = 60.0, 100.0
dem_suja = lambda pp: max(0.0, (CHOKE_0 - pp) / 10.0)
dem_limpa = lambda pp: max(0.0, (CHOKE_1 - pp) / 10.0)
AREA_SUJA = (CHOKE_0 - P_VIAGEM) * dem_suja(P_VIAGEM) / 2      # 80
AREA_LIMPA = (CHOKE_1 - P_VIAGEM) * dem_limpa(P_VIAGEM) / 2    # 320

LARG_CH, ALT_CH = 700, 340
X_MAX_CH, P_MAX_CH = 10.6, 114.0


def choke(nome, etapa):
    """etapa 1: so a praia suja. etapa 2: as duas, e a diferenca."""
    titulos = {
        1: "Praia suja: acima de R$ 60 ninguém viaja",
        2: "Praia limpa: o preço de esgotamento sobe, e a área junto",
    }
    t, p = moldura(titulos[etapa], LARG_CH, ALT_CH, (0, X_MAX_CH),
                   (0, P_MAX_CH), "x", "p (R$ por viagem)")

    if etapa == 2:
        p.area([(0, P_VIAGEM), (dem_limpa(P_VIAGEM), P_VIAGEM), (0, CHOKE_1)],
               COR_Q, 0.22)
    p.area([(0, P_VIAGEM), (dem_suja(P_VIAGEM), P_VIAGEM), (0, CHOKE_0)],
           COR_Q_CLARO, 0.60)

    if etapa == 2:
        p.reta(0, CHOKE_1, dem_limpa(0), 0, cor=COR_Q, larg=2.8)
        p.texto(dem_limpa(38) + 0.25, 40, "x(p, q¹)", cor=COR_Q, negrito=True)
        p.texto(0.3, CHOKE_1 - 8, "esgotamento com q¹", cor=COR_Q,
                negrito=True)
    p.reta(0, CHOKE_0, dem_suja(0), 0, cor=COR_Q_CLARO, larg=2.8)
    p.texto(dem_suja(34) + 0.25, 36, "x(p, q⁰)", cor=COR_Q_CLARO,
            negrito=True)
    # "p-barra" com macron combinante nao sobrevive a toda fonte, e um rotulo
    # que some sem erro nenhum e o pior tipo de rotulo. O numero esta no eixo;
    # aqui vai a palavra.
    p.texto(0.3, CHOKE_0 - 8, "esgotamento com q⁰", cor=COR_Q_CLARO,
            negrito=True)

    p.reta(0, P_VIAGEM, X_MAX_CH, P_VIAGEM, cor=COR_GUIA, larg=1.2,
           tracejado="4 3")
    p.marca_y(P_VIAGEM, "20")
    p.marca_y(CHOKE_0, "60")
    p.reta(dem_suja(P_VIAGEM), 0, dem_suja(P_VIAGEM), P_VIAGEM,
           cor=COR_GUIA, larg=1.1, tracejado="4 3")
    p.marca_x(dem_suja(P_VIAGEM), "4", cor=COR_Q_CLARO)

    if etapa == 1:
        p.texto(1.1, 34, "80", cor=COR_Q, negrito=True, italico=False, tam=19)
        rod = ("com a praia suja são 4 viagens, e o excedente é"
               " (60 − 20) × 4 ÷ 2 = R$ 80 por ano")
    else:
        p.marca_y(CHOKE_1, "100")
        p.reta(dem_limpa(P_VIAGEM), 0, dem_limpa(P_VIAGEM), P_VIAGEM,
               cor=COR_GUIA, larg=1.1, tracejado="4 3")
        p.marca_x(dem_limpa(P_VIAGEM), "8", cor=COR_Q)
        p.texto(1.1, 32, "80", cor=COR_Q, negrito=True, italico=False, tam=17)
        p.texto(4.1, 58, "320 ao todo", cor=COR_Q, negrito=True,
                italico=False, tam=18)
        rod = ("A = 320 − 80 = R$ 240 por pessoa por ano é a disposição a"
               " pagar pela despoluição")
    rodape(t, LARG_CH, ALT_CH, rod)
    t.salvar(nome, titulos[etapa])


def nao_uso():
    """O que os dois triangulos NAO enxergam.

    O `.pptx` faz essa discussao so em algebra, no slide marcado LOUSA: a
    identidade A = VC + {E[p-barra(q1), u0, q1] - E[p-barra(q0), u0, q0]}. O
    colchete e zero exatamente quando o bem ambiental nao vale nada para quem
    nao viaja. Aqui ele vira uma barra, que e uma coisa que se aponta.
    """
    larg, alt = 640, 330
    titulo = "Complementaridade fraca: o que a viagem não mede"
    t, p = moldura(titulo, larg, alt, (0, 3.6), (0, 420.0), "",
                   "R$ por pessoa por ano")

    def barra(xc, base, topo, cor, opac, rotulo, cor_rot):
        p.area([(xc - 0.34, base), (xc + 0.34, base), (xc + 0.34, topo),
                (xc - 0.34, topo)], cor, opac)
        p.texto(xc, (base + topo) / 2 + 6, rotulo, cor=cor_rot, negrito=True,
                italico=False, ancora="middle", tam=18)

    barra(0.8, 0, 240, COR_Q, 0.45, "240", COR_Q)
    barra(2.0, 0, 240, COR_Q, 0.45, "240", COR_Q)
    barra(2.0, 240, 340, COR_APAGADA, 0.95, "100", COR_DESTAQUE)

    p.marca_x(0.8, "o que A mede")
    p.marca_x(2.0, "o que VC vale")
    p.marca_y(240, "240")
    p.marca_y(340, "340")
    p.reta(0, 240, 3.6, 240, cor=COR_GUIA, larg=1.1, tracejado="4 3")

    p.texto(2.45, 302, "valor que não", cor=COR_DESTAQUE, italico=False)
    p.texto(2.45, 282, "passa pela viagem", cor=COR_DESTAQUE, italico=False)

    rodape(t, larg, alt,
           "se quem nunca viaja também se importa, A é um piso de VC, e não VC")
    t.salvar("11-nao-uso.svg", titulo)


# ===========================================================================
# Bloco 3 - bens substitutos: duas tecnologias, os mesmos dois pontos
# ===========================================================================

P_PRIV = 5.0
H_SOMA = 10.0     # f(x, q) = x + q
H_PROD = 21.0     # f(x, q) = x q
Q_ANTES, Q_DEPOIS = 3.0, 7.0

x_soma = lambda q: H_SOMA - q
x_prod = lambda q: H_PROD / q
mwtp_prod = lambda q: P_PRIV * H_PROD / (q * q)

LARG_2P, ALT_2P = 356, 336
Q_MAX = 10.6


def _dois_paineis(titulo_esq, titulo_dir, ylim, rot_y):
    t = Tela(2 * LARG_2P + FOLGA, ALT_2P + ALTURA_RODAPE)
    ps = []
    for k, tit in enumerate((titulo_esq, titulo_dir)):
        p = Painel(t, k * LARG_2P, LARG_2P, (0, Q_MAX), ylim, ALT_2P)
        p.titulo(tit)
        p.eixos("q", rot_y)
        ps.append(p)
    return t, ps


def isoquantas():
    """As duas isoquantas passam pelos MESMOS dois pontos, e e disso que a
    figura vive: o que muda entre os paineis e so a inclinacao, que e o
    f_q/f_x da formula da MWTP."""
    t, (pe, pd) = _dois_paineis("Substitutos perfeitos: f = x + q",
                                "Substitutos imperfeitos: f = x · q",
                                (0, 10.6), "x (garrafas por semana)")

    pe.curva(x_soma, 0, 10.5, cor=COR_PROD, larg=2.8)
    pe.texto(9.9, 3.2, "x = 10 − q", cor=COR_PROD, negrito=True,
             ancora="end")
    pd.curva(x_prod, H_PROD / 10.5, 10.5, cor=COR_Q, larg=2.8)
    pd.texto(10.2, x_prod(10.2) + 1.9, "x = 21 / q", cor=COR_Q,
             negrito=True, ancora="end")

    for p, f in ((pe, x_soma), (pd, x_prod)):
        for q in (Q_ANTES, Q_DEPOIS):
            p.guia(q, f(q), cor=COR_GUIA)
            p.ponto(q, f(q), cor=COR_DESTAQUE, r=4.2)
            p.marca_x(q, fmt(q, 0))
            p.marca_y(f(q), fmt(f(q), 0))

    # A tangente so entra no painel da direita. No da esquerda ela coincide com
    # a propria reta e viraria ruido: o que ha para dizer la e que a inclinacao
    # nao muda, e isso e uma frase, nao um traco.
    for q in (Q_ANTES, Q_DEPOIS):
        incl = -H_PROD / (q * q)
        dq = 1.35
        pd.reta(q - dq, x_prod(q) - incl * dq, q + dq,
                x_prod(q) + incl * dq, cor=COR_CMG, larg=1.8, tracejado="6 4")
    pd.texto(4.8, 8.7, "inclinação 7/3", cor=COR_CMG, negrito=True)
    pd.texto(8.5, 1.4, "3/7", cor=COR_CMG, negrito=True)
    pe.texto(5.3, 7.6, "inclinação −1 em", cor=COR_CMG, negrito=True,
             ancora="middle")
    pe.texto(5.3, 6.5, "todo ponto", cor=COR_CMG, negrito=True,
             ancora="middle")

    rodape(t, 2 * LARG_2P, ALT_2P,
           "as duas tecnologias passam pelos mesmos pontos e poupam os mesmos"
           " R$ 20: o que muda é a inclinação")
    t.salvar("11-substitutos.svg", "Duas tecnologias, os mesmos dois pontos")


def mwtp():
    """A disposicao MARGINAL a pagar. As duas areas valem 20, e e isso que
    separa o total da margem."""
    t, (pe, pd) = _dois_paineis("f = x + q: MWTP é o próprio preço",
                                "f = x · q: MWTP cai com a qualidade",
                                (0, 13.6), "R$ por ponto de q")

    pe.area([(Q_ANTES, 0), (Q_DEPOIS, 0), (Q_DEPOIS, P_PRIV),
             (Q_ANTES, P_PRIV)], COR_PROD, 0.24)
    pe.reta(0, P_PRIV, 10.5, P_PRIV, cor=COR_PROD, larg=2.8)
    pe.texto(10.4, P_PRIV + 1.0, "p = 5", cor=COR_PROD, negrito=True,
             ancora="end")
    pe.marca_y(P_PRIV, "5")
    pe.texto(5.0, 2.2, "área = 20", cor=COR_PROD, negrito=True,
             italico=False, ancora="middle")

    pts = [(Q_ANTES, 0)]
    pts += [(Q_ANTES + (Q_DEPOIS - Q_ANTES) * k / 60.0,
             mwtp_prod(Q_ANTES + (Q_DEPOIS - Q_ANTES) * k / 60.0))
            for k in range(61)]
    pts.append((Q_DEPOIS, 0))
    pd.area(pts, COR_Q, 0.24)
    pd.curva(mwtp_prod, math.sqrt(P_PRIV * H_PROD / 13.4), 10.5, cor=COR_Q,
             larg=2.8)
    pd.texto(10.4, mwtp_prod(8.6) + 1.2, "p · H / q²", cor=COR_Q,
             negrito=True, ancora="end")
    pd.marca_y(mwtp_prod(Q_ANTES), "11,7")
    pd.marca_y(mwtp_prod(Q_DEPOIS), "2,1")
    pd.texto(4.6, 2.2, "área = 20", cor=COR_Q, negrito=True, italico=False,
             ancora="middle")

    for p in (pe, pd):
        for q in (Q_ANTES, Q_DEPOIS):
            p.reta(q, 0, q, 12.8, cor=COR_GUIA, larg=1.1, tracejado="4 3")
            p.marca_x(q, fmt(q, 0))

    rodape(t, 2 * LARG_2P, ALT_2P,
           "a integral da disposição marginal entre 3 e 7 dá R$ 20 nos dois"
           " casos: total e margem são coisas diferentes")
    t.salvar("11-mwtp.svg", "Disposição marginal a pagar")


# ===========================================================================
# O exercicio - a versao discreta dos precos de esgotamento
# ===========================================================================

VAL_SUJA = [40, 30, 20, 10]
VAL_LIMPA = [80, 70, 60, 50, 40, 30, 20, 10]
P_EX = 20


def exercicio():
    larg, alt = 740, 340
    titulo = "Solução do exercício: duas escadas e uma linha"
    t, p = moldura(titulo, larg, alt, (0, 9.0), (0, 92.0), "x",
                   "R$ por viagem")

    # Retangulo por retangulo, e nao um triangulo: o aluno confere a soma
    # contando 60 + 50 + 40 + 30 + 20 + 10 na tela.
    for k, v in enumerate(VAL_LIMPA):
        if v >= P_EX:
            p.area([(k, P_EX), (k + 1, P_EX), (k + 1, v), (k, v)], COR_Q,
                   0.20)
    for k, v in enumerate(VAL_SUJA):
        if v >= P_EX:
            p.area([(k, P_EX), (k + 1, P_EX), (k + 1, v), (k, v)],
                   COR_Q_CLARO, 0.75)

    escada(p, VAL_LIMPA, COR_Q, larg=2.6)
    escada(p, VAL_SUJA, COR_Q_CLARO, larg=2.6)
    p.reta(0, P_EX, 9.0, P_EX, cor=COR_CMG, larg=2.2)

    p.texto(2.1, 63, "praia limpa", cor=COR_Q, negrito=True)
    p.texto(3.1, 12, "praia suja", cor=COR_Q_CLARO, negrito=True)
    p.texto(8.9, 24, "custo da viagem = 20", cor=COR_CMG, negrito=True,
            ancora="end", italico=False)

    p.marca_y(80, "80")
    p.marca_y(40, "40")
    p.marca_y(P_EX, "20")
    for k in range(1, 9):
        p.marca_x(k - 0.5, str(k))

    p.texto(3.5, 36, "210 ao todo", cor=COR_Q, negrito=True, italico=False,
            ancora="middle", tam=17)
    p.texto(0.5, 29, "30", cor=COR_DESTAQUE, negrito=True, italico=False,
            ancora="middle", tam=15)

    rodape(t, larg, alt,
           "A = 210 − 30 = R$ 180 por pessoa por ano, e os preços de"
           " esgotamento são os degraus mais altos: 40 e 80")
    t.salvar("11-exercicio.svg", titulo)


def main():
    print("aula 11 - valoracao de bens ambientais")
    variacao("11-vc.svg", "VC")
    variacao("11-ve.svg", "VE")
    areas("11-area-vc.svg", "VC")
    areas("11-area-ve.svg", "VE")
    areas("11-area-ec.svg", "EC")
    area_q()
    choke("11-choke-1.svg", 1)
    choke("11-choke-2.svg", 2)
    nao_uso()
    isoquantas()
    mwtp()
    exercicio()
    print()
    print("  conferencia da calibracao:")
    print("    u0 = {}   u1 = {}".format(fmt(U0), fmt(U1)))
    print("    VC = {}   EC = {}   VE = {}".format(fmt(VC), fmt(EC, 2),
                                                   fmt(VE)))
    print("    A  = {} - {} = {}".format(fmt(AREA_LIMPA), fmt(AREA_SUJA),
                                         fmt(AREA_LIMPA - AREA_SUJA)))
    exc_l = sum(v - P_EX for v in VAL_LIMPA if v >= P_EX)
    exc_s = sum(v - P_EX for v in VAL_SUJA if v >= P_EX)
    print("    exercicio: {} - {} = {}".format(exc_l, exc_s, exc_l - exc_s))
    print("    substitutos: economia {} (soma) e {} (produto)".format(
        fmt(P_PRIV * (x_soma(Q_ANTES) - x_soma(Q_DEPOIS))),
        fmt(P_PRIV * (x_prod(Q_ANTES) - x_prod(Q_DEPOIS)))))
    print("    integral da MWTP imperfeita entre 3 e 7: {}".format(
        fmt(P_PRIV * H_PROD * (1 / Q_ANTES - 1 / Q_DEPOIS))))
    print()
    print("  a tabela de participacao no orcamento (slide do excedente):")
    print("    alfa      VC       EC       VE    erro do EC sobre VC")
    for alfa in (0.5, 0.05):
        # Com Cobb-Douglas de expoente alfa as tres medidas tem forma fechada:
        #   VC = y (1 - p0^-alfa)   VE = y (p0^alfa - 1)   EC = alfa y ln p0
        # (com p1 = 1). O parametro alfa E a participacao do bem no orcamento,
        # entao a tabela do slide e literalmente uma leitura desta formula.
        vc = RENDA * (1 - P0 ** -alfa)
        ve = RENDA * (P0 ** alfa - 1)
        ec = alfa * RENDA * math.log(P0 / P1)
        print("    {:>4}  {:>7}  {:>7}  {:>7}      {:>5}%".format(
            fmt(alfa * 100, 0) + "%", fmt(vc, 2), fmt(ec, 2), fmt(ve, 2),
            fmt(100 * (ec - vc) / vc, 1)))


if __name__ == "__main__":
    main()
