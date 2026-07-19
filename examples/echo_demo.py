import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import numpy as np
from synapse.audio.voice_loop import VoiceLoop
from synapse.audio.player import AudioPlayer

def main():
    print("--- Synapse Echo (Record & Playback) Demo ---")
    
    loop = VoiceLoop()
    player = AudioPlayer()
    
    def on_start():
        print("\n[🎙️] Konuşma Başladı! (Kaydediliyor...)")
        
    def on_ongoing():
        sys.stdout.write("• ")
        sys.stdout.flush()
        
    def on_end(audio_data: np.ndarray):
        duration = len(audio_data) / loop.config.audio_sample_rate
        print(f"\n[🔇] Konuşma Bitti. Kayıt süresi: {duration:.2f} saniye.")
        
        print(f"[🔊] Sesinizi geri çalıyorum (Echo)...")
        # Pause the voice loop temporarily while playing back to avoid feedback loop
        loop.streamer.stop()
        player.play(audio_data, blocking=True)
        print("[✅] Çalma bitti. Tekrar dinleniyor...")
        loop.streamer.start()
        
    loop.on_speech_start = on_start
    loop.on_speech_ongoing = on_ongoing
    loop.on_speech_end = on_end
    
    print("\nMikrofon dinleniyor... (Durdurmak için Ctrl+C)")
    loop.start()

if __name__ == "__main__":
    main()
