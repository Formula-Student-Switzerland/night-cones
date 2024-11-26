import os
import sys
import shutil
import pyftdi.serialext as serial
from pyftdi.ftdi import Ftdi


def import_from_path(esptool_path, name="esptool"):
    if not os.path.isfile(esptool_path):
        esptool_lookup = shutil.which(esptool_path)
        if esptool_lookup == None:
            raise Exception("No such file: %s" % esptool_path)
        else:
            esptool_path = esptool_lookup

    if sys.version_info >= (3,5):
        import importlib.util
        spec = importlib.util.spec_from_file_location(name, esptool_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
    elif sys.version_info >= (3,3):
        from importlib.machinery import SourceFileLoader
        module = SourceFileLoader(name, esptool_path).load_module()
    else:
        import imp
        module = imp.load_source(name, esptool_path)
    return module
    
def set_dtr_override(self, state: bool) -> None:
    ''' Uses CBUS 0 instead of regular DTR Signal'''
    self.set_cbus_direction(1,1)
    value = 0x0 if state else 0x1;
    self.set_cbus_gpio(value)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        raise SystemExit("usage: %s <esptool.py> [args...]" % sys.argv[0])

    print("esptool-ftdi-dtr.py Wrapper\n")

    esptool = import_from_path(sys.argv[1])
    sys.argv[1:] = sys.argv[2:]
    
    Ftdi.set_dtr = set_dtr_override

    esptool.esptool.loader.serial = serial
    esptool.esptool._main()
