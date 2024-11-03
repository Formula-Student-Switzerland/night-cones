import NetworkInterface
import NightConesMessage
import cmd
#import readline
import threading

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
        if(ip_select.isdigit() and int(ip_select)<ip_index):
            self._networkif.setCurrentNetwork(ip_adresses[int(ip_select)],int(tx_port),int(rx_port))
        else: 
            print("No valid selection, terminating tool")
            exit()
        self._rx_active = True
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
        '''Set Colors for one cone ID. If no arguments are supplied, they will be prompted
        
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
        
    def do_SendConeConfig(self, line):
        ''' Send Data tuples to Cone 
        
        Arguments (despite IP, all positional, int): IP key1 value1 [key2 value2 ...]'''
        ip, line = line.split(' ',1)
        print(ip, line)
        data = [int(ele) for ele in line.split()]
        
        print(ip, data)
        if((len(data) % 2)== 1):
            print("Error: Number of keys and values not matching.")
            return
        data_tuples = []
        
        for i in range(0,len(data),2):
            tuple = (data[0],data[1]);
            data_tuples.append(tuple)            
        
        print(ip, data_tuples)
        self._networkif.sendConfigData(ip,data_tuples)
        
        
    def _rx_thread(self):
        ''' Runs the RX Function to print received packages.'''
        while self._rx_active:
            try:
                message,addr = self._networkif._rx_package()
                print(F"{addr} : {message}")
            except:
                pass

if __name__ == "__main__":
    NightConesCLI().cmdloop()     