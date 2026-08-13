#!/usr/bin/env python3
"""Fase 6 - cierre de los 38 pares desconectados finales en nebula_qshield.kicad_pcb.

Motor de ruteo: Dijkstra sobre una grilla local (F.Cu / B.Cu + transiciones por
via) alrededor de cada par, con verificacion final exacta (no-grilla) de
clearance contra pads/tracks/vias de otras nets antes de comprometer cualquier
track/via al board. Los pares "plane" (GND, /12V_RAIL, /5V_RAIL, /3V3_RAIL) se
tratan igual que cualquier net de señal: se traza copper explicito entre los
dos puntos reportados por DRC en vez de asumir que el plano interno los
conecta (los 4 pares de /12V_RAIL que quedan son justamente islas del plano en
In2.Cu que un via suelto no resuelve).

Si un par del bloque analogico no entra con el board tal cual, como ultimo
recurso se intenta mover UNO de los pasivos analogicos permitidos
(C20,C21,C23,R30,R31,R32), nunca mas de 2.0 mm, verificando que:
  1) el pin que estaba desconectado ahora rutea limpio, y
  2) el otro pin del mismo pasivo (que ya tenia copper) se reconecta con un
     jumper corto y valido a su stub existente.
Si ninguna de las 16 posiciones candidatas (8 direcciones x {1.0,2.0} mm)
cumple ambas condiciones sin colisionar, el movimiento se descarta y el par
queda reportado como pendiente.

Uso:
    <python-de-kicad> tools/route_fase6.py [--dry-run] [--verbose]

Rutas: por defecto asume que el repo esta en /workspace (imagen Docker
kicad/kicad:10.0.5); si no existe, usa la carpeta del script (..) - funciona
igual corriendo local con el interprete embebido de KiCad en Windows.
"""
import os
import re
import sys
import math
import shutil
import subprocess
import heapq
import time

import numpy as np
import pcbnew

try:
    sys.stdout.reconfigure(line_buffering=True)
except Exception:
    pass

MM = 1_000_000  # unidades internas (nm) por mm

# --------------------------------------------------------------------------
# Rutas
# --------------------------------------------------------------------------
_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
_REPO_CANDIDATES = ['/workspace', os.path.abspath(os.path.join(_SCRIPT_DIR, '..'))]
ROOT = next((p for p in _REPO_CANDIDATES if os.path.isdir(os.path.join(p, 'kicad'))), _REPO_CANDIDATES[-1])
_positional = [a for a in sys.argv[1:] if not a.startswith('--')]
BOARD_PATH = _positional[0] if _positional else os.path.join(ROOT, 'kicad', 'nebula_qshield.kicad_pcb')
DRC_PATH = os.path.splitext(BOARD_PATH)[0] + '-drc.rpt'

DRY_RUN = '--dry-run' in sys.argv
VERBOSE = '--verbose' in sys.argv or DRY_RUN


def log(*a):
    if VERBOSE:
        print(*a)


# --------------------------------------------------------------------------
# Geometria del board (edge cuts 150x120 mm, esquinas redondeadas) y las dos
# zonas de exclusion alrededor del header J21 (misma geometria validada por
# close_pairs_v8.py, que dejo el board en DRC 0 con estos limites).
# --------------------------------------------------------------------------
BOARD_LEFT, BOARD_RIGHT = -8.0, 142.0
BOARD_BOTTOM, BOARD_TOP = -2.0, 118.0
BOARD_CORNER_R = 2.5
EDGE_MARGIN = 0.25
CUTOUTS = [(2.08, 81.56, 22.5, 94.56), (60.08, 88.56, 77.08, 94.56)]

ANALOG_PASSIVES = ['C20', 'C21', 'C23', 'R30', 'R31', 'R32']
MAX_NUDGE_MM = 2.0

# Parametros reales de netclass leidos de kicad/nebula_qshield.kicad_pro
# (net_settings.classes). track_width / via_diameter / via_drill / clearance
# en mm. Estos son los valores que kicad-cli DRC va a exigir.
CLASS_PARAMS = {
    'Default':     dict(width=0.25, via_d=0.6, via_drill=0.3, clearance=0.20),
    'Analog':      dict(width=0.25, via_d=0.6, via_drill=0.3, clearance=0.30),
    'HighCurrent': dict(width=1.5,  via_d=1.0, via_drill=0.5, clearance=0.30),
    'I2C':         dict(width=0.25, via_d=0.6, via_drill=0.3, clearance=0.25),
    'Power':       dict(width=0.5,  via_d=0.8, via_drill=0.4, clearance=0.25),
    'RelayHV':     dict(width=1.0,  via_d=1.0, via_drill=0.5, clearance=0.50),
}

# Anchos MINIMOS reales (no solo el ancho "preferido" de arriba) segun las
# reglas custom de kicad/nebula_qshield.kicad_dru (Power_Rails,
# High_Current_12V, Analog_Signals, I2C_Bus, Relay_HV_Contacts,
# Signal_Default). El fallback a ancho angosto (neck-down en pads
# encajonados) nunca puede bajar de esto, aunque el board admita 0.2mm en
# general - para Power/HighCurrent/RelayHV ese piso es mas alto.
MIN_WIDTH_BY_CLASS = {
    'Default': 0.2, 'Analog': 0.25, 'HighCurrent': 0.5,
    'I2C': 0.25, 'Power': 0.5, 'RelayHV': 1.0,
}


def refresh_drc_report():
    """Intenta re-generar el .rpt con kicad-cli antes de leerlo. No es fatal
    si no se encuentra el binario (se usa el .rpt existente en el repo)."""
    candidates = [
        shutil.which('kicad-cli'),
        r'C:\Program Files\KiCad\10.0\bin\kicad-cli.exe',
        '/usr/bin/kicad-cli',
    ]
    exe = next((c for c in candidates if c and os.path.exists(c)), None)
    if not exe:
        log('[refresh_drc_report] kicad-cli no encontrado, uso el .rpt existente')
        return
    try:
        subprocess.run([exe, 'pcb', 'drc', '--severity-error', '--refill-zones',
                         '-o', DRC_PATH, BOARD_PATH], check=True, capture_output=True, timeout=180)
        log('[refresh_drc_report] .rpt actualizado con', exe)
    except Exception as e:
        log('[refresh_drc_report] fallo, uso el .rpt existente:', e)


# ==========================================================================
# Geometria basica (adaptada de tools/close_pairs_v8.py)
# ==========================================================================
def get_pad_rect(p):
    bb = p.GetBoundingBox()
    return (bb.GetX() / MM, bb.GetY() / MM,
            (bb.GetX() + bb.GetWidth()) / MM, (bb.GetY() + bb.GetHeight()) / MM)


