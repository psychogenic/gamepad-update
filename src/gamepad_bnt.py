'''
Burn and test functions

@author: Pat Deegan
@copyright: Copyright (C) 2025 Pat Deegan, https://psychogenic.com
'''

import utime

from gamepad_mem import flush_mem

flush_mem('prior to db and packread imports')
from gamepad_db import BareDemoboard, PacketReader

# import ttboard.util.colors as colors


flush_mem('prior to func defs')
def wait_for_go(db:BareDemoboard, go_only:bool=False):
    tlast = utime.time()
    outval = 0
    while True:
        if db.triggered_go:
            db.request_handled()
            return True 
        
        if db.triggered_reset:
            db.request_handled()
            if not go_only:
                return False 
            
        tnow = utime.time()
        if (tnow - tlast) >= 1:
            tlast = tnow 
            if outval:
                outval = 0
            else:
                outval = 0xff
            db.set_output(outval)
    
    
    
def run_test(db:BareDemoboard):
     
    outval = 0
    tlast = utime.time()
    numPacketsRcvd = 0
    pReader = PacketReader()
    db.gamepad.enable()
    packTime = utime.time()
    while True:
        # todo: capture events
        if db.triggered_reset:
            db.request_handled()
            db.gamepad.disable()
            return True 
        
        if utime.time() - packTime > 3:
            packTime = utime.time()
            print("\nShould have received packets by now...")
        
        if db.gamepad.new_packet:
            packTime = utime.time()
            numPacketsRcvd += 1
            if db.gamepad.changed_value:
                (ctrl1, ctrl2) = pReader.states(db.gamepad.captured_packet)
                print("\n", numPacketsRcvd, "\t", 
                      #colors.color(ctrl1.as_str(), 'red'),
                      ctrl1.as_str(),
                      " | ",
                      # colors.color(ctrl2.as_str(), 'blue'),
                      ctrl2.as_str(),
                      end='')
            else:
                print('.', end='')
                
                
                
        tnow = utime.time()
        if (tnow - tlast) >= 1:
            tlast = tnow 
            if outval:
                outval = 0
            else:
                outval = 0b0110
            db.set_output(outval)


def burn_and_test_loop(db:BareDemoboard, fw_file:str, skip_burn:bool=False):
    
    if not skip_burn:
        print("Press CLOCK to start burning.")
        if not wait_for_go(db):
            return 
        db.set_output(1)
        print(f"Burning firmware '{fw_file}'...")
        try_count = 0
        while try_count < 2:
            try:
                burn_fw(db, fw_file)
                try_count = 100
            except Exception as e:
                print(f"Issue burning fw (attempt {try_count + 1})!")
                print(str(e))
                utime.sleep_ms(500)
            try_count += 1
            
        if try_count < 100:
            print("\n*** Could not write firmware! ***")
            return False
        
        print("Done.  ")
        
    db.set_output(2)
    print("Connect controller and test buttons.  Press RESET when done.")
    run_test(db)
    return True
    
    
def burn_fw(db:BareDemoboard, fw_file):
    print(f'Burning {fw_file}')
    db.flasher.flash_binary(fw_file)
    db.flasher_release() # running out of mem


flush_mem('bnt loaded')