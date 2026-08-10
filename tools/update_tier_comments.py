from pathlib import Path

# Each old/new is literal text. File uses \n as backslash+n (two chars), so raw strings with r"...\n...".
REPLACEMENTS = {
    'kicad/analog_acquisition.kicad_sch': {
        'comments': {
            'Sheet 2 of 5: 6 Analog Channels + Galvanic Isolation (On-Board)': 'Sheet 2 of 5: 5 Analog Channels + Galvanic Isolation (On-Board)',
            'Channels: pH(A0), ORP(A1), Temp(A2), Hum(A3), CO2(A4), DO(A5)': 'Channels: pH(A0), ORP(A1), Temp(A2), CO2(A4), DO(A5); A3/HUM removed (J7 DNP all tiers)',
        },
        'text': {
            r'ANALOG ACQUISITION — 6 channels with on-board galvanic isolation\nEach wet sensor (pH, ORP, DO) has dedicated SN6501+ADuM1250 isolation barrier\nAll channels: Connector → TVS ESD → RC filter → Op-amp buffer → ADC\nPull-downs 10M prevent floating reads when sensor disconnected':
            r'ANALOG ACQUISITION — 5 active channels with on-board galvanic isolation\nWet sensors (pH, ORP, DO) use dedicated SN6501 isolation barrier\nChannels: pH(A0), ORP(A1), Temp(A2), CO2(A4), DO(A5); HUM(A3) removed/DNP\nAll channels: Connector → TVS ESD → RC filter → Op-amp buffer → ADC\nPull-downs 10M prevent floating reads when sensor disconnected',
            r'CO2 Channel (A2) — Tier: Insight+\nJST-XH — transductor presión CO₂':
            r'CO2 Channel (A4) — Tier: Insight+\nJST-XH — transductor presión CO₂',
            r'DO Channel (A3) — Tier: Insight+\nBNC hembra — sonda DO':
            r'DO Channel (A5) — Tier: Insight+\nBNC hembra — sonda DO',
            r'TEMP Channel (A4) — Tier: Essential+\nJST-XH — NTC thermistor':
            r'TEMP Channel (A2) — Tier: Essential+\nJST-XH — NTC thermistor',
            r'HUM Channel (A5) — Tier: Signature\nJST-XH — sensor humedad':
            r'HUM Channel (A3) — Tier: removed/DNP all tiers\nJ7 + D8 + R17/R18/C23 not populated',
        }
    },
    'kicad/digital_i2c.kicad_sch': {
        'comments': {
            'Sheet 3 of 5: I2C Bus, HX711 Load Cell, RS485 (DNP), Status LED': 'Sheet 3 of 5: I2C Bus, HX711 Load Cell (Insight+), RS485 (Signature), Status LED',
            'I2C devices: GPS(0x42), RTC(0x68), Cell Density(0x30), EZO optional': 'I2C: GPS(0x42), RTC(0x68), EZO optional; HX711 J15 DNP Essential; RS485 J16 Signature; J10 DNP all tiers',
        },
        'text': {
            r'RS485 MODBUS — DNP option for Hamilton Incyte/Dencytee\nPopulate for Signature tier with Hamilton sensors':
            r'RS485 MODBUS — Signature only\nHamilton TCD + ACD (Incyte/Dencytee) via MAX3485 + SC16IS740 bridge\nDNP in Essential and Insight',
        }
    },
    'kicad/actuator_drivers.kicad_sch': {
        'comments': {},
        'text': {
            r'ACTUATOR DRIVERS — All opto-isolated from MCU\nMotor: IR2104 half-bridge + IRLZ44N MOSFETs (Insight+)\nRelays: PC817 + 2N7002 + HF46F (Insight+/Signature)\nCO2 PWM: RC filter + Op-amp + MOSFET (Insight+)':
            r'ACTUATOR DRIVERS — All opto-isolated from MCU\nMotor/recirculation: IR2104 + IRLZ44N (Insight+)\nGas solenoid (CO2/H2): PC817 + 2N7002 + HF46F (Insight+)\nChiller relay: PC817 + 2N7002 + HF46F (Insight+)\nCO2 PWM proportional valve: DNP all tiers (single gas via solenoid)',
            r'CO2 SOLENOID RELAY — Insight+\nMCU D7 → R16 → PC817 → 2N7002 → Relay K2':
            r'GAS SOLENOID RELAY (CO2/H2) — Insight+\nMCU CO2_SOL_CTL → R26 → U18 → Q3 → Relay K1 → J18',
            r'CHILLER RELAY — Signature only\nMCU D6 → R15 → PC817 → 2N7002 → Relay K1':
            r'CHILLER RELAY — Insight+\nMCU CHILLER_CTL → R27 → U19 → Q4 → Relay K2 → J19',
            r'CO2 PWM FLOW REGULATOR — Insight+\nMCU D9 PWM → RC filter (10k/100nF) → MCP6002 Gain 3.6x → IRLZ44N → Valve':
            r'GAS PWM FLOW REGULATOR — DNP all tiers\nSingle gas output uses solenoid K1/J18; U20/Q5/D14/R28/C27/J22 not populated',
        }
    },
    'kicad/nebula_qshield.kicad_sch': {
        'comments': {},
        'text': {
            r'NEBULA Q-SHIELD® — Hierarchical Root Schematic\n\nIndustrial fermentation monitor shield for Arduino UNO Q (4GB)\n12 sensors, 3 actuators, 3 tiers (Essential/Insight/Signature)\nSingle PCB with DNP component selection per tier\n\nDesign decisions:\n- Galvanic isolation: ON-BOARD (Option A) for all wet sensors\n- Display: HMI UART (Nextion/Stone) — NOT HDMI\n- Watchdog: TPS3823 populated ALL tiers\n- RS485: DNP option for Hamilton Incyte/Dencytee\n- Connectors: All polarized/keyed, plug-and-play':
            r'NEBULA Q-SHIELD® — Hierarchical Root Schematic\n\nIndustrial fermentation monitor shield for Arduino UNO Q\nTiers (Essential/Insight/Signature) via DNP component selection\n\nTier mapping:\n- Essential: GPS, RTC/timestamp, temp, pH, ORP\n- Insight: Essential + load cells, DO, CO2 pressure, chiller, recirculation, gas solenoid\n- Signature: Insight + Hamilton TCD + ACD via RS485\n\nDesign decisions:\n- Galvanic isolation: ON-BOARD for all wet sensors\n- Display: HMI UART (Nextion/Stone)\n- Watchdog: TPS3823 populated all tiers\n- I2C pull-ups on D20/D21; A4/A5 reserved for CO2_ADC/DO_ADC\n- Humidity channel removed; J7 and passives DNP all tiers\n- Single gas output: solenoid J18; PWM regulator J22/U20 DNP\n- Connectors: All polarized/keyed, plug-and-play',
        }
    },
}

def process(path):
    text = path.read_text()
    spec = REPLACEMENTS.get(str(path))
    if not spec:
        return False
    changed = False
    for old, new in spec['comments'].items():
        if old in text:
            text = text.replace(old, new)
            changed = True
    for old, new in spec['text'].items():
        if old in text:
            text = text.replace(old, new)
            changed = True
    if changed:
        path.write_text(text)
        return True
    return False

if __name__ == '__main__':
    for p in REPLACEMENTS:
        path = Path(p)
        if process(path):
            print(f'Updated {path}')
    print('Done')
