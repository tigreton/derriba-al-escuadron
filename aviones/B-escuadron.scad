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

/* [Aviones] */
// Posición 1, centro izquierda (pensada para el gigante)
posicion_1 = "gigante"; // [pequeno:Pequeño - avioneta, mediano:Mediano - reactor delta, grande:Grande - caza, enorme:Enorme - transporte, gigante:Gigante - bombardero]
// Posición 2, abajo derecha (pensada para el enorme)
posicion_2 = "enorme"; // [pequeno:Pequeño - avioneta, mediano:Mediano - reactor delta, grande:Grande - caza, enorme:Enorme - transporte, gigante:Gigante - bombardero]
// Posición 3, arriba derecha (pensada para el grande)
posicion_3 = "grande"; // [pequeno:Pequeño - avioneta, mediano:Mediano - reactor delta, grande:Grande - caza, enorme:Enorme - transporte, gigante:Gigante - bombardero]
// Posición 4, abajo izquierda (pensada para el mediano)
posicion_4 = "mediano"; // [pequeno:Pequeño - avioneta, mediano:Mediano - reactor delta, grande:Grande - caza, enorme:Enorme - transporte, gigante:Gigante - bombardero]
// Posición 5, abajo centro (pensada para el pequeño)
posicion_5 = "pequeno"; // [pequeno:Pequeño - avioneta, mediano:Mediano - reactor delta, grande:Grande - caza, enorme:Enorme - transporte, gigante:Gigante - bombardero]
// Diámetro de la diana de cada tamaño, de pequeño a gigante
diametros_diana = [6, 7, 9, 11, 14];
// Inversa: cuanto más grande el avión, más pequeña la diana (y más puntos vale)
diana_inversa = false;

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

// Tipos de avión, de pequeño a gigante: [clave, tamaño, nombre,
//  [envergadura, morro, cola, fuselaje, cuerda raíz, cuerda punta, flecha, env. cola, cuerda cola, flecha cola]]
TIPOS = [
    ["pequeno", "pequeño", "Avioneta",      [30,  9, 14,  6,  8, 5,   0.5,  12, 4, 0.5]],
    ["mediano", "mediano", "Reactor delta", [34, 15, 13,  6, 24, 2.5, 21.5,  0, 0, 0  ]],
    ["grande",  "grande",  "Caza",          [44, 18, 22,  8, 14, 5,  11,    18, 6, 3  ]],
    ["enorme",  "enorme",  "Transporte",    [56, 16, 24, 10, 13, 7,   2,    22, 7, 1.5]],
    ["gigante", "gigante", "Bombardero",    [70, 20, 28, 12, 16, 8,   3,    28, 8, 2  ]],
];
// Posiciones en la lámina: [x, y, giro, [x, y] de la insignia, tipo para el que está pensado el sitio]
POSICIONES = [
    [ 48,  83, -45, [ 78,  81], 4],
    [106,  43,   0, [129,  27], 3],
    [108, 109, -90, [127, 127], 2],
    [ 28,  27, -30, [ 12,  47], 1],
    [ 66,  21,  20, [ 88,  13], 0],
];
ELEGIDOS = [posicion_1, posicion_2, posicion_3, posicion_4, posicion_5];

function tipo_idx(clave) = [for (i = [0:len(TIPOS) - 1]) if (TIPOS[i][0] == clave) i][0];
function diametro_tipo(i) = diana_inversa ? diametros_diana[len(TIPOS) - 1 - i] : diametros_diana[i];
// Cuanto más pequeña la diana, más puntos: la más pequeña vale 5 y la más grande 1
function puntos_diana(d) = 1 + len([for (x = diametros_diana) if (x > d) x]);

// [nombre, x, y, giro, Ø diana, puntos, [x, y] de la insignia, geometría, tipo, tipo previsto]
AVIONES = [for (k = [0:len(POSICIONES) - 1]) let(
        p = POSICIONES[k], t = tipo_idx(ELEGIDOS[k]), d = diametro_tipo(t))
    [str(TIPOS[t][2], " (", TIPOS[t][1], ")"), p[0], p[1], p[2], d, puntos_diana(d), p[3], TIPOS[t][3], t, p[4]]];

// Versión mínima: soportes [posición, punto del avión, destino]. El destino es un borde
// ("izq", "der", "arr", "aba") o [posición, punto] de otro avión. Puntos: ala_izq, ala_der, cola, morro
UNIONES = [
    [0, "ala_izq", "izq"],
    [0, "cola",    "izq"],
    [0, "ala_der", [1, "ala_izq"]],
    [1, "ala_der", "der"],
    [1, "cola",    "aba"],
    [2, "ala_izq", "arr"],
    [2, "morro",   "der"],
    [3, "ala_izq", "izq"],
    [3, "ala_der", "aba"],
    [4, "cola",    "aba"],
    [4, "ala_der", [1, "ala_izq"]],
];
function ancla_local(g, cual) = let(tip_y = g[4] / 2 - g[6] - g[5] / 2)
    cual == "ala_izq" ? [-(g[0] / 2 - 2.5), tip_y] :
    cual == "ala_der" ? [g[0] / 2 - 2.5, tip_y] :
    cual == "cola" ? [0, -(g[2] - 2)] : [0, g[1] - 3];
