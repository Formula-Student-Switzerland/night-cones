import socket
import NightConesMessage
import random

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
            #try:
                data, addr = self._rx_socket.recvfrom(1024) # buffer size is 1024 bytes
                header,message = self._NCMessage.unpackFrame(data)
                print("received message from %s: %s" % (addr, (header,message)))
                if(header is not None and header[1] == self._NCMessage._DATAREQUEST_FRAME):
                    dataresponse = self._NCMessage.DATARESPONSE_TUPLE(0, random.randrange(0, 255, 3), random.randrange(0, 255, 3),
                        (random.randrange(0, 255, 3), random.randrange(0, 255, 3), random.randrange(0, 255, 3), random.randrange(0, 255, 3), random.randrange(0, 255, 3), random.randrange(0, 255, 3)),
                        random.randrange(0, 65535, 3), 
                        random.randrange(0, 255, 3), 
                        random.randrange(0, 1, 1))
                    print("Return Data Response: %s"%str(dataresponse))
                    self._rx_socket.sendto(self._NCMessage.packDataResponseFrame(dataresponse), (self._ownIP, self._tx_port ))
                
            except KeyboardInterrupt:
                return
            except: 
                pass
            
if __name__ == "__main__":
   sim = NightConeSimulator(5006, 5005)
   sim.start()