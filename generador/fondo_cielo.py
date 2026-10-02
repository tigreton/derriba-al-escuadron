"""Fondo de cielo azul con nubes para imprimir en láser a color (139 x 139 mm).

Va detrás de la lámina impresa en 3D: en la versión mínima el cielo queda vacío y se ve el papel.
Las nubes caen en los huecos de esa versión. Saca:
  - fondo-cielo-A4.pdf: hoja A4 a tamaño real, con 3 mm de sangrado, marcas de corte y barra de escala
  - fondo-cielo-A4-dos.pdf: dos fondos por A4 para gastar menos papel (sangrado solo por fuera)
  - fondo-cielo-600ppp.png: solo el dibujo con sangrado (145 x 145 mm a 600 ppp)
  - vista-con-lamina-minima.png: cómo queda detrás de la lámina mínima (necesita OpenSCAD)
Uso:  python fondo_cielo.py [ppp]
"""
import math, os, random, re, subprocess, sys, tempfile
import numpy as np
from PIL import Image, ImageDraw

import hoja_a4

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "aviones", "fondo-cielo")
SCAD = os.path.join(ROOT, "aviones", "B-escuadron.scad")
OPENSCAD = os.environ.get("OPENSCAD", r"C:\Program Files\OpenSCAD\openscad.com")
PPP = int(sys.argv[1]) if len(sys.argv) > 1 else 600

LADO, SANGRADO = 139.0, 3.0

CIELO_ARRIBA, CIELO_ABAJO = (52, 140, 222), (190, 224, 249)
SOL = (0.0, 0.0)  # brillo suave en la esquina de arriba a la izquierda
SOMBRA_NUBE = (160, 186, 222)
LUZ = np.array([-0.45, -0.75, 0.55]) / np.linalg.norm([-0.45, -0.75, 0.55])

# Jirones lejanos: [x, y, medio largo, grueso, opacidad, semilla]
NEBLINA = [[98, 111, 26, 2.6, 0.55, 1], [22, 120, 16, 2.2, 0.5, 2], [120, 88, 14, 2.0, 0.45, 3], [55, 70, 11, 1.8, 0.4, 4]]
# [x, y, ancho, semilla] en mm, origen arriba a la izquierda del corte, vista desde el tirador
NUBES = [
    [42, 19, 36, 3], [72, 31, 26, 7], [112, 63, 32, 11], [84, 75, 18, 5],
    [29, 92, 32, 2], [57, 101, 20, 8], [125, 123, 15, 4], [11, 50, 12, 6],
    [125, 12, 13, 9], [47, 128, 13, 1],
]


def mm(v):
    return v * PPP / 25.4


def mezcla(a, b, t):
    a, b = np.asarray(a, float), np.asarray(b, float)
    return a + (b - a) * t[..., None]


def suave(e0, e1, x):
    t = np.clip((x - e0) / (e1 - e0), 0, 1)
    return t * t * (3 - 2 * t)


# ---------------- nubes ----------------
def bolas(cx, cy, w, semilla):
    """Cúmulo: una fila de bolas en la base y cúpulas más grandes encima. Devuelve (bolas, y de la base)."""
    rnd = random.Random(semilla)
    base = cy + 0.2 * w
    nb = rnd.choice((3, 4)) if w < 20 else rnd.choice((4, 5))
    rb = w / (2 * nb) * 1.35
    out = []
    for i in range(nb):
        x = cx - w / 2 + rb + i * (w - 2 * rb) / (nb - 1) + rnd.uniform(-0.1, 0.1) * rb
        r = rb * rnd.uniform(0.8, 1.15)
        out.append((x, base - r * rnd.uniform(0.55, 0.8), r, 0.0))
    # cúpulas: la más alta descentrada hacia un lado
    nt = 2 if w < 22 else 3
    lado = rnd.choice((-1, 1))
    for j in range(nt):
        t = (j + 0.5) / nt - 0.5
        x = cx + t * w * 0.55 + rnd.uniform(-0.06, 0.06) * w
        r = w * rnd.uniform(0.16, 0.21) * (1.25 - 0.5 * abs(t + lado * 0.15))
        out.append((x, base - w * 0.15 - r * rnd.uniform(0.4, 0.7), r, -0.2 * r))
    # algún moño pequeño encima
    for _ in range(rnd.choice((1, 2))):
        bx, by, br, _z = rnd.choice(out[nb:])
        a = math.radians(rnd.uniform(-150, -30))
        r = br * rnd.uniform(0.4, 0.55)
        out.append((bx + math.cos(a) * br * 0.7, by + math.sin(a) * br * 0.7, r, -0.3 * br))
    return out, base


