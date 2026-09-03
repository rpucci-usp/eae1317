#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Gera os diagramas da aula 08 (Informacao Assimetrica) a partir das equacoes.

Motivo de existir: no `.pptx` esta aula NAO TEM UMA FIGURA. Os dez pontos em
que o argumento vira geometria estao marcados com "(LOUSA)", ou seja, eram
desenhados a mao no quadro. Sem eles o deck e uma sequencia de integrais sem
desenho nenhum, e a aula inteira depende de o aluno reconstruir o triangulo de
perda de cabeca.

Como figuras05/06/07svg.py, este script IMPORTA Painel, Tela e as cores de
figuras04svg.py.

O QUE MUDA EM RELACAO AS AULAS 04 A 07
--------------------------------------
Ali as figuras eram DUAS FIRMAS lado a lado, porque o assunto era como o custo
de abatimento se reparte entre elas. Aqui o assunto e outro: o regulador erra
uma das duas curvas AGREGADAS, e a pergunta e quanto isso custa. O `.pptx`
trabalha o tempo todo com D'(E) e -C'(E), sem indice de firma, e as figuras
seguem esse recorte: painel unico, curvas agregadas.

A economia e ancorada na das aulas anteriores pelo ponto que importa:

    -C'(E) = (200 - E)/3        custo marginal de abatimento AGREGADO
    D'(E)  = 0,2 E              dano marginal
    =>  E* = 125,  preco = 25   os mesmos numeros das aulas 04, 06 e 07

(Nas aulas 04 a 07 esse agregado saia da soma horizontal de CMg_1 = 100 - e_1 e
CMg_2 = 50 - 0,5 e_2, valida enquanto as duas firmas abatem. Aqui ele e tomado
como primitivo, que e como o `.pptx` desta aula o trata.)

OS DOIS ERROS, E POR QUE OS NUMEROS SAO REDONDOS
------------------------------------------------
1. Dano subestimado. O regulador acha que as primeiras 40 t nao causam dano:

       D~'(E) = 0,2 (E - 40)   =>  E~ = 140,  preco 20,  perda 60

   Imposto e leilao produzem O MESMO ponto, entao a perda nao depende do
   instrumento. E o resultado do primeiro bloco da aula.

2. Custo de abatimento subestimado, por um deslocamento vertical de 80/3:

       -C~'(E) = (120 - E)/3

   Meta do regulador: E~ = 75, aliquota tau~ = 15.
       quantidade (L = 75):  a emissao FICA em 75          -> perda b = 666,7
       preco (tau~ = 15):    as firmas vao ate 155         -> perda c = 240

   Agora o instrumento importa, que e o resultado do segundo bloco.

A RAZAO ENTRE AS DUAS PERDAS
----------------------------
Com curvas lineares, chamando `a` a inclinacao de -C' e `eta` a de D', sai

    b = Delta^2 / (2 (a + eta))        c = b (eta / a)^2

ou seja c < b exatamente quando eta < a. E o Teorema de Weitzman em uma linha, e
e o que a figura de dois paineis desenha: mesma -C', mesma -C~', mesmo E*, so a
inclinacao do dano muda. Os `assert` abaixo conferem as duas formulas contra as
areas calculadas ponto a ponto.

O exercicio da aula reusa as usinas A e B das aulas 04, 06 e 07 pela sexta vez,
e e o canto eta = 0 do teorema: com dano marginal constante o imposto acerta em
cheio e a quantidade erra sozinha.

Depende so da biblioteca padrao, como os outros scripts desta pasta.

    py scripts/figuras08svg.py

