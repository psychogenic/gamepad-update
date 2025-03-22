'''
A nifty little PIO class to read the gamepad (https://github.com/psychogenic/gamepad-pmod) 
data packets.

@author: Pat Deegan
@copyright: Copyright (C) 2025 Pat Deegan, https://psychogenic.com
'''

from machine import Pin

import micropython
import rp2
from rp2 import PIO, StateMachine
from array import array

from gamepad_mem import flush_mem

DEBUG_OUT_PINSTART = 21

@rp2.asm_pio(in_shiftdir=PIO.SHIFT_LEFT,
             sideset_init=(PIO.OUT_LOW, PIO.OUT_LOW, PIO.OUT_LOW, PIO.OUT_LOW))
def sipo_reader():
    wrap_target()
    
    push(noblock).side(0b000)  # Reset ISR
    
    label("poll_loop")
    jmp(pin, "send_data")       # Pins are 0b[DAT CLK LATCH] 
    mov(x, isr)  # stash isr
    mov(isr, null) # zero isr
    in_(pins, 1)  # pull CLCK input into isr
    mov(y, isr) # stash current CLOCK
    nop()
    mov(isr, x) # restor isr
    nop()
    # push(block)
    # y (CLK) is either HIGH -- time to sample, or LOW wait some more
    jmp(not_y, "poll_loop") # CLK IS LOW, wait for HIGH or LATCH
    #CLOCK IS HIGH
    # get sample
    
    mov(x, isr) # stash ISR
    mov(isr, null)
    in_(pins, 2) # sampled CLOCK (HIGH) + DATA into ISR
    nop()
    mov(y, isr) # sample CLOCK + DAT
    nop()
    mov(isr, x) # restore accum ISR
    nop()
    set(x, 0b01) # DAT LOW + CLK HIGH
    
    jmp(x_not_y, "add_dat_high")  # not equal, so DAT HIGH
    label("add_dat_low")
    set(x, 0) # didn't jump, so DAT bit is LOW
    jmp("wait_clock_low")
    
    
    label("add_dat_high")
    set(x, 1) # jumped here, so DAT is HIGH
    jmp("wait_clock_low")
    
    label("wait_clock_low")
    in_(x, 1) # DAT bit stashed in X, add that to ISR
    wait(0, gpio, 18)  # WAIT FOR CLOCK LOW
    # wait(0, pins, 0)  # WAIT FOR CLOCK LOW
    jmp("poll_loop")
    

    label("send_data")
    push(noblock)               # Send ISR
    wait(0, gpio, 17)
    mov(isr, null) # clear ISR
    jmp("poll_loop")
    wrap()
    
    
class SIPO:
    def __init__(self, dat_pin, clk_pin, latch_pin, max_bits=32):
        # Configure StateMachine with specific pins
        
        self.clk_pin = Pin(clk_pin, Pin.IN)
        self.latch_pin = Pin(latch_pin, Pin.IN)
        self.dat_pin = Pin(dat_pin, Pin.IN) 
        
        flush_mem(f"LATCH {latch_pin} is {self.latch_pin}: {self.latch_pin.value()}")
        self.sm = StateMachine(6, sipo_reader,
                              # freq=12_000_000,           # 20 MHz sampling rate 
                              in_base=self.clk_pin,  
                              jmp_pin=self.latch_pin,
                              sideset_base=Pin(DEBUG_OUT_PINSTART)) # LATCH pin 
        
        
        
        
        # Buffer for data (32-bit unsigned int)
        self._last_data = 0
        self._cur_data = 0
        self.max_bits = min(max_bits, 32)  # Cap at 32 bits
        
        
        
    def enable(self):
        print("Enabling SIPO PIO reader")
        self.sm.active(1)
    def disable(self):
        print("Disabling SIPO PIO reader")
        self.sm.active(0)

    @property 
    def new_packet(self):
        if self.sm.rx_fifo() > 0:
            self.read()
            return True 
        
        return False
    
    @property 
    def captured_packet(self):
        return self._cur_data
    
    @property 
    def changed_value(self):
        return self._cur_data != self._last_data
    
    def read(self):
        """Read the latest variable-length data"""
        if self.sm.rx_fifo() > 0:  # Check if data is available
            self._last_data = self._cur_data
            self._cur_data = self.sm.get() & ((1 << self.max_bits) - 1)
        return self._cur_data