def point_on_board(px, py, margin=0.0):
    if not (BOARD_LEFT + margin <= px <= BOARD_RIGHT - margin and
            BOARD_BOTTOM + margin <= py <= BOARD_TOP - margin):
        return False
    centers = [(BOARD_LEFT + BOARD_CORNER_R, BOARD_BOTTOM + BOARD_CORNER_R),
               (BOARD_RIGHT - BOARD_CORNER_R, BOARD_BOTTOM + BOARD_CORNER_R),
               (BOARD_LEFT + BOARD_CORNER_R, BOARD_TOP - BOARD_CORNER_R),
               (BOARD_RIGHT - BOARD_CORNER_R, BOARD_TOP - BOARD_CORNER_R)]
    for cx, cy in centers:
        corner = ((px < cx and py < cy) or (px > cx and py < cy) or
                  (px < cx and py > cy) or (px > cx and py > cy))
        if corner and math.hypot(px - cx, py - cy) < BOARD_CORNER_R + margin:
            return False
    return True


def in_cutout(px, py, margin=0.0):
    for cl, cb, cr, ct in CUTOUTS:
        if cl - margin <= px <= cr + margin and cb - margin <= py <= ct + margin:
            return True
    return False


def seg_dist_to_point(px, py, ax, ay, bx, by):
    dx = bx - ax; dy = by - ay; l2 = dx * dx + dy * dy
    if l2 == 0:
        return math.hypot(px - ax, py - ay)
    t = max(0.0, min(1.0, ((px - ax) * dx + (py - ay) * dy) / l2))
    return math.hypot(px - (ax + t * dx), py - (ay + t * dy))


def seg_to_seg_dist(x1, y1, x2, y2, x3, y3, x4, y4):
    def orient(ax, ay, bx, by, cx, cy):
        return (bx - ax) * (cy - ay) - (by - ay) * (cx - ax)

    def onseg(ax, ay, bx, by, cx, cy):
        return min(ax, bx) - 1e-9 <= cx <= max(ax, bx) + 1e-9 and min(ay, by) - 1e-9 <= cy <= max(ay, by) + 1e-9

    def intersect():
        o1 = orient(x1, y1, x2, y2, x3, y3); o2 = orient(x1, y1, x2, y2, x4, y4)
        o3 = orient(x3, y3, x4, y4, x1, y1); o4 = orient(x3, y3, x4, y4, x2, y2)
        if o1 == 0 and onseg(x1, y1, x2, y2, x3, y3): return True
        if o2 == 0 and onseg(x1, y1, x2, y2, x4, y4): return True
        if o3 == 0 and onseg(x3, y3, x4, y4, x1, y1): return True
        if o4 == 0 and onseg(x3, y3, x4, y4, x2, y2): return True
        return (o1 > 0) != (o2 > 0) and (o3 > 0) != (o4 > 0)

    if intersect():
        return 0.0
    return min(seg_dist_to_point(x1, y1, x3, y3, x4, y4), seg_dist_to_point(x2, y2, x3, y3, x4, y4),
               seg_dist_to_point(x3, y3, x1, y1, x2, y2), seg_dist_to_point(x4, y4, x1, y1, x2, y2))


def rect_seg_dist(x1, y1, x2, y2, sx1, sy1, sx2, sy2):
    dmin = float('inf')
    for a, b, c, d in [(x1, y1, x2, y1), (x2, y1, x2, y2), (x2, y2, x1, y2), (x1, y2, x1, y1)]:
        dmin = min(dmin, seg_to_seg_dist(a, b, c, d, sx1, sy1, sx2, sy2))
    return dmin


def rect_point_dist(px, py, rect):
    x1, y1, x2, y2 = rect
    dx = max(max(x1 - px, 0.0), px - x2); dy = max(max(y1 - py, 0.0), py - y2)
    return math.hypot(dx, dy)


def point_in_pad(px, py, rect, margin=0.0):
    return rect[0] - margin <= px <= rect[2] + margin and rect[1] - margin <= py <= rect[3] + margin


# ==========================================================================
# Board / netclasses
# ==========================================================================
brd = pcbnew.LoadBoard(BOARD_PATH)

NET_CLASSES = {}
for net in brd.GetNetsByName().values():
    NET_CLASSES[net.GetNetname()] = [c.strip() for c in net.GetNetClassName().split(',')]


def netclasses(name):
    return NET_CLASSES.get(name, ['Default'])


def net_params(name):
    cs = netclasses(name)
    return dict(
        width=max(CLASS_PARAMS[c]['width'] for c in cs if c in CLASS_PARAMS) if any(c in CLASS_PARAMS for c in cs) else 0.25,
        via_d=max(CLASS_PARAMS[c]['via_d'] for c in cs if c in CLASS_PARAMS) if any(c in CLASS_PARAMS for c in cs) else 0.6,
        via_drill=max(CLASS_PARAMS[c]['via_drill'] for c in cs if c in CLASS_PARAMS) if any(c in CLASS_PARAMS for c in cs) else 0.3,
        clearance=max(CLASS_PARAMS[c]['clearance'] for c in cs if c in CLASS_PARAMS) if any(c in CLASS_PARAMS for c in cs) else 0.2,
    )


def track_width(name):
    return net_params(name)['width']


def min_track_width(name):
    cs = netclasses(name)
    applicable = [MIN_WIDTH_BY_CLASS[c] for c in cs if c in MIN_WIDTH_BY_CLASS]
    return max(applicable) if applicable else MIN_WIDTH_BY_CLASS['Default']


def via_size(name):
    p = net_params(name)
    return p['via_d'], p['via_drill']


def clearance(n1, n2):
    return max(net_params(n1)['clearance'], net_params(n2)['clearance'])


