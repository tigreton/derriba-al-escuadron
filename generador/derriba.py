"""Generador de bocetos 'Derriba al escuadrón' (lámina 139x139 mm, máx. 3 mm).

Saca, para cada diseño, un SVG a escala 1:1 (mm) y otro anotado.
Uso:  python derriba.py [carpeta_widgets]
"""
import math, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WIDGET_DIR = sys.argv[1] if len(sys.argv) > 1 else None

SIZE = 139.0
DISC, DISC_RING = "#E24B4A", "#FCEBEB"
BADGE_TXT = "#0C447C"
TAB_W = 1.5

THEMES = {
    "mar": dict(base="#378ADD", edge="#185FA5", relief="#E6F1FB", deco="#B5D4F4"),
    "radar": dict(base="#0F6E56", edge="#085041", relief="#E1F5EE", deco="#5DCAA5"),
    "cielo": dict(base="#85B7EB", edge="#378ADD", relief="#F4F9FE", deco="#F4F9FE"),
}


def f(v):
    s = f"{v:.2f}".rstrip("0").rstrip(".")
    return "0" if s == "-0" else s


def rot(p, cx, cy, ang):
    a = math.radians(ang)
    x, y = p
    return (cx + x * math.cos(a) - y * math.sin(a), cy + x * math.sin(a) + y * math.cos(a))


# ---------------- siluetas (coords locales, origen = centro de la diana) ----------------
def hull_ship(L, W):
    h, w = L / 2, W / 2
    b = min(L * 0.22, 1.5 * W)
    r = min(1.5, w * 0.4)
    return [("M", (-h + r, -w)), ("L", (h - b, -w)), ("Q", (h - b * 0.25, -w), (h, 0)),
            ("Q", (h - b * 0.25, w), (h - b, w)), ("L", (-h + r, w)), ("Q", (-h, w), (-h, w - r)),
            ("L", (-h, -w + r)), ("Q", (-h, -w), (-h + r, -w)), ("Z",)]


def hull_sub(L, W):
    h, w = L / 2, W / 2
    return [("M", (-h + w, -w)), ("L", (h - w, -w)), ("A", w, 1, (h - w, w)),
            ("L", (-h + w, w)), ("A", w, 1, (-h + w, -w)), ("Z",)]


def hull_carrier_small(L, W):
    h, w = L / 2, W / 2
    return [("M", (-h + 1, -w)), ("L", (h - 3.5, -w)), ("L", (h, -w + 2.5)), ("L", (h, w - 2.5)),
            ("L", (h - 3.5, w)), ("L", (-h + 1, w)), ("L", (-h, w - 1)), ("L", (-h, -w + 1)), ("Z",)]


def hull_carrier_big(L, W):
    h = L / 2
    pts = [(-h, -0.30 * W), (-0.5 * h, -0.30 * W), (-0.3 * h, -0.5 * W), (0.45 * h, -0.5 * W),
           (h, -0.18 * W), (h, 0.12 * W), (0.8 * h, 0.36 * W), (-h + 2, 0.36 * W), (-h, 0.30 * W)]
    return [("M", pts[0])] + [("L", p) for p in pts[1:]] + [("Z",)]


def plane(S, nose, tail_end, fw, cr, ct, sweep, ts=0.0, tc=0.0, tsw=0.0):
    """Avión visto desde arriba, morro hacia -y. Origen en la raíz del ala (centro de la diana)."""
    hw = fw / 2
    k = min(nose * 0.45, 2.2 * fw)
    right = [(hw, -cr / 2), (S / 2, -cr / 2 + sweep), (S / 2, -cr / 2 + sweep + ct), (hw, cr / 2)]
    if ts > 0:
        right += [(hw * 0.8, tail_end - tc), (ts / 2, tail_end - tc + tsw), (ts / 2, tail_end), (hw * 0.5, tail_end)]
    else:
        right += [(hw * 0.6, tail_end)]
    cmds = [("M", (0, -nose)), ("Q", (hw, -nose), (hw, -nose + k))]
    cmds += [("L", p) for p in right]
    cmds += [("L", (-x, y)) for (x, y) in reversed(right)]
    cmds += [("L", (-hw, -nose + k)), ("Q", (-hw, -nose), (0, -nose)), ("Z",)]
    return cmds


