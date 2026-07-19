import asyncio
import io
import os
import sys
import numpy as np
import scipy.io.wavfile as wav
import warnings

# OpenAI TTS WAV başlıklarında dosya boyutunu sonsuz atadığı için SciPy'ın fırlattığı uyarıları gizle
warnings.filterwarnings("ignore", category=wav.WavFileWarning)
warnings.filterwarnings("ignore", category=ResourceWarning)

from dotenv import load_dotenv

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from synapse.core.engine import AgentEngine
from synapse.core.memory import Memory
from synapse.core.event_bus import EventBus
from synapse.tools.registry import ToolRegistry
from synapse.llm.openai_adapter import OpenAIAdapter
from synapse.audio.voice_loop import VoiceLoop
from synapse.audio.player import AudioPlayer

def float32_to_int16(audio_data: np.ndarray) -> np.ndarray:
    return np.int16(audio_data * 32767)

def get_openai_client():
    from openai import OpenAI
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        print("Lütfen OPENAI_API_KEY çevre değişkenini ayarlayın.")
        sys.exit(1)
    return OpenAI(api_key=api_key)

async def process_voice_async(audio_data: np.ndarray, loop: VoiceLoop, player: AudioPlayer, engine: AgentEngine, client):
    # 1. Ses kaydını WAV formatında belleğe yaz (Whisper için int16 gerekli)
    audio_int16 = float32_to_int16(audio_data)
    wav_io = io.BytesIO()
    wav.write(wav_io, loop.config.audio_sample_rate, audio_int16)
    wav_io.seek(0)
    wav_io.name = "audio.wav"

    print("\n[🧠] Ses yazıya dökülüyor (Whisper STT)...")
    try:
        # 2. Whisper STT
        transcription = client.audio.transcriptions.create(
            model="whisper-1",
            file=wav_io,
            language="tr"
        )
        user_text = transcription.text
        print(f"\n🗣️ Siz: {user_text}")

        if not user_text.strip():
            print("[⚠️] Boş ses algılandı. Tekrar dinleniyor...")
            loop.streamer.start()
            return

        print("[🤖] Synapse düşünüyor...")
        
        # 3. AgentEngine ile cevap üret (agentic_mode=True ile araçları kullanmasını sağla)
        ai_response = await engine.process(user_text, agentic_mode=True)
        print(f"\n🤖 Synapse: {ai_response}")

        print("[🔊] Ses üretiliyor (TTS)...")
        # 4. OpenAI TTS
        tts_response = client.audio.speech.create(
            model="tts-1",
            voice="alloy",
            input=ai_response,
            response_format="wav"
        )
        
        # 5. Çıktı WAV'i bellekte oku
        out_wav_io = io.BytesIO(tts_response.content)
        out_sr, out_audio = wav.read(out_wav_io)
        
        # 6. Sesi Çal
        if out_audio.dtype == np.int16:
            out_audio = out_audio.astype(np.float32) / 32768.0
            
        print("[🔊] Cevap çalınıyor...")
        player.play(out_audio, source_sr=out_sr, blocking=True)
        
    except Exception as e:
        print(f"\n[❌] Bir hata oluştu: {e}")

    print("\n[🎙️] Tekrar dinleniyor... (Kapatmak için Ctrl+C)")
    loop.streamer.start()

def main():
    if sys.platform == "win32":
        sys.stdout.reconfigure(encoding='utf-8')
    load_dotenv()
    print("--- Synapse Voice Chat Demo ---")
    
    client = get_openai_client()

    # Agent Engine Kurulumu
    llm = OpenAIAdapter(model="gpt-4o-mini")
    registry = ToolRegistry()
    
    # Tüm varsayılan tool'ları ekle
    try:
        registry.register_builtins(["file_system", "system", "web_search"])
        print("[✅] Araçlar başarıyla yüklendi (Dosya Sistemi, Sistem Komutları, İnternet Araması).")
    except Exception as e:
        print(f"[⚠️] Araçlar yüklenirken uyarı: {e}")

    engine = AgentEngine(
        llm=llm,
        memory=Memory(),
        event_bus=EventBus(),
        tool_registry=registry
    )
    engine.system_prompt = (
        "Sen gelişmiş bir Türkçe sesli asistansın. "
        "Sana verilen araçları (web_search, dosya okuma vb.) kullanarak kullanıcının isteklerini yerine getirebilirsin. "
        "Cevaplarını sesli olarak okunacağını bilerek, doğal ve akıcı bir şekilde, aşırı uzun olmayan metinlerle ver."
    )

    loop = VoiceLoop()
    player = AudioPlayer()

    def on_start():
        print("\n[🎙️] Konuşma Başladı! (Kaydediliyor...)")
        
    def on_ongoing():
        sys.stdout.write("• ")
        sys.stdout.flush()
        
    def on_end(audio_data: np.ndarray):
        duration = len(audio_data) / loop.config.audio_sample_rate
        print(f"\n[🔇] Konuşma Bitti. ({duration:.2f} saniye)")
        
        # Çakışmayı önlemek için dinlemeyi durdur
        loop.streamer.stop()
        
        # İşlemleri arka planda asyncio ile çalıştır
        asyncio.run(process_voice_async(audio_data, loop, player, engine, client))
        
    loop.on_speech_start = on_start
    loop.on_speech_ongoing = on_ongoing
    loop.on_speech_end = on_end
    
    print("\n[🎙️] Mikrofon dinleniyor... (Durdurmak için Ctrl+C)")
    loop.start()

if __name__ == "__main__":
    main()