Escreve em aulas/_assets/figuras/.
"""

from figuras04svg import (Painel, Tela, COR_CMG, COR_DANO, COR_EIXO,
                          COR_GUIA, COR_DESTAQUE, FONTE, FONTE_LEGENDA)

# --- as curvas agregadas ----------------------------------------------------
E_LF = 200.0                     # emissao agregada sem regulacao
A_MAC = 1.0 / 3                  # inclinacao (em modulo) de -C'(E)
ETA = 0.2                        # inclinacao de D'(E)

mac = lambda E: (E_LF - E) * A_MAC
dano_mg = lambda E: ETA * E

E_OTIMO = 125.0
PRECO_OTIMO = 25.0
assert abs(mac(E_OTIMO) - dano_mg(E_OTIMO)) < 1e-9, "E* deixou de ser 125"
assert abs(dano_mg(E_OTIMO) - PRECO_OTIMO) < 1e-9, "o preco no otimo mudou"

# --- erro 1: o regulador subestima o dano -----------------------------------
# Um deslocamento (e nao uma rotacao) porque tem historia: o regulador acha que
# as primeiras 40 t sao absorvidas pelo rio sem dano nenhum. D~' < D' para todo
# E > 0, que e a hipotese do .pptx, e o cruzamento cai num numero redondo.
LIMIAR_DANO = 40.0
dano_mg_est = lambda E: max(0.0, ETA * (E - LIMIAR_DANO))

E_DANO = 140.0                   # onde -C' cruza D~'
PRECO_DANO = 20.0
assert abs(mac(E_DANO) - dano_mg_est(E_DANO)) < 1e-9, "E~ do bloco de dano mudou"
assert abs(mac(E_DANO) - PRECO_DANO) < 1e-9, "o preco induzido mudou"
assert E_DANO > E_OTIMO, "subestimar o dano deveria permitir MAIS poluicao"

# A perda e o triangulo entre D' VERDADEIRO e -C', de E* ate E~.
WL_DANO = 0.5 * (E_DANO - E_OTIMO) * (dano_mg(E_DANO) - mac(E_DANO))
assert abs(WL_DANO - 60.0) < 1e-9, "a perda do bloco de dano mudou"

# --- erro 2: o regulador subestima o custo de abatimento --------------------
DELTA = 80.0 / 3                 # o deslocamento vertical do erro
mac_est = lambda E: mac(E) - DELTA

E_QTD = 75.0                     # a meta do regulador, e o L que ele emite
TAU_EST = 15.0                   # a aliquota que ele calcula a partir dela
E_PRECO = 155.0                  # onde as firmas param, na curva VERDADEIRA

assert abs(mac_est(E_QTD) - dano_mg(E_QTD)) < 1e-9, "E~ do bloco de custo mudou"
assert abs(dano_mg(E_QTD) - TAU_EST) < 1e-9, "tau~ mudou"
assert abs(mac(E_PRECO) - TAU_EST) < 1e-9, "E(tau) mudou"
assert E_QTD < E_OTIMO < E_PRECO, \
    "subestimar o custo deveria apertar a meta e afrouxar o imposto"

B_QTD = 0.5 * (E_OTIMO - E_QTD) * (mac(E_QTD) - dano_mg(E_QTD))
C_PRECO = 0.5 * (E_PRECO - E_OTIMO) * (dano_mg(E_PRECO) - mac(E_PRECO))
assert abs(B_QTD - 2000.0 / 3) < 1e-9, "a perda b mudou"
assert abs(C_PRECO - 240.0) < 1e-9, "a perda c mudou"


def perdas(eta):
    """As duas perdas quando o dano marginal gira em torno de (E*, preco*).

    Gira em torno do otimo, e nao em torno da origem, para que a comparacao
    isole UMA coisa: a inclinacao. Com -C', -C~' e E* fixos nos dois paineis, o
    que muda de um para o outro e so eta.
    """
    dano_eta = lambda E: PRECO_OTIMO + eta * (E - E_OTIMO)
    # -C~'(E) = D'(E)  =>  a meta do regulador
    e_meta = (mac_est(0.0) - dano_eta(0.0)) / (eta + A_MAC)
    tau = dano_eta(e_meta)
    e_preco = E_LF - tau / A_MAC
    b = 0.5 * (E_OTIMO - e_meta) * (mac(e_meta) - dano_eta(e_meta))
    c = 0.5 * (e_preco - E_OTIMO) * (dano_eta(e_preco) - mac(e_preco))
    return dano_eta, e_meta, tau, e_preco, b, c


ETA_PLANO = 0.2
ETA_INGREME = 0.5

# A formula fechada, conferida contra as areas calculadas acima. Se ela vale, a
# frase "c < b exatamente quando eta < a" pode ir para o slide.
for _eta in (ETA_PLANO, 1.0 / 3, ETA_INGREME):
    _, _em, _, _ep, _b, _c = perdas(_eta)
    assert abs(_b - DELTA ** 2 / (2 * (A_MAC + _eta))) < 1e-6, \
        "a formula fechada de b nao bate com a area"
    assert abs(_c - _b * (_eta / A_MAC) ** 2) < 1e-6, \
        "a razao c/b deixou de ser (eta/a)^2"

# O painel plano tem que reproduzir o bloco de custo, e o ingreme tem que
# inverter o resultado — senao os dois paineis nao dizem coisas diferentes.
_, _EM_P, _TAU_P, _EP_P, _B_P, _C_P = perdas(ETA_PLANO)
_, _EM_I, _TAU_I, _EP_I, _B_I, _C_I = perdas(ETA_INGREME)
assert (round(_EM_P), round(_EP_P)) == (75, 155), "o painel plano saiu do bloco de custo"
assert (round(_EM_I), round(_EP_I)) == (93, 173), "o painel ingreme mudou"
assert _C_P < _B_P and _C_I > _B_I, "os dois paineis deixaram de se contradizer"
# As duas metades da proposicao do .pptx, medidas: com dano mais inclinado a
# meta erra menos e o imposto erra mais.
assert abs(E_OTIMO - _EM_I) < abs(E_OTIMO - _EM_P), "|E* - E~| deveria diminuir"
assert abs(_EP_I - E_OTIMO) > abs(_EP_P - E_OTIMO), "|E* - E(tau)| deveria aumentar"

# --- o exercicio: as mesmas usinas das aulas 04, 06 e 07 --------------------
BLOCOS_A = [10, 20, 30, 40, 50]
BLOCOS_B = [20, 40, 60, 80, 100]
DANO_BLOCO = 45.0                # dano de cada bloco de 10 t emitido
DANO_DEGRAU = 300.0              # dano de cada bloco emitido acima de 30 t
BLOCOS_LIMIAR = 3                # onde o degrau comeca

# A demanda por emissao, em blocos: emitir o e-esimo bloco poupa o custo do
# bloco mais caro que ainda estaria sendo cortado.
VERDADE = sorted(BLOCOS_A + BLOCOS_B, reverse=True)
CRENCA = sorted(BLOCOS_A + BLOCOS_A, reverse=True)   # "as duas sao como a A"

assert VERDADE[:4] == [100, 80, 60, 50] and VERDADE[4] == 40, \
    "a escada verdadeira mudou"
assert CRENCA[:2] == [50, 50] and CRENCA[2] == 40, "a escada suposta mudou"


def social(e, degrau=False):
    """Custo social com `e` blocos emitidos: abatimento + dano."""
    abat = sum(VERDADE[e:])
    if degrau:
        dano = DANO_BLOCO * min(e, BLOCOS_LIMIAR) \
            + DANO_DEGRAU * max(0, e - BLOCOS_LIMIAR)
    else:
        dano = DANO_BLOCO * e
    return abat + dano


E_EFIC = min(range(11), key=lambda e: social(e))
E_EFIC_DEG = min(range(11), key=lambda e: social(e, degrau=True))
E_META = sum(1 for v in CRENCA if v > DANO_BLOCO)     # o que o regulador mira
E_IMPOSTO = sum(1 for v in VERDADE if v > DANO_BLOCO)  # o que as firmas fazem

assert (E_EFIC, E_META, E_IMPOSTO) == (4, 2, 4), "o exercicio mudou de resposta"
assert E_EFIC_DEG == 3, "o eficiente sob o degrau mudou"
# A ponte com as aulas 04, 06 e 07: 4 blocos emitidos sao as 40 t eficientes, e
# os 6 blocos cortados custam os mesmos 160 mil de la.
assert sum(VERDADE[E_EFIC:]) == 160, "o corte eficiente deixou de custar 160"

PERDA_QTD = social(E_META) - social(E_EFIC)                          # 20
PERDA_IMP = social(E_IMPOSTO) - social(E_EFIC)                       # 0
PERDA_QTD_DEG = social(E_META, True) - social(E_EFIC_DEG, True)      # 15
PERDA_IMP_DEG = social(E_IMPOSTO, True) - social(E_EFIC_DEG, True)   # 250
assert (PERDA_QTD, PERDA_IMP) == (20, 0), "as perdas do dano constante mudaram"
assert (PERDA_QTD_DEG, PERDA_IMP_DEG) == (15, 250), "as perdas do degrau mudaram"

# --- geometria --------------------------------------------------------------
LARG_AG = 760                    # painel unico: cabe mais largo que os pares
ALT_AG = 330
X_MAX = 215
Y_MAX = 72                       # -C'(0) = 66,7 precisa caber
FOLGA_AG = 20                    # o rotulo "E" e escrito fora da largura

LARG_W = 460                     # os dois paineis da figura de Weitzman
ALT_W = 336
Y_MAX_W = 58                     # D' ingreme chega a 49 em E(tau)

LARG_EX = 760
ALT_EX = 344
Y_MAX_EX = 116
# O rotulo do eixo horizontal aqui e "blocos emitidos": ~146px a 19px, contra
# os ~14px do "E" das outras figuras desta aula. O Painel.eixos() o escreve 16px
# depois do fim do eixo com ancora "start", entao sem folga propria ele sai
# cortado pela borda do viewBox — a mesma armadilha que o "permissoes" da aula
# 07 ja tinha registrado, so que com uma palavra ainda mais larga.
FOLGA_EX = 150


def fmt(v, casas=1):
    """Numero em portugues, sem casa decimal sobrando.

    Uma casa por padrao (e nao quatro, como na aula 07): as perdas desta aula
    sao dizimas — b = 2000/3 — e "666,6667" no rodape de um slide e ruido.
    """
    inteiro, _, dec = ("{:." + str(casas) + "f}").format(v).partition(".")
    dec = dec.rstrip("0")
    milhar = "{:,}".format(int(inteiro)).replace(",", ".")
    return milhar + ("," + dec if dec else "")


def painel_agregado(titulo):
    """A moldura comum das seis figuras de painel unico."""
    t = Tela(LARG_AG + FOLGA_AG, ALT_AG + 46)
    p = Painel(t, 0, LARG_AG, (0, X_MAX), (0, Y_MAX), ALT_AG)
    p.titulo(titulo)
    p.eixos("E", "R$ por tonelada")
    return t, p


def rodape(t, texto, cor=COR_DESTAQUE, larg=None, alt=None):
    t.texto((larg or LARG_AG) / 2, (alt or ALT_AG) + 32, texto,
            ancora="middle", tam=FONTE_LEGENDA, cor=cor, negrito=True)


def reta_clip(p, f, cor, larg=2.2, tracejado=None, x_ini=None, x_fim=None):
    """Desenha a reta f so no trecho em que ela cabe DENTRO do painel.

    Sem isso a reta sai pelo topo e pelo pe do enquadramento: -C'(0) = 66,7 e o
    dano marginal ingreme da figura de Weitzman passa de 70 na ponta direita,
    enquanto os paineis vao ate 72 e 58. Uma reta que atravessa a moldura nao
    da erro nenhum e simplesmente polui o desenho.
    """
    x0 = p.x0 if x_ini is None else x_ini
    x1 = p.x1 if x_fim is None else x_fim
    # A reta e monotona, entao basta resolver f(x) = limite nas duas pontas.
    passo = (x1 - x0) / 400.0
    dentro = [x0 + k * passo for k in range(401)]
    dentro = [x for x in dentro if -1e-9 <= f(x) <= p.y1 + 1e-9]
    if len(dentro) < 2:
        return
    a, b = dentro[0], dentro[-1]
    p.reta(a, f(a), b, f(b), cor=cor, larg=larg, tracejado=tracejado)


def curva_mac(p, f, cor=COR_CMG, tracejado=None, larg=2.2):
    """-C'(E), do topo do painel ate onde ela morre no eixo."""
    reta_clip(p, f, cor, larg=larg, tracejado=tracejado)


