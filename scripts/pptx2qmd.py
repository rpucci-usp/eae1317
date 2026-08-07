"""PPTX -> Quarto revealjs converter for EAE1317.

Handles three things the naive approach got wrong:

1. OMML equations are converted to LaTeX (they are real equation objects, not
   images). Variable letters use the Unicode math-italic block, normalised back
   to ASCII/Greek via NFKD.

2. Progressive reveals: the deck fakes animation by duplicating a slide and
   parking a background-coloured rectangle over the not-yet-revealed text, then
   shrinking it. Consecutive duplicate slides are collapsed into ONE Quarto
   slide whose later bullets carry `.fragment` spans, so a click reveals the
   same groups the white box used to uncover.

3. Empty spacer paragraphs are dropped (CSS handles the spacing).
"""
import zipfile, re, os, sys, json, unicodedata, difflib
from xml.etree import ElementTree as ET

import shapes2svg

A_NS = 'http://schemas.openxmlformats.org/drawingml/2006/main'
A14_NS = 'http://schemas.microsoft.com/office/drawing/2010/main'

PT = 12700.0
T_INS = 45720
SZ_BY_LVL = {0: 18.0, 1: 16.0, 2: 14.0, 3: 12.0, 4: 12.0}
SPC_BEF_PT = 10.0
LINE_FACTOR = 1.2
WHITE_FILLS = {'scheme:bg1', 'scheme:lt1', 'FFFFFF'}
MASK_GEOMS = {'rect', 'roundRect'}
# A paragraph counts as hidden when the mask covers the MIDDLE of its line box.
# Comparing against an edge instead needs a tolerance, and no tolerance works:
# the estimated position is off by around 10px even on a slide the model gets
# essentially right, which is more than the 5px that 20% of a single line
# gives you — lecture 02 slide 12 flipped a visible bullet to hidden on a 2px
# margin. The midpoint is half a line away from either edge, so the same error
# no longer decides anything.

SYMS = {
    'α': r'\alpha', 'β': r'\beta', 'γ': r'\gamma', 'Γ': r'\Gamma',
    'δ': r'\delta', 'Δ': r'\Delta', 'ε': r'\varepsilon', 'θ': r'\theta',
    'λ': r'\lambda', 'Λ': r'\Lambda', 'μ': r'\mu', 'π': r'\pi',
    'ρ': r'\rho', 'σ': r'\sigma', 'Σ': r'\Sigma', 'τ': r'\tau',
    'φ': r'\phi', 'Φ': r'\Phi', 'ω': r'\omega', 'Ω': r'\Omega',
    'χ': r'\chi', 'η': r'\eta', 'ξ': r'\xi', 'ι': r'\iota',
    '≥': r'\geq', '≤': r'\leq', '≠': r'\neq', '→': r'\to',
    '×': r'\times', '·': r'\cdot', '∞': r'\infty', '∂': r'\partial',
    '∑': r'\sum', '∫': r'\int', '√': r'\sqrt', '°': r'^\circ',
    '−': '-', '–': '-', '∀': r'\forall', '∃': r'\exists', '∗': '*',
    '≡': r'\equiv', '∈': r'\in', '∅': r'\emptyset', '⋅': r'\cdot',
    'ℓ': r'\ell', '≈': r'\approx', '±': r'\pm', '⇒': r'\Rightarrow',
    # Braces typed inside an equation are literal set braces (e.g. "i ∈ {1,2}").
    # Unescaped they are LaTeX grouping and vanish from the output.
    '{': r'\{', '}': r'\}',
}
# limLow with one of these as its base is an operator with a limit underneath
# (\max_{...}), not an arbitrary under-set expression.
LIM_OPS = {'max': r'\max', 'min': r'\min', 'lim': r'\lim', 'sup': r'\sup',
           'inf': r'\inf', 'arg max': r'\arg\max', 'arg min': r'\arg\min'}
DELIMS = {'{': r'\{', '}': r'\}', '|': '|', '‖': r'\|', '⟨': r'\langle',
          '⟩': r'\rangle', '': '.'}
SKIP_PR = {'ctrlPr', 'sSubPr', 'sSupPr', 'sSubSupPr', 'fPr', 'radPr', 'naryPr',
           'dPr', 'mathPr', 'oMathParaPr', 'rPr', 'functPr', 'barPr',
           'groupChrPr', 'limLowPr', 'limUppPr'}
# Wingdings arrow used as "implies" in the source decks
WINGDINGS_ARROW = ''


def ln(t):
    return t.split('}')[-1] if '}' in t else t


def child(e, name):
    for c in e:
        if ln(c.tag) == name:
            return c
    return None


