#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Gera os diagramas da aula 14 (Transicao Energetica).

MOTIVO DE EXISTIR
-----------------
O `.pptx` 15 tem nove imagens e nenhuma sai de equacao: duas capturas do
Climate Watch, dois graficos do FMI, uma tabela da NPUC e quatro figuras
recortadas de working papers (Hong et al. 2025; Bushnell et al. 2022). So as
do Climate Watch tem licenca aberta (CC BY 4.0). A aula vai em duas versoes:

  - a publica (site), que nao pode trazer as figuras recortadas;
  - a restrita (.pptx de sala), que traz as originais.

Aqui ficam as figuras que servem as DUAS versoes:

  1. emissoes por setor e por subsetor de energia, redesenhadas a partir dos
     dados do Climate Watch (scripts/dados/14-climatewatch-mundo.csv);
  2. a parcela verde de uma carteira de menor risco, que da a intuicao do
     resultado de Hong et al. (nao e o modelo dos autores; as notas de orador
     dizem isso, o slide nao diz desde 02/11);
  3. a concentracao da producao de minerais e de combustiveis fosseis, com os
     numeros da fig. 1 de Dominguez-Iino, Elliott e Hsiao (2026);
  4. o aquecimento em 2200 com e sem a perda de produtividade agricola, por
     ano de inicio da mitigacao, com os numeros do texto de Xu et al. (2022).

Depende so da biblioteca padrao, como os outros scripts desta pasta.

    py scripts/figuras14svg.py

