"""Boceto rápido (no paramétrico): dos escuadrones 3 contra 3 en la lámina de 139 mm.

Saca aviones/boceto-3v3/boceto-3v3.png. Las fuentes se buscan en CANVAS_FONTS
(por defecto, la carpeta canvas-fonts de la skill canvas-design).
Uso:  python boceto_3v3.py
"""
import math, os
from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "aviones", "boceto-3v3", "boceto-3v3.png")
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

# escuadrón A (izquierda, morro a la derecha); B es A girado 180° sobre el centro
SQUAD_A = [  # (nombre, tipo, cx, cy, Ø diana, puntos, insignia)
    ("Bombardero", BOMB, 32, 33, 11, 1, (57, 44)),
    ("Caza", CAZA, 51, C, 8, 3, (58, 89)),
    ("Avioneta", AVIO, 31, 110, 6, 5, (13, 88)),
]


def squads():
    out = []
    for name, t, cx, cy, d, pts, b in SQUAD_A:
        out.append(("A", name, t, cx, cy, 90, d, pts, b))
        out.append(("B", name, t, SIZE - cx, SIZE - cy, -90, d, pts, (SIZE - b[0], SIZE - b[1])))
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


img = Image.new("RGB", (W * SS, H * SS), BG)
d = ImageDraw.Draw(img)

# lámina: marco + cielo
x0, y0 = P(0, 0); x1, y1 = P(SIZE, SIZE)
d.rounded_rectangle([x0, y0, x1, y1], radius=4 * K * SS, fill=FRAME, outline=EDGE, width=2 * SS)
x0, y0 = P(3, 3); x1, y1 = P(SIZE - 3, SIZE - 3)
d.rounded_rectangle([x0, y0, x1, y1], radius=1.5 * K * SS, fill=SKY)

# línea de frente en relieve (trazos) y nubes sobre ella
clouds = [(C - 1, 15, 0.75), (C + 1, SIZE - 15, 0.75), (C + 12, 39, 0.5), (C - 12, SIZE - 39, 0.5)]
y = 6.0
while y < SIZE - 6:
    xa, ya = P(C - 0.5, y); xb, yb = P(C + 0.5, min(y + 3.2, SIZE - 6))
    d.rounded_rectangle([xa, ya, xb, yb], radius=0.5 * K * SS, fill=FRAME)
    y += 5.6
for c in clouds:
    cloud(d, *c, FRAME, HOLE_EDGE)

# insignias de bando
for team, (x, yv) in [("A", (14, C)), ("B", (SIZE - 14, C))]:
    col, ring = TEAM[team]
    cx, cy = P(x, yv)
    for r_mm, c in [(6.2, FRAME), (4.6, col), (2.2, FRAME)]:
        r = r_mm * K * SS
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=c)
    d.text((cx, cy + 0.2 * SS), team, font=font("InstrumentSans-Bold.ttf", 15), fill=col, anchor="mm")

# aviones
for team, name, t, cx, cy, ang, dia, pts, b in squads():
    col, ring = TEAM[team]
    local = plane(**t)
    poly_mm = [rot(p, cx, cy, ang) for p in local]
    poly = [P(*p) for p in poly_mm]
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
T(60, 84, 12, "BOCETO  ·  3 CONTRA 3  ·  LÁMINA 139 × 139 MM", "GeistMono-Regular.ttf", INK2, "ls")

# línea de frente: rótulo centrado encima de la lámina
cx_px = OX + C * K
T(cx_px, OY - 18, 11, "LÍNEA DE FRENTE", "GeistMono-Regular.ttf", INK2, "ms")
d.line([(cx_px * SS, (OY - 12) * SS), (cx_px * SS, (OY + 1) * SS)], fill="#A9B3BE", width=SS)

LCOL = OX - 40          # borde derecho del texto de la izquierda
RCOL = OX + SIZE * K + 40
labels = [  # (lado, x_mm, y_mm, color, titulo, sub)
    ("L", 12, 30, TEAM["A"][0], "Bombardero", "Ø11 · 1 punto · retaguardia"),
    ("L", 7.8, C, TEAM["A"][0], "Escuadrón A", "insignia y dianas en rojo"),
    ("L", 17.5, 110, TEAM["A"][0], "Avioneta", "Ø6 · 5 puntos · retaguardia"),
    ("R", SIZE - 9.4, 51, INK, "Puntos en relieve", "más pequeño, más vale"),
    ("R", SIZE - 7.8, C, TEAM["B"][0], "Escuadrón B", "insignia y dianas en azul marino"),
    ("R", SIZE - 13, SIZE - 30, INK, "Media vuelta", "B es A girado 180°: los dos"),
]
for side, xm, ym, col, title, sub in labels:
    px, py = OX + xm * K, OY + ym * K
    dot = 3.0
    d.ellipse([(px - dot) * SS, (py - dot) * SS, (px + dot) * SS, (py + dot) * SS], fill=INK)
    if side == "L":
        d.line([(px * SS, py * SS), ((LCOL + 14) * SS, py * SS)], fill="#A9B3BE", width=SS)
        T(LCOL, py - 6, 21, title, "InstrumentSans-Regular.ttf", col, "rs")
        T(LCOL, py + 8, 14, sub, "InstrumentSans-Regular.ttf", INK2, "rt")
    else:
        d.line([(px * SS, py * SS), ((RCOL - 14) * SS, py * SS)], fill="#A9B3BE", width=SS)
        T(RCOL, py - 6, 21, title, "InstrumentSans-Regular.ttf", col, "ls")
        T(RCOL, py + 8, 14, sub, "InstrumentSans-Regular.ttf", INK2, "lt")
        if title == "Media vuelta":
            T(RCOL, py + 28, 14, "jugadores ven la misma lámina", "InstrumentSans-Regular.ttf", INK2, "lt")

# pie: tipos por bando
fy = OY + SIZE * K + 46
T(OX, fy, 11, "POR BANDO", "GeistMono-Regular.ttf", INK2, "ls")
items = [("Bombardero", "Ø11 · 1 pto"), ("Caza", "Ø8 · 3 ptos  ·  morro con morro en el centro"), ("Avioneta", "Ø6 · 5 ptos")]
x = OX + 110
for n, s in items:
    T(x, fy + 1, 17, n, "InstrumentSans-Regular.ttf", INK, "ls")
    x += d.textlength(n, font=font("InstrumentSans-Regular.ttf", 17)) / SS + 10
    T(x, fy, 12, s, "GeistMono-Regular.ttf", INK2, "ls")
    x += d.textlength(s, font=font("GeistMono-Regular.ttf", 12)) / SS + 44

img = img.resize((W, H), Image.LANCZOS)
os.makedirs(os.path.dirname(OUT), exist_ok=True)
img.save(OUT)
print(OUT)