def path_d(cmds, cx, cy, ang, k, ox, oy):
    out = []
    for c in cmds:
        op = c[0]
        if op == "Z":
            out.append("Z")
        elif op == "A":
            r, sweep, pt = c[1], c[2], c[3]
            X, Y = rot(pt, cx, cy, ang)
            out.append(f"A{f(r * k)} {f(r * k)} 0 0 {sweep} {f(ox + X * k)} {f(oy + Y * k)}")
        else:
            pts = [rot(p, cx, cy, ang) for p in c[1:]]
            out.append(op + " ".join(f"{f(ox + X * k)} {f(oy + Y * k)}" for X, Y in pts))
    return "".join(out)


def outline_pts(cmds):
    return [c[-1] for c in cmds if c[0] != "Z"]


def closest(p, a, b):
    ax, ay = a; bx, by = b; px, py = p
    dx, dy = bx - ax, by - ay
    t = max(0, min(1, ((px - ax) * dx + (py - ay) * dy) / (dx * dx + dy * dy or 1)))
    q = (ax + t * dx, ay + t * dy)
    return math.hypot(px - q[0], py - q[1]), q


def seg_dist(p, a, b):
    return closest(p, a, b)[0]


class Target:
    def __init__(self, name, cmds, cx, cy, ang, disc_d, disc_off=(0, 0), pts=None, badge=None):
        self.name, self.cmds, self.cx, self.cy, self.ang = name, cmds, cx, cy, ang
        self.disc_d, self.disc_off = disc_d, disc_off
        self.pts, self.badge = pts, badge
        # la pestaña va al punto del contorno más cercano a la diana
        P = outline_pts(cmds)
        best = min((closest(disc_off, P[i], P[(i + 1) % len(P)]) for i in range(len(P))), key=lambda c: c[0])
        d, (qx, qy) = best
        self.tab_dir = ((qx - disc_off[0]) / d, (qy - disc_off[1]) / d)
        self.tab_end = d

    def disc_c(self):
        return rot(self.disc_off, self.cx, self.cy, self.ang)

    def gap(self):
        P = outline_pts(self.cmds)
        return min(seg_dist(self.disc_off, P[i], P[(i + 1) % len(P)]) for i in range(len(P))) - self.disc_d / 2


def ship(name, shape, L, W, d, cx, cy, ang, disc_off=(0, 0), **kw):
    return Target(name, shape(L, W), cx, cy, ang, d, disc_off, **kw)


def plane_target(name, d, cx, cy, ang, **p):
    return Target(name, plane(**p), cx, cy, ang, d)


# ---------------- diseños ----------------
CELL, G0 = 12.0, 13.0


def cell_c(col, row):
    return G0 + (col + 0.5) * CELL, G0 + (row + 0.5) * CELL


def grid_ship(name, shape, n, c0, r0, vertical, bow_sign=1):
    L = n * CELL - 2
    if vertical:
        cx, cy = G0 + (c0 + 0.5) * CELL, G0 + r0 * CELL + n * CELL / 2
        ang = -90 if bow_sign > 0 else 90
    else:
        cx, cy = G0 + c0 * CELL + n * CELL / 2, G0 + (r0 + 0.5) * CELL
        ang = 0 if bow_sign > 0 else 180
    return ship(name, shape, L, 10.6, 8.0, cx, cy, ang)


BOMBER_GRID = dict(S=58, nose=17, tail_end=29, fw=10, cr=10.6, ct=6, sweep=2, ts=34, tc=8, tsw=1.5)
FIGHTER_GRID = dict(S=34, nose=17, tail_end=17, fw=9, cr=10.6, ct=4, sweep=5, ts=16, tc=6, tsw=1.5)

