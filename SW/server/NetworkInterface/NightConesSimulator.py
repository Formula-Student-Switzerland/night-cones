import argparse
import socket
import NightConesMessage
import random
import time

class NightConeSimulator:
    ''' Simulates several cones on localhost. Each cone answers from its own port, so the CLI
    sees them as separate cones. '''

    _ownIP = "127.0.0.1"
    _tx_port = None
    _rx_socket = None
    _NCMessage = NightConesMessage.NightConesMessage()


    def __init__(self, tx_port, rx_port, cone_ids, drop_rate=0.0, offline=0, stuck=0, drop_out=0, verbose=True):
        ''' cone_ids:  Cone ID of each simulated cone (IDs may repeat)
            drop_rate: Probability that a cone ignores a data frame
            offline:   Number of cones that never answer (the last ones)
            stuck:     Number of cones that never change their color (the first ones)
            drop_out:  Number of cones that answer the first request only (the ones before the offline ones)
            verbose:   Print all received messages'''
        self._rx_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._rx_socket.bind((self._ownIP, rx_port))
        self._tx_port = tx_port
        self._rx_socket.settimeout(1)
        self._running = False
        self._verbose = verbose
        self._NCMessage.ZeroTime = time.time()*1000
        self._drop_rate = drop_rate
        self._cones = []
        for i, cone_id in enumerate(cone_ids):
            tx_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            tx_socket.bind((self._ownIP, 0))
            self._cones.append({"id": cone_id, "socket": tx_socket, "color": 0, "brightness": 0, "mode": 0,
                                "online": i < len(cone_ids) - offline, "stuck": i < stuck,
                                "drop_out": len(cone_ids) - offline - drop_out <= i < len(cone_ids) - offline})
            if verbose:
                print("Cone ID %d on port %d%s%s" % (cone_id, tx_socket.getsockname()[1],
                            "" if self._cones[-1]["online"] else " (offline)", " (stuck)" if self._cones[-1]["stuck"] else "")
                      + (" (drops out)" if self._cones[-1]["drop_out"] else ""))


    def start(self):
        ''' Thread that receives and handles messages '''
        self._running = True
        while self._running:
            try:
                data, addr = self._rx_socket.recvfrom(1024) # buffer size is 1024 bytes
                header,message = self._NCMessage.unpackFrame(data)
                if self._verbose:
                    print("received message from %s: %s" % (addr, (header,message)))
                for cone in self._cones:
                    if not cone["online"]:
                        continue
                    if header[1] == self._NCMessage._DATA_FRAME:
                        if cone["id"] < len(message) and not cone["stuck"] and random.random() >= self._drop_rate:
                            cone["color"] = message[cone["id"]].Color
                            cone["brightness"] = message[cone["id"]].Brightness
                            cone["mode"] = message[cone["id"]].LightMode.value
                    elif header[1] == self._NCMessage._DATAREQUEST_FRAME:
                        dataresponse = self._NCMessage.DATARESPONSE_TUPLE(cone["id"], random.randrange(0, 255), random.randrange(180, 220),
                            random.randrange(20, 40), 0, cone["color"], cone["brightness"], cone["mode"])
                        cone["socket"].sendto(self._NCMessage.packDataResponseFrame(dataresponse), (self._ownIP, self._tx_port))
                        if cone["drop_out"]:
                            cone["online"] = False

            except KeyboardInterrupt:
                return
            except socket.timeout:
                pass
            except OSError:
                if self._running:
                    raise

    def stop(self):
        ''' Stops start() and closes all sockets '''
        self._running = False
        self._rx_socket.close()
        for cone in self._cones:
            cone["socket"].close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=NightConeSimulator.__doc__)
    parser.add_argument("--tx-port", type=int, default=5251, help="Port of the CLI to answer to")
    parser.add_argument("--rx-port", type=int, default=5250, help="Port to receive frames on")
    parser.add_argument("--ids", default="0,1,2,3", help="Comma separated cone ID of each simulated cone")
    parser.add_argument("--drop-rate", type=float, default=0.0, help="Probability that a cone ignores a data frame")
    parser.add_argument("--offline", type=int, default=0, help="Number of cones that never answer")
    parser.add_argument("--stuck", type=int, default=0, help="Number of cones that never change color")
    parser.add_argument("--drop-out", type=int, default=0, help="Number of cones that answer the first request only")
    args = parser.parse_args()
    sim = NightConeSimulator(args.tx_port, args.rx_port, [int(i) for i in args.ids.split(",")],
                             args.drop_rate, args.offline, args.stuck, args.drop_out)
    sim.start()
