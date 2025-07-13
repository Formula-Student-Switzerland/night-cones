from collections import namedtuple
from enum import Enum
import struct
import time




class NightConesMessage:
    ''' Class defining all Frames used for NightCones communication'''    
    
    ''' Header Definition
    Byte	Size	Usage
    0	    1 Byte	Version (currently only 1 is supported
    1	    1 Byte	Frame Type
    2	    1 Byte	Frame Number (The frame number is used for frame type 0 to identifiy lost packets. The 8-bit overflowing counter is incremented with every frame. )
    3	    1 Byte	Reserve
    4-7	    4 Byte	Timestamp (The current UNIX Timestamp to synchronize the cones (ms).)
    '''
    _HEADER_STRING = "BBBxI"
    _HEADER_LENGTH = 8
    _VERSION = 1;
    
    ''' Frame Types
        Host to Client Types'''
    _DATA_FRAME = 0	#Data Frame with current color data
    _CONFIG_FRAME = 1	#Config Frame for setting various parameters on the cone
    _DATAREQUEST_FRAME = 3	#Data Request frame to request data from any cone it is sent to. 
    _CONFIGREQUEST_FRAME = 2	#Data Request frame to request data from any cone it is sent to. 

    '''Client to Host Types'''
    _DATARESPONSE_FRAME = 128	#Data Request Response from cone to Host
    _CONFIGRESPONSE_FRAME = 129	#Config Request Response


    '''
    Data Frame Definition
    8 	1 Byte	Color (Encoding: see below)
    9 	4 Bit	Brightness
    9	4 Bit 	Light mode
    10	1 Byte	Repetition time [x100ms]
    11	1 Byte	Phase shift (0..255 scaled through repetition time)
            
    12	1 Byte	Color (Cone 1)
    13	4 Bit	Brightness (Cone 1)
    13	4 Bit	Light mode (Cone 1)    
    14	1 Byte	Repetition time [x100ms] (Cone 1)
    15	1 Byte	Phase shift (0..255 scaled through repetition time) (Cone 1)

'''
    _DATA_FRAME_DEFINITION = "BBBB"
    _dataframecounter = 0
    DATA_TUPLE = namedtuple('DataFrame', 'Color Brightness LightMode RepetitionTime Phase')
    
    class LightMode(Enum):
        ''' Enumeration for all Light Modes
                    Int	    Mode	        Description	                                Color interpretation	Brightness interpretation	Repetition time interpretation'''
        Continuous = 0	    # Continuous	Continuous light, no blinking whatsoever	Yes	                    Yes	                        Don’t care
        Blinking = 1	    # Blinking	    Blinking with duty cycle 50 %	            Yes	                    Yes	                        Blinking time (0.1 s .. 25.5 s)
        BlinkingShort = 2	# Blinking shortBlinking with duty cycle 25 %	            Yes	                    Yes	                        Blinking time (0.1 s .. 25.5 s)
        BlinkingLong = 3	# Blinking long	Blinking with duty cycle 75 %	            Yes	                    Yes	                        Blinking time (0.1 s .. 25.5 s)
        Circulating = 4	    # Circulating	Circulating light. Bottom LEDs 3 at a time. Yes	                    Yes	                        Rotation time (0.1 s .. 25.5 s)
        CirculatingSmooth=5	# Circulating smooth	Circulating light.                  Yes	                    Brightness b of middle LED	Rotation time (0.1 s .. 25.5 s)
        Fade=6              # Fade	Single color, brightness fades between zero to max	Yes	                    Maximum brightness	        Fade cycle time (0.1 s .. 25.5 s)
        RainbowFade=7       # Rainbow fade	Continuous light, color fades in rainbow 	Don’t care	            Yes	                        Fade cycle time (0.1 s .. 25.5 s)
        RainbowCircle=8     # Rainbow circle	rainbow dircling aroundDon’t            Don’t care	            Yes	                        Rotation time (0.1 s .. 25.5 s)
        Identification = 9  # Identification	Blinking with duty cycle 50 %, 2 Hz 	Don’t care	            Don’t care	                Don’t care
    
    _REPETITION_GAIN = 100 #ms   
    
    '''
    Cone Data Response Definition
    Byte	Size	Usage (description below)
    0-7	8 Byte	Header

    8-9	2 Byte	ID
    10	    1 Byte	SoC (0 → 0%, 255 → 100%)
    11	    1 Byte	RSSI
    12      1 Byte Temperature
    13	    1 Byte 	Hall Sensor State
    '''
    
    _DATA_RESPONSE_DEFINITION = "HBBbBxx"
    DATARESPONSE_TUPLE = namedtuple('DataResponse', 'ID SoC RSSI Temp Hall')
    
    '''
    Config Responste Frame Definition
    Byte	Size	Usage (description below)
    0-7	8 Byte	Header
            
    8-11	4 Byte	Parameter ID
    12-15	4 Byte	Value
    ...	
    '''
    _CONFIGRESPONSE_FRAME_ENTRY_DEFINITION = "I"
    
    '''
    Config Frame Definition
    Byte	Size	Usage (description below)
    0-7	8 Byte	Header
            
    8-11	4 Byte	Parameter ID
    12-15	4 Byte	Value
'''
    _CONFIGFRAME_FRAME_ENTRY_DEFINITION = "Ii"
    
    def unpackFrame(self, frame) :
        ''' frame: byte array of the message
        
        Unpacks a frame received from the network interface '''

        header = struct.unpack(self._HEADER_STRING, frame[0:self._HEADER_LENGTH])
        match header[1]:
            case self._DATA_FRAME:
                datalist = []
                for i in range(self._HEADER_LENGTH,len(frame),4):
                    temp = struct.unpack(self._DATA_FRAME_DEFINITION,frame[i:i+4])
                    brightness = temp[1]>>4
                    lightmode_temp = self.LightMode(temp[1] & 0xF)
                    datalist.append(self.DATA_TUPLE(temp[0],brightness, lightmode_temp,temp[2],temp[3]))
                return (header,datalist)
                
            case self._CONFIG_FRAME:
                raise NotImplementedError
            case self._CONFIGRESPONSE_FRAME:
                datalist = []
                for i in range(self._HEADER_LENGTH,len(frame),4):
                    value = struct.unpack(self._CONFIGRESPONSE_FRAME_ENTRY_DEFINITION,frame[i:i+4])
                    datalist.append(value[0]) 
                return (header, datalist)
                
            case self._CONFIGREQUEST_FRAME:
                raise NotImplementedError;
                return (header,'')
            case self._DATAREQUEST_FRAME:
                raise NotImplementedError;
                return (header,'')
            case self._DATARESPONSE_FRAME:
                temp = struct.unpack(self._DATA_RESPONSE_DEFINITION,frame[self._HEADER_LENGTH:])        
                data=self.DATARESPONSE_TUPLE(temp[0],temp[1],temp[2],temp[3],temp[4])
                return (header,data)
                
    
            # If an exact match is not confirmed, this last case will be used if provided
            case _:
                return "Something's wrong with the internet"    
    
    
    
    
    def packDataFrame(self, data):
        ''' data: List of Cone States consisting of (Color:int, Brightness:int, LightMode:LightMode, Frequency:int, phase:int)
        
        Packs a data frame as specified in the documentation.'''
        frame = struct.pack(self._HEADER_STRING,self._VERSION, self._DATA_FRAME, self._dataframecounter,int(time.time()*1000.0 - self.ZeroTime))

        for i in range(0,len(data)):
            byte1 = (data[i][1]<<4)+ (int(data[i][2].value)&0xF)
            frame += (struct.pack(self._DATA_FRAME_DEFINITION,data[i][0], byte1, data[i][3],data[i][4]))

        self._dataframecounter = (self._dataframecounter + 1)%256;
        return frame
    
    def packConfigFrame(self,datatuples):
        frame = struct.pack(self._HEADER_STRING,self._VERSION, self._CONFIG_FRAME, 0,int(time.time() * 1000 - self.ZeroTime))
        for tuple in datatuples:
            frame = frame + struct.pack(self._CONFIGFRAME_FRAME_ENTRY_DEFINITION, tuple[0], tuple[1])
        return frame
        
        
    def packConfigRequestFrame(self):
        ''' Creates a Config Request frame.'''
        frame = struct.pack(self._HEADER_STRING,self._VERSION, self._CONFIGREQUEST_FRAME, 0,int(time.time() * 1000 - self.ZeroTime))
        return frame
        
    #def packConfigResponseFrame(self,datalist):
    #    ''' datalist: List of parameter values (4 byte int)
    #    
    #    Creates a Config Response Frame'''
    #    frame = struct.pack(self._HEADER_STRING,self._VERSION, self._CONFIG_FRAME, 0,int(time.time() * 1000))
    #    frame += struct.pack(self._CONFIGRESPONSE_FRAME_SUBHEADER_DEFINITION,len(datalist))
    #    for el in datalist:
    #        frame += struct.pack(self._CONFIGRESPONSE_FRAME_ENTRY_DEFINITION, el)
            
    def packDataRequestFrame(self):
        ''' Creates a Data Request frame.'''
        frame = struct.pack(self._HEADER_STRING,self._VERSION, self._DATAREQUEST_FRAME, 0,int(time.time() * 1000 - self.ZeroTime))
        return frame
    
    def packDataResponseFrame(self,data):
        ''' data: DATARESPONSE_TUPLE of Data
        Creates a Data Response frame.'''
        frame = struct.pack(self._HEADER_STRING,self._VERSION, self._DATARESPONSE_FRAME, 0,int(time.time() * 1000 - self.ZeroTime))
        frame += struct.pack(self._DATA_RESPONSE_DEFINITION, data[0],  data[1], data[2], data[3][0], data[3][1], data[3][2], data[3][3], data[3][4], data[3][5], data[4], data[5], data[6])
        return frame