# ==========================================================================
# Obstaculos (copper existente por capa) + verificacion EXACTA (no-grilla)
# ==========================================================================
class ObstacleSet:
    """Vias/tracks/pads de TODAS las nets en una capa, para chequeo exacto de
    clearance. Se reconstruye on-demand para el area de cada par (rapido:
    listas ya filtradas por capa una sola vez al arrancar)."""

    def __init__(self, layer_id):
        self.layer = layer_id
        self.vias = []   # (x,y,r,net)
        self.tracks = []  # (x1,y1,x2,y2,r,net)
        self.pads = []   # (x1,y1,x2,y2,net)
        for t in brd.GetTracks():
            if isinstance(t, pcbnew.PCB_VIA):
                if not t.GetLayerSet().Contains(layer_id):
                    continue
                r = t.GetWidth(layer_id) / 2.0 / MM
                pos = t.GetPosition()
                self.vias.append((pos.x / MM, pos.y / MM, r, t.GetNetname()))
            elif isinstance(t, pcbnew.PCB_TRACK):
                if t.GetLayer() != layer_id:
                    continue
                r = t.GetWidth() / 2.0 / MM
                s = t.GetStart(); e = t.GetEnd()
                self.tracks.append((s.x / MM, s.y / MM, e.x / MM, e.y / MM, r, t.GetNetname()))
        for fp in brd.GetFootprints():
            for p in fp.Pads():
                if not p.GetLayerSet().Contains(layer_id):
                    continue
                rect = get_pad_rect(p)
                self.pads.append((rect[0], rect[1], rect[2], rect[3], p.GetNetname()))

    def track_clear(self, x1, y1, x2, y2, w, net):
        hw = w / 2.0
        for i in range(11):
            t = i / 10.0
            if not point_on_board(x1 + (x2 - x1) * t, y1 + (y2 - y1) * t, EDGE_MARGIN + hw):
                return False
        for cl, cb, cr, ct in CUTOUTS:
            m = EDGE_MARGIN + hw
            if rect_seg_dist(cl - m, cb - m, cr + m, ct + m, x1, y1, x2, y2) < 1e-6:
                return False
        for vx, vy, r, n in self.vias:
            if n == net: continue
            if seg_dist_to_point(vx, vy, x1, y1, x2, y2) - r - hw - clearance(net, n) < 0.01:
                return False
        for sx1, sy1, sx2, sy2, r, n in self.tracks:
            if n == net: continue
            if seg_to_seg_dist(x1, y1, x2, y2, sx1, sy1, sx2, sy2) - r - hw - clearance(net, n) < 0.01:
                return False
        for px1, py1, px2, py2, n in self.pads:
            if n == net: continue
            if rect_seg_dist(px1, py1, px2, py2, x1, y1, x2, y2) - hw - clearance(net, n) < 0.01:
                return False
        return True

    def point_safe(self, x, y, r, net, exempt_cutouts=False):
        if not point_on_board(x, y, EDGE_MARGIN + r):
            return False
        if not exempt_cutouts and in_cutout(x, y, EDGE_MARGIN + r):
            return False
        for vx, vy, rr, n in self.vias:
            if n == net: continue
            if math.hypot(x - vx, y - vy) - rr - r - clearance(net, n) < 0.01:
                return False
        for sx1, sy1, sx2, sy2, rr, n in self.tracks:
            if n == net: continue
            if seg_dist_to_point(x, y, sx1, sy1, sx2, sy2) - rr - r - clearance(net, n) < 0.01:
                return False
        for px1, py1, px2, py2, n in self.pads:
            if n == net: continue
            if rect_point_dist(x, y, (px1, py1, px2, py2)) - r - clearance(net, n) < 0.01:
                return False
        return True

    def add_track(self, x1, y1, x2, y2, w, net):
        self.tracks.append((x1, y1, x2, y2, w / 2.0, net))

    def add_via(self, x, y, r, net):
        self.vias.append((x, y, r, net))

    def remove_near(self, x, y, radius, net):
        """Usado por la fase de nudge de pasivos: saca de la lista de
        obstaculos los tracks/vias que van a ser removidos del board antes de
        re-simular (para no auto-bloquearse contra copper que ya no existe)."""
        self.vias = [v for v in self.vias if not (v[3] == net and math.hypot(v[0] - x, v[1] - y) <= radius)]
        self.tracks = [t for t in self.tracks
                        if not (t[5] == net and (math.hypot(t[0] - x, t[1] - y) <= radius or
                                                  math.hypot(t[2] - x, t[3] - y) <= radius))]


F_layer, B_layer = pcbnew.F_Cu, pcbnew.B_Cu
f_obs = ObstacleSet(F_layer)
b_obs = ObstacleSet(B_layer)
OBS = {F_layer: f_obs, B_layer: b_obs}

existing_vias = set()
for t in brd.GetTracks():
    if isinstance(t, pcbnew.PCB_VIA):
        pos = t.GetPosition()
        existing_vias.add((round(pos.x / MM, 3), round(pos.y / MM, 3), t.GetNetname()))


def add_track_obj(x1, y1, x2, y2, layer, w, net):
    t = pcbnew.PCB_TRACK(brd)
    t.SetStart(pcbnew.VECTOR2I(int(round(x1 * MM)), int(round(y1 * MM))))
    t.SetEnd(pcbnew.VECTOR2I(int(round(x2 * MM)), int(round(y2 * MM))))
    t.SetLayer(layer); t.SetWidth(int(round(w * MM))); t.SetNet(net)
    brd.Add(t)
    return t


def add_via_obj(x, y, vd, drill, net):
    v = pcbnew.PCB_VIA(brd)
    v.SetPosition(pcbnew.VECTOR2I(int(round(x * MM)), int(round(y * MM))))
    v.SetNet(net); v.SetWidth(int(round(vd * MM))); v.SetDrill(int(round(drill * MM)))
    v.SetLayerPair(pcbnew.F_Cu, pcbnew.B_Cu)
    v.SetRemoveUnconnected(False)
    brd.Add(v)
    return v


def place_via_if_new(x, y, net, exempt_cutouts=False):
    """-> (coords_or_None, via_obj_or_None, ok). via_obj es None si se
    reuso una via ya existente en ese punto (nada nuevo que revertir)."""
    vd, drill = via_size(net.GetNetname()); r = vd / 2.0
    k = (round(x, 3), round(y, 3), net.GetNetname())
    if k in existing_vias:
        return (x, y, vd, drill), None, True
    if not f_obs.point_safe(x, y, r, net.GetNetname(), exempt_cutouts) or \
       not b_obs.point_safe(x, y, r, net.GetNetname(), exempt_cutouts):
        return None, None, False
    v = add_via_obj(x, y, vd, drill, net)
    f_obs.add_via(x, y, r, net.GetNetname()); b_obs.add_via(x, y, r, net.GetNetname())
    existing_vias.add(k)
    return (x, y, vd, drill), v, True


# ==========================================================================
# Parseo del DRC report
# ==========================================================================
pads_by_ref = {}
for fp in brd.GetFootprints():
    for p in fp.Pads():
        pads_by_ref[(fp.GetReference(), str(p.GetNumber()))] = (fp, p, get_pad_rect(p))


def pad_info(item):
    m = re.match(r'(?:PTH )?Pad (\d+)', item['type'])
    if m and item['ref']:
        return pads_by_ref.get((item['ref'], m.group(1)))
    return None


