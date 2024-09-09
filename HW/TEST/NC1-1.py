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

###########################
# Test procedure switches #
###########################

SIMULATION  = False
DEBUG       = False
DEBUG_HALT  = 1 # 0: ignore all halts, 1: only halt when parameter "halt" is True, 2: halt on every debug() statement
DEBUG_DELAY = 0
MEAS_STAT   = True

TEST_ALL        = False
TEST_SHORT      = True
TEST_CHARGER    = True
TEST_BMS        = True
TEST_HALL       = True
TEST_ONOFF      = True
TEST_5V2        = True
TEST_3V3        = True
TEST_VMON       = True
TEST_TEMP       = True
TEST_FAILSAFE   = True
TEST_OFF_CURR   = True
TEST_PROG       = False  
TEST_KEEP_ON    = False

###################
# Test parameters #
###################

DUT_SERIAL_START = 1
SER_LEN = 6
BAT_VOLT_FULL = 4.2
BAT_VOLT_CHG = 3.7
BAT_VOLT_EMPTY = 2.5
BAT_AMP_CHG = 1.5
BAT_AMP_RUN = 3.0
BAT_LOAD_R = 2.67
BAT_LOAD_AMP_HEADROOM = 0.2
BAT_AMP_THRES_BRIGHT = 1.0
CHG_VOLT = 6
CHG_AMP = 1
MAGNET_VOLT = 2
MAGNET_AMP = 1
bat_status = "OFF"
bat_ampmeter = False
KILL_FREQ = 10e3
KILL_DUTY = 0.5
KILL_COUNT = 10
HALL_DELAY = 0.20
CHG_DELAY = 0.01
VBATMON_R1 = 100e3
VBATMON_R2 = 22e3
LED_OFF_PER = 1390e-9
LED_OFF_WIDTH = 300e-9
LED_ON_PER = 1410e-9
LED_ON_WIDTH = 1090e-9
LED_LOW = 0
LED_HIGH = 3.3
LED_COUNT = 20
LED_COLORS = 3
LED_BIT_PER_COLOR = 8

##################################################
# Measurement equipment connection configuration #
##################################################

# Voltage measurement channel configuration
CH_VOLT_3V3        = "00"
CH_VOLT_TEMP       = "01"
CH_VOLT_HALL       = "02"
CH_VOLT_FS_ACT     = "03"
CH_VOLT_5V_CHG     = "04"
CH_VOLT_VBAT_MON   = "05"
CH_VOLT_5V2        = "06"
CH_VOLT_VBAT       = "07"
CH_VOLT_SHORT      = "08"

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

# Signal Genreator channels
GEN_CH_SIG = 1

######################################
# Measurement equipment connectivity #
######################################

# Switch Unit
SW_INTERFACE = "GPIB0"
SW_ADDR = 22

#Power Supply
PS_INTERFACE = "GPIB0"
PS_ADDR = 3

# Oscilloscope
OSC_INTERFACE = "USB0"
OSC_ADDR = "0x0957::0x0588"
OSC_SERIAL = "CN50524177"

# Multimeter
DMM_INTERFACE = "GPIB0"
DMM_ADDR = 20

# Signal Generator
GEN_INTERFACE = "GPIB0"
GEN_ADDR = 10

def debug(msg = "", halt = False):
    if DEBUG:
        print(f"DEBUG: {msg}")
        if DEBUG_HALT >= 2 or (DEBUG_HALT >= 1 and halt):
            print(f"DEBUG: Halted...")
            input()
        else:
            time.sleep(DEBUG_DELAY)


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
    equipment["switch"].open_card(equipment["sw_cards"]["card_chg"])
    equipment["switch"].close(equipment["sw_cards"]["card_chg"].ch([CH_CHG_CHG_POS, ch_pos, CH_CHG_CHG_NEG, ch_neg]))
    equipment["ps"].set_volt(volt = volt, channel = PS_CH_CHG)
    equipment["ps"].set_amp(amp = amp, channel = PS_CH_CHG)
    equipment["ps"].on(channel = PS_CH_CHG)
    debug(f"Charging: {pos}, => {neg}")

def chg_short(equipment):
    equipment["switch"].close(equipment["sw_cards"]["card_chg"].ch([CH_CHG_CHG_NEG, CH_CHG_CHG_A, CH_CHG_CHG_NEG, CH_CHG_CHG_B, CH_CHG_CHG_NEG, CH_CHG_CHG_C]))
    debug(f"Charging: Short")

def chg_off(equipment):
    equipment["ps"].set_volt(volt = 0, channel = PS_CH_CHG)
    equipment["ps"].set_amp(amp = 0, channel = PS_CH_CHG)
    equipment["ps"].off(channel = PS_CH_CHG)
    equipment["switch"].open_card(equipment["sw_cards"]["card_chg"])
    debug(f"Charging: Off")

def magnet_turn_on(equipment):
    magnet_disable(equipment)
    equipment["switch"].close(equipment["sw_cards"]["card_chg"].ch([CH_CHG_CHG_POS, CH_CHG_CHG_A, CH_CHG_CHG_A, CH_CHG_MAG_POS]))
    equipment["switch"].close(equipment["sw_cards"]["card_chg"].ch([CH_CHG_CHG_NEG, CH_CHG_ROUTING, CH_CHG_ROUTING, CH_CHG_MAG_NEG]))
    equipment["ps"].on(channel = PS_CH_CHG)
    equipment["ps"].set_volt(volt = MAGNET_VOLT, channel = PS_CH_CHG)
    equipment["ps"].set_amp(amp = MAGNET_AMP, channel = PS_CH_CHG)
    debug(f"Magnet: On")

def magnet_turn_off(equipment):
    magnet_disable(equipment)
    equipment["switch"].close(equipment["sw_cards"]["card_chg"].ch([CH_CHG_CHG_POS, CH_CHG_CHG_A, CH_CHG_CHG_A, CH_CHG_MAG_NEG]))
    equipment["switch"].close(equipment["sw_cards"]["card_chg"].ch([CH_CHG_CHG_NEG, CH_CHG_ROUTING, CH_CHG_ROUTING, CH_CHG_MAG_POS]))
    equipment["ps"].on(channel = PS_CH_CHG)
    equipment["ps"].set_volt(volt = MAGNET_VOLT, channel = PS_CH_CHG)
    equipment["ps"].set_amp(amp = 2*MAGNET_AMP, channel = PS_CH_CHG)
    debug(f"Magnet: Off")

def magnet_disable(equipment):
    equipment["ps"].set_volt(volt = 0, channel = PS_CH_CHG)
    equipment["ps"].set_amp(amp = 0, channel = PS_CH_CHG)
    equipment["ps"].off(channel = PS_CH_CHG)
    equipment["switch"].open_card(equipment["sw_cards"]["card_chg"])
    debug(f"Magnet: Disabled")