CW = 22.0
DESIGNS = {
    "barcos-A": dict(
        theme="mar", grid=True, coords=True, frame=False, deco=None,
        title="Boceto A: tablero clásico",
        desc="Lámina de 139 mm con cuadrícula 10x10 y cinco barcos huecos alineados, cada uno con una diana central sujeta por una pestaña.",
        targets=[
            grid_ship("Portaaviones", hull_carrier_small, 5, 1, 1, False),
            grid_ship("Acorazado", hull_ship, 4, 8, 1, True),
            grid_ship("Crucero", hull_ship, 3, 3, 6, False, -1),
            grid_ship("Submarino", hull_sub, 3, 1, 5, True),
            grid_ship("Destructor", hull_ship, 2, 7, 8, False),
        ],
        labels=[
            (127, 10.5, 52, "Coordenadas", "A–J y 1–10 en relieve"),
            (115, 36, 132, "Barco hueco", "pasante, con borde"),
            (115, 49, 200, "Diana Ø8 mm", "sujeta con 1 pestaña"),
            (133, 97, 290, "Cuadrícula 12 mm", "relieve +0,8 mm"),
            (127, 115, 376, "Agua", "PETG, base 2 mm"),
        ]),
    "barcos-B": dict(
        theme="mar", grid=False, coords=False, frame=True, deco="olas",
        title="Boceto B: escuadra con puntos",
        desc="Lámina de 139 mm con olas en relieve y cinco barcos grandes en ángulos libres; cuanto más pequeño el barco, más pequeña la diana y más puntos vale.",
        targets=[
            ship("Portaaviones", hull_carrier_big, 78, CW, 14, 70, 27, -7, disc_off=(0, -0.07 * CW),
                 pts=1, badge=(124, 13)),
            ship("Acorazado", hull_ship, 64, 16, 11, 38, 84, 58, pts=2, badge=(55, 70)),
            ship("Crucero", hull_ship, 54, 14, 9, 101, 66, -32, pts=3, badge=(125, 85)),
            ship("Submarino", hull_sub, 46, 11, 7, 96, 113, 6, pts=4, badge=(128, 113)),
            ship("Destructor", hull_ship, 38, 10, 6, 40, 126, -4, pts=5, badge=(13, 125)),
        ],
        labels=[
            (137.5, 30, 52, "Marco en relieve", "3 mm de ancho"),
            (99, 23.4, 130, "Portaaviones", "diana Ø14 · 1 punto"),
            (128.6, 85, 210, "Puntos en relieve", "más pequeño, más vale"),
            (131, 98, 290, "Olas +0,6 mm", "textura en el agua"),
            (53, 125.1, 400, "Destructor", "diana Ø6 · 5 puntos"),
        ]),
    "aviones-A": dict(
        theme="radar", grid=True, coords=True, frame=False, deco="radar",
        title="Boceto A aviones: pantalla de radar",
        desc="Lámina de 139 mm tipo radar con cuadrícula 10x10 y cuatro aviones huecos encajados en casillas, cada uno con una diana Ø10 en el cruce de ala y fuselaje.",
        targets=[
            plane_target("Bombardero 1", 10, *cell_c(2, 1), 0, **BOMBER_GRID),
            plane_target("Bombardero 2", 10, *cell_c(7, 3), -90, **BOMBER_GRID),
            plane_target("Caza 1", 10, *cell_c(2, 7), 180, **FIGHTER_GRID),
            plane_target("Caza 2", 10, *cell_c(7, 8), 90, **FIGHTER_GRID),
        ],
        labels=[
            (127, 10.5, 52, "Coordenadas", "A–J y 1–10 en relieve"),
            (103, 33, 132, "Avión hueco", "pasante, con borde"),
            (103, 55, 200, "Diana Ø10 mm", "pestaña en diagonal"),
            (133, 85, 290, "Radar en relieve", "cuadrícula y anillos"),
            (127, 128, 376, "Cielo", "PETG, base 2 mm"),
        ]),
    "aviones-B": dict(
        theme="cielo", grid=False, coords=False, frame=True, deco="nubes",
        title="Boceto B aviones: escuadrón con puntos",
        desc="Lámina de 139 mm con nubes en relieve y cinco aviones de tamaños distintos en vuelo; cuanto más pequeño el avión, más pequeña la diana y más puntos vale.",
        targets=[],  # se rellena abajo
        labels=[],
    ),
}

