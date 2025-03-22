'''
debugging mem
@author: Pat Deegan
@copyright: Copyright (C) 2025 Pat Deegan, https://psychogenic.com
'''
import gc
import micropython
GCThreshold = gc.threshold()
gc.threshold(5000)

MemDebugOn = False

def flush_mem(msg:str='memdump'):
    gc.collect()
    if MemDebugOn:
        print(msg)
        micropython.mem_info()
    