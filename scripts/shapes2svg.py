"""Render the native PowerPoint vector shapes (freeform Bezier curves, ovals,
triangles, connectors, groups) that make up the hand-drawn-looking diagrams
in this deck (Edgeworth box, supply/demand curves) into a standalone SVG.

These are NOT images anywhere in the pptx -- they are literally DrawingML
shapes (a:custGeom, a:prstGeom, cxnSp) positioned on the slide, the same way
you'd draw them with PowerPoint's shape tools. python-pptx isn't available
here, so this parses the raw XML with the standard library.
"""
import zipfile, re, math, sys, unicodedata
from xml.etree import ElementTree as ET

A_NS = 'http://schemas.openxmlformats.org/drawingml/2006/main'


def ln(t):
    return t.split('}')[-1] if '}' in t else t


def child(e, name):
    for c in e:
        if ln(c.tag) == name:
            return c
    return None


def all_children(e, name):
    return [c for c in e if ln(c.tag) == name]


# --- theme / colour resolution ----------------------------------------------

def load_theme_colors(z, slide_num):
    """clrMap (from the slide's layout->master) composed with clrScheme (from
    the master's theme) -> {'tx1': '000000', 'accent1': '4472C4', ...}"""
    rels = z.read(f'ppt/slides/_rels/slide{slide_num}.xml.rels').decode('utf-8')
    m = re.search(r'Target="\.\./(slideLayouts/slideLayout\d+\.xml)"', rels)
    layout_path = 'ppt/' + m.group(1)
    lrels = z.read(layout_path.replace('slideLayouts/', 'slideLayouts/_rels/') + '.rels').decode('utf-8')
    mm = re.search(r'Target="\.\./(slideMasters/slideMaster\d+\.xml)"', lrels)
    master_path = 'ppt/' + mm.group(1)
    master = ET.fromstring(z.read(master_path))
    clrMap = child(master, 'clrMap')
    mapping = dict(clrMap.attrib) if clrMap is not None else {}

    mrels = z.read(master_path.replace('slideMasters/', 'slideMasters/_rels/') + '.rels').decode('utf-8')
    tm = re.search(r'Target="\.\./(theme/theme\d+\.xml)"', mrels)
    theme_path = 'ppt/' + tm.group(1)
    theme = ET.fromstring(z.read(theme_path))
    clrScheme = None
    for e in theme.iter():
        if ln(e.tag) == 'clrScheme':
            clrScheme = e
            break
    scheme = {}
    for c in clrScheme:
        name = ln(c.tag)
        srgb = child(c, 'srgbClr')
        sysClr = child(c, 'sysClr')
        if srgb is not None:
            scheme[name] = srgb.attrib['val']
        elif sysClr is not None:
            scheme[name] = sysClr.attrib.get('lastClr', '000000')

    # resolve the semantic names (tx1, bg1, tx2, bg2) via clrMap, keep
    # accent1-6/hlink/folHlink as-is
    resolved = dict(scheme)
    for semantic, target in mapping.items():
        if target in scheme:
            resolved[semantic] = scheme[target]
    return resolved


def resolve_color(el, theme, default='000000'):
    """el: an <a:solidFill> (or None). Applies lumMod/lumOff/shade/tint as a
    simple brightness scale -- good enough for recreated-diagram fidelity,
    not colour-managed precision."""
    if el is None:
        return default
    srgb = child(el, 'srgbClr')
    scheme = child(el, 'schemeClr')
    hexval = None
    mods = []
    src = srgb if srgb is not None else scheme
    if srgb is not None:
        hexval = srgb.attrib.get('val', default)
        mods = list(srgb)
    elif scheme is not None:
        name = scheme.attrib.get('val', 'tx1')
        hexval = theme.get(name, default)
        mods = list(scheme)
    else:
        return default
    r, g, b = int(hexval[0:2], 16), int(hexval[2:4], 16), int(hexval[4:6], 16)
    for mod in mods:
        tag = ln(mod.tag)
        val = int(mod.attrib.get('val', '0')) / 100000.0
        if tag == 'shade':      # darken toward black
            r, g, b = r * val, g * val, b * val
        elif tag == 'tint':     # lighten toward white
            r, g, b = r + (255 - r) * (1 - val), g + (255 - g) * (1 - val), b + (255 - b) * (1 - val)
        elif tag == 'lumMod':
            r, g, b = r * val, g * val, b * val
        elif tag == 'lumOff':
            off = val * 255
            r, g, b = r + off, g + off, b + off
    r, g, b = (max(0, min(255, int(round(v)))) for v in (r, g, b))
    return f'{r:02X}{g:02X}{b:02X}'


