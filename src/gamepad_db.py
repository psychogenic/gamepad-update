'''
Demoboard and support classes

@author: Pat Deegan
@copyright: Copyright (C) 2025 Pat Deegan, https://psychogenic.com
'''

import machine
import micropython
import rp2
import gc
from pico_ch32v003_prog.flash_ch32v003 import CH32_Flash
from sipo_reader import SIPO
from gamepad_mem import flush_mem



GamepadSWDGPIO = 12

class BareDemoboard:
    
    ResetPin = 1
    GoPin = 0
    SWDPin = GamepadSWDGPIO
    LEDPins = [5, 6, 7, 8]
    
    GPLatchPin = 17
    GPClockPin = 18
    GPDataPin = 19
    
    def __init__(self):
        flush_mem("DB 1 mem")
        self.triggered_go = False 
        self.triggered_reset = False
        self.pin_reset =  machine.Pin(self.ResetPin, machine.Pin.IN)
        self.pin_go = machine.Pin(self.GoPin, machine.Pin.IN)
        
        self.pin_reset.irq(trigger=machine.Pin.IRQ_FALLING, handler=self.reset_isr)
        self.pin_go.irq(trigger=machine.Pin.IRQ_RISING, handler=self.go_isr)
        
        self.out_pins = []
        for lp in self.LEDPins:
            op = machine.Pin(lp, machine.Pin.OUT)
            self.out_pins.append(op)
            
        flush_mem("DB 2 mem")
        self._flasher = None
        # self.gamepad = GamepadReader(self.GPDataPin, self.GPClockPin, self.GPLatchPin)
        flush_mem("DB 3 mem")
        self._gamepad = None
        flush_mem("DB 3 mem")
        
        # print(self.flasher)
        # print(self.gamepad)
        
        
    def set_output(self, nibble:int):
        for i in range(len(self.LEDPins)):
            self.out_pins[i].value(1 if nibble & (1<<i) else 0)
        
    def go_isr(self, p):
        self.triggered_go = True 
        
    def reset_isr(self, p):
        self.triggered_reset = True 
        
    def request_handled(self):
        self.triggered_go = False 
        self.triggered_reset = False

    @property 
    def flasher(self):
        flush_mem("DB FLSH 1 mem")
        if self._flasher is None:
            self._flasher = CH32_Flash(GamepadSWDGPIO, map_to_port=False)
            
        flush_mem("DB FLSH 2 mem")
        return self._flasher
    
    
    def flasher_release(self):
        flush_mem("DB FLSH 2 mem")
        if self._flasher is not None:
            self._flasher.deinit()
            self._flasher = None 
            flush_mem("flasher deinit done")
    
    @property 
    def gamepad(self):
        if self._gamepad is None:
            flush_mem("DB GP 1 mem")
            self._gamepad = SIPO(self.GPDataPin, self.GPClockPin, self.GPLatchPin)
            flush_mem("DB GP 2 mem")
            
        return self._gamepad 


class GamepadReader:
    def __init__(self, dat:int, clk:int, latch:int):
        self.pin_data =  machine.Pin(dat, machine.Pin.IN)
        self.pin_clock = machine.Pin(clk, machine.Pin.IN)
        self.pin_latch = machine.Pin(latch, machine.Pin.IN)
        
        self._current_bits = 0
        
        self._captured_packet = 0
        self._last_packet = 0
        self._new_packet = False 
        
        
        
        self.pin_clock.irq(trigger=machine.Pin.IRQ_RISING, handler=self.isr_clk, hard=True)
        self.pin_latch.irq(trigger=machine.Pin.IRQ_RISING, handler=self.isr_latch, hard=True)
        
    def enable(self):
        pass 
    
    def disable(self):
        pass 
    
    @property 
    def new_packet(self):
        np = self._new_packet
        self._new_packet = False 
        return np
    
    @property 
    def changed_value(self):
        return self._last_packet != self._captured_packet
    
    @property 
    def captured_packet(self):
        return self._captured_packet
        
    def isr_clk(self, p):
        # capture bit
        # print("c")
        self._current_bits = (self._current_bits << 1) | self.pin_data.value()
        
    def isr_latch(self, p):
        # print("L")
        self._last_packet = self._captured_packet
        self._captured_packet = self._current_bits
        self._current_bits = 0
        self._new_packet = True
    
class ControllerState:
    def __init__(self, raw_val:int):
        self._rawval = raw_val 
        
    @property 
    def present(self):
        return self._rawval != 0xfff 
    
    def as_str(self):
        vals = [
                'B ',
                'Y ',
                'SL',
                'ST',
                'UP',
                'DW',
                'L ',
                'R ',
                'A ',
                'X ',
                'LT',
                'RT'
            ]
        
        vals.reverse()
        
        if not self.present:
            return '     not connected      '
        rv = []
        for i in range(12):
            if self._rawval & (1 << i):
                rv.append(vals[i])
            else:
                rv.append('  ')
        return ''.join(rv)     
    
class PacketReader:
    
    def __init__(self):
        pass 
    
    def states(self, raw_packet_bits:int):
        ctl1 = ControllerState( (raw_packet_bits & 0xfff))
        ctl2 = ControllerState( (raw_packet_bits & (0xfff << 12)) >> 12)
        
        return (ctl1, ctl2)
    