def exact_track_nearest(track, px, py):
    sx = track.GetStart().x / MM; sy = track.GetStart().y / MM
    ex = track.GetEnd().x / MM; ey = track.GetEnd().y / MM
    dx = ex - sx; dy = ey - sy; l2 = dx * dx + dy * dy
    if l2 == 0:
        return (sx, sy)
    t = max(0.0, min(1.0, ((px - sx) * dx + (py - sy) * dy) / l2))
    return (sx + t * dx, sy + t * dy)


def find_track_exact(drc_point, net, layer_str):
    px, py = drc_point
    best = None; bd = 1e9
    for t in brd.GetTracks():
        if isinstance(t, pcbnew.PCB_VIA):
            if t.GetNetname() != net or 'F.Cu - B.Cu' not in layer_str:
                continue
            x = t.GetPosition().x / MM; y = t.GetPosition().y / MM
            d = math.hypot(x - px, y - py)
            if d < bd: bd = d; best = ('via', x, y)
        elif isinstance(t, pcbnew.PCB_TRACK):
            if t.GetNetname() != net: continue
            if layer_str == 'F.Cu' and t.GetLayer() != pcbnew.F_Cu: continue
            if layer_str == 'B.Cu' and t.GetLayer() != pcbnew.B_Cu: continue
            nx, ny = exact_track_nearest(t, px, py)
            d = math.hypot(nx - px, ny - py)
            if d < 0.2 and d < bd:
                bd = d; best = ('track', nx, ny)
    if best:
        return (best[1], best[2])
    return (px, py)


def connection_point(item):
    """-> (x, y, layers:set('F','B'), is_pad, rect_or_None)"""
    typ = item['type']; net = item['net']
    if 'Pad' in typ:
        info = pad_info(item)
        if info:
            p = info[1]
            pos = p.GetPosition()
            layers = set()
            if p.GetLayerSet().Contains(pcbnew.F_Cu): layers.add('F')
            if p.GetLayerSet().Contains(pcbnew.B_Cu): layers.add('B')
            return (pos.x / MM, pos.y / MM, layers, True, get_pad_rect(p))
    if typ == 'Via':
        x, y = find_track_exact((item['x'], item['y']), net, 'F.Cu - B.Cu')
        return (x, y, {'F', 'B'}, False, None)
    # Track (o fallback generico): snapear sobre el track real de la net
    layers = set()
    if 'F.Cu' in item['layer_raw']: layers.add('F')
    if 'B.Cu' in item['layer_raw']: layers.add('B')
    layer_str = 'F.Cu' if 'F' in layers else 'B.Cu'
    x, y = find_track_exact((item['x'], item['y']), net, layer_str)
    return (x, y, layers or {'F'}, False, None)


def parse_pairs():
    text = open(DRC_PATH, encoding='utf-8').read()
    blocks = re.split(r'(?=\[unconnected_items\]: Missing connection between items)', text)
    pairs = []
    for block in blocks[1:]:
        items = []
        for line in block.split('\n'):
            m = re.match(
                r'\s+@\(([\-\d.]+) mm, ([\-\d.]+) mm\): (Pad \d+|PTH pad \d+|Track|Via|Zone) '
                r'\[([^\]]+)\](?: of ([^ ]+))?(?: on ([\w. \-]+))?', line)
            if m:
                is_pth = 'PTH' in m.group(3)
                layer = m.group(6).strip() if m.group(6) else ('F.Cu - B.Cu' if is_pth else 'F.Cu')
                if is_pth:
                    layer = 'F.Cu - B.Cu'
                items.append({'x': float(m.group(1)), 'y': float(m.group(2)), 'type': m.group(3),
                              'net': m.group(4), 'ref': m.group(5), 'layer_raw': layer})
        if len(items) == 2:
            pairs.append(items)
    return pairs


# ==========================================================================
# Router de grilla (Dijkstra, 2 capas + transicion por via)
# ==========================================================================
VIA_PENALTY_MM = 3.0