function ancla(k, cual) = let(a = AVIONES[k], q = ancla_local(a[7], cual))
    [a[1] + q[0] * cos(a[3]) - q[1] * sin(a[3]), a[2] + q[0] * sin(a[3]) + q[1] * cos(a[3])];
function destino(q, d) = d == "izq" ? [0, q[1]] : d == "der" ? [lado, q[1]] :
    d == "aba" ? [q[0], 0] : d == "arr" ? [q[0], lado] : ancla(d[0], d[1]);
SOPORTES = [for (u = UNIONES) let(q = ancla(u[0], u[1])) [q, destino(q, u[2])]];
// [x, y, escala]
NUBES = [[18, 123, 0.8], [60, 126, 0.8], [124, 77, 0.7], [86, 67, 0.7], [106, 9, 0.8], [12, 69, 0.6]];

if (ALTURA > 3) echo(str("AVISO: la lámina mide ", ALTURA, " mm, pasa de 3 mm"));
assert(relieve_bajo <= relieve_alto, "relieve_bajo debe ser <= relieve_alto");
assert(pestana_grosor < GROSOR, "La pestaña debe ser más fina que la lámina");
assert(len(diametros_diana) == len(TIPOS), "diametros_diana necesita un diámetro por tamaño (5)");

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
// Silueta del avión; si la diana no cabe en el cruce de ala y fuselaje, el centro se ensancha en redondo
module silueta_2d(a, margen) en_avion(a) union() {
    polygon(silueta(a[7]));
    circle(r = radio(a) + margen, $fn = 72);
}
// Si el centro tiene que ensancharse, el hueco queda del largo de la pestaña (y nunca menos que holgura_min)
MARGEN_HUECO = max(holgura_min, pestana_largo);
module huecos() for (a = AVIONES) silueta_2d(a, MARGEN_HUECO);
module cielo() difference() { placa(); huecos(); }
module discos() for (a = AVIONES) en_avion(a) circle(r = radio(a), $fn = 72);

// Distancia del centro de la diana al borde del hueco, en la dirección de la pestaña
function dist_borde(a) = max(norm(punto_cercano(silueta(a[7]))), radio(a) + MARGEN_HUECO);
// Largo libre real de la pestaña: el pedido, o el hueco entero si no da para más
function largo_libre(a) = min(pestana_largo, dist_borde(a) - radio(a));

// Pestaña fina: va del centro de la diana hasta dentro de la lámina (lo que queda tapado no se ve)
module pestanas() if (MINIMA) pestanas_minima(); else for (a = AVIONES) {
    q = punto_cercano(silueta(a[7]));
    en_avion(a) rotate(atan2(q[1], q[0]))
        translate([0, -pestana_ancho / 2]) square([dist_borde(a) + pestana_solape, pestana_ancho]);
}

// Saliente de la lámina (grosor completo) que rellena el hueco hasta dejar solo pestana_largo libre
module anclajes() for (a = AVIONES) {
    q = punto_cercano(silueta(a[7]));
    desde = radio(a) + largo_libre(a);
    if (dist_borde(a) - desde > 0.01)
        en_avion(a) rotate(atan2(q[1], q[0]))
            translate([desde, -anclaje_ancho / 2]) square([dist_borde(a) - desde + pestana_solape, anclaje_ancho]);
}

// Versión mínima: el hueco alrededor de la diana es el largo de la pestaña
function hueco_min(a) = pestana_largo;

module soportes() for (s = SOPORTES)
    hull() { translate(s[0]) circle(d = soporte_ancho); translate(s[1]) circle(d = soporte_ancho); }

module estructura_minima() difference() {
    intersection() {
        placa();
        union() {
            difference() { placa(); offset(delta = -marco_minima) placa(); }
            for (a = AVIONES) silueta_2d(a, hueco_min(a) + pared_min);
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
for (k = [0:len(AVIONES) - 1]) {
    a = AVIONES[k];
    hp = norm(punto_cercano(silueta(a[7]))) - radio(a);
    h = MINIMA ? hueco_min(a) : dist_borde(a) - radio(a);
    echo(str("Posición ", k + 1, ": ", a[0], ", diana Ø", r2(2 * radio(a)), " mm, ", a[5], a[5] == 1 ? " punto" : " puntos", ", hueco ", r2(h), " mm",
             MINIMA ? "" : str(", pestaña libre ", r2(largo_libre(a)), " mm, saliente ", r2(h - largo_libre(a)), " mm"),
             h < holgura_min - 0.001 ? "  <-- HUECO DEMASIADO JUSTO" : "",
             (MINIMA ? hp < h + pared_min : hp < MARGEN_HUECO) ? "  (el centro del avión se ensancha para que quepa la diana)" : ""));
    if (TIPOS[a[8]][3][0] > TIPOS[a[9]][3][0])
        echo(str("AVISO: en la posición ", k + 1, " hay un avión más grande que el previsto (", TIPOS[a[9]][2],
                 "). Mira la vista previa por si se solapa con otro"));
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