def deep(e, name):
    for c in e.iter():
        if ln(c.tag) == name:
            return c
    return None


def sym_replace(s):
    """Map maths symbols to LaTeX, normalising anything left over.

    SYMS is consulted on both sides of the normalisation, because each side
    alone loses symbols:

    - before: NFKD decomposes some of them into a base character plus a
      combining mark ("≠" becomes "=" + U+0338), so a table lookup afterwards
      never sees them and a struck-through equals sign reaches the output as a
      plain "=";
    - after: the equations are typed in the maths-italic block, where "∂" and
      "λ" are U+1D715/U+1D706 rather than U+2202/U+03BB, and only normalising
      maps those onto the characters the table is keyed by.
    """
    out = []
    for ch in s:
        rep = SYMS.get(ch)
        if rep is None:
            norm = unicodedata.normalize('NFKD', ch)
            rep = SYMS.get(norm)
            if rep is None:
                out.append(norm)
                continue
        if rep[-1].isalpha():
            # trailing space so the next run can't glue onto the command name
            # (e.g. "∀" + "j" must be "\forall j", not "\forallj")
            out.append(rep + ' ')
        else:
            out.append(rep)
    return ''.join(out)


def math_text(elem):
    return ''.join(t.text or '' for t in elem.iter()
                   if ln(t.tag) == 't')


def latex_of(elem):
    tag = ln(elem.tag)
    if tag in SKIP_PR:
        return ''
    if tag == 'oMathPara':
        parts = [latex_of(c) for c in elem if ln(c.tag) == 'oMath']
        return r' \\ '.join(p for p in parts if p.strip())
    if tag == 'oMath':
        return ''.join(latex_of(c) for c in elem if ln(c.tag) not in SKIP_PR)
    if tag == 'r':
        return sym_replace(math_text(elem))
    if tag == 'f':
        num, den = child(elem, 'num'), child(elem, 'den')
        return r'\frac{%s}{%s}' % (latex_of(num) if num is not None else '',
                                   latex_of(den) if den is not None else '')
    if tag == 'sSub':
        e, sub = child(elem, 'e'), child(elem, 'sub')
        return r'{%s}_{%s}' % (latex_of(e) if e is not None else '',
                               latex_of(sub) if sub is not None else '')
    if tag == 'sSup':
        e, sup = child(elem, 'e'), child(elem, 'sup')
        return r'{%s}^{%s}' % (latex_of(e) if e is not None else '',
                               latex_of(sup) if sup is not None else '')
    if tag == 'sSubSup':
        e, sub, sup = child(elem, 'e'), child(elem, 'sub'), child(elem, 'sup')
        return r'{%s}_{%s}^{%s}' % (
            latex_of(e) if e is not None else '',
            latex_of(sub) if sub is not None else '',
            latex_of(sup) if sup is not None else '')
    if tag == 'rad':
        deg, e = child(elem, 'deg'), child(elem, 'e')
        inner = latex_of(e) if e is not None else ''
        d = latex_of(deg) if deg is not None else ''
        return r'\sqrt[%s]{%s}' % (d, inner) if d.strip() else r'\sqrt{%s}' % inner
    if tag == 'nary':
        chr_el = child(elem, 'naryPr')
        sub, sup, e = child(elem, 'sub'), child(elem, 'sup'), child(elem, 'e')
        op = r'\sum'
        if chr_el is not None:
            ch = child(chr_el, 'chr')
            if ch is not None:
                op = SYMS.get(ch.attrib.get('val', ''), r'\sum')
        out = op
        if sub is not None and latex_of(sub).strip():
            out += '_{%s}' % latex_of(sub)
        if sup is not None and latex_of(sup).strip():
            out += '^{%s}' % latex_of(sup)
        return out + ' ' + (latex_of(e) if e is not None else '')
    if tag in ('limLow', 'limUpp'):
        # "max" with the choice variables written underneath it. Reading only
        # the runs (the fallback below) flattens that into "max x1,x2,E U1(...)",
        # which reads as a product of variables instead of an operator.
        e, lim = child(elem, 'e'), child(elem, 'lim')
        base = (latex_of(e) if e is not None else '').strip()
        sub = (latex_of(lim) if lim is not None else '').strip()
        op = LIM_OPS.get(base.lower())
        slot = '_' if tag == 'limLow' else '^'
        if op:
            return '%s%s{%s} ' % (op, slot, sub)
        setter = r'\underset' if tag == 'limLow' else r'\overset'
        return r'%s{%s}{%s} ' % (setter, sub, base)
    if tag == 'func':
        fn, e = child(elem, 'fName'), child(elem, 'e')
        return ((latex_of(fn) if fn is not None else '')
                + (latex_of(e) if e is not None else ''))
    if tag == 'd':  # delimiters
        pr = child(elem, 'dPr')
        beg, end, sep = '(', ')', ','
        if pr is not None:
            for name, default in (('begChr', '('), ('endChr', ')'),
                                  ('sepChr', ',')):
                el = child(pr, name)
                if el is not None:
                    val = el.attrib.get(M_VAL, default)
                    if name == 'begChr':
                        beg = val
                    elif name == 'endChr':
                        end = val
                    else:
                        sep = val
        # A delimiter can hold several <e> children separated by sepChr; taking
        # only the first drops arguments (f(l, E) would come out as "f(l)").
        inner = sep.join(latex_of(c) for c in elem if ln(c.tag) == 'e')
        return r'\left%s%s\right%s' % (DELIMS.get(beg, beg), inner,
                                       DELIMS.get(end, end))
    if tag in ('e', 'num', 'den', 'sub', 'sup', 'deg', 'lim'):
        return ''.join(latex_of(c) for c in elem if ln(c.tag) not in SKIP_PR)
    return ''.join(latex_of(c) for c in elem)


