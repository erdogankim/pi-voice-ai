# Pi Voice AI — Bas-Konuş Yapay Zeka Cihazı

Raspberry Pi 4 üzerinde çalışan, fiziksel butonu ile **bas-konuş (push-to-talk)** mantığıyla Anthropic Claude'a soru soran, cevabı dokunmatik ekran üzerinde gösteren ve sesli olarak okuyan bir DIY (Kendin Yap) cihaz projesi.

## 🎯 Proje Amacı

Kaliteli, taşınabilir, kendi başına çalışan bir yapay zeka iletişim terminali oluşturmak. Telefon veya bilgisayar açmadan, tek bir butona basıp soru sorulabilen ve cevap alınabilen bağımsız bir donanım.

## ⚙️ Temel Özellikler

- **Bas-Konuş (PTT) Butonu** — Fiziksel düğmeye basılı tutulduğunda mikrofon dinler, bırakıldığında ses YZ'a gönderilir
- **Dokunmatik Ekran Arayüzü** — Soru/cevap geçmişi, durum bilgileri (Kivy ile)
- **Türkçe Sesli Cevap** — OpenAI TTS ile doğal sesli okuma
- **Anthropic Claude** — Cevap üretici olarak Claude Sonnet 4.5
- **OpenAI Whisper** — Konuşmadan-metne (STT)
- **Bağımsız Çalışma** — Wi-Fi haricinde harici cihaza ihtiyaç yok

## 🧰 Donanım

| Bileşen | Model |
|---|---|
| Ana kart | Raspberry Pi 4 Model B (4GB) |
| Ekran | 5" HDMI kapasitif dokunmatik |
| Mikrofon | USB konferans mikrofonu |
| Hoparlör | 3W aktif (USB veya 3.5mm) |
| Buton | 30mm arcade tipi |

Detaylı liste → [`docs/02-donanim-listesi.md`](docs/02-donanim-listesi.md)

## 🏗️ Mimari Özet

```
[BUTON] → [Mikrofon] → [Whisper STT] → [Claude] → [TTS + Ekran]
```

Detay → [`docs/03-yazilim-mimarisi.md`](docs/03-yazilim-mimarisi.md)

## 📁 Depo Yapısı

```
pi-voice-ai/
├── README.md                  # Bu dosya
├── docs/                      # Tüm proje dökümantasyonu
│   ├── 01-proje-tanimi.md
│   ├── 02-donanim-listesi.md
│   ├── 03-yazilim-mimarisi.md
│   ├── 04-kurulum-adimlari.md
│   └── 05-yol-haritasi.md
├── src/                       # Kaynak kod (Aşama 2'den itibaren)
├── config/                    # Yapılandırma
├── scripts/                   # Kurulum ve servis dosyaları
├── tests/                     # Testler
├── requirements.txt
├── .env.example               # API anahtarı şablonu
└── .gitignore
```

## 🚦 Mevcut Durum

🟦 **Aşama 0 — Planlama tamamlandı** ✅

🟨 **Sıradaki: Aşama 1 — Donanım temin ve kurulum**

Detaylı plan → [`docs/05-yol-haritasi.md`](docs/05-yol-haritasi.md)

## 💸 Tahmini Maliyet

- **Donanım (tek seferlik)**: ~6.400 TRY
- **API kullanımı (aylık)**: ~7 USD (günlük 50 etkileşim varsayımı)

## 🚀 Hızlı Başlangıç (Donanım hazır olduğunda)

```bash
git clone https://github.com/KULLANICI_ADIN/pi-voice-ai.git
cd pi-voice-ai
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env  # API anahtarlarını gir
python src/main.py
```

Tam kurulum → [`docs/04-kurulum-adimlari.md`](docs/04-kurulum-adimlari.md)

## 📜 Lisans

MIT (önerilen) — kesinleşince eklenecek.

## 🤝 Katkı

Bu proje aktif olarak geliştirilmektedir. Geri bildirim ve katkılar memnuniyetle karşılanır.
