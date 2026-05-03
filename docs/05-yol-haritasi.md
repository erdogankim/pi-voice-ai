# 05 — Yol Haritası

Aşamalı geliştirme planı. Her aşama tamamlandığında çalışan bir sürüm elde edilir.

## 🟦 Aşama 0 — Planlama ve Dökümantasyon (ŞU AN)

- [x] Proje tanımı yazıldı
- [x] Donanım listesi taslağı çıkarıldı
- [x] Yazılım mimarisi belirlendi
- [ ] Donanım kararları kesinleştirildi (Pi modeli, ekran, mikrofon, buton)
- [ ] Bütçe onaylandı
- [ ] Git deposu oluşturuldu ve dökümanlar yüklendi

## 🟨 Aşama 1 — Donanım Temin ve Kurulum

- [ ] Parçalar sipariş edildi
- [ ] Raspberry Pi OS kuruldu
- [ ] Wi-Fi ve SSH yapılandırıldı
- [ ] Ekran takıldı, dokunma test edildi
- [ ] Mikrofon takıldı, kayıt testi yapıldı
- [ ] Hoparlör takıldı, ses çıkışı test edildi
- [ ] Buton GPIO'ya bağlandı, basma testi yapıldı

## 🟧 Aşama 2 — Komut Satırı Prototipi

> Hedef: Ekran/UI olmadan, sadece terminal üzerinden çalışan ilk sürüm.

- [ ] Buton basıldığında kayıt başlatan Python betiği
- [ ] Kaydı dosyaya yazma, bırakıldığında durdurma
- [ ] Kaydı OpenAI Whisper'a gönderme, metni alma
- [ ] Metni Claude API'sine gönderme, cevabı alma
- [ ] Cevabı TTS ile seslendirme
- [ ] Tüm akışı tek dosyada birleştirme

**Çıktı**: Buton + mikrofon + hoparlör ile çalışan, ekransız tam fonksiyonel cihaz.

## 🟩 Aşama 3 — Dokunmatik Arayüz

- [ ] UI çatısı seçimi (Kivy / PyQt) ve "Merhaba Dünya"
- [ ] Konuşma geçmişi gösteren ana ekran
- [ ] "Dinliyor / Düşünüyor / Cevaplıyor" durum göstergesi
- [ ] Ayarlar ekranı (model seçimi, ses seviyesi, tema)
- [ ] Wi-Fi yapılandırma ekranı

## 🟦 Aşama 4 — Kasa ve Montaj

- [ ] 3D model tasarımı (veya hazır kutu seçimi)
- [ ] Baskı / kesim
- [ ] Bileşenlerin yerleştirilmesi
- [ ] Kablo düzenlemesi
- [ ] Dayanıklılık testi

## 🟪 Aşama 5 — Cilalama ve Yayın

- [ ] `systemd` ile otomatik açılış
- [ ] Kiosk modu (uygulama tam ekran, çıkışsız)
- [ ] Güncelleme mekanizması (`git pull` + restart)
- [ ] Hata günlükleri
- [ ] Kullanıcı kılavuzu (PDF)
- [ ] Açık kaynak yayını (GitHub)

## 🌟 Aşama 6+ — Geleceğe Yönelik

- Wake-word (uyandırma kelimesi) ile sürekli dinleme
- Yerel/offline YZ desteği (Pi 5 + uygun model)
- Pil/şarj devresi → taşınabilir sürüm
- LED durum halkası
- Çoklu kullanıcı sesi tanıma
- Ev otomasyon entegrasyonu (Home Assistant)

---

## ⏱️ Tahmini Süre

| Aşama | Süre Tahmini |
|---|---|
| 0. Planlama | 1 hafta |
| 1. Donanım kurulum | 1-2 hafta (kargo dahil) |
| 2. CLI prototip | 1-2 hafta |
| 3. UI | 2-3 hafta |
| 4. Kasa | 1-2 hafta |
| 5. Cilalama | 1 hafta |
| **TOPLAM (MVP)** | **7-11 hafta** |