# Words separated by spaces inside an equation are prose ("CMg Social"), not a
# product of variables. OMML splits them across many short runs, so this has to
# run on the assembled LaTeX. \textit keeps the source deck's italic look while
# restoring proper word spacing (plain math mode would render C*M*g*S*o*...).
PROSE_RE = re.compile(r'(?<![\\{])\b[A-Za-z]{2,}(?:[ ]+[A-Za-z]{2,})+')


def italicise_prose(latex):
    latex = PROSE_RE.sub(lambda m: r'\textit{%s}' % m.group(0), latex)
    return re.sub(r'[ \t]{2,}', ' ', latex).strip()


def find_omath(elem, acc):
    tag = ln(elem.tag)
    if tag == 'AlternateContent':
        ch = child(elem, 'Choice')
        if ch is not None:
            find_omath(ch, acc)
        return
    if tag == 'm' and elem.tag.startswith('{' + A14_NS):
        for c in elem:
            find_omath(c, acc)
        return
    if tag in ('oMathPara', 'oMath'):
        acc.append(elem)
        return
    for c in elem:
        find_omath(c, acc)


M_VAL = '{http://schemas.openxmlformats.org/officeDocument/2006/math}val'


def render_paragraph(p):
    """Parse one <a:p>.

    Returns a dict with the markdown text plus the presentation hints the deck
    carries: `no_bullet` (the paragraph had <a:buNone/>, i.e. it is not a bullet)
    and `centred` (its equation was centred via <m:jc m:val="centerGroup"/>).
    `math_only` marks paragraphs that are nothing but an equation, which become
    display math ($$...$$) instead of a list item.
    """
    lvl = 0
    pPr = child(p, 'pPr')
    if pPr is not None and 'lvl' in pPr.attrib:
        lvl = int(pPr.attrib['lvl'])
    no_bullet = pPr is not None and child(pPr, 'buNone') is not None
    numbered = pPr is not None and child(pPr, 'buAutoNum') is not None

    centred = False
    for el in p.iter():
        if ln(el.tag) == 'oMathPara':
            pr = child(el, 'oMathParaPr')
            j = child(pr, 'jc') if pr is not None else None
            if j is not None and 'center' in (j.attrib.get(M_VAL) or ''):
                centred = True

    parts = []
    latex_bits = []
    has_prose = False
    for c in p:
        tag = ln(c.tag)
        if tag == 'r' and c.tag.startswith('{' + A_NS):
            t = child(c, 't')
            rPr = child(c, 'rPr')
            txt = t.text if t is not None and t.text else ''
            if txt.strip():
                has_prose = True
            if rPr is not None and rPr.attrib.get('b') == '1' and txt.strip():
                lead = txt[:len(txt) - len(txt.lstrip())]
                trail = txt[len(txt.rstrip()):]
                txt = f'{lead}**{txt.strip()}**{trail}'
            parts.append(txt)
        elif tag in ('pPr', 'endParaRPr'):
            continue
        else:
            maths = []
            find_omath(c, maths)
            for m in maths:
                l = italicise_prose(latex_of(m).strip())
                if l:
                    latex_bits.append(l)
                    parts.append(f'${l}$')
    text = ''.join(parts)
    text = text.replace(WINGDINGS_ARROW, ' → ')
    text = re.sub(r'\*\*\s*\*\*', ' ', text)
    text = re.sub(r'[ \t]+', ' ', text).strip()
    return {'lvl': lvl, 'text': text, 'no_bullet': no_bullet,
            'numbered': numbered,
            'centred': centred, 'math_only': bool(latex_bits) and not has_prose,
            'latex': latex_bits}


