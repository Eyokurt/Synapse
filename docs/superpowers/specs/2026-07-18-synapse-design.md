# Synapse Kütüphanesi Tasarım ve Yol Haritası (100 Özellikli Master Plan)

## Proje Bağlamı ve Vizyon
Bu proje, geliştiricilerin AI asistanları inşa etmesini kolaylaştıran modüler, platformdan bağımsız, düşük gecikmeli (low-latency streaming odaklı) ve otonom ajanları (Agentic Loops) destekleyen kapsamlı bir Python kütüphanesidir. 

Aşağıdaki yol haritası, brainstorm aşamasında belirlenen **100 farklı özelliği**, projenin çöp olmasını (spaghetti code) engelleyecek mantıksal bir sıraya ve katmanlı mimariye oturtmaktadır. Geliştirme süreci tamamen bu sıralamaya sadık kalarak, çekirdekten dışa doğru yapılacaktır.

---

## FAZ 1: Çekirdek Altyapı ve DX (The Solid Foundation)
En yüksek öncelikli kısım. Asistanın çalışması için gerekli temel motor ve geliştirici deneyimini (DX) sağlayan modüller.

- [ ] **1. Tek Satırda Başlatma:** `Assistant(persona="Uzman").start_cli()` diyerek asistanı anında ayağa kaldırma.
- [ ] **2. Olay Veriyolu (Event Bus):** `EventEmitter` sınıfı ile asenkron olay dinleme ve fırlatma.
- [ ] **3. Özel Callback Sistemi:** `on_token_generated`, `on_speech_started`, `on_error` olayları.
- [ ] **4. Tam Tip Desteği (Type Hinting):** IDE (VS Code) otomatik tamamlama desteği.
- [ ] **5. Hazır Exception (Hata) Sınıfları:** Özel Python Exception sınıfları (`TokenLimitError`, `APIKeyInvalidError`).
- [ ] **6. .env Otomatik Yükleyici:** API anahtarlarını `.env` dosyasından otomatik bulup validate etme.
- [ ] **7. LLM Adaptör Katmanı:** OpenAI, Anthropic, Gemini vb. API'lerin standart bir arayüzle soyutlanması.
- [ ] **8. Sistem Promptu Birleştirici:** Persona, kurallar ve hafızayı arka planda otomatik olarak birleştirme.
- [ ] **9. Jinja Prompt Şablonlama:** Değişkenleri dinamik olarak promptlara basma.
- [ ] **10. Agentic Loop Engine:** Otonom ReAct döngüsünü (Düşün->Araç Kullan->Cevapla) açıp kapatabilme özelliği.
- [ ] **11. Temel Hafıza Yönetimi:** Basit `Memory` mesaj listesi ve rol tabanlı (user/assistant) saklama.
- [ ] **12. Çevrimdışı Geliştirme (Mock) Modu:** Geliştirme yaparken maliyet yaratmayan fake-response modu.
- [ ] **13. Debug ve Trace Modu:** Konsola veri akışını adım adım basan modül.
- [ ] **14. Sıfır Konfigürasyon Veritabanı:** Konuşmaları yerel SQLite'a otomatik kaydeden gömülü (embedded) DB modülü.
- [ ] **15. Kesinti Desteği (Graceful Shutdown):** Uygulama kapandığında state'i kaydetme ve açılınca geri yükleme.

## FAZ 2: Fonksiyon Çağırma ve LLM Optimizasyonu (Tooling & LLM)
Ajanın dış dünyayla etkileşime girmesini sağlayan modüller.

