import NetworkInterface
import NightConesMessage
import cmd
#import readline
import threading
from datetime import datetime
import time

class NightConesCLI(cmd.Cmd):
    
    _UDP_TX_PORT = 5250
    _UDP_RX_PORT = 5251  
    prompt = '>> '
    intro = 'Welcome to the Nightcones CLI. Type "help" for available commands.'
    
    def preloop(self):
        ''' Gets Executed before starting the CLI'''
        self._networkif = NetworkInterface.NetworkInterface()
    
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
            self._networkif.setCurrentNetwork(ip_adresses[int(ip_select)],int(tx_port),int(rx_port))
        else: 
            print("No valid selection, terminating tool")
            exit()
            
        if(self._rx_active == True):
            print("Starting RX Thread")
            thread = threading.Thread(target = self._rx_thread)
            thread.start()
            
    def do_hello(self, line):
        """Print a greeting."""
        print("Hello, World!")

    def do_quit(self, line):
        """Exit the CLI."""
        self._rx_active = False
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
            
        self._networkif.sendDataFrame([data])  
        
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
            
        self._networkif.sendDataFrame(cone_values)  
        
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
            self._networkif.sendDataFrame(cone_values)  
            time.sleep(0.1)
       
    def do_Test(self, line):
        cone_values=[[31,2,NightConesMessage.NightConesMessage.LightMode(1),10,0]]
        #cone_values = max_id*cone_values
        for i in range(1,100):
            self._networkif.sendDataFrame(cone_values)  
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
                self._networkif.sendDataFrame(cone_values)  
                time.sleep(sampling_time)
        # Flashing uniform 1 ------------------------------------------
        print("Flash with uniform color")
        for color in [31, 96, 192, 255]:
            cone_values=[[color,br,NightConesMessage.NightConesMessage.LightMode(1),10,0]]*max_id
            #cone_values = max_id*cone_values
            for i in range(1,int(1/sampling_time)):
                self._networkif.sendDataFrame(cone_values)  
                time.sleep(sampling_time)
        # Flashing uniform 2 25% ------------------------------------------
        print("Flash blue with 25% Duty")
        color = 31
        cone_values=[[color,br,NightConesMessage.NightConesMessage.LightMode(2),5,0]]*max_id
        #cone_values = max_id*cone_values
        for i in range(1,int(2/sampling_time)):
            self._networkif.sendDataFrame(cone_values)  
            time.sleep(sampling_time)
        
        # Rainbow Flashing outwards ------------------------------------------
        print("Flash in rainbow colors with increasing phaseshift")
        for phase in range(0,255,25):
            cone_values = []
            for i in range(0,max_id):  
                data = [int(255*i/max_id),br,NightConesMessage.NightConesMessage.LightMode(2),5,int(phase*i/max_id)]  
                cone_values.append(data)
            for i in range(1,int(1/sampling_time)):
                self._networkif.sendDataFrame(cone_values)  
                time.sleep(sampling_time)
                
         # Rainbow Fading inwards ------------------------------------------
        print("Fade in rainbow colors with decreasing phaseshift")
        for phase in range(255,0,-25):
            cone_values = []
            for i in range(0,max_id):  
                data = [int(255*i/max_id),br,NightConesMessage.NightConesMessage.LightMode(6),5,int(phase*i/max_id)]  
                cone_values.append(data)
            for i in range(1,int(1/sampling_time)):
                self._networkif.sendDataFrame(cone_values)  
                time.sleep(sampling_time)
                
        # circle single color ------------------------------------------
        print("Circulate with a single color with increasing speed")
        cone_values = []
        for i in range(0,max_id):  
            data = [color,br,NightConesMessage.NightConesMessage.LightMode(4),i+1,0]  
            cone_values.append(data)
        for i in range(1,int(5/sampling_time)):
            self._networkif.sendDataFrame(cone_values)  
            time.sleep(sampling_time)
            
        # circle smooth single color ------------------------------------------
        print("Smooth circling with a single color")
        cone_values = []
        for i in range(0,max_id):  
            data = [color,br,NightConesMessage.NightConesMessage.LightMode(5),i+1,0]  
            cone_values.append(data)
        for i in range(1,int(5/sampling_time)):
            self._networkif.sendDataFrame(cone_values)  
            time.sleep(sampling_time)
            
        # All Yellow ------------------------------------------
        print("Set all cones to yellow")
        cone_values = []
        for i in range(0,max_id):  
            data = [138,br,NightConesMessage.NightConesMessage.LightMode(0),0,0]  
            cone_values.append(data)
        for i in range(1,int(2/sampling_time)):
            self._networkif.sendDataFrame(cone_values)  
            time.sleep(sampling_time)
            
        # Ident------------------------------------------  
        print("Set Cone 27 to ident")
        data = [0,0,NightConesMessage.NightConesMessage.LightMode(9),0,0]  
        cone_values[27] = data
        for i in range(1,int(5/sampling_time)):
            self._networkif.sendDataFrame(cone_values)  
            time.sleep(sampling_time)
            
        # Turn down------------------------------------------   
        print("Set all cones to yellow on low brightness")
        cone_values=[[138,1,NightConesMessage.NightConesMessage.LightMode(0),0,0]]*max_id
        #cone_values = max_id*cone_values
        for i in range(1,int(2/sampling_time)):
            self._networkif.sendDataFrame(cone_values)  
            time.sleep(sampling_time)
        
        

        

        
    def _rx_thread(self):
        ''' Runs the RX Function to print received packages.'''
        while self._rx_active:
            try:
                message,addr = self._networkif._rx_package()
                print(F"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}{addr} : {message}")
            except Exception as e: 
                #print(e)                
                pass

if __name__ == "__main__":
    NightConesCLI().cmdloop()     