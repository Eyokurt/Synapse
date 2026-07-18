# Synapse Kütüphanesi Tasarım ve Yol Haritası

## Proje Bağlamı ve Vizyon
Bu proje, geliştiricilerin AI asistanları inşa etmesini kolaylaştıran modüler, platformdan bağımsız, düşük gecikmeli (low-latency streaming odaklı) ve otonom ajanları (Agentic Loops) destekleyen kapsamlı bir Python kütüphanesidir. Codebase'in uzun vadede temiz kalması için çekirdekten (core) eklentilere (plugins) doğru katmanlı bir mimari benimsenecektir.

## Mimari Yaklaşım
Ana mimari 4 temel bileşene ayrılmıştır:
1. **Core Agent Engine:** Ajanın karar döngüsünü (Observe -> Think -> Act) yöneten, agentic modun açılıp kapatılabildiği çekirdek.
2. **Event Bus:** Asenkron olayları (`on_token`, `on_tool_call`) yöneten sinir ağı.
3. **Voice & Streaming Pipeline:** Düşük gecikme ile STT ve TTS işlemlerini birleştiren veri yolu.
4. **Tool Registry:** `@agent_tool` dekoratörü ile çalışan, otomatik fonksiyon şeması üreten araç sistemi.

---

## Yol Haritası (Fazlar)

### FAZ 1: Çekirdek Altyapı (The Solid Foundation)
En yüksek öncelikli kısım. Diğer her şey bu motorun üzerine inşa edilecek.
- **Olay Veriyolu (Event Bus):** `EventEmitter` sınıfı ile asenkron olay dinleme ve fırlatma.
- **LLM Adaptör Katmanı:** OpenAI, Anthropic, Gemini vb. API'lerin standart bir arayüzle soyutlanması.
- **Araç Kayıt Sistemi (Tool Registry):** Python fonksiyonlarını `@agent_tool` dekoratörü ile işaretleme ve şema üretme.
- **Agentic Loop Engine:** 
  - `agentic_mode=False`: Soru gider, cevap gelir (Hızlı ve basit kullanım).
  - `agentic_mode=True`: Ajan döngüsü başlar (Düşün -> Araç Kullan -> Sonucu Gör -> Tekrar Düşün -> Cevapla).
- **Temel Hafıza (Context) Yönetimi:** Basit `Memory` sınıfı.

### FAZ 2: Ses ve Akış (Voice & Streaming Pipeline)
Düşük gecikme (latency) odaklı akış katmanı.
- **Akış Yöneticisi (Stream Orchestrator):** STT -> LLM -> TTS asenkron köprüsü.
- **STT ve TTS Adaptörleri:** Standart arayüzler.
- **Audio Utilities:** Ses formatlama, resample, sıkıştırma.
- **VAD (Voice Activity Detection):** Sessizlik algılama.

### FAZ 3: Gelişmiş Hafıza ve RAG (Advanced Context & Memory)
- **Sliding Window & Summary Memory:** Token sınırı dolduğunda otomatik özetleme.
- **Vector DB Adaptörleri:** Chroma/FAISS entegrasyonu (`VectorMemory`).
- **Semantik Önbellek (Semantic Cache):** API maliyetini düşüren caching.

### FAZ 4: Güvenlik, Hata Yönetimi ve Kontrol
- **API Fallback Mekanizması:** Sağlayıcı çökerse otomatik geçiş.
- **Human-in-the-Loop:** Kritik işlemler öncesi onay bekleme.
- **Halüsinasyon / Güvenlik Filtreleri:** Çıktı ayrıştırıcıları.
- **Kapsamlı Hata Sınıfları:** Özel Python Exception sınıfları.

### FAZ 5: Eklentiler, Arayüzler ve Çoklu Ajan
- **UI Veri Üreticileri:** Waveform, Viseme, Progress.
- **Hazır Sistem Araçları Paketi:** Kütüphane ile gelen default tool'lar (web arama vb.).
- **Multi-Agent Orkestratörü:** Ajanların kendi aralarında iletişim kurabilmesi.
