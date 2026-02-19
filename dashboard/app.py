import streamlit as st
import sys
import os
import pandas as pd
import plotly.express as px # Alan grafiği için eklendi

# Ana dizini sisteme tanıtıyoruz
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

# Tüm fonksiyonları içeri aktarıyoruz
from src.data_loader import load_data
from src.analysis import calculate_kpis, get_monthly_sales, get_category_performance
from src.recommender import get_recommendations, sim_df # Batuhan'ın importları eklendi

# Sayfa Ayarları
st.set_page_config(page_title="E-Ticaret Dashboard", layout="wide")

@st.cache_data
def fetch_data():
    return load_data()

df = fetch_data()

# --- SOL MENÜ ---
st.sidebar.title("Navigasyon 🧭")
secilen_sayfa = st.sidebar.radio("Sayfa Seçin:", ["Genel Bakış", "Kategori Analizi", "Akıllı Öneri Motoru"])

if df.empty:
    st.error("Veri yüklenemedi! Lütfen terminali kontrol et.")
    st.stop()

# --- SAYFALAR ---

if secilen_sayfa == "Genel Bakış":
    st.title("📊 Satış Trendleri ve KPI'lar")
    
    # 1. KPI Kartları
    kpis = calculate_kpis(df)
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Toplam Ciro", f"₺{kpis['total_revenue']:,.0f}")
    col2.metric("Toplam Sipariş", kpis['total_orders'])
    col3.metric("Müşteri Sayısı", kpis['total_customers'])
    col4.metric("Ortalama Sepet", f"₺{kpis['avg_order_value']:,.0f}")
    
    st.markdown("---")
    
    # 2. Aylık Satış Trendi (Alan Grafiği)
    st.subheader("Aylık Ciro Trendi")
    monthly_sales = get_monthly_sales(df)
    
    fig = px.area(
        x=monthly_sales.index, 
        y=monthly_sales.values, 
        labels={'x': 'Tarih', 'y': 'Toplam Ciro (₺)'},
        color_discrete_sequence=['#636EFA'] # Hoş bir mavi tonu
    )
    fig.update_layout(margin=dict(l=0, r=0, t=30, b=0)) # Boşlukları kırptık
    st.plotly_chart(fig, use_container_width=True)

elif secilen_sayfa == "Kategori Analizi":
    st.title("📦 Kategori ve Ürün Performansı")
    
    # 1. Kategori Dağılımı (Pasta Grafik)s
    st.subheader("Kategorilerin Ciroya Katkısı")
    cat_perf = get_category_performance(df)
    
    fig_pie = px.pie(
        cat_perf, 
        values='TotalAmount', 
        names='CategoryName', 
        hole=0.3 # Ortası delik (Donut) stili daha modern durur
    )
    st.plotly_chart(fig_pie, use_container_width=True)
    
    st.markdown("---")
    
    # 2. En Çok Satan 10 Ürün Tablosu
    st.subheader("🏆 En Çok Satan 10 Ürün")
    top_products = get_top_products(df, n=10)
    
    # Tabloyu daha şık göstermek için sütun isimlerini arayüzde Türkçe yapıyoruz
    top_products = top_products.rename(columns={'ProductName': 'Ürün Adı', 'TotalAmount': 'Toplam Ciro (₺)'})
    
    # Tabloyu Streamlit dataframe ile basıyoruz
    st.dataframe(top_products, use_container_width=True, hide_index=True)
    
elif secilen_sayfa == "Akıllı Öneri Motoru":
    # Batuhan'ın kodları tamamen buraya taşındı
    st.title("🚀 E-Ticaret Akıllı Öneri Motoru")
    st.write("Müşterilerin sepet alışkanlıklarına göre ürün önerileri.")

    urun_listesi = sim_df.columns.tolist()
    secilen_urun = st.selectbox("Lütfen bir ürün seçin:", urun_listesi)

    if st.button("Benzer Ürünleri Öner"):
        st.success(f"**{secilen_urun}** alan müşterilerimizin ilgilendiği diğer ürünler:")
        oneriler = get_recommendations(secilen_urun)
        for i, urun in enumerate(oneriler, 1):
            st.write(f"{i}. {urun}")