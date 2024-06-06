import datetime

class Device:
    """ Class for reporting """

    def add_meas(self, value, name = ""):
        self.meas_value.append(value)
        self.meas_name.append(name)
        
    def __init__(self, name = "", version = "", serial = 0):
        # Variables
        self.name = name
        self.version = version
        self.serial = serial
        self.meas_value = []
        self.meas_name = []
        self.datetime = datetime.datetime.now()

    if __name__ == "__main__":
        __init__(self)