AB = DESIGNS["aviones-B"]
AB["targets"] = [
    Target("Bombardero", plane(S=70, nose=20, tail_end=28, fw=12, cr=16, ct=8, sweep=3, ts=28, tc=8, tsw=2),
           48, 56, 45, 14, pts=1, badge=(78, 58)),
    Target("Transporte", plane(S=56, nose=16, tail_end=24, fw=10, cr=13, ct=7, sweep=2, ts=22, tc=7, tsw=1.5),
           106, 96, 0, 11, pts=2, badge=(129, 112)),
    Target("Caza", plane(S=44, nose=18, tail_end=22, fw=8, cr=14, ct=5, sweep=11, ts=18, tc=6, tsw=3),
           108, 30, 90, 9, pts=3, badge=(127, 12)),
    Target("Reactor delta", plane(S=34, nose=15, tail_end=13, fw=6, cr=24, ct=2.5, sweep=21.5),
           28, 112, 30, 7, pts=4, badge=(12, 92)),
    Target("Avioneta", plane(S=30, nose=9, tail_end=14, fw=6, cr=8, ct=5, sweep=0.5, ts=12, tc=4, tsw=0.5),
           66, 118, -20, 6, pts=5, badge=(88, 126)),
]
AB["labels"] = [
    (137.5, 45, 52, "Marco en relieve", "3 mm de ancho"),
    (56.5, 47.5, 130, "Bombardero", "diana Ø14 · 1 punto"),
    (124, 60, 210, "Nubes +0,6 mm", "textura del cielo"),
    (132.6, 112, 300, "Puntos en relieve", "más pequeño, más vale"),
    (75, 115, 400, "Avioneta", "diana Ø6 · 5 puntos"),
]

CLOUDS = [  # (x, y, escala) en mm
    (18, 16, 0.8), (60, 13, 0.8), (124, 62, 0.7), (86, 72, 0.7), (106, 130, 0.8), (12, 70, 0.6),
]


def cloud(x, y, s, k, ox, oy, fill, stroke):
    P = lambda a, b: (ox + (x + a * s) * k, oy + (y + b * s) * k)
    parts = []
    for (a, b, r) in [(-6, 0, 4), (-1, -2.5, 5.5), (5, -1, 4.5), (9, 1, 3)]:
        cx, cy = P(a, b)
        parts.append(f'<circle cx="{f(cx)}" cy="{f(cy)}" r="{f(r * s * k)}"/>')
    x0, y0 = P(-10, 0)
    parts.append(f'<rect x="{f(x0)}" y="{f(y0)}" width="{f(22 * s * k)}" height="{f(4 * s * k)}" rx="{f(2 * s * k)}"/>')
    return f'<g fill="{fill}" stroke="{stroke}" stroke-width="{f(0.15 * k)}">' + "".join(parts) + "</g>"


def tab_poly(t, k, ox, oy):
    (ux, uy), (dx, dy) = t.tab_dir, t.disc_off
    vx, vy = -uy, ux
    r = t.disc_d / 2
    a, b = r - 0.3, t.tab_end + 0.35
    loc = [(dx + ux * a + vx * TAB_W / 2, dy + uy * a + vy * TAB_W / 2), (dx + ux * b + vx * TAB_W / 2, dy + uy * b + vy * TAB_W / 2),
           (dx + ux * b - vx * TAB_W / 2, dy + uy * b - vy * TAB_W / 2), (dx + ux * a - vx * TAB_W / 2, dy + uy * a - vy * TAB_W / 2)]
    P = [rot(p, t.cx, t.cy, t.ang) for p in loc]
    return "M" + "L".join(f"{f(ox + X * k)} {f(oy + Y * k)}" for X, Y in P) + "Z"


def plate_path(k, ox, oy, rr=4.0):
    s, r = SIZE * k, rr * k
    return (f"M{f(ox + r)} {f(oy)}H{f(ox + s - r)}A{f(r)} {f(r)} 0 0 1 {f(ox + s)} {f(oy + r)}"
            f"V{f(oy + s - r)}A{f(r)} {f(r)} 0 0 1 {f(ox + s - r)} {f(oy + s)}H{f(ox + r)}"
            f"A{f(r)} {f(r)} 0 0 1 {f(ox)} {f(oy + s - r)}V{f(oy + r)}A{f(r)} {f(r)} 0 0 1 {f(ox + r)} {f(oy)}Z")


