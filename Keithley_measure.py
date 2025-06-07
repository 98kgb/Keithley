# -*- coding: utf-8 -*-
"""
This code connect to the keithely, and measure save the data.

The measurement includes:
    the output, transfer characteristics of OTFTs.

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
    if mode == 1: # measurement setting for r1
        v1_a, v2_a, v2_b = 0, 0, 0
        v1_b = v_range
    elif mode == 2: # measurement setting for r2
        v1_a, v1_b, v2_b = 0, 0, 0
        v2_a = v_range
    elif mode == 3: # measurement setting for reset transistor 
        if char_type == 'output':
            v1_a = v_range # v_ds
            v2_a = v_fixed # v_gs
            v1_b, v2_b = 0, 0
        elif char_type == 'transfer':
            v1_a = v_fixed # v_ds
            v2_a = v_range # v_gs
            v1_b, v2_b = 0, 0 
        else:
            raise ValueError("Invalid mode")
    elif mode == 4: # measurement setting for transistor 2
        if char_type == 'output':
            v1_b = v_fixed # v_gs
            v2_a = v_range # v_ds
            v1_a, v2_b = 0, 0
        elif char_type == 'transfer':
            v1_b = v_range # v_gs
            v2_a = v_fixed # v_ds
            v1_a, v2_b = 0, 0
        else:
            raise ValueError("Invalid mode")
            
    elif mode == 5: # measurement setting for transistor 1
        if char_type == 'output':
            v1_a = v_fixed # v_gs
            v1_b = v_range # v_ds
            v2_a, v2_b = 0, 0
        elif char_type == 'transfer':
            v1_a = v_range # v_gs
            v1_b = v_fixed # v_ds
            v2_a, v2_b = 0, 0
        else:
            raise ValueError("Invalid mode")
    else:
        raise ValueError("Invalid mode")
    
    return v1_a, v1_b, v2_a, v2_b

def apply_V(inst, ch_name, v, v_assigned, char_type, prev_I):
    print('NPLC: ',5 if abs(prev_I) > 5e-8 else 10)
    inst.write(f"smu{ch_name}.source.func = smu{ch_name}.OUTPUT_DCVOLTS")
    inst.write(f"smu{ch_name}.source.levelv = {v_assigned if isinstance(v_assigned, (int, float)) else v}")
    inst.write(f"smu{ch_name}.source.limiti = 1e-5")
    inst.write(f"smu{ch_name}.measure.nplc = {5 if abs(prev_I) > 5e-8 else 10}")
    inst.write(f"smu{ch_name}.measure.rangei = 1e-5")  # expectation range
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
1: Measuring resistance 1
2: Measuring resistance 2

3: Measuring reset transistor
4: Measuring transistor 2
5: Measuring transistor 1
"""

mode = 4 ## insert measurement mode ##
char_type = 'transfer' ## insert measurement characteristics (output or transfer)##
saving = True
saving_name = 'AH1_10um'
v_fix_list = [-4,-6,-8,-10]

