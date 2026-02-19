# Adal'ın alanı
# öneri algoritması burada fonksiyon olarak olacak.

import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
import os

# --- 1. SİSTEM BAŞLARKEN BİR KERE ÇALIŞACAK KISIM (PERFORMANS İÇİN) ---
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MATRIX_PATH = os.path.join(BASE_DIR, 'data', 'user_item_matrix.csv')
# Tabloyu oku
# Eren'in matrix benzerlik tablosu.
df_matrix = pd.read_csv(MATRIX_PATH, index_col=0)

# Ürünleri satıra alıp, devasa benzerlik matrisini BİR KERE hesapla
item_matrix = df_matrix.T
# O 0'ları ve sayıları kullanarak, ürünlerin birbirine olan açısını hesaplattık:
sim_array = cosine_similarity(item_matrix)
sim_df = pd.DataFrame(sim_array, index=item_matrix.index, columns=item_matrix.index)


# --- 2. SİTE ÜZERİNDEN ÇAĞRILACAK FONKSİYON ---
def get_recommendations(product_id, top_n=5):
    # CSV'deki sütun isimleri string (yazı) olduğu için garantiye alıyoruz
    product_id = str(product_id) 
    
    # Adım A: Hata Yönetimi (Ürün hiç satılmamışsa veya yoksa)
    if product_id not in sim_df.columns:
        return ["Ürün veritabanında bulunamadı."]
    
    # Adım B: İlgili ürünün diğer tüm ürünlerle olan benzerlik puanlarını al ve büyükten küçüğe sırala
    similar_scores = sim_df[product_id].sort_values(ascending=False)
    
    # Adım C: En çok benzeyen ürün kendisidir (Puanı 1.0). Onu listeden çıkar!
    similar_scores = similar_scores.drop(product_id)
    
    # Adım D: En üstteki (en çok benzeyen) 5 ürünün ID'sini/İsmini bir liste olarak ver
    top_products = similar_scores.head(top_n).index.tolist()
    
    return top_products

# Sadece bizim testimiz için ufak bir kontrol (Web sitesine bağlandığında burası çalışmaz)
if __name__ == "__main__":
    # Veritabanındaki rastgele bir ürün kodunu (Örneğin '11' numaralı ürünü) test edelim
    # (Senin veritabanındaki gerçek bir ID ile değiştirebilirsin)
    ornek_urunler = sim_df.columns[:3] # İlk 3 ürünün ID'sini görelim
    print("Mevcut ilk 3 ürün ID'si:", ornek_urunler.tolist())
    
    test_id = ornek_urunler[0]
    print(f"\n{test_id} ID'li ürün için öneriler:")
    print(get_recommendations(test_id))