# --- transforms --------------------------------------------------------------

class Xform:
    """Maps a shape's local path coordinates -> absolute EMU slide coords."""
    def __init__(self, off, ext, rot=0, flipH=False, flipV=False, path_wh=None):
        self.off = off      # (x, y) in parent space
        self.ext = ext      # (cx, cy) actual on-slide box size
        self.rot = rot      # radians
        self.flipH = flipH
        self.flipV = flipV
        self.path_wh = path_wh or ext   # local path's own w/h (for custGeom)

    def point(self, lx, ly):
        pw, ph = self.path_wh
        sx = self.ext[0] / pw if pw else 1
        sy = self.ext[1] / ph if ph else 1
        x = lx * sx
        y = ly * sy
        if self.flipH:
            x = self.ext[0] - x
        if self.flipV:
            y = self.ext[1] - y
        # rotate about the shape's own centre
        cx, cy = self.ext[0] / 2, self.ext[1] / 2
        dx, dy = x - cx, y - cy
        cos_r, sin_r = math.cos(self.rot), math.sin(self.rot)
        rx = dx * cos_r - dy * sin_r
        ry = dx * sin_r + dy * cos_r
        return (self.off[0] + cx + rx, self.off[1] + cy + ry)


def parse_xfrm(spPr_or_grpSpPr):
    xfrm = child(spPr_or_grpSpPr, 'xfrm')
    if xfrm is None:
        return None
    off = child(xfrm, 'off')
    ext = child(xfrm, 'ext')
    rot = int(xfrm.attrib.get('rot', '0')) * math.pi / (180 * 60000)
    flipH = xfrm.attrib.get('flipH') == '1'
    flipV = xfrm.attrib.get('flipV') == '1'
    o = (int(off.attrib['x']), int(off.attrib['y'])) if off is not None else (0, 0)
    e = (int(ext.attrib['cx']), int(ext.attrib['cy'])) if ext is not None else (0, 0)
    chOff = child(xfrm, 'chOff')
    chExt = child(xfrm, 'chExt')
    ch = None
    if chOff is not None and chExt is not None:
        ch = ((int(chOff.attrib['x']), int(chOff.attrib['y'])),
              (int(chExt.attrib['cx']), int(chExt.attrib['cy'])))
    return {'off': o, 'ext': e, 'rot': rot, 'flipH': flipH, 'flipV': flipV, 'ch': ch}


def compose_group(parent_xf, group_xfrm):
    """A child shape's own xfrm off/ext are expressed in the group's *child*
    coordinate space (chOff/chExt), which must be remapped through the
    group's own off/ext before applying the parent transform."""
    if group_xfrm['ch'] is None:
        return group_xfrm
    (chx, chy), (chcx, chcy) = group_xfrm['ch']
    ox, oy = group_xfrm['off']
    ecx, ecy = group_xfrm['ext']
    sx = ecx / chcx if chcx else 1
    sy = ecy / chcy if chcy else 1

    def remap(local_off, local_ext):
        lx, ly = local_off
        lcx, lcy = local_ext
        return ((ox + (lx - chx) * sx, oy + (ly - chy) * sy), (lcx * sx, lcy * sy))
    return remap


# --- path parsing --------------------------------------------------------------

def custgeom_to_svg_path(spPr, xform):
    """Returns (d_string_in_emu, all_vertex_points_in_emu). The point list
    includes bezier control points, not just on-curve points -- a safe
    superset for cropping purposes since control points never fall outside
    the curve's convex hull by much."""
    cg = child(spPr, 'custGeom')
    pathLst = child(cg, 'pathLst')
    path_el = child(pathLst, 'path')
    w = int(path_el.attrib.get('w', xform.path_wh[0]))
    h = int(path_el.attrib.get('h', xform.path_wh[1]))
    xform.path_wh = (w, h)
    d = []
    all_pts = []
    for cmd in path_el:
        tag = ln(cmd.tag)
        pts = [child_pt for child_pt in cmd if ln(child_pt.tag) == 'pt']
        coords = [xform.point(int(p.attrib['x']), int(p.attrib['y'])) for p in pts]
        all_pts.extend(coords)
        if tag == 'moveTo':
            x, y = coords[0]
            d.append(f'M {x:.1f} {y:.1f}')
        elif tag == 'lnTo':
            x, y = coords[0]
            d.append(f'L {x:.1f} {y:.1f}')
        elif tag == 'cubicBezTo':
            (x1, y1), (x2, y2), (x, y) = coords
            d.append(f'C {x1:.1f} {y1:.1f} {x2:.1f} {y2:.1f} {x:.1f} {y:.1f}')
        elif tag == 'quadBezTo':
            (x1, y1), (x, y) = coords
            d.append(f'Q {x1:.1f} {y1:.1f} {x:.1f} {y:.1f}')
        elif tag == 'close':
            d.append('Z')
    return ' '.join(d), all_pts


