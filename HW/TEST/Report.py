import os
import datetime
from Device import Device

class Report:
    """ Class for reporting """

    def add_dut(self, name = "", version = "", serial = 0):
        dut = Device(name = name, version = version, serial = serial)
        self.dut.append(dut)

    def add_meas(self, value, name = "", min = "", max = ""):
        self.dut[len(self.dut)-1].add_meas(value = value, name = name, min = min, max = max)

    def print_dut(self, filename = "", path = "", idx = -1, print_passfail = False, print_minmax = False):
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
            f.write(f"Overall result: {self.dut[idx].passfail}\n")
            for i in range(len(self.dut[idx].meas_value)):
                f.write(f"\n{self.dut[idx].meas_name[i]}: {self.dut[idx].meas_value[i]}\n")
                if print_passfail:
                    if print_minmax:
                        # Todo: do not print empty limits
                        if self.dut[idx].meas_min[i] == "" and self.dut[idx].meas_max[i] == "":
                            f.write(f"    Result: {self.dut[idx].meas_passfail[i]}\n")
                        elif self.dut[idx].meas_min[i] == "":
                            f.write(f"    Result: {self.dut[idx].meas_passfail[i]} Max: {self.dut[idx].meas_max[i]}\n")
                        elif self.dut[idx].meas_max[i] == "":
                            f.write(f"    Result: {self.dut[idx].meas_passfail[i]} Min: {self.dut[idx].meas_min[i]}\n")
                        else: 
                            f.write(f"    Result: {self.dut[idx].meas_passfail[i]} Limits: {self.dut[idx].meas_min[i]} .. {self.dut[idx].meas_max[i]}\n")
                    else:
                        f.write(f"    Result: {self.dut[idx].meas_passfail[i]}\n")
            f.close()

    def print_report(self, filename = "", path = "", print_passfail = False, print_minmax = False):
        # Title line
        title = ""
        separator = ""
        title = f"{title}{separator}DUT"
        separator = self.SEPARATOR
        title = f"{title}{separator}DUT Serial"
        title = f"{title}{separator}Date Time"
        title = f"{title}{separator}DUT Pass / Fail"
        for meas_idx in range(len(self.dut[0].meas_name)):
            title = f"{title}{separator}{self.dut[0].meas_name[meas_idx]}"
            separator = self.SEPARATOR
            if print_passfail:
                title = f"{title}{separator}Pass / Fail"
                if print_minmax:
                    title = f"{title}{separator}Min{separator}Max"
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
            data[dut_idx] = f"{data[dut_idx]}{separator}{self.dut[dut_idx].passfail}"
            for meas_idx in range(len(self.dut[0].meas_name)):
                data[dut_idx] = f"{data[dut_idx]}{separator}{self.dut[dut_idx].meas_value[meas_idx]}"
                separator = self.SEPARATOR
                if print_passfail:
                    data[dut_idx] = f"{data[dut_idx]}{separator}{self.dut[dut_idx].meas_passfail[meas_idx]}"
                    if print_minmax:
                        data[dut_idx] = f"{data[dut_idx]}{separator}{self.dut[dut_idx].meas_min[meas_idx]}"
                        data[dut_idx] = f"{data[dut_idx]}{separator}{self.dut[dut_idx].meas_max[meas_idx]}"
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

