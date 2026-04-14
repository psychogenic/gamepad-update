class PinMapTT06:
    '''
        TT06/7/8 Pin mapping
    '''
    ResetPin = 1 # prj rst
    GoPin = 0 # prj clk
    SWDPin = 12 # in 3
    LEDPins = [5, 6, 7, 8] # out low nibble
    
    GPLatchPin = 17 # in4
    GPClockPin = 18 # in5
    GPDataPin = 19 # in6
    
    BidirPinsStart = 21 # uio0
    
class PinMapTTETR:
    '''
        ETR demoboard pin mapping
    '''
    ResetPin = 14 # prj rst
    GoPin = 16 # prj clk
    SWDPin = 20 # in 3
    LEDPins = [33, 34, 35, 36] # out low nibble
    
    GPLatchPin = 21 # in4
    GPClockPin = 22 # in5
    GPDataPin = 23 # in6

    BidirPinsStart = 25 # uio0
    
# selected pin mapping default
PinMapSelected = PinMapTTETR




