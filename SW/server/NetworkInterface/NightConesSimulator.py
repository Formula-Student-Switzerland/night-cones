import socket
import NightConesMessage


class NightConeSimulator:
   
    _ownIP = "127.0.0.1"
    _tx_port = None
    _rx_socket = None
    _NCMessage = NightConesMessage.NightConesMessage()
    
   
    def __init__(self, tx_port, rx_port):
        self._rx_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._rx_socket.bind((self._ownIP, rx_port))
        self._tx_port = tx_port
        self._rx_socket.settimeout(10)
    
    
    def start(self):
        ''' Thread that receives and handles messages '''
        MESSAGE = b"NC an Erde"
        data = b''
        while True:
            try:
                data, addr = self._rx_socket.recvfrom(1024) # buffer size is 1024 bytes
                message = self._NCMessage.unpackFrame(data)
                print("received message from %s: %s" % (addr, message))
            except KeyboardInterrupt:
                return
            except: 
                pass
            self._rx_socket.sendto(data, (self._ownIP, self._tx_port ))

if __name__ == "__main__":
   sim = NightConeSimulator(5006, 5005)
   sim.start()