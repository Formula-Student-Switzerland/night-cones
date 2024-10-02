import ifaddr
import socket
import NightConesMessage
import ipaddress


class NetworkInterface:
    ''' This class is used to interface with nightcones over a network interface. '''
    _currentAdapter = ''
    _currentIP = '127.0.0.1'
    _UDP_TX_PORT = 5005
    _UDP_RX_PORT = 5006
    _socket = None
    _NCMessage = NightConesMessage.NightConesMessage()
    
    def __init__(self):
        
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        self._socket.settimeout(10)
        pass
        
    def getAdpaterList(self):
        ''' return list of ifaddr.Adapter
        
        Discovers all available adapters'''
        adapters = ifaddr.get_adapters()
        return adapters        
        
    def setCurrentNetwork(self,ipaddr, tx_port, rx_port):
        ''' Set the current IP Subnet for this class to operate on'''
        net = ipaddress.IPv4Network(ipaddr.ip + '/' + str(ipaddr.network_prefix), False)
        if(ipaddr.ip == "127.0.0.1"):
            self._currentIP = "127.0.0.1"
        else:      
            self._currentIP = str(net.broadcast_address)  
        print('Configured for Address:', str(ipaddr.ip)) 
        print('Using Port %d for TX and %d for RX'%(tx_port,rx_port))
        self._UDP_TX_PORT = tx_port
        self._UDP_RX_PORT = rx_port
        self._socket.bind((str(ipaddr.ip), self._UDP_RX_PORT)) 
        print('Configured for Address:', str(net.network_address)) 
        print('Using Port %d for TX and %d for RX'%(tx_port,rx_port))
        
    def _rx_package(self):
        ''' Receives a package and prints it to the console '''
        try:
            data, addr = self._socket.recvfrom(1024) # buffer size is 1024 bytes
            message = self._NCMessage.unpackFrame(data)
            print("Decoded: ")
            print(message)
        except: 
            #print("RX Error")
            pass
    
        
    def sendDataFrame(self,data):
        '''  data: List of tuple with (Color, Brightness, LightMode, Frequency, phase)
        Sends a DATA Frame with the settings provided.
        
        '''
        frame = self._NCMessage.packDataFrame(data)
        self._socket.sendto(frame, (self._currentIP, self._UDP_TX_PORT));
   
    def sendConfigData(self, ip, data_tuple):
        raise NotImplementedError;
   
    def sendConfigRequestFrame(self, ip):
        ''' Request Config Data from specified Cone. Send to Broadcast, if no IP is given. '''
        if(ip == ''):
            ip = self._currentIP;
        frame = self._NCMessage.packConfigRequestFrame()
        self._socket.sendto(frame, (ip, self._UDP_TX_PORT));      
        
    def sendDataRequestFrame(self, ip):
        ''' Request Data from specified Cone. Send to Broadcast, if no IP is given.'''
        if(ip == ''):
            ip = self._currentIP;
        frame = self._NCMessage.packDataRequestFrame()
        self._socket.sendto(frame, (ip, self._UDP_TX_PORT));      
   
if __name__ == "__main__":
    ''' This is only for testing purpose. Do not use as script'''
    networkif = NetworkInterface()
    data = [(100,11, NightConesMessage.NightConesMessage.LightMode.Blinking,10,0)];
    print(data)
    for i in range (0,10):
        networkif.sendDataFrame(data)
    networkif._rx_package()