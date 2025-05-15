# -*- coding: utf-8 -*-
"""
Created on Mon Apr 14 17:33:14 2025

@author: Gibaek
"""

import pyvisa

# Resource Manager 생성
rm = pyvisa.ResourceManager()
print(rm.list_resources())  # 연결된 장비 주소 리스트 확인

#%%
# 장비 연결 (주소는 위에서 확인한 값으로 대체)
inst = rm.open_resource('GPIB0::10::INSTR')  # 또는 USB / TCPIP 주소
#%%
# 장비 초기화
inst.write("*RST")
inst.write("*CLS")
#%%
# 전압 소스 모드 설정 (1V 출력, 전류 측정)
inst.write("smua.source.func = smua.OUTPUT_DCVOLTS")
inst.write("smua.source.levelv = 4.0")
inst.write("smua.source.limiti = 0.01")  # 10mA 한도 설정
inst.write("smua.measure.autorangei = smua.AUTORANGE_ON")

# 출력 ON
inst.write("smua.source.output = smua.OUTPUT_ON")

# 전류 측정
current = inst.query("print(smua.measure.i())")
print("측정 전류 (A):", current)

#%% 출력 OFF
inst.write("smua.source.output = smua.OUTPUT_OFF")
