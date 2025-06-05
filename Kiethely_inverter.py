# -*- coding: utf-8 -*-
"""
This code connect to the keithely, and measure save the data.

The measurement includes invertor 1 and 2.

The measurement result would be saved in ./result.

@author: Gibaek KIM, Yerin KIM
"""

import pyvisa
import os
import time
# path for saving
date = time.strftime("%Y%m%d", time.localtime())
path_c = os.path.dirname(os.path.abspath(__file__))

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

def assign_V(mode, v_range, v_fixed):
    if mode == 1: # measurement setting for invertor 1
        v1_a = v_range # v_mem
        v2_b = v_fixed # v_dd
        v2_a, v1_b = 0, 0 # v_out, v_c
        
    elif mode == 2: # measurement setting for invertor 2
        v1_b = v_range # v_c
        v2_b = v_fixed # v_dd
        v2_a, v1_a = 0, 0 # v_out, v_mem
        
    else:
        raise ValueError("Invalid mode")
    
    return v1_a, v1_b, v2_a, v2_b

def apply_V(inst, ch_name, v, v_assigned, char_type):
    inst.write(f"smu{ch_name}.source.func = smu{ch_name}.OUTPUT_DCVOLTS")
    inst.write(f"smu{ch_name}.source.levelv = {v_assigned if isinstance(v_assigned, (int, float)) else v}")
    inst.write(f"smu{ch_name}.source.limiti = 1e-4")
    inst.write(f"smu{ch_name}.measure.nplc = 5")
    inst.write(f"smu{ch_name}.measure.rangei = 1e-5")  # expectation range
    inst.write(f"smu{ch_name}.source.output = smu{ch_name}.OUTPUT_ON")

def apply_I(inst, ch_name, i, i_assigned, char_type):
    inst.write(f"smu{ch_name}.source.func = smu{ch_name}.OUTPUT_DCAMPS")
    inst.write(f"smu{ch_name}.source.leveli = {i_assigned if isinstance(i_assigned, (int, float)) else i}")
    inst.write(f"smu{ch_name}.source.limiti = 1e-4")
    inst.write(f"smu{ch_name}.measure.nplc = 5")
    inst.write(f"smu{ch_name}.measure.rangev = 1e1")  # expectation range
    inst.write(f"smu{ch_name}.source.output = smu{ch_name}.OUTPUT_ON")

    
rm = pyvisa.ResourceManager()
print(rm.list_resources())  # device address list

#%% Connect to device

inst1 = rm.open_resource('GPIB0::26::INSTR')  # insert device address
inst2 = rm.open_resource('GPIB0::25::INSTR')  # insert device address

#%% Measurement
    
"""
Change mode that you want.

Each mode number corresponding to:
1: invertor 1
2: invertor 2
"""

mode = 2 ## insert measurement mode ##
saving = False
saving_name = 'AH1_10um'

for mode in range(1,3):
        
    v_range = np.arange(0.2, -10, -0.2)
    v_fixed = -10
    # Define sweep voltage for each channel.
    
    # initialize
    for inst in  [inst1, inst2]:
        inst.timeout = 5000
        inst.write("reset()")
        inst.write("errorqueue.clear()")
    
    measures = np.zeros([len(v_range), 2])
    measures[:, 0] = v_range
    v1_a, v1_b, v2_a, v2_b = assign_V(mode, v_range, v_fixed)
    
    
    # Apply voltage and measurement
    for idx, v in enumerate(v_range):
    
        print(f'v1_a: {v1_a if isinstance(v1_a, (int, float)) else v}')
        print(f'v1_b: {v1_b if isinstance(v1_b, (int, float)) else v}')
        print(f'v2_a: {v2_a if isinstance(v2_a, (int, float)) else v}')
        print(f'v2_b: {v2_b if isinstance(v2_b, (int, float)) else v}')
        
        # SMU1A setting
        apply_V(inst1, ch_name='a', v=v, v_assigned=v1_a, char_type=None) # V_mem
      
        # SMU1B setting
        if mode == 1:
            apply_I(inst1, ch_name='b', i=v, i_assigned=v1_b, char_type=None)
        else:
            apply_V(inst1, ch_name='b', v=v, v_assigned=v1_b, char_type=None)
            
        # SMU2A setting
        if mode == 2:
            apply_I(inst2, ch_name='a', i=v, i_assigned=v2_a, char_type=None)
        else:
            apply_V(inst2, ch_name='a', v=v, v_assigned=v2_a, char_type=None)
        
        # SMU2B setting
        apply_V(inst2, ch_name='b', v=v, v_assigned=v2_b, char_type=None)
        
        if mode == 1:
            voltage = inst1.query("print(smub.measure.v())")
        elif mode == 2:
            voltage = inst2.query("print(smua.measure.v())")
            
        measures[idx, 1] = float(voltage)
        print(f"Vin = {v:.2f}, Vout = {voltage.strip()} V")
    
    # turn off the Keithley output
    inst1.write("smua.source.output = smua.OUTPUT_OFF")
    inst1.write("smub.source.output = smub.OUTPUT_OFF")
    
    inst2.write("smua.source.output = smua.OUTPUT_OFF")
    inst2.write("smub.source.output = smub.OUTPUT_OFF")
    
    # Visualization of result
    
    plt.plot(measures[:, 0], measures[:, 1], marker='o', color='k')
    if mode == 1:
        plt.xlabel('Vmem (V)', fontsize=15)
        plt.ylabel('Vc (V)', fontsize=15)
    elif mode == 2:
        plt.xlabel('Vc (V)', fontsize=15)
        plt.ylabel('Vout (V)', fontsize=15)

    plt.xticks(fontsize=12)
    plt.yticks(fontsize=12)
    plt.grid(True)
    plt.tight_layout()
    plt.show()
    
    # Saving the result
    if saving:
        # check existence of directory
        save_dir = os.path.join(path_c, "result", date)
        os.makedirs(save_dir, exist_ok=True)
        
        # save measurement result
        columns = ['Vmem', 'Vc'] if mode == 1 else ['Vc', 'Vout']
        df = pd.DataFrame(measures, columns = columns)
        df.to_csv(f"{save_dir}\\{saving_name}_invertor_{mode}.csv")
        print("Data saved.")