# ---------------------------------------------------------------------------
# Bloco 1 — o regulador subestima o dano
# ---------------------------------------------------------------------------

def dano_1():
    t, p = painel_agregado("O regulador subestima o dano marginal")
    curva_mac(p, mac)
    p.reta(0, 0, X_MAX, dano_mg(X_MAX), cor=COR_DANO)
    p.reta(LIMIAR_DANO, 0, X_MAX, dano_mg_est(X_MAX), cor=COR_DANO,
           larg=2.0, tracejado="7 5")

    p.texto(X_MAX - 8, dano_mg(X_MAX) - 4, "D′(E)", cor=COR_DANO,
            negrito=True, ancora="end")
    p.texto(X_MAX - 8, dano_mg_est(X_MAX) - 4, "D̃′(E)", cor=COR_DANO,
            negrito=True, ancora="end")
    p.texto(20, mac(20) + 5, "−C′(E)", cor=COR_CMG, negrito=True)

    p.guia(E_OTIMO, PRECO_OTIMO)
    p.ponto(E_OTIMO, PRECO_OTIMO)
    p.marca_x(E_OTIMO, "E*", cor=COR_DESTAQUE)
    p.guia(E_DANO, PRECO_DANO, cor=COR_DANO)
    p.ponto(E_DANO, PRECO_DANO, cor=COR_DANO)
    p.marca_x(E_DANO, "Ẽ", cor=COR_DANO)

    rodape(t, "com o dano subestimado, a meta escorrega de E* = 125 para"
              " Ẽ = 140")
    return t


