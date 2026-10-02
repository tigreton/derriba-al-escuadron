"""Fondo de cielo con nubes para la lámina mínima de 'Derriba al escuadrón' (139 x 139 mm).

Todo se define en milímetros (origen abajo a la izquierda, y hacia arriba, como en B-escuadron.scad),
así que la misma composición sale igual a cualquier resolución. Las nubes están colocadas en el
cielo que deja libre la versión mínima; para moverlas, edita la lista NUBES.
Uso: python fondo_cielo_ruido.py <px_por_mm> <salida.png> [hoja-dos.pdf]
     Además de la imagen saca un PDF A4 con dos fondos para imprimir juntos (por defecto
     fondo-cielo-A4-imprimir-dos.pdf, junto a la imagen).
     600 ppp = 23.62204724 px/mm; la imagen sale con 3 mm de sangrado por cada lado (145 x 145 mm).
"""
import os, sys
import numpy as np
from PIL import Image

import hoja_a4

LADO = 139.0          # mm, corte final
SANGRADO = 3.0        # mm de sangrado a cada lado
TOTAL = LADO + 2 * SANGRADO

# ---------------------------------------------------------------- ruido
def _tabla(seed):
    rng = np.random.default_rng(seed)
    perm = rng.permutation(256)
    perm = np.concatenate([perm, perm]).astype(np.int32)
    ang = rng.uniform(0, 2 * np.pi, 256)
    return perm, np.cos(ang).astype(np.float32), np.sin(ang).astype(np.float32)

_TABLAS = {}
def perlin(x, y, seed=0):
    if seed not in _TABLAS:
        _TABLAS[seed] = _tabla(seed)
    perm, gx, gy = _TABLAS[seed]
    x0 = np.floor(x); y0 = np.floor(y)
    fx = (x - x0).astype(np.float32); fy = (y - y0).astype(np.float32)
    xi = x0.astype(np.int64) & 255; yi = y0.astype(np.int64) & 255
    def g(ix, iy, dx, dy):
        h = perm[perm[ix] + iy]
        return gx[h] * dx + gy[h] * dy
    n00 = g(xi, yi, fx, fy)
    n10 = g((xi + 1) & 255, yi, fx - 1, fy)
    n01 = g(xi, (yi + 1) & 255, fx, fy - 1)
    n11 = g((xi + 1) & 255, (yi + 1) & 255, fx - 1, fy - 1)
    u = fx * fx * fx * (fx * (fx * 6 - 15) + 10)
    v = fy * fy * fy * (fy * (fy * 6 - 15) + 10)
    a = n00 + u * (n10 - n00)
    b = n01 + u * (n11 - n01)
    return (a + v * (b - a)) * 1.41

def fbm(x, y, oct=5, seed=0, lac=2.0, gan=0.5):
    tot = np.zeros(np.broadcast(x, y).shape, np.float32)
    amp, f, norm = 1.0, 1.0, 0.0
    for i in range(oct):
        tot += amp * perlin(x * f + 17.3 * i, y * f - 9.1 * i, seed + i)
        norm += amp; amp *= gan; f *= lac
    return tot / norm

def smooth(a, b, x):
    t = np.clip((x - a) / (b - a), 0, 1)
    return t * t * (3 - 2 * t)

def mezcla(c1, c2, t):
    t = np.asarray(t, np.float32)[..., None]
    return c1 * (1 - t) + c2 * t

def hexc(h):
    h = h.lstrip('#')
    return np.array([int(h[i:i + 2], 16) for i in (0, 2, 4)], np.float32)

# ---------------------------------------------------------------- cielo
CENIT = hexc('#1F63B8')
ALTO = hexc('#3C86D3')
MEDIO = hexc('#6AA9E4')
HORIZONTE = hexc('#B4DAF4')
BRILLO_SOL = hexc('#EAF5FD')

