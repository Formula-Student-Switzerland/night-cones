# FSCH Night-Cones
![FSCH night-cones](https://github.com/Formula-Student-Switzerland/night-cones/releases/download/NC1-1BA/SampleImage.jpg)

The FSCH Night-Cones are ESP8266 controlled RGB lights for the illumination of a formula student track. The project is described in detail in the documentation available in the `doc` folder. 

## Hardware

### PCBs

#### NC1-1
Nightcone main PCB

##### NC1-1AA
Initial prototype PCB as ordered

##### NC1-1AB
Modifications to the assembly of the initial prototype

##### NC1-1BA
PCB version for first series production run

##### NC1-1BB
Modifications to first series prodction run, version used in FSCH 2024 night skidpad

##### NC1-1CA
All issues from previous versions implemented. 
This version should be used for reproduction of the NightCones. 

##### Assembly variants
Multiple versions of the WS2813 LED exist, which have a slightly different pinout. This is covered by the different assembly variants of the PCB. 

###### NC1-11
WS2813B-B: 
* Pin 1 is VCC
* DATA_IN is connected to BACKUP_OUT
* VCC pin is supplied with a 270 Ohm resistor and bypassed with a 1uF capacitor

###### NC1-12
WS2813B-V5:
* Pin 1 is BO
* The BO pin and is connected to BACKUP_OUT

###### NC1-13
WS2813C:
* Pin 1 is VCC
* DATA_IN is connected to BACKUP_OUT
* VCC pin is supplied with a 270 Ohm resistor and bypassed with a 1uF capacitor

###### NC1-14
WS2813E:
* Pin 1 is NC
* DATA_IN is connected to BACKUP_OUT

#### NC1-2
Testadapter for automated PCB test of the main nightcone PCB NC1-1. Only index NC1-2BA exists, which is intended to be used for NC1-1B*. 

#### NC1-3
Programming adapter to program the nightcone PCB standalone as well as mounted in the enclosure. To program, a USB-A to UAB-B cable and a 6-pin RJ-11 TagConnect cable are required. 

### Housing
The current housing is designed to be printed out of transparent PETG. It consists of three parts that are printed independently and glued together afterwards. 

## Software
The current software state includes a running software on the cone (`SW/client`) and a command line tool to control the cones from a computer (`SW/server/NetworkInterface`).

### Server GUI
The GUI shows the state of all cones and sets their colors without typing commands. It requires Python 3.10 or newer with Tkinter and the `ifaddr` package (`pip install ifaddr`). Start it in `SW/server/NetworkInterface` with:

```
python NightConesGUI.py
```

1. **Connect:** Choose the mode and press *Connect*.
   * *Real cones*: select the network adapter connected to the cone WiFi. A `192.168.0.x` adapter is preselected if one exists.
   * *Simulator*: simulated cones run inside the GUI, no cones or network are needed. A yellow bar shows that no real cones are controlled. Ten cones are simulated: one never changes its color, one drops out after the first refresh, one is offline and the cones miss some messages, so all error reports can be tried out. Start with `python NightConesGUI.py --simulator` to preselect this mode.
2. **Cones:** The list shows every cone with its current color, brightness, mode, battery, signal and temperature. Cones that are not connected are shown in red. The list refreshes every 10 s, or with the *Refresh* button.
3. **Set color:** Select the cones (all connected cones, IDs like `3`, `1,4,7` or `10-20`, or click them in the list), pick a color, brightness and mode and press *Apply*. The GUI checks whether the cones changed and retries up to 3 times, like the `SetColor` command of the CLI. The result is shown at the bottom.

The GUI uses the same ports as the CLI. They can be changed with `--tx-port` and `--rx-port`. The GUI and the CLI cannot run at the same time on the same computer.

### Server CLI
The CLI requires Python 3.10 or newer and the `ifaddr` package (`pip install ifaddr`). Start it in `SW/server/NetworkInterface` with:

```
python NightConesCLI.py
```

On startup, select the network adapter connected to the cone network, keep the default ports and type `1` to activate the RX thread. The RX thread is required to receive any feedback from the cones. Type `help` for a list of all commands.

#### State of the cones
`State [ids]` requests the state of all cones and lists the ID, color, brightness, light mode, state of charge, RSSI and temperature of every cone that responded. Afterwards, all cones that are not connected are reported. This includes cones that responded earlier but not anymore and, on the `192.168.0.x` network, every IP of the skidpad and exit/entry range (`.11` to `.108`) that never responded.

#### Setting colors
`SetColor <ids> <color> [brightness] [mode] [repetition] [phase]` sets the color of single cone IDs or lists of IDs:

* IDs: `3`, `1,4,7`, `10-20`, `1,4-6` or `all` (all IDs that responded)
* Color: `0`-`255` or `red`, `green`, `blue`, `white`, `yellow`
* Brightness: `0`-`15` (default `15`), light mode: `0`-`9` (default `0`, continuous), repetition time and phase: `0`-`255` (default `0`)

Example: `SetColor 1,3,10-12 red 8`

After sending, the CLI requests the state of the cones and checks whether they actually changed. IDs that did not change, or for which no cone responded, are retried up to 3 times. In the end, the cones that still did not change are reported with the state they show, as well as the IDs no cone responded for.

A data frame always contains all IDs up to the highest one. The CLI therefore remembers the last state sent per ID and sends it again for all IDs that are not changed. IDs that were never set from the CLI are filled with the state reported by the cones (repetition time and phase are not reported and set to `0`). IDs without any state are switched off.

The verification requires the cone firmware SW rev 1.2 or newer, which reports the currently shown color in the status frame. Cones with older firmware report color `0` and are therefore always reported as not changed.

### Simulator
`NightConesSimulator.py` simulates several cones on localhost to test the CLI without hardware. Run it in a second terminal and select `127.0.0.1` in the CLI:

```
python NightConesSimulator.py --ids 0,0,1,2,3,5 --stuck 1 --offline 1 --drop-rate 0.3
```

* `--ids`: cone ID of each simulated cone (IDs may repeat)
* `--stuck`: number of cones that never change their color
* `--offline`: number of cones that never respond
* `--drop-out`: number of cones that respond to the first request only
* `--drop-rate`: probability that a cone ignores a data frame 
