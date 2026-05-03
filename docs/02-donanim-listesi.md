# 02 — Donanım Listesi

> ✅ **Pi 4 (4GB) seçildi.** Liste bu karara göre netleştirildi.

## 2.1 Kesin Bileşenler

| # | Bileşen | Önerilen Model | Neden | Tahmini Fiyat (TRY) |
|---|---|---|---|---|
| 1 | Ana kart | **Raspberry Pi 4 Model B (4GB)** | Yeterli RAM, geniş topluluk desteği | 2.800 |
| 2 | MicroSD | SanDisk Extreme 32GB U3 A2 | Hızlı boot, dayanıklı | 280 |
| 3 | Güç adaptörü | Resmi Pi USB-C 5V/3A | Voltaj düşüşü uyarısı yaşanmaz | 350 |
| 4 | Soğutucu | Alüminyum heatsink + fan kit | Pi 4 ısınır, fan şart | 200 |
| 5 | Dokunmatik ekran | **5" HDMI kapasitif (800x480)** | Boyut/fiyat dengesi en iyi | 1.400 |
| 6 | Mikrofon | **USB konferans mikrofonu** | Tak-çalıştır, sürücü derdi yok | 400 |
| 7 | Hoparlör | **3W USB veya 3.5mm aktif hoparlör** | Pi'nin 3.5mm jack'i kullanılabilir | 350 |
| 8 | Buton | **Arcade tipi 30mm push button** (LED'li) | Bas-konuş için ideal his | 120 |
| 9 | Direnç & Kablo | 10kΩ pull-up + jumper kablolar | Buton bağlantısı için | 80 |
| 10 | HDMI kablo | Mikro-HDMI → HDMI (kısa) | Pi 4 mikro-HDMI kullanır | 80 |
| 11 | Kasa | 3D baskı veya hazır ABS kutu | Bileşenleri barındıracak | 350 |

**Toplam tahmini bütçe: ~6.410 TRY**

## 2.2 GPIO Pin Bağlantı Şeması

```
Raspberry Pi 4 — GPIO Bağlantıları
┌─────────────────────────────────┐
│  GPIO 17 (Pin 11) → BUTON       │  ← Bas-konuş butonu
│  GND     (Pin 9)  → BUTON GND   │
│  GPIO 27 (Pin 13) → LED (+)     │  ← Buton içi LED (opsiyonel)
│  GND     (Pin 14) → LED (-)     │
│                                 │
│  USB 3.0          → MİKROFON    │
│  USB 2.0          → HOPARLÖR    │  (veya 3.5mm)
│  Mikro-HDMI 0     → EKRAN       │
│  USB              → DOKUNMA     │  (ekran dokunma sinyali)
│  USB-C            → GÜÇ         │
└─────────────────────────────────┘
```

### Buton Bağlantı Detayı
```
3.3V ──[10kΩ pull-up]── GPIO 17 ── [BUTON] ── GND
```
> Buton basılınca GPIO 17 → GND (LOW), bırakılınca pull-up ile HIGH.
> **Not**: `gpiozero` dahili pull-up sunar, harici dirence gerek kalmayabilir.

## 2.3 Alışveriş Kontrol Listesi

- [ ] Raspberry Pi 4 Model B 4GB
- [ ] 32GB MicroSD + USB kart okuyucu
- [ ] Resmi USB-C güç adaptörü (5V/3A)
- [ ] Pi 4 soğutucu seti (heatsink + fan)
- [ ] 5" HDMI kapasitif dokunmatik ekran
- [ ] USB konferans mikrofonu
- [ ] 3.5mm veya USB aktif hoparlör
- [ ] Arcade buton (30mm, LED'li tercih)
- [ ] Jumper kablo seti (dişi-dişi)
- [ ] Mikro-HDMI → HDMI kablo (30cm)
- [ ] Kasa malzemesi (3D filament veya hazır kutu)

## 2.4 Tedarik Kaynakları (Türkiye)

- **robotistan.com** — Pi ve aksesuar geniş seçenek
- **direnc.net** — Buton, kablo, direnç
- **n11 / trendyol** — USB mikrofon ve hoparlör
- **3D baskı**: 3dorbit.com.tr veya yerel makerspace

## 2.5 İleride Eklenebilecekler

- Şarj edilebilir pil + güç yönetim modülü
- WS2812 LED halka (durum göstergesi)
- Ek butonlar (geri, ses kontrolü)
- Daha büyük ekran (7" — masaüstü kullanım için)
