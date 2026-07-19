import os
import numpy as np
import pyttsx3
import scipy.io.wavfile as wav
import scipy.signal as signal
from synapse.audio.vad import SileroVAD
from synapse.config import SynapseConfig

def generate_test_speech(filename="test_speech.wav"):
    engine = pyttsx3.init()
    engine.save_to_file("Hello, this is a test of the voice activity detection system.", filename)
    engine.runAndWait()
    print(f"Generated {filename}")

def test_vad_on_file(filename="test_speech.wav"):
    # Load audio
    sr, data = wav.read(filename)
    
    # Convert to mono if necessary
    if len(data.shape) > 1:
        data = data.mean(axis=1)
    
    # Resample to 16000 if necessary
    if sr != 16000:
        samples = int(len(data) * 16000 / sr)
        data = signal.resample(data, samples)
        sr = 16000
        
    # Convert to float32 between -1 and 1
    data = data.astype(np.float32)
    max_val = np.max(np.abs(data))
    if max_val > 1.0:
        data = data / max_val
        
    print(f"Audio loaded: {len(data)} samples at {sr}Hz. Max amp: {np.max(np.abs(data))}")
    
    config = SynapseConfig(audio_sample_rate=16000)
    vad = SileroVAD(config=config)
    
    chunk_size = 512
    detected_speech = False
    
    for i in range(0, len(data) - chunk_size, chunk_size):
        chunk = data[i:i+chunk_size]
        
        has_speech = vad.is_speech(chunk)
        
        if has_speech:
            detected_speech = True
            print(f"Chunk {i//chunk_size:03d} | Amp: {np.max(np.abs(chunk)):.4f} | SPEECH DETECTED!")
            
    if not detected_speech:
        print("VAD FAILED TO DETECT SPEECH IN THE FILE!")
    else:
        print("VAD SUCCESSFULLY DETECTED SPEECH!")

if __name__ == "__main__":
    generate_test_speech()
    test_vad_on_file()
