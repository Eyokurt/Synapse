import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from synapse.config import SynapseConfig
from synapse.audio.voice_loop import VoiceLoop

def main():
    print("--- Synapse VAD (Voice Activity Detection) Demo ---")
    
    # Example of overriding default config
    custom_config = SynapseConfig(
        vad_silence_duration_ms=2000, # Wait 2 seconds instead of 1.5
        vad_speech_threshold=0.6      # Slightly more strict detection
    )
    
    loop = VoiceLoop(config=custom_config)
    
    def on_start():
        print("\n[🎙️] Konuşma Başladı! Sizi dinliyorum...")
        
    def on_ongoing():
        sys.stdout.write("• ")
        sys.stdout.flush()
        
    def on_end(audio_data: np.ndarray):
        print(f"\n[🔇] Konuşma Bitti. ({custom_config.vad_silence_duration_ms}ms suskunluk tespit edildi, {len(audio_data)} samples kaydedildi)")
        
    loop.on_speech_start = on_start
    loop.on_speech_ongoing = on_ongoing
    loop.on_speech_end = on_end
    
    print(f"\nAyarlar: {custom_config.vad_silence_duration_ms}ms suskunluk süresi, {custom_config.vad_speech_threshold} eşik")
    print("Starting microphone stream... (Press Ctrl+C to stop)")
    
    loop.start()

if __name__ == "__main__":
    main()
