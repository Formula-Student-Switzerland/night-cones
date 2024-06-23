import pyvisa

class SwitchUnit:
    """ Class for HP 3488 Switch Unit """
    def open_all(self):
        for card in self.cards.values():
            self.sw.query(f"CRESET {card.card_slot}")

    def open_card(self, card):
        self.sw.query(f"CRESET {card.card_slot}")

    def open(self, ch):
        if isinstance(ch, str):
            self.sw.query(f"OPEN {ch}")
        elif isinstance(ch, list):
            separator = ""
            channels = ""
            for c in ch:
                channels = f"{channels}{separator}{c}"
                separator = ", "
            self.sw.query(f"OPEN {channels}")

    def close(self, ch):
        if isinstance(ch, str):
            self.sw.query(f"CLOSE {ch}")
        elif isinstance(ch, list):
            separator = ""
            channels = ""
            for c in ch:
                channels = f"{channels}{separator}{c}"
                separator = ", "
            self.sw.query(f"CLOSE {channels}")

    def __init__(self, rm, GPIB_INTERFACE="GPIB0", GPIB_Addr=20, cards = [], DispMsg="", run_selftest = True):
        # Variables
        self.rm = rm
        self.cards = cards
        self.ID = "HP3488A"

        # Initiate GPIB communication
        self.sw = self.rm.open_resource(f"{GPIB_INTERFACE}::{str(GPIB_Addr)}::INSTR")

        # Selftest
        Resp = self.sw.query("ID?")
        if self.ID not in Resp:
            raise NameError(f"Switch unit: Equipment setup incorrect, Expected: {self.ID}, Detected: {Resp}...")
        if run_selftest:
            Resp = self.sw.query("TEST")
            if (int(Resp) != 0):
                raise NameError("Switch unit: Self-test failed")

        # Card type check
        for card in self.cards.values():
            Response = self.sw.query(f"CTYPE {card.card_slot}")
            if card.card_type not in Response:
                raise NameError(f"Switch unit: Incorrect card configuration in slot {card.card_slot}, Expected: {card.card_type}, Installed: {Response}")

        # Reset to power-on state
        self.sw.query("RESET")

        # Display
        if DispMsg != "":
            self.sw.query("DISP " + DispMsg)
        #self.sw.query("LOCK1")

    if __name__ == "__main__":
        self.rm = pyvisa.ResourceManager()
        __init__(self, rm, "GPIB0", 20, [], "HP 3488 INIT")