def bat_supply(equipment, volt, amp, ampmeter = False):
    global bat_status
    global bat_ampmeter
    if bat_status == "OFF":
        if ampmeter:
            equipment["switch"].close(equipment["sw_cards"]["card_vbat"].ch([CH_VBAT_VBAT_NEG, CH_VBAT_SUP_NEG, CH_VBAT_VBAT_POS, CH_VBAT_AMP_NEG, CH_VBAT_AMP_POS, CH_VBAT_SUP_POS]))
            bat_ampmeter = True
        else:
            equipment["switch"].close(equipment["sw_cards"]["card_vbat"].ch([CH_VBAT_VBAT_NEG, CH_VBAT_SUP_NEG, CH_VBAT_VBAT_POS, CH_VBAT_SUP_POS]))
            bat_ampmeter = False
        equipment["ps"].set_volt(volt = volt, channel = PS_CH_BAT)
        equipment["ps"].set_amp(amp = amp, channel = PS_CH_BAT)
        equipment["ps"].on(channel = PS_CH_BAT)
    elif bat_status == "SUP":
        if ampmeter:
            bat_ampmeter_enable(equipment)
        else:
            bat_ampmeter_disable(equipment)
        equipment["ps"].set_volt(volt = volt, channel = PS_CH_BAT)
        equipment["ps"].set_amp(amp = amp, channel = PS_CH_BAT)
    elif bat_status == "SIM":
        if ampmeter:
            bat_ampmeter_enable(equipment)
        else:
            bat_ampmeter_disable(equipment)
        equipment["switch"].open(equipment["sw_cards"]["card_vbat"].ch([CH_VBAT_LOAD_POS, CH_VBAT_SUP_POS, CH_VBAT_LOAD_NEG, CH_VBAT_VBAT_NEG]))
        equipment["ps"].set_volt(volt = volt, channel = PS_CH_BAT)
        equipment["ps"].set_amp(amp = amp + volt / BAT_LOAD_R, channel = PS_CH_BAT)
    else:
        bat_off(equipment)
        raise NameError(f"Unrecognized battery state: {bat_status}")
    bat_status = "SUP"
    bat_ampmeter = ampmeter
    debug(f"Battery: Supply {volt}V, {amp}A, Ampmeter: {bat_ampmeter}")

def bat_sim(equipment, volt, amp, ampmeter = False):
    global bat_status
    global bat_ampmeter
    if bat_status == "OFF":
        if ampmeter:
            equipment["switch"].close(equipment["sw_cards"]["card_vbat"].ch([CH_VBAT_VBAT_NEG, CH_VBAT_SUP_NEG, CH_VBAT_VBAT_POS, CH_VBAT_AMP_NEG, CH_VBAT_AMP_POS, CH_VBAT_SUP_POS, CH_VBAT_LOAD_POS, CH_VBAT_SUP_POS, CH_VBAT_LOAD_NEG, CH_VBAT_VBAT_NEG]))
            bat_ampmeter = True
        else:
            equipment["switch"].close(equipment["sw_cards"]["card_vbat"].ch([CH_VBAT_VBAT_NEG, CH_VBAT_SUP_NEG, CH_VBAT_VBAT_POS, CH_VBAT_SUP_POS, CH_VBAT_LOAD_POS, CH_VBAT_SUP_POS, CH_VBAT_LOAD_NEG, CH_VBAT_VBAT_NEG]))
            bat_ampmeter = False
        equipment["ps"].set_volt(volt = volt, channel = PS_CH_BAT)
        equipment["ps"].set_amp(amp = amp + volt / BAT_LOAD_R + BAT_LOAD_AMP_HEADROOM, channel = PS_CH_BAT)
        equipment["ps"].on(channel = PS_CH_BAT)
    elif bat_status == "SUP":
        if ampmeter:
            bat_ampmeter_enable(equipment)
        else:
            bat_ampmeter_disable(equipment)
        equipment["ps"].set_volt(volt = volt, channel = PS_CH_BAT)
        equipment["ps"].set_amp(amp = amp + volt / BAT_LOAD_R + BAT_LOAD_AMP_HEADROOM, channel = PS_CH_BAT)
        equipment["switch"].close(equipment["sw_cards"]["card_vbat"].ch([CH_VBAT_LOAD_POS, CH_VBAT_SUP_POS, CH_VBAT_LOAD_NEG, CH_VBAT_VBAT_NEG]))
    elif bat_status == "SIM":
        if ampmeter:
            bat_ampmeter_enable(equipment)
        else:
            bat_ampmeter_disable(equipment)
        equipment["ps"].set_volt(volt = volt, channel = PS_CH_BAT)
        equipment["ps"].set_amp(amp = amp + volt / BAT_LOAD_R + BAT_LOAD_AMP_HEADROOM, channel = PS_CH_BAT)
    else:
        bat_off(equipment)
        raise NameError(f"Unrecognized battery state: {bat_status}")
    bat_status = "SIM"
    bat_ampmeter = ampmeter
    debug(f"Battery: Simulation {volt}V, {amp}A, Ampmeter: {bat_ampmeter}")

def bat_ampmeter_enable(equipment, microamp = False):
    global bat_ampmeter
    if not bat_ampmeter:
        meas_volt_off(equipment)
        equipment["switch"].close(equipment["sw_cards"]["card_vbat"].ch([CH_VBAT_VBAT_POS, CH_VBAT_AMP_NEG, CH_VBAT_AMP_POS, CH_VBAT_SUP_POS]))
        equipment["switch"].open(equipment["sw_cards"]["card_vbat"].ch([CH_VBAT_VBAT_POS, CH_VBAT_SUP_POS]))
        bat_ampmeter = True
        debug(f"Battery: Ampmeter enabled")

def bat_ampmeter_disable(equipment):
    global bat_ampmeter
    if bat_ampmeter:
        equipment["switch"].close(equipment["sw_cards"]["card_vbat"].ch([CH_VBAT_VBAT_POS, CH_VBAT_SUP_POS]))
        equipment["switch"].open(equipment["sw_cards"]["card_vbat"].ch([CH_VBAT_VBAT_POS, CH_VBAT_AMP_NEG, CH_VBAT_AMP_POS, CH_VBAT_SUP_POS]))
        bat_ampmeter = False
        debug(f"Battery: Ampmeter disabled")

def bat_off(equipment):
    global bat_status
    global bat_ampmeter
    equipment["ps"].set_volt(volt = 0, channel = PS_CH_BAT)
    equipment["ps"].set_amp(amp = 0, channel = PS_CH_BAT)
    equipment["ps"].off(channel = PS_CH_BAT)
    equipment["switch"].open_card(equipment["sw_cards"]["card_vbat"])
    bat_status = "OFF"
    bat_ampmeter = False
    debug(f"Battery: Off")

def meas_volt_select(equipment, channel):
    bat_ampmeter_disable(equipment)
    equipment["switch"].open_card(equipment["sw_cards"]["card_volt"])
    equipment["switch"].close(equipment["sw_cards"]["card_volt"].ch([channel]))
    if channel == CH_VOLT_3V3:
        ch_str = "3V3"
    elif channel == CH_VOLT_TEMP:
        ch_str = "TEMP"
    elif channel == CH_VOLT_FS_ACT:
        ch_str = "FS_ACT"
    elif channel == CH_VOLT_HALL:
        ch_str = "HALL"
    elif channel == CH_VOLT_5V_CHG:
        ch_str = "5V_CHG"
    elif channel == CH_VOLT_VBAT_MON:
        ch_str = "VBAT_MON"
    elif channel == CH_VOLT_5V2:
        ch_str = "5V2"
    elif channel == CH_VOLT_VBAT:
        ch_str = "VBAT"
    else:
        ch_str = "UNRECOGNIZED CHANNEL"
    debug(f"Voltage Measurement: {ch_str}")

