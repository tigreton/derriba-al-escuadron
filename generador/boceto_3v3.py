"""Boceto rápido (no paramétrico): dos escuadrones 3 contra 3 en la lámina de 139 mm.

Dos disposiciones: "frente" (cara a cara, línea de frente vertical) y
"esquinas" (cada escuadrón sale en abanico de una esquina, frente en diagonal).
Saca aviones/boceto-3v3/boceto-3v3[-esquinas].png y avisa si dos huecos, una
insignia o una nube quedan a menos de 2 mm entre sí o del marco.
Las fuentes se buscan en CANVAS_FONTS (por defecto, la carpeta canvas-fonts de
la skill canvas-design).
Uso:  python boceto_3v3.py [frente|esquinas]   (sin argumento, las dos)
"""
import math, os, sys
from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.path.join(ROOT, "aviones", "boceto-3v3")
FONTS = os.environ.get("CANVAS_FONTS") or r"C:\Users\tigreton\AppData\Roaming\Claude\local-agent-mode-sessions\skills-plugin\c3d3d928-b081-4aaf-84d0-bec91b2e1548\f8c26230-eebc-45a4-be02-1c49063e1557\skills\canvas-design\canvas-fonts"

SS = 3                      # supersampling
W, H = 1830, 1260
K = 7.4                     # px por mm
OX, OY = 400, 132            # esquina de la lámina en px
SIZE = 139.0
C = SIZE / 2

SKY, FRAME, EDGE = "#85B7EB", "#F4F9FE", "#378ADD"
HOLE, HOLE_EDGE = "#FFFFFF", "#D3E4F5"
TEAM = {"A": ("#E24B4A", "#FCEBEB"), "B": ("#0C447C", "#E6F1FB")}
INK, INK2, BG = "#1F2A37", "#6B7785", "#FBFAF7"


def font(name, px):
    return ImageFont.truetype(os.path.join(FONTS, name), int(px * SS))


def P(x, y):
    return ((OX + x * K) * SS, (OY + y * K) * SS)


def rot(p, cx, cy, ang):
    a = math.radians(ang)
    x, y = p
    return (cx + x * math.cos(a) - y * math.sin(a), cy + x * math.sin(a) + y * math.cos(a))


def plane(S, nose, tail_end, fw, cr, ct, sweep, ts=0.0, tc=0.0, tsw=0.0):
    hw = fw / 2
    k = min(nose * 0.45, 2.2 * fw)
    right = [(hw, -cr / 2), (S / 2, -cr / 2 + sweep), (S / 2, -cr / 2 + sweep + ct), (hw, cr / 2)]
    if ts > 0:
        right += [(hw * 0.8, tail_end - tc), (ts / 2, tail_end - tc + tsw), (ts / 2, tail_end), (hw * 0.5, tail_end)]
    else:
        right += [(hw * 0.6, tail_end)]

    def quad(p0, c, p1, n=10):
        return [((1 - t) ** 2 * p0[0] + 2 * (1 - t) * t * c[0] + t * t * p1[0],
                 (1 - t) ** 2 * p0[1] + 2 * (1 - t) * t * c[1] + t * t * p1[1]) for t in [i / n for i in range(1, n + 1)]]
    pts = [(0, -nose)] + quad((0, -nose), (hw, -nose), (hw, -nose + k)) + right
    pts += [(-x, y) for (x, y) in reversed(right)]
    pts += [(-hw, -nose + k)] + quad((-hw, -nose + k), (-hw, -nose), (0, -nose))[:-1]
    return pts


# tipos (morro hacia -y, origen = centro de la diana)
BOMB = dict(S=54, nose=16, tail_end=22, fw=10, cr=14, ct=7, sweep=2.5, ts=20, tc=7, tsw=1.5)
CAZA = dict(S=40, nose=16, tail_end=19, fw=8, cr=12, ct=5, sweep=9, ts=14, tc=5, tsw=2.5)
AVIO = dict(S=30, nose=9, tail_end=14, fw=6, cr=8, ct=5, sweep=0.5, ts=12, tc=4, tsw=0.5)

