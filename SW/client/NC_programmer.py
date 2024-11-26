import subprocess
import time
import pyftdi.serialext as serial
import argparse

# NC_programmer.py -s 1 0x2 "../../../esptool/esptool.py" --chip esp8266 --port "ftdi://ftdi:ft-x:0:1/1" --baud 115200 write_flash 0x0 .pio\build\nodemcuv2\firmware.bin


def auto_int(x):
    return int(x, 0)


if __name__ == "__main__":
   
   
   #subprocess.call("test1.py", shell=True)
   #time.sleep(10)
   #
   
   parser = argparse.ArgumentParser(
                    prog='ProgramName',
                    description='What the program does',
                    epilog='Text at the bottom of help')
   parser.add_argument('esptool_path', help ="Path to the esptool.py", default="../../../esptool/esptool.py")
   parser.add_argument('-s','--set_EEPROM_config', help="Set EEPROM values ['Serial Number' 'HW Revision']", nargs=2, type=auto_int)  
   parser.add_argument('-p', '--port', help="Serial port device")
   parser.add_argument('-b','--baudrate', help="serial port baudrate (default: 115200)", default=115200)
   args, unknown = parser.parse_known_args()
   print(args)
   print(unknown)
   print(F"Call: esptool-ftdi.py {args.esptool_path} --port {args.port} --baud {args.baudrate} {' '.join(unknown)}")
   subprocess.call(F"esptool-ftdi.py {args.esptool_path} --port {args.port} {' '.join(unknown)}", shell=True)
   
   if(args.set_EEPROM_config==None):
    exit()
   print("Wait until restarted...\r\n")
   time.sleep(10)
   port = serial.serial_for_url("ftdi://ftdi:ft-x:0:1/1", baudrate=args.baudrate, timeout=2)
   port.write('readEEPROM\n')
   port.write(F"setSerialNo {args.set_EEPROM_config[0]} {args.set_EEPROM_config[1]}\n")
   port.write("saveEEPROM\n")
   port.write('readEEPROM\n')
   port.flush()
   #while port.in_waiting:
   line = port.readline().decode('UTF-8')
   while line != "":
    print(F"{line}", end="")
    line = port.readline().decode('UTF-8')