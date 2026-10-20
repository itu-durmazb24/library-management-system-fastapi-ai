# 📚 Kütüphane Yönetim Sistemi & AI Asistanı API

FastAPI ve PostgreSQL kullanılarak geliştirilmiş; kitap takibi, üyelik yönetimi, ödünç ve ceza hesaplama mekanizmaları ile Google Gemini tabanlı Text-to-SQL sohbet asistanını bir araya getiren kapsamlı bir RESTful API projesidir.

---

## 🚀 Özellikler

- **Kullanıcı & Personel Yönetimi:** Yönetici şifresiyle korunan yönetici kaydı, kütüphane çalışanları ve üyeler için CRUD işlemleri.
- **Kitap & Stok Takibi:** Dinamik arama ve filtreleme (isim, yazar, kategori, müsaitlik durumu), kitap ekleme ve silme kontrolleri.
- **Ödünç & Ceza Mekanizması:** 
  - Dinamik ödünç alma limiti ve teslim süresi kontrolleri.
  - Günlük ceza hesaplama ve geciken kitapların takibi.
  - Ceza ödeme ve süre uzatma kuralları.
- **Değerlendirme & Yorum Sistemi:** Kitaplara 1-5 arası puan verme ve kullanıcı yorumları.
- **İşlem Geçmişi (Audit Log):** Sistemde yapılan tüm kritik işlemlerin loglanması.
- **🤖 LLM Destekli Sohbet Asistanı (Text-to-SQL):** Kullanıcının doğal dilde sorduğu soruları arka planda SQL sorgusuna çevirip PostgreSQL'den veri çeken ve insansı yanıtlar üreten yapay zeka entegrasyonu.

---

## 🛠️ Teknolojiler

- **Backend:** Python 3.13, FastAPI, Uvicorn, Pydantic
- **Veritabanı:** PostgreSQL
- **Yapay Zeka (LLM):** Google Gemini API (`google-genai`)
- **Dokümantasyon:** Swagger UI / OpenAPI

---

## 📋 API Uç Noktaları (Endpoints)

### Yönetici & Personel
- `POST /yoneticiler` - Özel şifre ile sistem yöneticisi ekleme
- `GET /calisanlar` - Çalışan personelleri listeleme
- `POST /calisanlar/calisanekle` - Yeni personel ekleme
- `DELETE /calisanlar/calisansil` - Personel silme

### Üyeler
- `GET /uyeler` - Kayıtlı üyeleri listeleme
- `POST /uyeler/uyeekle` - Yeni üye kaydı oluşturma
- `DELETE /uyeler/uyesil` - Üye silme
- `GET /uyeler/cezalar` - Ceza durumu olan üyeleri görme
- `POST /uyeler/cezalar/cezaode` - Üye borç ödeme işlemi
- `GET /uyeler/gecmis` - Kullanıcının geçmiş işlemlerini listeleme

### Kitaplar
- `GET /kitaplar` - Tüm kitapları ve durumlarını listeleme
- `POST /kitaplar/kitapekle` - Yeni kitap girişi yapma
- `DELETE /kitaplar/kitapsil` - Kitap silme (Ödünçte olan kitaplar silinemez)
- `GET /kitaplar/ara` - Dinamik filtreleme ile kitap arama
- `GET /kitaplar/populer` - En çok okunan kitapları listeleme

### Ödünç & İade İşlemleri
- `GET /kitaplar/oduncler` - Aktif ödünç kayıtları
- `POST /kitaplar/oduncler/oduncal` - Kitap ödünç alma
- `POST /kitaplar/oduncler/oduncver` - Kitap iade etme (Gecikme cezası hesabı ile)
- `GET /kitaplar/oduncler/gecikenler` - Teslim tarihi geçmiş kitaplar
- `POST /kitaplar/oduncler/sureuzat` - Teslim süresini uzatma

### Değerlendirme & Yorumlar
- `POST /kitaplar/degerlendir` - Kitaba puan (1-5) ve yorum bırakma
- `GET /kitaplar/yorumlar` - Kitap yorumlarını okuma

### Sistem & Ayarlar
- `GET /istatistikler` - Genel sistem ve kütüphane istatistikleri
- `GET /gecmis` - Sistem denetim günlükleri (Audit log)
- `PUT /ayarlar` - Dinamik parametreleri güncelleme (Ceza tutarı, süre, limit)

### Yapay Zeka
- `POST /sohbet` - Doğal dilde soru-cevap ve veritabanı sorgulama asistanı

---

## ⚙️ Kurulum ve Çalıştırma

1. **Depoyu Klonlayın:**
   ```bash
   git clone https://github.com/itu-durmazb24/library-management-system-fastapi-ai.git
   cd library-management-system-fastapi-ai