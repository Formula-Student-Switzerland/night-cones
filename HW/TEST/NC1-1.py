import time
import pyvisa
#from tkinter import *
#from tkinter import ttk

def main():
    #root = Tk()
    #frm = ttk.Frame(root, padding=10)
    #frm.grid()
    #ttk.Label(frm, text="Hello World!").grid(column=0, row=0)
    #ttk.Button(frm, text="Quit", command=root.destroy).grid(column=1, row=0)
    #root.mainloop()

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

if __name__ == "__main__":
    main()
