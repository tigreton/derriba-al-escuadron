"""Corte transversal de diana + pestaña (escala 22 px/mm)."""
K, X0, BED = 22.0, 50.0, 240.0
WATER, EDGE, REL, DISC, RING, LEAD = "#378ADD", "#185FA5", "#E6F1FB", "#E24B4A", "#FCEBEB", "#888780"
f = lambda v: f"{v:.1f}".rstrip("0").rstrip(".")
X = lambda mm: X0 + mm * K
Z = lambda mm: BED - mm * K
def box(x0, x1, z0, z1, fill, stroke=EDGE):
    return f'<rect x="{f(X(x0))}" y="{f(Z(z1))}" width="{f((x1-x0)*K)}" height="{f((z1-z0)*K)}" fill="{fill}" stroke="{stroke}" stroke-width="0.5"/>'
o = []
o.append(box(0, 5.0, 0, 2.0, WATER))
o.append(box(1.0, 1.6, 2.0, 2.8, REL)); o.append(box(4.2, 5.0, 2.0, 2.8, REL))
o.append(box(5.0, 6.3, 0, 0.6, DISC, "#A32D2D"))
o.append(box(6.3, 14.3, 0, 2.0, DISC, "#A32D2D"))
for a, b in [(7.57, 8.07), (9.58, 11.02), (12.53, 13.03)]:
    o.append(box(a, b, 2.0, 2.6, RING, "#A32D2D"))
o.append(box(15.6, 20.6, 0, 2.0, WATER))
o.append(box(15.6, 16.4, 2.0, 2.8, REL)); o.append(box(19.0, 19.6, 2.0, 2.8, REL))
o.append(f'<line x1="40" y1="{BED}" x2="515" y2="{BED}" stroke="{LEAD}" stroke-width="1"/>')
cx = X(10.3); r = 2.25 * K
o.append(f'<path d="M{f(cx-r)} 100V110.5A{f(r)} {f(r)} 0 0 0 {f(cx+r)} 110.5V100L{f(cx+30)} 86L{f(cx+r-2)} 50H{f(cx-r+2)}L{f(cx-30)} 86Z" fill="{LEAD}" stroke="#5F5E5A" stroke-width="0.5"/>')
o.append(f'<line class="leader" x1="{f(cx+r+4)}" y1="100" x2="515" y2="100"/><text class="ts" x="522" y="104">Balín 4,5 mm</text>')
for zmm, txt in [(2.8, "2,8 mm · relieve"), (2.0, "2,0 mm · color"), (0.6, "0,6 mm · pestaña")]:
    o.append(f'<line class="leader" x1="{f(X(20.6)+4)}" y1="{f(Z(zmm))}" x2="515" y2="{f(Z(zmm))}"/><text class="ts" x="522" y="{f(Z(zmm)+4)}">{txt}</text>')
o.append(f'<line class="leader" x1="{f(X(5.65))}" y1="{f(Z(0.3))}" x2="{f(X(5.65))}" y2="262"/><text class="ts" x="{f(X(5.65)-30)}" y="278">Pestaña de 1,5 mm de ancho</text>')
o.append(f'<line class="leader" x1="{f(X(14.95))}" y1="{f(Z(1.2))}" x2="{f(X(14.95))}" y2="300"/><text class="ts" x="{f(X(14.95)-30)}" y="316">Hueco pasante, holgura ≥1,2 mm</text>')
svg = ('<svg width="100%" viewBox="0 0 680 336" role="img"><title>Sección de diana y pestaña</title>'
       '<desc>Corte transversal: lámina de agua de 2 mm con relieve hasta 2,8 mm, diana de 8 mm unida por una pestaña fina de 0,6 mm en la base, y un balín de 4,5 mm a escala.</desc>'
       + "".join(o) + '</svg>')
import os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
css = ('<style>.ts{font:12px Arial,sans-serif;fill:#5F5E5A}'
       '.leader{stroke:#888780;stroke-width:.5;stroke-dasharray:3 3;fill:none}</style>')
std = svg.replace('<svg width="100%" viewBox="0 0 680 336" role="img">',
                  '<svg xmlns="http://www.w3.org/2000/svg" width="680" height="336" viewBox="0 0 680 336">' + css)
open(os.path.join(ROOT, "detalle-pestana.svg"), "w", encoding="utf-8").write(std)
if len(sys.argv) > 1:
    open(os.path.join(sys.argv[1], "widget-S.svg"), "w", encoding="utf-8").write(svg)
