import pyvisa

class SwitchUnit:
    """ Class for HP 3488 Switch Unit """
    def close_all():
        self.sw.query("CLOSE 100, 101, 102, 103, 110, 111, 112, 113, 120, 121, 122, 123, 130, 131, 132, 133, 200, 201, 202, 203, 210, 211, 212, 213, 220, 221, 222, 223, 230, 231, 232, 233, 300, 301, 302, 303, 310, 311, 312, 313, 320, 321, 322, 323, 330, 331, 332, 333, 400, 401, 402, 403, 410, 411, 412, 413, 420, 421, 422, 423, 430, 431, 432, 433")

    def open_all():
        self.sw.query("OPEN 100, 101, 102, 103, 110, 111, 112, 113, 120, 121, 122, 123, 130, 131, 132, 133, 200, 201, 202, 203, 210, 211, 212, 213, 220, 221, 222, 223, 230, 231, 232, 233, 300, 301, 302, 303, 310, 311, 312, 313, 320, 321, 322, 323, 330, 331, 332, 333, 400, 401, 402, 403, 410, 411, 412, 413, 420, 421, 422, 423, 430, 431, 432, 433")

    def __init__(self, rm, GPIB_Addr DispMsg):
        self.sw = rm.open_resource('GPIB::' + str(GPIB_Addr) + '::INSTR')
        Resp = self.sw.query("ID?")
        if(Resp != "HP3488A"):
            error("Switch unit: Equipment setup incorrect")
        Resp = self.sw.query("TEST")
        if(int(Resp) != 0):
            error("Switch unit: Self-test failed")
        Resp = self.sw.query("CTYPE 1")
        if(Resp != "MATRIX SW 44473"):
            error("Switch unit: Incorrect card configuration in slot 1")
        Resp = self.sw.query("CTYPE 2")
        if(Resp != "MATRIX SW 44473"):
            error("Switch unit: Incorrect card configuration in slot 2")
        Resp = self.sw.query("CTYPE 3")
        if(Resp != "MATRIX SW 44473"):
            error("Switch unit: Incorrect card configuration in slot 3")
        Resp = self.sw.query("CTYPE 4")
        if(Resp != "MATRIX SW 44473"):
            error("Switch unit: Incorrect card configuration in slot 4")
        Resp = self.sw.query("CTYPE 5")
        if(Resp != "RELAY MUX 44470"):
            error("Switch unit: Incorrect card configuration in slot 5")
        self.sw.query("DISP " + DispMsg)
        self.sw.query("LOCK1")
        self.open_all()

    if __name__ == "__main__":
        rm = pyvisa.ResourceManager()
        __init__(self, rm, 20, "HP 3488 INIT")

""" ####################################################################### """
""" ### OLD CODE ########################################################## """
""" ####################################################################### """

    def main():

        rm = pyvisa.ResourceManager()
        rm.list_resources()
        switch_unit = rm.open_resource('GPIB::20::INSTR')

        print(switch_unit.query("TEST"))
        print(switch_unit.query("CTYPE 1"))
        print(switch_unit.query("CTYPE 2"))
        print(switch_unit.query("CTYPE 3"))
        print(switch_unit.query("CTYPE 4"))
        print(switch_unit.query("CTYPE 5"))
        switch_unit.query("DISP NC1-1 TEST")

        switch_unit.query("CLOSE 100, 101, 102, 103")
        time.sleep(0.1)
        switch_unit.query("OPEN 100, 101, 102, 103")
        time.sleep(1)
        switch_unit.query("CLOSE 100, 101, 102, 103, 110, 111, 112, 113, 120, 121, 122, 123, 130, 131, 132, 133")
        time.sleep(0.1)
        switch_unit.query("OPEN 100, 101, 102, 103, 110, 111, 112, 113, 120, 121, 122, 123, 130, 131, 132, 133")
        time.sleep(1)

    def sw_close_all():
        switch_unit.query("CLOSE 100, 101, 102, 103, 110, 111, 112, 113, 120, 121, 122, 123, 130, 131, 132, 133, 200, 201, 202, 203, 210, 211, 212, 213, 220, 221, 222, 223, 230, 231, 232, 233, 300, 301, 302, 303, 310, 311, 312, 313, 320, 321, 322, 323, 330, 331, 332, 333, 400, 401, 402, 403, 410, 411, 412, 413, 420, 421, 422, 423, 430, 431, 432, 433")

    def sw_open_all():
        switch_unit.query("OPEN 100, 101, 102, 103, 110, 111, 112, 113, 120, 121, 122, 123, 130, 131, 132, 133, 200, 201, 202, 203, 210, 211, 212, 213, 220, 221, 222, 223, 230, 231, 232, 233, 300, 301, 302, 303, 310, 311, 312, 313, 320, 321, 322, 323, 330, 331, 332, 333, 400, 401, 402, 403, 410, 411, 412, 413, 420, 421, 422, 423, 430, 431, 432, 433")

    def sw_reset():
        switch_unit.query("CRESET 1, 2, 3, 4, 5")