def dano_2():
    t, p = painel_agregado("A perda é medida com o dano verdadeiro")
    curva_mac(p, mac)
    p.reta(0, 0, X_MAX, dano_mg(X_MAX), cor=COR_DANO)
    p.reta(LIMIAR_DANO, 0, X_MAX, dano_mg_est(X_MAX), cor=COR_DANO,
           larg=2.0, tracejado="7 5")

    # O triangulo entre D' VERDADEIRO e -C', de E* ate E~. E o ponto do slide:
    # quem calcula a perda usa D', e nao a estimativa que produziu o erro.
    p.area([(E_OTIMO, PRECO_OTIMO), (E_DANO, dano_mg(E_DANO)),
            (E_DANO, mac(E_DANO))], COR_DESTAQUE, 0.72)
    # O triangulo desta figura e pequeno de propósito (a perda por errar o dano
    # e mesmo pequena perto das do bloco seguinte), entao o rotulo nao cabe
    # dentro dele: vai acima, com uma perna curta ligando os dois.
    p.reta(E_DANO - 6, 0.5 * (dano_mg(E_DANO) + mac(E_DANO)),
           E_DANO - 14, 0.62 * Y_MAX, cor=COR_DESTAQUE, larg=1.1)
    p.texto(E_DANO - 16, 0.62 * Y_MAX + 4, "WL = " + fmt(WL_DANO),
            cor=COR_DESTAQUE, negrito=True, italico=False, ancora="end")

    p.ponto(E_OTIMO, PRECO_OTIMO)
    p.marca_x(E_OTIMO, "E*", cor=COR_DESTAQUE)
    p.marca_x(E_DANO, "Ẽ", cor=COR_DANO)
    p.texto(X_MAX - 8, dano_mg(X_MAX) - 4, "D′(E)", cor=COR_DANO,
            negrito=True, ancora="end")
    p.texto(X_MAX - 8, dano_mg_est(X_MAX) - 4, "D̃′(E)", cor=COR_DANO,
            negrito=True, ancora="end")

    rodape(t, "cada tonelada entre E* e Ẽ custa mais em dano do que poupa em"
              " abatimento")
    return t


