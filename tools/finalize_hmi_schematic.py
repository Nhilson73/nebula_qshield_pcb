#!/usr/bin/env python3
"""Finalize hmi_connectors.kicad_sch: corrected J21, I2C pull-ups, clean wiring."""
import copy
import uuid
from pathlib import Path

import sexpdata

REPO = Path('/home/ubuntu/repos/nebula_qshield_pcb')
SCH = REPO / 'kicad' / 'hmi_connectors.kicad_sch'
SYM_LIB = REPO / 'kicad' / 'lib' / 'nebula_symbols.kicad_sym'
PM_SCH = REPO / 'kicad' / 'power_management.kicad_sch'

J21_POS = (88.9, 119.38, 0.0)

PIN_NETS = {
    '1': None, '2': None, '3': '/MCU_NRST', '4': '/3V3_RAIL', '5': '/5V_RAIL',
    '6': 'GND', '7': 'GND', '8': '/12V_RAIL', '9': '/PH_ADC', '10': '/ORP_ADC',
    '11': '/TEMP_ADC', '12': '/HUM_ADC', '13': '/CO2_ADC', '14': '/DO_ADC',
    '15': '/HMI_RX', '16': '/HMI_TX', '17': '/HX711_DOUT', '18': '/HX711_SCK',
    '19': '/PUMP_DIR', '20': '/PUMP_PWM', '21': '/CO2_PWM', '22': '/CO2_SOL_CTL',
    '23': '/MCU_WDI', '24': '/CHILLER_CTL', '25': None, '26': None, '27': None,
    '28': '/LED_STATUS', '29': 'GND', '30': None, '31': '/I2C_SDA', '32': '/I2C_SCL',
}

PIN_SHAPE = {
    '1': None, '2': None, '3': 'input', '4': 'bidirectional', '5': 'bidirectional',
    '6': 'bidirectional', '7': 'bidirectional', '8': 'input', '9': 'input', '10': 'input',
    '11': 'input', '12': 'input', '13': 'input', '14': 'input', '15': 'input',
    '16': 'output', '17': 'input', '18': 'output', '19': 'output', '20': 'output',
    '21': 'output', '22': 'output', '23': 'output', '24': 'output', '25': None,
    '26': None, '27': None, '28': 'output', '29': 'bidirectional', '30': None,
    '31': 'bidirectional', '32': 'bidirectional',
}


def S(name):
    return sexpdata.Symbol(name)


def new_uuid():
    return str(uuid.uuid4())


def find_first(lst, pred):
    for item in lst:
        if pred(item):
            return item
    return None


def is_symbol_start(obj, name):
    return isinstance(obj, list) and len(obj) > 0 and str(obj[0]) == 'symbol' and len(obj) > 1 and obj[1] == name


def find_lib_symbols(expr):
    for e in expr:
        if isinstance(e, list) and len(e) > 0 and str(e[0]) == 'lib_symbols':
            return e
    raise RuntimeError('lib_symbols not found')


def find_symbol(lib_symbols, name):
    for e in lib_symbols:
        if is_symbol_start(e, name):
            return e
    return None


def set_power_type(sym_expr, pin_nums, new_type='passive'):
    """Change pin type for specified pin numbers in a symbol's _1_1 unit."""
    for sub in sym_expr:
        if not isinstance(sub, list) or len(sub) <= 1 or str(sub[0]) != 'symbol' or not str(sub[1]).endswith('_1_1'):
            continue
        for pin in sub:
            if not isinstance(pin, list) or len(pin) == 0 or str(pin[0]) != 'pin':
                continue
            num_obj = find_first(pin, lambda x: isinstance(x, list) and len(x) > 0 and str(x[0]) == 'number')
            if num_obj and len(num_obj) > 1 and num_obj[1] in pin_nums:
                pin[1] = S(new_type)


def get_pin_positions(sym_expr, at_x, at_y):
    """Return {number: {x,y,side,name,type}} for a J21 symbol."""
    pins = {}
    for sub in sym_expr:
        if not isinstance(sub, list) or len(sub) <= 1 or str(sub[0]) != 'symbol' or not str(sub[1]).endswith('_1_1'):
            continue
        for pin in sub:
            if not isinstance(pin, list) or len(pin) == 0 or str(pin[0]) != 'pin':
                continue
            at = find_first(pin, lambda x: isinstance(x, list) and len(x) > 0 and str(x[0]) == 'at')
            num_obj = find_first(pin, lambda x: isinstance(x, list) and len(x) > 0 and str(x[0]) == 'number')
            name_obj = find_first(pin, lambda x: isinstance(x, list) and len(x) > 0 and str(x[0]) == 'name')
            if not at or not num_obj:
                continue
            sx, sy = float(at[1]), float(at[2])
            number = num_obj[1]
            pins[number] = {
                'name': name_obj[1] if name_obj else '',
                'type': str(pin[1]),
                'x': round(at_x + sx, 6),
                'y': round(at_y - sy, 6),
                'side': 'left' if sx < 0 else 'right',
            }
    return pins