def prstgeom_ellipse(xform):
    (x0, y0) = xform.point(0, 0)
    (x1, y1) = xform.point(xform.path_wh[0], xform.path_wh[1])
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    rx, ry = abs(x1 - x0) / 2, abs(y1 - y0) / 2
    return cx, cy, rx, ry


def prstgeom_arc(spPr, xform):
    """PowerPoint 'arc' preset: an elliptical arc from adj1 to adj2 (angles in
    60,000ths of a degree, 0=3 o'clock, clockwise) inscribed in the shape's
    bounding box. Rendered as an SVG elliptical-arc path.

    An 'arc' is an open curve: PowerPoint ignores the theme fill for it, so any
    fillRef from <p:style> must be dropped or the chart gets a huge coloured
    wedge behind it.
    """
    pg = child(spPr, 'prstGeom')
    avLst = child(pg, 'avLst')
    adj = {g.attrib['name']: int(g.attrib['fmla'].split()[-1]) for g in (avLst or [])}
    a1 = adj.get('adj1', 0) / 60000.0
    a2 = adj.get('adj2', 5400000) / 60000.0
    w, h = xform.path_wh
    cx0, cy0 = w / 2, h / 2
    rx0, ry0 = w / 2, h / 2

    def ellipse_pt(deg):
        r = math.radians(deg)
        return cx0 + rx0 * math.cos(r), cy0 + ry0 * math.sin(r)

    sx, sy = ellipse_pt(a1)
    ex, ey = ellipse_pt(a2)
    p_start = xform.point(sx, sy)
    p_end = xform.point(ex, ey)
    # scaled radii in output space
    (ox0, oy0) = xform.point(0, 0)
    (ox1, oy1) = xform.point(w, h)
    out_rx, out_ry = abs(ox1 - ox0) / 2, abs(oy1 - oy0) / 2
    sweep = 1 if a2 > a1 else 0
    large_arc = 1 if abs(a2 - a1) > 180 else 0
    d = (f'M {p_start[0]:.1f} {p_start[1]:.1f} '
         f'A {out_rx:.1f} {out_ry:.1f} 0 {large_arc} {sweep} '
         f'{p_end[0]:.1f} {p_end[1]:.1f}')
    # Tight bbox: always include the endpoints, plus any of the ellipse's own
    # cardinal extrema (top/right/bottom/left) the sweep actually passes
    # through. Earlier this used all 4 corners of the *full* ellipse's
    # bounding box "to be safe" -- correct for a full ellipse, but a wedge
    # like this deck's supply/demand arc only sweeps 90 degrees of it, so
    # that padding dragged in a huge blank margin never touched by any ink,
    # and the crop (hence the rendered image) was mostly empty canvas.
    span = (a2 - a1) % 360 or 360
    pts = [p_start, p_end]
    for cardinal in (0, 90, 180, 270):
        if (cardinal - a1) % 360 <= span:
            cx, cy = ellipse_pt(cardinal)
            pts.append(xform.point(cx, cy))
    return d, pts


def prstgeom_triangle(xform):
    p0 = xform.point(xform.path_wh[0] / 2, 0)
    p1 = xform.point(xform.path_wh[0], xform.path_wh[1])
    p2 = xform.point(0, xform.path_wh[1])
    return [p0, p1, p2]


EMU_PER_PX = 9525.0   # 96 dpi; 12192000/9525 = 1280, 6858000/9525 = 720


