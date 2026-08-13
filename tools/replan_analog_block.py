#!/usr/bin/env python3
"""Fase 6b - amplia el board a 170x120 mm y redistribuye el bloque analogico
para descongestionarlo, dejando el resto del board intacto.

Por que no se desplazo la columna de conectores J2/J3/J5/J15-19 ni el sector
de reles/actuadores (K1,K2,U17,U20,...): entre el bloque analogico y esa
columna (x=98.4) pasan ~15 nets que NO son del bloque analogico (bus RS485,
control de bomba/CO2, interfaz HX711) en distintas alturas y. Desplazar esa
columna hubiera obligado a re-rutear todas esas nets ademas de las del
bloque analogico, muy por fuera del alcance pedido. En cambio, el board se
amplia 20 mm a la derecha (queda vacio, no toca nada existente) y el bloque
analogico se expande verticalmente dentro de su propio corredor
(x:[54.5, 97], y:[6, 60]), que estaba casi vacio salvo por un puñado de
tracks de paso (HX711/RS485/I2C_SCL) que se re-rutean si hace falta.

Pasos:
  1. Reempaquetar (shelf-pack) los ~59 componentes del bloque analogico en
     el corredor ampliado, con separacion generosa.
  2. Extender Edge.Cuts y las 2 zonas de plano full-board (GND x2 capas,
     /12V_RAIL) 20 mm a la derecha (150.1 -> 170.1 mm de ancho).
  3. Ripear el copper que quedo invalido: todo lo de las nets propias del
     bloque analogico; solo la porcion LOCAL de GND/rieles dentro del
     bbox viejo del cluster; y los tracks de paso (HX711/RS485/I2C_SCL)
     que caen dentro del nuevo corredor.
  4. Refill de zonas y guardado.

Despues de correr este script hay que regenerar el DRC report y correr
tools/route_fase6.py para re-cerrar todo lo que quedo desconectado.
"""
import os
import sys
import math
import pcbnew

MM = 1_000_000
_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
_REPO_CANDIDATES = ['/workspace', os.path.abspath(os.path.join(_SCRIPT_DIR, '..'))]
ROOT = next((p for p in _REPO_CANDIDATES if os.path.isdir(os.path.join(p, 'kicad'))), _REPO_CANDIDATES[-1])
BOARD_PATH = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, 'kicad', 'nebula_qshield.kicad_pcb')

SHIFT_X = 20.0
OLD_RIGHT = 142.05   # borde derecho actual (ver Edge.Cuts bbox)
EDGE_SHIFT_THRESHOLD = 130.0  # cualquier vertice de Edge.Cuts/zona full-board
                               # con x > esto es "borde derecho" -> +20mm

CLUSTER_REFS = [
    'C12', 'C13', 'C14', 'C15', 'C16', 'C17', 'C18', 'C19', 'C20', 'C21',
    'C22', 'C23', 'C24', 'C28', 'C29', 'C30',
    'D19', 'D20', 'D21', 'D22', 'D23', 'D24', 'D3', 'D4', 'D5', 'D6', 'D7', 'D8',
    'R10', 'R11', 'R12', 'R13', 'R14', 'R15', 'R16', 'R17', 'R18',
    'R30', 'R31', 'R32', 'R33', 'R7', 'R8', 'R9',
    'T1', 'T2', 'T3', 'TP1', 'TP2',
    'U10', 'U11', 'U12', 'U13', 'U4', 'U5', 'U6', 'U7', 'U8', 'U9',
]

OLD_CLUSTER_BBOX = (52.0, -0.5, 95.0, 39.0)     # rip local de GND/rieles aca

# Corredor destino en forma de L: el courtyard de J21 (area de acoplamiento
# UNO Q, INMUTABLE) ocupa x:[3.785,74.955] y:[34.265,90.195], asi que no se
# puede simplemente bajar en Y usando todo el ancho. Region 1 = la franja de
# siempre (arriba del courtyard); Region 2 = angosta pero larga, a la
# derecha del courtyard, entre este y J16/D10 (fijos, x>=98.4 / y>=70).
REGION_1 = (55.1, 6.0, 91.6, 34.0)
REGION_2 = (76.0, 37.5, 94.5, 68.0)
REGIONS = [REGION_1, REGION_2]
NEW_REGION = (54.5, 6.0, 97.0, 68.0)            # bbox total, para el rip de PASSING_NETS
PASSING_NETS = ['/Digital & I2C/HX711_EN', '/Digital & I2C/HX711_EP',
                 '/Digital & I2C/HX711_SP', '/HX711_DOUT',
                 '/Digital & I2C/RS485_A', '/Digital & I2C/RS485_B',
                 '/I2C_SCL', '/Actuator Drivers/MOTOR_VS']
