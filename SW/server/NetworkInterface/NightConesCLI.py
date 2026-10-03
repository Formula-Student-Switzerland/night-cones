import NightConesController
import NightConesMessage
import cmd
#import readline
import threading
from datetime import datetime
import time

class NightConesCLI(cmd.Cmd):
    
    _UDP_TX_PORT = 5250
    _UDP_RX_PORT = 5251  
    SEND_LOOP = 100
    COLOR_RED = 191
    COLOR_GREEN = 95
    COLOR_BLUE = 32
    COLOR_WHITE = 255
    COLOR_YELLOW = 127
    BRIGHTNESS_LOW = 2
    BRIGHTNESS_HIGH = 15
    LIGHTMODE_CONT = 0
    GW_SLEEP = 3.0
    SKIDPAD_NOF = 72
    EXITENTRY_NOF = 26
    SKIDPAD_IP_START = 11
    SKIDPAD_IP_STOP = SKIDPAD_IP_START + SKIDPAD_NOF - 1
    EXITENTRY_IP_START = SKIDPAD_IP_STOP + 1
    EXITENTRY_IP_STOP = EXITENTRY_IP_START + EXITENTRY_NOF - 1
    SKIDPAD_ID = 0
    EXITENTRY_ID = 1
    IP_PREFIX = "192.168.0."
    IP_BROADCAST = "192.168.255.255"
    prompt = '>> '
    intro = 'Welcome to the Nightcones CLI. Type "help" for available commands.'
    
    def preloop(self):
        ''' Gets Executed before starting the CLI'''
        self._controller = NightConesController.NightConesController(self._print_message)
        self._networkif = self._controller.networkif
        self._send_data = self._controller.send_data
    
        print("Available Network Interfaces:")
        ip_adresses = []
        ip_index = 0
        adapters = self._networkif.getAdpaterList()
        for adapter in adapters:
            print("IPs of network adapter " + adapter.nice_name)
            for ip in adapter.ips:
                    print("     (%d):   %s/%s" % (ip_index, ip.ip, ip.network_prefix))
                    ip_adresses.append(ip)
                    ip_index += 1
                    
        ip_select=input("Select IP Range: ")
        tx_port = input("Select UDP TX Port (Default %d):" % self._UDP_TX_PORT)
        if(tx_port.isdigit() == False):
            tx_port=self._UDP_TX_PORT
        rx_port = input("Select UDP RX Port (Default %d):" % self._UDP_RX_PORT)
        if(rx_port.isdigit() == False):
            rx_port=self._UDP_RX_PORT
        
        rx_active = input("Type 1 to activate RX Thread:")
        if(rx_active.isdigit() == True) and (rx_active == "1"):
            self._rx_active = True
        else:
            self._rx_active = False
            rx_port=self._UDP_RX_PORT+1
        
        if(ip_select.isdigit() and int(ip_select)<ip_index):
            if(self._rx_active == True):
                print("Starting RX Thread")
            self._controller.connect(ip_adresses[int(ip_select)],int(tx_port),int(rx_port),self._rx_active)
        else: 
            print("No valid selection, terminating tool")
            exit()
            
    def do_hello(self, line):
        """Print a greeting."""
        print("Hello, World!")

    def do_quit(self, line):
        """Exit the CLI."""
        self._controller.close()
        return True
        
    def do_SetConeState(self, line):
        '''Set Colors for one cone ID. If no arguments are supplied, they will be prompted
        
        Arguments (all positional, int): Color  Brightness  Lightmode  Frequency  phase
        '''
        try:
            data = [int(ele) for ele in line.split()]
            data[2] = NightConesMessage.NightConesMessage.LightMode(data[2])
            if(len(data) !=5):
                raise Exception
        except:
            data = []
            #data.append(int(input("Select Cone ID: ")))
            data.append(max(0,min(255,int(input("Select Color [0-255]: ")))))
            data.append(max(0,min(15,int(input("Select Brightness [0-15]: ")))))
            data.append(NightConesMessage.NightConesMessage.LightMode(max(0,min(15,int(input("Select Light Mode [0-15]: "))))))
            data.append(max(0,min(255,int(input("Select Frequency [0-255]: ")))))
            data.append(max(0,min(255,int(input("Select Phase [0-255]: ")))))
            
        self._send_data([data])  
        
    def do_SetConeStates(self, line):
        '''Set Colors for one cone ID. 
        
        Arguments (all positional, int): Color  Brightness  Lightmode  Frequency  phase
        '''
        try:
            line = [int(ele) for ele in line.split()]
            if((len(line) % 5) !=0):
                print("***Error: Number of arguments not a multiple of 5")
                return 
            
            cone_values = []
            for i in range(0,len(line),5):
                data = line[i:(i+5)]
                data[2] = NightConesMessage.NightConesMessage.LightMode(data[2])
                cone_values.append(data)
        except Exception as e:
            print(F"***Error {e}")
            return
            
        self._send_data(cone_values)  
        
    def do_SetupSkidpad(self, line):
        ''' Setup cone IDs for skidpad
        '''
        data = []
        #data.append(int(input("Select Cone ID: ")))
        data.append(max(0,min(255,int(self.COLOR_BLUE))))
        data.append(max(0,min(15,int(self.BRIGHTNESS_HIGH))))
        data.append(NightConesMessage.NightConesMessage.LightMode(max(0,min(15,int(self.LIGHTMODE_CONT)))))
        data.append(max(0,min(255,int(0)))) #input("Select Frequency [0-255]: ")))))
        data.append(max(0,min(255,int(0)))) #input("Select Phase [0-255]: ")))))
        for i in range(0, self.SEND_LOOP):
            self._send_data([data])  

        for i in range(self.SKIDPAD_IP_START, self.EXITENTRY_IP_STOP+1):
            data_tuples = []
            if i <= self.SKIDPAD_IP_STOP:
                tuple = (3,self.SKIDPAD_ID);
                data_tuples.append(tuple)            
            elif i <= self.EXITENTRY_IP_STOP:
                tuple = (3,self.EXITENTRY_ID);
                data_tuples.append(tuple)            
            ip = F"{self.IP_PREFIX}{i}"
            #print(ip)
            #print(data_tuples)
            self._networkif.sendConfigData(data_tuples,ip)

        data = []
        #data.append(int(input("Select Cone ID: ")))
        data.append(max(0,min(255,int(self.COLOR_RED))))
        data.append(max(0,min(15,int(self.BRIGHTNESS_HIGH))))
        data.append(NightConesMessage.NightConesMessage.LightMode(max(0,min(15,int(self.LIGHTMODE_CONT)))))
        data.append(max(0,min(255,int(0)))) #input("Select Frequency [0-255]: ")))))
        data.append(max(0,min(255,int(0)))) #input("Select Phase [0-255]: ")))))
        for i in range(0, self.SEND_LOOP):
            self._send_data([data])  
        self.do_SetConeStates(F"{self.COLOR_RED} {self.BRIGHTNESS_HIGH} {self.LIGHTMODE_CONT} 0 0 {self.COLOR_BLUE} {self.BRIGHTNESS_HIGH} {self.LIGHTMODE_CONT} 0 0")

    def do_S(self, line):
        ''' Setup cone IDs for skidpad
        '''
        self.do_SetupSkidpad("")

    def do_Off(self, line):
        ''' Turn all cones off
        '''
        #for i in range(self.SKIDPAD_IP_START,self.EXITENTRY_IP_STOP+1):
            #self.do_SetConeConfig(F"{self.IP_PREFIX}{i} 5 0")
        self.do_SetConeConfig(F"{self.IP_BROADCAST} 5 0")

    def do_CS(self, line):
        '''Set Rainbow pattern for cheese award
        Start
        '''
        for i in range(0, self.SEND_LOOP):
            self.do_SetConeState(F"0 {self.BRIGHTNESS_HIGH} 7 80 0")

    def do_CP(self, line):
        '''Set Rainbow pattern for cheese award
        Presentation
        '''
        self.do_W("")

    def do_CJ(self, line):
        '''Set Rainbow pattern for cheese award
        Judging
        '''
        for i in range(0, self.SEND_LOOP):
            self.do_SetConeState(F"0 {self.BRIGHTNESS_HIGH} 8 20 0")

    def do_CT(self, line):
        '''Set Rainbow pattern for cheese award
        Tension before announcement
        '''
        for i in range(0, self.SEND_LOOP):
            self.do_SetConeState(F"0 {self.BRIGHTNESS_HIGH} 6 3 0")

    def do_CA(self, line):
        '''Set Rainbow pattern for cheese award
        Announcement
        '''
        for i in range(0, self.SEND_LOOP):
            self.do_SetConeState(F"0 {self.BRIGHTNESS_HIGH} 2 3 0")

    def do_O(self, line):
        '''Set Colors for one cone ID to white at no brightness. 
        '''
        for i in range(0, self.SEND_LOOP):
            self.do_SetConeStates(F"{self.COLOR_WHITE} 0 {self.LIGHTMODE_CONT} 0 0 {self.COLOR_WHITE} {0} {self.LIGHTMODE_CONT} 0 0")
        
    def do_o(self, line):
        '''Set Colors for one cone ID to white at no brightness. 
        '''
        for i in range(0, self.SEND_LOOP):
            self.do_SetConeStates(F"{self.COLOR_WHITE} 0 {self.LIGHTMODE_CONT} 0 0 {self.COLOR_WHITE} {0} {self.LIGHTMODE_CONT} 0 0")
        
    def do_R(self, line):
        '''Set Colors for one cone ID to red at high brightness. 
        '''
        for i in range(0, self.SEND_LOOP):
            #self.do_SetConeState(F"{self.COLOR_RED} {self.BRIGHTNESS_HIGH} {self.LIGHTMODE_CONT} 0 0")
            self.do_SetConeStates(F"{self.COLOR_RED} {self.BRIGHTNESS_HIGH} {self.LIGHTMODE_CONT} 0 0 {self.COLOR_BLUE} {self.BRIGHTNESS_HIGH} {self.LIGHTMODE_CONT} 0 0")
        
    def do_r(self, line):
        '''Set Colors for one cone ID to red at low brightness. 
        '''
        for i in range(0, self.SEND_LOOP):
            #self.do_SetConeState(F"{self.COLOR_RED} {self.BRIGHTNESS_LOW} {self.LIGHTMODE_CONT} 0 0")
            self.do_SetConeStates(F"{self.COLOR_RED} {self.BRIGHTNESS_LOW} {self.LIGHTMODE_CONT} 0 0 {self.COLOR_BLUE} {self.BRIGHTNESS_LOW} {self.LIGHTMODE_CONT} 0 0")
        
    def do_G(self, line):
        '''Set Colors for one cone ID to green at high brightness. 
        '''
        for i in range(0, self.SEND_LOOP):
            #self.do_SetConeState(F"{self.COLOR_GREEN} {self.BRIGHTNESS_HIGH} {self.LIGHTMODE_CONT} 0 0")
            self.do_SetConeStates(F"{self.COLOR_GREEN} {self.BRIGHTNESS_HIGH} {self.LIGHTMODE_CONT} 0 0 {self.COLOR_BLUE} {self.BRIGHTNESS_HIGH} {self.LIGHTMODE_CONT} 0 0")
        
    def do_g(self, line):
        '''Set Colors for one cone ID to green at low brightness. 
        '''
        for i in range(0, self.SEND_LOOP):
            #self.do_SetConeState(F"{self.COLOR_GREEN} {self.BRIGHTNESS_LOW} {self.LIGHTMODE_CONT} 0 0")
            self.do_SetConeStates(F"{self.COLOR_GREEN} {self.BRIGHTNESS_LOW} {self.LIGHTMODE_CONT} 0 0 {self.COLOR_BLUE} {self.BRIGHTNESS_LOW} {self.LIGHTMODE_CONT} 0 0")
        
    def do_B(self, line):
        '''Set Colors for one cone ID to blue at high brightness. 
        '''
        for i in range(0, self.SEND_LOOP):
            #self.do_SetConeState(F"{self.COLOR_BLUE} {self.BRIGHTNESS_HIGH} {self.LIGHTMODE_CONT} 0 0")
            self.do_SetConeStates(F"{self.COLOR_BLUE} {self.BRIGHTNESS_HIGH} {self.LIGHTMODE_CONT} 0 0 {self.COLOR_BLUE} {self.BRIGHTNESS_HIGH} {self.LIGHTMODE_CONT} 0 0")
        
    def do_b(self, line):
        '''Set Colors for one cone ID to blue at low brightness. 
        '''
        for i in range(0, self.SEND_LOOP):
            #self.do_SetConeState(F"{self.COLOR_BLUE} {self.BRIGHTNESS_LOW} {self.LIGHTMODE_CONT} 0 0")
            self.do_SetConeStates(F"{self.COLOR_BLUE} {self.BRIGHTNESS_LOW} {self.LIGHTMODE_CONT} 0 0 {self.COLOR_BLUE} {self.BRIGHTNESS_LOW} {self.LIGHTMODE_CONT} 0 0")
        
    def do_Y(self, line):
        '''Set Colors for one cone ID to yellow at high brightness. 
        '''
        for i in range(0, self.SEND_LOOP):
            #self.do_SetConeState(F"{self.COLOR_YELLOW} {self.BRIGHTNESS_HIGH} {self.LIGHTMODE_CONT} 0 0")
            self.do_SetConeStates(F"{self.COLOR_YELLOW} {self.BRIGHTNESS_HIGH} {self.LIGHTMODE_CONT} 0 0 {self.COLOR_BLUE} {self.BRIGHTNESS_HIGH} {self.LIGHTMODE_CONT} 0 0")
        
    def do_y(self, line):
        '''Set Colors for one cone ID to yellow at low brightness. 
        '''
        for i in range(0, self.SEND_LOOP):
            #self.do_SetConeState(F"{self.COLOR_YELLOW} {self.BRIGHTNESS_LOW} {self.LIGHTMODE_CONT} 0 0")
            self.do_SetConeStates(F"{self.COLOR_YELLOW} {self.BRIGHTNESS_LOW} {self.LIGHTMODE_CONT} 0 0 {self.COLOR_BLUE} {self.BRIGHTNESS_LOW} {self.LIGHTMODE_CONT} 0 0")
        
    def do_W(self, line):
        '''Set Colors for one cone ID to white at high brightness. 
        '''
        for i in range(0, self.SEND_LOOP):
            #self.do_SetConeState(F"{self.COLOR_WHITE} {self.BRIGHTNESS_HIGH} {self.LIGHTMODE_CONT} 0 0")
            self.do_SetConeStates(F"{self.COLOR_WHITE} {self.BRIGHTNESS_HIGH} {self.LIGHTMODE_CONT} 0 0 {self.COLOR_BLUE} {self.BRIGHTNESS_HIGH} {self.LIGHTMODE_CONT} 0 0")
        
    def do_w(self, line):
        '''Set Colors for one cone ID to white at low brightness. 
        '''
        for i in range(0, self.SEND_LOOP):
            #self.do_SetConeState(F"{self.COLOR_WHITE} {self.BRIGHTNESS_LOW} {self.LIGHTMODE_CONT} 0 0")
            self.do_SetConeStates(F"{self.COLOR_WHITE} {self.BRIGHTNESS_LOW} {self.LIGHTMODE_CONT} 0 0 {self.COLOR_BLUE} {self.BRIGHTNESS_LOW} {self.LIGHTMODE_CONT} 0 0")
        
    def do_GW(self, line):
        '''Set Colors for one cone ID to green and then to white at high brightness. 
        '''
        for i in range(0, self.SEND_LOOP):
            #self.do_SetConeState(F"{self.COLOR_GREEN} {self.BRIGHTNESS_HIGH} {self.LIGHTMODE_CONT} 0 0")
            self.do_SetConeStates(F"{self.COLOR_GREEN} {self.BRIGHTNESS_HIGH} {self.LIGHTMODE_CONT} 0 0 {self.COLOR_BLUE} {self.BRIGHTNESS_HIGH} {self.LIGHTMODE_CONT} 0 0")
        time.sleep(self.GW_SLEEP)
        for i in range(0, self.SEND_LOOP):
            #self.do_SetConeState(F"{self.COLOR_WHITE} {self.BRIGHTNESS_HIGH} {self.LIGHTMODE_CONT} 0 0")
            self.do_SetConeStates(F"{self.COLOR_WHITE} {self.BRIGHTNESS_HIGH} {self.LIGHTMODE_CONT} 0 0 {self.COLOR_BLUE} {self.BRIGHTNESS_HIGH} {self.LIGHTMODE_CONT} 0 0")
        
    def do_RequestConeData(self, line):
        ''' Request Data from specific Cone. If no IP Address is given, broadcast address is used.        
        '''        
        self._networkif.sendDataRequestFrame(line)
        
    def do_RequestConeConfig(self, line):
        ''' Request Data from specific Cone. If no IP Address is given, broadcast address is used.        
        '''        
        self._networkif.sendConfigRequestFrame(line)
        
    def do_SetConeConfig(self, line):
        ''' Send Data tuples to Cone 
        
        Arguments (despite IP, all positional, int): IP key1 value1 [key2 value2 ...]'''
        ip, line = line.split(' ',1)
        data = [int(ele) for ele in line.split()]
        
        if((len(data) % 2)== 1):
            print("Error: Number of keys and values not matching.")
            return
        data_tuples = []
        
        for i in range(0,len(data),2):
            tuple = (data[0],data[1]);
            data_tuples.append(tuple)            
        
        self._networkif.sendConfigData(data_tuples,ip)
        
        
    def do_NumberAllCones(self, line):
        ''' Number all cones with the ID according to their serial number.  
        
            if a number is given as argument, set all cones to that number '''
        if(len(line)>0):
            id = int(line)
            self._networkif.sendConfigData([(3,id)])
        else:
            for i in range(1,100):
                try:
                    self._networkif.sendConfigData([(3,i),(13,0)],F"Night-cone-{i:06d}.local")
                    self._networkif.sendConfigData([(3,i),(13,0)],F"Night-cone-{i:06d}.local")
                    print(F"Successfully set Cone {i}", end="\r")
                except:
                    print(F"Failed to set Cone    {i}", end="\r")
                    pass
     
    def do_Rainbow(self, line):
        if(len(line)>0):
            max_id = int(line)
        else:
            max_id = 255
        cone_values = []
        for i in range(0,max_id):  
            data = [int(255*i/max_id),15,NightConesMessage.NightConesMessage.LightMode(6),10,int(255*i/max_id)]  
            cone_values.append(data)
        for i in range(1,10):
            self._send_data(cone_values)  
            time.sleep(0.1)
       
    def do_Test(self, line):
        cone_values=[[31,2,NightConesMessage.NightConesMessage.LightMode(1),10,0]]
        #cone_values = max_id*cone_values
        for i in range(1,100):
            self._send_data(cone_values)  
            time.sleep(0.1)
            
    def do_Demo(self, line):
        ''' Demo Programm to include all light modes
        
        '''
        br = 8
        max_id = 90
        cone_values = []
        sampling_time = 0.01;
        # Steady -------------------------------------------------
        print("Set Steady Colors")
        for color in [31, 96, 192, 255]:
            cone_values=[[color,br,NightConesMessage.NightConesMessage.LightMode(0),0,0]]*max_id
            #cone_values = max_id*cone_values
            for i in range(1,int(1/sampling_time)):
                self._send_data(cone_values)  
                time.sleep(sampling_time)
        # Flashing uniform 1 ------------------------------------------
        print("Flash with uniform color")
        for color in [31, 96, 192, 255]:
            cone_values=[[color,br,NightConesMessage.NightConesMessage.LightMode(1),10,0]]*max_id
            #cone_values = max_id*cone_values
            for i in range(1,int(1/sampling_time)):
                self._send_data(cone_values)  
                time.sleep(sampling_time)
        # Flashing uniform 2 25% ------------------------------------------
        print("Flash blue with 25% Duty")
        color = 31
        cone_values=[[color,br,NightConesMessage.NightConesMessage.LightMode(2),5,0]]*max_id
        #cone_values = max_id*cone_values
        for i in range(1,int(2/sampling_time)):
            self._send_data(cone_values)  
            time.sleep(sampling_time)
        
        # Rainbow Flashing outwards ------------------------------------------
        print("Flash in rainbow colors with increasing phaseshift")
        for phase in range(0,255,25):
            cone_values = []
            for i in range(0,max_id):  
                data = [int(255*i/max_id),br,NightConesMessage.NightConesMessage.LightMode(2),5,int(phase*i/max_id)]  
                cone_values.append(data)
            for i in range(1,int(1/sampling_time)):
                self._send_data(cone_values)  
                time.sleep(sampling_time)
                
         # Rainbow Fading inwards ------------------------------------------
        print("Fade in rainbow colors with decreasing phaseshift")
        for phase in range(255,0,-25):
            cone_values = []
            for i in range(0,max_id):  
                data = [int(255*i/max_id),br,NightConesMessage.NightConesMessage.LightMode(6),5,int(phase*i/max_id)]  
                cone_values.append(data)
            for i in range(1,int(1/sampling_time)):
                self._send_data(cone_values)  
                time.sleep(sampling_time)
                
        # circle single color ------------------------------------------
        print("Circulate with a single color with increasing speed")
        cone_values = []
        for i in range(0,max_id):  
            data = [color,br,NightConesMessage.NightConesMessage.LightMode(4),i+1,0]  
            cone_values.append(data)
        for i in range(1,int(5/sampling_time)):
            self._send_data(cone_values)  
            time.sleep(sampling_time)
            
        # circle smooth single color ------------------------------------------
        print("Smooth circling with a single color")
        cone_values = []
        for i in range(0,max_id):  
            data = [color,br,NightConesMessage.NightConesMessage.LightMode(5),i+1,0]  
            cone_values.append(data)
        for i in range(1,int(5/sampling_time)):
            self._send_data(cone_values)  
            time.sleep(sampling_time)
            
        # All Yellow ------------------------------------------
        print("Set all cones to yellow")
        cone_values = []
        for i in range(0,max_id):  
            data = [138,br,NightConesMessage.NightConesMessage.LightMode(0),0,0]  
            cone_values.append(data)
        for i in range(1,int(2/sampling_time)):
            self._send_data(cone_values)  
            time.sleep(sampling_time)
            
        # Ident------------------------------------------  
        print("Set Cone 27 to ident")
        data = [0,0,NightConesMessage.NightConesMessage.LightMode(9),0,0]  
        cone_values[27] = data
        for i in range(1,int(5/sampling_time)):
            self._send_data(cone_values)  
            time.sleep(sampling_time)
            
        # Turn down------------------------------------------   
        print("Set all cones to yellow on low brightness")
        cone_values=[[138,1,NightConesMessage.NightConesMessage.LightMode(0),0,0]]*max_id
        #cone_values = max_id*cone_values
        for i in range(1,int(2/sampling_time)):
            self._send_data(cone_values)  
            time.sleep(sampling_time)
        
        

        

        
    def do_State(self, line):
        ''' Request the state of all cones and report it, including the cones that are not connected.

        Arguments (optional): IDs to report, e.g. "3", "1,4,7", "10-20" or "1,4-6"
        '''
        if not self._check_rx():
            return
        try:
            ids = NightConesController.parse_ids(line) if line.strip() else None
        except ValueError as e:
            print(F"***Error: {e}")
            return
        responses = self._controller.request_states()
        if ids is not None:
            responses = {addr: data for addr, data in responses.items() if data.ID in ids}
        print(F"{len(responses)} cone(s) responded:")
        if responses:
            print("  Address              ID  Color          Bright  Mode               SoC  RSSI  Temp")
        for addr, data in sorted(responses.items(), key=lambda item: (item[1].ID, item[0])):
            print(F"  {NightConesController.format_addr(addr):<19} {data.ID:>3}  {NightConesController.format_color(data.Color):<13}  "
                  F"{data.Brightness:>6}  {NightConesController.format_mode(data.LightMode):<17} {data.SoC*100//255:>3}%  "
                  F"{NightConesController.signed(data.RSSI):>4}  {data.Temp:>3}°C")
        self._report_not_connected(responses, ids)

    def do_SetColor(self, line):
        ''' Set the color of single cone IDs or lists of IDs and verify that the cones changed.
        Cones that did not change are retried up to 3 times and reported in the end.

        Arguments: IDs Color [Brightness] [LightMode] [RepetitionTime] [Phase]
            IDs:        "3", "1,4,7", "10-20", "1,4-6" or "all" (all IDs that responded)
            Color:      0-255 or red, green, blue, white, yellow
            Brightness: 0-15 (default 15), LightMode: 0-9 (default 0), RepetitionTime, Phase: 0-255 (default 0)
        Example: SetColor 1,3,10-12 red 8
        '''
        args = line.split()
        if len(args) < 2 or len(args) > 6:
            print("***Error: Usage: SetColor IDs Color [Brightness] [LightMode] [RepetitionTime] [Phase]")
            return
        try:
            target = [NightConesController.parse_color(args[1]), self.BRIGHTNESS_HIGH, self.LIGHTMODE_CONT, 0, 0]
            for i, arg in enumerate(args[2:], start=1):
                target[i] = int(arg)
            target[1] = max(0, min(15, target[1]))
            target[2] = NightConesMessage.NightConesMessage.LightMode(target[2])
            target[3] = max(0, min(255, target[3]))
            target[4] = max(0, min(255, target[4]))
            if args[0].lower() == "all":
                if not self._check_rx():
                    return
                ids = sorted({data.ID for data in self._controller.request_states().values()})
                if not ids:
                    print("***Error: No cone responded, nothing to set")
                    return
            else:
                ids = NightConesController.parse_ids(args[0])
        except ValueError as e:
            print(F"***Error: {e}")
            return

        if not self._rx_active:
            print("RX Thread not active: sending without verification")
        result = self._controller.set_color(ids, target, lambda retry, pending:
            print(F"Retry {retry}/{NightConesController.SET_RETRIES} for ID(s) {NightConesController.format_ids(pending)}"))
        if result is None:
            return

        if result.changed:
            print(F"Changed: ID(s) {NightConesController.format_ids(result.changed)}")
        if result.wrong:
            print(F"NOT changed after {NightConesController.SET_RETRIES} retries ({len(result.wrong)} cone(s)), "
                  F"expected {NightConesController.format_color(target[0])} / brightness {target[1]} / "
                  F"{NightConesController.format_mode(target[2].value)}:")
            for addr, data in sorted(result.wrong.items(), key=lambda item: (item[1].ID, item[0])):
                print(F"  ID {data.ID:>3}  {NightConesController.format_addr(addr):<19} shows {NightConesController.format_color(data.Color)} / "
                      F"brightness {data.Brightness} / {NightConesController.format_mode(data.LightMode)}")
        if result.no_answer:
            print(F"No cone responded for ID(s) {NightConesController.format_ids(result.no_answer)}, change could not be verified")
        self._report_not_connected(result.responses, set(ids))

    def _check_rx(self):
        ''' Responses of the cones are only received if the RX Thread is active. '''
        if not self._rx_active:
            print("***Error: RX Thread not active. Restart the CLI and type 1 to activate the RX Thread.")
        return self._rx_active

    def _report_not_connected(self, responses, ids=None):
        ''' Report expected or previously seen cones (optionally only of the given IDs) that did not respond. '''
        missing = self._controller.not_connected(responses, ids)
        if not missing:
            print("All known cones are connected.")
            return
        print(F"Not connected ({len(missing)} cone(s)):")
        for addr, last in sorted(missing.items()):
            if last is None:
                print(F"  {NightConesController.format_addr(addr):<19} never seen")
            else:
                print(F"  {NightConesController.format_addr(addr):<19} ID {last[1].ID:>3}, last seen {datetime.fromtimestamp(last[0]).strftime('%H:%M:%S')}")

    def _print_message(self, message, addr):
        ''' Prints the packages received by the RX Thread.'''
        print(F"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}{addr} : {message}")

if __name__ == "__main__":
    NightConesCLI().cmdloop()     
