import pyvisa
import time

class Multimeter:
    """ Class for HP 34401A Digital Multimeter """

    def opc_check(self, opccnt_time = 1): # Change OPC time to constant <self.opccnt_time>
        opccnt_limit = int(opccnt_time / self.opccnt_delay)
        opc = 0
        opccnt = 0
        while opc != 1:
            opc = int(self.dmm.query("*OPC?"))
            opccnt += 1
            if opccnt > opccnt_limit:
                raise NameError("Multimeter: Operation complete not achieved within {opccnt_time}s")
            time.sleep(self.opccnt_delay)

    def reset(self):
        self.dmm.write("*RST")
        self.opc_check()

    def meas(self, func, samples = 1, mrange = "DEF", resolution = "DEF"):
        if "DEF" in mrange or "def" in mrange:
            mrange = f""
        elif "MIN" in mrange or "min" in mrange:
            mrange = f" MIN"
        elif "MAX" in mrange or "max" in mrange:
            mrange = f" MAX"
        elif isinstance(mrange, int):
            mrange = f" {mrange}"
        else :
            try:
                mrange = f" {str(int(mrange))}"
            except:
                raise NameError(f"Multimeter: Invalid range: {mrange}")
        if samples == 1:
            self.dmm.write(f"VOLT:DC:RES MIN")
            res = float(self.dmm.query(f"MEAS:{func}?"))
        elif samples <= 512:
            self.dmm.write(f"CONF:{func}")
            self.dmm.write(f"SAMP:COUN {str(samples)}")
            self.dmm.write(f"TRIG:SOUR BUS")
            self.opc_check()
            self.dmm.write(f"INIT")
            self.dmm.write(f"*TRG")
            timeout = self.dmm.timeout
            self.dmm.timeout = 100*samples
            res = self.dmm.query(f"FETC?")
            self.dmm.timeout = timeout
            res = [float(idx) for idx in res.split(",")]
        else:
            separator = ""
            res = ""
            while samples > 0:
                s = min(samples, 512)
                samples -= s
                res = f"{res}{separator}"
                separator = ","
                self.dmm.write(f"CONF:{func}")
                self.dmm.write(f"VOLT:NPLC 1")
                self.dmm.write(f"SAMP:COUN {str(s)}")
                self.dmm.write(f"TRIG:SOUR BUS")
                self.opc_check()
                self.dmm.write(f"INIT")
                self.dmm.write(f"*TRG")
                timeout = self.dmm.timeout
                self.dmm.timeout = 300*s
                res = f"{res}{self.dmm.query(f'FETC?')}"
                self.dmm.timeout = timeout
            res = [float(idx) for idx in res.split(",")]
        return res

    def meas_volt_dc(self, samples = 1):
        return self.meas("VOLT:DC", samples)

    def meas_volt_dc_ratio(self, samples = 1):
        return self.meas("VOLT:DC:RAT", samples)

    def meas_volt_ac(self, samples = 1):
        return self.meas("VOLT:AC", samples)

    def meas_amp_dc(self, samples = 1):
        return self.meas("CURR:DC", samples)

    def meas_amp_ac(self, samples = 1):
        return self.meas("CURR:AC", samples)

    def meas_res(self, samples = 1):
        return self.meas("RES", samples)

    def meas_res_kelvin(self, samples = 1):
        return self.meas("FRES", samples)

    def meas_frequency(self, samples = 1):
        return self.meas("FREQ", samples)

    def meas_period(self, samples = 1):
        return self.meas("PER", samples)

    def meas_continuity(self, samples = 1):
        return self.meas("CONT", samples)

    def meas_diode(self, samples = 1):
        return self.meas("DIOD", samples)

    def __init__(self, rm, Interface="GPIB0", GPIB_Addr=5, DispMsg=""):
        # Variables
        self.rm = rm
        self.ID = "HEWLETT-PACKARD,34401A"
        self.opccnt_time = 1
        self.opccnt_delay = 0.1

        # Initiate GPIB communication
        self.dmm = self.rm.open_resource(f"{Interface}::{str(GPIB_Addr)}::INSTR")

        # Selftest
        Resp = self.dmm.query("*IDN?")
        if self.ID not in Resp:
            raise NameError(f"Multimeter: Equipment setup incorrect, Expected: {self.ID}, Detected: {Resp}...")
        #timeout = self.dmm.timeout
        #self.dmm.timeout = 20000
        #Resp = self.dmm.query("*TST?")
        #if int(Resp) != 0:
        #    raise NameError(f"Multimeter: Selftest failed")
        #self.dmm.timeout = timeout

        # Reset to power-on state
        self.reset()
        self.opc_check()

        # Display
        if DispMsg != "":
            self.dmm.write(f"DISP:TEXT \"{DispMsg}\"")

    if __name__ == "__main__":
        self.rm = pyvisa.ResourceManager()
        __init__(self, rm, "GPIB0", 5)

