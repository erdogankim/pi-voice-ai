# Git'e Koyma Kılavuzu

Bu döküman, projeyi GitHub'a (veya başka bir Git sağlayıcısına) nasıl yükleyeceğini anlatır.

## Seçenek 1 — GitHub'a Yeni Depo

### 1. GitHub'da yeni depo oluştur
- https://github.com/new adresine git
- **Repository name**: `pi-voice-ai`
- **Description**: "Raspberry Pi tabanlı bas-konuş yapay zeka cihazı"
- **Public** seç (açık kaynak için) veya **Private**
- ⚠️ **README, .gitignore, license EKLEME** — biz zaten ekledik

### 2. Yerel makinede projeyi başlat
```bash
cd pi-voice-ai
git init
git add .
git commit -m "İlk commit: Proje dökümantasyonu ve iskelet"
git branch -M main
git remote add origin https://github.com/erdogankim/pi-voice-ai.git
git push -u origin main
```

### 3. Doğrula
GitHub sayfanı yenile, dosyalar görünmeli.

---

## Seçenek 2 — Sadece Yerel Git

Bulut servisine yüklemek istemiyorsan:
```bash
cd pi-voice-ai
git init
git add .
git commit -m "İlk commit: Proje dökümantasyonu ve iskelet"
```

İleride uzak depo eklemek istersen yukarıdaki `git remote add` adımını uygulayabilirsin.

---

## Sürekli Çalışma Akışı

Her değişiklikten sonra:
```bash
git add .
git commit -m "Anlamlı bir değişiklik mesajı"
git push
```

Pi'ye en güncel sürümü çekmek için:
```bash
cd ~/pi-voice-ai
git pull
```

---

## Dal (Branch) Stratejisi

| Dal | Amaç |
|---|---|
| `main` | Çalışan, kararlı sürüm |
| `dev` | Aktif geliştirme |
| `feature/*` | Yeni özellikler (örn. `feature/wake-word`) |

Yeni özellik için:
```bash
git checkout -b feature/yeni-ozellik
# çalış, commit'le
git push -u origin feature/yeni-ozellik
# GitHub'da Pull Request aç
```

---

## ⚠️ Hassas Dosyalar

Bunlar **asla** Git'e gitmez (`.gitignore`'da listeli):
- `.env` — API anahtarları
- `*.wav`, `*.mp3` — Ses kayıtları
- `history.db` — Konuşma geçmişi
- `__pycache__/` — Python derleme dosyaları

Yanlışlıkla `.env` commit edersen:
```bash
git rm --cached .env
git commit -m ".env'i takipten çıkar"
# API anahtarlarını DERHAL iptal et ve yenilerini al
```