class GridRouter:
    def __init__(self, x0, y0, x1, y1, res, net_name, width, via_d, via_drill,
                 exempt_rects=()):
        self.x0, self.y0 = x0, y0
        self.res = res
        self.w = max(2, int(round((x1 - x0) / res)) + 1)
        self.h = max(2, int(round((y1 - y0) / res)) + 1)
        self.net = net_name
        self.hw = width / 2.0
        self.via_r = via_d / 2.0
        self.clr = {}  # cache clearance(net, other) por other-net
        self.exempt_rects = exempt_rects

        xs = x0 + np.arange(self.w) * res
        ys = y0 + np.arange(self.h) * res
        X, Y = np.meshgrid(xs, ys)  # shape (h, w)
        self.X, self.Y = X, Y

        self.free = {}  # layer -> bool grid libre para TRACK (halfwidth)
        self.via_free = {}  # layer -> bool grid libre para VIA (radio de via)
        for layer in (F_layer, B_layer):
            self.free[layer] = self._build_mask(OBS[layer], self.hw)
            self.via_free[layer] = self._build_mask(OBS[layer], self.via_r)

        # borde de placa / redondeo de esquinas / cutouts, comun a ambas capas
        board_mask = self._board_mask(self.hw)
        board_mask_via = self._board_mask(self.via_r)
        for layer in (F_layer, B_layer):
            self.free[layer] &= board_mask
            self.via_free[layer] &= board_mask_via

    def _exempt_mask(self, margin):
        if not self.exempt_rects:
            return None
        m = np.zeros_like(self.X, dtype=bool)
        for (rx1, ry1, rx2, ry2) in self.exempt_rects:
            m |= (self.X >= rx1 - margin) & (self.X <= rx2 + margin) & \
                 (self.Y >= ry1 - margin) & (self.Y <= ry2 + margin)
        return m

    def _board_mask(self, margin):
        X, Y = self.X, self.Y
        mask = (X >= BOARD_LEFT + EDGE_MARGIN + margin) & (X <= BOARD_RIGHT - EDGE_MARGIN - margin) & \
               (Y >= BOARD_BOTTOM + EDGE_MARGIN + margin) & (Y <= BOARD_TOP - EDGE_MARGIN - margin)
        r = BOARD_CORNER_R
        for cx, cy in [(BOARD_LEFT + r, BOARD_BOTTOM + r), (BOARD_RIGHT - r, BOARD_BOTTOM + r),
                       (BOARD_LEFT + r, BOARD_TOP - r), (BOARD_RIGHT - r, BOARD_TOP - r)]:
            in_corner_quadrant = ((X < cx) & (Y < cy)) | ((X > cx) & (Y < cy)) | \
                                  ((X < cx) & (Y > cy)) | ((X > cx) & (Y > cy))
            cut = in_corner_quadrant & (np.hypot(X - cx, Y - cy) < r + EDGE_MARGIN + margin)
            mask &= ~cut
        exempt = self._exempt_mask(EDGE_MARGIN + margin + 0.05)
        cutout_block = np.zeros_like(mask)
        for cl, cb, cr, ct in CUTOUTS:
            m = EDGE_MARGIN + margin
            cutout_block |= (X >= cl - m) & (X <= cr + m) & (Y >= cb - m) & (Y <= ct + m)
        if exempt is not None:
            cutout_block &= ~exempt
        mask &= ~cutout_block
        return mask

    def _idx_range(self, xa, ya, xb, yb, pad):
        """Rango de indices [ix0,ix1] x [iy0,iy1] (inclusive) que cubre el
        bbox de un obstaculo + margen pad, recortado a la grilla."""
        res = self.res
        ix0 = max(0, int(math.floor((min(xa, xb) - pad - self.x0) / res)))
        ix1 = min(self.w - 1, int(math.ceil((max(xa, xb) + pad - self.x0) / res)))
        iy0 = max(0, int(math.floor((min(ya, yb) - pad - self.y0) / res)))
        iy1 = min(self.h - 1, int(math.ceil((max(ya, yb) + pad - self.y0) / res)))
        return ix0, ix1, iy0, iy1

    def _build_mask(self, obs, half):
        """Solo toca, por obstaculo, el recorte de grilla que realmente puede
        verse afectado (evita operar sobre la grilla completa por cada
        objeto, que es lo que hacia esto impracticamente lento en zonas
        congestionadas)."""
        blocked = np.zeros((self.h, self.w), dtype=bool)
        pad = 12.0
        gx0, gy0 = self.x0 - pad, self.y0 - pad
        gx1 = self.x0 + self.w * self.res + pad
        gy1 = self.y0 + self.h * self.res + pad

        for vx, vy, r, n in obs.vias:
            if n == self.net or not (gx0 <= vx <= gx1 and gy0 <= vy <= gy1):
                continue
            c = clearance(self.net, n); rr = r + half + c
            ix0, ix1, iy0, iy1 = self._idx_range(vx, vy, vx, vy, rr)
            if ix0 > ix1 or iy0 > iy1:
                continue
            Xs = self.X[iy0:iy1 + 1, ix0:ix1 + 1]; Ys = self.Y[iy0:iy1 + 1, ix0:ix1 + 1]
            blocked[iy0:iy1 + 1, ix0:ix1 + 1] |= (Xs - vx) ** 2 + (Ys - vy) ** 2 <= rr * rr

        for sx1, sy1, sx2, sy2, r, n in obs.tracks:
            if n == self.net:
                continue
            if not (min(sx1, sx2) - pad <= gx1 and max(sx1, sx2) + pad >= gx0 and
                    min(sy1, sy2) - pad <= gy1 and max(sy1, sy2) + pad >= gy0):
                continue
            c = clearance(self.net, n); rr = r + half + c
            ix0, ix1, iy0, iy1 = self._idx_range(sx1, sy1, sx2, sy2, rr)
            if ix0 > ix1 or iy0 > iy1:
                continue
            Xs = self.X[iy0:iy1 + 1, ix0:ix1 + 1]; Ys = self.Y[iy0:iy1 + 1, ix0:ix1 + 1]
            dx = sx2 - sx1; dy = sy2 - sy1; l2 = dx * dx + dy * dy
            if l2 == 0:
                d = np.hypot(Xs - sx1, Ys - sy1)
            else:
                t = np.clip(((Xs - sx1) * dx + (Ys - sy1) * dy) / l2, 0.0, 1.0)
                d = np.hypot(Xs - (sx1 + t * dx), Ys - (sy1 + t * dy))
            blocked[iy0:iy1 + 1, ix0:ix1 + 1] |= d <= rr

        for px1, py1, px2, py2, n in obs.pads:
            if n == self.net:
                continue
            if not (px1 - pad <= gx1 and px2 + pad >= gx0 and py1 - pad <= gy1 and py2 + pad >= gy0):
                continue
            c = clearance(self.net, n); rr = half + c
            ix0, ix1, iy0, iy1 = self._idx_range(px1, py1, px2, py2, rr)
            if ix0 > ix1 or iy0 > iy1:
                continue
            Xs = self.X[iy0:iy1 + 1, ix0:ix1 + 1]; Ys = self.Y[iy0:iy1 + 1, ix0:ix1 + 1]
            dx = np.maximum(np.maximum(px1 - Xs, 0.0), Xs - px2)
            dy = np.maximum(np.maximum(py1 - Ys, 0.0), Ys - py2)
            blocked[iy0:iy1 + 1, ix0:ix1 + 1] |= np.hypot(dx, dy) <= rr
        return ~blocked

    def _cell(self, x, y):
        ix = int(round((x - self.x0) / self.res))
        iy = int(round((y - self.y0) / self.res))
        return max(0, min(self.w - 1, ix)), max(0, min(self.h - 1, iy))

    def route(self, p1, layers1, p2, layers2):
        """p1/p2: (x,y). layers1/layers2: set subset of {'F','B'}.
        Devuelve lista [(layer_id, [(x,y),...]), ...] o None."""
        L = {'F': F_layer, 'B': B_layer}
        h, w = self.h, self.w
        INF = float('inf')
        dist = {F_layer: np.full((h, w), INF, dtype=np.float64),
                B_layer: np.full((h, w), INF, dtype=np.float64)}
        prev = {F_layer: [[None] * w for _ in range(h)], B_layer: [[None] * w for _ in range(h)]}
        heap = []
        ix1, iy1 = self._cell(*p1)
        ix2, iy2 = self._cell(*p2)
        # El punto exacto de origen/destino es cobre real ya existente y valido
        # en el board actual (0 violaciones DRC) - forzarlo transitable evita
        # que la cuantizacion de la grilla lo bloquee por error. El chequeo
        # geometrico EXACTO (no-grilla) sigue aplicando sobre cada segmento
        # antes de comprometer nada al board (simplify_polyline + track_clear).
        for l in layers1:
            layer = L[l]
            self.free[layer][iy1, ix1] = True
        for l in layers2:
            layer = L[l]
            self.free[layer][iy2, ix2] = True
        for l in layers1:
            layer = L[l]
            dist[layer][iy1, ix1] = 0.0
            heapq.heappush(heap, (0.0, layer, ix1, iy1))
        target_layers = {L[l] for l in layers2}
        target_cell = (ix2, iy2)
        if not heap:
            return None

        neigh = [(-1, 0, 1.0), (1, 0, 1.0), (0, -1, 1.0), (0, 1, 1.0),
                 (-1, -1, math.sqrt(2)), (-1, 1, math.sqrt(2)), (1, -1, math.sqrt(2)), (1, 1, math.sqrt(2))]
        res = self.res
        best_found = None
        while heap:
            d, layer, cx, cy = heapq.heappop(heap)
            if d > dist[layer][cy, cx] + 1e-9:
                continue
            if (cx, cy) == target_cell and layer in target_layers:
                best_found = (layer, cx, cy)
                break
            for dxn, dyn, cost in neigh:
                nx, ny = cx + dxn, cy + dyn
                if not (0 <= nx < w and 0 <= ny < h):
                    continue
                if not self.free[layer][ny, nx]:
                    continue
                nd = d + cost * res
                if nd < dist[layer][ny, nx]:
                    dist[layer][ny, nx] = nd
                    prev[layer][ny][nx] = (layer, cx, cy)
                    heapq.heappush(heap, (nd, layer, nx, ny))
            other = B_layer if layer == F_layer else F_layer
            if self.via_free[F_layer][cy, cx] and self.via_free[B_layer][cy, cx]:
                nd = d + VIA_PENALTY_MM
                if nd < dist[other][cy, cx]:
                    dist[other][cy, cx] = nd
                    prev[other][cy][cx] = ('via', layer, cx, cy)
                    heapq.heappush(heap, (nd, other, cx, cy))
        if not best_found:
            return None
        # reconstruir camino
        path = []  # lista de (layer, ix, iy) o ('via', ix, iy)
        node = best_found
        cur_layer, cx, cy = node
        chain = [(cur_layer, cx, cy)]
        while True:
            pv = prev[cur_layer][cy][cx]
            if pv is None:
                break
            if pv[0] == 'via':
                _, plyr, pcx, pcy = pv
                chain.append(('via', cx, cy))
                cur_layer, cx, cy = plyr, pcx, pcy
                chain.append((cur_layer, cx, cy))
            else:
                _, pcx, pcy = pv
                cur_layer, cx, cy = pv
                chain.append((cur_layer, cx, cy))
        chain.reverse()
        # convertir a segmentos por capa con vias en las transiciones
        segments = []  # (layer, [pts])
        vias = []      # (x,y)
        cur_layer = None
        cur_pts = []
        for node in chain:
            if node[0] == 'via':
                x = self.x0 + node[1] * res; y = self.y0 + node[2] * res
                if cur_pts:
                    cur_pts.append((x, y))
                    segments.append((cur_layer, cur_pts))
                vias.append((x, y))
                cur_pts = [(x, y)]
            else:
                layer, ix, iy = node
                x = self.x0 + ix * res; y = self.y0 + iy * res
                if cur_layer is None:
                    cur_layer = layer
                elif layer != cur_layer:
                    cur_layer = layer
                cur_pts.append((x, y))
        if cur_pts:
            segments.append((cur_layer, cur_pts))
        return segments, vias