def pinta_nube(img, x0, y0, nube):
    """Pinta una nube sobre img (float, píxeles), cuyo píxel (0, 0) está en (x0, y0) mm."""
    cx, cy, w, semilla = nube
    bs, base = bolas(cx, cy, w, semilla)
    xa = min(b[0] - b[2] for b in bs) - 1
    xb = max(b[0] + b[2] for b in bs) + 1
    ya = min(b[1] - b[2] for b in bs) - 1
    i0, i1 = int(mm(xa - x0)), int(math.ceil(mm(xb - x0)))
    j0, j1 = int(mm(ya - y0)), int(math.ceil(mm(base + 1 - y0)))
    i0, j0 = max(i0, 0), max(j0, 0)
    i1, j1 = min(i1, img.shape[1]), min(j1, img.shape[0])
    if i1 <= i0 or j1 <= j0:
        return
    px = x0 + (np.arange(i0, i1) + 0.5) * 25.4 / PPP
    py = y0 + (np.arange(j0, j1) + 0.5) * 25.4 / PPP
    X, Y = np.meshgrid(px, py)

    # silueta: unión suave de las bolas, con la base plana un poco redondeada
    k = 0.018 * w
    dist = None
    for bx, by, r, _z in bs:
        d = np.hypot(X - bx, Y - by) - r
        if dist is None:
            dist = d
        else:
            h = np.clip(0.5 + 0.5 * (d - dist) / k, 0, 1)
            dist = d + (dist - d) * h - k * h * (1 - h)
    kb = 0.03 * w
    yb = Y - base
    h = np.clip(0.5 - 0.5 * (yb - dist) / kb, 0, 1)
    dist = yb + (dist - yb) * h + kb * h * (1 - h)

    # relieve: cada bola es media esfera; las normales se mezclan sin costuras
    tau = 0.03 * w
    hs = []
    for bx, by, r, z in bs:
        dx, dy = X - bx, Y - by
        dd = np.minimum(dx * dx + dy * dy, r * r)
        hs.append((np.sqrt(r * r - dd) + z, dx / r, dy / r, np.sqrt(r * r - dd) / r))
    alto = np.max([q[0] for q in hs], axis=0)
    peso_total = np.zeros(X.shape); nx = np.zeros(X.shape); ny = np.zeros(X.shape); nz = np.zeros(X.shape)
    segundo = np.full(X.shape, -1e9)
    for hz, ax, ay, az in hs:
        p = np.exp((hz - alto) / tau)
        peso_total += p; nx += p * ax; ny += p * ay; nz += p * az
        segundo = np.where(hz < alto - 1e-9, np.maximum(segundo, hz), segundo)
    n = np.sqrt(nx * nx + ny * ny + nz * nz) + 1e-9
    luz = np.clip((nx * LUZ[0] + ny * LUZ[1] + nz * LUZ[2]) / n, 0, 1)
    tono = 0.3 + 0.75 * luz
    # pliegues entre bolas algo más oscuros
    tono *= 1 - 0.22 * np.exp(-(alto - segundo) / (0.04 * w))
    # tripa de la nube en sombra
    tono *= 1 - 0.35 * suave(base - 0.3 * w, base, Y)
    tono = np.clip(tono, 0, 1) ** 1.5
    color = mezcla(SOMBRA_NUBE, (255, 255, 255), tono)
    # cuanto más abajo, más se tiñe del cielo (lejanía)
    lejos = 0.2 * np.clip(cy / LADO, 0, 1)
    color = mezcla(color, cielo_color(X, Y), np.full(X.shape, lejos))

    alfa = np.clip(0.5 - mm(dist), 0, 1)[..., None]
    trozo = img[j0:j1, i0:i1]
    trozo[:] = trozo * (1 - alfa) + color * alfa


def pinta_neblina(img, x0, y0, banda):
    """Jirón de nube lejana: varias manchas alargadas, suaves y transparentes."""
    cx, cy, largo, grueso, fuerza, semilla = banda
    rnd = random.Random(semilla)
    p = x0 + (np.arange(img.shape[1]) + 0.5) * 25.4 / PPP
    q = y0 + (np.arange(img.shape[0]) + 0.5) * 25.4 / PPP
    j0, j1 = np.searchsorted(q, [cy - 4 * grueso, cy + 3 * grueso])
    i0, i1 = np.searchsorted(p, [cx - 1.3 * largo, cx + 1.3 * largo])
    X, Y = np.meshgrid(p[i0:i1], q[j0:j1])
    a = np.zeros(X.shape)
    for _ in range(6):
        mx = cx + rnd.uniform(-0.75, 0.75) * largo
        my = cy + rnd.uniform(-0.6, 0.3) * grueso
        sx = largo * rnd.uniform(0.25, 0.45)
        sy = grueso * rnd.uniform(0.6, 1.0)
        a = np.maximum(a, rnd.uniform(0.6, 1) * np.exp(-((X - mx) / sx) ** 2 - ((Y - my) / sy) ** 2))
    trozo = img[j0:j1, i0:i1]
    trozo[:] = mezcla(trozo, (248, 251, 255), np.clip(fuerza * a, 0, 1))


