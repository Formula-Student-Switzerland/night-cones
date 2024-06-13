import time
import pyvisa
from SwitchUnit import SwitchUnit
from SwitchUnitCard import SwitchUnitCard
from PowerSupply import PowerSupply
from Oscilloscope import Oscilloscope
from Multimeter import Multimeter
from Generator import Generator
from Report import Report
#from tkinter import *
#from tkinter import ttk

SIMULATION = False

# Test parameters
BAT_VOLT_FULL = 4.2
BAT_VOLT_CHG = 3.7
BAT_VOLT_EMPTY = 2.5
BAT_AMP_CHG = 1.5
BAT_LOAD_R = 2.5
CHG_VOLT = 6
CHG_AMP = 1
MAGNET_VOLT = 2
MAGNET_AMP = 1

# Voltage measurement channel configuration
CH_VOLT_3V3        = "00"
CH_VOLT_TEMP       = "01"
CH_VOLT_FS_ACT     = "02"
CH_VOLT_HALL       = "03"
CH_VOLT_5V_CHG     = "04"
CH_VOLT_VBAT_MOB   = "05"
CH_VOLT_5V2        = "06"
CH_VOLT_VBAT       = "07"

# VBAT, load and current measurement channel configuration
CH_VBAT_VBAT_POS   = "C2"
CH_VBAT_VBAT_NEG   = "C3"
CH_VBAT_SUP_POS    = "R0"
CH_VBAT_SUP_NEG    = "R1"
CH_VBAT_AMP_POS    = "C0"
CH_VBAT_AMP_NEG    = "R3"
CH_VBAT_LOAD_POS   = "C1"
CH_VBAT_LOAD_NEG   = "R2"

# Charge and magnet channel configuration
CH_CHG_CHG_POS     = "R0"
CH_CHG_CHG_NEG     = "R1"
CH_CHG_CHG_A       = "C1"
CH_CHG_CHG_B       = "C2"
CH_CHG_CHG_C       = "C3"
CH_CHG_MAG_POS     = "R2"
CH_CHG_MAG_NEG     = "R3"
CH_CHG_ROUTING     = "C0"

# Signal channel configuration
CH_SIG_M_DATA_FS   = "R0"
CH_SIG_M_FS_PULSE  = "R1"
CH_SIG_M_FS_DATA   = "R2"
CH_SIG_S_KILL      = "C0"
CH_SIG_S_DATA_FS   = "C1"
CH_SIG_S_DATA      = "C2"
CH_SIG_GENERATOR   = "R3"
CH_SIG_MEASUREMENT = "C3"

# Short circuit channel configuration
CH_SHORT_DATA_FS   = "00"
CH_SHORT_DATA      = "01"
CH_SHORT_GPIO0     = "02"
CH_SHORT_RST       = "03"
CH_SHORT_HALL      = "04"

# Power supply channels
PS_CH_BAT = 1
PS_CH_CHG = 2

def chg_on(equipment, volt = CHG_VOLT, amp = CHG_AMP, pos="A", neg="B"):
    if pos == "A":
        ch_pos = CH_CHG_CHG_A
    elif pos == "B":
        ch_pos = CH_CHG_CHG_B
    elif pos == "C":
        ch_pos = CH_CHG_CHG_C
    else:
        ch_pos = pos
    if neg == "A":
        ch_neg = CH_CHG_CHG_A
    elif neg == "B":
        ch_neg = CH_CHG_CHG_B
    elif neg == "C":
        ch_neg = CH_CHG_CHG_C
    else:
        ch_neg = neg
    #print(equipment["sw_cards"]["card_chg"].card_slot)
    equipment["switch"].open_card(equipment["sw_cards"]["card_chg"])
    equipment["switch"].close(equipment["sw_cards"]["card_chg"].ch([CH_CHG_CHG_POS, ch_pos, CH_CHG_CHG_NEG, ch_neg]))
    equipment["ps"].set_volt(volt = volt, channel = PS_CH_CHG)
    equipment["ps"].set_amp(amp = amp, channel = PS_CH_CHG)
    equipment["ps"].on(channel = PS_CH_CHG)

def chg_off(equipment):
    equipment["ps"].set_volt(volt = 0, channel = PS_CH_CHG)
    equipment["ps"].set_amp(amp = 0, channel = PS_CH_CHG)
    equipment["ps"].off(channel = PS_CH_CHG)
    equipment["switch"].open_card(equipment["sw_cards"]["card_chg"])

