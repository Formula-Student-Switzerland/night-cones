import pyvisa
import time
import statistics

class Oscilloscope:
    """ Class for Keysight DSO1000 Oscilloscope """

    def opc_check(self, opccnt_time = 1): # Change OPC time to constant <self.opccnt_time>
        opccnt_limit = int(opccnt_time / self.opccnt_delay)
        opc = 0
        opccnt = 0
        while opc != 1:
            opc = int(self.osc.query("*OPC?"))
            opccnt += 1
            if opccnt > opccnt_limit:
                raise NameError("Oscilloscope: Operation complete not achieved within {opccnt_time}s")
            time.sleep(self.opccnt_delay)

    def reset(self):
        self.osc.write("*RST")
        self.opc_check()

    def meas(self, ch, func, samples = 1):
        if samples == 1:
            self.osc.write(f":SINGLE")
            self.opc_check()
            trig_cnt = 0
            trig_stat = 0
            while trig_cnt < self.trig_time / self.trig_delay and trig_stat != 1:
                if "STOP" in self.osc.query(f":TRIG:STAT?"):
                    self.opc_check()
                    trig_stat = 1
                time.sleep(self.trig_delay)
                trig_cnt += 1
            if trig_stat != 1:
                self.osc.write(f":FORC")
                self.opc_check()
                while trig_stat != 2:
                    if "STOP" in self.osc.query(f":TRIG:STAT?"):
                        self.opc_check()
                        trig_stat = 2
                    time.sleep(self.trig_delay)
            if trig_stat == 2:
                print(f"Warning! Trigger forced, check measurement value plausibility!")
                self.osc.write(f":BEEP:ACT")
            result = float(self.osc.query(f":MEAS:{func}? CHAN{int(ch)}"))
            self.opc_check()
        else:
            res = []
            for i in range(samples):
                self.osc.write(f":SINGLE")
                self.opc_check()
                trig_cnt = 0
                trig_stat = 0
                while trig_cnt < self.trig_time / self.trig_delay and trig_stat != 1:
                    if "STOP" in self.osc.query(f":TRIG:STAT?"):
                        self.opc_check()
                        trig_stat = 1
                    time.sleep(self.trig_delay)
                    trig_cnt += 1
                if trig_stat != 1:
                    self.osc.write(f":FORC")
                    self.opc_check()
                    while trig_stat != 2:
                        if "STOP" in self.osc.query(f":TRIG:STAT?"):
                            self.opc_check()
                            trig_stat = 2
                        time.sleep(self.trig_delay)
                if trig_stat == 2:
                    print(f"Warning! Trigger forced, check measurement value plausibility!")
                    self.osc.write(f":BEEP:ACT")
                res.append(float(self.osc.query(f":MEAS:{func}? CHAN{int(ch)}")))
                self.opc_check()
            result = [sum(res)/len(res), min(res), max(res), statistics.stdev(res), res]
        return result

    def meas_falltime(self, ch, samples = 1):
        return self.meas(ch, "FALL", samples)

    def meas_freq(self, ch, samples = 1):
        return self.meas(ch, "FREQ", samples)

    def meas_nduty(self, ch, samples = 1):
        return self.meas(ch, "NDUT", samples)

    def meas_nwidth(self, ch, samples = 1):
        return self.meas(ch, "NWID", samples)

    def meas_overshoot(self, ch, samples = 1):
        return self.meas(ch, "OVER", samples)

    def meas_pduty(self, ch, samples = 1):
        return self.meas(ch, "PDUT", samples)

    def meas_period(self, ch, samples = 1):
        return self.meas(ch, "PER", samples)

    def meas_preshoot(self, ch, samples = 1):
        return self.meas(ch, "PRES", samples)

    def meas_pwidth(self, ch, samples = 1):
        return self.meas(ch, "PWID", samples)

    def meas_risetime(self, ch, samples = 1):
        return self.meas(ch, "RIS", samples)

    def meas_amp(self, ch, samples = 1):
        return self.meas(ch, "VAMP", samples)

    def meas_avg(self, ch, samples = 1):
        return self.meas(ch, "VAV", samples)

    def meas_basevolt(self, ch, samples = 1):
        return self.meas(ch, "VBAS", samples)

    def meas_vmax(self, ch, samples = 1):
        return self.meas(ch, "VMAX", samples)

    def meas_vmin(self, ch, samples = 1):
        return self.meas(ch, "VMIN", samples)

    def meas_vpp(self, ch, samples = 1):
        return self.meas(ch, "VPP", samples)

    def meas_vrms(self, ch, samples = 1):
        return self.meas(ch, "VRMS", samples)

    def meas_vtop(self, ch, samples = 1):
        return self.meas(ch, "VTOP", samples)

    def setup_nightcone(self):
        setup = []
        setup.append(":ACQ:TYPE NORM")
        # Channel 1
        setup.append(":CHAN1:DISP 1")
        setup.append(":CHAN1:COUP DC")
        setup.append(":CHAN1:BWL 1") # Added BW Limit to reduce ringing
        setup.append(":CHAN1:FILT 0")
        setup.append(":CHAN1:INV 0")
        setup.append(":CHAN1:PROB 10X")
        #setup.append(":CHAN1:PROB 1X") ###################DEBUG#############
        setup.append(":CHAN1:SCAL 1")
        setup.append(":CHAN1:OFFS -2.5")
        setup.append(":CHAN1:UNIT VOLT")
        setup.append(":CHAN1:VERN 0")
        #Channel 2
        setup.append(":CHAN2:DISP 1")
        setup.append(":CHAN2:COUP DC")
        setup.append(":CHAN2:BWL 0")
        setup.append(":CHAN2:FILT 0")
        setup.append(":CHAN2:INV 0")
        setup.append(":CHAN2:PROB 10X")
        #setup.append(":CHAN2:PROB 1X") ###################DEBUG#############
        setup.append(":CHAN2:SCAL 1")
        setup.append(":CHAN2:OFFS -2.5")
        setup.append(":CHAN2:UNIT VOLT")
        setup.append(":CHAN2:VERN 0")
        # Counter
        setup.append(":COUN:ENAB 0")
        # Cursors - No cursor setup, not needed for this measurement
        # Display - No display setup, default setup after reset sufficient
        # Keys
        setup.append(":KEY:LOCK ENAB")
        # Mask - No mask setup, not needed for this measurement
        # Math - No math setup, not needed for this measurement
        # Measurement
        #setup.append(":MEAS:TOT 1")
        # Timebase
        #setup.append(":TIM:DEL:OFF 0")
        #setup.append(":TIM:DEL:SCAL 1e-6")
        setup.append(":TIM:FORM:YT")
        setup.append(":TIM:OFFS 0")
        setup.append(":TIM:SCAL 500e-9")
        #setup.append(":TIM:SCAL 200e-6") ################DEBUG###############
        setup.append(":TIM:MODE:MAIN")
        # Trigger
        setup.append(":TRIG:COUP DC")
        setup.append(":TRIG:HFRE 0")
        setup.append(":TRIG:HOLD 100e-9")
        setup.append(":TRIG:MODE EDGE")
        setup.append(":TRIG:SENS 0.5")
        setup.append(":TRIG:EDGE:LEV 1.67")
        setup.append(":TRIG:EDGE:SLOP POS")
        setup.append(":TRIG:EDGE:SOUR CHAN1")
        setup.append(":TRIG:EDGE:SWE NORM")
        # Waveform - No waveform setup, not needed for this measurement
        setup.append(":DISP:MNUS 0")

        for s in setup:
            print(s)
            self.osc.write(s)
            self.opc_check()

    def __init__(self, rm, interface="USB0", USB_ID=16, serialnumber="CN00000000"):
        # Variables
        self.rm = rm
        self.ID = ""
        self.opccnt_time = 10
        self.opccnt_delay = 0.001
        self.trig_time = 1
        self.trig_delay = 0.001

        # Initiate USB communication
        self.osc = self.rm.open_resource(f"{interface}::{str(USB_ID)}::{serialnumber}::0::INSTR")

        # Selftest
        Resp = self.osc.query("*IDN?")
        if self.ID not in Resp:
            raise NameError(f"Oscilloscope: Equipment setup incorrect, Expected: THURBLY THANDAR, CPX200DP, Detected: {Resp}...")

        # Reset to power-on state
        self.osc.write("*RST")
        self.opc_check()

    if __name__ == "__main__":
        self.rm = pyvisa.ResourceManager()
        __init__(self, rm, "USB0")