def cielo_color(X, Y):
    t = suave(-SANGRADO, LADO + SANGRADO, Y) * 0.85 + 0.15 * np.clip(Y / LADO, 0, 1)
    c = mezcla(CIELO_ARRIBA, CIELO_ABAJO, t)
    brillo = 0.35 * np.exp(-((X - SOL[0]) ** 2 + (Y - SOL[1]) ** 2) / (2 * 38.0 ** 2))
    return mezcla(c, (246, 251, 255), brillo)


def dibujo():
    """El fondo con sangrado: devuelve (imagen PIL, mm de su esquina)."""
    x0 = y0 = -SANGRADO
    n = int(round(mm(LADO + 2 * SANGRADO)))
    p = x0 + (np.arange(n) + 0.5) * 25.4 / PPP
    X, Y = np.meshgrid(p, p)
    img = cielo_color(X, Y)
    for banda in NEBLINA:
        pinta_neblina(img, x0, y0, banda)
    for nube in NUBES:
        pinta_nube(img, x0, y0, nube)
    return Image.fromarray(np.clip(img + 0.5, 0, 255).astype(np.uint8)), (x0, y0)


# ---------------- vista con la lámina mínima ----------------
def svg_scad(modulo):
    """Saca de OpenSCAD el 2D de la versión mínima: lista de contornos en mm (origen arriba a la izquierda)."""
    with tempfile.TemporaryDirectory() as tmp:
        scad, svg = os.path.join(tmp, "v.scad"), os.path.join(tmp, "v.svg")
        with open(scad, "w", encoding="utf-8") as fh:
            fh.write(f'include <{SCAD.replace(os.sep, "/")}>\nparte = "nada";\nversion = "minima";\n{modulo}();\n')
        subprocess.run([OPENSCAD, "-o", svg, scad], check=True, capture_output=True)
        d = " ".join(re.findall(r'd="([^"]*)"', open(svg, encoding="utf-8").read(), re.S))
    return [[(float(a), LADO + float(b)) for a, b in re.findall(r"(-?[\d.e+-]+),(-?[\d.e+-]+)", parte)]
            for parte in d.split("M")[1:]]


def mascara(contornos, tam, k, esquina):
    acc = np.zeros((tam, tam), bool)
    for pts in contornos:
        m = Image.new("L", (tam, tam), 0)
        ImageDraw.Draw(m).polygon([((x - esquina[0]) * k, (y - esquina[1]) * k) for x, y in pts], fill=255)
        acc ^= np.array(m) > 127
    return acc


def vista(fondo, esquina):
    try:
        est, dis = svg_scad("lamina_2d"), svg_scad("discos")
    except (OSError, subprocess.CalledProcessError) as e:
        print("Sin OpenSCAD, no saco la vista con la lámina:", e)
        return None
    tam = 900
    img = fondo.resize((tam, tam), Image.LANCZOS)
    k = tam / (LADO + 2 * SANGRADO)
    a = np.array(img).astype(float)
    sombra = mascara([[(x + 0.8, y + 0.8) for x, y in c] for c in est], tam, k, esquina)
    a[sombra] *= 0.7
    a[mascara(est, tam, k, esquina)] = (88, 98, 110)
    a[mascara(dis, tam, k, esquina)] = (226, 75, 74)
    fuera = mascara([[(0, 0), (LADO, 0), (LADO, LADO), (0, LADO)]], tam, k, esquina)
    a[~fuera] = (255, 255, 255)
    return Image.fromarray(a.astype(np.uint8))


def main():
    os.makedirs(OUT, exist_ok=True)
    fondo, esquina = dibujo()
    fondo.save(os.path.join(OUT, "fondo-cielo-600ppp.png" if PPP == 600 else f"fondo-cielo-{PPP}ppp.png"),
               dpi=(PPP, PPP), optimize=True)
    hoja_a4.una(fondo, PPP, LADO, SANGRADO).guarda(os.path.join(OUT, "fondo-cielo-A4.pdf"),
                                                   "Derriba al escuadrón - fondo de cielo 139 mm")
    hoja_a4.dos(fondo, PPP, LADO, SANGRADO).guarda(os.path.join(OUT, "fondo-cielo-A4-dos.pdf"),
                                                   "Derriba al escuadrón - dos fondos de cielo 139 mm")
    v = vista(fondo, esquina)
    if v is not None:
        v.save(os.path.join(OUT, "vista-con-lamina-minima.png"), optimize=True)
    print(f"Hecho en {OUT} ({fondo.size[0]} px = {LADO + 2 * SANGRADO:g} mm a {PPP} ppp)")


if __name__ == "__main__":
    main()
