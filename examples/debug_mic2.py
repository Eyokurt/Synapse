import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import numpy as np
import sounddevice as sd
from synapse.audio.vad import SileroVAD

def main():
    print("--- Mikrofon Hata Ayıklama V2 (PortAudio Native Resampling) ---")
    
    vad = SileroVAD()
    
    # Doğrudan 16000Hz ve 512 blocksize ile PortAudio üzerinden açıyoruz
    # PortAudio (Sounddevice) donanımla uyumsuzluğu kendi içinde kaliteli bir şekilde çözecektir.
    stream = sd.InputStream(
        samplerate=16000,
        channels=1,
        blocksize=512,
        dtype=np.float32
    )
    
    print("Lütfen mikrofona doğru sesli bir şekilde konuşun (3 saniye)...")
    
    stream.start()
    try:
        for i in range(100):
            chunk, overflowed = stream.read(512)
            chunk = chunk[:, 0]
            
            amp = np.max(np.abs(chunk))
            
            inputs = {
                "input": np.expand_dims(chunk, axis=0),
                "sr": vad.sr_tensor,
                "state": vad.state
            }
            out, vad.state = vad.session.run(None, inputs)
            confidence = out[0][0]
            
            print(f"Chunk {i:03d} | Amp: {amp:.5f} | Yapay Zeka: %{confidence*100:.1f} {'(SES ALGILANDI!)' if confidence > 0.5 else ''}")
    finally:
        stream.stop()

if __name__ == "__main__":
    main()
