# Veri yükleme ve temizleme fonksiyonları
import pandas as pd
import os

def load_data():
    """
    Bu fonksiyon işlenmiş (processed) klasöründeki tüm CSV dosyalarını okur,
    gerekli birleştirmeleri (Merge) yapar ve analize hazır 'Master DataFrame' döndürür.
    """
    
    # 1. Dosya Yollarını Dinamik Belirleme
    # Bu dosyanın (data_loader.py) olduğu yerden 2 üst klasöre çık, data/processed'a gir.
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    DATA_PATH = os.path.join(BASE_DIR, 'data')

    try:
        # 2. Dosyaları Oku
        df_orders = pd.read_csv(os.path.join(DATA_PATH, 'clean_orders.csv'))
        df_details = pd.read_csv(os.path.join(DATA_PATH, 'clean_ordersdetails.csv'))
        df_products = pd.read_csv(os.path.join(DATA_PATH, 'clean_products.csv'))
        df_customers = pd.read_csv(os.path.join(DATA_PATH, 'clean_customers.csv'))
        df_categories = pd.read_csv(os.path.join(DATA_PATH, 'clean_categories.csv'))

        # 3. Tarih Formatını Düzelt
        df_orders['OrderDate'] = pd.to_datetime(df_orders['OrderDate'])

        # 4. BÜYÜK BİRLEŞTİRME (The Merge)
        df_master = df_details.merge(df_orders, on='OrderID', how='left') \
                              .merge(df_products, on='ProductID', how='left') \
                              .merge(df_categories, on='CategoryID', how='left') \
                              .merge(df_customers, on='CustomerID', how='left')

        # 5. Temizlik (Tarihi olmayanları temizle)
        df_master = df_master.dropna(subset=['OrderDate'])

        # 6. Feature Engineering (Yeni Sütunlar)
        df_master['Month'] = df_master['OrderDate'].dt.month_name()
        df_master['Year'] = df_master['OrderDate'].dt.year
        df_master['Month_Year'] = df_master['OrderDate'].dt.to_period('M').astype(str)

        print("✅ Veri başarıyla yüklendi ve birleştirildi!")
        return df_master

    except FileNotFoundError as e:
        print(f"❌ HATA: Dosya bulunamadı! {e}")
        return pd.DataFrame() # Hata olursa boş tablo dön