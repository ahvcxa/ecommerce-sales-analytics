# Batuhan'ın Streamlit kodu. src'deki fonksiyonları çağıracak

import streamlit as st
import sys
import os

# BEST PRACTICE: Python'un 'src' klasörünü bulabilmesi için ana dizini sisteme tanıtıyoruz
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

# Artık kendi yazdığın beyni buraya çağırabilirsin!
from src.recommender import get_recommendations, sim_df

# Web sitesinin başlığı
st.title("E-Ticaret Akıllı Öneri Motoru 🚀")
st.write("Müşterilerin sepet alışkanlıklarına göre ürün önerileri.")

# Kullanıcıya rastgele yazı yazdırmak yerine, veritabanındaki ürünleri bir açılır menü (Dropdown) ile sunalım
urun_listesi = sim_df.columns.tolist()
secilen_urun = st.selectbox("Lütfen bir ürün seçin:", urun_listesi)

# Butona basıldığında olacaklar
if st.button("Benzer Ürünleri Öner"):
    st.success(f"**{secilen_urun}** alan müşterilerimizin ilgilendiği diğer ürünler:")
    
    oneriler = get_recommendations(secilen_urun)
    
    # Gelen listeyi ekranda alt alta şık bir şekilde yazdırıyoruz
    for i, urun in enumerate(oneriler, 1):
        st.write(f"{i}. {urun}")