A, B = TEAM["A"][0], TEAM["B"][0]
LAYOUTS = {
    "frente": dict(
        out="boceto-3v3.png", subtitle="3 CONTRA 3",
        # escuadrón A (izquierda, morro a la derecha); B es A girado 180° sobre el centro
        squad_a=[  # (nombre, tipo, cx, cy, ángulo, Ø diana, puntos, insignia de puntos)
            ("Bombardero", BOMB, 32, 33, 90, 11, 1, (57, 44)),
            ("Caza", CAZA, 51, C, 90, 8, 3, (58, 89)),
            ("Avioneta", AVIO, 31, 110, 90, 6, 5, (13, 88)),
        ],
        insignia_a=(14, C), front="vertical",
        clouds=[(C - 1, 15, 0.75), (C + 1, SIZE - 15, 0.75), (C + 12, 39, 0.5), (C - 12, SIZE - 39, 0.5)],
        labels=[  # (lado, x_mm, y_mm, color, titulo, subtítulo en una o dos líneas)
            ("L", 12, 30, A, "Bombardero", ["Ø11 · 1 punto · retaguardia"]),
            ("L", 7.8, C, A, "Escuadrón A", ["insignia y dianas en rojo"]),
            ("L", 17.5, 110, A, "Avioneta", ["Ø6 · 5 puntos · retaguardia"]),
            ("R", SIZE - 9.4, 51, INK, "Puntos en relieve", ["más pequeño, más vale"]),
            ("R", SIZE - 7.8, C, B, "Escuadrón B", ["insignia y dianas en azul marino"]),
            ("R", SIZE - 13, SIZE - 30, INK, "Media vuelta", ["B es A girado 180°: los dos", "jugadores ven la misma lámina"]),
        ],
        caza_note="  ·  morro con morro en el centro"),
    "esquinas": dict(
        out="boceto-3v3-esquinas.png", subtitle="3 CONTRA 3  ·  DESDE LAS ESQUINAS",
        # escuadrón A sale en abanico de la esquina inferior izquierda; B, de la superior derecha
        squad_a=[
            ("Bombardero", BOMB, 37, 102, 45, 11, 1, (60, 103)),
            ("Caza", CAZA, 83, 112, 72, 8, 3, (106, 126)),
            ("Avioneta", AVIO, 22, 61, 18, 6, 5, (39, 79)),
        ],
        insignia_a=(11.5, SIZE - 11.5), front="diagonal",
        clouds=[(C, C - 1, 0.75), (31, 27, 0.6), (SIZE - 31, SIZE - 27, 0.6)],
        labels=[
            ("L", 7.6, 58, A, "Avioneta", ["Ø6 · 5 puntos"]),
            ("L", 17, 84, A, "Bombardero", ["Ø11 · 1 punto"]),
            ("L", 5.3, SIZE - 11.5, A, "Escuadrón A", ["sale de la esquina", "insignia y dianas en rojo"]),
            ("R", SIZE - 5.3, 11.5, B, "Escuadrón B", ["sale de la esquina contraria", "insignia y dianas en azul marino"]),
            ("R", SIZE - 7.6, SIZE - 58, INK, "Media vuelta", ["B es A girado 180°: los dos", "jugadores ven la misma lámina"]),
            ("R", SIZE - 6, SIZE - 6, INK, "Línea de frente", ["en diagonal, de esquina a esquina"]),
        ],
        caza_note=""),
}


def squads(L):
    out = []
    for name, t, cx, cy, ang, d, pts, b in L["squad_a"]:
        out.append(("A", name, t, cx, cy, ang, d, pts, b))
        out.append(("B", name, t, SIZE - cx, SIZE - cy, ang + 180, d, pts, (SIZE - b[0], SIZE - b[1])))
    return out


def nearest_on_outline(poly, p):
    best = None
    for i in range(len(poly)):
        a, b = poly[i], poly[(i + 1) % len(poly)]
        dx, dy = b[0] - a[0], b[1] - a[1]
        t = max(0, min(1, ((p[0] - a[0]) * dx + (p[1] - a[1]) * dy) / (dx * dx + dy * dy or 1)))
        q = (a[0] + t * dx, a[1] + t * dy)
        dd = math.hypot(p[0] - q[0], p[1] - q[1])
        if best is None or dd < best[0]:
            best = (dd, q)
    return best[1]


def inside(poly, p):
    x, y = p
    c = False
    for i in range(len(poly)):
        (x1, y1), (x2, y2) = poly[i], poly[(i + 1) % len(poly)]
        if (y1 > y) != (y2 > y) and x < x1 + (y - y1) * (x2 - x1) / (y2 - y1):
            c = not c
    return c


def gap(a, b):
    """Distancia libre entre dos formas: ("poly", puntos) o ("circ", (x, y), r). Negativa si se pisan."""
    if a[0] == "circ" and b[0] == "circ":
        return math.dist(a[1], b[1]) - a[2] - b[2]
    if a[0] == "circ":
        a, b = b, a
    if b[0] == "circ":
        dd = math.dist(nearest_on_outline(a[1], b[1]), b[1])
        return (-dd if inside(a[1], b[1]) else dd) - b[2]
    if any(inside(b[1], p) for p in a[1]) or any(inside(a[1], p) for p in b[1]):
        return -1.0
    return min(min(math.dist(p, nearest_on_outline(b[1], p)) for p in a[1]),
               min(math.dist(p, nearest_on_outline(a[1], p)) for p in b[1]))