def shape_text(sp):
    """Plain-text label for a shape, flattening any embedded OMML equation.

    Axis labels here are often real equations (e.g. -p_x/p_y), whose letters
    live in the Unicode math-italic block; NFKD brings them back to ASCII, and
    fractions are flattened to num/den since SVG has no math layout.
    """
    txBody = child(sp, 'txBody')
    if txBody is None:
        return ''

    def render(el):
        tag = ln(el.tag)
        if tag == 'f':                       # fraction
            num, den = child(el, 'num'), child(el, 'den')
            return (f'{render(num) if num is not None else ""}/'
                    f'{render(den) if den is not None else ""}')
        if tag == 'sSub':
            e, sub = child(el, 'e'), child(el, 'sub')
            return ((render(e) if e is not None else '') +
                    (render(sub) if sub is not None else ''))
        if tag == 'sSup':
            e, sup = child(el, 'e'), child(el, 'sup')
            return ((render(e) if e is not None else '') +
                    (render(sup) if sup is not None else ''))
        if tag == 't':
            return el.text or ''
        return ''.join(render(c) for c in el)

    parts = []
    for p in txBody:
        if ln(p.tag) != 'p':
            continue
        for node in p:
            ntag = ln(node.tag)
            if ntag == 'r' and node.tag.startswith('{' + A_NS):
                t = child(node, 't')
                if t is not None and t.text:
                    parts.append(t.text)
            elif ntag in ('pPr', 'endParaRPr'):
                continue
            else:
                parts.append(render(node))
    text = unicodedata.normalize('NFKD', ''.join(parts)).strip()
    return re.sub(r'\s+', ' ', text)


def px(emu_xy):
    return emu_xy[0] / EMU_PER_PX, emu_xy[1] / EMU_PER_PX


# OOXML preset dash styles -> SVG stroke-dasharray (values scaled to a ~1-2px
# stroke; PowerPoint defines these relative to line width, this is a simple
# fixed approximation which is plenty for a recreated diagram).
PRST_DASH = {
    'dot': '2,2', 'sysDot': '2,2',
    'dash': '6,3', 'sysDash': '5,3',
    'lgDash': '10,4',
    'dashDot': '6,3,2,3', 'sysDashDot': '5,3,2,3',
    'lgDashDot': '10,4,2,4',
    'lgDashDotDot': '10,4,2,4,2,4',
    'sysDashDotDot': '5,3,2,3,2,3',
}


def shape_style(sp, theme, default_stroke='000000', default_fill=None):
    spPr = child(sp, 'spPr')
    fill = default_fill
    stroke = None
    stroke_w = 1.0
    dash = None
    if spPr is not None:
        if child(spPr, 'noFill') is not None:
            fill = 'none'
        else:
            sf = child(spPr, 'solidFill')
            if sf is not None:
                fill = '#' + resolve_color(sf, theme)
        ln_el = child(spPr, 'ln')
        if ln_el is not None:
            if child(ln_el, 'noFill') is not None:
                stroke = 'none'
            else:
                lf = child(ln_el, 'solidFill')
                if lf is not None:
                    stroke = '#' + resolve_color(lf, theme, default_stroke)
                w = ln_el.attrib.get('w')
                if w:
                    stroke_w = max(0.75, int(w) / EMU_PER_PX)
            pd = child(ln_el, 'prstDash')
            if pd is not None:
                dash = PRST_DASH.get(pd.attrib.get('val'))
    # fall back to the shape's <p:style> refs when spPr didn't say
    style = child(sp, 'style')
    if style is not None:
        if fill is None:
            fRef = child(style, 'fillRef')
            if fRef is not None:
                sc = child(fRef, 'schemeClr')
                if sc is not None:
                    fill = '#' + resolve_color(fRef, theme)
        if stroke is None:
            lRef = child(style, 'lnRef')
            if lRef is not None:
                stroke = '#' + resolve_color(lRef, theme, default_stroke)
    if fill is None:
        fill = 'none'
    if stroke is None:
        stroke = 'none'
    return fill, stroke, stroke_w, dash


def has_arrow(spPr, end):
    ln_el = child(spPr, 'ln') if spPr is not None else None
    if ln_el is None:
        return False
    e = child(ln_el, end)
    return e is not None and e.attrib.get('type', 'none') != 'none'