def color_cielo(X, Y):
    t = np.clip(Y / LADO, -0.05, 1.05)       # 0 abajo, 1 arriba
    # pincelada: el degradado no es perfectamente horizontal
    t = t + 0.035 * fbm(X / 45, Y / 45, 3, seed=11) + 0.012 * (X - LADO / 2) / LADO
    c = mezcla(HORIZONTE, MEDIO, smooth(0.0, 0.42, t))
    c = mezcla(c, ALTO, smooth(0.35, 0.78, t))
    c = mezcla(c, CENIT, smooth(0.72, 1.08, t))
    # resplandor del sol, fuera del cuadro arriba a la izquierda
    d = np.hypot(X + 25, Y - 170)
    c = mezcla(c, BRILLO_SOL, 0.42 * np.exp(-d / 48))
    # textura de pincel en diagonal, muy suave
    u = (X * 0.8 + Y * 0.6); v = (-X * 0.6 + Y * 0.8)
    trazo = fbm(u / 9, v / 1.6, 3, seed=23)
    c = c * (1 + 0.012 * trazo[..., None])
    return c

# ---------------------------------------------------------------- cirros
def cirros(X, Y, c):
    a = np.deg2rad(-9)
    u = X * np.cos(a) - Y * np.sin(a); v = X * np.sin(a) + Y * np.cos(a)
    n = fbm(u / 36, v / 5.0, 4, seed=41)
    q = fbm(u / 60, v / 14, 2, seed=47)              # dónde hay cirros y dónde no
    hebra = smooth(0.12, 0.55, n) * smooth(0.0, 0.3, q)
    altura = smooth(70, 110, Y)                      # solo en lo alto
    alpha = 0.42 * hebra * altura
    return mezcla(c, hexc('#F3F8FE'), alpha)

# ---------------------------------------------------------------- nubes
SOMBRA = hexc('#7F93C6')     # núcleo de sombra, azul lavanda
MEDIA = hexc('#B3C5E6')
CLARA = hexc('#E3ECF8')
LUZ = hexc('#FFFFFF')        # blanco del papel: sin tóner
LUZ_DIR = np.array([-0.52, 0.58, 0.63], np.float32)
LUZ_DIR /= np.linalg.norm(LUZ_DIR)

def posterizar(t, niveles=4, dureza=0.28):
    """Bandas de gouache con transición suave entre tonos."""
    s = np.clip(t, 0, 1) * niveles
    base = np.floor(s); fr = s - base
    return np.clip((base + smooth(0.5 - dureza, 0.5 + dureza, fr)) / niveles, 0, 1)

def paleta(t):
    c = mezcla(SOMBRA, MEDIA, smooth(0.0, 0.38, t))
    c = mezcla(c, CLARA, smooth(0.35, 0.68, t))
    return mezcla(c, LUZ, smooth(0.66, 0.95, t))

def cumulo(cx, base, ancho, alto, seed, lobulos=1.0, forma=1.6, picos=((0, 1, 1),)):
    """Bolas [x, y, r, delante] que forman un cúmulo de base plana y copa de coliflor.
    picos: torres de la copa como (desplazamiento, altura, anchura), relativos al ancho y al alto."""
    rng = np.random.default_rng(seed)
    def perfil(x):            # la copa sube en cada pico y baja hacia los extremos
        v = 0.22
        for dx, h, w in picos:
            u = np.clip(abs(x - (cx + dx * ancho)) / (w * ancho / 2), 0, 1)
            v = max(v, h * (1 - 0.78 * u ** forma))
        return v
    bolas = []
    # contorno de la copa: muchas bolas pegadas al perfil -> borde de coliflor
    n = int(round(ancho / alto * 4.2 * lobulos)) + 3
    for x in np.sort(rng.uniform(cx - ancho * 0.47, cx + ancho * 0.47, n)):
        p = perfil(x)
        r = alto * rng.uniform(0.15, 0.30) * (0.55 + 0.45 * p)
        y = base + alto * p - r * rng.uniform(0.95, 1.15)
        bolas.append([x, max(y, base + r * 0.4), r])
    # relleno grande por dentro
    m = int(round(ancho / alto * 1.6)) + 2
    for x in np.linspace(cx - ancho * 0.36, cx + ancho * 0.36, m) + rng.uniform(-1, 1, m) * alto * 0.1:
        p = perfil(x)
        r = alto * rng.uniform(0.30, 0.40) * (0.6 + 0.4 * p)
        y = base + alto * p * 0.55
        bolas.append([x, y, r])
    # fila de abajo, delante, apoyada en la base
    b = int(round(ancho / alto * 1.2)) + 2
    for x in np.linspace(cx - ancho * 0.44, cx + ancho * 0.44, b) + rng.uniform(-1, 1, b) * alto * 0.06:
        r = alto * rng.uniform(0.22, 0.30) * (0.6 + 0.4 * perfil(x))
        bolas.append([x, base + r * rng.uniform(0.2, 0.45), r])
    return [[x, y, r, 2 * (1 - np.clip((y - base) / alto, 0, 1))] for x, y, r in bolas]

