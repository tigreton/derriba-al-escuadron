// Derriba al escuadrón — Boceto B aviones: escuadrón con puntos
// Lámina diana de 139 x 139 mm, como mucho 3 mm de alto.
// Ajustes: Ventana > Personalizador. Para exportar: elige "parte", F6 y luego F7.
// Coordenadas en mm, origen en la esquina inferior izquierda, vista desde el lado del tirador.

/* [Salida] */
// Pieza a generar
parte = "completa"; // [completa:Lámina completa (1 cuerpo), base:Multimaterial - cielo, relieve:Multimaterial - relieve, dianas:Multimaterial - dianas y pestañas, probeta:Probeta de pestañas, vista:Vista en color]

/* [Versión] */
// Express: lámina lisa y fina, sin relieve. Mínima: al revés, solo se imprimen los aviones y el cielo queda vacío
version = "normal"; // [normal:Normal (con relieve), express:Express (liviana y rápida), minima:Mínima (solo aviones, cielo sin imprimir)]
// Grosor de las versiones express y mínima (mínimo razonable: pestaña + 0,6 mm)
grosor_express = 1.2;
// Opciones de la versión normal (express y mínima las apagan todas)
mostrar_numeros = true;
mostrar_rebordes = true;
mostrar_marco = true;
mostrar_nubes = true;
mostrar_anillos = true;

/* [Versión mínima] */
// Marco exterior que sujeta todo y encaja en el portadianas
marco_minima = 4;
// Ancho de los soportes que unen los aviones al marco
soporte_ancho = 3;
// Material de avión que queda como mínimo alrededor del hueco de la diana
pared_min = 0.8;

/* [Lámina] */
lado = 139;
radio_esquina = 4;
// Grosor de la lámina (cielo y dianas) en la versión normal, sin contar el relieve
grosor_lamina = 2.0;
// Marco, rebordes de los huecos y puntos
relieve_alto = 0.8;
// Nubes y anillos de las dianas
relieve_bajo = 0.6;
marco_ancho = 3;
// Reborde alrededor de cada hueco
borde_ancho = 0.8;

/* [Pestaña] */
// Grosor: múltiplo de la altura de capa (0.2 -> 3 capas)
pestana_grosor = 0.6;
pestana_ancho = 1.5;
// Largo libre entre la diana y la lámina. Si el hueco es mayor, un saliente de la lámina sale a buscar la pestaña
pestana_largo = 1.5;
// Ancho del saliente que sujeta la pestaña
anclaje_ancho = 3.5;
// Cuánto se mete la pestaña dentro de la lámina
pestana_solape = 0.6;

/* [Dianas] */
// Multiplica todos los diámetros de diana
escala_diana = 1.0;
// Avisa si el hueco entre diana y avión queda por debajo de esto
holgura_min = 1.2;

/* [Probeta] */
probeta_grosores = [0.4, 0.6, 0.8, 1.0];
probeta_diana = 10;
probeta_holgura = 2.5;

/* [Hidden] */
$fn = 48;
FUENTE = "Liberation Sans:style=Bold";

MINIMA = version == "minima";
FINA = version == "express" || MINIMA;
GROSOR = FINA ? grosor_express : grosor_lamina;
CON_NUMEROS = !FINA && mostrar_numeros;
CON_REBORDES = !FINA && mostrar_rebordes;
CON_MARCO = !FINA && mostrar_marco;
CON_NUBES = !FINA && mostrar_nubes;
CON_ANILLOS = !FINA && mostrar_anillos;
CON_RELIEVE_ALTO = CON_NUMEROS || CON_REBORDES || CON_MARCO;
CON_RELIEVE = CON_RELIEVE_ALTO || CON_NUBES || CON_ANILLOS;
ALTURA = GROSOR + (CON_RELIEVE_ALTO ? relieve_alto : CON_RELIEVE ? relieve_bajo : 0);

