import datetime

class Device:
    """ Class for reporting """

    def add_meas(self, value, name = "", min = "", max = ""):
        self.meas_value.append(value)
        self.meas_name.append(name)
        nopassfail = ""
        nopassfails = ["", "N/A", "n/a", "n.a."]
        if isinstance(value, str):
            self.meas_passfail.append(f"N/A")
            min = nopassfail
            max = nopassfail
            print(f"Test failed: {name}: {value}, Min: {min}, Max: {max}")
        elif (min in nopassfails) and (max in nopassfails):
            self.meas_passfail.append(f"N/A")
            min = nopassfail
            max = nopassfail
        elif min in nopassfails:
            if value <= max:
                self.meas_passfail.append(f"Pass")
            else:
                self.meas_passfail.append(f"Fail")
                self.passfail = "Fail"
                print(f"Test failed: {name}: {value}, Min: {min}, Max: {max}")
            min = nopassfail
        elif max in nopassfails:
            if value >= min:
                self.meas_passfail.append(f"Pass")
            else:
                self.meas_passfail.append(f"Fail")
                self.passfail = "Fail"
                print(f"Test failed: {name}: {value}, Min: {min}, Max: {max}")
            max = nopassfail
        else:
            if value >= min and value <= max:
                self.meas_passfail.append(f"Pass")
            else:
                self.meas_passfail.append(f"Fail")
                self.passfail = "Fail"
                print(f"Test failed: {name}: {value}, Min: {min}, Max: {max}")
        self.meas_min.append(min)
        self.meas_max.append(max)

    def __init__(self, name = "", version = "", serial = 0):
        # Variables
        self.name = name
        self.version = version
        self.serial = serial
        self.passfail = "Pass"
        self.meas_value = []
        self.meas_name = []
        self.meas_passfail = []
        self.meas_min = []
        self.meas_max = []
        self.datetime = datetime.datetime.now()

    if __name__ == "__main__":
        __init__(self)