def pintar_nube(img, X, Y, ppmm, nube, cielo):
    from scipy.ndimage import gaussian_filter
    cx, base, ancho, alto, seed = nube['cx'], nube['base'], nube['ancho'], nube['alto'], nube['seed']
    lejania = nube.get('lejania', 0.0)
    bolas = cumulo(cx, base, ancho, alto, seed, nube.get('lobulos', 1.0), nube.get('forma', 1.6),
                   nube.get('picos', ((0, 1, 1),)))
    x0 = min(b[0] - b[2] for b in bolas) - 3; x1 = max(b[0] + b[2] for b in bolas) + 3
    y0 = base - 2; y1 = max(b[1] + b[2] for b in bolas) + 3
    c0 = max(0, int((x0 + SANGRADO) * ppmm)); c1 = min(X.shape[1], int((x1 + SANGRADO) * ppmm) + 1)
    r0 = max(0, int((LADO + SANGRADO - y1) * ppmm)); r1 = min(X.shape[0], int((LADO + SANGRADO - y0) * ppmm) + 1)
    if c0 >= c1 or r0 >= r1:
        return
    x = X[r0:r1, c0:c1]; y = Y[r0:r1, c0:c1]
    sub = img[r0:r1, c0:c1]; sk = cielo[r0:r1, c0:c1]
    esc = alto / 14.0
    # deformación del dominio: bordes algodonosos sin dientes
    wx = x + 0.9 * esc * fbm(x / (4 * esc), y / (4 * esc), 4, seed=seed + 100)
    wy = y + 0.9 * esc * fbm(x / (4 * esc), y / (4 * esc), 4, seed=seed + 150)
    k = 0.035 * alto
    acc = np.zeros(x.shape, np.float64)
    H = np.zeros(x.shape, np.float32)
    for bx, by, br, capa in bolas:
        d = np.hypot(wx - bx, wy - by)
        acc += np.exp(-(d - br) / k)
        H = np.maximum(H, np.sqrt(np.clip(br * br - d * d, 0, None)) + 0.03 * alto * capa)
    # losa de la base: cápsula horizontal que cierra los huecos de abajo
    h0 = 0.26 * alto; xa = cx - ancho * 0.40; xb = cx + ancho * 0.40
    qx = np.clip(wx, xa, xb)
    dcap = np.hypot(wx - qx, wy - (base + h0))
    acc += np.exp(-(dcap - h0) / k)
    H = np.maximum(H, np.sqrt(np.clip(h0 * h0 - dcap * dcap, 0, None)))
    sdf = -k * np.log(acc + 1e-30)
    sdf += 0.25 * esc * fbm(x / (1.3 * esc), y / (1.3 * esc), 3, seed=seed + 200)
    pie = base + 0.25 * esc * fbm(x / (5 * esc), np.full_like(x, seed * 1.0), 2, seed=seed + 400)
    suelo = smooth(pie - 0.12, pie + 0.25, y)
    feather = 0.18 + 0.25 * lejania
    alfa = smooth(-feather, feather, -sdf) * suelo
    # relieve: alturas de las bolas suavizadas -> normal -> luz
    px = 1.0 / ppmm
    Hs = gaussian_filter(H, sigma=0.035 * alto * ppmm)
    gy_rows, gx = np.gradient(Hs, px)
    gyy = -gy_rows                                    # filas hacia abajo, y hacia arriba
    nrm = np.sqrt(gx * gx + gyy * gyy + 1)
    lam = np.clip((-gx * LUZ_DIR[0] - gyy * LUZ_DIR[1] + LUZ_DIR[2]) / nrm, 0, 1)
    # oclusión en los pliegues entre lóbulos
    Hb = gaussian_filter(H, sigma=0.28 * alto * ppmm)
    pliegue = np.clip((Hs - Hb) / (0.25 * alto), -1, 1)
    vert = np.clip((y - base) / alto, 0, 1) ** 0.7
    borde = smooth(0.0, 0.9 * esc, -sdf)              # el canto se aclara un poco al contraluz
    detalle = fbm(x / (2.5 * esc), y / (2.5 * esc), 3, seed=seed + 300)
    tono = (0.22 + 0.48 * vert) * lam + 0.42 * vert + 0.10 * pliegue * vert + 0.03 * detalle + 0.02 + 0.06 * (1 - borde) * vert
    c = paleta(posterizar(tono, 4, 0.36))
    if lejania > 0:
        c = mezcla(c, sk, 0.6 * lejania)
        alfa = alfa * (1 - 0.1 * lejania)
    img[r0:r1, c0:c1] = mezcla(sub, c, alfa * nube.get('opacidad', 1.0))