def frame_gap(shape):
    lo, hi = 3.0, SIZE - 3.0
    if shape[0] == "circ":
        (x, y), r = shape[1], shape[2]
        return min(x - lo, hi - x, y - lo, hi - y) - r
    return min(min(x - lo, hi - x, y - lo, hi - y) for x, y in shape[1])


def check(L):
    shapes = []
    for team, name, t, cx, cy, ang, dia, pts, b in squads(L):
        shapes.append((f"{name} {team}", ("poly", [rot(p, cx, cy, ang) for p in plane(**t)])))
        shapes.append((f"puntos {name} {team}", ("circ", b, 3.6)))
    ia = L["insignia_a"]
    shapes.append(("insignia A", ("circ", ia, 6.2)))
    shapes.append(("insignia B", ("circ", (SIZE - ia[0], SIZE - ia[1]), 6.2)))
    for i, (x, y, sc) in enumerate(L["clouds"]):
        shapes.append((f"nube {i + 1}", ("circ", (x + 1.5 * sc, y - 1 * sc), 10.5 * sc)))
    bad = []
    for i in range(len(shapes)):
        fg = frame_gap(shapes[i][1])
        if fg < 2:
            bad.append(f"  {shapes[i][0]} a {fg:.1f} mm del marco")
        for j in range(i + 1, len(shapes)):
            g = gap(shapes[i][1], shapes[j][1])
            if g < 2:
                bad.append(f"  {shapes[i][0]} / {shapes[j][0]}: {g:.1f} mm")
    return bad


def cloud(d, x, y, s, fill, edge):
    for (a, b, r) in [(-6, 0, 4), (-1, -2.5, 5.5), (5, -1, 4.5), (9, 1, 3)]:
        cx, cy = P(x + a * s, y + b * s)
        rr = r * s * K * SS
        d.ellipse([cx - rr, cy - rr, cx + rr, cy + rr], fill=fill, outline=edge, width=int(0.15 * K * SS))
    x0, y0 = P(x - 10 * s, y)
    x1, y1 = P(x + 12 * s, y + 4 * s)
    d.rounded_rectangle([x0, y0, x1, y1], radius=2 * s * K * SS, fill=fill)


def disc(d, cx, cy, dia, col, ring):
    for f, c in [(1.0, col), (0.72, ring), (0.56, col), (0.30, ring), (0.16, col)]:
        r = dia / 2 * f * K * SS
        x, y = P(cx, cy)
        d.ellipse([x - r, y - r, x + r, y + r], fill=c)


def badge(d, x, y, txt, col):
    cx, cy = P(x, y)
    r = 3.6 * K * SS
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=FRAME, outline=HOLE_EDGE, width=SS)
    d.text((cx, cy + 0.3 * SS), txt, font=font("InstrumentSans-Bold.ttf", 17), fill=col, anchor="mm")


def front_line(d, kind):
    """Trazos en relieve de 3,2 mm cada 5,6 mm."""
    if kind == "vertical":
        y = 6.0
        while y < SIZE - 6:
            xa, ya = P(C - 0.5, y); xb, yb = P(C + 0.5, min(y + 3.2, SIZE - 6))
            d.rounded_rectangle([xa, ya, xb, yb], radius=0.5 * K * SS, fill=FRAME)
            y += 5.6
        return
    s, e = 7.0, SIZE - 7.0
    u = (1 / math.sqrt(2), 1 / math.sqrt(2))
    t, n = 0.0, math.dist((s, s), (e, e))
    while t < n:
        t1 = min(t + 3.2, n)
        a, b = P(s + u[0] * t, s + u[1] * t), P(s + u[0] * t1, s + u[1] * t1)
        w = 1.0 * K * SS
        d.line([a, b], fill=FRAME, width=int(w))
        for c in (a, b):
            d.ellipse([c[0] - w / 2, c[1] - w / 2, c[0] + w / 2, c[1] + w / 2], fill=FRAME)
        t += 5.6


