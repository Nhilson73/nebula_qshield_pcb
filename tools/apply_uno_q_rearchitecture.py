#!/usr/bin/env python3
"""Apply UNO Q shield re-architecture to the Q-Shield PCB."""
import pcbnew
import shutil
import os
import sys

SRC = '/workspace/kicad/nebula_qshield.kicad_pcb'
DST = '/workspace/kicad/nebula_qshield_rearch.kicad_pcb'

# Copy source to destination for a safe sandbox run
shutil.copy(SRC, DST)
print('copied src to dst', flush=True)
board = pcbnew.LoadBoard(DST)
print('loaded board', len(list(board.GetFootprints())), flush=True)

# footprint origin (mm -> nm)
ORIGIN_MM = (5.08, 35.56)
ORIGIN = pcbnew.VECTOR2I(int(ORIGIN_MM[0] * 1e6), int(ORIGIN_MM[1] * 1e6))


def get_net(name):
    net = board.FindNet(name)
    if net is None:
        raise RuntimeError(f'Net not found: {name}')
    return net


PIN_NETS = {
    '1': None, '2': None, '3': '/MCU_NRST', '4': '/3V3_RAIL', '5': '/5V_RAIL',
    '6': 'GND', '7': 'GND', '8': '/12V_RAIL', '9': '/PH_ADC', '10': '/ORP_ADC',
    '11': '/TEMP_ADC', '12': '/HUM_ADC', '13': '/CO2_ADC', '14': '/DO_ADC',
    '15': '/HMI_RX', '16': '/HMI_TX', '17': '/HX711_DOUT', '18': '/HX711_SCK',
    '19': '/PUMP_DIR', '20': '/PUMP_PWM', '21': '/CO2_PWM', '22': '/CO2_SOL_CTL',
    '23': '/MCU_WDI', '24': '/CHILLER_CTL', '25': None, '26': None, '27': None,
    '28': '/LED_STATUS', '29': 'GND', '30': None, '31': '/I2C_SDA', '32': '/I2C_SCL',
}

# Replace J21
old_j21 = None
for fp in board.GetFootprints():
    if str(fp.GetReference()) == 'J21':
        old_j21 = fp
        break
if old_j21 is None:
    print('ERROR: J21 not found', file=sys.stderr); sys.exit(1)

new_fp = pcbnew.FootprintLoad('/workspace/kicad/lib/nebula_footprints.pretty', 'Arduino_UNO_Q_Shield')
new_fp.SetReference('J21')
new_fp.SetValue('Arduino UNO Q Shield')
new_fp.SetPosition(ORIGIN)
new_fp.SetFPID(pcbnew.LIB_ID('nebula_footprints', 'Arduino_UNO_Q_Shield'))

for pad in new_fp.Pads():
    pin = str(pad.GetNumber())
    net_name = PIN_NETS.get(pin)
    if net_name is None:
        pad.SetNetCode(0)
    else:
        pad.SetNet(get_net(net_name))

board.Remove(old_j21)
board.Add(new_fp)
print('Replaced J21 at', ORIGIN_MM, flush=True)

# Relocate colliding components
RELOCATIONS = {
    'D10': (78.74, 49.53, 0), 'D11': (74.93, 82.55, 0), 'F4': (74.93, 54.61, 0),
    'K1': (74.93, 76.20, 90), 'K2': (74.93, 66.04, 90), 'Q4': (74.93, 57.15, 90),
    'U16': (74.93, 86.36, 0), 'U17': (85.09, 82.55, 0), 'U19': (74.93, 34.29, 90),
    'U20': (67.31, 90.17, 0),
}
for ref, (x_mm, y_mm, angle) in RELOCATIONS.items():
    for fp in board.GetFootprints():
        if str(fp.GetReference()) == ref:
            fp.SetPosition(pcbnew.VECTOR2I(int(x_mm*1e6), int(y_mm*1e6)))
            if angle:
                fp.SetOrientation(pcbnew.EDA_ANGLE(angle*10, pcbnew.TENTHS_OF_A_DEGREE_T))
            print(f'Moved {ref}', flush=True)
            break