def dano_3():
    t, p = painel_agregado("Imposto e leilão caem no mesmo ponto")
    curva_mac(p, mac)
    p.reta(0, 0, X_MAX, dano_mg(X_MAX), cor=COR_DANO)
    p.reta(LIMIAR_DANO, 0, X_MAX, dano_mg_est(X_MAX), cor=COR_DANO,
           larg=2.0, tracejado="7 5")
    p.area([(E_OTIMO, PRECO_OTIMO), (E_DANO, dano_mg(E_DANO)),
            (E_DANO, mac(E_DANO))], COR_DESTAQUE, 0.35)

    # A aliquota e o preco do leilao sao o MESMO numero, e e por isso que os
    # dois instrumentos produzem a mesma alocacao ineficiente.
    p.reta(0, PRECO_DANO, E_DANO, PRECO_DANO, cor=COR_DESTAQUE, larg=1.8,
           tracejado="7 4")
    p.reta(E_DANO, 0, E_DANO, Y_MAX - 16, cor=COR_DESTAQUE, larg=1.8)
    p.marca_y(PRECO_DANO, "τ̃ = 20", cor=COR_DESTAQUE)
    p.texto(E_DANO + 5, Y_MAX - 20, "L = Ẽ = 140", cor=COR_DESTAQUE,
            negrito=True, italico=False)
    p.ponto(E_DANO, PRECO_DANO, cor=COR_DESTAQUE)
    p.marca_x(E_OTIMO, "E*", cor=COR_DESTAQUE)

    rodape(t, "a altura e a largura são o mesmo ponto: com dano errado, o"
              " instrumento não muda a perda")
    return t


# ---------------------------------------------------------------------------
# Bloco 2 — o regulador subestima o custo de abatimento
# ---------------------------------------------------------------------------

def moldura_custo(titulo):
    t, p = painel_agregado(titulo)
    curva_mac(p, mac)
    curva_mac(p, mac_est, tracejado="7 5", larg=2.0)
    p.reta(0, 0, X_MAX, dano_mg(X_MAX), cor=COR_DANO)
    p.texto(X_MAX - 8, dano_mg(X_MAX) - 4, "D′(E)", cor=COR_DANO,
            negrito=True, ancora="end")
    p.texto(14, mac(14) + 5, "−C′(E)", cor=COR_CMG, negrito=True)
    p.texto(14, mac_est(14) - 7, "−C̃′(E)", cor=COR_CMG, negrito=True)
    return t, p


def custo_1():
    t, p = moldura_custo("O regulador subestima o custo de abatimento")
    p.guia(E_OTIMO, PRECO_OTIMO)
    p.ponto(E_OTIMO, PRECO_OTIMO)
    p.marca_x(E_OTIMO, "E*", cor=COR_DESTAQUE)
    p.guia(E_QTD, TAU_EST, cor=COR_CMG)
    p.ponto(E_QTD, TAU_EST, cor=COR_CMG)
    p.marca_x(E_QTD, "Ẽ", cor=COR_CMG)

    rodape(t, "achando o abatimento mais barato do que é, o regulador mira"
              " Ẽ = 75 no lugar de 125")
    return t


def custo_quantidade():
    t, p = moldura_custo("Instrumento de quantidade: L = Ẽ")
    # Com L fixo em 75 a emissao FICA em 75, qualquer que seja o custo real: a
    # perda e a area inteira entre as duas curvas verdadeiras.
    p.area([(E_QTD, mac(E_QTD)), (E_OTIMO, PRECO_OTIMO),
            (E_QTD, dano_mg(E_QTD))], COR_DESTAQUE, 0.72)
    p.texto(E_QTD - 6, 0.5 * (mac(E_QTD) + dano_mg(E_QTD)), "b",
            cor=COR_DESTAQUE, negrito=True, ancora="end", tam=18)
    p.reta(E_QTD, 0, E_QTD, Y_MAX - 16, cor=COR_DESTAQUE, larg=2.0)
    p.texto(E_QTD + 5, Y_MAX - 20, "L = 75", cor=COR_DESTAQUE, negrito=True,
            italico=False)
    p.ponto(E_OTIMO, PRECO_OTIMO)
    p.marca_x(E_OTIMO, "E*", cor=COR_DESTAQUE)

    rodape(t, "a emissão para em 75 e abate-se demais: perda b = " + fmt(B_QTD))
    return t