def text_el(x, y, s, fill, widget, size_mm=4.0):
    if widget:
        return f'<text class="ts" x="{f(x)}" y="{f(y)}" text-anchor="middle" style="fill:{fill}">{s}</text>'
    return (f'<text x="{f(x)}" y="{f(y)}" text-anchor="middle" font-family="Arial, sans-serif" '
            f'font-size="{f(size_mm)}" font-weight="bold" fill="{fill}">{s}</text>')


def render(key, k, ox, oy, widget):
    D = DESIGNS[key]
    T = THEMES[D["theme"]]
    targets = D["targets"]
    cid = "w" + key.replace("-", "")
    P = lambda x, y: (ox + x * k, oy + y * k)
    sw = lambda mm: f(mm * k)
    holes = "".join(path_d(t.cmds, t.cx, t.cy, t.ang, k, ox, oy) for t in targets)
    o = [f'<defs><clipPath id="{cid}"><path clip-rule="evenodd" d="{plate_path(k, ox, oy)}{holes}"/></clipPath></defs>',
         f'<path fill-rule="evenodd" fill="{T["base"]}" d="{plate_path(k, ox, oy)}{holes}"/>',
         f'<g clip-path="url(#{cid})" fill="none" stroke-linecap="round">']
    if D["deco"] == "radar":
        cx, cy = P(G0 + 5 * CELL, G0 + 5 * CELL)
        rings = "".join(f'<circle cx="{f(cx)}" cy="{f(cy)}" r="{sw(r)}"/>' for r in (20, 40, 60))
        o.append(f'<g stroke="{T["deco"]}" stroke-width="{sw(0.5)}" stroke-dasharray="{sw(1.5)} {sw(1.5)}">{rings}</g>')
    if D["grid"]:
        lines = []
        for i in range(11):
            x0, y0 = P(G0 + i * CELL, G0); x1, y1 = P(G0 + i * CELL, G0 + 10 * CELL)
            lines.append(f"M{f(x0)} {f(y0)}V{f(y1)}")
            x0, y0 = P(G0, G0 + i * CELL); x1, y1 = P(G0 + 10 * CELL, G0 + i * CELL)
            lines.append(f"M{f(x0)} {f(y0)}H{f(x1)}")
        o.append(f'<path stroke="{T["deco"]}" stroke-width="{sw(0.6)}" d="{"".join(lines)}"/>')
    if D["deco"] == "olas":
        segs, lam, amp, gap = [], 6.0, 1.0, 8.0
        for row, y in enumerate([9 + 7 * j for j in range(18)]):
            x = 4 - (row % 3) * 7
            while x < 135:
                x0, y0 = P(x, y)
                segs.append(f"M{f(x0)} {f(y0)}q{sw(lam / 4)} {sw(-amp * 1.2)} {sw(lam / 2)} 0" + f"t{sw(lam / 2)} 0" * 3)
                x += 2 * lam + gap
        o.append(f'<path stroke="{T["deco"]}" stroke-width="{sw(0.7)}" d="{"".join(segs)}"/>')
    if D["deco"] == "nubes":
        for (x, y, s) in CLOUDS:
            o.append(cloud(x, y, s, k, ox, oy, T["deco"], T["edge"]))
    o.append(f'<path stroke="{T["relief"]}" stroke-width="{sw(1.6)}" stroke-linejoin="round" d="{holes}"/>')
    o.append("</g>")
    if D["frame"]:
        fx, fy = P(1.5, 1.5)
        o.append(f'<rect x="{f(fx)}" y="{f(fy)}" width="{sw(136)}" height="{sw(136)}" rx="{sw(2.5)}" '
                 f'fill="none" stroke="{T["relief"]}" stroke-width="{sw(3)}"/>')
    for t in targets:
        o.append(f'<path fill="{DISC}" d="{tab_poly(t, k, ox, oy)}"/>')
        cx, cy = P(*t.disc_c())
        r = t.disc_d / 2
        o.append(f'<circle cx="{f(cx)}" cy="{f(cy)}" r="{sw(r)}" fill="{DISC}"/>')
        for q in ([0.62] if t.disc_d < 9 else [0.7, 0.4]):
            o.append(f'<circle cx="{f(cx)}" cy="{f(cy)}" r="{sw(r * q)}" fill="none" stroke="{DISC_RING}" stroke-width="{sw(0.5)}"/>')
        o.append(f'<circle cx="{f(cx)}" cy="{f(cy)}" r="{sw(min(0.9, r * 0.18))}" fill="{DISC_RING}"/>')
    if D["coords"]:
        for i, ch in enumerate("ABCDEFGHIJ"):
            o.append(text_el(*P(G0 + (i + 0.5) * CELL, 8.0), ch, T["relief"], widget))
        for j in range(10):
            o.append(text_el(*P(6.5, G0 + (j + 0.5) * CELL + 1.45), str(j + 1), T["relief"], widget))
    for t in targets:
        if t.badge:
            bx, by = P(*t.badge)
            o.append(f'<circle cx="{f(bx)}" cy="{f(by)}" r="{sw(3.6)}" fill="{T["relief"]}" stroke="{T["edge"]}" stroke-width="{sw(0.15)}"/>')
            o.append(text_el(bx, by + 1.45 * k, str(t.pts), BADGE_TXT, widget))
    o.append(f'<path fill="none" stroke="{T["edge"]}" stroke-width="{f(max(0.3, k / 3))}" d="{plate_path(k, ox, oy)}"/>')
    return "".join(o)