def in_j21_region(x, y):
    if not (90.0 <= y <= 150.0):
        return False
    return (50.0 <= x <= 74.0) or (101.0 <= x <= 130.0)


def wire_touching_region(wire):
    pts = find_first(wire, lambda x: isinstance(x, list) and len(x) > 0 and str(x[0]) == 'pts')
    if not pts:
        return False
    for p in pts:
        if isinstance(p, list) and len(p) > 0 and str(p[0]) == 'xy':
            if in_j21_region(float(p[1]), float(p[2])):
                return True
    return False


def at_touching_region(elem):
    at = find_first(elem, lambda x: isinstance(x, list) and len(x) > 0 and str(x[0]) == 'at')
    if at and len(at) >= 3:
        return in_j21_region(float(at[1]), float(at[2]))
    return False


def is_j21_wiring(elem):
    if not isinstance(elem, list) or len(elem) == 0:
        return False
    tag = str(elem[0])
    if tag == 'wire':
        return wire_touching_region(elem)
    if tag in ('label', 'hierarchical_label', 'no_connect'):
        return at_touching_region(elem)
    return False


def gen_j21_elements(pins):
    elements = []
    for n in range(1, 33):
        ns = str(n)
        pin = pins[ns]
        net = PIN_NETS[ns]
        px, py = pin['x'], pin['y']
        if net is None:
            elements.append([S('no_connect'), [S('at'), px, py], [S('uuid'), new_uuid()]])
            continue
        label_x = 55.88 if pin['side'] == 'left' else 121.92
        rot = 180 if pin['side'] == 'left' else 0
        shape = PIN_SHAPE[ns]
        label_text = net.lstrip('/')
        wire_id = new_uuid()
        label_id = new_uuid()
        elements.append([
            S('wire'),
            [S('pts'), [S('xy'), px, py], [S('xy'), label_x, py]],
            [S('stroke'), [S('width'), 0], [S('type'), S('default')]],
            [S('uuid'), wire_id],
        ])
        elements.append([
            S('hierarchical_label'), label_text,
            [S('shape'), S(shape)],
            [S('at'), label_x, py, rot],
            [S('effects'), [S('font'), [S('size'), 1.27, 1.27]]],
            [S('uuid'), label_id],
        ])
    return elements


def gen_resistor(ref, center, value, pin2_label, pin2_y, pin1_label, pin1_y):
    """Vertical Device:R; pin2 top, pin1 bottom."""
    cx, cy = center[0], center[1]
    comp_uuid = new_uuid()
    pin1_uuid = new_uuid()
    pin2_uuid = new_uuid()
    comp = [
        S('symbol'),
        [S('lib_id'), 'Device:R'],
        [S('at'), cx, cy, 0],
        [S('unit'), 1],
        [S('exclude_from_sim'), S('no')],
        [S('in_bom'), S('yes')],
        [S('on_board'), S('yes')],
        [S('uuid'), comp_uuid],
        [S('property'), 'Reference', ref, [S('at'), cx, cy - 5.08, 0], [S('effects'), [S('font'), [S('size'), 1.27, 1.27]]]],
        [S('property'), 'Value', value, [S('at'), cx, cy + 5.08, 0], [S('effects'), [S('font'), [S('size'), 1.27, 1.27]]]],
        [S('property'), 'Footprint', 'nebula_footprints:R_0603_1608Metric', [S('at'), cx, cy, 0], [S('effects'), [S('font'), [S('size'), 1.27, 1.27]], [S('hide'), S('yes')]]],
        [S('pin'), '1', [S('uuid'), pin1_uuid]],
        [S('pin'), '2', [S('uuid'), pin2_uuid]],
        [S('instances'),
            [S('project'), 'nebula_qshield',
                [S('path'), '/c6da75fc-541f-4933-b134-f5eb8982a11b/f787f9da-3fea-4da5-bd0c-c3201676b3de',
                    [S('reference'), ref], [S('unit'), 1]
                ]
            ]
        ],
    ]
    # pin2 top branch to label (stay on 1.27 mm grid)
    lx2 = cx + 3.81
    elements = [comp]
    elements.append([
        S('wire'),
        [S('pts'), [S('xy'), cx, pin2_y], [S('xy'), lx2, pin2_y]],
        [S('stroke'), [S('width'), 0], [S('type'), S('default')]],
        [S('uuid'), new_uuid()],
    ])
    elements.append([
        S('label'), pin2_label,
        [S('at'), lx2, pin2_y, 0],
        [S('effects'), [S('font'), [S('size'), 1.27, 1.27]]],
        [S('uuid'), new_uuid()],
    ])
    # pin1 bottom branch to label
    lx1 = cx + 3.81
    elements.append([
        S('wire'),
        [S('pts'), [S('xy'), cx, pin1_y], [S('xy'), lx1, pin1_y]],
        [S('stroke'), [S('width'), 0], [S('type'), S('default')]],
        [S('uuid'), new_uuid()],
    ])
    elements.append([
        S('label'), pin1_label,
        [S('at'), lx1, pin1_y, 0],
        [S('effects'), [S('font'), [S('size'), 1.27, 1.27]]],
        [S('uuid'), new_uuid()],
    ])
    return elements


