# 01 — Proje Tanımı

## 1.1 Amaç

Raspberry Pi tabanlı, **bas-konuş** mantığıyla çalışan, dokunmatik ekranlı, taşınabilir bir yapay zeka iletişim cihazı yapmak. Hedef: Telefon/PC bağımlılığı olmadan, tek dokunuşla YZ'a soru sorabilen kişisel bir asistan terminali.

## 1.2 Hedef Kullanıcı

- Yapay zeka ile sürekli iletişim kuran ama her seferinde uygulama açmak istemeyen kişiler
- Kendin Yap (DIY) elektronik tutkunları
- Çocuklar/yaşlılar için sade arayüzlü YZ erişim cihazı arayanlar
- Atölye, mutfak, garaj gibi ellerin meşgul olduğu ortamlarda çalışanlar

## 1.3 Temel Kullanım Senaryosu

1. Kullanıcı cihazın **butonuna basılı tutar**.
2. Cihaz mikrofonu açar, kullanıcının sesini kaydeder.
3. Kullanıcı butonu **bırakır**.
4. Ses, **konuşmadan-metne (STT)** servisine gönderilir.
5. Çıkan metin, seçili **yapay zeka modeline** (örn. Claude) gönderilir.
6. Gelen cevap dokunmatik ekranda yazıyla görünür.
7. Aynı cevap **metinden-konuşmaya (TTS)** ile seslendirilir.
8. Tüm konuşma geçmişi ekranda kayar şekilde tutulur.

## 1.4 Başarı Kriterleri (Minimum Uygulanabilir Ürün — MVP)

- [ ] Buton basılı → ses kaydı başlıyor
- [ ] Buton bırakıldı → kayıt YZ'a gidip cevap dönüyor
- [ ] Cevap ekranda okunabilir şekilde gösteriliyor
- [ ] Cevap hoparlörden duyulabiliyor
- [ ] Cihaz açıldığında otomatik olarak çalışmaya başlıyor (kiosk modu)
- [ ] Wi-Fi yapılandırması cihaz üzerinden yapılabiliyor

## 1.5 Kapsam Dışı (İlk Sürüm İçin)

- Sürekli dinleme (wake-word) modu
- Çoklu kullanıcı desteği
- Yerel/offline YZ modeli (ileride değerlendirilebilir)
- Pil/şarj devresi (ilk sürüm prizden çalışacak)
- Kamera/görüntü işleme

## 1.6 Tasarım İlkeleri

1. **Sadelik**: Tek buton, tek ekran. Karmaşa yok.
2. **Dayanıklılık**: Çocuk veya gürültülü ortam için sağlam kasa.
3. **Hızlı tepki**: Buton bırakıldıktan en geç ~2 saniye içinde cevap akışı başlamalı.
4. **Anlaşılır arayüz**: Yaşı ne olursa olsun kullanılabilir.
5. **Onarılabilirlik**: Parçalar standart, açık kaynak, değiştirilebilir.
