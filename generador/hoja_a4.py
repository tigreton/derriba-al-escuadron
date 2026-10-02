"""Hojas A4 a tamaño real para los fondos de 139 x 139 mm: marcas de corte, instrucciones y barra de escala.

Las usan fondo_cielo.py y fondo_cielo_ruido.py. El fondo llega como imagen PIL con el mismo sangrado
en los cuatro lados; la hoja se guarda como PDF de una página a la misma resolución.
"""
import os
from PIL import Image, ImageDraw, ImageFont

A4 = (210.0, 297.0)
GRIS = (90, 90, 90)


class Hoja:
    def __init__(self, ppp):
        self.ppp = ppp
        self.img = Image.new("RGB", (int(round(self.mm(A4[0]))), int(round(self.mm(A4[1])))), "white")
        self.d = ImageDraw.Draw(self.img)

    def mm(self, v):
        return v * self.ppp / 25.4

    def fuente(self, tam_mm, negrita=False):
        nombre = "arialbd.ttf" if negrita else "arial.ttf"
        for ruta in (os.path.join(os.environ.get("WINDIR", r"C:\Windows"), "Fonts", nombre), nombre,
                     "DejaVuSans-Bold.ttf" if negrita else "DejaVuSans.ttf"):
            try:
                return ImageFont.truetype(ruta, int(round(self.mm(tam_mm))))
            except OSError:
                pass
        return ImageFont.load_default()

    def raya(self, xa, ya, xb, yb):
        mm = self.mm
        self.d.line([(mm(xa), mm(ya)), (mm(xb), mm(yb))], fill="black", width=max(1, int(round(mm(0.25)))))

    def texto(self, x, y, texto, tam, negrita=False, color=GRIS):
        self.d.text((self.mm(x), self.mm(y)), texto, font=self.fuente(tam, negrita), fill=color)

    def texto_girado(self, x, y, texto, tam, negrita=False, color=(0, 0, 0)):
        """Texto que se lee de abajo arriba. (x, y) en mm es la esquina de abajo a la izquierda."""
        f = self.fuente(tam, negrita)
        _, _, ancho, alto = f.getbbox(texto)
        m = Image.new("L", (ancho, alto), 0)
        ImageDraw.Draw(m).text((0, 0), texto, font=f, fill=255)
        m = m.rotate(90, expand=True)
        self.img.paste(color, (int(round(self.mm(x))), int(round(self.mm(y))) - m.height), m)

    def barra_escala(self, x, y, vertical=False):
        """Barra de 100 mm en tramos de 10. (x, y) en mm es el cero; la vertical sube desde ahí."""
        mm, d = self.mm, self.d
        g = max(1, int(round(mm(0.25))))
        for i in range(10):
            if vertical:
                caja = [mm(x), mm(y - i * 10 - 10), mm(x + 2.5), mm(y - i * 10)]
            else:
                caja = [mm(x + i * 10), mm(y), mm(x + i * 10 + 10), mm(y + 2.5)]
            d.rectangle(caja, fill="black" if i % 2 == 0 else "white", outline="black", width=g)
        for i in (0, 5, 10):
            etiqueta = "100 mm" if i == 10 else str(i * 10)
            if vertical:
                d.text((mm(x + 3.8), mm(y - i * 10)), etiqueta, font=self.fuente(2.8), fill=GRIS, anchor="lm")
            else:
                d.text((mm(x + i * 10), mm(y + 3.8)), etiqueta, font=self.fuente(2.8), fill=GRIS,
                       anchor="ma" if i else "la")

    def guarda(self, ruta, titulo):
        self.img.save(ruta, resolution=self.ppp, quality=94, title=titulo)