PLANE_NETS = ['GND', '/3V3_RAIL', '/5V_RAIL', '/12V_RAIL']

def gap_for(w, h):
    """Separacion escalada al tamaño de cada footprint: los ~28 pasivos
    0402 no necesitan 2mm de gap (eso desperdicia la mayor parte del
    corredor); los IC/transformadores grandes si se benefician de mas
    aire. En cualquier caso es varias veces mas que los ~0.25mm actuales."""
    s = min(w, h)
    if s < 2.5:
        return 0.4
    if s < 5.0:
        return 0.8
    return 1.2


def rect_overlaps(a, b, margin=0.0):
    ax1, ay1, ax2, ay2 = a
    bx1, by1, bx2, by2 = b
    return not (ax2 + margin <= bx1 or bx2 + margin <= ax1 or
                ay2 + margin <= by1 or by2 + margin <= ay1)


def pack_cluster(brd, refs, regions):
    """Shelf-packing (next-fit decreasing height) sobre una secuencia de
    regiones rectangulares (para corredores en forma de L). Ordena por
    altura descendente para agrupar filas de tamaño similar y minimizar
    desperdicio - los ~28 pasivos 0402 quedan juntos en filas muy
    compactas, dejando la mayor parte del corredor para los IC grandes.
    Devuelve tambien cuantos componentes NO entraron (overflow)."""
    items = []
    for ref in refs:
        fp = brd.FindFootprintByReference(ref)
        pos = fp.GetPosition()
        bb = fp.GetBoundingBox(False, False)
        w = bb.GetWidth() / MM
        h = bb.GetHeight() / MM
        items.append((ref, fp, w, h, pos.y / MM))
    # Ordena por tamaño descendente (next-fit decreasing height): es lo que
    # realmente entra en el corredor disponible. Se probo tambien agrupar
    # por banda de Y original para preservar adyacencia funcional, pero
    # mezclar partes grandes y chicas en la misma fila desperdicia tanto
    # espacio que deja de entrar la mitad del cluster - no viable con el
    # area disponible.
    items.sort(key=lambda t: -min(t[2], t[3]))

    region_iter = iter(regions)
    rx0, ry0, rx1, ry1 = next(region_iter)
    cx, cy = rx0, ry0
    row_h = 0.0
    placements = {}
    overflow = []
    for ref, fp, w, h, _orig_y in items:
        g = gap_for(w, h)
        if cx + w > rx1 and cx > rx0:
            cx = rx0
            cy += row_h + g
            row_h = 0.0
        if cy + h > ry1:
            nxt = next(region_iter, None)
            if nxt is None:
                overflow.append(ref)
                continue
            rx0, ry0, rx1, ry1 = nxt
            cx, cy = rx0, ry0
            row_h = 0.0
        cx0, cy0 = cx, cy
        placements[ref] = (cx0 + w / 2.0, cy0 + h / 2.0, w, h)
        cx += w + g
        row_h = max(row_h, h)
    return placements, overflow


def _sh(p):
    return pcbnew.VECTOR2I(int(p.x + (SHIFT_X * MM if p.x / MM > EDGE_SHIFT_THRESHOLD else 0)), p.y)


def shift_pcb_shape(shape):
    changed = False
    st = shape.GetShape()
    if st in (pcbnew.SHAPE_T_SEGMENT, pcbnew.SHAPE_T_RECT):
        s = shape.GetStart(); e = shape.GetEnd()
        ns, ne = _sh(s), _sh(e)
        if ns != s or ne != e:
            shape.SetStart(ns); shape.SetEnd(ne); changed = True
    elif st == pcbnew.SHAPE_T_ARC:
        s = shape.GetStart(); m = shape.GetArcMid(); e = shape.GetEnd()
        ns, nm, ne = _sh(s), _sh(m), _sh(e)
        if (ns, nm, ne) != (s, m, e):
            shape.SetArcGeometry(ns, nm, ne)
            changed = True
    elif st == pcbnew.SHAPE_T_POLY:
        poly = shape.GetPolyShape()
        for oi in range(poly.OutlineCount()):
            outline = poly.Outline(oi)
            for i in range(outline.PointCount()):
                p = outline.CPoint(i)
                if p.x / MM > EDGE_SHIFT_THRESHOLD:
                    outline.SetPoint(i, pcbnew.VECTOR2I(int(p.x + SHIFT_X * MM), p.y))
                    changed = True
    return changed