def choose_resolution(dx, dy):
    area = max(dx * dy, 1.0)
    res = math.sqrt(area / 260000.0)
    return min(max(res, 0.05), 0.20)


def simplify_polyline(pts, layer, width, net, obs, exempt_cutouts=False):
    """Line-of-sight greedy simplification usando el chequeo EXACTO (no
    grilla). Garantiza que cada segmento final es realmente valido."""
    if len(pts) < 2:
        return pts
    out = [pts[0]]
    i = 0
    while i < len(pts) - 1:
        j = len(pts) - 1
        while j > i + 1:
            x1, y1 = out[-1]; x2, y2 = pts[j]
            if obs.track_clear(x1, y1, x2, y2, width, net):
                break
            j -= 1
        out.append(pts[j])
        i = j
    return out


def route_grid(p1, layers1, p2, layers2, net, width, via_d, via_drill, exempt_rects=()):
    for margin in (5.0, 9.0, 15.0, 24.0, 36.0):
        x0 = min(p1[0], p2[0]) - margin; x1 = max(p1[0], p2[0]) + margin
        y0 = min(p1[1], p2[1]) - margin; y1 = max(p1[1], p2[1]) + margin
        x0 = max(x0, BOARD_LEFT); x1 = min(x1, BOARD_RIGHT)
        y0 = max(y0, BOARD_BOTTOM); y1 = min(y1, BOARD_TOP)
        res = choose_resolution(x1 - x0, y1 - y0)
        gr = GridRouter(x0, y0, x1, y1, res, net, width, via_d, via_drill, exempt_rects)
        result = gr.route(p1, layers1, p2, layers2)
        if result:
            return result
        if x0 <= BOARD_LEFT and x1 >= BOARD_RIGHT and y0 <= BOARD_BOTTOM and y1 >= BOARD_TOP:
            break  # ya cubrimos todo el board, no tiene sentido seguir agrandando
    return None


def _rollback(added_tracks, added_vias, checkpoint):
    for t in added_tracks:
        brd.Remove(t)
    for v in added_vias:
        pos = v.GetPosition()
        key = (round(pos.x / MM, 3), round(pos.y / MM, 3), v.GetNetname())
        existing_vias.discard(key)
        brd.Remove(v)
    for layer in (F_layer, B_layer):
        nt, nv = checkpoint[layer]
        del OBS[layer].tracks[nt:]
        del OBS[layer].vias[nv:]


def commit_route(segments, vias, net, width, via_d, via_drill, obs_map):
    """Todo o nada: si cualquier parte falla, se revierte exactamente lo que
    este intento agrego (board + obstaculos), sin dejar copper huerfano."""
    checkpoint = {layer: (len(OBS[layer].tracks), len(OBS[layer].vias)) for layer in (F_layer, B_layer)}
    added_tracks, added_vias = [], []

    for (x, y) in vias:
        coords, vobj, ok = place_via_if_new(x, y, net, exempt_cutouts=True)
        if not ok:
            _rollback(added_tracks, added_vias, checkpoint)
            return False
        if vobj is not None:
            added_vias.append(vobj)

    for layer, pts in segments:
        simp = simplify_polyline(pts, layer, width, net.GetNetname(), obs_map[layer])
        for i in range(len(simp) - 1):
            x1, y1 = simp[i]; x2, y2 = simp[i + 1]
            if math.hypot(x2 - x1, y2 - y1) < 0.005:
                continue
            if not obs_map[layer].track_clear(x1, y1, x2, y2, width, net.GetNetname()):
                _rollback(added_tracks, added_vias, checkpoint)
                return False
        for i in range(len(simp) - 1):
            x1, y1 = simp[i]; x2, y2 = simp[i + 1]
            if math.hypot(x2 - x1, y2 - y1) < 0.005:
                continue
            t = add_track_obj(x1, y1, x2, y2, layer, width, net)
            obs_map[layer].add_track(x1, y1, x2, y2, width, net.GetNetname())
            added_tracks.append(t)
    return True


