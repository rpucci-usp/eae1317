#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Gera os diagramas da aula 09 (Instrumento Hibrido) a partir das equacoes.

Segunda metade de `06_eae1317_informacaoAssimetrica.pptx`, e como a primeira ela
nao tem figura nenhuma: os pontos em que o argumento vira geometria estao
marcados "(LOUSA)".

Importa `Painel`, `Tela` e as cores de figuras04svg.py, e as curvas agregadas e
os utilitarios de figuras08svg.py — a economia e a mesma da aula passada, o que
muda e o instrumento.

O INSTRUMENTO
-------------
O regulador leiloa L permissoes, cobra um imposto tau por unidade emitida ACIMA
do que a firma detem e paga um subsidio psi por unidade abaixo. Arbitragem poe
o preco da permissao numa faixa:

    psi <= sigma <= tau

Em (E, preco) isso e uma ESCADA de oferta: horizontal em psi ate L, vertical em
L entre psi e tau, horizontal em tau depois de L. A curva de abatimento cruza
essa escada em um dos tres trechos, e e o trecho que diz qual instrumento esta
mordendo.

OS TRES CENARIOS, E POR QUE ELES SAO "BASTANTE CONVENIENTES"
------------------------------------------------------------
O `.pptx` pede tres curvas -C^1' < -C^2' < -C^3' desenhadas "de forma bastante
conveniente", com o parenteses "(essas curvas vao cruzar o dano marginal em
E*)". A construcao que satisfaz isso e exata:

    -C^k'(E) = (A_k - E)/3,   A = 280, 200, 120
    D'(E)    = 0,2 E,  L = 125,  psi = 15,  tau = 35

    cenario 1: eficiente em 175, preco 35  = tau  -> o TETO entrega o eficiente
    cenario 2: eficiente em 125, preco 25         -> a VERTICAL entrega
    cenario 3: eficiente em  75, preco 15  = psi  -> o PISO entrega

A ordem dos cenarios e a do proprio .pptx, que escreve C^1' < C^2' < C^3'. Como
C' e negativo, isso e -C^1' > -C^2' > -C^3': o cenario 1 e o de abatimento CARO.
Inverter a numeracao aqui deixaria a figura contradizendo a equacao do slide.

Os tres pontos eficientes ficam sobre D', espacados de 50 em 50, e os tres
precos de 10 em 10. O cenario 2 e a economia das aulas 04 a 08 (E* = 125,
preco 25), entao a figura tem uma ancora conhecida no meio.

O QUE O HIBRIDO GANHA
---------------------
Com L = 125 e NADA MAIS, o cenario 3 fica preso em 125 (perda 666,7, que e o
mesmo b da aula 08, e nao por acaso: mesmo deslocamento, mesmas inclinacoes) e
o cenario 1 escorrega para 120 com preco zero (perda 540). As duas valvulas
zeram as duas perdas.

O exercicio e a setima volta das usinas A e B, e fecha o par com o da aula 08:
la cada instrumento puro tinha um caso catastrofico, aqui o hibrido nao tem.

Depende so da biblioteca padrao, como os outros scripts desta pasta.

    py scripts/figuras09svg.py