// [nombre, x, y, giro, Ø diana, puntos, [x, y] de la insignia,
//  [envergadura, morro, cola, fuselaje, cuerda raíz, cuerda punta, flecha, env. cola, cuerda cola, flecha cola]]
AVIONES = [
    ["Bombardero",     48,  83, -45, 14, 1, [ 78,  81], [70, 20, 28, 12, 16, 8,   3,    28, 8, 2  ]],
    ["Transporte",    106,  43,   0, 11, 2, [129,  27], [56, 16, 24, 10, 13, 7,   2,    22, 7, 1.5]],
    ["Caza",          108, 109, -90,  9, 3, [127, 127], [44, 18, 22,  8, 14, 5,  11,    18, 6, 3  ]],
    ["Reactor delta",  28,  27, -30,  7, 4, [ 12,  47], [34, 15, 13,  6, 24, 2.5, 21.5,  0, 0, 0  ]],
    ["Avioneta",       66,  21,  20,  6, 5, [ 88,  13], [30,  9, 14,  6,  8, 5,   0.5,  12, 4, 0.5]],
];
// Versión mínima: soportes [punto en el avión, punto en el borde]; se recortan al tamaño de la lámina
SOPORTES = [
    [[ 25.7, 106.7], [  0, 106.7]],   // bombardero, ala izquierda
    [[ 29.6,  64.6], [  0,  64.6]],   // bombardero, cola
    [[ 71.7,  60.7], [ 80.5,  44  ]], // bombardero - transporte
    [[131.5,  44  ], [139,  44  ]],   // transporte, ala derecha
    [[106,    21  ], [106,   0  ]],   // transporte, cola
    [[101.5, 128.5], [101.5, 139]],   // caza, ala izquierda
    [[123,   109  ], [139, 109  ]],   // caza, morro
    [[ 10.1,  24.9], [  0,  24.9]],   // delta, ala izquierda
    [[ 35.2,  10.4], [ 35.2,  0 ]],   // delta, ala derecha
    [[ 70.1,   9.7], [ 70.1,  0 ]],   // avioneta, cola
    [[ 77.4,  26.2], [ 80.5,  44]],   // avioneta - transporte
];
// [x, y, escala]
NUBES = [[18, 123, 0.8], [60, 126, 0.8], [124, 77, 0.7], [86, 67, 0.7], [106, 9, 0.8], [12, 69, 0.6]];

if (ALTURA > 3) echo(str("AVISO: la lámina mide ", ALTURA, " mm, pasa de 3 mm"));
assert(relieve_bajo <= relieve_alto, "relieve_bajo debe ser <= relieve_alto");
assert(pestana_grosor < GROSOR, "La pestaña debe ser más fina que la lámina");

// ---------------- geometría ----------------
function bez2(p0, p1, p2, n = 8) = [for (i = [0:n]) let(t = i / n) (1 - t) * (1 - t) * p0 + 2 * (1 - t) * t * p1 + t * t * p2];

// Silueta vista desde arriba, morro hacia +y, origen en el centro de la diana
function silueta(g) = let(
    S = g[0], morro = g[1], cola = g[2], hw = g[3] / 2, cr = g[4], ct = g[5], fl = g[6],
    ts = g[7], tc = g[8], tsw = g[9],
    k = min(morro * 0.45, 2.2 * g[3]),
    der = concat(
        [[hw, cr / 2], [S / 2, cr / 2 - fl], [S / 2, cr / 2 - fl - ct], [hw, -cr / 2]],
        ts > 0 ? [[hw * 0.8, -(cola - tc)], [ts / 2, -(cola - tc + tsw)], [ts / 2, -cola], [hw * 0.5, -cola]]
               : [[hw * 0.6, -cola]]),
    izq = [for (i = [len(der) - 1:-1:0]) [-der[i][0], der[i][1]]],
    morro_d = bez2([0, morro], [hw, morro], [hw, morro - k]),
    morro_i = bez2([-hw, morro - k], [-hw, morro], [0, morro])
) concat(morro_d, der, izq, [for (i = [0:len(morro_i) - 2]) morro_i[i]]);

// Punto del contorno más cercano al centro de la diana (ahí va la pestaña)
function punto_seg(a, b) = let(d = b - a, t = max(0, min(1, -(a * d) / (d * d)))) a + t * d;
function punto_cercano(pts) = let(
    c = [for (i = [0:len(pts) - 1]) punto_seg(pts[i], pts[(i + 1) % len(pts)])],
    ds = [for (q = c) norm(q)],
    m = min(ds)
) [for (i = [0:len(c) - 1]) if (ds[i] == m) c[i]][0];

function radio(a) = a[4] * escala_diana / 2;
function un_decimal(x) = let(d = round(x * 10)) str(floor(d / 10), ".", d % 10);

module en_avion(a) translate([a[1], a[2]]) rotate(a[3]) children();

// ---------------- piezas 2D ----------------
module placa() offset(r = radio_esquina) offset(delta = -radio_esquina) square(lado);
module huecos() for (a = AVIONES) en_avion(a) polygon(silueta(a[7]));
module cielo() difference() { placa(); huecos(); }
module discos() for (a = AVIONES) en_avion(a) circle(r = radio(a), $fn = 72);

