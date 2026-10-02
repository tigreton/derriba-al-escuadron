// Derriba al escuadrón — 3 contra 3: dos escuadrones enfrentados
// Lámina diana de 139 x 139 mm, como mucho 3 mm de alto. Mismos ajustes que B-escuadron.scad.
// El escuadrón B es el A girado 180° sobre el centro: los dos jugadores ven la misma lámina.
// Ajustes: Ventana > Personalizador. Para exportar: elige "parte", F6 y luego F7.
// Coordenadas en mm, origen en la esquina inferior izquierda, vista desde el lado del tirador.

/* [Salida] */
// Pieza a generar
parte = "completa"; // [completa:Lámina completa (1 cuerpo), base:Multimaterial - cielo, relieve:Multimaterial - relieve, dianas:Multimaterial - dianas de los dos bandos, dianas_a:Multimaterial - dianas del bando A, dianas_b:Multimaterial - dianas del bando B, probeta:Probeta de pestañas, vista:Vista en color]

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
// Línea de frente en relieve entre los dos bandos
mostrar_frente = true;
// Insignia de cada bando: disco del color de sus dianas con la letra en relieve
mostrar_insignias = true;

/* [Aviones] */
// Dónde van los aviones. Las dos disposiciones usan la misma lámina, tipos y pestañas
disposicion = "frente"; // [frente:Frente - cara a cara, esquinas:Esquinas - en abanico desde las esquinas]
// Posición 1 de cada bando, pensada para el grande (frente: retaguardia, en el ala de arriba; esquinas: por la diagonal)
posicion_1 = "grande"; // [pequeno:Pequeño - avioneta, mediano:Mediano - caza, grande:Grande - bombardero]
// Posición 2 de cada bando, pensada para el mediano (frente: en cabeza, morro con morro; esquinas: pegado al borde)
posicion_2 = "mediano"; // [pequeno:Pequeño - avioneta, mediano:Mediano - caza, grande:Grande - bombardero]
// Posición 3 de cada bando, pensada para el pequeño (frente: retaguardia, en el ala de abajo; esquinas: pegado al otro borde)
posicion_3 = "pequeno"; // [pequeno:Pequeño - avioneta, mediano:Mediano - caza, grande:Grande - bombardero]
// Diámetro de la diana de cada tamaño, de pequeño a grande
diametros_diana = [6, 8, 11];
// Puntos de cada diana, de la más pequeña a la más grande
puntos_por_diana = [5, 3, 1];
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
// Marco, rebordes de los huecos, puntos e insignias
relieve_alto = 0.8;
// Nubes, línea de frente y anillos de las dianas
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
COLORES = ["#E24B4A", "#0C447C"];   // dianas e insignia del bando A y del B
BANDOS = ["A", "B"];

MINIMA = version == "minima";
FINA = version == "express" || MINIMA;
GROSOR = FINA ? grosor_express : grosor_lamina;
CON_NUMEROS = !FINA && mostrar_numeros;
CON_REBORDES = !FINA && mostrar_rebordes;
CON_MARCO = !FINA && mostrar_marco;
CON_NUBES = !FINA && mostrar_nubes;
CON_ANILLOS = !FINA && mostrar_anillos;
CON_FRENTE = !FINA && mostrar_frente;
CON_INSIGNIAS = !FINA && mostrar_insignias;
CON_RELIEVE_ALTO = CON_NUMEROS || CON_REBORDES || CON_MARCO || CON_INSIGNIAS;
CON_RELIEVE = CON_RELIEVE_ALTO || CON_NUBES || CON_ANILLOS || CON_FRENTE;
ALTURA = GROSOR + (CON_RELIEVE_ALTO ? relieve_alto : CON_RELIEVE ? relieve_bajo : 0);

