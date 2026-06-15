import pyaudio
import numpy as np
import sys
import time

try:
    sys.stdout.reconfigure(encoding='utf-8')
except:
    pass

p = pyaudio.PyAudio()

def test_mic(idx, name):
    print(f"Testing {name} (index {idx}) for 2.5 seconds...")
    try:
        stream = p.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=16000,
            input=True,
            frames_per_buffer=1024,
            input_device_index=idx
        )
        
        rms_values = []
        start_time = time.time()
        while time.time() - start_time < 2.5:
            data = stream.read(1024, exception_on_overflow=False)
            chunk = np.frombuffer(data, dtype=np.int16)
            rms = np.sqrt(np.mean(chunk.astype(np.float64)**2))
            rms_values.append(rms)
            
        stream.stop_stream()
        stream.close()
        avg_rms = np.mean(rms_values)
        max_rms = np.max(rms_values)
        print(f"  -> Avg RMS: {avg_rms:.2f} | Max RMS: {max_rms:.2f}")
        return avg_rms
    except Exception as e:
        print(f"  -> Error: {e}")
        return 0

test_mic(1, "BIRD UM1")
test_mic(15, "HyperX Virtual Surround Sound")
p.terminate()
