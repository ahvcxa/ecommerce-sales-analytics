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
from src.analysis import calculate_kpis, get_monthly_sales, get_category_performance, get_top_products,calculate_rfm,get_daily_sales_performance
from src.recommender import get_recommendations, sim_df 

# Sayfa Ayarları
st.set_page_config(page_title="E-Ticaret Dashboard", layout="wide")

@st.cache_data
def fetch_data():
    return load_data()

df = fetch_data()

# --- SOL MENÜ ---
st.sidebar.title("Navigasyon 🧭")
secilen_sayfa = st.sidebar.selectbox("Sayfa Seçin:", ["Genel Bakış", "Kategori Analizi", "Bölgesel Analiz", "Müşteri Segmentasyonu", "Sepet Analizi", "Akıllı Öneri Motoru"])
st.sidebar.markdown("---")
st.sidebar.subheader("📅 Tarih Filtresi")
    
    # Veritabanındaki en eski ve en yeni tarihi bul
min_date = df['OrderDate'].min().date()
max_date = df['OrderDate'].max().date()
    
    # Kullanıcıya takvim sun
secilen_tarihler = st.sidebar.date_input(
        "Aralık Seçin:", 
    [min_date, max_date], 
    min_value=min_date, 
    max_value=max_date
)
st.sidebar.markdown("---")
st.sidebar.caption("🍀 **Project Team** 🍀")
st.sidebar.write("Batuhan • Adal Su • Eren • Dilara")
st.sidebar.caption("v1.0.0 | © 2026 BAED")
    # Eğer kullanıcı iki tarih seçtiyse veriyi filtrele
if len(secilen_tarihler) == 2:
        baslangic, bitis = secilen_tarihler
        df = df[(df['OrderDate'].dt.date >= baslangic) & (df['OrderDate'].dt.date <= bitis)]
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
        color_discrete_sequence=['#2E7D32'] 
    )
    fig.update_layout(margin=dict(l=0, r=0, t=30, b=0)) # Boşlukları kırptık
    st.plotly_chart(fig, use_container_width=True)
    st.markdown("---")
    st.subheader("📅 Günlük Satış Performansı")
    
    daily_df = get_daily_sales_performance(df)
    
    fig_daily = px.bar(
        daily_df, 
        x='Gun_Adi', 
        y='TotalAmount',
        labels={'Gun_Adi': 'Gün', 'TotalAmount': 'Toplam Satış (₺)'},
        color='TotalAmount',
        color_continuous_scale='Viridis',
        text_auto='.2s'
    )
    # Rakamları Türk usulü formatla (opsiyonel ama şık durur)
    fig_daily.update_layout(xaxis_title="", yaxis_title="Ciro (₺)")
    
    st.plotly_chart(fig_daily, use_container_width=True)

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
    top_products['Toplam Ciro (₺)'] = top_products['Toplam Ciro (₺)'].apply(lambda x: f"{x:,.0f}".replace(',', '.'))
    
    # Tabloyu Streamlit dataframe ile basıyoruz
    st.dataframe(top_products, use_container_width=True, hide_index=True)
    st.markdown("---")
    st.subheader("🗺️ Ürün Satış Yoğunluk Haritası")
    st.write("Kutuların büyüklüğü ve koyu yeşil tonları, ürünün toplam cirodaki ağırlığını gösterir.")
    
    # Kategori ve ürün bazında ciroları toparla
    tree_df = df.groupby(['CategoryName', 'ProductName'])['TotalAmount'].sum().reset_index()
    tree_df = tree_df[tree_df['TotalAmount'] > 0] # Sadece satışı olanları al
    
    # Treemap Çizimi
    fig_tree = px.treemap(
        tree_df, 
        path=['CategoryName', 'ProductName'], 
        values='TotalAmount',
        color='TotalAmount',
        color_continuous_scale='Greens' 
    )
    fig_tree.update_traces(root_color="lightgrey")
    fig_tree.update_layout(margin=dict(t=10, l=10, r=10, b=10))
    
    st.plotly_chart(fig_tree, use_container_width=True)
    
