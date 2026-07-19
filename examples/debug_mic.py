import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import numpy as np
from synapse.audio.stream import AudioStreamer
from synapse.audio.vad import SileroVAD

def main():
    print("--- Mikrofon Hata Ayıklama (Debug) ---")
    
    streamer = AudioStreamer()
    vad = SileroVAD()
    
    print(f"Cihaz Native Sample Rate: {streamer.native_sr}Hz")
    print("Lütfen mikrofona doğru sesli bir şekilde konuşun (3 saniye boyunca test edilecek)...")
    
    streamer.start()
    
    try:
        # 3 saniye boyunca (yaklaşık 100 chunk) analiz edelim
        for i in range(100):
            chunk = streamer.get_chunk()
            amp = np.max(np.abs(chunk))
            
            # VAD olasılığını hesapla
            inputs = {
                "input": np.expand_dims(chunk.astype(np.float32), axis=0),
                "sr": vad.sr_tensor,
                "state": vad.state
            }
            out, vad.state = vad.session.run(None, inputs)
            confidence = out[0][0]
            
            print(f"Chunk {i:03d} | Maksimum Ses Seviyesi (Amplitude): {amp:.5f} | Yapay Zeka İnsan Sesi Olasılığı: %{confidence*100:.1f}")
            
    finally:
        streamer.stop()

if __name__ == "__main__":
    main()
