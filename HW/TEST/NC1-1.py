import time
import pyvisa
from SwitchUnit import SwitchUnit
from SwitchUnitCard import SwitchUnitCard
from PowerSupply import PowerSupply
from Oscilloscope import Oscilloscope
from Multimeter import Multimeter
from Generator import Generator
#from tkinter import *
#from tkinter import ttk

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
    sw_cards = [card_volt, card_vbat, card_chg, card_sig, card_short]

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

    rm = pyvisa.ResourceManager()
    rm.list_resources()

    ## Switch Unit demonstration
    #switch = SwitchUnit(rm, "GPIB0", 20, sw_cards, "NC1-1B TEST")
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

    ## Power supply demonstration
    #PS_CH_BAT = 1
    #PS_CH_CHG = 2
    #ps = PowerSupply(rm, "GPIB0", 16)
    #ps.reset()
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

    ## Oscilloscope
    #osc = Oscilloscope(rm, "USB0", "0x0957::0x0588", "CN50524177")
    #osc.setup_nightcone()
    #print(osc.meas_amp(1))
    #print(f"Positive width: {osc.meas_pwidth(1, 100)}")
    #print(f"Negative width: {osc.meas_nwidth(1, 100)}")

    ##Multimeter
    #dmm = Multimeter(rm, "GPIB0", 20, "NC1-1B TEST", False)
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
    gen = Generator(rm, Interface = "GPIB0", GPIB_Addr = 10, DispMsg = Gen_Disp_Msg_Selftest, load = ["INF", "INF"], run_selftest = True)
    #gen.disp_text(Gen_Disp_Msg)
    gen.pulse_setup(low=0, high=3.3, per=1390e-9, width=300e-9, ch = ch_sig)
    gen.burst_setup(mode = "TRIG", per = 1e-3, cycles = leds*colors*bit_per_led, ch = ch_sig)
    gen.output_on(ch = ch_sig)
    gen.beep()
    time.sleep(2)
    gen.pulse_period(per = 1410e-9, ch = ch_sig)
    gen.pulse_width(width = 1090e-9, ch = ch_sig)
    gen.beep()
    time.sleep(2)
    gen.pulse_period(per = 1390e-9, ch = ch_sig)
    gen.pulse_width(width = 300e-9, ch = ch_sig)
    gen.beep()
    time.sleep(2)
    gen.output_off(ch_sig)
    gen.beep()

if __name__ == "__main__":
    main()