def custo_preco():
    t, p = moldura_custo("Instrumento de preço: τ̃ = D′(Ẽ)")
    # Com a aliquota fixa em 15 as firmas respondem na curva VERDADEIRA, e
    # param em 155 — do outro lado do otimo.
    p.area([(E_OTIMO, PRECO_OTIMO), (E_PRECO, dano_mg(E_PRECO)),
            (E_PRECO, mac(E_PRECO))], COR_DESTAQUE, 0.72)
    p.texto(E_PRECO + 6, 0.5 * (dano_mg(E_PRECO) + mac(E_PRECO)), "c",
            cor=COR_DESTAQUE, negrito=True, tam=18)
    p.reta(0, TAU_EST, E_PRECO, TAU_EST, cor=COR_DESTAQUE, larg=1.8,
           tracejado="7 4")
    p.marca_y(TAU_EST, "τ̃ = 15", cor=COR_DESTAQUE)
    p.ponto(E_PRECO, TAU_EST, cor=COR_DESTAQUE)
    p.ponto(E_OTIMO, PRECO_OTIMO)
    p.marca_x(E_OTIMO, "E*", cor=COR_DESTAQUE)
    p.marca_x(E_PRECO, "E(τ̃)", cor=COR_DESTAQUE)

    rodape(t, "as firmas seguem a curva verdadeira até 155 e abate-se de menos:"
              " perda c = " + fmt(C_PRECO))
    return t


def custo_4():
    t, p = moldura_custo("As duas perdas no mesmo desenho")
    p.area([(E_QTD, mac(E_QTD)), (E_OTIMO, PRECO_OTIMO),
            (E_QTD, dano_mg(E_QTD))], COR_DESTAQUE, 0.72)
    p.area([(E_OTIMO, PRECO_OTIMO), (E_PRECO, dano_mg(E_PRECO)),
            (E_PRECO, mac(E_PRECO))], COR_DANO, 0.72)
    p.texto(E_QTD - 6, 0.5 * (mac(E_QTD) + dano_mg(E_QTD)), "b",
            cor=COR_DESTAQUE, negrito=True, ancora="end", tam=18)
    p.texto(E_PRECO + 6, 0.5 * (dano_mg(E_PRECO) + mac(E_PRECO)), "c",
            cor=COR_DANO, negrito=True, tam=18)
    p.ponto(E_OTIMO, PRECO_OTIMO)
    p.marca_x(E_QTD, "Ẽ", cor=COR_DESTAQUE)
    p.marca_x(E_OTIMO, "E*", cor=COR_DESTAQUE)
    p.marca_x(E_PRECO, "E(τ̃)", cor=COR_DANO)

    rodape(t, "b = " + fmt(B_QTD) + " contra c = " + fmt(C_PRECO)
              + ": com este dano, o imposto perde menos")
    return t


# ---------------------------------------------------------------------------
# Weitzman: mesma -C', mesma -C~', mesmo E*, so a inclinacao do dano muda
# ---------------------------------------------------------------------------