# El board admite legalmente track/via mas angostos que el ancho "de
# preferencia" de la netclass (eso es solo el default con el que el editor
# dibuja pistas nuevas; el DRC real solo exige el minimo absoluto del board,
# ver kicad/nebula_qshield.kicad_pro net_settings). Varios de los 38 pares
# quedan con el pad literalmente encajonado entre pines vecinos de otras
# nets a ~0.25-0.45 mm, insuficiente para el ancho de la netclass pero de
# sobra para un tramo corto de fan-out al minimo legal - tecnica estandar
# de PCB (neck-down) en vez de mover el componente.
BOARD_MIN_TRACK_WIDTH = 0.2
BOARD_MIN_VIA_D, BOARD_MIN_VIA_DRILL = 0.6, 0.3


def width_candidates(netclass_width, net_floor):
    """net_floor = min_track_width(net_name): el piso REAL de esa net segun
    las reglas custom del .kicad_dru (Power/HighCurrent/RelayHV exigen mas
    que el piso generico del board). Nunca se ofrece un ancho por debajo de
    eso, aunque el board admita 0.2mm en general."""
    cands = [netclass_width]
    for w in (0.3, 0.25, BOARD_MIN_TRACK_WIDTH):
        if net_floor - 1e-9 <= w < netclass_width - 1e-9 and w not in cands:
            cands.append(w)
    if net_floor < netclass_width - 1e-9 and net_floor not in cands:
        cands.append(net_floor)
    return cands


def route_pair(pair, tag=''):
    it1, it2 = pair
    net_name = it1['net']
    if it2['net'] != net_name:
        log(f'  [{tag}] nets distintas en el par ({it1["net"]} vs {it2["net"]}), skip'); return False
    net = brd.FindNet(net_name)
    if not net:
        log(f'  [{tag}] net {net_name} no encontrada en el board'); return False
    x1, y1, layers1, is_pad1, rect1 = connection_point(it1)
    x2, y2, layers2, is_pad2, rect2 = connection_point(it2)
    full_width = track_width(net_name)
    full_via_d, full_via_drill = via_size(net_name)
    common = layers1 & layers2
    exempt = tuple(r for r in (rect1, rect2) if r)

    widths = width_candidates(full_width, min_track_width(net_name))

    # 1) intento directo / codo (rapido) en cada capa comun, ancho completo
    #    primero y despues progresivamente mas angosto
    for width in widths:
        for lname in common:
            layer = F_layer if lname == 'F' else B_layer
            obs = OBS[layer]
            if obs.track_clear(x1, y1, x2, y2, width, net_name):
                add_track_obj(x1, y1, x2, y2, layer, width, net)
                obs.add_track(x1, y1, x2, y2, width, net_name)
                if width < full_width - 1e-9:
                    log(f'  [{tag}] cerrado directo con ancho reducido {width} mm (netclass pide {full_width} mm)')
                return True

    # 2) grilla (Dijkstra, con transicion por via si hace falta). Se prueba
    #    con el via de la netclass y, si no entra, con el via minimo legal.
    via_options = [(full_via_d, full_via_drill)]
    if full_via_d > BOARD_MIN_VIA_D + 1e-9:
        via_options.append((BOARD_MIN_VIA_D, BOARD_MIN_VIA_DRILL))

    for width in widths:
        for via_d, via_drill in via_options:
            result = route_grid((x1, y1), layers1, (x2, y2), layers2, net_name, width, via_d, via_drill, exempt)
            if not result:
                continue
            segments, vias = result
            ok = commit_route(segments, vias, net, width, via_d, via_drill, OBS)
            if ok:
                if width < full_width - 1e-9 or via_d < full_via_d - 1e-9:
                    log(f'  [{tag}] cerrado por grilla con ancho {width} mm / via {via_d}/{via_drill} mm '
                        f'(netclass pide {full_width} mm / {full_via_d}/{full_via_drill} mm)')
                return True
    return False


# ==========================================================================
# Fase B: nudge de pasivos analogicos (<=2 mm) para pares que no entraron
# ==========================================================================
NUDGE_OFFSETS = []
for mag in (1.0, 2.0):
    for ang_deg in (90, 270, 0, 180, 45, 135, 225, 315):  # +Y primero (sugerencia Spark), luego resto
        a = math.radians(ang_deg)
        NUDGE_OFFSETS.append((round(mag * math.cos(a), 4), round(mag * math.sin(a), 4)))


def footprint_pad_touches(fp, pad_margin=0.12):
    """Para cada pad del footprint, lista de tracks/vias (de su MISMA net) que
    tocan su rect actual -> lo que hay que reconectar si el pad se mueve."""
    touches = {}
    for p in fp.Pads():
        rect = get_pad_rect(p)
        net = p.GetNetname()
        items = []
        for t in brd.GetTracks():
            if t.GetNetname() != net:
                continue
            if isinstance(t, pcbnew.PCB_VIA):
                vx, vy = t.GetPosition().x / MM, t.GetPosition().y / MM
                if point_in_pad(vx, vy, rect, pad_margin):
                    items.append(('via', vx, vy, t))
            else:
                sx, sy = t.GetStart().x / MM, t.GetStart().y / MM
                ex, ey = t.GetEnd().x / MM, t.GetEnd().y / MM
                if point_in_pad(sx, sy, rect, pad_margin):
                    items.append(('track_start', sx, sy, t))
                elif point_in_pad(ex, ey, rect, pad_margin):
                    items.append(('track_end', ex, ey, t))
        touches[p.GetNumber()] = (net, rect, items)
    return touches