// Tipos de avión, de pequeño a grande: [clave, tamaño, nombre,
//  [envergadura, morro, cola, fuselaje, cuerda raíz, cuerda punta, flecha, env. cola, cuerda cola, flecha cola]]
TIPOS = [
    ["pequeno", "pequeño", "Avioneta",   [30,  9, 14,  6,  8, 5, 0.5, 12, 4, 0.5]],
    ["mediano", "mediano", "Caza",       [40, 16, 19,  8, 12, 5, 9,   14, 5, 2.5]],
    ["grande",  "grande",  "Bombardero", [54, 16, 22, 10, 14, 7, 2.5, 20, 7, 1.5]],
];
// Disposiciones: [clave, posiciones del bando A, insignia del bando A, nubes, soportes del bando A, línea de frente]
//  El bando B sale de girar el A 180° sobre el centro (posiciones, insignias y soportes)
//  Posiciones: [x, y, giro, [x, y] de la insignia de puntos, tipo para el que está pensado el sitio]
//  Nubes: [x, y, escala]
//  Soportes: [posición, punto del avión, destino]. El destino es un borde ("izq", "der", "arr", "aba")
//  o [posición, punto] de otro avión (0-2 bando A, 3-5 bando B). Puntos: ala_izq, ala_der, cola, morro
//  Línea de frente: [desde, hasta]
DISPOSICIONES = [
    // A sale por la izquierda con el morro a la derecha: el caza en cabeza, morro con morro con el de B
    ["frente",
        [[32, 106, -90, [57, 95], 2],
         [51, 69.5, -90, [58, 50], 1],
         [31,  29, -90, [13, 51], 0]],
        [14, 69.5],
        [[68.5, 124, 0.75], [70.5, 15, 0.75], [81.5, 100, 0.5], [57.5, 39, 0.5]],
        [[0, "ala_izq", "arr"],
         [0, "cola",    "izq"],
         [0, "ala_der", [1, "ala_izq"]],
         [1, "ala_der", [2, "ala_izq"]],
         [1, "morro",   [4, "morro"]],
         [2, "ala_der", "aba"],
         [2, "cola",    "izq"]],
        [[69.5, 6], [69.5, 133]]],
    // A sale en abanico de la esquina de abajo a la izquierda: el grande por la diagonal,
    // el mediano pegado al borde de abajo y el pequeño pegado al de la izquierda
    ["esquinas",
        [[37, 37, -45, [60, 36], 2],
         [83, 27, -72, [106, 13], 1],
         [22, 78, -18, [39, 60], 0]],
        [11.5, 11.5],
        [[69.5, 70.5, 0.75], [31, 112, 0.6], [108, 27, 0.6]],
        [[0, "cola",    "izq"],
         [0, "ala_izq", [2, "cola"]],
         [0, "ala_der", [1, "cola"]],
         [1, "ala_der", "aba"],
         [1, "morro",   "der"],
         [2, "ala_izq", "izq"],
         [2, "morro",   "arr"]],
        [[7, 132], [132, 7]]],
];
DISPOSICION = [for (d = DISPOSICIONES) if (d[0] == disposicion) d][0];
// Girar 180° sobre el centro de la lámina
function girar(p) = [lado - p[0], lado - p[1]];
function posicion_b(p) = [lado - p[0], lado - p[1], p[2] + 180, girar(p[3]), p[4]];
function destino_b(d) = d == "izq" ? "der" : d == "der" ? "izq" : d == "arr" ? "aba" : d == "aba" ? "arr"
    : [(d[0] + 3) % 6, d[1]];
POSICIONES_A = DISPOSICION[1];
POSICIONES = concat(POSICIONES_A, [for (p = POSICIONES_A) posicion_b(p)]);
INSIGNIAS_BANDO = [DISPOSICION[2], girar(DISPOSICION[2])];
NUBES = DISPOSICION[3];
UNIONES = concat(DISPOSICION[4], [for (u = DISPOSICION[4]) [u[0] + 3, u[1], destino_b(u[2])]]);
FRENTE = DISPOSICION[5];
ELEGIDOS = [posicion_1, posicion_2, posicion_3];

function tipo_idx(clave) = [for (i = [0:len(TIPOS) - 1]) if (TIPOS[i][0] == clave) i][0];
function diametro_tipo(i) = diana_inversa ? diametros_diana[len(TIPOS) - 1 - i] : diametros_diana[i];
// Cuanto más pequeña la diana, más puntos
function puntos_diana(d) = puntos_por_diana[len([for (x = diametros_diana) if (x < d) x])];

// Si el centro tiene que ensancharse, el hueco queda del largo de la pestaña (y nunca menos que holgura_min)
MARGEN_HUECO = max(holgura_min, pestana_largo);
// Lo que necesita la diana a su alrededor: hueco, y en la versión mínima además la pared de avión
MARGEN_DIANA = MINIMA ? pestana_largo + pared_min : MARGEN_HUECO;

// Avión más rechoncho: fuselaje, raíz del ala y cola más anchos; la envergadura no cambia
function engordar(g, f) = let(cr = g[4] * f) [
    g[0],
    max(g[1], cr / 2 + 3),
    max(g[2], g[7] > 0 ? cr / 2 + g[8] + 1.5 : cr / 2 + 1),
    g[3] * f, cr, g[5] * sqrt(f), g[6], g[7] * f, g[8], g[9]];
function cabe(g, r) = norm(punto_cercano(silueta(g))) >= r + MARGEN_DIANA - 0.001;
// El menor engorde (de 1 a 3) con el que cabe la diana
function factor_engorde(g, r) = let(ok = [for (i = [0:40]) let(f = 1 + i * 0.05) if (cabe(engordar(g, f), r)) f])
    len(ok) > 0 ? ok[0] : 3;