def magnet_turn_on(equipment):
    magnet_disable(equipment)
    equipment["switch"].close(equipment["sw_cards"]["card_chg"].ch([CH_CHG_CHG_POS, CH_CHG_CHG_A, CH_CHG_CHG_A, CH_CHG_MAG_POS]))
    equipment["switch"].close(equipment["sw_cards"]["card_chg"].ch([CH_CHG_CHG_NEG, CH_CHG_ROUTING, CH_CHG_ROUTING, CH_CHG_MAG_NEG]))
    equipment["ps"].on(channel = PS_CH_CHG)
    equipment["ps"].set_volt(volt = MAGNET_VOLT, channel = PS_CH_CHG)
    equipment["ps"].set_amp(amp = MAGNET_AMP, channel = PS_CH_CHG)

def magnet_turn_off(equipment):
    magnet_disable(equipment)
    equipment["switch"].close(equipment["sw_cards"]["card_chg"].ch([CH_CHG_CHG_POS, CH_CHG_CHG_A, CH_CHG_CHG_A, CH_CHG_MAG_NEG]))
    equipment["switch"].close(equipment["sw_cards"]["card_chg"].ch([CH_CHG_CHG_NEG, CH_CHG_ROUTING, CH_CHG_ROUTING, CH_CHG_MAG_POS]))
    equipment["ps"].on(channel = PS_CH_CHG)
    equipment["ps"].set_volt(volt = MAGNET_VOLT, channel = PS_CH_CHG)
    equipment["ps"].set_amp(amp = MAGNET_AMP, channel = PS_CH_CHG)

def magnet_disable(equipment):
    equipment["ps"].set_volt(volt = 0, channel = PS_CH_CHG)
    equipment["ps"].set_amp(amp = 0, channel = PS_CH_CHG)
    equipment["ps"].off(channel = PS_CH_CHG)
    equipment["switch"].open_card(equipment["sw_cards"]["card_chg"])

#def bat_supply(equipment, volt, amp):
#
#def bat_sim(equipment, volt, amp):
#
#def bat_ampmeter_enable(equipment, microamp = False):
#
#def bat_ampmeter_disable(equipment):
#
#def bat_off(equipment):

