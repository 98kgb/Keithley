# -*- coding: utf-8 -*-
"""
Created on Wed Jun  4 09:16:37 2025

@author: Gibaek
"""

import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import os

path_c = os.path.dirname(os.path.abspath(__file__))

load_name = 'AH1_10um'
mode = 5
char_type = 'transfer'
if mode <= 2:
    data = pd.read_csv(f'{path_c}\\result\\20250603\\{load_name}_R{mode}.csv')
else:
    Tr_name = ['TR_reset', 'TR_2', 'TR_1']
    data = pd.read_csv(f'{path_c}\\result\\20250603\\{load_name}_{Tr_name[mode-3]}_{char_type}.csv')
    
if mode <3:
    plt.title(f'R{mode}')
    plt.plot(data['V'], data['I'], marker = 'o', color = 'k', label = f"{data['R'][0]*1e-9:.2f} GOhm")
    plt.xlabel('Voltage (V)')
    plt.ylabel('Currenct (A)')
    plt.grid()
    plt.legend()
    
else:
    if char_type == 'output':
        plt.title(f'{Tr_name[mode-3]}')
        plt.plot(data['Vds'], data['Ids']-data['Vds']/0.9e9, marker = 'o', color = 'k', label = 'Vgs = -10V')
        plt.xlabel('$V_{DS}$ (V)')
        plt.ylabel('$I_{DS}$ (A)')
        plt.grid()
        plt.legend()
    else:
        plt.title(f'{Tr_name[mode-3]}')
        plt.semilogy(np.arange(0, -10, -0.5), abs(data['Ids']-data['Vds']/0.92e9), marker = 'o', color = 'k', label = 'Vds = -10V')
        plt.xlabel('$V_{GS}$ (V)')
        plt.ylabel('$I_{DS}$ (A)')
        plt.grid()
        plt.legend()
    