def render(name):
    L = LAYOUTS[name]
    img = Image.new("RGB", (W * SS, H * SS), BG)
    d = ImageDraw.Draw(img)

    # lámina: marco + cielo
    x0, y0 = P(0, 0); x1, y1 = P(SIZE, SIZE)
    d.rounded_rectangle([x0, y0, x1, y1], radius=4 * K * SS, fill=FRAME, outline=EDGE, width=2 * SS)
    x0, y0 = P(3, 3); x1, y1 = P(SIZE - 3, SIZE - 3)
    d.rounded_rectangle([x0, y0, x1, y1], radius=1.5 * K * SS, fill=SKY)

    # línea de frente en relieve y nubes sobre ella
    front_line(d, L["front"])
    for c in L["clouds"]:
        cloud(d, *c, FRAME, HOLE_EDGE)

    # insignias de bando
    ia = L["insignia_a"]
    for team, (x, yv) in [("A", ia), ("B", (SIZE - ia[0], SIZE - ia[1]))]:
        col, ring = TEAM[team]
        cx, cy = P(x, yv)
        for r_mm, c in [(6.2, FRAME), (4.6, col), (2.2, FRAME)]:
            r = r_mm * K * SS
            d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=c)
        d.text((cx, cy + 0.2 * SS), team, font=font("InstrumentSans-Bold.ttf", 15), fill=col, anchor="mm")

    # aviones
    for team, pname, t, cx, cy, ang, dia, pts, b in squads(L):
        col, ring = TEAM[team]
        local = plane(**t)
        poly = [P(*rot(p, cx, cy, ang)) for p in local]
        d.polygon(poly, fill=HOLE, outline=HOLE_EDGE, width=int(1.2 * SS))
        q = nearest_on_outline(local, (0, 0))
        qx, qy = rot(q, cx, cy, ang)
        d.line([P(cx, cy), P(qx, qy)], fill=col, width=int(1.6 * K * SS))
        disc(d, cx, cy, dia, col, ring)
        badge(d, *b, str(pts), col)

    # ---------- texto ----------
    def T(x, y, s, txt, f, col, anchor="la"):
        d.text((x * SS, y * SS), txt, font=font(f, s), fill=col, anchor=anchor)

    T(60, 58, 34, "Derriba al escuadrón", "InstrumentSerif-Regular.ttf", INK, "ls")
    T(60, 84, 12, f"BOCETO  ·  {L['subtitle']}  ·  LÁMINA 139 × 139 MM", "GeistMono-Regular.ttf", INK2, "ls")

    if L["front"] == "vertical":  # rótulo centrado encima de la lámina
        cx_px = OX + C * K
        T(cx_px, OY - 18, 11, "LÍNEA DE FRENTE", "GeistMono-Regular.ttf", INK2, "ms")
        d.line([(cx_px * SS, (OY - 12) * SS), (cx_px * SS, (OY + 1) * SS)], fill="#A9B3BE", width=SS)

    LCOL = OX - 40          # borde derecho del texto de la izquierda
    RCOL = OX + SIZE * K + 40
    for side, xm, ym, col, title, sub in L["labels"]:
        px, py = OX + xm * K, OY + ym * K
        dot = 3.0
        d.ellipse([(px - dot) * SS, (py - dot) * SS, (px + dot) * SS, (py + dot) * SS], fill=INK)
        if side == "L":
            d.line([(px * SS, py * SS), ((LCOL + 14) * SS, py * SS)], fill="#A9B3BE", width=SS)
            x, anchors = LCOL, ("rs", "rt")
        else:
            d.line([(px * SS, py * SS), ((RCOL - 14) * SS, py * SS)], fill="#A9B3BE", width=SS)
            x, anchors = RCOL, ("ls", "lt")
        T(x, py - 6, 21, title, "InstrumentSans-Regular.ttf", col, anchors[0])
        for i, line in enumerate(sub):
            T(x, py + 8 + 20 * i, 14, line, "InstrumentSans-Regular.ttf", INK2, anchors[1])

    # pie: tipos por bando
    fy = OY + SIZE * K + 46
    T(OX, fy, 11, "POR BANDO", "GeistMono-Regular.ttf", INK2, "ls")
    items = [("Bombardero", "Ø11 · 1 pto"), ("Caza", "Ø8 · 3 ptos" + L["caza_note"]), ("Avioneta", "Ø6 · 5 ptos")]
    x = OX + 110
    for n, s in items:
        T(x, fy + 1, 17, n, "InstrumentSans-Regular.ttf", INK, "ls")
        x += d.textlength(n, font=font("InstrumentSans-Regular.ttf", 17)) / SS + 10
        T(x, fy, 12, s, "GeistMono-Regular.ttf", INK2, "ls")
        x += d.textlength(s, font=font("GeistMono-Regular.ttf", 12)) / SS + 44

    img = img.resize((W, H), Image.LANCZOS)
    os.makedirs(OUT_DIR, exist_ok=True)
    out = os.path.join(OUT_DIR, L["out"])
    img.save(out)
    print(out)
    for line in check(L):
        print(line)


for name in (sys.argv[1:] or LAYOUTS):
    render(name)