def main():
    #root = Tk()
    #frm = ttk.Frame(root, padding=10)
    #frm.grid()
    #ttk.Label(frm, text="Hello World!").grid(column=0, row=0)
    #ttk.Button(frm, text="Quit", command=root.destroy).grid(column=1, row=0)
    #root.mainloop()

    # Switch Unit Card configuration
    card_volt  = SwitchUnitCard(5, "RELAY MUX 44470")
    card_vbat  = SwitchUnitCard(1, "MATRIX SW 44473")
    card_chg   = SwitchUnitCard(2, "MATRIX SW 44473")
    card_sig   = SwitchUnitCard(3, "MATRIX SW 44473")
    card_short = SwitchUnitCard(4, "GP RELAY 44471")
    sw_cards = {"card_volt": card_volt, "card_vbat": card_vbat, "card_chg": card_chg, "card_sig": card_sig, "card_short": card_short}

    rm = pyvisa.ResourceManager()
    if not SIMULATION:
        rm.list_resources()

    # Switch Unit demonstration
    if not SIMULATION:
        switch = SwitchUnit(rm, "GPIB0", 22, sw_cards, "NC1-1B TEST")
        #switch.close(card_vbat.ch([CH_VBAT_VBAT_POS, CH_VBAT_SUP_POS, CH_VBAT_VBAT_NEG, CH_VBAT_AMP_NEG, CH_VBAT_AMP_POS, CH_VBAT_SUP_NEG]))
        #time.sleep(0.1)
        #switch.close(card_volt.ch(CH_VOLT_FS_ACT))
        #time.sleep(0.1)
        #switch.close(card_short.ch(CH_SHORT_HALL))
        #time.sleep(0.1)
        #switch.close(card_sig.ch([CH_SIG_M_DATA_FS, CH_SIG_MEASUREMENT, CH_SIG_S_KILL, CH_SIG_GENERATOR]))
        #time.sleep(0.1)
        #switch.close(card_chg.ch([CH_CHG_CHG_POS, CH_CHG_CHG_A, CH_CHG_CHG_NEG, CH_CHG_CHG_B]))
        #time.sleep(0.1)
        #switch.open_all()

    # Power supply demonstration
    if not SIMULATION:
        ps = PowerSupply(rm, "GPIB0", 16)
        ps.reset()
        #time.sleep(0.1)
        #ps.set_ovp(5, PS_CH_BAT)
        #time.sleep(0.1)
        #ps.set_ovp(7, PS_CH_CHG)
        #time.sleep(0.1)
        #ps.set_volt(4.2, PS_CH_BAT)
        #time.sleep(1)
        #ps.set_amp(3, PS_CH_BAT)
        #time.sleep(1)
        #ps.set_volt(6, PS_CH_CHG)
        #time.sleep(1)
        #ps.set_amp(1, PS_CH_CHG)
        #time.sleep(1)
        #ps.on(PS_CH_BAT)
        #time.sleep(1)
        #ps.on(PS_CH_CHG)
        #time.sleep(1)
        #ps.off(PS_CH_CHG)
        #time.sleep(1)
        #ps.set_amp(3, PS_CH_BAT)
        #time.sleep(1)
        #ps.set_volt(4.2, PS_CH_BAT)
        #ps.reset()

    # Oscilloscope
    if not SIMULATION:
        osc = Oscilloscope(rm, "USB0", "0x0957::0x0588", "CN50524177")
        osc.setup_nightcone()
        #print(osc.meas_amp(1))
        #print(f"Positive width: {osc.meas_pwidth(1, 100)}")
        #print(f"Negative width: {osc.meas_nwidth(1, 100)}")

    #Multimeter
    if not SIMULATION:
        dmm = Multimeter(rm, "GPIB0", 20, "NC1-1B TEST", False)
        #print(f"DC Voltage: {dmm.meas_volt_dc(1)}")
        #print(f"DC Voltage: {dmm.meas_volt_dc(10)}")
        #print(f"Number of measurements: {len(dmm.meas_volt_dc(1024))}")

    #Signal Generator
    ch_sig = 1
    leds = 20
    colors = 3
    bit_per_led = 8
    Gen_Disp_Msg = "Formula Student Switzerland\n\nNC1-1B TEST"
    Gen_Disp_Msg_Selftest = "FSCH\n\nNC1-1B TEST\n\nSelftest in progress..."
    if not SIMULATION:
        gen = Generator(rm, Interface = "GPIB0", GPIB_Addr = 10, DispMsg = Gen_Disp_Msg_Selftest, load = ["INF", "INF"], run_selftest = False)
        #gen.disp_text(Gen_Disp_Msg)
        gen.pulse_setup(low=0, high=3.3, per=1390e-9, width=300e-9, ch = ch_sig)
        gen.burst_setup(mode = "TRIG", per = 1e-3, cycles = leds*colors*bit_per_led, ch = ch_sig)
        gen.output_on(ch = ch_sig)
        #gen.beep()
        #time.sleep(2)
        #gen.pulse_period(per = 1410e-9, ch = ch_sig)
        #gen.pulse_width(width = 1090e-9, ch = ch_sig)
        #gen.beep()
        #time.sleep(2)
        #gen.pulse_period(per = 1390e-9, ch = ch_sig)
        #gen.pulse_width(width = 300e-9, ch = ch_sig)
        #gen.beep()
        #time.sleep(2)
        #gen.output_off(ch_sig)
        #gen.beep()

    #equipment = [switch, sw_cards, ps, dmm, osc, gen]
    equipment = {"switch": switch, "sw_cards": sw_cards, "ps": ps, "dmm": dmm, "osc": osc, "gen": gen, "card_volt":  card_volt, "card_vbat":  card_vbat, "card_chg":   card_chg, "card_sig":   card_sig, "card_short": card_short}

    rep_name = f"NC1-1B 2024-06-06"
    rep = Report(rep_name)
    report_path = "nc1-1/report"
    dut_name = "NC1-1"
    dut_ver = "BA"
    dut_serial = "123456"
    meas_value = 1
    dut_serial_start = 1
    dut_serial_stop = 10
    print(f"Confirm Starting Serial Number: {str(dut_serial_start).zfill(6)}")
    ser_input = input()
    if ser_input != "":
        dut_serial_start = int(ser_input)
    print(f"Confirm Stopping Serial Number: {str(dut_serial_stop).zfill(6)}")
    ser_input = input()
    if ser_input != "":
        dut_serial_stop = int(ser_input)
    for dut_serial in range(dut_serial_start, dut_serial_stop+1):
        dut_serial = str(dut_serial).zfill(6)
        rep.add_dut(name = dut_name, version = dut_ver, serial = dut_serial)

        if SIMULATION:
            meas_name = "Meas 1"
            rep.add_meas(value = meas_value, name = meas_name)
            meas_value += 1
            meas_name = "Meas 2"
            rep.add_meas(value = meas_value, name = meas_name, min = 2)
            meas_value += 1
            meas_name = "Meas 3"
            rep.add_meas(value = meas_value, name = meas_name, min = 4)
            meas_value += 1
            meas_name = "Meas 4"
            rep.add_meas(value = meas_value, name = meas_name, max = 0)
            meas_value += 1
            meas_name = "Meas 5"
            rep.add_meas(value = meas_value, name = meas_name, max = 5)
            meas_value += 1
            meas_name = "Meas 6"
            rep.add_meas(value = meas_value, name = meas_name, min = 2, max = 5.9)
            meas_value += 1
            meas_name = "Meas 7"
            rep.add_meas(value = meas_value, name = meas_name, min = 7, max = 7)
            meas_value += 1
            meas_name = "Meas 8"
            rep.add_meas(value = meas_value, name = meas_name, min = 8.01, max = 10)
            meas_value += 1
            meas_name = "Meas 9"
            rep.add_meas(value = meas_value, name = meas_name, min = 8, max = 10)
            meas_value += 1
            meas_name = "Meas 10"
            rep.add_meas(value = meas_value, name = meas_name, min = 9, max = 10)
            meas_value += 1
            #time.sleep(2)

        if not SIMULATION:
            # Test pcb for short-circuits
            switch.close(card_volt.ch([CH_VOLT_5V2]))
            rep.add_meas(value = dmm.meas_res(), name = f"SHORT: Resistance +5V2", min = 10e3, max = 1e6)
            #switch.open(card_volt.ch([CH_VOLT_5V2]))
            switch.open_card(card_volt)
            switch.close(card_volt.ch([CH_VOLT_3V3]))
            rep.add_meas(value = dmm.meas_res(), name = f"SHORT: Resistance +3V3", min = 10e3, max = 1e6)
            #switch.open(card_volt.ch([CH_VOLT_3V3]))
            switch.open_card(card_volt)
            switch.close(card_volt.ch([CH_VOLT_VBAT]))
            rep.add_meas(value = dmm.meas_res(), name = f"SHORT: Resistance VBAT", min = 10e3, max = 1e6)
            #switch.open(card_volt.ch([CH_VOLT_VBAT]))
            switch.open_card(card_volt)
            switch.close(card_chg.ch([CH_CHG_CHG_NEG, CH_CHG_CHG_A, CH_CHG_CHG_NEG, CH_CHG_CHG_B, CH_CHG_CHG_NEG, CH_CHG_CHG_C]))
            switch.close(card_volt.ch([CH_VOLT_5V_CHG]))
            rep.add_meas(value = dmm.meas_res(), name = f"SHORT: Resistance +5V_CHG", min = 10e3, max = 1e6)
            #switch.open(card_chg.ch([CH_CHG_CHG_NEG, CH_CHG_CHG_A, CH_CHG_CHG_NEG, CH_CHG_CHG_B, CH_CHG_CHG_NEG, CH_CHG_CHG_C]))
            #switch.open(card_volt.ch([CH_VOLT_5V_CHG]))
            switch.open_card(card_chg)
            switch.open_card(card_volt)

            # Test charger
            switch.close(card_chg.ch([CH_VBAT_VBAT_NEG, CH_VBAT_SUP_NEG, CH_VBAT_VBAT_POS, CH_VBAT_AMP_NEG, CH_VBAT_AMP_POS, CH_VBAT_SUP_POS, CH_VBAT_LOAD_POS, CH_VBAT_SUP_POS, CH_VBAT_LOAD_NEG, CH_VBAT_VBAT_NEG]))
            ps.set_volt(volt = BAT_VOLT_CHG, channel = PS_CH_BAT)
            ps.set_amp(amp = BAT_AMP_CHG, channel = PS_CH_BAT)
            ps.on(channel = PS_CH_BAT)
            chg_on(equipment = equipment, volt = CHG_VOLT, amp = CHG_AMP, pos = "A", neg = "B")
            rep.add_meas(value = dmm.meas_amp_dc(), name = f"CHARGE: Charging current A => B", min = 0.55, max = 0.65)
            chg_off(equipment = equipment)
            chg_on(equipment = equipment, volt = CHG_VOLT, amp = CHG_AMP, pos = "B", neg = "C")
            rep.add_meas(value = dmm.meas_amp_dc(), name = f"CHARGE: Charging current B => C", min = 0.55, max = 0.65)
            chg_off(equipment = equipment)
            chg_on(equipment = equipment, volt = CHG_VOLT, amp = CHG_AMP, pos = "C", neg = "A")
            rep.add_meas(value = dmm.meas_amp_dc(), name = f"CHARGE: Charging current C => A", min = 0.55, max = 0.65)
            chg_off(equipment = equipment)

            # BMS

            # Test Hall sensor (on and off and HALL/)

            # Test On/Off controller (Kill, charge and hall)

            # Test supply 5.2V

            # Test supply 3.3V

            # Test voltage monitor

            # Test temperature measurement

            # Test Failsafe (Oscillator, Missing Pulse detection, combined signal, switch-over

            # Programming

            switch.open_all()

        print(f"Testing of {dut_name}{dut_ver}-{dut_serial} completed")

        rep.print_dut(filename = f"{dut_name}{dut_ver}-{dut_serial}.txt", path = report_path, print_passfail = True, print_minmax = True)
    rep.print_report(filename = f"NC1-1BA {rep.datetime.strftime('%Y-%m-%d %H-%M-%S')}.csv", path = report_path, print_passfail = True, print_minmax = True)


if __name__ == "__main__":
    main()