def main():
    # 1. Update symbol library
    sym_expr = sexpdata.loads(SYM_LIB.read_text())
    for item in sym_expr:
        if is_symbol_start(item, 'Arduino_UNO_Q_Shield_Header_Corrected'):
            set_power_type(item, ['4', '5'], 'passive')
            break
    SYM_LIB.write_text(sexpdata.dumps(sym_expr, pretty_print=True))

    # 2. Load schematic
    expr = sexpdata.loads(SCH.read_text())
    lib_symbols = find_lib_symbols(expr)

    # 3. Update embedded corrected symbol
    embedded_corr = find_symbol(lib_symbols, 'nebula_symbols:Arduino_UNO_Q_Shield_Header_Corrected')
    if not embedded_corr:
        embedded_corr = find_symbol(lib_symbols, 'Arduino_UNO_Q_Shield_Header_Corrected')
    if embedded_corr:
        set_power_type(embedded_corr, ['4', '5'], 'passive')
    else:
        raise RuntimeError('Corrected J21 symbol not found in hmi_connectors lib_symbols')

    # 4. Embed Device:R from global or power_management
    pm_expr = sexpdata.loads(PM_SCH.read_text())
    pm_libs = find_lib_symbols(pm_expr)
    device_r = find_symbol(pm_libs, 'Device:R')
    if not device_r:
        # fallback to global Device library
        global_dev = sexpdata.loads(Path('/usr/share/kicad/symbols/Device.kicad_sym').read_text())
        for item in global_dev:
            if is_symbol_start(item, 'R'):
                device_r = copy.deepcopy(item)
                device_r[1] = 'Device:R'
                break
    if not device_r:
        raise RuntimeError('Device:R symbol not found')
    if not find_symbol(lib_symbols, 'Device:R'):
        lib_symbols.append(copy.deepcopy(device_r))

    # 5. Remove old J21 wiring in the J21 region
    new_expr = [expr[0]]
    for item in expr[1:]:
        if is_j21_wiring(item):
            continue
        new_expr.append(item)

    # 6. Get pin positions and generate wiring
    pins = get_pin_positions(embedded_corr, J21_POS[0], J21_POS[1])
    new_expr.extend(gen_j21_elements(pins))

    # 7. Add I2C pull-up resistors
    # I2C_SDA line at y=135.89, I2C_SCL at y=138.43
    # Place pull-ups on the 1.27 mm schematic grid
    r36_x, r36_y = 114.3, 139.7   # pin2 on I2C_SDA wire (y=135.89)
    r37_x, r37_y = 119.38, 142.24 # pin2 on I2C_SCL wire (y=138.43)
    for elem in gen_resistor('R36', (r36_x, r36_y, 0.0), '4.7k',
                             'I2C_SDA', r36_y - 3.81,
                             '3V3_RAIL', r36_y + 3.81):
        new_expr.append(elem)
    for elem in gen_resistor('R37', (r37_x, r37_y, 0.0), '4.7k',
                             'I2C_SCL', r37_y - 3.81,
                             '3V3_RAIL', r37_y + 3.81):
        new_expr.append(elem)

    SCH.write_text(sexpdata.dumps(new_expr, pretty_print=True))
    print('Finalized', SCH)


if __name__ == '__main__':
    main()