def shift_zone_outline(zone):
    changed = False
    outline = zone.Outline()
    for oi in range(outline.OutlineCount()):
        poly = outline.Outline(oi)
        for i in range(poly.PointCount()):
            p = poly.CPoint(i)
            if p.x / MM > EDGE_SHIFT_THRESHOLD:
                poly.SetPoint(i, pcbnew.VECTOR2I(int(p.x + SHIFT_X * MM), p.y))
                changed = True
    return changed


def main():
    brd = pcbnew.LoadBoard(BOARD_PATH)

    # 1) Reempaquetar el bloque analogico
    placements, overflow = pack_cluster(brd, CLUSTER_REFS, REGIONS)
    print(f'regiones destino: {REGIONS}; componentes colocados: {len(placements)}/{len(CLUSTER_REFS)}')
    if overflow:
        print(f'AVISO: no entraron {len(overflow)} componentes en las regiones: {overflow}')

    for ref, (cx, cy, w, h) in placements.items():
        fp = brd.FindFootprintByReference(ref)
        fp.SetPosition(pcbnew.VECTOR2I(int(round(cx * MM)), int(round(cy * MM))))

    # 2) Extender Edge.Cuts y zonas full-board 20mm a la derecha
    n_shapes = 0
    for d in brd.GetDrawings():
        if d.GetLayer() == pcbnew.Edge_Cuts and shift_pcb_shape(d):
            n_shapes += 1
    n_zones = 0
    for z in brd.Zones():
        # solo las zonas full-board (GND x2 capas, /12V_RAIL) tienen vertices
        # > EDGE_SHIFT_THRESHOLD; las zonas locales del bloque analogico
        # (x<=100) no se tocan.
        if shift_zone_outline(z):
            n_zones += 1
    print(f'Edge.Cuts shapes extendidos: {n_shapes}, zonas extendidas: {n_zones}')

    # 3) Rip-up de copper invalido
    cluster_nets = set()
    for ref in CLUSTER_REFS:
        fp = brd.FindFootprintByReference(ref)
        for pad in fp.Pads():
            cluster_nets.add(pad.GetNetname())
    cluster_only_nets = cluster_nets - set(PLANE_NETS)

    def in_rect(x, y, rect, margin=0.0):
        x0, y0, x1, y1 = rect
        return x0 - margin <= x <= x1 + margin and y0 - margin <= y <= y1 + margin

    to_remove = []
    for t in brd.GetTracks():
        net = t.GetNetname()
        if isinstance(t, pcbnew.PCB_VIA):
            pos = t.GetPosition()
            pts = [(pos.x / MM, pos.y / MM)]
        else:
            s = t.GetStart(); e = t.GetEnd()
            pts = [(s.x / MM, s.y / MM), (e.x / MM, e.y / MM), ((s.x + e.x) / 2 / MM, (s.y + e.y) / 2 / MM)]

        remove = False
        if net in cluster_only_nets:
            remove = True
        elif net in PLANE_NETS:
            if any(in_rect(x, y, OLD_CLUSTER_BBOX) or in_rect(x, y, NEW_REGION) for x, y in pts):
                remove = True
        elif net in PASSING_NETS:
            if any(in_rect(x, y, NEW_REGION, margin=1.5) for x, y in pts):
                remove = True
        if remove:
            to_remove.append(t)

    print(f'tracks/vias a remover: {len(to_remove)}')
    for t in to_remove:
        brd.Remove(t)

    # 4) Refill y guardado
    filler = pcbnew.ZONE_FILLER(brd)
    filler.Fill(brd.Zones())
    brd.BuildConnectivity()
    pcbnew.SaveBoard(BOARD_PATH, brd)
    print('Guardado', BOARD_PATH)


if __name__ == '__main__':
    main()