STANDALONE_CSS = ('<style>.ts{font:12px Arial,sans-serif;fill:#5F5E5A}.th{font:500 14px Arial,sans-serif;fill:#2C2C2A}'
                  '.leader{stroke:#888780;stroke-width:.5;stroke-dasharray:3 3;fill:none}</style>')


def annotated(key, standalone):
    D = DESIGNS[key]
    k, ox, oy = 3.0, 40, 22
    lab = []
    for (tx_mm, ty_mm, ly, t1, t2) in D["labels"]:
        tx, ty = ox + tx_mm * k, oy + ty_mm * k
        lab.append(f'<line class="leader" x1="{f(tx)}" y1="{f(ty)}" x2="474" y2="{ly - 4}"/>'
                   f'<circle cx="{f(tx)}" cy="{f(ty)}" r="2.5" fill="var(--t)"/>'
                   f'<text class="th" x="480" y="{ly}">{t1}</text>'
                   f'<text class="ts" x="480" y="{ly + 17}">{t2}</text>')
    H = int(oy + SIZE * k + 22)
    head = ('<svg xmlns="http://www.w3.org/2000/svg" width="680" height="%d" viewBox="0 0 680 %d">' % (H, H) + STANDALONE_CSS
            if standalone else f'<svg width="100%" viewBox="0 0 680 {H}" role="img">')
    svg = (f'{head}<title>{D["title"]}</title><desc>{D["desc"]}</desc>'
           f'{render(key, k, ox, oy, True)}{"".join(lab)}</svg>')
    return svg.replace("var(--t)", "#888780") if standalone else svg


def full_scale(key):
    D = DESIGNS[key]
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="139mm" height="139mm" viewBox="0 0 139 139">'
            f'<title>{D["title"]} (139x139 mm)</title>{render(key, 1.0, 0, 0, False)}</svg>')


FILES = {
    "barcos-A": ("barcos", "A-tablero-clasico"),
    "barcos-B": ("barcos", "B-escuadra-con-puntos"),
    "aviones-A": ("aviones", "A-pantalla-radar"),
    "aviones-B": ("aviones", "B-escuadron-con-puntos"),
}

if __name__ == "__main__":
    for key, (folder, name) in FILES.items():
        d = os.path.join(ROOT, folder)
        os.makedirs(d, exist_ok=True)
        with open(os.path.join(d, f"{name}-1a1.svg"), "w", encoding="utf-8") as fh:
            fh.write(full_scale(key))
        with open(os.path.join(d, f"{name}-anotado.svg"), "w", encoding="utf-8") as fh:
            fh.write(annotated(key, True))
        if WIDGET_DIR:
            with open(os.path.join(WIDGET_DIR, f"widget-{key}.svg"), "w", encoding="utf-8") as fh:
                fh.write(annotated(key, False))
        gaps = ", ".join(f"{t.name}: {t.gap():.2f}" for t in DESIGNS[key]["targets"])
        print(f"{key}: holgura mín. diana-borde (mm) -> {gaps}")