def sig_gen_select(equipment, channel):
    if channel == CH_SIG_S_KILL:
        equipment["switch"].open(equipment["sw_cards"]["card_sig"].ch([CH_SIG_GENERATOR, CH_SIG_S_DATA_FS, CH_SIG_GENERATOR, CH_SIG_S_DATA]))
        equipment["switch"].close(equipment["sw_cards"]["card_sig"].ch([CH_SIG_GENERATOR, CH_SIG_S_KILL]))
        debug(f"Signal Generator: CH_SIG_S_KILL")
    elif channel == CH_SIG_S_DATA_FS:
        equipment["switch"].open(equipment["sw_cards"]["card_sig"].ch([CH_SIG_GENERATOR, CH_SIG_S_KILL, CH_SIG_GENERATOR, CH_SIG_S_DATA]))
        equipment["switch"].close(equipment["sw_cards"]["card_sig"].ch([CH_SIG_GENERATOR, CH_SIG_S_DATA_FS]))
        debug(f"Signal Generator: CH_SIG_S_DATA_FS")
    elif channel == CH_SIG_S_DATA:
        equipment["switch"].open(equipment["sw_cards"]["card_sig"].ch([CH_SIG_GENERATOR, CH_SIG_S_KILL, CH_SIG_GENERATOR, CH_SIG_S_DATA_FS]))
        equipment["switch"].close(equipment["sw_cards"]["card_sig"].ch([CH_SIG_GENERATOR, CH_SIG_S_DATA]))
        debug(f"Signal Generator: CH_SIG_S_DATA")
    else:
        raise NameError(f"Unrecognized Signal generator channel: {channel}")

def sig_meas_select(equipment, channel):
    if channel == CH_SIG_M_DATA_FS:
        equipment["switch"].open(equipment["sw_cards"]["card_sig"].ch([CH_SIG_MEASUREMENT, CH_SIG_M_FS_PULSE, CH_SIG_MEASUREMENT, CH_SIG_M_FS_DATA]))
        equipment["switch"].close(equipment["sw_cards"]["card_sig"].ch([CH_SIG_MEASUREMENT, CH_SIG_M_DATA_FS]))
        debug(f"Signal Generator: CH_SIG_M_DATA_FS")
    elif channel == CH_SIG_M_FS_PULSE:
        equipment["switch"].open(equipment["sw_cards"]["card_sig"].ch([CH_SIG_MEASUREMENT, CH_SIG_M_DATA_FS, CH_SIG_MEASUREMENT, CH_SIG_M_FS_DATA]))
        equipment["switch"].close(equipment["sw_cards"]["card_sig"].ch([CH_SIG_MEASUREMENT, CH_SIG_M_FS_PULSE]))
        debug(f"Signal Generator: CH_SIG_M_FS_PULSE")
    elif channel == CH_SIG_M_FS_DATA:
        equipment["switch"].open(equipment["sw_cards"]["card_sig"].ch([CH_SIG_MEASUREMENT, CH_SIG_M_DATA_FS, CH_SIG_MEASUREMENT, CH_SIG_M_FS_PULSE]))
        equipment["switch"].close(equipment["sw_cards"]["card_sig"].ch([CH_SIG_MEASUREMENT, CH_SIG_M_FS_DATA]))
        debug(f"Signal Generator: CH_SIG_M_FS_DATA")
    else:
        raise NameError(f"Unrecognized Signal generator channel: {channel}")

def meas_volt_short(equipment):
    bat_ampmeter_disable(equipment = equipment)
    bat_off(equipment = equipment)
    chg_off(equipment = equipment)
    equipment["switch"].close(equipment["sw_cards"]["card_volt"].ch([CH_VOLT_3V3, CH_VOLT_TEMP, CH_VOLT_HALL, CH_VOLT_FS_ACT, CH_VOLT_5V_CHG, CH_VOLT_VBAT_MON, CH_VOLT_5V2, CH_VOLT_VBAT, CH_VOLT_SHORT]))
    debug(f"Voltage Measurement: Short")
    time.sleep(0.5)
    equipment["switch"].open_card(equipment["sw_cards"]["card_volt"])

def meas_volt_off(equipment):
    equipment["switch"].open_card(equipment["sw_cards"]["card_volt"])
    debug(f"Voltage measurement: Disabled")

def short(equipment, channel):
    if isinstance(channel, list):
        equipment["switch"].close(equipment["sw_cards"]["card_short"].ch(channel))
    else:
        equipment["switch"].close(equipment["sw_cards"]["card_short"].ch([channel]))
    debug(f"Short: {channel}")

def short_open(equipment, channel):
    if isinstance(channel, list):
        equipment["switch"].open(equipment["sw_cards"]["card_short"].ch(channel))
    else:
        equipment["switch"].open(equipment["sw_cards"]["card_short"].ch([channel]))
    debug(f"Short: {channel}")

def short_clear(equipment):
    equipment["switch"].open_card(equipment["sw_cards"]["card_short"])
    debug(f"Short: Disabled")

def led_off(equipment, keep_gen = False):
    equipment["gen"].pulse_setup(low=LED_LOW, high=LED_HIGH, per=LED_OFF_PER, width=LED_OFF_WIDTH, ch = GEN_CH_SIG)
    equipment["gen"].burst_setup(mode = "TRIG", per = 1e-3, cycles = LED_COUNT*LED_COLORS*LED_BIT_PER_COLOR, ch = GEN_CH_SIG)
    equipment["gen"].output_on(ch = GEN_CH_SIG)
    sig_gen_select(equipment = equipment, channel = CH_SIG_S_DATA)
    short_open(equipment = equipment, channel = CH_SHORT_DATA)
    short_open(equipment = equipment, channel = CH_SHORT_DATA_FS)
    if not keep_gen:
        time.sleep(0.2)
        short(equipment = equipment, channel = CH_SHORT_DATA_FS)
        equipment["gen"].output_off(ch = GEN_CH_SIG)
    debug(f"LED: Off")