// [nombre, x, y, giro, Ø diana, puntos, [x, y] de la insignia, geometría, tipo, tipo previsto, engorde, bando (0 A, 1 B)]
AVIONES = [for (k = [0:len(POSICIONES) - 1]) let(
        p = POSICIONES[k], t = tipo_idx(ELEGIDOS[k % 3]), d = diametro_tipo(t),
        f = factor_engorde(TIPOS[t][3], d * escala_diana / 2))
    [str(TIPOS[t][2], " (", TIPOS[t][1], ")"), p[0], p[1], p[2], d, puntos_diana(d), p[3],
     engordar(TIPOS[t][3], f), t, p[4], f, k < 3 ? 0 : 1]];

// Versión mínima: dónde se agarra cada soporte (los soportes de cada disposición van en DISPOSICIONES)
function ancla_local(g, cual) = let(tip_y = g[4] / 2 - g[6] - g[5] / 2)
    cual == "ala_izq" ? [-(g[0] / 2 - 2.5), tip_y] :
    cual == "ala_der" ? [g[0] / 2 - 2.5, tip_y] :
    cual == "cola" ? [0, -(g[2] - 2)] : [0, g[1] - 3];
function ancla(k, cual) = let(a = AVIONES[k], q = ancla_local(a[7], cual))
    [a[1] + q[0] * cos(a[3]) - q[1] * sin(a[3]), a[2] + q[0] * sin(a[3]) + q[1] * cos(a[3])];
function destino(q, d) = d == "izq" ? [0, q[1]] : d == "der" ? [lado, q[1]] :
    d == "aba" ? [q[0], 0] : d == "arr" ? [q[0], lado] : ancla(d[0], d[1]);
SOPORTES = [for (u = UNIONES) let(q = ancla(u[0], u[1])) [q, destino(q, u[2])]];

assert(DISPOSICION != undef, str("No hay ninguna disposición llamada \"", disposicion, "\""));
if (ALTURA > 3) echo(str("AVISO: la lámina mide ", ALTURA, " mm, pasa de 3 mm"));
assert(relieve_bajo <= relieve_alto, "relieve_bajo debe ser <= relieve_alto");
assert(pestana_grosor < GROSOR, "La pestaña debe ser más fina que la lámina");
assert(len(diametros_diana) == len(TIPOS), "diametros_diana necesita un diámetro por tamaño (3)");
assert(len(puntos_por_diana) == len(TIPOS), "puntos_por_diana necesita un valor por diana (3)");

// ---------------- geometría ----------------
function bez2(p0, p1, p2, n = 8) = [for (i = [0:n]) let(t = i / n) (1 - t) * (1 - t) * p0 + 2 * (1 - t) * t * p1 + t * t * p2];