elif secilen_sayfa == "Akıllı Öneri Motoru":
    st.title("🤖 Akıllı Öneri ve Sadakat Motoru")
    
    tab1, tab2 = st.tabs(["Ürün Bazlı Öneri", "Müşteriye Özel Fırsatlar"])
    
    with tab1:
        st.subheader("🔍 Ürüne Göre Benzerlerini Bul")
        
        # Kullanıcının bir ürün seçmesini sağla
        tum_urunler = df['ProductName'].unique()
        secilen_urun = st.selectbox("Benzerlerini görmek istediğiniz ürünü seçin:", tum_urunler)
        
        if secilen_urun:
            from src.recommender import get_recommendations
            
            # Algoritmayı çalıştır ve önerileri al
            oneriler = get_recommendations(secilen_urun)
            
            if oneriler: # Liste boş değilse çalışır
                st.write(f"**'{secilen_urun}'** ürününü beğenenler bunları da beğendi:")
            
            # Önerileri yan yana sütunlar halinde göster
            # oneriler bir liste olduğu için direkt üzerinden dönebiliriz
                cols = st.columns(len(oneriler))
                for idx, urun_adi in enumerate(oneriler):
                    with cols[idx]:
                        st.info(f"📦 {urun_adi}")
                        # Liste döndüğü için benzerlik skoru elimizde yoksa caption'ı kaldırabiliriz
                        st.caption("Benzer Ürün")
            else:
                st.warning("Bu ürün için yeterli benzerlik verisi bulunamadı.")
    
    with tab2:
        st.subheader("🎯 Müşteri Segmentine Göre Akıllı Teklif")
        
        # RFM verisini al
        rfm_df = calculate_rfm(df)
        
        # Müşteri seçimi
        selected_user = st.selectbox("Analiz Edilecek Müşteri ID:", rfm_df.index)
        
        user_info = rfm_df.loc[selected_user]
        segment = user_info['Segment']
        
        # Segmentlere göre dinamik mesaj ve aksiyon
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Müşteri Segmenti", segment)
            st.write(f"**Toplam Harcama:** {user_info['Monetary']:,.0f} ₺".replace(',', '.'))
            
        with col2:
            if segment == 'Champions':
                st.success("🌟 Bu bir VIP müşteridir. Yeni koleksiyonu öncelikli gösterin.")
            elif segment == 'At Risk' or segment == 'Hibernating':
                st.warning("⚠️ Bu müşteriyi kaybetmek üzereyiz! %20 indirim kuponu tanımlayın.")
            else:
                st.info("📈 Bu müşteri düzenli alım yapıyor, sepet büyütme odaklı ürünler önerin.")

        # O MÜŞTERİNİN EN ÇOK ALDIĞI KATEGORİDEN ÖNERİ YAPALIM
        st.markdown("---")
        st.subheader(f"🎁 {selected_user} İçin Kişiselleştirilmiş Öneriler")
        
        # Müşterinin en çok harcama yaptığı kategoriyi bulalım
        user_top_cat = df[df['CustomerID'] == selected_user].groupby('CategoryName')['TotalAmount'].sum().idxmax()
        
        st.write(f"Bu müşteri en çok **{user_top_cat}** kategorisine ilgi duyuyor. İşte o kategoriden seçtiklerimiz:")
        
        cat_rec = df[df['CategoryName'] == user_top_cat]['ProductName'].unique()[:5]
        for item in cat_rec:
            st.write(f"✅ {item}")