- [ ] **16. `@assistant_tool` Dekoratörü:** Herhangi bir Python fonksiyonunu ajanın aracı yapma.
- [ ] **17. Otomatik Şema Üretici:** Fonksiyon docstring'lerinden OpenAI JSON Tool şeması oluşturma.
- [ ] **18. Hazır Sistem Araçları:** Web araması yapma, dosya okuma, saat/tarih (10+ hazır araç).
- [ ] **19. Tool Hata Kurtarma:** Fonksiyon hata verirse LLM'e geri fırlatıp tekrar denemesini sağlayan retry döngüsü.
- [ ] **20. Tool Çıktısı Maskeleme:** Çok uzun dönen yanıtları filtreleme.
- [ ] **21. Paralel Tool Çalıştırma:** İki ayrı fonksiyonu asenkron olarak aynı anda tetikleme.
- [ ] **22. Human-in-the-Loop:** Kritik işlemler (kredi kartı vb.) öncesi döngüyü durdurup UI'dan onay (True/False) bekleme.
- [ ] **23. İnsan Onayı Bekleme Mekanizması:** Pause & resume yeteneği.
- [ ] **24. Güvenli Sandboxing:** Code Interpreter ile yazılan Python kodunu güvenli ortamda çalıştırma.
- [ ] **25. Kod Yorumlayıcı (Code Interpreter):** Lokal bilgisayarda veya Docker'da python çalıştırıp sonucu yanıta ekleme.
- [ ] **26. Tool Callback'leri:** Bir araç kullanıldığında dış bir UI sistemini tetikleme (`on_tool_start`).
- [ ] **27. Yapısal Çıktı Garantisi (Pydantic):** Yanıtın kesinlikle bir JSON formatında gelmesini zorlama.
- [ ] **28. Çoklu Sağlayıcı API Fallback:** Eğer bir API çökerse kodu değiştirmeden otomatik diğerine geçiş.
- [ ] **29. Model Yönlendirici (Router):** Kolay soruları ucuz modele, zor soruları zeki modele gönderme.
- [ ] **30. Anlamsal Yönlendirme (Semantic Routing):** Intent'e göre tamamen farklı pipeline'lara dallanma.

## FAZ 3: Ses ve Akış (Voice & Streaming Pipeline)
Düşük gecikmeli ses iletişimi.

- [ ] **31. Tek Satır STT->LLM->TTS:** Saf sesten sese pipeline.
- [ ] **32. Akış Yöneticisi (Stream Orchestrator):** STT metnini anında LLM'e, kelimeleri anında TTS'e aktarma.
- [ ] **33. Kesintisiz Akış (End-to-End Streaming):** Yanıt hızını milisaniyelere düşürme.
- [ ] **34. Chunked Streaming Birleştirici:** Karmaşık stream parçacıklarını temiz bir metin akışına çevirme.
- [ ] **35. Akıllı Sessizlik Algılama (VAD):** Kullanıcının ne zaman sustuğunu tespit etme.
- [ ] **36. Ses Formatı Düzeltici:** 16kHz, mono resampling.
- [ ] **37. Otomatik Ses Sıkıştırma:** Sesi API'ye yollamadan mp3/opus'a çevirme.
- [ ] **38. Ses Normalizasyonu:** Zayıf sesin kazancını artırma, paraziti azaltma.
- [ ] **39. Arka Plan Gürültüsü Filtreleme:** Dip ses temizleyici.
- [ ] **40. Çoklu Hoparlör Ayrımı (Diarization):** Kaç kişinin konuştuğunu ayırma.
- [ ] **41. Konuşma Duygu Analizi:** Gelen sesin tonundan duygu çıkarımı (metadata).
- [ ] **42. Ses Tonu Uyumu:** Kullanıcı kızgınsa asistanın ses tonunu ayarlama.
- [ ] **43. Hazır Ses Klonlama Arayüzü:** 5 saniyelik referans ile klonlama.
- [ ] **44. Dudak Senkronizasyonu (Viseme Data):** 3D avatarlar için dudak hareketi datası yayınlama.
- [ ] **45. Offline Fallback:** İnternet yoksa lokal STT/TTS (Whisper.cpp) modellerine geçiş.
- [ ] **46. Bekleme Sesleri (Filler Words):** Asistan düşünürken "hmm", "bir saniye" gibi sesler atması.
- [ ] **47. Söz Kesme (Interruption / Barge-in) Desteği:** Asistan konuşurken araya girildiğinde anında susma.
- [ ] **48. Gerçek Zamanlı Görselleştirme (Visualizer Data):** UI waveform için Hz/Amplitude veri akışı.

