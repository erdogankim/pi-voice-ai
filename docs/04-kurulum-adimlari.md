# 04 — Kurulum Adımları

> Bu döküman, donanım eline geldikten sonra sıfırdan çalışır cihaza kadar olan tüm adımları içerir.

## Aşama A — İşletim Sistemi Kurulumu

### A.1 Raspberry Pi Imager ile SD kart hazırlama
1. Bilgisayara [Raspberry Pi Imager](https://www.raspberrypi.com/software/) indir
2. SD kartı USB okuyucuya tak
3. Imager'da:
   - **OS**: Raspberry Pi OS (64-bit) — **Bookworm** sürümü
   - **Storage**: 32GB SD kart
   - **Ayarlar (⚙️)**:
     - Hostname: `pi-voice-ai`
     - Kullanıcı adı: `pi`, şifre: (güvenli bir şifre belirle)
     - Wi-Fi: SSID + şifre
     - SSH: Etkin
     - Locale: `tr_TR.UTF-8`, Timezone: `Europe/Istanbul`
4. **WRITE** → ~10 dakika bekle
5. SD kartı Pi'ye tak

### A.2 İlk açılış
1. Ekranı, klavye-fareyi (geçici) ve gücü bağla
2. Pi açılsın, masaüstü gelsin
3. Wi-Fi bağlantısını doğrula
4. Bilgisayardan SSH ile bağlanmayı dene:
   ```bash
   ssh pi@pi-voice-ai.local
   ```

### A.3 Sistem güncelleme
```bash
sudo apt update && sudo apt full-upgrade -y
sudo apt install -y git python3-pip python3-venv python3-dev \
                    portaudio19-dev libsdl2-mixer-2.0-0 \
                    alsa-utils pulseaudio
sudo reboot
```

---

## Aşama B — Donanım Bağlantıları

### B.1 Ekran (5" HDMI dokunmatik)
1. Mikro-HDMI → HDMI kabloyu Pi'nin **HDMI 0** portuna bağla
2. Ekranın USB dokunma kablosunu Pi'nin USB portuna tak
3. Ekranın güç kablosunu (varsa) bağla
4. Pi yeniden başlat → ekran otomatik tanınmalı

> Tanınmazsa `/boot/firmware/config.txt` dosyasına ekran üreticisinin verdiği satırları ekle.

### B.2 Mikrofon ve Hoparlör
```bash
# USB mikrofonu tak, listele:
arecord -l
# Çıktıda kart numarasını not et (örn. card 1)

# Test kayıt:
arecord -D plughw:1,0 -f cd -d 5 test.wav
aplay test.wav
```

`~/.asoundrc` oluştur (varsayılan ses cihazları):
```
pcm.!default {
    type asym
    playback.pcm "plughw:0,0"
    capture.pcm  "plughw:1,0"
}
```

### B.3 Buton (GPIO 17)
Pi kapalıyken:
- Butonun bir bacağı → **GPIO 17 (Pin 11)**
- Butonun diğer bacağı → **GND (Pin 9)**
- (Opsiyonel) Buton LED: **GPIO 27 (Pin 13)** ve GND

Pi açıkken test:
```bash
python3 -c "
from gpiozero import Button
from signal import pause
btn = Button(17)
btn.when_pressed = lambda: print('Basıldı')
btn.when_released = lambda: print('Bırakıldı')
pause()
"
```
Butona bas-bırak — terminale yazmalı. `Ctrl+C` ile çık.

---

## Aşama C — Proje Kurulumu

### C.1 Depoyu indir
```bash
cd ~
git clone https://github.com/KULLANICI_ADIN/pi-voice-ai.git
cd pi-voice-ai
```

### C.2 Sanal ortam ve bağımlılıklar
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

### C.3 API anahtarları
```bash
cp .env.example .env
nano .env
```
İçine:
```
ANTHROPIC_API_KEY=sk-ant-...
OPENAI_API_KEY=sk-...
```

API anahtarlarını alma:
- **Anthropic**: https://console.anthropic.com/settings/keys
- **OpenAI**: https://platform.openai.com/api-keys

### C.4 İlk test (CLI)
```bash
python src/main.py --no-ui
```
- Butona bas → "Dinliyorum..." görünmeli
- Türkçe bir şey söyle, butonu bırak
- Birkaç saniye sonra terminalde Claude'un cevabı + hoparlörden ses

---

## Aşama D — Otomatik Başlatma (Kiosk)

### D.1 systemd servisi
```bash
sudo cp scripts/pi-voice-ai.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable pi-voice-ai
sudo systemctl start pi-voice-ai
```

Durum kontrolü:
```bash
sudo systemctl status pi-voice-ai
journalctl -u pi-voice-ai -f
```

### D.2 Kiosk modu (UI tam ekran)
`~/.config/wayfire.ini` veya `autostart` üzerinden uygulama tam ekran açılacak. Detayları `scripts/install.sh` halleder.

### D.3 Yeniden başlatma testi
```bash
sudo reboot
```
Pi açıldığında doğrudan Pi Voice AI arayüzü gelmeli.

---

## Aşama E — Sorun Giderme

| Sorun | Olası Çözüm |
|---|---|
| Ekran siyah | `config.txt`'te `hdmi_force_hotplug=1` ekle |
| Dokunma çalışmıyor | `xinput` ile cihazı listele, kalibre et |
| Mikrofon kayıt yapmıyor | `alsamixer` → mikrofonu unmute et, kazancı artır |
| Hoparlörden ses gelmiyor | `sudo raspi-config` → Audio → çıkış cihazı seç |
| GPIO 17 buton tepkisiz | Kabloları tersine bağla, GND ile başla |
| `gpiozero` import hatası | `sudo apt install python3-gpiozero` |
| API "401 Unauthorized" | `.env` dosyasındaki anahtar yanlış veya eksik |
| Whisper Türkçe anlamıyor | `language="tr"` parametresinin gönderildiğini kontrol et |
| Pi ısınıp yavaşlıyor | Soğutucu fan bağlantısını kontrol et, `vcgencmd measure_temp` |

---

## Aşama F — Doğrulama Listesi (MVP Tamamlandı)

- [ ] Pi açılışta Pi Voice AI arayüzü otomatik gelir
- [ ] Wi-Fi bağlı, internet erişimi var
- [ ] Buton basılınca "Dinliyorum" gösterilir
- [ ] Türkçe konuşma doğru transkribe ediliyor
- [ ] Claude'dan cevap geliyor
- [ ] Cevap ekranda görünüyor
- [ ] Cevap hoparlörden duyuluyor
- [ ] Konuşma geçmişi ekranda kayar şekilde tutuluyor
- [ ] Cihaz yeniden başlatıldığında her şey çalışmaya devam ediyor