def weitzman():
    t = Tela(2 * LARG_W + FOLGA_AG, ALT_W + 46)
    dados = ((0, ETA_PLANO, "Dano marginal pouco inclinado"),
             (1, ETA_INGREME, "Dano marginal muito inclinado"))
    for i, eta, titulo in dados:
        p = Painel(t, i * LARG_W, LARG_W, (0, X_MAX), (0, Y_MAX_W), ALT_W)
        p.titulo(titulo)
        p.eixos("E", "R$ por t")
        d_eta, e_meta, tau, e_preco, b, c = perdas(eta)

        # -C' e a estimativa dela, iguais nos dois paineis
        reta_clip(p, mac, COR_CMG)
        reta_clip(p, mac_est, COR_CMG, larg=2.0, tracejado="7 5")
        # D'(E) gira em torno de (E*, 25), entao no painel ingreme ela e
        # negativa a esquerda e passa do topo a direita: os dois trechos ficam
        # de fora, e o rotulo do eixo continua dizendo qual e a grandeza.
        reta_clip(p, d_eta, COR_DANO)

        p.area([(e_meta, mac(e_meta)), (E_OTIMO, PRECO_OTIMO),
                (e_meta, d_eta(e_meta))], COR_DESTAQUE, 0.72)
        p.area([(E_OTIMO, PRECO_OTIMO), (e_preco, d_eta(e_preco)),
                (e_preco, mac(e_preco))], COR_DANO, 0.72)
        p.texto(e_meta - 6, 0.5 * (mac(e_meta) + d_eta(e_meta)),
                "b", cor=COR_DESTAQUE, negrito=True, ancora="end", tam=18)
        p.texto(e_preco + 6, 0.5 * (d_eta(e_preco) + mac(e_preco)),
                "c", cor=COR_DANO, negrito=True, tam=18)
        p.ponto(E_OTIMO, PRECO_OTIMO)
        p.marca_x(E_OTIMO, "E*", cor=COR_DESTAQUE)
        p.texto(0.5 * X_MAX, Y_MAX_W - 5,
                ("b = " + fmt(b) + "  >  c = " + fmt(c)) if c < b
                else ("c = " + fmt(c) + "  >  b = " + fmt(b)),
                cor=COR_EIXO, negrito=True, italico=False, ancora="middle",
                tam=FONTE)

    t.texto((2 * LARG_W + FOLGA_AG) / 2, ALT_W + 32,
            "mesmo custo, mesmo erro, mesmo E*: só a inclinação do dano muda",
            ancora="middle", tam=FONTE_LEGENDA, cor=COR_DESTAQUE, negrito=True)
    return t


# ---------------------------------------------------------------------------
# O exercicio: a versao discreta, com as usinas das aulas 04, 06 e 07
# ---------------------------------------------------------------------------

def escada(p, valores, cor, tracejado=None, larg=2.4):
    for k, v in enumerate(valores):
        p.reta(k, v, k + 1, v, cor=cor, larg=larg, tracejado=tracejado)
        if k + 1 < len(valores):
            p.reta(k + 1, v, k + 1, valores[k + 1], cor=cor, larg=1.2,
                   tracejado=tracejado)


def exercicio():
    """As duas escadas de disposicao a pagar por emitir, e o dano constante.

    A leitura que a figura precisa entregar: a linha do dano corta a escada
    VERDADEIRA no quarto degrau e a SUPOSTA no segundo. O imposto de 45 poe as
    firmas na escada verdadeira, entao acerta; o L de 2 as prende no ponto que
    saiu da escada errada.
    """
    t = Tela(LARG_EX + FOLGA_EX, ALT_EX + 46)
    p = Painel(t, 0, LARG_EX, (0, 10.6), (0, Y_MAX_EX), ALT_EX)
    p.titulo("Quanto vale emitir mais um bloco de 10 t")
    p.eixos("blocos emitidos", "R$ mil por bloco")

    # As duas escadas descem da esquerda para a direita, entao o espaco vazio
    # da figura e o canto de cima a direita e o de baixo a esquerda. Todo
    # rotulo vai para um dos dois: postos ao lado do proprio degrau, os quatro
    # se empilhavam na faixa entre 40 e 60, que e justamente onde as duas
    # escadas e a linha do dano se cruzam.
    escada(p, CRENCA, COR_GUIA, tracejado="6 4", larg=2.2)
    escada(p, VERDADE, COR_CMG)
    p.texto(0.15, VERDADE[0] + 8, "escada verdadeira", cor=COR_CMG,
            negrito=True, italico=False)
    p.texto(0.15, CRENCA[0] + 6, "o regulador supõe", cor=COR_GUIA,
            negrito=True, italico=False)

    p.reta(0, DANO_BLOCO, 10.6, DANO_BLOCO, cor=COR_DANO, larg=1.6,
           tracejado="6 4")
    p.texto(10.45, DANO_BLOCO + 7, "D′ = 45", cor=COR_DANO, negrito=True,
            ancora="end")

    p.reta(E_META, 0, E_META, Y_MAX_EX - 16, cor=COR_DESTAQUE, larg=2.0)
    p.texto(E_META + 0.15, Y_MAX_EX - 20, "L = 2", cor=COR_DESTAQUE,
            negrito=True, italico=False)
    # Onde a escada verdadeira cruza o dano: o imposto de 45 para no quarto
    # degrau, que e o corte eficiente das aulas 04, 06 e 07.
    p.reta(E_IMPOSTO, 0, E_IMPOSTO, VERDADE[E_IMPOSTO - 1], cor=COR_DANO,
           larg=2.0)
    p.texto(E_IMPOSTO + 0.15, 12, "imposto de 45 para aqui", cor=COR_DANO,
            negrito=True, italico=False)

    rodape(t, "o imposto lê a escada verdadeira; a quantidade foi escolhida na"
              " escada errada", larg=LARG_EX, alt=ALT_EX)
    return t


