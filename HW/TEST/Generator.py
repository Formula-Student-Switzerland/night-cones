import pyvisa
import time

class Generator:
    """ Class for Keysight 33500B Signal Generator """

    def opc_check(self, opccnt_time = 1): # Change OPC time to constant <self.opccnt_time>
        opccnt_limit = int(opccnt_time / self.opccnt_delay)
        opc = 0
        opccnt = 0
        while opc != 1:
            opc = int(self.gen.query("*OPC?"))
            opccnt += 1
            if opccnt > opccnt_limit:
                raise NameError("Signal Generator: Operation complete not achieved within {opccnt_time}s")
            time.sleep(self.opccnt_delay)

    def reset(self):
        self.gen.write("*RST")
        self.opc_check()

    def output_on(self, ch = 1):
        self.gen.write(f"OUTP{ch} 1")

    def output_off(self, ch = 1):
        self.gen.write(f"OUTP{ch} 0")

    def output_load(self, load, ch = 1):
        self.gen.write(f"OUTP{ch}:LOAD {load}")

    def pulse_setup(self, low, high, per, width, ch = 1, lead = 0, trail = 0):
        self.gen.write(f"SOUR{ch}:FUNC PULS")
        self.gen.write(f"SOUR{ch}:FUNC:PULS:WIDT {width}")
        if lead > 0:
            self.gen.write(f"SOUR{ch}:FUNC:PULS:TRAN:LEAD {lead}")
        if trail > 0:
            self.gen.write(f"SOUR{ch}:FUNC:PULS:TRAN:TRA {trail}")
        self.gen.write(f"SOUR{ch}:FUNC:PULS:PER {per}")
        self.gen.write(f"SOUR{ch}:VOLT:LOW {low}")
        self.gen.write(f"SOUR{ch}:VOLT:HIGH {high}")

    def pulse_width(self, width, ch = 1):
        self.gen.write(f"SOUR{ch}:FUNC:PULS:WIDT {width}")

    def pulse_period(self, per, ch = 1):
        self.gen.write(f"SOUR{ch}:FUNC:PULS:PER {per}")

    def pulse_low(self, low, ch = 1):
        self.gen.write(f"SOUR{ch}:VOLT:LOW {low}")

    def pulse_high(self, high, ch = 1):
        self.gen.write(f"SOUR{ch}:VOLT:HIGH {high}")

    def burst_setup(self, mode = "TRIG", per = 0, cycles = 0, ch = 1):
        self.gen.write(f"SOUR{ch}:BURS:MODE {mode}")
        if cycles > 0:
            self.gen.write(f"SOUR{ch}:BURS:NCYC {cycles}")
        if isinstance(per, str) or per > 0:
            self.gen.write(f"SOUR{ch}:BURS:INT:PER {per}")
        self.burst_on()

    def burst_on(self, ch = 1):
        self.gen.write(f"SOUR{ch}:BURS:STAT 1")

    def burst_off(self, ch = 1):
        self.gen.write(f"SOUR{ch}:BURS:STAT 0")

    def burst_period(self, per, ch = 1):
        self.gen.write(f"SOUR{ch}:BURS:INT:PER {per}")

    def burst_cycles(self, cycles, ch = 1):
        self.gen.write(f"SOUR{ch}:BURS:NCYC {cycles}")

    def trig_immediate(self, ch = 1):
        self.gen.write(f"TRIG{ch}:SOUR IMM")

    def trig_bus(self, ch = 1):
        self.gen.write(f"TRIG{ch}:SOUR BUS")

    def trigger(self, ch = 1):
        self.gen.write(f"TRIG{ch}")

    def disp_text(self, DispMsg = ""):
        if DispMsg != "":
            if len(DispMsg) > 40:
                DispMsg = DispMsg[:40]
            self.gen.write(f"DISP:TEXT \"{DispMsg}\"")
        else:
            self.gen.write(f"DISP:TEXT:CLE")

    def beep(self):
        self.gen.write(f"SYST:BEEP")

    def __init__(self, rm, Interface="GPIB0", GPIB_Addr=10, DispMsg="", load = ["INF", "INF"], run_selftest = True):
        # Variables
        self.rm = rm
        self.ID = "Agilent Technologies,33512B"
        self.opccnt_time = 1
        self.opccnt_delay = 0.1

        # Initiate GPIB communication
        self.gen = self.rm.open_resource(f"{Interface}::{str(GPIB_Addr)}::INSTR")

        # Selftest
        Resp = self.gen.query("*IDN?")
        if self.ID not in Resp:
            raise NameError(f"Signal Generator: Equipment setup incorrect, Expected: {self.ID}, Detected: {Resp}...")
        self.disp_text(DispMsg)
        if run_selftest:
            timeout = self.gen.timeout
            self.gen.timeout = 20000
            Resp = self.gen.query("*TST?")
            if int(Resp) != 0:
                raise NameError(f"Signal Generator: Selftest failed")
            self.gen.timeout = timeout

        # Reset to power-on state
        self.reset()
        self.opc_check()

        # Display
        self.disp_text()
        self.gen.write(f"DISP:FOC CH1")
        self.gen.write(f"DISP:UNIT:ARBR PER")
        self.gen.write(f"DISP:UNIT:PULS WIDT")
        self.gen.write(f"DISP:UNIT:RATE PER")
        self.gen.write(f"DISP:UNIT:VOLT HIGH")
        self.gen.write(f"DISP:VIEW STAN")

        # Output
        if isinstance(load, str) or isinstance(load, int):
            load = [load, load]
        self.output_load(load = load[0], ch = 1)
        self.output_load(load = load[1], ch = 2)
        self.output_off(1)
        self.output_off(2)

    if __name__ == "__main__":
        self.rm = pyvisa.ResourceManager()
        __init__(self, rm, "GPIB0", 10)