Escreve em aulas/_assets/figuras/.
"""

import math
import os

from figuras04svg import (Painel, Tela, COR_EIXO, COR_CMG, COR_DANO, COR_GUIA,
                          COR_APAGADA, COR_DESTAQUE, FONTE, FONTE_EIXO)
from figuras08svg import fmt
from figuras11svg import COR_Q, COR_PROD, FOLGA, ALTURA_RODAPE, rodape, moldura
from figuras13svg import COR_FUT

LARG, ALT = 700, 340

# ===========================================================================
# 1. Emissoes (Climate Watch)
# ===========================================================================

CSV = os.path.join(os.path.dirname(os.path.abspath(__file__)), "dados",
                   "14-climatewatch-mundo.csv")


def ler_cw():
    with open(CSV, encoding="utf-8") as fh:
        linhas = [l.strip() for l in fh if l.strip() and not l.startswith("#")]
    anos = [int(a) for a in linhas[0].split(",")[1:]]
    dados = {}
    for l in linhas[1:]:
        campos = l.split(",")
        dados[campos[0]] = {a: float(v) / 1000.0           # Mt -> Gt
                            for a, v in zip(anos, campos[1:]) if v}
    return anos, dados


ANOS, CW = ler_cw()
ANO_FIM = ANOS[-1]
TOTAL_FIM = CW["Total including LULUCF"][ANO_FIM]
ENERGIA_FIM = CW["Energy"][ANO_FIM]
PARTE_ENERGIA = ENERGIA_FIM / TOTAL_FIM
assert ANO_FIM == 2023
assert 0.74 < PARTE_ENERGIA < 0.79          # o "~75%" do slide


def linha_cw(p, serie, cor, larg=2.6):
    pts = [(a, serie[a]) for a in ANOS if a in serie]
    d = "M {:.1f} {:.1f} ".format(*p.p(*pts[0]))
    d += " ".join("L {:.1f} {:.1f}".format(*p.p(x, y)) for x, y in pts[1:])
    p.t.add('<path d="{}" fill="none" stroke="{}" stroke-width="{:.1f}"'
            ' stroke-linejoin="round"/>'.format(d, cor, larg))
    p.ponto(pts[-1][0], pts[-1][1], cor=cor, r=4)


def marcas_anos(p):
    for a in (1990, 2000, 2010, 2023):
        p.marca_x(a, str(a))


SETORES = (
    ("Energy", "energia", COR_DESTAQUE),
    ("Agriculture", "agricultura", COR_PROD),
    ("Industrial Processes", "processos industriais", COR_Q),
    ("Waste", "resíduos", COR_FUT),
    ("Land Use  Land-Use Change and Forestry", "uso da terra", COR_GUIA),
)


def emissoes_setores():
    titulo = "Emissões mundiais de gases de efeito estufa, por setor"
    t, p = moldura(titulo, LARG, ALT, (1990, 2023), (0, 44), "",
                   "GtCO₂e")
    for v in (10, 20, 30, 40):
        p.marca_y(v, str(v))
        p.reta(1990, v, 2023, v, cor=COR_APAGADA, larg=0.8)
    for chave, _, cor in SETORES:
        linha_cw(p, CW[chave], cor)
    # rotulos junto da linha, cada um num trecho onde ela esta sozinha
    p.texto(2006, CW["Energy"][2006] + 1.6, "energia", cor=COR_DESTAQUE,
            negrito=True, ancora="middle")
    p.texto(1991, CW["Agriculture"][1991] + 1.2, "agricultura", cor=COR_PROD,
            negrito=True)
    p.texto(2022.4, CW["Agriculture"][2022] + 1.6,
            "processos industriais", cor=COR_Q, negrito=True, ancora="end")
    p.reta(2019, CW["Agriculture"][2019] + 1.0, 2019,
           CW["Industrial Processes"][2019] + 0.3, cor=COR_Q, larg=1.0)
    p.texto(2000.5, 13.8, "uso da terra", cor=COR_GUIA, negrito=True)
    p.reta(2003.5, 12.9, 2003.5, CW[SETORES[4][0]][2003] + 0.4,
           cor=COR_GUIA, larg=1.0)
    p.texto(2006, 8.4, "resíduos", cor=COR_FUT, negrito=True)
    p.reta(2008, 7.5, 2008, CW["Waste"][2008] + 0.4, cor=COR_FUT, larg=1.0)
    p.texto(ANO_FIM, ENERGIA_FIM + 2.4, fmt(ENERGIA_FIM), cor=COR_DESTAQUE,
            negrito=True, italico=False, ancora="end")
    marcas_anos(p)
    rodape(t, LARG, ALT,
           "em {}, a energia emitiu {} das {} GtCO₂e do mundo ({}%)".format(
               ANO_FIM, fmt(ENERGIA_FIM), fmt(TOTAL_FIM),
               fmt(100 * PARTE_ENERGIA, 0)))
    t.salvar("14-emissoes-setores.svg", titulo)


SUBSETORES = (
    ("Electricity/Heat", "eletricidade e calor", COR_DESTAQUE),
    ("Transportation", "transporte", COR_CMG),
    ("Manufacturing/Construction", "indústria e construção", COR_PROD),
    ("Building", "edificações", COR_FUT),
)


def emissoes_energia():
    titulo = "Emissões do setor de energia, por subsetor"
    t, p = moldura(titulo, LARG, ALT, (1990, 2023), (0, 19), "", "GtCO₂e")
    for v in (5, 10, 15):
        p.marca_y(v, str(v))
        p.reta(1990, v, 2023, v, cor=COR_APAGADA, larg=0.8)
    for chave, _, cor in SUBSETORES:
        linha_cw(p, CW[chave], cor)
    p.texto(2003, CW["Electricity/Heat"][2003] + 1.0, "eletricidade e calor",
            cor=COR_DESTAQUE, negrito=True, ancora="end")
    p.texto(2013, CW["Transportation"][2013] + 0.9, "transporte",
            cor=COR_CMG, negrito=True, ancora="end")
    p.texto(2013, CW["Manufacturing/Construction"][2013] - 1.1,
            "indústria e construção", cor=COR_PROD, negrito=True,
            ancora="start", tam=FONTE)
    p.texto(1991, CW["Building"][1991] - 1.0, "edificações", cor=COR_FUT,
            negrito=True)
    for chave, _, cor in SUBSETORES[:2]:
        v = CW[chave][ANO_FIM]
        p.texto(ANO_FIM, v + 0.75, fmt(v), cor=cor, negrito=True,
                italico=False, ancora="end")
    marcas_anos(p)
    ele, tra = CW["Electricity/Heat"][ANO_FIM], CW["Transportation"][ANO_FIM]
    rodape(t, LARG, ALT,
           "em {}, eletricidade e transporte somaram {} GtCO₂e: {}% das"
           " emissões da energia".format(ANO_FIM, fmt(ele + tra),
                                         fmt(100 * (ele + tra) / ENERGIA_FIM,
                                             0)))
    t.salvar("14-emissoes-energia.svg", titulo)


# ===========================================================================
# 2. Volatilidade: a parcela verde de uma carteira de menor risco
# ===========================================================================
# Intuicao, e nao o modelo de Hong et al.: dois ativos com o mesmo retorno
# esperado, um verde e um marrom. A carteira de variancia minima poe no verde
#
#   w = (s_m^2 - rho s_v s_m) / (s_v^2 + s_m^2 - 2 rho s_v s_m)
#
# Com volatilidades iguais, w = 1/2 para qualquer rho. As volatilidades sao as
# que os autores imputam (39% contra 23%); rho = 0,2 e hipotese.

S_MARROM, S_VERDE, RHO = 0.23, 0.39, 0.2


def parcela_verde(s_v, s_m=S_MARROM, rho=RHO):
    return ((s_m * s_m - rho * s_v * s_m)
            / (s_v * s_v + s_m * s_m - 2 * rho * s_v * s_m))


W_IGUAL = parcela_verde(S_MARROM)
W_HONG = parcela_verde(S_VERDE)
assert abs(W_IGUAL - 0.5) < 1e-12
assert abs(W_HONG - 0.2067) < 1e-3


def volatilidade():
    titulo = "Carteira de menor risco: quanto vai para o ativo verde?"
    t, p = moldura(titulo, LARG, ALT, (0.10, 0.50), (0, 90), "σ",
                   "% no ativo verde")
    for v in (25, 50, 75):
        p.marca_y(v, str(v))
    p.curva(lambda s: 100 * parcela_verde(s), 0.145, 0.50,
            cor=COR_PROD, larg=2.8)
    for s, w, rot in ((S_MARROM, W_IGUAL, "0,23"), (S_VERDE, W_HONG, "0,39")):
        p.guia(s, 100 * w)
        p.ponto(s, 100 * w, r=5.5)
        p.marca_x(s, rot)
    p.texto(S_MARROM + 0.01, 100 * W_IGUAL + 4, "volatilidades iguais: 50%",
            cor=COR_DESTAQUE, negrito=True)
    p.texto(S_VERDE + 0.01, 100 * W_HONG + 4,
            "verde a 39%: {}%".format(fmt(100 * W_HONG, 0)),
            cor=COR_DESTAQUE, negrito=True)
    p.texto(0.49, 80, "σ do marrom = 0,23; correlação = 0,2", cor=COR_GUIA,
            ancora="end", italico=False)
    rodape(t, LARG, ALT,
           "no eixo, a volatilidade do ativo verde. Mesmo retorno esperado:"
           " o investidor só olha o risco")
    t.salvar("14-volatilidade.svg", titulo)


# ===========================================================================
# 3. Concentracao da producao (Dominguez-Iino et al. 2026, fig. 1)
# ===========================================================================
# Parcela da producao mundial, media de 2015 a 2024, dos tres maiores
# produtores. Valores lidos da figura (duas casas); o do maior produtor de
# cada mineral bate com o texto da secao 7.1 (50%, 53%, 74%).

CONCENTRACAO = (
    ("petróleo", (("EUA", 0.14), ("Rússia", 0.13), ("Arábia S.", 0.12))),
    ("gás natural", (("EUA", 0.23), ("Rússia", 0.17), ("Irã", 0.06))),
    ("níquel", (("Indonésia", 0.53), ("Filipinas", 0.115), ("Rússia", 0.065))),
    ("cobalto", (("RDC", 0.74), ("Indonésia", 0.04), ("Austrália", 0.03))),
    ("lítio", (("Austrália", 0.50), ("Chile", 0.27), ("Argentina", 0.08))),
)
TOP3 = [sum(v for _, v in paises) for _, paises in CONCENTRACAO]
assert [round(100 * x) for x in TOP3] == [39, 46, 71, 81, 85]

CORES_PAISES = (COR_DESTAQUE, "#4f6f94", "#9db2cc")


def concentracao():
    titulo = "Parcela da produção mundial dos três maiores produtores"
    t = Tela(LARG + FOLGA, ALT + ALTURA_RODAPE)
    p = Painel(t, 0, LARG, (0, 5), (0, 1.0), ALT)
    p.titulo(titulo)
    p.eixos("", "")
    for v in (0.25, 0.5, 0.75, 1.0):
        p.marca_y(v, "{}%".format(int(100 * v)))
        p.reta(0, v, 5, v, cor=COR_APAGADA, larg=0.8)
    for k, (bem, paises) in enumerate(CONCENTRACAO):
        x, base = k + 0.5, 0.0
        for j, (pais, v) in enumerate(paises):
            p.area([(x - 0.33, base), (x - 0.33, base + v),
                    (x + 0.33, base + v), (x + 0.33, base)],
                   CORES_PAISES[j])
            if v >= 0.06:
                p.texto(x, base + v / 2 - 0.018, pais, italico=False,
                        cor="#ffffff" if j < 2 else COR_EIXO,
                        ancora="middle", tam=14, halo=False)
            base += v
        p.texto(x, base + 0.035, "{}%".format(round(100 * base)),
                cor=COR_DESTAQUE, negrito=True, italico=False,
                ancora="middle", tam=FONTE_EIXO)
        p.marca_x(x, bem)
    p.reta(2.0, 0, 2.0, 0.98, cor=COR_GUIA, larg=1.1,
           tracejado="4 3")
    p.texto(1.0, 0.93, "combustíveis fósseis", cor=COR_GUIA, negrito=True,
            italico=False, ancora="middle")
    p.texto(3.5, 0.97, "minerais das baterias", cor=COR_GUIA, negrito=True,
            italico=False, ancora="middle")
    rodape(t, LARG, ALT,
           "três países produzem 39% a 46% dos fósseis, mas 71% a 85% dos"
           " minerais (média 2015 a 2024)")
    t.salvar("14-concentracao.svg", titulo)


# ===========================================================================
# 4. Biomassa: o atraso que se realimenta (Xu et al. 2022)
# ===========================================================================
# Numeros do texto do artigo (p. 302), nao lidos de figura. Aquecimento em
# 2200 acima de 1850-1900, mediana, com a produtividade agricola respondendo
# ao clima; "sem feedback" e o mesmo cenario com a capacidade de BECCS fixa
# no clima de 2020 ("0,3, 0,6 e 0,8 C a menos").

INICIOS = (2040, 2050, 2060)
AQUEC_2200 = (1.7, 2.6, 3.7)
PARTE_FEEDBACK = (0.3, 0.6, 0.8)
AQUEC_2200_SEM = tuple(round(a - d, 1)
                       for a, d in zip(AQUEC_2200, PARTE_FEEDBACK))

assert AQUEC_2200_SEM == (1.4, 2.0, 2.9)
assert all(a < b for a, b in zip(PARTE_FEEDBACK, PARTE_FEEDBACK[1:]))
assert [a < 2 for a in AQUEC_2200] == [True, False, False]
assert AQUEC_2200_SEM[1] == 2.0           # 2050 sem feedback: na meta (47%)

COR_SEM = "#9db2cc"     # o azul claro de CORES_PAISES


def atraso_biomassa():
    titulo = "Aquecimento em 2200, por ano de início da mitigação"
    um = lambda v: "{:.1f}".format(v).replace(".", ",")   # 2,0 e nao 2
    t = Tela(LARG + FOLGA, ALT + ALTURA_RODAPE)
    p = Painel(t, 0, LARG, (0, 3), (0, 4.5), ALT)
    p.titulo(titulo)
    p.eixos("", "°C")
    for v in (1, 2, 3, 4):
        p.marca_y(v, str(v))
        p.reta(0, v, 3, v, cor=COR_APAGADA, larg=0.8)
    for k, ano in enumerate(INICIOS):
        x, base, topo = k + 0.5, AQUEC_2200_SEM[k], AQUEC_2200[k]
        p.area([(x - 0.22, 0), (x - 0.22, base), (x + 0.22, base),
                (x + 0.22, 0)], COR_SEM)
        p.area([(x - 0.22, base), (x - 0.22, topo), (x + 0.22, topo),
                (x + 0.22, base)], COR_CMG)
        p.texto(x, base / 2 - 0.08, um(base), cor=COR_DESTAQUE,
                negrito=True, italico=False, ancora="middle",
                tam=FONTE_EIXO, halo=False)
        p.texto(x + 0.28, (base + topo) / 2 - 0.08,
                "+" + um(PARTE_FEEDBACK[k]), cor=COR_CMG, negrito=True,
                italico=False, ancora="start")
        p.texto(x, topo + 0.12, um(topo), cor=COR_EIXO, negrito=True,
                italico=False, ancora="middle", tam=FONTE_EIXO)
        p.marca_x(x, str(ano))
    p.reta(0, 2, 3, 2, cor=COR_EIXO, larg=1.4, tracejado="6 4")
    p.texto(0.03, 2.1, "meta: 2 °C", cor=COR_EIXO, negrito=True,
            italico=False)
    for j, (cor, nome) in enumerate(
            ((COR_SEM, "com a produtividade fixa no clima de 2020"),
             (COR_CMG, "acréscimo pela perda de produtividade"))):
        y = 4.3 - 0.3 * j
        p.area([(0.06, y - 0.1), (0.06, y + 0.1), (0.13, y + 0.1),
                (0.13, y - 0.1)], cor)
        p.texto(0.18, y - 0.08, nome, cor=COR_EIXO, italico=False)
    rodape(t, LARG, ALT,
           "cada década de atraso aumenta a parte do aquecimento que vem"
           " da perda de produtividade agrícola")
    t.salvar("14-atraso-biomassa.svg", titulo)

def main():
    print("aula 14 - transicao energetica")
    emissoes_setores()
    emissoes_energia()
    volatilidade()
    concentracao()
    atraso_biomassa()
    print()
    print("  conferencia:")
    print("    Climate Watch {}: total {:.2f} Gt, energia {:.2f} Gt ({:.1f}%)"
          .format(ANO_FIM, TOTAL_FIM, ENERGIA_FIM, 100 * PARTE_ENERGIA))
    for chave, nome, _ in SUBSETORES:
        print("      {}: {:.2f} Gt".format(nome, CW[chave][ANO_FIM]))
    print("    carteira: w(0,23) = {:.3f}, w(0,39) = {:.4f}".format(
        W_IGUAL, W_HONG))
    print("    top 3: {}".format(", ".join(
        "{} {:.0f}%".format(b, 100 * x)
        for (b, _), x in zip(CONCENTRACAO, TOP3))))
    print("    biomassa 2200: com {}, sem {}".format(AQUEC_2200,
                                                  AQUEC_2200_SEM))


if __name__ == "__main__":
    main()