// Largo libre real de la pestaña: el pedido, o el hueco entero si no da para más
function largo_libre(a) = min(pestana_largo, norm(punto_cercano(silueta(a[7]))) - radio(a));

// Pestaña fina: va del centro de la diana hasta dentro de la lámina (lo que queda tapado no se ve)
module pestanas() if (MINIMA) pestanas_minima(); else for (a = AVIONES) {
    q = punto_cercano(silueta(a[7]));
    en_avion(a) rotate(atan2(q[1], q[0]))
        translate([0, -pestana_ancho / 2]) square([norm(q) + pestana_solape, pestana_ancho]);
}

// Saliente de la lámina (grosor completo) que rellena el hueco hasta dejar solo pestana_largo libre
module anclajes() for (a = AVIONES) {
    q = punto_cercano(silueta(a[7]));
    desde = radio(a) + largo_libre(a);
    if (norm(q) - desde > 0.01)
        en_avion(a) rotate(atan2(q[1], q[0]))
            translate([desde, -anclaje_ancho / 2]) square([norm(q) - desde + pestana_solape, anclaje_ancho]);
}

// Versión mínima: hueco alrededor de la diana dentro del avión macizo
function hueco_min(a) = min(pestana_largo, norm(punto_cercano(silueta(a[7]))) - radio(a) - pared_min);

module soportes() for (s = SOPORTES)
    hull() { translate(s[0]) circle(d = soporte_ancho); translate(s[1]) circle(d = soporte_ancho); }

module estructura_minima() difference() {
    intersection() {
        placa();
        union() {
            difference() { placa(); offset(delta = -marco_minima) placa(); }
            for (a = AVIONES) en_avion(a) polygon(silueta(a[7]));
            soportes();
        }
    }
    for (a = AVIONES) en_avion(a) circle(r = radio(a) + hueco_min(a), $fn = 72);
}

// Pestaña de la versión mínima: hacia la cola, cruzando el hueco hasta el fuselaje
module pestanas_minima() for (a = AVIONES) {
    largo = radio(a) + hueco_min(a) + pestana_solape;
    en_avion(a) translate([-pestana_ancho / 2, -largo]) square([pestana_ancho, largo]);
}

module lamina_2d() if (MINIMA) estructura_minima(); else union() { cielo(); anclajes(); }

module anillos() for (a = AVIONES) {
    r = radio(a);
    en_avion(a) {
        for (f = (a[4] < 9 ? [0.62] : [0.7, 0.4]))
            difference() { circle(r = r * f + 0.25, $fn = 72); circle(r = r * f - 0.25, $fn = 72); }
        circle(r = min(0.9, r * 0.18), $fn = 24);
    }
}

module bordes() difference() { offset(r = borde_ancho) huecos(); huecos(); }
module marco() difference() { placa(); offset(delta = -marco_ancho) placa(); }

module nube(n) translate([n[0], n[1]]) scale(n[2]) {
    for (c = [[-6, 0, 4], [-1, 2.5, 5.5], [5, 1, 4.5], [9, -1, 3]]) translate([c[0], c[1]]) circle(r = c[2]);
    hull() { translate([-8, -2]) circle(r = 2); translate([10, -2]) circle(r = 2); }
}

module insignias() if (CON_NUMEROS) for (a = AVIONES) translate(a[6]) circle(r = 3.6);
// Los números se graban atravesando el relieve: salen del color de la base
module numeros() if (CON_NUMEROS) for (a = AVIONES) translate(a[6])
    text(str(a[5]), size = 4.2, font = FUENTE, halign = "center", valign = "center");

module relieve_bajo_2d() union() {
    difference() {
        intersection() {
            cielo();
            union() {
                if (CON_NUBES) for (n = NUBES) nube(n);
                if (CON_REBORDES) bordes();
                if (CON_MARCO) marco();
                insignias();
            }
        }
        numeros();
    }
    if (CON_ANILLOS) anillos();
}
module relieve_alto_2d() difference() {
    intersection() { cielo(); union() { if (CON_REBORDES) bordes(); if (CON_MARCO) marco(); insignias(); } }
    numeros();
}

// ---------------- piezas 3D ----------------
module relieve_3d() if (CON_RELIEVE) translate([0, 0, GROSOR]) {
    linear_extrude(relieve_bajo) relieve_bajo_2d();
    if (CON_RELIEVE_ALTO && relieve_alto > relieve_bajo)
        translate([0, 0, relieve_bajo]) linear_extrude(relieve_alto - relieve_bajo) relieve_alto_2d();
}