elif secilen_sayfa == "Müşteri Segmentasyonu":
    st.title("👥 Müşteri Segmentasyonu")
    
    # Veriyi hesapla
    rfm_df = calculate_rfm(df)
    
    # 1. Bar Chart (Segment Dağılımı)
    st.subheader("Müşteri Kitlemizin Dağılımı")
    segment_counts = rfm_df['Segment'].value_counts().reset_index()
    segment_counts.columns = ['Segment', 'Müşteri Sayısı']
    
    fig_bar = px.bar(
        segment_counts, 
        x='Müşteri Sayısı', 
        y='Segment', 
        color='Segment',
        orientation='h', # Yatay çubuk grafik daha rahat okunur
        text_auto=True
    )
    fig_bar.update_layout(showlegend=False) # Renkler zaten belli, sağdaki lejantı gizleyelim yer kaplamasın
    st.plotly_chart(fig_bar, use_container_width=True)
    
    st.markdown("---")
    
    # 2. Şampiyonlar Tablosu (En Değerli Müşteriler)
    st.subheader("🏆 VIP Müşterilerimiz (Şampiyonlar)")
    champions = rfm_df[rfm_df['Segment'] == 'Champions'].reset_index()
    
    # Ekranda şık durması için sadece önemli kolonları alıp isimlendiriyoruz
    champions_display = champions[['CustomerID', 'Recency', 'Frequency', 'Monetary']]
    champions_display = champions_display.sort_values(by='Monetary', ascending=False).head(15) # En çok harcayan ilk 15 VIP
    champions_display = champions_display.rename(columns={
        'CustomerID': 'Müşteri ID', 
        'Recency': 'Son Alışveriş (Gün Önce)', 
        'Frequency': 'Toplam Sipariş', 
        'Monetary': 'Toplam Harcama (₺)'
    })
    champions_display['Toplam Harcama (₺)'] = champions_display['Toplam Harcama (₺)'].apply(lambda x: f"{x:,.0f}".replace(',', '.'))
    st.dataframe(champions_display, use_container_width=True, hide_index=True)
    
elif secilen_sayfa == "Bölgesel Analiz":
    st.title("🌍 Bölgesel Satış Dağılımı")
    
    # Şehir bazlı satışları grupla
    city_sales = df.groupby('City')['TotalAmount'].sum().reset_index()
    city_sales = city_sales.sort_values(by='TotalAmount', ascending=False)
    
    # 1. En Çok Satış Yapılan Şehirler (Bar Chart)
    st.subheader("Şehir Bazlı Ciro Sıralaması")
    fig_city = px.bar(
        city_sales.head(10), 
        x='TotalAmount', 
        y='City', 
        orientation='h',
        color='TotalAmount',
        color_continuous_scale='Blues',
        text_auto='.2s'
    )
    st.plotly_chart(fig_city, use_container_width=True)
    
    st.markdown("---")
    
    # 2. Ülke Bazlı Dağılım (Pasta Grafik)
    st.subheader("Ülkelere Göre Satış Payı")
    country_sales = df.groupby('Country')['TotalAmount'].sum().reset_index()
    fig_country = px.pie(country_sales, values='TotalAmount', names='Country', hole=0.4)
    st.plotly_chart(fig_country, use_container_width=True)

elif secilen_sayfa == "Sepet Analizi":
    st.title("🛒 Sepet Analizi ve Ürün Birliktelikleri")
    st.write("Bu analiz, hangi ürünlerin birlikte satılma ihtimalinin en yüksek olduğunu gösterir.")

    # Algoritma dosyasındaki benzerlik matrisini kullanıyoruz
    from src.recommender import sim_df
    
    # En güçlü 10 birlikteliği bulalım
    st.subheader("🔗 En Güçlü Ürün Eşleşmeleri")
    
    # Matrisi düzeltip ikili kombinasyonları çıkarıyoruz
    pairs = sim_df.unstack().reset_index()
    pairs.columns = ['Ürün A', 'Ürün B', 'Birliktelik Skoru']
    
    # Aynı ürünlerin eşleşmesini (Skor 1.0 olanlar) temizle
    pairs = pairs[pairs['Ürün A'] != pairs['Ürün B']]
    
    # En yüksek skorlu ilk 15 eşleşmeyi al (Tekrarları önlemek için sıralı alabilirsin)
    top_pairs = pairs.sort_values(by='Birliktelik Skoru', ascending=False).head(15)
    
    # Skoru daha okunabilir yap (Türk usulü nokta ile)
    top_pairs['Birliktelik Skoru'] = top_pairs['Birliktelik Skoru'].apply(lambda x: f"{x:.2f}".replace('.', ','))
    
    st.dataframe(top_pairs, use_container_width=True, hide_index=True)
    
    st.info("💡 **Aksiyon Önerisi:** Yukarıdaki tabloda birliktelik skoru yüksek olan ürünleri aynı paket (bundle) içinde kampanya ile satarak ciroyu artırabilirsiniz.")