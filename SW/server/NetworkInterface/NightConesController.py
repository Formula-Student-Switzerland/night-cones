''' Shared logic to request the state of the cones and to set their colors with verification.
Used by NightConesCLI and NightConesGUI. '''
import NetworkInterface
import ifaddr
import NightConesMessage
import threading
import time
from collections import namedtuple

LightMode = NightConesMessage.NightConesMessage.LightMode

UDP_TX_PORT = 5250
UDP_RX_PORT = 5251
CONE_PORT = 5250              # Source port cones send their responses from
COLOR_RED = 191
COLOR_GREEN = 95
COLOR_BLUE = 63
COLOR_WHITE = 255
COLOR_YELLOW = 127
COLOR_NAMES = {"red": COLOR_RED, "green": COLOR_GREEN, "blue": COLOR_BLUE,
               "white": COLOR_WHITE, "yellow": COLOR_YELLOW}
BRIGHTNESS_HIGH = 15
LIGHTMODE_CONT = 0
SKIDPAD_NOF = 72
EXITENTRY_NOF = 26
SKIDPAD_IP_START = 11
SKIDPAD_IP_STOP = SKIDPAD_IP_START + SKIDPAD_NOF - 1
EXITENTRY_IP_START = SKIDPAD_IP_STOP + 1
EXITENTRY_IP_STOP = EXITENTRY_IP_START + EXITENTRY_NOF - 1
IP_PREFIX = "192.168.0."
STATE_TIMEOUT = 1.0           # [s] Time to collect responses after a data request
SET_BURST = 5                 # Data frames sent per attempt when setting colors
SET_BURST_INTERVAL = 0.02     # [s] Time between frames of a burst
VERIFY_DELAY = 0.3            # [s] Time for the cones to apply a frame before verifying
SET_RETRIES = 3               # Retries for cones that did not change

# changed:   IDs that changed on all responding cones
# wrong:     {address: DataResponse} of cones that still show another state
# no_answer: IDs no cone responded for
# responses: {address: DataResponse} of the last state request
SetResult = namedtuple('SetResult', 'changed wrong no_answer responses')


class NightConesController:
    ''' Connects to the cone network, keeps track of the cones and sets their colors. '''

    def __init__(self, on_message=None):
        ''' on_message: called from the RX Thread with (message, addr) for every received frame,
                        except data responses collected by request_states. '''
        self.networkif = NetworkInterface.NetworkInterface()
        self.rx_active = False
        self.expected_ips = []
        self._on_message = on_message
        self._desired = {}          # Cone ID -> [Color, Brightness, LightMode, RepetitionTime, Phase] last sent
        self._known = {}            # Cone address -> (time, DataResponse) of the last response received
        self._known_lock = threading.Lock()
        self._collecting = False    # Data responses are not passed to on_message while collecting them

    @staticmethod
    def adapter_ips():
        ''' Returns a list of (adapter name, ifaddr.IP) of all IPv4 addresses '''
        return [(adapter.nice_name, ip) for adapter in ifaddr.get_adapters()
                for ip in adapter.ips if isinstance(ip.ip, str)]

    def connect(self, ip, tx_port=UDP_TX_PORT, rx_port=UDP_RX_PORT, rx_active=True):
        ''' ip: ifaddr.IP of the adapter connected to the cone network '''
        self.networkif.setCurrentNetwork(ip, tx_port, rx_port)
        # On the cone network, every IP of the skidpad/exit-entry range is expected to answer
        if str(ip.ip).startswith(IP_PREFIX):
            self.expected_ips = [F"{IP_PREFIX}{i}" for i in range(SKIDPAD_IP_START, EXITENTRY_IP_STOP+1)]
        self.rx_active = rx_active
        if rx_active:
            threading.Thread(target=self._rx_thread, daemon=True).start()

    def close(self):
        self.rx_active = False
        self.networkif._socket.close()

    def send_data(self, cone_values):
        ''' Send a data frame and remember the values sent for each cone ID. '''
        for cone_id, values in enumerate(cone_values):
            self._desired[cone_id] = list(values)
        self.networkif.sendDataFrame(cone_values)

    def request_states(self):
        ''' Broadcast a data request and return {address: DataResponse} of all cones that answered. '''
        self._collecting = True
        try:
            start = time.time()
            self.networkif.sendDataRequestFrame('')
            time.sleep(STATE_TIMEOUT)
        finally:
            self._collecting = False
        return {addr: data for addr, (rx_time, data) in self.known().items() if rx_time >= start}

    def known(self):
        ''' Returns {address: (time, DataResponse)} of the last response of every cone ever seen. '''
        with self._known_lock:
            return dict(self._known)

    def not_connected(self, responses, ids=None):
        ''' Returns {address: (time, DataResponse) or None if never seen} of all expected or previously
        seen cones (optionally only of the given IDs) that are not in responses. '''
        missing = {}
        if ids is None:
            for ip in self.expected_ips:
                missing[(ip, CONE_PORT)] = None
        for addr, last in self.known().items():
            if ids is None or last[1].ID in ids:
                missing[addr] = last
        for addr in responses:
            missing.pop(addr, None)
        return missing

    def set_color(self, ids, target, on_progress=None):
        ''' Set the given cone IDs to target and verify that the cones changed. IDs that did not change
        are retried up to SET_RETRIES times.

            ids:         list of cone IDs
            target:      [Color, Brightness, LightMode, RepetitionTime, Phase]
            on_progress: called with (retry, pending IDs) before each retry
        Returns a SetResult, or None if the RX Thread is not active and nothing could be verified. '''
        if not self.rx_active:
            for cone_id in ids:
                self._desired[cone_id] = list(target)
            self._send_burst()
            return None

        # The data frame always carries all IDs up to the highest one. IDs that were not set yet are
        # filled with the state the cones report, so they are not changed by accident.
        if not self.known():
            self.request_states()
        for _, data in self.known().values():
            if data.ID not in self._desired and data.LightMode <= 9:
                self._desired[data.ID] = [data.Color, data.Brightness, LightMode(data.LightMode), 0, 0]
        for cone_id in ids:
            self._desired[cone_id] = list(target)

        expected = (target[0], target[1], LightMode(target[2]).value)
        pending = set(ids)
        for attempt in range(SET_RETRIES + 1):
            if attempt > 0 and on_progress:
                on_progress(attempt, sorted(pending))
            self._send_burst()
            time.sleep(VERIFY_DELAY)
            responses = self.request_states()
            wrong = {addr: data for addr, data in responses.items()
                     if data.ID in ids and (data.Color, data.Brightness, data.LightMode) != expected}
            no_answer = set(ids) - {data.ID for data in responses.values()}
            pending = {data.ID for data in wrong.values()} | no_answer
            if not pending:
                break
        return SetResult(sorted(set(ids) - pending), wrong, sorted(no_answer), responses)

    def _send_burst(self):
        ''' Send the remembered state of all cone IDs. Unknown IDs in between are switched off. '''
        off = [COLOR_WHITE, 0, LightMode(LIGHTMODE_CONT), 0, 0]
        cone_values = [self._desired.get(i, off) for i in range(max(self._desired) + 1)]
        for i in range(SET_BURST):
            self.send_data(cone_values)
            time.sleep(SET_BURST_INTERVAL)

    def _rx_thread(self):
        ''' Receives all frames, keeps track of data responses and passes the frames to on_message. '''
        while self.rx_active:
            try:
                message, addr = self.networkif._rx_package()
                header, data = message
                is_status = header[1] == NightConesMessage.NightConesMessage._DATARESPONSE_FRAME
                if is_status:
                    with self._known_lock:
                        self._known[addr] = (time.time(), data)
                if self._on_message and not (is_status and self._collecting):
                    self._on_message(message, addr)
            except Exception:
                pass