def una(fondo, ppp, lado, sangrado, arriba=32.0):
    """Un fondo por A4, con sangrado en los cuatro lados, marcas de corte e instrucciones."""
    h = Hoja(ppp)
    x = (A4[0] - lado) / 2
    h.img.paste(fondo, (int(round(h.mm(x - sangrado))), int(round(h.mm(arriba - sangrado)))))

    # marcas de corte: fuera del sangrado, alineadas con el borde de la lámina
    sep, largo = sangrado + 1.5, 6.0
    for cx in (x, x + lado):
        for cy in (arriba, arriba + lado):
            sx = -1 if cx == x else 1
            sy = -1 if cy == arriba else 1
            h.raya(cx + sx * sep, cy, cx + sx * (sep + largo), cy)
            h.raya(cx, cy + sy * sep, cx, cy + sy * (sep + largo))

    h.texto(x, 8, "Derriba al escuadrón · fondo de cielo", 5, True, "black")
    h.texto(x, 14.5, f"Lámina de {lado:g} × {lado:g} mm · corta por las marcas", 3.4)

    y = arriba + lado + sangrado + 12
    textos = [
        ("Imprime a TAMAÑO REAL (100 %).", True),
        (f"Desactiva «Ajustar a la página» o «Reducir»; si no, la lámina no saldrá de {lado:g} mm.", False),
        ("Comprueba la escala con la barra: tiene que medir 100 mm.", False),
        (f"Lleva {sangrado:g} mm de sangrado: corta por las marcas y el azul llega hasta el borde.", False),
        ("Va detrás de la lámina, sobre todo de la versión mínima: el cielo se ve por los huecos.", False),
        ("Papel o cartulina de 120-200 g/m², mate, para que no se ondule ni brille.", False),
    ]
    for t, negrita in textos:
        h.texto(x, y, t, 3.6 if negrita else 3.2, negrita, "black" if negrita else GRIS)
        y += 6.2
    h.barra_escala(x, y + 5)
    return h


def dos(fondo, ppp, lado, sangrado):
    """Dos fondos por A4, uno encima del otro y pegados: el corte del medio sirve para los dos.

    Solo hay sangrado por fuera. Las instrucciones y la barra van giradas en los márgenes de los lados.
    """
    h = Hoja(ppp)
    mm = h.mm
    x = (A4[0] - lado) / 2
    arriba = (A4[1] - 2 * lado) / 2
    abajo = arriba + 2 * lado
    x0 = int(round(mm(x - sangrado)))
    y0 = int(round(mm(arriba - sangrado)))
    junta = int(round(mm(arriba + lado)))
    s = int(round(mm(sangrado)))
    h.img.paste(fondo.crop((0, 0, fondo.width, junta - y0)), (x0, y0))
    h.img.paste(fondo.crop((0, s, fondo.width, fondo.height)), (x0, junta))

    # cortes horizontales: marcas en los márgenes de los lados
    sep, largo = sangrado + 1.5, 6.0
    for y in (arriba, arriba + lado, abajo):
        h.raya(x - sep, y, x - sep - largo, y)
        h.raya(x + lado + sep, y, x + lado + sep + largo, y)
    # cortes verticales: arriba y abajo no queda margen, la marca se mete en el sangrado (que se tira)
    for cx in (x, x + lado):
        h.raya(cx, arriba - sangrado - 3, cx, arriba - 0.8)
        h.raya(cx, abajo + 0.8, cx, abajo + sangrado + 3)

    izq = [
        ("Imprime a TAMAÑO REAL (100 %), sin «Ajustar a la página».", 3.4, True, (0, 0, 0)),
        ("Comprueba la escala: la barra de la derecha tiene que medir 100 mm.", 3.1, False, GRIS),
        (f"Corta por las marcas: salen dos fondos de {lado:g} × {lado:g} mm (mejor en cartulina mate).", 3.1, False, GRIS),
    ]
    for i, (t, tam, negrita, color) in enumerate(izq):
        h.texto_girado(8 + 5.5 * i, abajo - 8, t, tam, negrita, color)
    h.texto_girado(196, abajo - 8, "Derriba al escuadrón · fondo de cielo · 2 por hoja", 3.4, True)
    h.barra_escala(x + lado + sangrado + 8.5, arriba + 115, vertical=True)
    return h