# Add pull-ups
r36 = pcbnew.FootprintLoad('/workspace/kicad/lib/nebula_footprints.pretty', 'R_0603_1608Metric')
r36.SetReference('R36'); r36.SetValue('4.7k'); r36.SetFPID(pcbnew.LIB_ID('nebula_footprints', 'R_0603_1608Metric'))
r36.SetPosition(pcbnew.VECTOR2I(int(66.04e6), int(88.90e6)))
for pad in r36.Pads():
    if str(pad.GetNumber()) == '1': pad.SetNet(get_net('/3V3_RAIL'))
    else: pad.SetNet(get_net('/I2C_SDA'))
board.Add(r36)

r37 = pcbnew.FootprintLoad('/workspace/kicad/lib/nebula_footprints.pretty', 'R_0603_1608Metric')
r37.SetReference('R37'); r37.SetValue('4.7k'); r37.SetFPID(pcbnew.LIB_ID('nebula_footprints', 'R_0603_1608Metric'))
r37.SetPosition(pcbnew.VECTOR2I(int(68.58e6), int(88.90e6)))
for pad in r37.Pads():
    if str(pad.GetNumber()) == '1': pad.SetNet(get_net('/3V3_RAIL'))
    else: pad.SetNet(get_net('/I2C_SCL'))
board.Add(r37)
print('Added pull-ups', flush=True)


def add_edge_cut_rect(x1, y1, x2, y2):
    shape = pcbnew.PCB_SHAPE(board)
    shape.SetShape(pcbnew.SHAPE_T_POLY)
    shape.SetLayer(pcbnew.Edge_Cuts)
    shape.SetWidth(int(0.1e6))
    shape.SetFilled(False)
    pts = [pcbnew.VECTOR2I(int(x1*1e6), int(y1*1e6)),
           pcbnew.VECTOR2I(int(x2*1e6), int(y1*1e6)),
           pcbnew.VECTOR2I(int(x2*1e6), int(y2*1e6)),
           pcbnew.VECTOR2I(int(x1*1e6), int(y2*1e6)),
           pcbnew.VECTOR2I(int(x1*1e6), int(y1*1e6))]
    shape.SetPolyPoints(pts)
    board.Add(shape)
    print(f'Edge cut {x1},{y1}-{x2},{y2}', flush=True)

add_edge_cut_rect(2.08, 81.56, 23.08, 94.56)
add_edge_cut_rect(13.08, 86.06, 19.08, 94.56)
add_edge_cut_rect(60.08, 85.56, 77.08, 94.56)


def add_keepout_marker(x1, y1, x2, y2, name):
    """Mark keepout area on Eco1.User as a polygon (guideline, not DRC-enforced)."""
    shape = pcbnew.PCB_SHAPE(board)
    shape.SetShape(pcbnew.SHAPE_T_POLY)
    shape.SetLayer(pcbnew.Eco1_User)
    shape.SetWidth(int(0.2e6))
    shape.SetFilled(False)
    pts = [
        pcbnew.VECTOR2I(int(x1*1e6), int(y1*1e6)),
        pcbnew.VECTOR2I(int(x2*1e6), int(y1*1e6)),
        pcbnew.VECTOR2I(int(x2*1e6), int(y2*1e6)),
        pcbnew.VECTOR2I(int(x1*1e6), int(y2*1e6)),
        pcbnew.VECTOR2I(int(x1*1e6), int(y1*1e6)),
    ]
    shape.SetPolyPoints(pts)
    board.Add(shape)
    # label
    cx = int((x1 + x2) * 0.5e6)
    cy = int((y1 + y2) * 0.5e6)
    txt = pcbnew.PCB_TEXT(board)
    txt.SetText(name)
    txt.SetLayer(pcbnew.Eco1_User)
    txt.SetPosition(pcbnew.VECTOR2I(cx, cy))
    txt.SetTextSize(pcbnew.VECTOR2I(int(1e6), int(1e6)))
    txt.SetTextThickness(int(0.15e6))
    board.Add(txt)
    print(f'Keepout marker {name}', flush=True)

add_keepout_marker(17.08, 87.06, 40.08, 94.56, 'JCTL_keepout')
add_keepout_marker(67.08, 68.56, 77.08, 88.56, 'SPI2_keepout')
add_keepout_marker(67.08, 50.56, 77.08, 65.56, 'QWIIC_keepout')
add_keepout_marker(2.08, 65.56, 11.08, 94.56, 'USB_C PMIC_keepout')

board.Save(DST)
print('Saved', DST, flush=True)
