import sys
import time
from synapse.audio.vad import SileroVAD
from synapse.audio.stream import AudioStreamer

def main():
    print("--- Synapse VAD (Voice Activity Detection) Demo ---")
    print("Initializing Silero VAD...")
    
    # 1. Initialize VAD
    vad = SileroVAD(sample_rate=16000, threshold=0.5)
    
    # 2. Initialize Streamer
    # 512ms chunk is recommended for Silero VAD for stable detection
    streamer = AudioStreamer(sample_rate=16000, chunk_duration_ms=512)
    
    print("\nStarting microphone stream... (Press Ctrl+C to stop)")
    streamer.start()
    
    try:
        # State tracking
        is_talking = False
        silence_chunks = 0
        
        while True:
            # Block and wait for 512ms of audio
            chunk = streamer.get_chunk()
            
            # Ask the VAD if there is a voice
            has_voice = vad.is_speech(chunk)
            
            if has_voice:
                if not is_talking:
                    print("\n[🎙️] Konuşma Başladı! Sizi dinliyorum...")
                    is_talking = True
                else:
                    # Print dots to show continuous speech
                    sys.stdout.write("• ")
                    sys.stdout.flush()
                silence_chunks = 0
            else:
                if is_talking:
                    silence_chunks += 1
                    # If 3 consecutive chunks (1.5 seconds) are silence, we assume they stopped.
                    if silence_chunks >= 3:
                        print("\n[🔇] Konuşma Bitti. Suskunluk tespit edildi.")
                        is_talking = False
                        silence_chunks = 0
    except KeyboardInterrupt:
        print("\nStopping stream...")
    finally:
        streamer.stop()

if __name__ == "__main__":
    main()