def walk(elem, theme, xf_stack, out, group_remap_stack):
    """xf_stack holds Xform-building info accumulated from ancestor groups:
    a list of (off, ext, rot, flipH, flipV) already composed down to this
    element's *parent* space. group_remap_stack holds the chOff/chExt remap
    functions still pending for direct children of a group."""
    for c in elem:
        tag = ln(c.tag)
        if tag == 'AlternateContent':
            ch = child(c, 'Choice')
            if ch is not None:
                walk(ch, theme, xf_stack, out, group_remap_stack)
            continue
        if tag == 'grpSp':
            grpSpPr = child(c, 'grpSpPr')
            gx = parse_xfrm(grpSpPr)
            if gx is None:
                walk(c, theme, xf_stack, out, group_remap_stack)
                continue
            remap = compose_group(None, gx)
            new_stack = xf_stack + [(gx['off'], gx['ext'], gx['rot'], gx['flipH'], gx['flipV'])]
            walk(c, theme, new_stack, out, group_remap_stack + [remap] if callable(remap) else group_remap_stack)
            continue
        if tag in ('sp', 'cxnSp', 'pic'):
            render_leaf(c, tag, theme, xf_stack, group_remap_stack, out)


def resolve_local_xfrm(sp, tag, group_remap_stack):
    spPr = child(sp, 'nvCxnSpPr' if tag == 'cxnSp' else ('spPr' if tag == 'sp' else 'spPr'))
    spPr = child(sp, 'spPr')
    x = parse_xfrm(spPr) if spPr is not None else None
    if x is None:
        return None, None
    off, ext = x['off'], x['ext']
    for remap in reversed(group_remap_stack):
        off, ext = remap(off, ext)
    return {'off': off, 'ext': ext, 'rot': x['rot'], 'flipH': x['flipH'], 'flipV': x['flipV']}, spPr


def render_leaf(sp, tag, theme, xf_stack, group_remap_stack, out):
    local, spPr = resolve_local_xfrm(sp, tag, group_remap_stack)
    if local is None or spPr is None:
        return
    xform = Xform(local['off'], local['ext'], local['rot'], local['flipH'], local['flipV'])

    pg = child(spPr, 'prstGeom')
    cg = child(spPr, 'custGeom')
    geom = pg.attrib.get('prst') if pg is not None else ('custGeom' if cg is not None else None)
    fill, stroke, stroke_w, dash = shape_style(sp, theme)
    dash_attr = f' stroke-dasharray="{dash}"' if dash else ''

    text = shape_text(sp)

    # skip invisible hitbox/container rectangles (no fill, no stroke, no text).
    # Careful: a rect with noFill can still be a *visible* outline when its
    # stroke comes from <p:style><a:lnRef> — that's the Edgeworth box — so this
    # must run after shape_style() has consulted the style refs.
    if geom == 'rect' and fill == 'none' and stroke == 'none' and not text:
        return

    # skip the reveal masks: a rectangle filled with the background colour,
    # parked over the text that must not show yet (see pptx2qmd). It is
    # invisible on a white slide by construction, and rendering it produced an
    # all-white "diagram" for three slides of lecture 03.
    if (geom in ('rect', 'roundRect') and not text
            and fill.upper() == '#FFFFFF'
            and stroke.upper() in ('NONE', '#FFFFFF')):
        return

    if text:
        x0, y0 = px(xform.point(0, 0))
        x1, y1 = px(xform.point(local['ext'][0], local['ext'][1]))
        tx, ty = min(x0, x1), (y0 + y1) / 2 + 5
        out.append((f'<text x="{tx:.1f}" y="{ty:.1f}" font-size="15" '
                    f'font-style="italic" fill="#000000">{text}</text>',
                    [(tx, ty)]))
        return

    if geom == 'custGeom':
        d, pts_emu = custgeom_to_svg_path(spPr, xform)
        d_px = _scale_path_to_px(d)
        pts_px = [(x / EMU_PER_PX, y / EMU_PER_PX) for x, y in pts_emu]
        out.append((f'<path d="{d_px}" fill="{fill}" stroke="{stroke}" '
                    f'stroke-width="{stroke_w:.2f}"{dash_attr}/>', pts_px))
    elif geom == 'ellipse':
        cx, cy, rx, ry = prstgeom_ellipse(xform)
        cx, cy, rx, ry = cx/EMU_PER_PX, cy/EMU_PER_PX, rx/EMU_PER_PX, ry/EMU_PER_PX
        out.append((f'<ellipse cx="{cx:.1f}" cy="{cy:.1f}" rx="{rx:.1f}" ry="{ry:.1f}" '
                    f'fill="{fill}" stroke="{stroke}" stroke-width="{stroke_w:.2f}"/>',
                    [(cx-rx, cy-ry), (cx+rx, cy+ry)]))
    elif geom == 'triangle':
        pts = prstgeom_triangle(xform)
        pts_px_t = [(x/EMU_PER_PX, y/EMU_PER_PX) for x, y in pts]
        pts_str = ' '.join(f'{x:.1f},{y:.1f}' for x, y in pts_px_t)
        out.append((f'<polygon points="{pts_str}" fill="{fill}"/>', pts_px_t))
    elif geom in ('rect', 'roundRect'):
        # e.g. the Edgeworth box itself: noFill, and its outline comes from
        # <p:style><a:lnRef> rather than an explicit <a:ln>.
        corners = [xform.point(0, 0), xform.point(local['ext'][0], 0),
                   xform.point(local['ext'][0], local['ext'][1]),
                   xform.point(0, local['ext'][1])]
        pts_px_c = [(x/EMU_PER_PX, y/EMU_PER_PX) for x, y in corners]
        pts_str = ' '.join(f'{x:.1f},{y:.1f}' for x, y in pts_px_c)
        out.append((f'<polygon points="{pts_str}" fill="{fill}" stroke="{stroke}" '
                    f'stroke-width="{stroke_w:.2f}"/>', pts_px_c))
    elif geom == 'arc':
        d, pts_emu = prstgeom_arc(spPr, xform)
        d_px = _scale_path_to_px(d)
        pts_px = [(x / EMU_PER_PX, y / EMU_PER_PX) for x, y in pts_emu]
        out.append((f'<path d="{d_px}" fill="none" stroke="{stroke}" '
                    f'stroke-width="{stroke_w:.2f}"{dash_attr}/>', pts_px))
    elif geom in ('line', 'straightConnector1'):
        (x0, y0) = xform.point(0, 0)
        (x1, y1) = xform.point(local['ext'][0], local['ext'][1])
        x0, y0, x1, y1 = x0/EMU_PER_PX, y0/EMU_PER_PX, x1/EMU_PER_PX, y1/EMU_PER_PX
        marker = ''
        if has_arrow(spPr, 'tailEnd') or has_arrow(spPr, 'headEnd'):
            marker = ' marker-end="url(#arrow)"'
        out.append((f'<line x1="{x0:.1f}" y1="{y0:.1f}" x2="{x1:.1f}" y2="{y1:.1f}" '
                    f'stroke="{stroke if stroke != "none" else "#000000"}" '
                    f'stroke-width="{stroke_w:.2f}"{dash_attr}{marker}/>',
                    [(x0, y0), (x1, y1)]))


