import os
import datetime
from Device import Device

class Report:
    """ Class for reporting """

    def add_dut(self, name = "", version = "", serial = 0):
        dut = Device(name = name, version = version, serial = serial)
        self.dut.append(dut)

    def add_meas(self, value, name = ""):
        self.dut[len(self.dut)-1].add_meas(value = value, name = name)

    def print_dut(self, filename = "", path = "", idx = -1):
        if idx < 0:
            idx = len(self.dut)-1
        if filename == "":
            for i in range(len(self.dut[idx].meas_value)):
                print(f"> {self.dut[idx].meas_name[i]} => {self.dut[idx].meas_value[i]}")
        else:
            # Path check and creation
            if path != "":
                path_split = path.split("/")
                path_separator = ""
                path_check = ""
                for path_idx in range(len(path_split)):
                    path_check = f"{path_check}{path_separator}{path_split[path_idx]}"
                    path_separator = "/"
                    if not os.path.isdir(path_check):
                        os.mkdir(path_check)
                path = f"{path}/"
            # File export
            f = open(f"{path}{filename}", "w")
            f.write(f"{self.dut[idx].name}{self.dut[idx].version} - {self.dut[idx].serial} - Test Protocol - {self.dut[idx].datetime.strftime('%Y-%m-%d %H:%M:%S')}\n")
            for i in range(len(self.dut[idx].meas_value)):
                f.write(f"{self.dut[idx].meas_name[i]}: {self.dut[idx].meas_value[i]}\n")
            f.close()

    def print_report(self, filename = "", path = ""):
        # Title line
        title = ""
        separator = ""
        title = f"{title}{separator}DUT"
        separator = self.SEPARATOR
        title = f"{title}{separator}DUT Serial"
        title = f"{title}{separator}Date Time"
        for meas_idx in range(len(self.dut[0].meas_name)):
            title = f"{title}{separator}{self.dut[0].meas_name[meas_idx]}"
            separator = self.SEPARATOR
        # Data block
        data = []
        for dut_idx in range(len(self.dut)):
            data.append("")
            separator = ""
            data[dut_idx] = f"{data[dut_idx]}{separator}{self.dut[dut_idx].name}"
            data[dut_idx] = f"{data[dut_idx]}{separator}{self.dut[dut_idx].version}"
            separator = self.SEPARATOR
            data[dut_idx] = f"{data[dut_idx]}{separator}{self.dut[dut_idx].serial}"
            data[dut_idx] = f"{data[dut_idx]}{separator}{self.dut[dut_idx].datetime.strftime('%Y-%m-%d %H:%M:%S')}"
            for meas_idx in range(len(self.dut[0].meas_name)):
                data[dut_idx] = f"{data[dut_idx]}{separator}{self.dut[dut_idx].meas_value[meas_idx]}"
                separator = self.SEPARATOR
        if filename == "":
            print(title)
            for data_line in data:
                print(data_line)
        else:
            # Path check and creation
            if path != "":
                path_split = path.split("/")
                path_separator = ""
                path_check = ""
                for path_idx in range(len(path_split)):
                    path_check = f"{path_check}{path_separator}{path_split[path_idx]}"
                    path_separator = "/"
                    if not os.path.isdir(path_check):
                        os.mkdir(path_check)
                path = f"{path}/"
            # File export
            f = open(f"{path}{filename}", "w")
            f.write(f"{title}\n")
            for data_line in data:
                f.write(f"{data_line}\n")
            f.close()

    def __init__(self, title = ""):
        # Variables
        self.title = title
        self.dut = []
        self.SEPARATOR = ","
        self.datetime = datetime.datetime.now()

    if __name__ == "__main__":
        __init__(self)