# Nubes colocadas en el cielo que queda libre en la versión mínima (mm, origen abajo izquierda).
# De arriba (cerca, grandes) a abajo (lejos, pequeñas y planas).
NUBES = [
    dict(cx=40, base=108.5, ancho=70, alto=24, seed=3, forma=1.8, picos=((-0.2, 1, 0.7), (0.24, 0.78, 0.6))),                # la grande de arriba a la izquierda
    dict(cx=106, base=61.5, ancho=54, alto=26, seed=8, forma=1.5, picos=((0.06, 1, 0.75), (-0.3, 0.6, 0.45))),     # torre del centro a la derecha
    dict(cx=128, base=119, ancho=22, alto=11, seed=5, lejania=0.1),    # esquina de arriba a la derecha
    dict(cx=74, base=91, ancho=17, alto=8, seed=14, lejania=0.15),     # hueco de arriba al centro
    dict(cx=16, base=40, ancho=34, alto=15, seed=33, lejania=0.2, picos=((0.18, 1, 0.7), (-0.25, 0.7, 0.5))),     # izquierda, sobre el delta
    dict(cx=58, base=34, ancho=28, alto=11, seed=29, lejania=0.3, picos=((-0.12, 1, 0.8),)),     # centro abajo
    dict(cx=127, base=17, ancho=26, alto=7, seed=44, lejania=0.5, forma=2.5, lobulos=0.6),
    dict(cx=86, base=3.5, ancho=40, alto=8, seed=37, lejania=0.6, forma=3, lobulos=0.7),
    dict(cx=40, base=2.5, ancho=26, alto=6, seed=41, lejania=0.65, forma=3, lobulos=0.6),
    dict(cx=4, base=9, ancho=16, alto=6, seed=52, lejania=0.6, forma=2.5, lobulos=0.6),
]

def pintar(ppmm):
    n = int(round(TOTAL * ppmm))
    c = (np.arange(n, dtype=np.float32) + 0.5) / ppmm - SANGRADO
    X, Y = np.meshgrid(c, (LADO + SANGRADO) - (np.arange(n, dtype=np.float32) + 0.5) / ppmm)
    cielo = color_cielo(X, Y).astype(np.float32)
    img = cirros(X, Y, cielo.copy())
    for nube in NUBES:
        pintar_nube(img, X, Y, ppmm, nube, cielo)
    # grano fino contra el bandeado del tóner (±1,5 niveles)
    # (no se aplica sobre los blancos: ahí manda el papel, sin nada de tóner)
    rng = np.random.default_rng(7)
    grano = rng.normal(0, 1.4, img.shape[:2]).astype(np.float32) * smooth(253, 240, img.min(axis=2))
    img = img + grano[..., None]
    return np.clip(img + 0.5, 0, 255).astype(np.uint8)

if __name__ == '__main__':
    ppmm = float(sys.argv[1]); out = sys.argv[2]
    arr = pintar(ppmm)
    dpi = ppmm * 25.4
    img = Image.fromarray(arr)
    img.save(out, dpi=(dpi, dpi))
    print(out, arr.shape, f'{dpi:.0f} ppp')
    pdf = sys.argv[3] if len(sys.argv) > 3 else os.path.join(os.path.dirname(out), 'fondo-cielo-A4-imprimir-dos.pdf')
    hoja_a4.dos(img, dpi, LADO, SANGRADO).guarda(pdf, 'Derriba al escuadrón - dos fondos de cielo 139 mm')
    print(pdf)
