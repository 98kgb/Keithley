import pyvisa
import numpy as np
import time

# VISA 초기화
rm = pyvisa.ResourceManager()
inst = rm.open_resource('GPIB0::26::INSTR')

# SMU 설정
inst.write("*RST")
inst.write("smua.source.func = smua.OUTPUT_DCVOLTS")
inst.write("smua.source.limiti = 0.01")  # 10mA
inst.write("smua.measure.autorangei = smua.AUTORANGE_ON")
inst.write("smua.source.output = smua.OUTPUT_ON")

# 사인파 설정
freq = 60            # Hz
duration = 1        # seconds
sampling_rate = 100000  # Hz
amplitude = 4.0     # V

t = np.linspace(0, duration, int(duration * sampling_rate))
v_signal = amplitude * np.sin(2 * np.pi * freq * t)

# 출력 + 측정 루프
for i, v in enumerate(v_signal):
    inst.write(f"smua.source.levelv = {v}")
    current = inst.query("print(smua.measure.i())")
    print(f"{t[i]:.3f}s | V = {v:.3f} | I = {float(current):.6e}")
    time.sleep(1 / sampling_rate)

#%% 출력 OFF
inst.write("smua.source.output = smua.OUTPUT_OFF")
