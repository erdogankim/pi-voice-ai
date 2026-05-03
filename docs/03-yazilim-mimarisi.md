# 03 — Yazılım Mimarisi

> ✅ **Kararlar**: Anthropic Claude (LLM) + OpenAI Whisper (STT) + OpenAI TTS

## 3.1 Genel Akış

```
[BUTON BASILDI]
      ↓
[Mikrofon kaydı başlat] ──→ Ekran: "Dinliyorum..."
      ↓
[BUTON BIRAKILDI]
      ↓
[Kayıt durdur → .wav dosyası]
      ↓
[OpenAI Whisper API] ──→ Ekran: "Anlıyorum..."
      ↓
[Metin alındı]
      ↓
[Anthropic Claude API] ──→ Ekran: "Düşünüyorum..."
      ↓
[Cevap metni alındı]
      ↓
   ├──→ [Ekrana yazdır]
   └──→ [OpenAI TTS API → mp3] → [Hoparlör] ──→ Ekran: "Konuşuyorum..."
      ↓
[Konuşma geçmişine ekle]
      ↓
[Hazır — yeni soruyu bekle]
```

## 3.2 Modüller

| Modül | Görevi | Kütüphane |
|---|---|---|
| `button_handler` | GPIO 17 buton olayları | `gpiozero` |
| `audio_recorder` | Mikrofondan kayıt | `sounddevice` + `numpy` |
| `stt_client` | OpenAI Whisper'a istek | `openai` SDK |
| `ai_client` | Claude'a soru gönder, cevap al | `anthropic` SDK |
| `tts_client` | OpenAI TTS'ten ses üret | `openai` SDK |
| `audio_player` | mp3 oynat | `pygame.mixer` |
| `ui` | Dokunmatik arayüz | `Kivy` |
| `config` | Ayarlar yönetimi | `python-dotenv` + `pyyaml` |
| `history` | Konuşma geçmişi | `sqlite3` (yerel) |
| `service` | Otomatik başlatma | `systemd` |

## 3.3 Dil ve Sürüm

- **Python 3.11+** (Raspberry Pi OS Bookworm ile gelir)
- Sanal ortam: `venv`
- Bağımlılıklar: `requirements.txt`

## 3.4 API Kullanımı

### Anthropic Claude
```python
from anthropic import Anthropic

client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

response = client.messages.create(
    model="claude-sonnet-4-5",
    max_tokens=1024,
    system="Sen Türkçe konuşan, kısa ve net cevap veren bir asistansın.",
    messages=[
        {"role": "user", "content": user_text}
    ]
)
cevap = response.content[0].text
```

### OpenAI Whisper (STT)
```python
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

with open("kayit.wav", "rb") as audio:
    transcript = client.audio.transcriptions.create(
        model="whisper-1",
        file=audio,
        language="tr"
    )
metin = transcript.text
```

### OpenAI TTS
```python
response = client.audio.speech.create(
    model="tts-1",
    voice="alloy",  # alloy, echo, fable, onyx, nova, shimmer
    input=cevap
)
response.stream_to_file("cevap.mp3")
```

## 3.5 Yapılandırma Dosyası

**`config/config.yaml`** — Genel ayarlar (Git'e eklenir)
```yaml
ai:
  model: "claude-sonnet-4-5"
  max_tokens: 1024
  system_prompt: |
    Sen Türkçe konuşan, kısa ve net cevap veren bir asistansın.
    Cevaplarını 2-3 cümleyi geçmeyecek şekilde tut.
    Sesli okunacağı için emoji ve tablo kullanma.

stt:
  model: "whisper-1"
  language: "tr"

tts:
  model: "tts-1"
  voice: "alloy"
  speed: 1.0

audio:
  sample_rate: 16000
  channels: 1
  recording_max_seconds: 30

button:
  gpio_pin: 17
  led_pin: 27
  mode: "hold"  # hold = bas-tut, toggle = bas-bırak

ui:
  theme: "dark"
  font_size: 18
  show_history: true
  history_limit: 50
```

**`.env`** — Sırlar (Git'e GİRMEZ, `.gitignore`'da)
```
ANTHROPIC_API_KEY=sk-ant-...
OPENAI_API_KEY=sk-...
```

## 3.6 Klasör Yapısı (Kod)

```
pi-voice-ai/
├── src/
│   ├── main.py                    # Giriş noktası
│   ├── button_handler.py
│   ├── audio_recorder.py
│   ├── stt_client.py
│   ├── ai_client.py
│   ├── tts_client.py
│   ├── audio_player.py
│   ├── history.py
│   ├── config.py
│   └── ui/
│       ├── app.py                 # Kivy uygulaması
│       ├── screens.py
│       └── theme.py
├── config/
│   └── config.yaml
├── tests/
│   ├── test_audio.py
│   ├── test_button.py
│   └── test_api.py
├── scripts/
│   ├── install.sh                 # Tek tıkla kurulum
│   └── pi-voice-ai.service        # systemd servisi
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

## 3.7 Hata Yönetimi

| Hata | Davranış |
|---|---|
| Wi-Fi yok | Ekran: "İnternet yok", buton pasif |
| Whisper API hatası | Ekran: "Sesi anlayamadım", tekrar dene butonu |
| Claude API hatası | Ekran: "Cevap alınamadı, tekrar dene" |
| TTS hatası | Cevabı sadece ekranda göster, ses olmadan |
| Mikrofon yok | Açılışta uyarı, çalışmama |
| API kotası dolu | Ekran: "Limit aşıldı, ayarları kontrol et" |

## 3.8 Maliyet Tahmini (Aylık API)

Günde 50 etkileşim, ortalama 200 kelime soru-cevap varsayımı:

| Servis | Aylık Tahmini Kullanım | Aylık Maliyet (USD) |
|---|---|---|
| Claude Sonnet 4.5 | ~150K input + 75K output token | ~1.50 |
| OpenAI Whisper | ~150 dakika ses | ~0.90 |
| OpenAI TTS-1 | ~300K karakter | ~4.50 |
| **TOPLAM** | | **~7 USD/ay** |

## 3.9 Güvenlik

- API anahtarları **`.env`** dosyasında, Git'e gitmez
- `.env.example` şablon olarak tutulur (boş anahtarlarla)
- Konuşma geçmişi yerel SQLite'ta, buluta gönderilmez
- Cihaz Wi-Fi şifresi NetworkManager tarafından şifrelenmiş tutulur
- API kullanım limitleri Anthropic/OpenAI panelinden ayarlanır