## FAZ 4: Gelişmiş Hafıza ve RAG (Advanced Context & Memory)
Büyük veriyi ve geçmişi hatırlama.

- [ ] **49. Otomatik Pencere Yönetimi (Sliding Window):** Token sınırı dolduğunda kırpma.
- [ ] **50. Otomatik Özetleyici Hafıza:** Eski konuşmaları arkaplanda özetleyerek tutma.
- [ ] **51. Çoklu Kullanıcı (Multi-tenant) Hafıza:** `user_id` parametresiyle binlerce kullanıcının contextini ayırma.
- [ ] **52. Dinamik Context Window Optimizasyonu:** Modeline göre context'i akıllıca boyutlandırma.
- [ ] **53. Anlamsal Önbellek (Semantic Cache):** Aynı soru sorulduğunda maliyeti sıfırlayan LLM cache.
- [ ] **54. Zaman Farkındalığı (Time-Aware Memory):** Asistana sistem saatini devamlı enjekte etme.
- [ ] **55. Unutma Mekanizması (TTL):** Bilgilerin sadece 1 saat tutulması.
- [ ] **56. Hafıza İçe/Dışa Aktarma:** Asistan hafızasını JSON import/export etme.
- [ ] **57. Ekstrem Sıkıştırma (Prompt Compression):** LLMLingua gibi yaklaşımlarla contexti sıkıştırma.
- [ ] **58. Kullanıcı Profili Çıkarımı:** Düzenli olarak kullanıcı gerçeklerini (isim, yaş, hobi) ayıklayıp profilleme.
- [ ] **59. Tak-Çalıştır Vektör DB:** Chroma/FAISS entegrasyonlu `VectorMemory`.
- [ ] **60. Bağlam İçi Dosya Yükleme (Drop-in RAG):** `add_document("rapor.pdf")` ile anında analiz.
- [ ] **61. RAG için Bilgi Grafiği (Knowledge Graph):** Metinlerden graph veri yapısı çıkarma.
- [ ] **62. Etkileşimli Tablo İşleyici:** RAG için CSV/Excel okuma.

## FAZ 5: Çoklu Modallik ve Arayüz (Vision & UI Bridges)
Metin dışı veri türleri ve frontend köprüleri.

- [ ] **63. Video Kare Çıkarıcı:** Videoyu FPS'e bölüp VLM'e gönderme.
- [ ] **64. Görüntüden Bağlam Okuma:** Resim dosyasını sohbete ekleme.
- [ ] **65. Ekran Okuyucu Entegrasyonu:** Asistanın ekran kaydı alarak bilgisayarda ne olduğunu anlaması.
- [ ] **66. Gözlem (Observation) Modu:** Pasif olarak ekran/mikrofon dinleyip bağlam toplama.
- [ ] **67. Sesli Wake-Word Tespiti:** Arkaplanda çalışıp "Hey Asistan" duyduğunda uyanma.
- [ ] **68. LLM Destekli Resim Üretme:** Midjourney/DALL-E entegrasyonu.
- [ ] **69. Web URL Okuyucu:** Link verildiğinde sayfa metnini arkadan scrape etme.
- [ ] **70. Çıktı Belgesi Oluşturma:** Sohbet sonunda otomatik PDF/Markdown rapor çıktısı alma.
- [ ] **71. Durum Makinesi (State Machine):** `idle`, `listening`, `processing`, `speaking` callbackleri.
- [ ] **72. React/Next.js Hook Üretici:** Frontend ekibi için otomatik `useAssistant` hook şablonu oluşturucu.
- [ ] **73. İlerleme Çubuğu Verisi (Progress):** Uzun işlemlerde UI'a `% bitti` verisi atma.
- [ ] **74. Markdown Stream Ayrıştırıcı:** Tablo/kod bloklarını UI için yolda ayrıştırma.
- [ ] **75. Akıllı UI Teması Tetikleyiciler:** Asistanın cevabıyla uygulamanın temanın değişmesini sağlayan eventler.