// Silueta vista desde arriba, morro hacia +y, origen en el centro de la diana
function silueta(g) = let(
    S = g[0], morro = g[1], cola = g[2], hw = g[3] / 2, cr = g[4], ct = g[5], fl = g[6],
    ts = g[7], tc = g[8], tsw = g[9],
    k = min(morro * 0.45, 2.2 * g[3], morro - cr / 2 - 0.5),
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
// ¿Es del bando pedido? (-1: de los dos)
function del_bando(a, e) = e < 0 || a[11] == e;

module en_avion(a) translate([a[1], a[2]]) rotate(a[3]) children();

// ---------------- piezas 2D ----------------
module placa() offset(r = radio_esquina) offset(delta = -radio_esquina) square(lado);
// Silueta del avión; si la diana no cabe en el cruce de ala y fuselaje, el centro se ensancha en redondo
module silueta_2d(a, margen) en_avion(a) union() {
    polygon(silueta(a[7]));
    circle(r = radio(a) + margen, $fn = 72);
}
module huecos() for (a = AVIONES) silueta_2d(a, MARGEN_HUECO);
module cielo() difference() { placa(); huecos(); }

// Insignia de bando: disco del color de las dianas, con aro y letra en relieve
module disco_bando(e) if (CON_INSIGNIAS) translate(INSIGNIAS_BANDO[e]) circle(r = 4.6, $fn = 72);
module aros_bando() if (CON_INSIGNIAS) for (e = [0, 1]) translate(INSIGNIAS_BANDO[e])
    difference() { circle(r = 6.2, $fn = 72); circle(r = 4.6, $fn = 72); }
module letras_bando() if (CON_INSIGNIAS) for (e = [0, 1]) translate(INSIGNIAS_BANDO[e])
    text(BANDOS[e], size = 5, font = FUENTE, halign = "center", valign = "center");

// Lo que va del color de un bando: sus dianas y su insignia (-1: los dos bandos)
module discos(e = -1) {
    for (a = AVIONES) if (del_bando(a, e)) en_avion(a) circle(r = radio(a), $fn = 72);
    for (b = [0, 1]) if (e < 0 || e == b) disco_bando(b);
}

// Distancia del centro de la diana al borde del hueco, en la dirección de la pestaña
function dist_borde(a) = max(norm(punto_cercano(silueta(a[7]))), radio(a) + MARGEN_HUECO);
// Largo libre real de la pestaña: el pedido, o el hueco entero si no da para más
function largo_libre(a) = min(pestana_largo, dist_borde(a) - radio(a));

// Pestaña fina: va del centro de la diana hasta dentro de la lámina (lo que queda tapado no se ve)
module pestanas(e = -1) if (MINIMA) pestanas_minima(e); else for (a = AVIONES) if (del_bando(a, e)) {
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
module pestanas_minima(e = -1) for (a = AVIONES) if (del_bando(a, e)) {
    largo = radio(a) + hueco_min(a) + pestana_solape;
    en_avion(a) translate([-pestana_ancho / 2, -largo]) square([pestana_ancho, largo]);
}

// La lámina del color del cielo: sin los discos de las insignias, que van del color de cada bando
module lamina_2d() if (MINIMA) estructura_minima(); else difference() {
    union() { cielo(); anclajes(); }
    for (e = [0, 1]) disco_bando(e);
}

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

// Línea de frente: trazos de 3,2 mm cada 5,6 mm
module frente() if (CON_FRENTE) {
    a = FRENTE[0];
    b = FRENTE[1];
    largo = norm(b - a);
    u = (b - a) / largo;
    for (t = [0:5.6:largo - 1]) hull() {
        translate(a + u * (t + 0.5)) circle(d = 1, $fn = 16);
        translate(a + u * min(t + 2.7, largo - 0.5)) circle(d = 1, $fn = 16);
    }
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
                frente();
                if (CON_REBORDES) bordes();
                if (CON_MARCO) marco();
                insignias();
                aros_bando();
            }
        }
        numeros();
    }
    if (CON_ANILLOS) anillos();
    letras_bando();
}
module relieve_alto_2d() union() {
    difference() {
        intersection() { cielo(); union() { if (CON_REBORDES) bordes(); if (CON_MARCO) marco(); insignias(); aros_bando(); } }
        numeros();
    }
    letras_bando();
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
// Dianas, pestañas e insignia de un bando (-1: los dos)
module dianas_mm(e = -1) union() {
    linear_extrude(GROSOR) discos(e);
    linear_extrude(pestana_grosor) difference() { pestanas(e); lamina_2d(); }
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
    echo(str("Bando ", BANDOS[a[11]], ", posición ", k % 3 + 1, ": ", a[0], ", diana Ø", r2(2 * radio(a)), " mm, ",
             a[5], a[5] == 1 ? " punto" : " puntos", ", hueco ", r2(h), " mm",
             MINIMA ? "" : str(", pestaña libre ", r2(largo_libre(a)), " mm, saliente ", r2(h - largo_libre(a)), " mm"),
             h < holgura_min - 0.001 ? "  <-- HUECO DEMASIADO JUSTO" : "",
             a[10] > 1 ? str("  (avión engordado x", a[10], " para que quepa la diana)") : "",
             hp < MARGEN_DIANA - 0.001 ? "  (ni engordado cabe: el centro se ensancha en redondo)" : ""));
    if (k < 3 && TIPOS[a[8]][3][0] > TIPOS[a[9]][3][0])
        echo(str("AVISO: en la posición ", k + 1, " hay un avión más grande que el previsto (", TIPOS[a[9]][2],
                 "). Mira la vista previa por si se solapa con otro"));
}
echo(str("Pestaña: ", pestana_grosor, " x ", pestana_ancho, " mm, largo libre ", pestana_largo, " mm"));
echo(str("Versión ", version, ", disposición ", disposicion, ": lámina ", GROSOR, " mm, altura total ", ALTURA, " mm",
         CON_RELIEVE ? "" : " (sin relieve)"));
if (parte == "relieve" && !CON_RELIEVE) echo("AVISO: esta versión no tiene relieve, la pieza sale vacía");

// ---------------- salida ----------------
if (parte == "completa") completa();
else if (parte == "base") base_mm();
else if (parte == "relieve") relieve_3d();
else if (parte == "dianas") dianas_mm();
else if (parte == "dianas_a") dianas_mm(0);
else if (parte == "dianas_b") dianas_mm(1);
else if (parte == "probeta") probeta();
else if (parte == "vista") {
    color("#378ADD") base_mm();
    color(COLORES[0]) dianas_mm(0);
    color(COLORES[1]) dianas_mm(1);
    color("#F4F9FE") relieve_3d();
}