def get_xfrm(sp):
    spPr = child(sp, 'spPr')
    if spPr is None:
        return None
    xfrm = child(spPr, 'xfrm')
    if xfrm is None:
        return None
    off, ext = child(xfrm, 'off'), child(xfrm, 'ext')
    if off is None or ext is None:
        return None
    return {'x': int(off.attrib.get('x', 0)), 'y': int(off.attrib.get('y', 0)),
            'cx': int(ext.attrib.get('cx', 0)), 'cy': int(ext.attrib.get('cy', 0))}


def get_fill(sp):
    spPr = child(sp, 'spPr')
    if spPr is None:
        return None
    solid = child(spPr, 'solidFill')
    if solid is None:
        return None
    srgb = child(solid, 'srgbClr')
    if srgb is not None:
        return srgb.attrib.get('val')
    scheme = child(solid, 'schemeClr')
    if scheme is not None:
        return 'scheme:' + scheme.attrib.get('val', '?')
    return None


def get_geom(sp):
    spPr = child(sp, 'spPr')
    if spPr is None:
        return None
    pg = child(spPr, 'prstGeom')
    return pg.attrib.get('prst') if pg is not None else None


def shape_has_text(sp):
    txBody = child(sp, 'txBody')
    if txBody is None:
        return False
    return any(ln(t.tag) == 't' and t.text and t.text.strip()
               for t in txBody.iter())


def walk_shapes(elem, acc):
    for c in elem:
        tag = ln(c.tag)
        if tag == 'AlternateContent':
            ch = child(c, 'Choice')
            if ch is not None:
                walk_shapes(ch, acc)
        elif tag in ('sp', 'pic'):
            acc.append(c)
        elif tag == 'grpSp':
            walk_shapes(c, acc)


_LAYOUTS = {}


def slide_layout(z, num):
    """Parsed slideLayout XML this slide is based on (cached per slide)."""
    if num not in _LAYOUTS:
        rels = z.read(f'ppt/slides/_rels/slide{num}.xml.rels').decode('utf-8')
        m = re.search(r'Target="\.\./(slideLayouts/slideLayout\d+\.xml)"', rels)
        _LAYOUTS[num] = ET.fromstring(z.read('ppt/' + m.group(1))) if m else None
    return _LAYOUTS[num]


def layout_name(z, num):
    lay = slide_layout(z, num)
    cSld = child(lay, 'cSld') if lay is not None else None
    return cSld.attrib.get('name', '') if cSld is not None else ''


def layout_body_box(z, num):
    lay = slide_layout(z, num)
    if lay is None:
        return None
    for sp in lay.iter():
        if ln(sp.tag) != 'sp':
            continue
        nv = child(sp, 'nvSpPr')
        nvPr = child(nv, 'nvPr') if nv is not None else None
        ph = child(nvPr, 'ph') if nvPr is not None else None
        if ph is not None and ph.attrib.get('type', 'body') == 'body':
            return get_xfrm(sp)
    return None


# Mean glyph advance as a fraction of the font size, for the deck's body font.
# Only used to guess how many lines a bullet wraps to. Measured on exported
# slides: 12px per character at an 18pt (24px) body font.
CHAR_W = 0.5
LVL_INDENT = 342900          # EMU per outline level (0.375", PowerPoint default)
_BODY_MARL = {}


def body_indents(z):
    """Left margin of each outline level, from the master's bodyStyle.

    The bullet indent is not decoration for the purposes of this file: it eats
    into the line width, and the line width decides where a bullet wraps, which
    decides where every bullet below it sits. Assuming level 0 starts at the
    box edge made a 76-character bullet fit on one line when the deck wraps it
    onto two, and everything under it was then estimated half a line too high.
    """
    if not _BODY_MARL:
        try:
            master = ET.fromstring(z.read('ppt/slideMasters/slideMaster1.xml'))
        except KeyError:
            master = None
        styles = deep(master, 'bodyStyle') if master is not None else None
        for i, lvl in enumerate(styles if styles is not None else []):
            _BODY_MARL[i] = int(lvl.attrib.get('marL', LVL_INDENT * (i + 1)))
    return _BODY_MARL


