import time
import pyvisa
from SwitchUnit import SwitchUnit
from SwitchUnitCard import SwitchUnitCard
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

    # Switch Unit demonstration
    switch = SwitchUnit(rm, "GPIB0", 20, sw_cards, "NC1-1B TEST")
    switch.close(card_vbat.ch([CH_VBAT_VBAT_POS, CH_VBAT_SUP_POS, CH_VBAT_VBAT_NEG, CH_VBAT_AMP_NEG, CH_VBAT_AMP_POS, CH_VBAT_SUP_NEG]))
    time.sleep(0.1)
    switch.close(card_volt.ch(CH_VOLT_FS_ACT))
    time.sleep(0.1)
    switch.close(card_short.ch(CH_SHORT_HALL))
    time.sleep(0.1)
    switch.close(card_sig.ch([CH_SIG_M_DATA_FS, CH_SIG_MEASUREMENT, CH_SIG_S_KILL, CH_SIG_GENERATOR]))
    time.sleep(0.1)
    switch.close(card_chg.ch([CH_CHG_CHG_POS, CH_CHG_CHG_A, CH_CHG_CHG_NEG, CH_CHG_CHG_B]))
    time.sleep(0.1)
    switch.open_all()

    ##switch_unit = rm.open_resource('GPIB::20::INSTR')
    #print(switch_unit.query("TEST"))
    #print(switch_unit.query("CTYPE 1"))
    #print(switch_unit.query("CTYPE 2"))
    #print(switch_unit.query("CTYPE 3"))
    #print(switch_unit.query("CTYPE 4"))
    #print(switch_unit.query("CTYPE 5"))
    #switch_unit.query("DISP NC1-1 TEST")

    #switch_unit.query("CLOSE 100, 101, 102, 103")
    #time.sleep(0.1)
    #switch_unit.query("OPEN 100, 101, 102, 103")
    #time.sleep(1)
    #switch_unit.query("CLOSE 100, 101, 102, 103, 110, 111, 112, 113, 120, 121, 122, 123, 130, 131, 132, 133")
    #time.sleep(0.1)
    #switch_unit.query("OPEN 100, 101, 102, 103, 110, 111, 112, 113, 120, 121, 122, 123, 130, 131, 132, 133")
    #time.sleep(1)

def sw_close_all():
    switch_unit.query("CLOSE 100, 101, 102, 103, 110, 111, 112, 113, 120, 121, 122, 123, 130, 131, 132, 133, 200, 201, 202, 203, 210, 211, 212, 213, 220, 221, 222, 223, 230, 231, 232, 233, 300, 301, 302, 303, 310, 311, 312, 313, 320, 321, 322, 323, 330, 331, 332, 333, 400, 401, 402, 403, 410, 411, 412, 413, 420, 421, 422, 423, 430, 431, 432, 433")

def sw_open_all():
    switch_unit.query("OPEN 100, 101, 102, 103, 110, 111, 112, 113, 120, 121, 122, 123, 130, 131, 132, 133, 200, 201, 202, 203, 210, 211, 212, 213, 220, 221, 222, 223, 230, 231, 232, 233, 300, 301, 302, 303, 310, 311, 312, 313, 320, 321, 322, 323, 330, 331, 332, 333, 400, 401, 402, 403, 410, 411, 412, 413, 420, 421, 422, 423, 430, 431, 432, 433")

def sw_reset():
    switch_unit.query("CRESET 1, 2, 3, 4, 5")

if __name__ == "__main__":
    main()