Escreve em aulas/_assets/figuras/.
"""

from figuras04svg import (Painel, Tela, COR_CMG, COR_DANO, COR_EIXO,
                          COR_GUIA, COR_DESTAQUE, FONTE, FONTE_LEGENDA)
from figuras08svg import (E_LF, A_MAC, ETA, dano_mg, E_OTIMO, PRECO_OTIMO,
                          BLOCOS_A, BLOCOS_B, DANO_BLOCO, DANO_DEGRAU,
                          BLOCOS_LIMIAR, VERDADE, social, fmt, reta_clip,
                          escada)

# --- o instrumento ----------------------------------------------------------
L_PERM = E_OTIMO                 # 125 permissoes, a meta do cenario central
TETO = 35.0                      # imposto: o preco nunca passa disso
PISO = 15.0                      # subsidio: o preco nunca cai abaixo disso
assert PISO < PRECO_OTIMO < TETO, "sigma* deveria cair dentro do corredor"

# --- os tres cenarios de custo ---------------------------------------------
# A_k escolhido para que o eficiente de cada cenario caia exatamente sobre o
# trecho da escada que aquele cenario alcanca. Ver docstring.
CENARIOS = (280.0, E_LF, 120.0)


def mac_k(A):
    return lambda E: (A - E) * A_MAC


def eficiente(A):
    """Onde -C^k' cruza D'."""
    e = A * A_MAC / (ETA + A_MAC)
    return e, dano_mg(e)


EFIC = [eficiente(A) for A in CENARIOS]
assert [round(e) for e, _ in EFIC] == [175, 125, 75], "os eficientes mudaram"
assert [round(p) for _, p in EFIC] == [35, 25, 15], "os precos eficientes mudaram"
# O que torna a construcao "conveniente": o teto e o piso sao exatamente os
# precos eficientes dos cenarios extremos.
assert abs(EFIC[0][1] - TETO) < 1e-9, "o teto deixou de entregar o cenario 1"
assert abs(EFIC[2][1] - PISO) < 1e-9, "o piso deixou de entregar o cenario 3"
assert abs(EFIC[1][0] - L_PERM) < 1e-9, "a vertical deixou de entregar o cenario 2"


def sem_valvula(A):
    """Onde o cenario para com L e mais nada.

    O preco nao pode ser negativo: se as firmas quiserem emitir menos que L, o
    excedente de permissoes vira lixo e o preco vai a zero. E o que acontece no
    cenario 1, e e por isso que a perda dele nao e simetrica a do cenario 3.
    """
    e_livre = A                            # onde -C^k' encosta no eixo
    if e_livre < L_PERM:
        return e_livre, 0.0
    return L_PERM, mac_k(A)(L_PERM)


def perda(A, e_real):
    """Area entre -C^k' e D' entre o ponto realizado e o eficiente."""
    e_ot, _ = eficiente(A)
    alt = abs(mac_k(A)(e_real) - dano_mg(e_real))
    return 0.5 * abs(e_ot - e_real) * alt


E_CARO, SIGMA_CARO = sem_valvula(CENARIOS[0])
E_BARATO, SIGMA_BARATO = sem_valvula(CENARIOS[2])
PERDA_CARO = perda(CENARIOS[0], E_CARO)
PERDA_BARATO = perda(CENARIOS[2], E_BARATO)

assert (E_CARO, round(SIGMA_CARO, 4)) == (125.0, round(155.0 / 3, 4)), \
    "o cenario caro sem valvula mudou"
assert (E_BARATO, SIGMA_BARATO) == (120.0, 0.0), \
    "o cenario barato sem valvula mudou"
assert abs(PERDA_CARO - 2000.0 / 3) < 1e-9, "a perda do cenario caro mudou"
assert abs(PERDA_BARATO - 540.0) < 1e-9, "a perda do cenario barato mudou"
# A ponte com a aula 08: a perda do cenario caro sob L puro E o `b` de la,
# porque o deslocamento vertical do erro e o mesmo (80/3) e as inclinacoes
# tambem.
assert abs(PERDA_CARO - 666.6666667) < 1e-6, "a ponte com o b da aula 08 quebrou"

# --- o exercicio: as mesmas usinas, agora com as duas valvulas --------------
L_EX = 2                         # o que o regulador emite, crendo nas contas erradas
TETO_EX = 55.0
PISO_EX = 30.0


def resultado_hibrido():
    """Quantos blocos as firmas emitem sob permissoes + teto + piso.

    Acima de L elas pagam o teto por bloco, entao emitem enquanto o bloco valer
    mais que o teto. Abaixo de L elas recebem o piso por bloco abatido, entao
    so descem se o bloco valer menos que o piso.
    """
    e = L_EX
    while e < len(VERDADE) and VERDADE[e] > TETO_EX:
        e += 1
    while e > 0 and VERDADE[e - 1] < PISO_EX:
        e -= 1
    return e


E_HIB = resultado_hibrido()
E_EFIC = min(range(11), key=lambda e: social(e))
E_EFIC_DEG = min(range(11), key=lambda e: social(e, degrau=True))
E_IMPOSTO = sum(1 for v in VERDADE if v > DANO_BLOCO)

assert (E_HIB, E_EFIC, E_EFIC_DEG, E_IMPOSTO) == (3, 4, 3, 2 + 2), \
    "o exercicio mudou de resposta"

PERDAS_EX = {
    "só permissões": (social(L_EX) - social(E_EFIC),
                      social(L_EX, True) - social(E_EFIC_DEG, True)),
    "só imposto": (social(E_IMPOSTO) - social(E_EFIC),
                   social(E_IMPOSTO, True) - social(E_EFIC_DEG, True)),
    "híbrido": (social(E_HIB) - social(E_EFIC),
                social(E_HIB, True) - social(E_EFIC_DEG, True)),
}
assert PERDAS_EX["só permissões"] == (20, 15), "as perdas de L puro mudaram"
assert PERDAS_EX["só imposto"] == (0, 250), "as perdas do imposto puro mudaram"
assert PERDAS_EX["híbrido"] == (5, 0), "as perdas do hibrido mudaram"
# O resultado que a aula quer: nenhum instrumento puro e bom nos dois cenarios,
# e o hibrido nunca e o pior.
for _dano in (0, 1):
    assert PERDAS_EX["híbrido"][_dano] <= max(PERDAS_EX["só permissões"][_dano],
                                              PERDAS_EX["só imposto"][_dano]), \
        "o hibrido deixou de ser o meio-termo"
assert max(PERDAS_EX["híbrido"]) < max(PERDAS_EX["só permissões"]) and \
    max(PERDAS_EX["híbrido"]) < max(PERDAS_EX["só imposto"]), \
    "o hibrido deixou de ter o menor caso ruim"

# --- geometria --------------------------------------------------------------
LARG_H = 760
ALT_H = 330
X_MAX_H = 215
# Os tres cenarios sao desenhados no mesmo painel e na mesma escala, que e o
# que torna comparavel dizer que um esta "acima" do outro. O teto do
# enquadramento nao acomoda -C^3'(0) = 93,3 de proposito: com 100 o corredor
# [15, 35] virava um quarto da altura e as tres travessias se amontoavam no pe
# do painel. Com 80 a curva 3 entra pela esquerda em E = 40, bem antes da
# primeira travessia, e o corredor ganha um terco da altura.
Y_MAX_H = 80
FOLGA_H = 20

LARG_EX_H = 760
ALT_EX_H = 344
Y_MAX_EX_H = 116
FOLGA_EX_H = 150                 # o rotulo "blocos emitidos", como na aula 08


def painel(titulo, rot_y="R$ por tonelada"):
    t = Tela(LARG_H + FOLGA_H, ALT_H + 46)
    p = Painel(t, 0, LARG_H, (0, X_MAX_H), (0, Y_MAX_H), ALT_H)
    p.titulo(titulo)
    p.eixos("E", rot_y)
    return t, p


def rodape(t, texto, larg=LARG_H, alt=ALT_H, cor=COR_DESTAQUE):
    t.texto(larg / 2, alt + 32, texto, ancora="middle", tam=FONTE_LEGENDA,
            cor=cor, negrito=True)


def escada_hibrida(p, rotulos=True):
    """A oferta efetiva: plana em psi, vertical em L, plana em tau."""
    p.reta(0, PISO, L_PERM, PISO, cor=COR_DESTAQUE, larg=2.6)
    p.reta(L_PERM, PISO, L_PERM, TETO, cor=COR_DESTAQUE, larg=2.6)
    p.reta(L_PERM, TETO, X_MAX_H, TETO, cor=COR_DESTAQUE, larg=2.6)
    if rotulos:
        p.marca_y(PISO, "ψ = 15", cor=COR_DESTAQUE)
        p.marca_y(TETO, "τ = 35", cor=COR_DESTAQUE)
        p.marca_x(L_PERM, "L = 125", cor=COR_DESTAQUE)


# ---------------------------------------------------------------------------
# 1. o corredor de preco
# ---------------------------------------------------------------------------

def corredor():
    t, p = painel("A oferta efetiva de permissões")
    escada_hibrida(p)
    reta_clip(p, mac_k(CENARIOS[1]), COR_CMG)
    p.texto(16, mac_k(CENARIOS[1])(16) + 6, "−C′(E)", cor=COR_CMG, negrito=True)
    p.ponto(L_PERM, PRECO_OTIMO)

    # As tres regioes, nomeadas pelo que a firma faz em cada uma.
    p.texto(0.5 * L_PERM, PISO - 12, "aqui a firma recebe subsídio",
            cor=COR_DESTAQUE, negrito=True, italico=False, ancora="middle")
    p.texto(0.5 * (L_PERM + X_MAX_H), TETO + 10, "aqui a firma paga imposto",
            cor=COR_DESTAQUE, negrito=True, italico=False, ancora="middle")

    rodape(t, "o preço da permissão fica preso entre ψ e τ: ψ ≤ σ ≤ τ")
    return t


# ---------------------------------------------------------------------------
# 2. os tres cenarios de custo
# ---------------------------------------------------------------------------

def cenarios():
    t, p = painel("Três cenários de custo, uma escada só")
    reta_clip(p, dano_mg, COR_DANO)
    p.texto(X_MAX_H - 6, 46, "D′(E)", cor=COR_DANO, negrito=True, ancora="end")
    escada_hibrida(p)

    for k, A in enumerate(CENARIOS):
        f = mac_k(A)
        reta_clip(p, f, COR_CMG, larg=2.0,
                  tracejado=None if k == 1 else "8 5")
        e_ot, preco = EFIC[k]
        p.ponto(e_ot, preco, cor=COR_CMG)
        # O cenario do meio nao ganha marca: ela cairia em cima do "L = 125"
        # que a propria escada ja escreve, e sao o mesmo numero.
        if k != 1:
            p.marca_x(e_ot, fmt(e_ot), cor=COR_CMG)
        # Um x por cenario, e nao um so: postos todos na mesma abscissa os tres
        # rotulos se empilhavam. O do 1 vai por BAIXO da curva (por cima ele
        # encostava no braco do teto, que corre em 35 justamente ali) e o do 3
        # nao vai ate a ponta (la ele cairia sobre a marca "L = 125" do eixo).
        x_rot, dy = ((213, -9), (196, 8), (60, 8))[k]
        p.texto(x_rot, f(x_rot) + dy, "−C" + "¹²³"[k] + "′(E)", cor=COR_CMG,
                negrito=True, ancora="end")

    rodape(t, "os três cenários cruzam D′ exatamente sobre a escada: o híbrido"
              " acerta nos três")
    return t


# ---------------------------------------------------------------------------
# 3 e 4. o que cada valvula salva
# ---------------------------------------------------------------------------

def valvula(cenario, titulo, texto_rodape):
    """Cenario 1 (piso) ou 3 (teto): a perda com L puro, e o ponto com valvula."""
    A = CENARIOS[cenario]
    f = mac_k(A)
    e_ot, preco_ot = EFIC[cenario]
    e_sem, sigma_sem = sem_valvula(A)

    t, p = painel(titulo)
    reta_clip(p, dano_mg, COR_DANO)
    reta_clip(p, f, COR_CMG)
    p.texto(X_MAX_H - 6, 46, "D′(E)", cor=COR_DANO, negrito=True, ancora="end")

    # A perda que L sozinho deixaria: triangulo entre as duas curvas.
    p.area([(e_sem, f(e_sem)), (e_ot, preco_ot), (e_sem, dano_mg(e_sem))],
           COR_DANO, 0.68)
    lado = -1 if e_sem < e_ot else 1
    p.texto(e_sem + lado * 6, 0.5 * (f(e_sem) + dano_mg(e_sem)),
            "perda " + fmt(perda(A, e_sem)), cor=COR_DANO, negrito=True,
            italico=False, ancora="end" if lado < 0 else "start")

    escada_hibrida(p)
    p.ponto(e_ot, preco_ot)
    p.marca_x(e_ot, "com a válvula", cor=COR_DESTAQUE)
    p.reta(e_sem, 0, e_sem, max(sigma_sem, 6), cor=COR_GUIA, larg=1.4,
           tracejado="4 3")
    # No cenario do teto o ponto sem valvula E o proprio L; no do piso ele fica
    # a 5 unidades dele, o que no eixo sao 16px e uma colisao. Nos dois casos
    # quem fica no eixo e a marca de L, e o "só L" vai para dentro do painel.
    if abs(e_sem - L_PERM) > 1e-9:
        p.texto(e_sem + 3, 5, "só L para aqui", cor=COR_GUIA, negrito=True,
                italico=False)

    rodape(t, texto_rodape)
    return t


def perda_teto():
    return valvula(0, "Custo maior do que o regulador supôs",
                   "sem o teto a emissão trava em 125; com τ = 35 ela chega"
                   " aos 175 eficientes")


def perda_piso():
    return valvula(2, "Custo menor do que o regulador supôs",
                   "sem o piso o preço vai a zero e sobra poluição; com ψ = 15"
                   " a emissão cai aos 75 eficientes")


# ---------------------------------------------------------------------------
# 5. o exercicio, em blocos
# ---------------------------------------------------------------------------

def exercicio():
    t = Tela(LARG_EX_H + FOLGA_EX_H, ALT_EX_H + 46)
    p = Painel(t, 0, LARG_EX_H, (0, 10.6), (0, Y_MAX_EX_H), ALT_EX_H)
    p.titulo("A mesma escada das usinas, com teto e piso")
    p.eixos("blocos emitidos", "R$ mil por bloco")

    escada(p, VERDADE, COR_CMG)
    p.texto(0.15, VERDADE[0] + 8, "escada verdadeira", cor=COR_CMG,
            negrito=True, italico=False)

    # A oferta hibrida, na mesma forma da figura do corredor.
    p.reta(0, PISO_EX, L_EX, PISO_EX, cor=COR_DESTAQUE, larg=2.6)
    p.reta(L_EX, PISO_EX, L_EX, TETO_EX, cor=COR_DESTAQUE, larg=2.6)
    p.reta(L_EX, TETO_EX, 10.6, TETO_EX, cor=COR_DESTAQUE, larg=2.6)
    p.marca_y(PISO_EX, "ψ = 30", cor=COR_DESTAQUE)
    p.marca_y(TETO_EX, "τ = 55", cor=COR_DESTAQUE)
    p.marca_x(L_EX, "L = 2", cor=COR_DESTAQUE)

    # Onde a escada de custo cruza o braco do teto.
    p.ponto(E_HIB, TETO_EX, cor=COR_DESTAQUE)
    p.reta(E_HIB, 0, E_HIB, TETO_EX, cor=COR_DESTAQUE, larg=1.4,
           tracejado="4 3")
    p.texto(E_HIB + 0.15, 12, "as firmas param em 3 blocos", cor=COR_DESTAQUE,
            negrito=True, italico=False)

    rodape(t, "o teto solta a emissão até onde o bloco vale menos que τ, e o"
              " piso a segura em L", larg=LARG_EX_H, alt=ALT_EX_H)
    return t


# ---------------------------------------------------------------------------

FIGURAS = [
    ("09-corredor.svg", corredor, "A oferta efetiva do instrumento híbrido"),
    ("09-cenarios.svg", cenarios, "Três cenários de custo sobre a mesma escada"),
    ("09-perda-teto.svg", perda_teto, "O teto salva o cenário de custo alto"),
    ("09-perda-piso.svg", perda_piso, "O piso salva o cenário de custo baixo"),
    ("09-exercicio.svg", exercicio, "O híbrido no exercício das usinas"),
]


def main():
    print("Figuras da aula 09 (L = {}, ψ = {}, τ = {}; eficientes {}):"
          .format(fmt(L_PERM), fmt(PISO), fmt(TETO),
                  ", ".join(fmt(e) for e, _ in EFIC)))
    for nome, fn, titulo in FIGURAS:
        fn().salvar(nome, titulo)
    print("  sem válvula: custo caro para em {} (perda {}), custo barato em {}"
          " (perda {})".format(fmt(E_CARO), fmt(PERDA_CARO), fmt(E_BARATO),
                               fmt(PERDA_BARATO)))
    print("  exercício: híbrido {} blocos; perdas (dano constante, degrau) = {}"
          .format(E_HIB, PERDAS_EX))


if __name__ == "__main__":
    main()
