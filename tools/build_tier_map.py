import json
from pathlib import Path

components = json.loads(Path('kicad/actual_components.json').read_text())

# DNP convention: list tiers where component is NOT populated.
# Tiers: Essential, Insight, Signature.

def tier_for_component(c):
    ref = c['Reference']
    val = c['Value']
    desc = c['Description']
    sheet = c['sheet']
    text = f"{ref} {val} {desc}"

    # Power management / HMI / common
    if sheet == 'power_management.kicad_sch':
        return 'NO'  # populated all tiers

    # Digital / I2C
    if ref in ('J8','J9','U21','R19','R20','D9','J20'):
        return 'NO'
    if ref in ('U14','J15','R21','C25','C26'):
        # HX711 load cell -> Insight+
        return 'Essential'
    if ref in ('J10',):
        # Qwiic cell density connector -> DNP all (use RS485 Hamilton instead)
        return 'Essential,Insight,Signature'
    if ref in ('J11','J12','J13','J14'):
        # EZO optional in all tiers
        return 'Optional'
    if ref in ('U15','J16','U22','U23','Y1','C31','C32','C33','R38'):
        # RS485 Hamilton bridge / MAX3485 -> Signature only
        return 'Essential,Insight'
    if ref == 'R22':
        return 'All'
    if ref in ('LED4','R23'):
        return 'NO'

    # Actuators
    if sheet == 'actuator_drivers.kicad_sch':
        if ref in ('U16','U17','Q1','Q2','D10','D11','F2','J17','R24','R25'):
            # recirculation motor driver -> Insight+
            return 'Essential'
        if ref in ('U18','Q3','K1','D12','F3','J18','R26'):
            # CO2/H2 gas solenoid -> Insight+
            return 'Essential'
        if ref in ('U19','Q4','K2','D13','F4','J19','R27'):
            # chiller -> Insight+ (moved from Signature)
            return 'Essential'
        if ref in ('U20','Q5','D14','R28','C27','J22'):
            # PWM proportional gas valve -> not used (single gas via solenoid)
            return 'All'

    # Analog acquisition
    if sheet == 'analog_acquisition.kicad_sch':
        # pH and ORP common
        if ref in ('J2','J3','TP1','TP2'):
            return 'NO'
        # Temperature common (J6)
        if ref == 'J6':
            return 'NO'
        # CO2 pressure -> Insight+
        if ref == 'J4':
            return 'Essential'
        # DO -> Insight+
        if ref == 'J5':
            return 'Essential'
        # Humidity -> removed (DNP all)
        if ref == 'J7':
            return 'Essential,Insight,Signature'
        # CO2 channel (J4, D5, R11, C18, R12, U10)
        if ref in ('D5','R11','C18','R12','U10'):
            return 'Essential'
        # DO channel (J5, D6, R13, C19, R14, U11, U12, U13, C20, C21, T3, D23, D24, C30)
        if ref in ('D6','R13','C19','R14','U11','U12','U13','C20','C21','T3','D23','D24','C30'):
            return 'Essential'
        # Humidity channel (J7 already handled, plus D8, R17, R18, C23)
        if ref in ('D8','R17','R18','C23'):
            return 'Essential,Insight,Signature'

    # Default: keep existing DNP value if set, else NO
    return c.get('DNP','') if c.get('DNP') not in ('','NO') else 'NO'

mapping = {}
for c in components:
    mapping[c['Reference']] = tier_for_component(c)

# Write mapping
Path('kicad/tier_dnp_mapping.json').write_text(json.dumps(mapping, indent=2))
print('wrote tier_dnp_mapping.json')
print(json.dumps({t: len([v for v in mapping.values() if v==t]) for t in sorted(set(mapping.values()))}, indent=2))