def _scale_path_to_px(d):
    """Convert a path built in EMU coordinates to px.

    Careful with the elliptical-arc command: "A rx ry rot large-arc sweep x y"
    has three *flags* in the middle that are not lengths. Scaling them (as a
    naive number-substitution does) turns sweep=1 into 0.0001, which SVG reads
    as 0 and silently flips the arc's direction.
    """
    out = []
    for token in d.split(' '):
        out.append(token)
    result = []
    i = 0
    tokens = d.split(' ')
    while i < len(tokens):
        tok = tokens[i]
        if tok == 'A':
            # rx ry rot large-arc sweep x y  -> scale all but the 3 flags
            rx, ry, rot, laf, sf, x, y = tokens[i + 1:i + 8]
            result.append('A')
            result.append(f'{float(rx) / EMU_PER_PX:.2f}')
            result.append(f'{float(ry) / EMU_PER_PX:.2f}')
            result.append(rot)
            result.append(laf)
            result.append(sf)
            result.append(f'{float(x) / EMU_PER_PX:.2f}')
            result.append(f'{float(y) / EMU_PER_PX:.2f}')
            i += 8
            continue
        if re.fullmatch(r'-?\d+\.?\d*', tok):
            result.append(f'{float(tok) / EMU_PER_PX:.2f}')
        else:
            result.append(tok)
        i += 1
    return ' '.join(result)


NUM_RE = re.compile(r'-?\d+\.?\d*')


def content_bbox(elements):
    """Bounding box of the drawn elements, so the SVG can be cropped to the
    diagram instead of carrying the whole 1280x720 slide (most of which is the
    empty area where the slide's title and bullets live).

    Each element carries the points that produced it (recorded during
    rendering). Re-parsing the emitted `d=""` string instead would be wrong:
    an SVG arc command is `A rx ry rotation large-arc-flag sweep-flag x y`, so
    naively pairing up its numbers turns the two 0/1 flags into a phantom point
    near the origin and stretches the crop back to the top-left corner.
    """
    xs, ys = [], []
    for _svg, pts in elements:
        for (x, y) in pts:
            xs.append(x)
            ys.append(y)
    if not xs:
        return (0, 0, 1280, 720)
    return (min(xs), min(ys), max(xs), max(ys))