def autofit(txBody):
    """(font scale, line-spacing scale) PowerPoint applied to this placeholder.

    When text overflows its box PowerPoint shrinks it instead of spilling, and
    records the factors it used in <a:normAutofit>. Ignoring them makes every
    paragraph of a crowded slide come out lower than it really is, and the
    error accumulates down the slide until bullets land on the wrong side of a
    reveal mask (lecture 03 slides 25-27, shrunk to 92.5%, drifted ~70px by the
    last bullet).
    """
    bodyPr = child(txBody, 'bodyPr') if txBody is not None else None
    fit = child(bodyPr, 'normAutofit') if bodyPr is not None else None
    if fit is None:
        return 1.0, 1.0
    fs = float(fit.attrib.get('fontScale', 100000)) / 100000.0
    ln_red = float(fit.attrib.get('lnSpcReduction', 0)) / 100000.0
    return fs, 1.0 - ln_red


def drawn_text(text):
    """The characters that actually reach the slide.

    Markup and LaTeX plumbing are not drawn and must not count towards the
    line width: "$i\\in \\{1,2\\}$" is four characters wide on screen and
    fourteen in the source. Counting the source made bullets with maths in
    them wrap a line early, and everything below them was then estimated a
    line too low.
    """
    plain = re.sub(r'\\[a-zA-Z]+', 'x', text)      # \partial etc: one glyph
    return re.sub(r'[$*{}_^\\]', '', plain)


def frac_depth(text):
    """Extra line-heights a paragraph needs for its stacked fractions.

    A fraction is taller than a line, and a fraction of fractions (the
    Lagrangian conditions of lecture 03) is nearly four lines tall. Treating
    every paragraph as one line put the bullet after such an equation a
    hundred pixels too high.
    """
    depth = best = 0
    for m in re.finditer(r'\\frac|[{}]', text):
        tok = m.group(0)
        if tok == '\\frac':
            depth += 1
            best = max(best, depth)
        elif tok == '}' and depth:
            # crude: a closing brace at the end of a fraction's denominator
            # closes it. Good enough to tell one level from two.
            depth -= 0 if text[m.end():m.end() + 1] == '{' else 1
    return best