def exercicio_degrau():
    """A mesma escada, com dano marginal que salta de 45 para 300 em 30 t.

    O 300 nao cabe no painel e nem precisa caber: o que a figura tem de dizer e
    que passar dos tres blocos e caro DEMAIS, e uma seta saindo pelo topo diz
    isso melhor do que uma escala tres vezes maior diria.
    """
    t = Tela(LARG_EX + FOLGA_EX, ALT_EX + 46)
    p = Painel(t, 0, LARG_EX, (0, 10.6), (0, Y_MAX_EX), ALT_EX)
    p.titulo("O mesmo custo, com dano marginal em degrau")
    p.eixos("blocos emitidos", "R$ mil por bloco")

    escada(p, VERDADE, COR_CMG)
    p.texto(0.15, VERDADE[0] + 8, "escada verdadeira", cor=COR_CMG,
            negrito=True, italico=False)

    # A perna de 300 sai pelo topo, com seta. Desenhar a escala ate 300 para
    # acomoda-la achataria a escada de custo inteira na faixa de baixo, e a
    # escada e o objeto que a turma tem de ler.
    p.reta(0, DANO_BLOCO, BLOCOS_LIMIAR, DANO_BLOCO, cor=COR_DANO, larg=1.8)
    topo = p.py(Y_MAX_EX - 4)
    p.t.add('<line x1="{:.1f}" y1="{:.1f}" x2="{:.1f}" y2="{:.1f}"'
            ' stroke="{}" stroke-width="1.8" marker-end="url(#seta-dano)"/>'
            .format(p.px(BLOCOS_LIMIAR), p.py(DANO_BLOCO),
                    p.px(BLOCOS_LIMIAR), topo, COR_DANO))
    p.texto(BLOCOS_LIMIAR + 0.15, Y_MAX_EX - 30, "D′ = 300 do 4º bloco em"
            " diante", cor=COR_DANO, negrito=True, italico=False)
    p.texto(0.15, DANO_BLOCO - 14, "D′ = 45 até 30 t", cor=COR_DANO,
            negrito=True, italico=False)
    # O eficiente e o degrau: vale a pena emitir enquanto o bloco custar menos
    # de 45 em dano, e o terceiro e o ultimo que custa isso.
    p.marca_x(BLOCOS_LIMIAR, "eficiente", cor=COR_DESTAQUE)

    p.reta(E_META, 0, E_META, 78, cor=COR_DESTAQUE, larg=2.0)
    p.texto(E_META + 0.15, 74, "L = 2 para aqui", cor=COR_DESTAQUE,
            negrito=True, italico=False)
    p.reta(E_IMPOSTO, 0, E_IMPOSTO, VERDADE[E_IMPOSTO - 1], cor=COR_DANO,
           larg=2.0, tracejado="5 4")
    p.texto(E_IMPOSTO + 0.15, 12, "o imposto de 45 continua parando aqui",
            cor=COR_DANO, negrito=True, italico=False)

    rodape(t, "agora o quarto bloco custa 300 em dano, e quem erra é o"
              " imposto", larg=LARG_EX, alt=ALT_EX)
    return t


# ---------------------------------------------------------------------------

FIGURAS = [
    ("08-dano-1.svg", dano_1, "Dano subestimado desloca a meta"),
    ("08-dano-2.svg", dano_2, "A perda medida com o dano verdadeiro"),
    ("08-dano-3.svg", dano_3, "Imposto e leilão produzem o mesmo ponto"),
    ("08-custo-1.svg", custo_1, "Custo de abatimento subestimado"),
    ("08-custo-2.svg", custo_preco, "A perda sob instrumento de preço"),
    ("08-custo-3.svg", custo_quantidade,
     "A perda sob instrumento de quantidade"),
    ("08-custo-4.svg", custo_4, "As duas perdas lado a lado"),
    ("08-weitzman.svg", weitzman, "Weitzman: a inclinação do dano decide"),
    ("08-exercicio.svg", exercicio, "As duas escadas do exercício"),
    ("08-exercicio-degrau.svg", exercicio_degrau,
     "O exercício com dano marginal em degrau"),
]


def main():
    print("Figuras da aula 08 (E* = 125; dano: Ẽ = 140, WL = 60; custo:"
          " Ẽ = 75, E(τ) = 155, b = {}, c = {}):"
          .format(fmt(B_QTD), fmt(C_PRECO)))
    for nome, fn, titulo in FIGURAS:
        fn().salvar(nome, titulo)
    print("  exercício: eficiente {} blocos, meta do regulador {}, imposto {}"
          .format(E_EFIC, E_META, E_IMPOSTO))
    print("  perdas: quantidade {} e imposto {} (dano constante);"
          " {} e {} (degrau)".format(PERDA_QTD, PERDA_IMP,
                                     PERDA_QTD_DEG, PERDA_IMP_DEG))


if __name__ == "__main__":
    main()