def is_diagram(elements):
    """True when what was recovered is a drawing and not slide decoration.

    Not every slide with loose shapes has a graph on it. The other things
    authors park on a slide are annotations anchored to the text: a couple of
    red curly braces under an equation, a circle around one term, a floating
    caption. Cropped out of the slide and dropped into `::: {.diagram}` those
    become meaningless — two red ellipses on their own, or a line of text
    rendered as a picture. They belong in the markup instead (`\\underbrace`
    for the braces, prose for the captions).

    A real diagram is drawn with strokes: axes, curves, connectors. Every
    diagram recovered from lecture 02 has at least three <path>/<line>
    elements; every false positive in lecture 03 has none.
    """
    strokes = sum(1 for svg_str, _pts in elements
                  if svg_str.startswith(('<path', '<line')))
    return strokes >= 2


def render_slide_svg(pptx_path, slide_num, shape_names=None):
    """shape_names: optional whitelist of top-level shape names to include
    (skips Title/Content Placeholder/slide number automatically either way)."""
    z = zipfile.ZipFile(pptx_path)
    theme = load_theme_colors(z, slide_num)
    root = ET.fromstring(z.read(f'ppt/slides/slide{slide_num}.xml'))
    spTree = None
    for e in root.iter():
        if ln(e.tag) == 'spTree':
            spTree = e
            break

    out = []
    SKIP_NAME_RE = re.compile(r'^(Title|Content Placeholder|Espaço Reservado)')
    filtered = ET.Element('root')
    for c in spTree:
        tag = ln(c.tag)
        target = c
        if tag == 'AlternateContent':
            ch = child(c, 'Choice')
            target = ch if ch is not None else None
            if target is None:
                continue
            inner = list(target)
            for ic in inner:
                itag = ln(ic.tag)
                if itag not in ('sp', 'cxnSp', 'pic', 'grpSp'):
                    continue
                nv = child(ic, 'nvSpPr') or child(ic, 'nvCxnSpPr') or child(ic, 'nvGrpSpPr') or child(ic, 'nvPicPr')
                cNvPr = child(nv, 'cNvPr') if nv is not None else None
                name = cNvPr.attrib.get('name', '') if cNvPr is not None else ''
                if SKIP_NAME_RE.match(name):
                    continue
                filtered.append(ic)
            continue
        if tag not in ('sp', 'cxnSp', 'pic', 'grpSp'):
            continue
        nv = child(c, 'nvSpPr') or child(c, 'nvCxnSpPr') or child(c, 'nvGrpSpPr') or child(c, 'nvPicPr')
        cNvPr = child(nv, 'cNvPr') if nv is not None else None
        name = cNvPr.attrib.get('name', '') if cNvPr is not None else ''
        if SKIP_NAME_RE.match(name):
            continue
        filtered.append(c)

    walk(filtered, theme, [], out, [])

    if not out or not is_diagram(out):
        return None

    pad = 14
    x0, y0, x1, y1 = content_bbox(out)
    vx, vy = x0 - pad, y0 - pad
    vw, vh = (x1 - x0) + 2 * pad, (y1 - y0) + 2 * pad

    body = '\n  '.join(svg_str for svg_str, _pts in out)
    # width/height as well as viewBox: without them the browser falls back to a
    # 150px-tall default intrinsic size, which makes the figure tiny.
    svg = f'''<svg width="{vw:.0f}" height="{vh:.0f}"
     viewBox="{vx:.1f} {vy:.1f} {vw:.1f} {vh:.1f}"
     xmlns="http://www.w3.org/2000/svg" role="img">
  <defs>
    <marker id="arrow" markerWidth="8" markerHeight="8" refX="4" refY="4" orient="auto">
      <path d="M0,0 L8,4 L0,8 Z" fill="#000000"/>
    </marker>
  </defs>
  {body}
</svg>'''
    return svg


if __name__ == '__main__':
    pptx, num, out_path = sys.argv[1], sys.argv[2], sys.argv[3]
    svg = render_slide_svg(pptx, num)
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(svg)
    print('wrote', out_path)
