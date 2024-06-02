class SwitchUnitCard:
    """ Class for HP 3488 Switch Unit Card """
    SEPARATOR = ", "

    def ch(self, channels):
        if isinstance(channels, int):
            channels = [str(channels).zfill(2)]
        elif isinstance(channels, str):
            channels = [f"{channels[0]}{channels[1]}"]
        elif isinstance(channels, list):
            for i in range(len(channels)):
                if isinstance(channels[i], int):
                    channels[i] = str(channels[i]).zfill(2)
        if len(channels) > 0:
            separator = ""
            ch_str = ""
            if "00000" in self.card_type:
                ch_str = ""
            elif "44470" in self.card_type:
                for ch in channels:
                    if (int(f"{ch[0]}{ch[1]}") >= 0) and (int(f"{ch[0]}{ch[1]}") <= 9):
                        ch_str = f"{ch_str}{separator}{str(self.card_slot)}{ch[0]}{ch[1]}"
                        separator = self.SEPARATOR
                    else:
                        raise NameError(f"HP3488 SwitchUnitCard: Channel out of range [0..9]: {int(f'{ch[0]}{ch[1]}')}")
            elif "44471" in self.card_type:
                for ch in channels:
                    if (int(f"{ch[0]}{ch[1]}") >= 0) and (int(f"{ch[0]}{ch[1]}") <= 9):
                        ch_str = f"{ch_str}{separator}{str(self.card_slot)}{ch[0]}{ch[1]}"
                        separator = self.SEPARATOR
                    else:
                        raise NameError(f"HP3488 SwitchUnitCard: Channel out of range [0..9]: {int(f'{ch[0]}{ch[1]}')}")
            elif "44472" in self.card_type:
                raise NameError(f"HP3488A SwitchUnitCard: {self.card_type} not implemented yet")
            elif "44473" in self.card_type:
                if (len(channels) % 2) == 0:
                    for idx in range(int(len(channels)/2)):
                        ch_a = channels[2*idx]
                        ch_b = channels[2*idx+1]
                        if (int(f"{ch_a[1]}") >= 0) and (int(f"{ch_a[1]}") <= 3) and (int(f"{ch_b[1]}") >= 0) and (int(f"{ch_b[1]}") <= 3):
                            if (ch_a[0] == "R" and ch_b[0] == "C"):
                                ch_str = f"{ch_str}{separator}{str(self.card_slot)}{ch_a[1]}{ch_b[1]}"
                                separator = self.SEPARATOR
                            elif(ch_a[0] == "C" and ch_b[0] == "R"):
                                ch_str = f"{ch_str}{separator}{str(self.card_slot)}{ch_b[1]}{ch_a[1]}"
                                separator = self.SEPARATOR
                            else:
                                raise NameError(f"HP3488A SwitchUnitCard: Each pair of a connection must specify a row (R) and a column (C). CH A: {ch_a}, CH B: {ch_b}")
                        else:
                            raise NameError(f"HP3488 SwitchUnitCard: Channel out of range [0..3]: {int(f'{ch_a[1]}')}, {int(f'{ch_b[1]}')}")
                else:
                    raise NameError(f"HP3488A SwitchUnitCard: Number of channels to connect must be a multiple of 2")
            elif "44474" in self.card_type:
                raise NameError(f"HP3488A SwitchUnitCard: {self.card_type} not implemented yet")
            elif "44475" in self.card_type:
                raise NameError(f"HP3488A SwitchUnitCard: {self.card_type} not implemented yet")
            else:
                raise NameError(f"HP3488A SwitchUnitCard: Unrecognised card type: {type}")
        else:
            raise NameError("HP3488A SwitchUnitCard: channel list empty")
        return ch_str

    def __init__(self, slot, type):
        # ID
        if int(slot) >= 1 and int(slot) <= 5:
            self.card_slot = int(slot)
        else:
            raise NameError(f"HP3488 SwitchUnitCard: Card slot out of range [1..5]: {slot} ({int(slot)})")
        # Type
        if (type == 0) or (type == "00000") or (type == "NO CARD") or (type == "NO CARD 00000"):
            self.card_type = "00000"
        elif (type == 44470) or (type == "44470") or (type == "RELAY MUX") or (type == "RELAY MUX 44470"):
            self.card_type = "44470"
        elif (type == 44471) or (type == "44471") or (type == "GP RELAY") or (type == "GP RELAY 44471"):
            self.card_type = "44471"
        elif (type == 44472) or (type == "44472") or (type == "VHF SW") or (type == "VHF SW 44472"):
            self.card_type = "44472"
        elif (type == 44473) or (type == "44473") or (type == "MATRIX SW") or (type == "MATRIX SW 44473"):
            self.card_type = "44473"
        elif (type == 44474) or (type == "44474") or (type == "DIGITAL IO") or (type == "DIGITAL IO 44474"):
            self.card_type = "44474"
        elif (type == 44475) or (type == "44475") or (type == "BREADBOARD") or (type == "BREADBOARD 44475"):
            self.card_type = "44475"
        else:
            raise NameError(f"HP3488A SwitchUnitCard: Unrecognised card type: {type}")


    if __name__ == "__main__":
        __init__(self, 1, "NO CARD 00000")