## FAZ 6: Dağıtım, Ağ ve Orkestrasyon (Integrations)
Uygulamayı farklı platformlara taşıma ve ajanları yönetme.

- [ ] **76. FastAPI Adaptörü:** Tek satırda asistanı REST API'ye dönüştürme.
- [ ] **77. Hazır WebSockets Sınıfı:** Socket.io/WS sunucusunu ayağa kaldırma.
- [ ] **78. GraphQL Desteği:** REST haricinde GraphQL endpoint desteği.
- [ ] **79. Discord Bot Adaptörü:** Tek satırda Discord entegrasyonu.
- [ ] **80. Telegram Bot Adaptörü:** Telegram entegrasyonu.
- [ ] **81. Redis Pub/Sub Uyumu:** Mikroservisler arası asistan haberleşmesi.
- [ ] **82. Serverless Edge Uyumluluğu:** AWS Lambda / Vercel uyumlu cold-start optimizasyonu.
- [ ] **83. Oturum Paylaşımı (State Sync):** Mobil/Masaüstü senkronizasyonu için DB eşitlemesi.
- [ ] **84. Docker Konteyner Üretici:** Otomatik Dockerfile üreten CLI komutu.
- [ ] **85. Çoklu Ajan (Multi-Agent) Sistemi:** Yazılımcı Asistan + Testçi Asistan'ın birbiriyle konuşarak görev çözmesi.
- [ ] **86. Dinamik Araç Yükleme:** Ajanın UI durumuna göre sadece o sayfadaki araçları kullanması.
- [ ] **87. Görev Planlayıcı (Task Planner):** Büyük istekleri 5 alt göreve bölüp sırayla otonom çözme.
- [ ] **88. Proaktif Asistan:** Asistanın sadece soru sorulunca değil, cron ile zamanı gelince mesaj atması.
- [ ] **89. Oto-Düzeltme (Self-Correction):** Yazdığı Python kodu hata verirse gizlice kendini düzeltip işlemi baştan alması.
- [ ] **90. Dinamik Persona/Rol Yapma:** Kullanıcı kızgınsa özür dileyen persona'ya anında geçiş.

## FAZ 7: Test, Güvenlik ve İleri Analiz (Testing, Eval & Safety)
Canlı ortama çıkmadan önceki son güvenlik kontrolleri.

- [ ] **91. Otomatik Maliyet / Token Sayacı:** Tek bir oturumun dolar/maliyet raporu.
- [ ] **92. Langfuse/Helicone Uyumlu Loglama:** Yapılan çağrıları analiz platformlarına gönderme.
- [ ] **93. Performans (Gecikme) Profilleyici:** Ses/LLM adımlarının süre ölçümü.
- [ ] **94. Token Sızıntısı (Leak) Dedektörü:** Hafızanın gereksiz şişmesini analiz eden araç.
- [ ] **95. LLM-as-a-Judge Puanlama:** Asistanın yanıtlarının başka LLM ile 1-10 arası otomatik puanlanması.
- [ ] **96. Stres Testi Botu:** Asistanı test etmek için sürekli soru soran bot.
- [ ] **97. Otomatik Senaryo Testleri (Asserts):** Pytest entegrasyonu (örn: hava durumu fonksiyonu çağrıldı mı?).
- [ ] **98. Yanıt Filtreleme (Moderasyon):** Hakaret veya NSFW engelleyici filtre.
- [ ] **99. KVKK / Veri Anonimleştirici:** Prompt öncesi TC numarası/Kredi kartı maskeleme.
- [ ] **100. Prompt Injection Koruması:** Asistanı hacklemeye çalışan jailbreak promptlarını filtreleme.