module completa() union() {
    linear_extrude(pestana_grosor) union() { lamina_2d(); discos(); pestanas(); }
    translate([0, 0, pestana_grosor]) linear_extrude(GROSOR - pestana_grosor) union() { lamina_2d(); discos(); }
    relieve_3d();
}

module base_mm() linear_extrude(GROSOR) lamina_2d();
module dianas_mm() union() {
    linear_extrude(GROSOR) discos();
    linear_extrude(pestana_grosor) difference() { pestanas(); lamina_2d(); }
}

module probeta() {
    n = len(probeta_grosores);
    d_hueco = probeta_diana + 2 * probeta_holgura;
    paso = d_hueco + 6;
    ancho = n * paso + 4;
    alto = d_hueco + 16;
    cy = alto - (d_hueco / 2 + 4);
    desde = probeta_diana / 2 + min(pestana_largo, probeta_holgura);
    // Etiquetas en relieve; en la versión sin relieve se graban para que la tira quede plana
    module etiquetas() for (i = [0:n - 1]) translate([2 + paso * (i + 0.5), 5])
        text(un_decimal(probeta_grosores[i]), size = 4, font = FUENTE, halign = "center", valign = "center");
    grabado = min(0.6, GROSOR / 2);
    difference() {
        linear_extrude(GROSOR) difference() {
            offset(r = 3) offset(delta = -3) square([ancho, alto]);
            for (i = [0:n - 1]) translate([2 + paso * (i + 0.5), cy]) difference() {
                circle(d = d_hueco, $fn = 72);
                translate([-anclaje_ancho / 2, -d_hueco]) square([anclaje_ancho, d_hueco - desde]);
            }
        }
        if (!CON_RELIEVE) translate([0, 0, GROSOR - grabado]) linear_extrude(grabado + 0.01) etiquetas();
    }
    for (i = [0:n - 1]) translate([2 + paso * (i + 0.5), cy]) {
        linear_extrude(GROSOR) circle(d = probeta_diana, $fn = 72);
        linear_extrude(probeta_grosores[i])
            translate([-pestana_ancho / 2, -(d_hueco / 2 + pestana_solape)])
                square([pestana_ancho, d_hueco / 2 + pestana_solape]);
        if (CON_ANILLOS) translate([0, 0, GROSOR]) linear_extrude(relieve_bajo) difference() {
            circle(r = probeta_diana * 0.35 + 0.25, $fn = 72);
            circle(r = probeta_diana * 0.35 - 0.25, $fn = 72);
        }
    }
    if (CON_RELIEVE) translate([0, 0, GROSOR]) linear_extrude(relieve_alto) etiquetas();
}

// ---------------- comprobaciones ----------------
function r2(x) = round(x * 100) / 100;
if (MINIMA) for (a = AVIONES) {
    hm = hueco_min(a);
    echo(str(a[0], ": diana Ø", r2(2 * radio(a)), " mm, hueco ", r2(hm), " mm, pared de avión ",
             r2(norm(punto_cercano(silueta(a[7]))) - radio(a) - hm), " mm",
             hm < holgura_min ? "  <-- HUECO DEMASIADO JUSTO" : ""));
}
if (!MINIMA) for (a = AVIONES) {
    h = norm(punto_cercano(silueta(a[7]))) - radio(a);
    echo(str(a[0], ": diana Ø", r2(2 * radio(a)), " mm, hueco ", r2(h), " mm, pestaña libre ", r2(largo_libre(a)),
             " mm, saliente ", r2(h - largo_libre(a)), " mm",
             h < holgura_min ? "  <-- HUECO DEMASIADO JUSTO" : "",
             pestana_largo > h ? "  <-- el hueco no da para el largo pedido" : ""));
}
echo(str("Pestaña: ", pestana_grosor, " x ", pestana_ancho, " mm, largo libre ", pestana_largo, " mm"));
echo(str("Versión ", version, ": lámina ", GROSOR, " mm, altura total ", ALTURA, " mm",
         CON_RELIEVE ? "" : " (sin relieve)"));
if (parte == "relieve" && !CON_RELIEVE) echo("AVISO: esta versión no tiene relieve, la pieza sale vacía");

// ---------------- salida ----------------
if (parte == "completa") completa();
else if (parte == "base") base_mm();
else if (parte == "relieve") relieve_3d();
else if (parte == "dianas") dianas_mm();
else if (parte == "probeta") probeta();
else if (parte == "vista") {
    color("#378ADD") base_mm();
    color("#E24B4A") dianas_mm();
    color("#F4F9FE") relieve_3d();
}