def wrapped_lines(text, lvl, sz_pt, box, marl):
    """How many lines this paragraph takes once wrapped.

    Assuming one line per paragraph (what this did at first) puts every
    paragraph after a two-line bullet too high on the slide, and the reveal
    masks are matched against those positions — on a dense slide the error
    reaches several lines and whole bullets end up on the wrong side of the
    mask. Rough is fine here: the comparison only needs to land within a line
    of the truth, and HIDE_TOL absorbs the rest.
    """
    width = max(box.get('cx', 0) - 2 * T_INS
                - marl.get(lvl, LVL_INDENT * (lvl + 1)), 1)
    per_line = max(int(width / (CHAR_W * sz_pt * PT)), 10)
    plain = drawn_text(text)
    return max(1, -(-len(plain) // per_line)) + frac_depth(text)


def parse_slide(z, num):
    root = ET.fromstring(z.read(f'ppt/slides/slide{num}.xml'))
    tree = deep(root, 'spTree')
    shapes = []
    walk_shapes(tree, shapes)

    title = None
    body_sp = None
    masks = []
    loose = []          # text boxes that aren't placeholders (graph labels)
    for sp in shapes:
        nv = child(sp, 'nvSpPr') or child(sp, 'nvPicPr')
        nvPr = child(nv, 'nvPr') if nv is not None else None
        ph = child(nvPr, 'ph') if nvPr is not None else None
        ptype = ph.attrib.get('type', 'body') if ph is not None else None
        txBody = child(sp, 'txBody')

        if ptype in ('title', 'ctrTitle'):
            if txBody is not None:
                paras = [render_paragraph(p) for p in txBody if ln(p.tag) == 'p']
                title = ' '.join(d['text'] for d in paras if d['text'].strip())
            continue
        if ptype in ('sldNum', 'ftr', 'dt'):
            continue
        if ptype == 'body' and body_sp is None:
            body_sp = sp
            continue
        if ph is None and ln(sp.tag) == 'sp':
            # 'roundRect' as well as 'rect': the mask is whatever rectangle the
            # author happened to draw, and lecture 03 uses rounded ones in
            # places. Missing it costs a whole reveal sequence silently.
            if get_fill(sp) in WHITE_FILLS and get_geom(sp) in MASK_GEOMS \
                    and not shape_has_text(sp):
                xf = get_xfrm(sp)
                if xf:
                    masks.append(xf)
            elif txBody is not None:
                for p in txBody:
                    if ln(p.tag) != 'p':
                        continue
                    d = render_paragraph(p)
                    if d['text'].strip():
                        loose.append(d['text'].strip())

    paras = []
    if body_sp is not None:
        # last resort if neither slide nor layout carries a body box: the
        # master's own geometry (9.75" wide, starting 1.8" down)
        box = (get_xfrm(body_sp) or layout_body_box(z, num)
               or {'y': 1647645, 'cx': 8915400})
        txBody = child(body_sp, 'txBody')
        font_scale, line_scale = autofit(txBody)
        marl = body_indents(z)
        y = box['y'] + T_INS
        for p in [q for q in txBody if ln(q.tag) == 'p']:
            d = render_paragraph(p)
            lvl, text = d['lvl'], d['text']
            empty = not text.strip()
            endPr = child(p, 'endParaRPr')
            end_sz = endPr.attrib.get('sz') if endPr is not None else None
            sz = SZ_BY_LVL.get(lvl, 12.0)
            if empty and end_sz:
                sz = float(end_sz) / 100.0
            sz *= font_scale
            # No space-before on the first paragraph: PowerPoint drops it at
            # the top of a text frame (measured against exported slides — the
            # first line starts exactly at the box top plus its inset). Adding
            # it there shifted every paragraph on every slide down by a third
            # of a line, which is most of the error the mask test was fighting.
            if paras:
                y += SPC_BEF_PT * font_scale * PT
            top = y
            y += (wrapped_lines(text, lvl, sz, box, marl) * sz * LINE_FACTOR
                  * line_scale * PT)
            d.update({'empty': empty, 'top': top, 'bottom': y})
            paras.append(d)

    # The mask's bottom edge matters, not only its top. The usual mask runs
    # from somewhere in the middle of the slide down past its bottom edge, so
    # for those the two tests agree — but the deck also uses a rectangle
    # covering a *band* in the middle (lecture 03 slide 27 dims the block it
    # already discussed while the one below it is on screen). Testing the top
    # edge alone marks everything under the band as hidden, which loses the
    # last reveal step of that sequence.
    for p in paras:
        if p['empty']:
            p['hidden'] = False
            continue
        mid = (p['top'] + p['bottom']) / 2.0
        p['hidden'] = any(m['y'] <= mid <= m['y'] + m['cy'] for m in masks)
    mask_top = min((m['y'] for m in masks), default=None)

    return {'num': num, 'title': title or '', 'paras': paras,
            'mask_top': mask_top, 'n_masks': len(masks), 'loose': loose,
            'section': layout_name(z, num) == 'Section Header'}


def texts_of(slide):
    return [p['text'] for p in slide['paras'] if not p['empty']]


def content_texts(slide):
    """Body texts excluding LOUSA markers, used for grouping comparisons."""
    return [t for t in texts_of(slide) if not LOUSA_RE.match(t.strip())]


def _similar(xs, ys, thresh=0.9):
    if not xs or not ys:
        return False
    return difflib.SequenceMatcher(
        None, ' '.join(xs), ' '.join(ys)).ratio() > thresh


def _norm_for_match(t):
    return re.sub(r'\s+', ' ', t.replace('**', '')).strip().lower()


def _lcs_fuzzy(xs, ys, thresh=0.85):
    """Length of the longest common subsequence, treating near-equal items as
    equal (same bullet, reworded slightly between reveal stages)."""
    m = [[0] * (len(ys) + 1) for _ in range(len(xs) + 1)]
    for i, x in enumerate(xs):
        for j, y in enumerate(ys):
            if x == y or difflib.SequenceMatcher(None, x, y).ratio() > thresh:
                m[i + 1][j + 1] = m[i][j] + 1
            else:
                m[i + 1][j + 1] = max(m[i][j + 1], m[i + 1][j])
    return m[len(xs)][len(ys)]


def same_content(a, b):
    """True when b is another stage of the same slide as a.

    Covers every way the decks fake animation: an identical duplicate with a
    shrinking white mask, and duplicates where the author also appended or
    inserted bullets between stages.
    """
    if a['title'] != b['title']:
        return False
    ta = [_norm_for_match(t) for t in content_texts(a)]
    tb = [_norm_for_match(t) for t in content_texts(b)]
    if not ta or not tb:
        return False
    if ta == tb:
        return True
    # How many bullets survive, in order, from one stage to the next? Compared
    # loosely on purpose: between stages the author also fixes typos and adds
    # the full stop he left off, so exact string equality undercounts badly
    # (lecture 03 slides 25-27 shared 8 bullets but only 3 of them character
    # for character, which fell under the threshold and split the sequence
    # into two near-identical Quarto slides).
    matched = _lcs_fuzzy(ta, tb)
    smaller = min(len(ta), len(tb))
    if matched and matched >= 0.6 * smaller:
        return True
    # last resort: same bullet count, author only reworded
    return len(ta) == len(tb) and _similar(ta, tb)


def group_slides(slides):
    groups = []
    for s in slides:
        if groups and same_content(groups[-1][-1], s):
            groups[-1].append(s)
        else:
            groups.append([s])
    return groups


LOUSA_RE = re.compile(r'^\**\s*LOUSA\s*\**$', re.I)
LABEL_RE = re.compile(r'^[A-Za-z0-9]{1,2}$')


def build_group_markdown(group, figure=None):
    """Collapse a reveal sequence into one slide with .fragment spans."""
    last = group[-1]           # most-corrected wording
    n_stages = len(group)

    # Slides built on the master's "Section Header" layout are not content
    # slides: they announce the block that follows, with the title left-aligned
    # further down the slide and an optional support line under it, in grey and
    # without a bullet. Converting them like a normal slide loses that — the
    # support line came out as a lone bullet. `.section-cover` / `.section-sub`
    # in styles.css reproduce the layout's geometry.
    if last.get('section'):
        sub = [p['text'] for p in last['paras'] if not p['empty']]
        out = [f'## {last["title"]} {{.section-cover}}']
        if sub:
            out += ['', '::: {.section-sub}', '\n\n'.join(sub), ':::']
        return '\n'.join(out), n_stages, 0

    # For each stage, the set of body texts actually on screen: present in that
    # slide AND not covered by the white mask.
    stage_visible = []
    for s in group:
        stage_visible.append([p['text'] for p in s['paras']
                              if not p['empty'] and not p['hidden']])

    def first_stage(text):
        """Earliest stage where this paragraph is visible, None if never."""
        key = _norm_for_match(text)
        for i, vis in enumerate(stage_visible):
            keys = [_norm_for_match(v) for v in vis]
            if key in keys:
                return i
            # fuzzy: author tweaked the wording between stages
            if any(_similar([key], [k], 0.92) for k in keys):
                return i
        return None

    frag_of = {}
    for pos, p in enumerate(x for x in last['paras'] if not x['empty']):
        frag_of[pos] = first_stage(p['text'])

    body = [p for p in last['paras'] if not p['empty']]
    has_lousa = any(LOUSA_RE.match(p['text'].strip()) for p in body)
    # Single letters left loose in the body are labels for a graph ("A", "B").
    # Only strip them when this slide actually has a graph, otherwise real
    # content disappears — the agenda of lecture 03 lists "Ar" as a bullet.
    strip_labels = has_lousa or bool(figure)

    lines = []
    labels = list(last['loose'])
    indent = {}
    pos = 0
    for p in last['paras']:
        if p['empty']:
            continue
        text = p['text']
        cur = pos
        pos += 1
        if LOUSA_RE.match(text.strip()):
            continue
        if strip_labels and LABEL_RE.match(text.strip()):
            labels.append(text.strip())
            continue
        f = frag_of.get(cur, 0)
        if f is None:
            # Covered by the white rectangle in every copy of the slide: the
            # author masked it out for good rather than deleting it, so it is
            # never projected. Kept as a comment — dropping it silently would
            # hide from the next reader that the .pptx still carries the text.
            lines += ['', f'<!-- oculto pela caixa branca em todas as etapas '
                          f'do .pptx: {text} -->', '']
            continue

        # Paragraphs the deck marked <a:buNone/> are not bullets. When they are
        # nothing but an equation they become display math, which revealjs
        # centres — matching the m:jc="centerGroup" of the source.
        if p.get('no_bullet') and p.get('math_only'):
            # A bare "$$...$$" with only blank lines around it does NOT
            # reliably break out of the preceding bullet list in Pandoc: an
            # unindented block right after a list item can still be swallowed
            # as a lazy-continuation paragraph of that <li> (confirmed by
            # rendering — the equation ended up inside the list item, left-
            # aligned, instead of centred on its own). A fenced div is a real
            # block-level construct and reliably terminates the list, the same
            # way the callout-note div already does further down.
            #
            # A standalone equation is centred whether or not the deck says so
            # in the XML. Lecture 02 centres them properly (m:jc="centerGroup",
            # which `centred` picks up); lecture 03 eyeballs it by typing
            # non-breaking spaces in front of the formula, which survives
            # nowhere. Both are meant to be centred, so `.eq-block` is the
            # default and `centred` only documents which mechanism was used.
            eq = ' \\\\ '.join(p['latex'])
            css_class = '.eq-block'
            div_attrs = (f'{css_class} .fragment fragment-index={f}'
                         if f > 0 else css_class)
            lines.extend(['', f'::: {{{div_attrs}}}', f'$${eq}$$', ':::', ''])
            continue
        if p.get('no_bullet'):
            # Plain text the deck set without a bullet (e.g. a trailing
            # "Referência: ..." line) — no bullet, but not centred either.
            if f > 0:
                text = f'[{text}]{{.fragment fragment-index={f}}}'
            lines.extend(['', f'::: {{.no-bullet}}', text, ':::', ''])
            continue

        if f > 0:
            text = f'[{text}]{{.fragment fragment-index={f}}}'
        # `1.` for every item of a <a:buAutoNum> list: markdown renumbers them
        # on its own, and writing the real number would break if a stage of the
        # reveal starts halfway down the list.
        marker = '1.' if p.get('numbered') else '-'
        # Children have to line up past the parent's marker, which is one
        # column wider for a numbered list. Indenting every level by a flat two
        # spaces puts a sub-bullet of "1. " back at the margin, and Pandoc then
        # closes the ordered list and starts a sibling one.
        pad = indent.get(p['lvl'], '  ' * p['lvl'])
        indent[p['lvl'] + 1] = pad + ' ' * (len(marker) + 1)
        lines.append(pad + f'{marker} {text}')

    title = last['title']
    out = [f'## {title}', '']
    out.extend(lines)

    if figure:
        # The diagram was drawn with native PowerPoint shapes and recovered as
        # SVG; its own text labels are inside the figure, so the loose labels
        # collected above would just be duplicates.
        out += ['', '::: {.diagram}', f'![]({figure})', ':::']
        labels = []
    elif has_lousa:
        out += ['', '::: {.callout-note appearance="simple"}',
                'Diagrama desenhado ao vivo no quadro (LOUSA) — não existe no '
                'PowerPoint original.']
        if labels:
            out.append(f'Rótulos do gráfico: {", ".join(labels)}.')
        out.append(':::')
    elif labels:
        out += ['', f'<!-- Rótulos no slide original: {", ".join(labels)} -->']
    return '\n'.join(out), n_stages, max(
        [f for f in frag_of.values() if f is not None], default=0)


HEADER = '''---
title: "{title}"
subtitle: "EAE1317 — Economia do Meio Ambiente e dos Recursos Naturais"
author: "Rafael Pucci"
date: "{date}"
lang: pt
format:
  revealjs:
    theme: simple
    width: 1280
    height: 720
    margin: 0.08
    slide-number: true
    chalkboard: true
    incremental: false
    css: styles.css
    footer: "EAE1317 — Economia do Meio Ambiente e dos Recursos Naturais"
---
'''


def main(pptx, out_qmd, title, date):
    z = zipfile.ZipFile(pptx)
    nums = sorted(int(re.search(r'(\d+)', n).group(1))
                  for n in z.namelist()
                  if re.match(r'ppt/slides/slide\d+\.xml$', n))
    slides = [parse_slide(z, n) for n in nums]
    body = slides[1:]          # slide 1 is the title slide
    groups = group_slides(body)

    out_dir = os.path.dirname(os.path.abspath(out_qmd))
    stem = os.path.splitext(os.path.basename(out_qmd))[0]
    fig_dir = os.path.join(out_dir, 'figuras')

    chunks = []
    report = []
    for g in groups:
        # Diagrams are drawn with native PowerPoint shapes (Bezier freeforms,
        # ovals, connectors) rather than stored as images, so they're recovered
        # as SVG. Use the last stage of the group: it has the most shapes.
        figure = None
        svg = shapes2svg.render_slide_svg(pptx, g[-1]['num'])
        if svg:
            os.makedirs(fig_dir, exist_ok=True)
            fname = f'{stem}-slide{g[-1]["num"]}.svg'
            with open(os.path.join(fig_dir, fname), 'w', encoding='utf-8') as f:
                f.write(svg)
            figure = f'figuras/{fname}'

        md, n_stages, max_frag = build_group_markdown(g, figure)
        chunks.append(md)
        report.append({'slides': [s['num'] for s in g], 'title': g[-1]['title'],
                       'stages': n_stages, 'fragments': max_frag,
                       'figure': figure})

    with open(out_qmd, 'w', encoding='utf-8') as f:
        f.write(HEADER.format(title=title, date=date) + '\n')
        f.write('\n\n'.join(chunks) + '\n')

    n_figs = sum(1 for r in report if r['figure'])
    print(f'{len(body)} slides -> {len(groups)} Quarto slides, {n_figs} diagramas SVG')
    print(f'{"pptx slides":<14} {"frags":>5} {"fig":>4}  title')
    for r in report:
        rng = (f'{r["slides"][0]}-{r["slides"][-1]}' if len(r['slides']) > 1
               else str(r['slides'][0]))
        mark = ' <-- reveal' if r['fragments'] > 0 else ''
        fig = 'SVG' if r['figure'] else ''
        print(f'{rng:<14} {r["fragments"]:>5} {fig:>4}  {r["title"][:40]}{mark}')


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])