for v_fix in v_fix_list:
    if mode <= 2:
        char_list = ['output']
        v_range = np.arange(-2, 2, 0.1)
        v_fixed = None
    else:
        char_list = ['transfer']
        # v_range = np.concatenate([np.arange(0, -10, -0.1), np.arange(-9.9, 0, 0.2)]) # input for forward and inverse
        v_range = np.arange(0.1, -4, -0.1)
        
        v_fixed = v_fix        
    for char_type in char_list:    
        
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
        prev_I = -1e-12
        for idx, v in enumerate(v_range):
        
            print(f'v1_a: {v1_a if isinstance(v1_a, (int, float)) else v}')
            print(f'v1_b: {v1_b if isinstance(v1_b, (int, float)) else v}')
            print(f'v2_a: {v2_a if isinstance(v2_a, (int, float)) else v}')
            print(f'v2_b: {v2_b if isinstance(v2_b, (int, float)) else v}')
            
            # SMU1A setting
            apply_V(inst1, ch_name='a', v=v, v_assigned=v1_a, char_type=char_type, prev_I = prev_I)
          
            # SMU1B setting
            apply_V(inst1, ch_name='b', v=v, v_assigned=v1_b, char_type=char_type, prev_I = prev_I)
                
            # SMU2A setting
            apply_V(inst2, ch_name='a', v=v, v_assigned=v2_a, char_type=char_type, prev_I = prev_I)
          
            # SMU2B setting
            apply_V(inst2, ch_name='b', v=v, v_assigned=v2_b, char_type=char_type, prev_I = prev_I)
            
            if mode == 1:
                current = inst1.query("print(smub.measure.i())")
            elif mode == 2:
                current = inst2.query("print(smua.measure.i())")
            elif mode == 3:
                current = inst1.query("print(smua.measure.i())")
            elif mode == 4:
                current = inst2.query("print(smua.measure.i())")
            elif mode == 5:
                current = inst1.query("print(smub.measure.i())")
            
            measures[idx, 1] = float(current)
            print(f"Voltage = {v:.2f}, Current = {current.strip()} A")
            prev_I = float(current)
            
        # turn off the Keithley output
        inst1.write("smua.source.output = smua.OUTPUT_OFF")
        inst1.write("smub.source.output = smub.OUTPUT_OFF")
        
        inst2.write("smua.source.output = smua.OUTPUT_OFF")
        inst2.write("smub.source.output = smub.OUTPUT_OFF")
        
        # Visualization of result
        if mode <=2:
            dv = measures[1,0]-measures[0,0]
            di = measures[1:,1] - measures[:len(measures)-1,1]
            R = np.mean(dv/di)
            plt.title(f'R{mode}')
            plt.plot(measures[1:, 0], measures[1:, 1], label = f'{R*1e-9:.2f} GOhm', marker='o', color='k')
            plt.xlabel('V (V)', fontsize=15)
            plt.ylabel('I (A)', fontsize=15)
        else:
            Tr_name = ['TR_reset', 'TR_2', 'TR_1']

            if char_type == 'output':
                plt.title(f'{Tr_name[mode-3]}')
                plt.plot(measures[1:, 0], measures[1:, 1], label=f"Vgs = {v_fixed}V", marker='o', color='red')
                plt.xlabel('Vds (V)', fontsize=15)
                plt.ylabel('Ids (A)', fontsize=15)
            elif char_type == 'transfer':
                plt.title(f'{Tr_name[mode-3]}')
                plt.semilogy(measures[1:, 0], abs(measures[1:, 1]), label=f"Vds = {v_fixed}V", marker='o', color='blue')
                plt.xlabel('Vgs (V)', fontsize=15)
                plt.ylabel('Ids (A)', fontsize=15)
        
        plt.xticks(fontsize=12)
        plt.yticks(fontsize=12)
        plt.legend(loc='best', fontsize=12)
        plt.grid(True)
        plt.tight_layout()
        plt.show()
        
        # Saving the result
        if saving:
            # check existence of directory
            save_dir = os.path.join(path_c, "result", date)
            os.makedirs(save_dir, exist_ok=True)
            
            # save measurement result
            if mode <= 2:
                df = pd.DataFrame(measures, columns=['V', 'I'])
                df['R'] = np.mean(dv/di)
                df.to_csv(f"{save_dir}\\{saving_name}_R{mode}.csv")
            else:
                Tr_name = ['TR_reset', 'TR_2', 'TR_1']
                columns = ['Vds', 'Ids'] if char_type == 'output' else ['Vgs', 'Ids']
                column = 'Vgs' if char_type == 'output' else 'Vds'
                df = pd.DataFrame(measures, columns=columns)
                df[f'{column}'] = v_fixed
                df.to_csv(f'{save_dir}\\{saving_name}_{Tr_name[mode-3]}_{char_type}_{v_fix}.csv')    
            print("Data saved.")


