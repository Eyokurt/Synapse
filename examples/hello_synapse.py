import asyncio
import os
from dotenv import load_dotenv

# Load API key from .env file
load_dotenv()

from synapse.core.engine import AgentEngine
from synapse.core.memory import Memory
from synapse.core.event_bus import EventBus
from synapse.tools.registry import ToolRegistry
from synapse.llm.openai_adapter import OpenAIAdapter

async def main():
    print("[SISTEM] Synapse baslatiliyor...")
    
    # 1. Modüllerin Kurulumu
    memory = Memory()
    event_bus = EventBus()
    tool_registry = ToolRegistry()
    
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        print("Hata: OPENAI_API_KEY bulunamadi!")
        return
        
    llm = OpenAIAdapter(model="gpt-4o-mini")
    
    # 2. Araç (Tool) Tanımlama
    @tool_registry.register
    async def get_weather(location: str, unit: str = "celsius") -> str:
        """Belirtilen sehrin hava durumunu getirir."""
        print(f"[ARAC CALISTI]: {location} icin hava durumu kontrol ediliyor...")
        # Gerçek dünyada burada bir API çağrısı (ör: OpenWeather) yapılır
        if location.lower() == "istanbul":
            return f"{location} hava durumu: 25C, gunesli"
        elif location.lower() == "ankara":
            return f"{location} hava durumu: 20C, ruzgarli"
        return f"{location} hava durumu verisi bulunamadi."

    # 3. Motoru Başlatma
    engine = AgentEngine(
        llm=llm,
        memory=memory,
        event_bus=event_bus,
        tool_registry=tool_registry,
        max_iterations=10
    )
    
    # Sisteme nasıl davranması gerektiğini söyleyelim
    memory.add_message("system", "Sen dost canlisi bir asistansin. Hava durumunu ogrenmek icin araclari kullan.")
    
    # 4. Ajanı Çalıştırma
    user_msg = "Istanbul ve Ankara'da hava nasil? Ikisini de kontrol edip bana ozet gec."
    print(f"\n[KULLANICI]: {user_msg}\n")
    
    # agentic_mode=True sayesinde kendi kendine karar döngüsüne (loop) girer
    result = await engine.process(user_msg, agentic_mode=True)
    
    print(f"\n[ASISTAN]: {result}\n")

if __name__ == "__main__":
    asyncio.run(main())
