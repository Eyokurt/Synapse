import asyncio
import os
from dotenv import load_dotenv
import logging

load_dotenv()
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

from synapse.core.engine import AgentEngine
from synapse.core.persistent_memory import SQLiteMemory
from synapse.core.event_bus import EventBus
from synapse.tools.registry import ToolRegistry
from synapse.core.plugin_manager import PluginManager
from synapse.llm.openai_adapter import OpenAIAdapter
from synapse.utils.logger import AgentLogger

async def main():
    print("[SISTEM] Synapse Gelismis Mod Baslatiliyor...")
    
    # 1. Temel Sistemler
    event_bus = EventBus()
    tool_registry = ToolRegistry()
    
    # Yeni Özellik 1: Loglama
    logger = AgentLogger(event_bus)
    
    # Yeni Özellik 2: Kalıcı SQLite Hafıza
    db_path = "synapse_demo.db"
    session_id = "demo_session_1"
    memory = SQLiteMemory(db_path=db_path, session_id=session_id)
    
    # Yeni Özellik 3: Eklenti Sistemi
    # Sistemin plugin yükleyebildiğini göstermek için dummy plugin'i geçici olarak oluşturuyoruz
    plugin_code = """
def setup(registry, bus):
    @registry.register
    def calculate_tax(amount: int) -> float:
        '''Verilen tutarin %20 vergisini hesaplar.'''
        return amount * 0.20
    """
    with open("my_plugin.py", "w", encoding="utf-8") as f:
        f.write(plugin_code)
        
    plugin_manager = PluginManager(tool_registry, event_bus)
    plugin_manager.load_plugin("my_plugin")
    
    # API Kontrolü
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        print("Hata: OPENAI_API_KEY bulunamadi!")
        return
        
    llm = OpenAIAdapter(model="gpt-4o-mini")
    
    engine = AgentEngine(
        llm=llm,
        memory=memory,
        event_bus=event_bus,
        tool_registry=tool_registry,
        max_iterations=10
    )
    
    memory.add_message("system", "Sen dost canlisi ve finansal hesaplamalar yapabilen bir asistansin.")
    
    user_msg = "Merhaba! 5000 TL'nin vergisi ne kadar yapar?"
    print(f"\n[KULLANICI]: {user_msg}\n")
    
    # Ajanı Çalıştırma
    result = await engine.process(user_msg, agentic_mode=True)
    
    print(f"\n[ASISTAN]: {result}\n")
    
    # Hafıza Silme (İsteğe bağlı)
    # memory.clear() 

if __name__ == "__main__":
    asyncio.run(main())
