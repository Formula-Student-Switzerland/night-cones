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
    4-7	    4 Byte	Reserved
    8-15	8 Byte	Timestamp (The current UNIX Timestamp to synchronize the cones (ms).)
    '''
    _HEADER_STRING = "BBBxxxxxQ"
    _VERSION = 1;
    
    ''' Frame Types
        Host to Client Types'''
    _DATA_FRAME = 0	#Data Frame with current color data
    _CONFIG_FRAME = 1	#Config Frame for setting various parameters on the cone
    _DATAREQUEST_FRAME = 2	#Data Request frame to request data from any cone it is sent to. 

    '''Client to Host Types'''
    _DATARESPONSE_FRAME = 128	#Data Request Response from cone to Host


    '''
    Data Frame Definition
    16	1 Byte	Color (Encoding: see below)
    17	4 Bit	Brightness
    17	4 Bit 	Light mode
    18	1 Byte	Repetition time [x100ms]
    19	1 Byte	Phase shift (0..255 scaled through repetition time)
            
    20	1 Byte	Color (Cone 1)
    21	4 Bit	Brightness (Cone 1)
    21	4 Bit	Light mode (Cone 1)    
    22	1 Byte	Repetition time [x100ms] (Cone 1)
    23	1 Byte	Phase shift (0..255 scaled through repetition time) (Cone 1)

'''
    _DATA_FRAME_DEFINITION = "BBBB"
    _dataframecounter = 0
    
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
    
    
    
    def unpackFrame(self, frame) :
        ''' frame: byte array of the message
        
        Unpacks a frame received from the network interface '''
        header = struct.unpack(self._HEADER_STRING, frame[0:16])
        match header[1]:
            case self._DATA_FRAME:
                data_list = []
                for i in range(16,len(frame),4):
                    temp = struct.unpack(self._DATA_FRAME_DEFINITION,frame[i:i+4])
                    brightness = temp[1]>>4
                    lightmode_temp = self.LightMode(temp[1] & 0xF)
                    data_list.append((temp[0],brightness, lightmode_temp,temp[2],temp[3]))
                return (header,data_list)
                
            case self._CONFIG_FRAME:
                raise NotImplementedError
            case self._DATAREQUEST_FRAME:
                raise NotImplementedError
            case self._DATARESPONSE_FRAME:
                raise NotImplementedError
    
            # If an exact match is not confirmed, this last case will be used if provided
            case _:
                return "Something's wrong with the internet"    
    
    
    
    
    def packDataFrame(self, data):
        ''' data: List of Cone States consisting of (Color:int, Brightness:int, LightMode:LightMode, Frequency:int, phase:int)
        
        Packs a data frame as specified in the documentation.'''
        frame = struct.pack(self._HEADER_STRING,self._VERSION, self._DATA_FRAME, self._dataframecounter,int(time.time() * 1000))
        
        for i in range(0,len(data)):
            byte1 = data[i][1]<<4 + int(data[i][2].value)&0xF
            frame += (struct.pack(self._DATA_FRAME_DEFINITION,data[i][0], byte1, data[i][3],data[i][4]))
    
        self._dataframecounter = self._dataframecounter + 1;
        return frame
    



