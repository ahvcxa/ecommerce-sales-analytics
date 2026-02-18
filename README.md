# 🛒 E-Ticaret Satış Analizi ve Öneri Sistemi

Bu proje, 72 saatlik Ideathon kapsamında geliştirilen bir veri analizi ve görselleştirme çözümüdür. E-ticaret verilerini temizler, analiz eder ve kullanıcı dostu bir dashboard üzerinden sunar.

## 📂 Proje Mimarisi (Klasör Yapısı)

Düzenli çalışmak için aşağıdaki klasör yapısına sadık kalıyoruz:

* **`data/`**: Veri setleri burada durur.
    * `raw/`: Ham (işlenmemiş) veriler.
    * `processed/`: Temizlenmiş ve analize hazır veriler.
* **`notebooks/`**: Deneme kodları ve analizler (Jupyter Notebook).
* **`src/`**: Projenin ana mantık kodları (Fonksiyonlar, temiz kod).
* **`dashboard/`**: Streamlit/Dash arayüz kodları.
* **`requirements.txt`**: Gerekli kütüphaneler.

## 👥 Ekip ve Roller

* **Dilara (Data Engineer):** Veri temizleme, `data/processed` klasörünü besleme.
* **Eren (Data Analyst):** Keşifsel veri analizi, trend analizleri (`notebooks/`).
* **Adal (Algorithm Architect):** Proje mimarisi, öneri motoru algoritmaları (`src/`).
* **Batuhan (UI/UX Developer):** Dashboard tasarımı ve görselleştirme (`dashboard/`).