def led_on(equipment):
    equipment["gen"].pulse_setup(low=LED_LOW, high=LED_HIGH, per=LED_ON_PER, width=LED_ON_WIDTH, ch = GEN_CH_SIG)
    equipment["gen"].burst_setup(mode = "TRIG", per = 1e-3, cycles = LED_COUNT*LED_COLORS*LED_BIT_PER_COLOR, ch = GEN_CH_SIG)
    equipment["gen"].output_on(ch = GEN_CH_SIG)
    sig_gen_select(equipment = equipment, channel = CH_SIG_S_DATA)
    short_open(equipment = equipment, channel = CH_SHORT_DATA)
    short_open(equipment = equipment, channel = CH_SHORT_DATA_FS)
    debug(f"LED: On")

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
        debug(f"Measurement equipment: {rm.list_resources()}")

    # Switch Unit demonstration
    if not SIMULATION:
        switch = SwitchUnit(rm, SW_INTERFACE, SW_ADDR, sw_cards, "NC1-1B TEST")
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
        ps = PowerSupply(rm, PS_INTERFACE, PS_ADDR, [5, 7])
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
        osc = Oscilloscope(rm, OSC_INTERFACE, OSC_ADDR, OSC_SERIAL)
        osc.setup_nightcone()
        #print(osc.meas_amp(1))
        #print(f"Positive width: {osc.meas_pwidth(1, 100)}")
        #print(f"Negative width: {osc.meas_nwidth(1, 100)}")

    #Multimeter
    if not SIMULATION:
        dmm = Multimeter(rm, DMM_INTERFACE, DMM_ADDR, "NC1-1B TEST", False)
        #print(f"DC Voltage: {dmm.meas_volt_dc(1)}")
        #print(f"DC Voltage: {dmm.meas_volt_dc(10)}")
        #print(f"Number of measurements: {len(dmm.meas_volt_dc(1024))}")

    #Signal Generator
    Gen_Disp_Msg = "Formula Student Switzerland\n\nNC1-1B TEST"
    Gen_Disp_Msg_Selftest = "FSCH\n\nNC1-1B TEST\n\nSelftest in progress..."
    if not SIMULATION:
        gen = Generator(rm, Interface = GEN_INTERFACE, GPIB_Addr = GEN_ADDR, DispMsg = Gen_Disp_Msg_Selftest, load = ["INF", "INF"], run_selftest = False)
        #gen.disp_text(Gen_Disp_Msg)
        gen.pulse_setup(low=LED_LOW, high=LED_HIGH, per=LED_OFF_PER, width=LED_OFF_WIDTH, ch = GEN_CH_SIG)
        gen.burst_setup(mode = "TRIG", per = 1e-3, cycles = LED_COUNT*LED_COLORS*LED_BIT_PER_COLOR, ch = GEN_CH_SIG)
        #gen.output_on(ch = GEN_CH_SIG)
        #gen.beep()
        #time.sleep(2)
        #gen.pulse_period(per = LED_ON_PER, ch = GEN_CH_SIG)
        #gen.pulse_width(width = LED_ON_WIDTH, ch = GEN_CH_SIG)
        #gen.beep()
        #time.sleep(2)
        #gen.pulse_period(per = LED_OFF_PER, ch = GEN_CH_SIG)
        #gen.pulse_width(width = LED_OFF_WIDTH, ch = GEN_CH_SIG)
        #gen.beep()
        #time.sleep(2)
        #gen.output_off(GEN_CH_SIG)
        #gen.beep()

    #equipment = [switch, sw_cards, ps, dmm, osc, gen]
    equipment = {"switch": switch, "sw_cards": sw_cards, "ps": ps, "dmm": dmm, "osc": osc, "gen": gen, "card_volt":  card_volt, "card_vbat":  card_vbat, "card_chg":   card_chg, "card_sig":   card_sig, "card_short": card_short}

    rep_name = f"NC1-1B 2024-06-06"
    rep = Report(rep_name)
    report_path = "nc1-1/report"
    dut_name = "NC1-1"
    dut_ver = "BA"
    #dut_serial = "123456"
    #dut_serial_start = 1
    #dut_serial_stop = 10
    #print(f"Confirm Starting Serial Number: {str(dut_serial_start).zfill(6)}")
    #ser_input = input()
    #if ser_input != "":
    #    dut_serial_start = int(ser_input)
    #print(f"Confirm Stopping Serial Number: {str(dut_serial_stop).zfill(6)}")
    #ser_input = input()
    #if ser_input != "":
    #    dut_serial_stop = int(ser_input)
    #for dut_serial in range(dut_serial_start, dut_serial_stop+1):

    dut_serial = DUT_SERIAL_START-1
    testing_continue = True
    testing_run = True
    testing_pass = True
    print(f"Usage: ")
    print(f"[ ]: Continue with next device when passed, rerun when failed")
    print(f"[R]: Rerun")
    print(f"[C]: Continue with next device")
    print(f"[S]: Stop testing and summarize results")
    print(f"[#ser] continue with specified serial number #ser")
    print(f"[H]: Print this help")
    print(f"")
    print(f"Starting with {dut_name}{dut_ver}-{str(dut_serial+1).zfill(SER_LEN)}")
    while testing_continue:
        if testing_pass:
            print(f"Continue with {dut_name}{dut_ver}-{str(dut_serial+1).zfill(SER_LEN)}")
        else:
            print(f"Retry {dut_name}{dut_ver}-{str(dut_serial).zfill(SER_LEN)}")
        #print(f"Confirm serial number for next Device: {dut_serial}")
        response = input()
        if response == "":
            testing_continue = True
            testing_run = True
            if testing_pass:
                dut_serial = dut_serial + 1
        elif "s" in response or "S" in response:
            testing_continue = False
            testing_run = False
        elif "r" in response or "R" in response:
            testing_continue = True
            testing_run = True
        elif "c" in response or "C" in response:
            testing_continue = True
            testing_run = True
            dut_serial = dut_serial + 1
        elif "h" in response or "H" in response:
            testing_continue = True
            testing_run = False
            print(f"Usage: ")
            print(f"[ ]: Continue with next device when passed, rerun when failed")
            print(f"[R]: Rerun")
            print(f"[C]: Continue with next device")
            print(f"[S]: Stop testing and summarize results")
            print(f"[#ser] continue with specified serial number #ser")
            print(f"[H]: Print this help")
            print(f"")
        else:
            try:
                dut_serial = int(response)
                testing_continue = True
                testing_run = True
            except:
                print(f"ERROR: Unable to interpret command or serial number: {response}")
                testing_continue = True
                testing_run = False
        if testing_run:
            dut_serial_str = str(dut_serial).zfill(SER_LEN)
            print(f"Testing {dut_name}{dut_ver}-{dut_serial_str}") 
            rep.add_dut(name = dut_name, version = dut_ver, serial = dut_serial_str)

            if SIMULATION:
                meas_value = 1
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
                ###############################
                # Test pcb for short-circuits #
                ###############################
                if TEST_ALL or TEST_SHORT:
                    meas_volt_short(equipment = equipment)
                    # +5V2
                    meas_volt_select(equipment = equipment, channel = CH_VOLT_5V2)
                    rep.add_meas(value = dmm.meas_res(), name = f"SHORT: Resistance +5V2", min = 500, max = 10.0e3)
                    debug(f"Resistance: +5V2")
                    meas_volt_off(equipment = equipment)
                    # +3V3
                    meas_volt_select(equipment = equipment, channel = CH_VOLT_3V3)
                    rep.add_meas(value = dmm.meas_res(), name = f"SHORT: Resistance +3V3", min = 500, max = 10.0e3)
                    debug(f"Resistance: +3V3")
                    meas_volt_off(equipment = equipment)
                    # VBAT
                    meas_volt_select(equipment = equipment, channel = CH_VOLT_VBAT)
                    rep.add_meas(value = dmm.meas_res(), name = f"SHORT: Resistance VBAT", min = 100e3, max = 100.0e6)
                    debug(f"Resistance: +VBAT")
                    meas_volt_off(equipment = equipment)
                    # +5V_CHG
                    chg_short(equipment = equipment)
                    meas_volt_select(equipment = equipment, channel = CH_VOLT_5V_CHG)
                    rep.add_meas(value = dmm.meas_res(), name = f"SHORT: Resistance +5V_CHG", min = 100e3, max = 1e6)
                    debug(f"Resistance: +5V_CHG")
                    meas_volt_off(equipment = equipment)
                    chg_off(equipment = equipment)

                ################
                # Test charger #
                ################
                if TEST_ALL or TEST_CHARGER:
                    # Prepare battery simulator
                    bat_sim(equipment = equipment, volt = BAT_VOLT_CHG, amp = BAT_AMP_CHG, ampmeter = True)
                    # Charge A => B
                    chg_on(equipment = equipment, volt = CHG_VOLT, amp = CHG_AMP, pos = "A", neg = "B")
                    time.sleep(CHG_DELAY)
                    rep.add_meas(value = dmm.meas_amp_dc(), name = f"CHARGE: Charging current A => B", min = 0.45, max = 0.55)
                    chg_off(equipment = equipment)
                    # Charge B => C
                    chg_on(equipment = equipment, volt = CHG_VOLT, amp = CHG_AMP, pos = "B", neg = "C")
                    time.sleep(CHG_DELAY)
                    rep.add_meas(value = dmm.meas_amp_dc(), name = f"CHARGE: Charging current B => C", min = 0.45, max = 0.55)
                    chg_off(equipment = equipment)
                    # Charge C => A
                    chg_on(equipment = equipment, volt = CHG_VOLT, amp = CHG_AMP, pos = "C", neg = "A")
                    time.sleep(CHG_DELAY)
                    rep.add_meas(value = dmm.meas_amp_dc(), name = f"CHARGE: Charging current C => A", min = 0.45, max = 0.55)
                    chg_off(equipment = equipment)
                    # Charge voltage
                    meas_volt_select(equipment = equipment, channel = CH_VOLT_VBAT)
                    chg_on(equipment = equipment, volt = CHG_VOLT, amp = CHG_AMP, pos = "A", neg = "B")
                    time.sleep(CHG_DELAY)
                    bat_supply(equipment = equipment, volt = BAT_VOLT_CHG, amp = BAT_AMP_CHG)
                    #bat_off(equipment = equipment)
                    time.sleep(1)
                    #print(f"CHARGE: Charging voltage: {dmm.meas_volt_dc(samples = 100)}")
                    #for i in range(10):
                    #    print(f"CHARGE: Charging voltage: {dmm.meas_volt_dc(samples = 10)}")
                    rep.add_meas(value = dmm.meas_volt_dc(), name = f"CHARGE: Charging voltage", min = 4.050, max = 4.242)
                    chg_off(equipment = equipment)
                    # Disable battery simulator
                    bat_off(equipment = equipment)

                #######
                # BMS #
                #######
                if TEST_ALL or TEST_BMS:
                    bat_supply(equipment = equipment, volt = BAT_VOLT_FULL, amp = BAT_AMP_RUN)
                    chg_on(equipment = equipment, volt = CHG_VOLT, amp = CHG_AMP, pos = "A", neg = "B")
                    time.sleep(CHG_DELAY)
                    chg_off(equipment = equipment)
                    led_off(equipment = equipment)
                    magnet_turn_on(equipment = equipment)
                    time.sleep(HALL_DELAY)
                    magnet_disable(equipment = equipment)
                    level = 2.8
                    bms_test_running = True
                    volt_vbat_bms = 0
                    while(bms_test_running):
                        bat_supply(equipment = equipment, volt = level, amp = BAT_AMP_RUN)
                        meas_volt_select(equipment = equipment, channel = CH_VOLT_VBAT)
                        volt_vbat = dmm.meas_volt_dc()
                        meas_volt_select(equipment = equipment, channel = CH_VOLT_5V2)
                        volt_5v2 = dmm.meas_volt_dc()
                        bms_test_running = volt_5v2 > 4.5
                        if bms_test_running:
                            volt_vbat_bms = volt_vbat
                        level = round(level - 0.01, 3)
                        #print(level)
                        #print(volt_vbat)
                        #print(volt_5v2)
                        #print("")
                    rep.add_meas(value = volt_vbat_bms, name = f"BMS: Undervoltage cutoff", min = 2.46, max = 2.78)
                    ## Cutoff voltage under load
                    #chg_on(equipment = equipment, volt = CHG_VOLT, amp = CHG_AMP, pos = "A", neg = "B")
                    #time.sleep(CHG_DELAY)
                    #chg_off(equipment = equipment)
                    #time.sleep(0.5)
                    #magnet_turn_on(equipment = equipment)
                    #time.sleep(0.5)
                    #magnet_disable(equipment = equipment)
                    #time.sleep(1.5)
                    #short_clear(equipment = equipment)
                    #level = 4.2
                    #bms_test_running = True
                    #while(bms_test_running):
                    #    level = level - 0.01
                    #    bat_supply(equipment = equipment, volt = level, amp = BAT_AMP_RUN)
                    #    meas_volt_select(equipment = equipment, channel = CH_VOLT_5V2)
                    #    volt_5v2 = dmm.meas_volt_dc()
                    #    bms_test_running = volt_5v2 > 4.5
                    #    meas_volt_select(equipment = equipment, channel = CH_VOLT_VBAT)
                    #    volt_vbat = dmm.meas_volt_dc()
                    #    meas_volt_select(equipment = equipment, channel = CH_VOLT_VBAT_MON)
                    #    volt_vbat_mon = dmm.meas_volt_dc()
                    #    print(level)
                    #    print(volt_vbat)
                    #    print(volt_vbat_mon/22*122)
                    #    print(volt_5v2)
                    #    print("")
                    #print(level)

                ###############
                # Hall sensor #
                ###############
                if TEST_ALL or TEST_HALL:
                    bat_supply(equipment = equipment, volt = BAT_VOLT_FULL, amp = BAT_AMP_RUN)
                    chg_on(equipment = equipment, volt = CHG_VOLT, amp = CHG_AMP, pos = "A", neg = "B")
                    time.sleep(CHG_DELAY)
                    chg_off(equipment = equipment)
                    led_off(equipment = equipment)
                    # Check hall sensor turn-on
                    magnet_turn_on(equipment = equipment)
                    time.sleep(HALL_DELAY)
                    magnet_disable(equipment = equipment)
                    meas_volt_select(equipment = equipment, channel = CH_VOLT_3V3)
                    rep.add_meas(value = dmm.meas_volt_dc(), name = f"Hall: +3V3 after turn-on", min = 3.0, max = 3.6)
                    debug(f"Hall: on")
                    time.sleep(HALL_DELAY)
                    meas_volt_select(equipment = equipment, channel = CH_VOLT_HALL)
                    rep.add_meas(value = dmm.meas_volt_dc(), name = f"Hall: HALL when inactive", min = 3.7, max = 4.7)
                    debug(f"Hall: inactive")
                    # Test hall sensor as magnet presence detection
                    magnet_turn_on(equipment = equipment)
                    meas_volt_select(equipment = equipment, channel = CH_VOLT_HALL)
                    rep.add_meas(value = dmm.meas_volt_dc(), name = f"Hall: HALL when active", min = -0.1, max = 0.2)
                    magnet_disable(equipment = equipment)
                    debug(f"Hall: active")
                    meas_volt_off(equipment = equipment)

                #####################
                # On/Off controller #
                #####################
                if TEST_ALL or TEST_ONOFF:
                    bat_supply(equipment = equipment, volt = BAT_VOLT_FULL, amp = BAT_AMP_RUN)
                    chg_on(equipment = equipment, volt = CHG_VOLT, amp = CHG_AMP, pos = "A", neg = "B")
                    time.sleep(CHG_DELAY)
                    chg_off(equipment = equipment)
                    led_off(equipment = equipment)
                    # Hall sensor turn-off
                    magnet_turn_on(equipment = equipment)
                    time.sleep(HALL_DELAY)
                    magnet_disable(equipment = equipment)
                    meas_volt_select(equipment = equipment, channel = CH_VOLT_3V3)
                    if dmm.meas_volt_dc() >= 3.0:
                        magnet_turn_off(equipment = equipment)
                        time.sleep(HALL_DELAY)
                        magnet_disable(equipment = equipment)
                        time.sleep(0.5)
                        meas_volt_select(equipment = equipment, channel = CH_VOLT_3V3)
                        #time.sleep(2)
                        rep.add_meas(value = dmm.meas_volt_dc(), name = f"On/Off Controller: +3V3 after magnet turn-off", min = -0.5, max = 0.5)
                    else:
                        rep.add_meas(value = "FAIL: +3V3 not started", name = f"On/Off Controller: +3V3 after magnet turn-off")
                    debug(f"On/Off Controller: Magnet off")
                    # Charger turn-off
                    magnet_turn_on(equipment = equipment)
                    time.sleep(HALL_DELAY)
                    magnet_disable(equipment = equipment)
                    meas_volt_select(equipment = equipment, channel = CH_VOLT_3V3)
                    if dmm.meas_volt_dc() >= 3.0:
                        chg_on(equipment = equipment, volt = CHG_VOLT, amp = CHG_AMP, pos = "A", neg = "B")
                        time.sleep(CHG_DELAY)
                        chg_off(equipment = equipment)
                        #time.sleep(0.5)
                        meas_volt_select(equipment = equipment, channel = CH_VOLT_3V3)
                        rep.add_meas(value = dmm.meas_volt_dc(), name = f"On/Off Controller: +3V3 after charger turn-off", min = -0.5, max = 0.5)
                    else:
                        rep.add_meas(value = "FAIL: +3V3 not started", name = f"On/Off Controller: +3V3 after charger turn-off")
                    debug(f"On/Off Controller: Charger off")
                    # Kill turn-off
                    sig_gen_select(equipment = equipment, channel = CH_SIG_S_KILL)
                    gen.trig_bus(ch = GEN_CH_SIG)
                    gen.output_on(ch = GEN_CH_SIG)
                    gen.burst_period(per = 10e-3)
                    gen.burst_cycles(cycles = KILL_COUNT, ch = GEN_CH_SIG)
                    gen.pulse_period(per = 1 / KILL_FREQ, ch = GEN_CH_SIG)
                    gen.pulse_width(width = (1/KILL_FREQ*KILL_DUTY), ch = GEN_CH_SIG)
                    time.sleep(2.0)
                    magnet_turn_on(equipment = equipment)
                    time.sleep(HALL_DELAY)
                    magnet_disable(equipment = equipment)
                    meas_volt_select(equipment = equipment, channel = CH_VOLT_3V3)
                    if dmm.meas_volt_dc() >= 3.0:
                        gen.trigger(ch = GEN_CH_SIG)
                        #time.sleep(0.5)
                        meas_volt_select(equipment = equipment, channel = CH_VOLT_3V3)
                        rep.add_meas(value = dmm.meas_volt_dc(), name = f"On/Off Controller: +3V3 after kill turn-off", min = -0.5, max = 0.5)
                    else:
                        rep.add_meas(value = "FAIL: +3V3 not started", name = f"On/Off Controller: +3V3 after kill turn-off")
                    #gen.burst_period(per = 1e-3, ch = GEN_CH_SIG)
                    gen.pulse_width(width = LED_OFF_WIDTH, ch = GEN_CH_SIG)
                    gen.pulse_period(per = LED_OFF_PER, ch = GEN_CH_SIG)
                    gen.burst_cycles(cycles = LED_COUNT*LED_COLORS*LED_BIT_PER_COLOR, ch = GEN_CH_SIG)
                    gen.output_off(ch = GEN_CH_SIG)
                    gen.trig_immediate(ch = GEN_CH_SIG)
                    debug(f"On/Off Controller: KILL off")

                ###############
                # 5.2V Supply #
                ###############
                if TEST_ALL or TEST_5V2:
                    bat_supply(equipment = equipment, volt = BAT_VOLT_FULL, amp = BAT_AMP_RUN)
                    chg_on(equipment = equipment, volt = CHG_VOLT, amp = CHG_AMP, pos = "A", neg = "B")
                    time.sleep(CHG_DELAY)
                    chg_off(equipment = equipment)
                    led_off(equipment = equipment)
                    magnet_turn_on(equipment = equipment)
                    time.sleep(HALL_DELAY)
                    magnet_disable(equipment = equipment)
                    meas_volt_select(equipment = equipment, channel = CH_VOLT_5V2)
                    rep.add_meas(value = dmm.meas_volt_dc(), name = f"5.2V Supply: Voltage", min = 0.58/13e3*(100e3+13e3)*.98, max = 0.61/13e3*(100e3+13e3)*1.02)
                    debug(f"5.2V Supply: voltage idle")
                    # 5V2 voltage with maimum load
                    led_on(equipment = equipment)
                    time.sleep(0.5)
                    bat_current = ps.meas_amp(channel = PS_CH_BAT)
                    if bat_current >= BAT_AMP_THRES_BRIGHT:
                        meas_volt_select(equipment = equipment, channel = CH_VOLT_5V2)
                        rep.add_meas(value = dmm.meas_volt_dc(), name = f"5.2V Supply: Voltage under load", min = 0.58/13e3*(100e3+13e3)*.98-0.1, max = 0.61/13e3*(100e3+13e3)*1.02)
                    else:
                        rep.add_meas(value = f"FAIL: supply current too low: {bat_current}A", name = f"5.2V Supply: Voltage under load", min = 0.58/13e3*(100e3+13e3)*.98-0.1, max = 0.61/13e3*(100e3+13e3)*1.02)
                    debug(f"5.2V Supply: voltage under load")
                    led_off(equipment = equipment)
                    magnet_turn_off(equipment = equipment)
                    time.sleep(HALL_DELAY)
                    magnet_disable(equipment = equipment)
                    magnet_turn_on(equipment = equipment)
                    time.sleep(HALL_DELAY)
                    magnet_disable(equipment = equipment)

                ###############
                # 3.3V Supply #
                ###############
                if TEST_ALL or TEST_3V3:
                    bat_supply(equipment = equipment, volt = BAT_VOLT_FULL, amp = BAT_AMP_RUN)
                    chg_on(equipment = equipment, volt = CHG_VOLT, amp = CHG_AMP, pos = "A", neg = "B")
                    time.sleep(CHG_DELAY)
                    chg_off(equipment = equipment)
                    led_off(equipment = equipment)
                    magnet_turn_on(equipment = equipment)
                    time.sleep(HALL_DELAY)
                    magnet_disable(equipment = equipment)
                    meas_volt_select(equipment = equipment, channel = CH_VOLT_3V3)
                    rep.add_meas(value = dmm.meas_volt_dc(), name = f"3.3V Supply: Voltage", min = 0.588/22e3*(100e3+22e3)*0.98, max = 0.612/22e3*(100e3+22e3)*1.02)
                    debug(f"3.3V Supply: voltage")

                ###################
                # voltage monitor #
                ###################
                if TEST_ALL or TEST_VMON:
                    bat_supply(equipment = equipment, volt = BAT_VOLT_FULL, amp = BAT_AMP_RUN)
                    chg_on(equipment = equipment, volt = CHG_VOLT, amp = CHG_AMP, pos = "A", neg = "B")
                    time.sleep(CHG_DELAY)
                    chg_off(equipment = equipment)
                    led_off(equipment = equipment)
                    magnet_turn_on(equipment = equipment)
                    time.sleep(HALL_DELAY)
                    magnet_disable(equipment = equipment)
                    time.sleep(0.5)
                    meas_volt_select(equipment = equipment, channel = CH_VOLT_VBAT)
                    vbat_meas = dmm.meas_volt_dc()
                    rep.add_meas(value = vbat_meas, name = f"Voltage Monitor: VBAT", min = 4.0, max = 4.3)
                    meas_volt_select(equipment = equipment, channel = CH_VOLT_VBAT_MON)
                    vbat_mon_meas = dmm.meas_volt_dc()
                    rep.add_meas(value = vbat_mon_meas, name = f"Voltage Monitor: VBAT_MON", min = 0.7, max = 0.8)
                    rep.add_meas(value = vbat_meas / vbat_mon_meas, name = f"Voltage Monitor: VBAT_MON divider", min = (VBATMON_R1+VBATMON_R2)/VBATMON_R2*0.98, max = (VBATMON_R1+VBATMON_R2)/VBATMON_R2*1.02)
                    debug(f"Voltage Monitor: Battery voltage")

                ###########################
                # Temperature measurement #
                ###########################
                if TEST_ALL or TEST_TEMP:
                    bat_supply(equipment = equipment, volt = BAT_VOLT_FULL, amp = BAT_AMP_RUN)
                    chg_on(equipment = equipment, volt = CHG_VOLT, amp = CHG_AMP, pos = "A", neg = "B")
                    time.sleep(CHG_DELAY)
                    chg_off(equipment = equipment)
                    led_off(equipment = equipment)
                    magnet_turn_on(equipment = equipment)
                    time.sleep(HALL_DELAY)
                    magnet_disable(equipment = equipment)
                    meas_volt_select(equipment = equipment, channel = CH_VOLT_TEMP)
                    rep.add_meas(value = dmm.meas_volt_dc(), name = f"Temperature: TEMP Voltage", min = 0.55, max = 0.71)
                    debug(f"Termperature: TEMP Voltage")

                ############
                # Failsafe #
                ############
                if TEST_ALL or TEST_FAILSAFE:
                    bat_supply(equipment = equipment, volt = BAT_VOLT_FULL, amp = BAT_AMP_RUN)
                    chg_on(equipment = equipment, volt = CHG_VOLT, amp = CHG_AMP, pos = "A", neg = "B")
                    time.sleep(CHG_DELAY)
                    chg_off(equipment = equipment)
                    led_off(equipment = equipment)
                    magnet_turn_on(equipment = equipment)
                    time.sleep(HALL_DELAY)
                    magnet_disable(equipment = equipment)
                    # Oscillator properties
                    sig_meas_select(equipment = equipment, channel = CH_SIG_M_FS_PULSE)
                    fs_osc_amp = osc.meas_amp(1, 20)
                    #print(fs_osc_amp)
                    rep.add_meas(value = fs_osc_amp[0], name = f"Failsafe: Oscillator Amplitude", min = 4.5, max = 6.0)
                    if MEAS_STAT:
                        rep.add_meas(value = fs_osc_amp[1], name = f"Failsafe: Oscillator Amplitude min")
                        rep.add_meas(value = fs_osc_amp[2], name = f"Failsafe: Oscillator Amplitude max")
                        rep.add_meas(value = fs_osc_amp[3], name = f"Failsafe: Oscillator Amplitude dev")
                    debug(f"Failsafe: Oscillator amplitude")
                    # Oscillator positive pulse width
                    fs_osc_pos_width = osc.meas_pwidth(1, 20)
                    #print(fs_osc_pos_width)
                    rep.add_meas(value = fs_osc_pos_width[0], name = f"Failsafe: Oscillator Positive Width", min = 580e-9, max = 1600e-9)
                    if MEAS_STAT:
                        rep.add_meas(value = fs_osc_pos_width[1], name = f"Failsafe: Oscillator Positive Width min", min =  580e-9, max = 1600e-9)
                        rep.add_meas(value = fs_osc_pos_width[2], name = f"Failsafe: Oscillator Positive Width max", min =  580e-9, max = 1600e-9)
                        rep.add_meas(value = fs_osc_pos_width[3], name = f"Failsafe: Oscillator Positive Width dev", min = -300e-9, max =  300e-9)
                    debug(f"Failsafe: Oscillator positive width")
                    # Oscillator negative pulse width
                    fs_osc_neg_width = osc.meas_nwidth(1, 20)
                    #print(fs_osc_neg_width)
                    rep.add_meas(value = fs_osc_neg_width[0], name = f"Failsafe: Oscillator Negative Width", min = 220e-9, max = 600e-9)
                    if MEAS_STAT:
                        rep.add_meas(value = fs_osc_neg_width[1], name = f"Failsafe: Oscillator Negative Width min", min =  220e-9, max = 600e-9)
                        rep.add_meas(value = fs_osc_neg_width[2], name = f"Failsafe: Oscillator Negative Width max", min =  220e-9, max = 600e-9)
                        rep.add_meas(value = fs_osc_neg_width[3], name = f"Failsafe: Oscillator Negative Width dev", min = -100e-9, max = 100e-9)
                    debug(f"Failsafe: Oscillator negative width")
                    # Oscillator period
                    fs_osc_period = osc.meas_period(1, 20)
                    #print(fs_osc_period)
                    rep.add_meas(value = fs_osc_period[0], name = f"Failsafe: Oscillator Period", min = 800e-9, max = 2200e-9)
                    if MEAS_STAT:
                        rep.add_meas(value = fs_osc_period[1], name = f"Failsafe: Oscillator Period min", min =  800e-9, max = 2200e-9)
                        rep.add_meas(value = fs_osc_period[2], name = f"Failsafe: Oscillator Period max", min =  800e-9, max = 2200e-9)
                        rep.add_meas(value = fs_osc_period[3], name = f"Failsafe: Oscillator Period dev", min = -100e-9, max = 2200e-9)
                    debug(f"Failsafe: Oscillator period")
                    # Missing Pulse Detection
                    led_off(equipment = equipment)
                    meas_volt_select(equipment = equipment, channel = CH_VOLT_FS_ACT)
                    rep.add_meas(value = dmm.meas_volt_dc(), name = f"Failsafe: Missing Pulse Detection without signal", min = -0.55, max = 0.5)
                    debug(f"Failsafe: Missing Pulse Detection without signal")
                    led_on(equipment = equipment)
                    meas_volt_select(equipment = equipment, channel = CH_VOLT_FS_ACT)
                    rep.add_meas(value = dmm.meas_volt_dc(), name = f"Failsafe: Missing Pulse Detection with on signal", min = 5.0, max = 5.5)
                    debug(f"Failsafe: Missing Pulse Detection with on signal")
                    led_off(equipment = equipment, keep_gen = True)
                    meas_volt_select(equipment = equipment, channel = CH_VOLT_FS_ACT)
                    rep.add_meas(value = dmm.meas_volt_dc(), name = f"Failsafe: Missing Pulse Detection with off signal", min = 5.0, max = 5.5)
                    debug(f"Failsafe: Missing Pulse Detection with off signal")
                    # Failsafe switch-over
                    led_off(equipment = equipment, keep_gen = True)
                    time.sleep(0.5)
                    rep.add_meas(value = ps.meas_amp(channel = PS_CH_BAT), name = f"Failsafe: Switch-over normal operation", min = 0.02, max = 0.20)
                    debug(f"Failsafe: Switch-over normal operation")
                    short(equipment = equipment, channel = CH_SHORT_DATA)
                    gen.output_off(ch = GEN_CH_SIG)
                    time.sleep(0.5)
                    rep.add_meas(value = ps.meas_amp(channel = PS_CH_BAT), name = f"Failsafe: Switch-over Failsafe operation", min = 1.00, max = 2.00)
                    debug(f"Failsafe: Switch-over Failsafe operation")

                #############################
                # Off state battery current #
                #############################
                if TEST_ALL or TEST_OFF_CURR:
                    bat_supply(equipment = equipment, volt = BAT_VOLT_FULL, amp = BAT_AMP_RUN, ampmeter = True)
                    dmm.meas_amp_dc()
                    chg_on(equipment = equipment, volt = CHG_VOLT, amp = CHG_AMP, pos = "A", neg = "B")
                    time.sleep(CHG_DELAY)
                    chg_off(equipment = equipment)
                    time.sleep(0.5)
                    #print(f"Off state current{dmm.meas_amp_dc(samples = 100)}")
                    off_state_current = dmm.meas_amp_dc(samples = 10, get_statistics = True)
                    #print(off_state_current)
                    rep.add_meas(value = off_state_current[0], name = f"Off state battery current: Current", min = -10.0e-6, max = -2e-6)
                    if MEAS_STAT:
                        rep.add_meas(value = off_state_current[1], name = f"Off state battery current: Current min")#, min = -10e-6, max = -2e-6)
                        rep.add_meas(value = off_state_current[2], name = f"Off state battery current: Current max")#, min = -10e-6, max = -2e-6)
                        rep.add_meas(value = off_state_current[3], name = f"Off state battery current: Current dev")#, min =  -5e-6, max =  5e-6)
                    debug(f"Off state battery current: Current")

                ###############
                # Programming #
                ###############
                if TEST_ALL or TEST_PROG:
                    bat_supply(equipment = equipment, volt = BAT_VOLT_FULL, amp = BAT_AMP_RUN)
                    chg_on(equipment = equipment, volt = CHG_VOLT, amp = CHG_AMP, pos = "A", neg = "B")
                    time.sleep(CHG_DELAY)
                    chg_off(equipment = equipment)
                    #time.sleep(0.5)
                    short(equipment = equipment, channel = CH_SHORT_DATA_FS)
                    short(equipment = equipment, channel = [CH_SHORT_GPIO0, CH_SHORT_RST])
                    magnet_turn_on(equipment = equipment)
                    time.sleep(HALL_DELAY)
                    magnet_disable(equipment = equipment)
                    time.sleep(HALL_DELAY)
                    short_open(equipment = equipment, channel = [CH_SHORT_RST])
                    print("Confirm Programming completion: ")
                    #TODO: Replace input() statement with programming
                    input()
                    short_open(equipment = equipment, channel = [CH_SHORT_GPIO0])
                    short(equipment = equipment, channel = [CH_SHORT_RST])
                    time.sleep(0.1)
                    short_open(equipment = equipment, channel = [CH_SHORT_RST])

                ###################
                # Stop everything #
                ###################
                if TEST_ALL or not TEST_KEEP_ON:
                    bat_off(equipment = equipment)
                    switch.open_all()
                else:
                    bat_supply(equipment = equipment, volt = BAT_VOLT_FULL, amp = BAT_AMP_RUN)
                    chg_on(equipment = equipment, volt = CHG_VOLT, amp = CHG_AMP, pos = "A", neg = "B")
                    time.sleep(CHG_DELAY)
                    chg_off(equipment = equipment)
                    magnet_turn_on(equipment = equipment)
                    time.sleep(HALL_DELAY)
                    magnet_disable(equipment = equipment)
                    led_off(equipment = equipment, keep_gen = True)
                    meas_volt_select(equipment = equipment, channel = CH_VOLT_TEMP)
                    print(dmm.meas_volt_dc())

                ########################
                # Unused code snippets #
                ########################
                ## Iterate through number of activated LEDs
                #gen.pulse_setup(low=LED_LOW, high=LED_HIGH, per=LED_OFF_PER, width=LED_OFF_WIDTH, ch = GEN_CH_SIG)
                #gen.burst_setup(mode = "TRIG", per = 1e-3, cycles = LED_COUNT*LED_COLORS*LED_BIT_PER_COLOR, ch = GEN_CH_SIG)
                #gen.output_on(ch = GEN_CH_SIG)
                #sig_gen_select(equipment = equipment, channel = CH_SIG_S_DATA_FS)
                #meas_volt_select(equipment = equipment, channel = CH_VOLT_VBAT)
                #for n in range(1, 21):
                #    gen.burst_setup(mode = "TRIG", per = 1e-3, cycles = n*LED_COLORS*LED_BIT_PER_COLOR, ch = GEN_CH_SIG)
                #    gen.pulse_period(per = LED_ON_PER, ch = GEN_CH_SIG)
                #    gen.pulse_width(width = LED_ON_WIDTH, ch = GEN_CH_SIG)
                #    print(f"Number of LEDs: {n}")
                #    print(f"Voltage: {dmm.meas_volt_dc()}")
                #    time.sleep(1)

            rep.print_dut(filename = f"{dut_name}{dut_ver}-{dut_serial_str}.txt", path = report_path, print_passfail = True, print_minmax = True)

            if rep.get_dut_pass():
                testing_pass = True
                print(f"Testing of {dut_name}{dut_ver}-{dut_serial_str} completed: Pass")
            else:
                testing_pass = False
                print(f"Testing of {dut_name}{dut_ver}-{dut_serial_str} completed: Fail")
    rep.print_report(filename = f"NC1-1BA {rep.datetime.strftime('%Y-%m-%d %H-%M-%S')}.csv", path = report_path, print_passfail = True, print_minmax = True)


if __name__ == "__main__":
    main()