def try_nudge(ref, target_pair):
    fp = brd.FindFootprintByReference(ref)
    if not fp:
        return False
    orig_pos = fp.GetPosition()
    orig_x, orig_y = orig_pos.x / MM, orig_pos.y / MM
    pre_touches = footprint_pad_touches(fp)

    for dx, dy in NUDGE_OFFSETS:
        new_x, new_y = orig_x + dx, orig_y + dy
        fp.SetPosition(pcbnew.VECTOR2I(int(round(new_x * MM)), int(round(new_y * MM))))
        added_tracks = []
        added_vias = []
        success = True
        checkpoint = {layer: (len(OBS[layer].tracks), len(OBS[layer].vias)) for layer in (F_layer, B_layer)}

        for pad_num, (net_name, old_rect, items) in pre_touches.items():
            pad = fp.FindPadByNumber(pad_num)
            new_center = (pad.GetPosition().x / MM, pad.GetPosition().y / MM)
            net = brd.FindNet(net_name)
            width = track_width(net_name)
            via_d, via_drill = via_size(net_name)
            layer = F_layer if pad.GetLayerSet().Contains(pcbnew.F_Cu) else B_layer
            obs = OBS[layer]

            if items:
                # pad ya tenia copper: reconectar con un jumper corto desde el
                # nuevo centro del pad hasta el punto de contacto original
                # (ese track/via existente no se movio, sigue fisicamente ahi).
                ox, oy = items[0][1], items[0][2]
                if math.hypot(new_center[0] - ox, new_center[1] - oy) < 0.01:
                    continue
                if not obs.track_clear(new_center[0], new_center[1], ox, oy, width, net_name):
                    success = False; break
                t = add_track_obj(new_center[0], new_center[1], ox, oy, layer, width, net)
                obs.add_track(new_center[0], new_center[1], ox, oy, width, net_name)
                added_tracks.append(t)
            else:
                # este es el pad que estaba desconectado: rutear el par target
                other_item = target_pair[0] if target_pair[1]['ref'] == ref else target_pair[1]
                ox, oy, olayers, _, orect = connection_point(other_item)
                res = route_grid(new_center, {'F' if layer == F_layer else 'B'}, (ox, oy), olayers,
                                  net_name, width, via_d, via_drill,
                                  exempt_rects=(get_pad_rect(pad),) + ((orect,) if orect else ()))
                if not res:
                    success = False; break
                segs, vias = res
                ok = True
                for (vx, vy) in vias:
                    coords, vobj, vok = place_via_if_new(vx, vy, net, exempt_cutouts=True)
                    if not vok:
                        ok = False; break
                    if vobj is not None:
                        added_vias.append(vobj)
                if not ok:
                    success = False; break
                for slayer, pts in segs:
                    simp = simplify_polyline(pts, slayer, width, net_name, OBS[slayer])
                    for i in range(len(simp) - 1):
                        sx1, sy1 = simp[i]; sx2, sy2 = simp[i + 1]
                        if math.hypot(sx2 - sx1, sy2 - sy1) < 0.005:
                            continue
                        if not OBS[slayer].track_clear(sx1, sy1, sx2, sy2, width, net_name):
                            ok = False; break
                        tt = add_track_obj(sx1, sy1, sx2, sy2, slayer, width, net)
                        OBS[slayer].add_track(sx1, sy1, sx2, sy2, width, net_name)
                        added_tracks.append(tt)
                    if not ok:
                        break
                if not ok:
                    success = False; break

        if success:
            log(f'  [nudge] {ref} movido ({dx:+.1f},{dy:+.1f}) mm -> ({new_x:.3f},{new_y:.3f})')
            return True

        # revertir: sacar todo lo agregado en este intento (board + obstaculos
        # via checkpoint, sin reconstruir todo desde cero) y restaurar posicion
        _rollback(added_tracks, added_vias, checkpoint)
        fp.SetPosition(pcbnew.VECTOR2I(int(round(orig_x * MM)), int(round(orig_y * MM))))

    fp.SetPosition(orig_pos)
    return False


# ==========================================================================
# Main
# ==========================================================================
def main():
    refresh_drc_report()
    pairs = parse_pairs()
    zone_pairs = [p for p in pairs if p[0]['type'] == 'Zone' or p[1]['type'] == 'Zone']
    if zone_pairs:
        # kicad-cli reporta a veces (no-deterministico, ligado al orden de
        # relleno de zonas) un par Zone-Zone sin coordenada real utilizable
        # como punto de conexion (cae en el propio corner del board). No es
        # un target de ruteo punto-a-punto valido: se omite y se documenta.
        print(f'omitidos (Zone, no accionable): {len(zone_pairs)}')
        pairs = [p for p in pairs if p not in zone_pairs]
    print(f'pares leidos de {os.path.relpath(DRC_PATH, ROOT)}: {len(pairs)} (+{len(zone_pairs)} Zone omitidos)')

    def pair_dist(p):
        return math.hypot(p[0]['x'] - p[1]['x'], p[0]['y'] - p[1]['y'])

    order = sorted(range(len(pairs)), key=lambda i: pair_dist(pairs[i]))

    closed, failed = [], []
    for rank, idx in enumerate(order):
        p = pairs[idx]
        tag = f'{rank + 1}/{len(pairs)} {p[0]["net"]}'
        t0 = time.time()
        ok = route_pair(p, tag)
        dt = time.time() - t0
        status = 'OK' if ok else 'FAIL'
        print(f'[{status}] ({dt:5.1f}s) {tag}: {p[0]["ref"] or p[0]["type"]}@({p[0]["x"]:.2f},{p[0]["y"]:.2f}) '
              f'<-> {p[1]["ref"] or p[1]["type"]}@({p[1]["x"]:.2f},{p[1]["y"]:.2f})', flush=True)
        (closed if ok else failed).append(p)

    # Fase B: nudge de pasivos analogicos para lo que sigue fallando
    still_failed = []
    nudged = []
    for p in failed:
        refs_in_pair = [it['ref'] for it in p if it['ref'] in ANALOG_PASSIVES]
        done = False
        for ref in refs_in_pair:
            t0 = time.time()
            nudge_ok = try_nudge(ref, p)
            print(f'[nudge {"OK" if nudge_ok else "FAIL"}] ({time.time() - t0:5.1f}s) {ref} para par {p[0]["net"]}', flush=True)
            if nudge_ok:
                nudged.append((ref, p))
                done = True
                break
        if done:
            closed.append(p)
        else:
            still_failed.append(p)

    print()
    print('=== Resumen ===')
    print(f'Pares intentados: {len(pairs)}')
    print(f'Cerrados:         {len(closed)}')
    print(f'  de los cuales via nudge de pasivo: {len(nudged)}')
    for ref, p in nudged:
        print(f'    - {ref}: par {p[0]["net"]}')
    print(f'Fallidos:         {len(still_failed)}')
    for p in still_failed:
        print(f'  - {p[0]["net"]}: {p[0]["ref"] or p[0]["type"]}@({p[0]["x"]:.2f},{p[0]["y"]:.2f}) '
              f'<-> {p[1]["ref"] or p[1]["type"]}@({p[1]["x"]:.2f},{p[1]["y"]:.2f})')

    if DRY_RUN:
        print('\n--dry-run: NO se refillearon zonas ni se guardo el board.')
        return

    print('\nRefilling zonas...')
    filler = pcbnew.ZONE_FILLER(brd)
    filler.Fill(brd.Zones())
    brd.BuildConnectivity()
    pcbnew.SaveBoard(BOARD_PATH, brd)
    print('Guardado', BOARD_PATH)


if __name__ == '__main__':
    main()