def parse_ids(text):
    ''' Parse "3", "1,4,7", "10-20" or "1,4-6" into a sorted list of cone IDs. '''
    ids = set()
    try:
        for part in text.replace(' ', '').split(','):
            if '-' in part:
                first, last = part.split('-', 1)
                ids.update(range(int(first), int(last) + 1))
            elif part:
                ids.add(int(part))
    except ValueError:
        raise ValueError(F"Invalid cone IDs '{text}', use e.g. 3 or 1,4,7 or 10-20")
    if not ids or min(ids) < 0 or max(ids) > 255:
        raise ValueError(F"Invalid cone IDs '{text}', IDs must be between 0 and 255")
    return sorted(ids)


def parse_color(text):
    if text.lower() in COLOR_NAMES:
        return COLOR_NAMES[text.lower()]
    color = int(text)
    if not 0 <= color <= 255:
        raise ValueError(F"Color {color} not in range 0-255")
    return color


def format_ids(ids):
    ''' Format cone IDs compactly, e.g. [1,2,3,7] -> "1-3,7" '''
    ranges = []
    for cone_id in sorted(ids):
        if ranges and cone_id == ranges[-1][1] + 1:
            ranges[-1][1] = cone_id
        else:
            ranges.append([cone_id, cone_id])
    return ",".join(F"{a}" if a == b else F"{a}-{b}" for a, b in ranges)


def format_addr(addr):
    return addr[0] if addr[1] == CONE_PORT else F"{addr[0]}:{addr[1]}"


def format_color(color):
    names = [name for name, value in COLOR_NAMES.items() if value == color]
    return F"{color} ({names[0]})" if names else F"{color}"


def format_mode(mode):
    try:
        return F"{mode} {LightMode(mode).name}"
    except ValueError:
        return F"{mode}"


def signed(value):
    ''' The cones transmit the RSSI as unsigned byte '''
    return value - 256 if value > 127 else value


def color_to_rgb(color):
    ''' Returns the (r, g, b) the cone shows for a color at full brightness, see color_decode in the
    cone firmware (SW/client/src/color.cpp). '''
    if color < 32:
        red = (31 - color) / 32
    elif color < 96:
        red = 0
    elif color < 128:
        red = (color - 96) / 32
    else:
        red = 1
    if 64 <= color <= 127:
        green = 1
    elif 32 <= color <= 63:
        green = (color - 31) / 32
    elif 128 <= color <= 191:
        green = 1 - (color - 127) / 64
    elif color >= 224:
        green = (color - 223) / 32
    else:
        green = 0
    if color <= 63 or color >= 224:
        blue = 1
    elif color <= 95:
        blue = (96 - color) / 32
    elif color >= 192:
        blue = (color - 191) / 32
    else:
        blue = 0
    scale = 255 / max(red, green, blue)
    return (int(red * scale), int(green * scale), int(blue * scale))
