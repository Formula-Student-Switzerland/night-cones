# night-cones

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
