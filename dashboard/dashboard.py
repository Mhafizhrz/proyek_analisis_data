import os
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

st.set_page_config(page_title="E-commerce Dashboard", layout="wide")

# === DATA LOADING ===
@st.cache_data
def load_main_data():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(base_dir, "main_data.csv")
    return pd.read_csv(file_path, parse_dates=['order_purchase_timestamp'])

@st.cache_data
def load_rfm_data():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(base_dir, "main_data.csv")
    df = pd.read_csv(file_path, parse_dates=['order_purchase_timestamp'])

    now = df['order_purchase_timestamp'].max()
    rfm = df.groupby('customer_unique_id').agg({
        'order_purchase_timestamp': lambda x: (now - x.max()).days,  # Recency
        'order_id': 'nunique',                                       # Frequency
        'price': 'sum'                                               # Monetary
    }).reset_index()

    rfm.columns = ['customer_id', 'Recency', 'Frequency', 'Monetary']
    rfm['R'] = pd.qcut(rfm['Recency'], 4, labels=[4, 3, 2, 1])
    rfm['F'] = pd.qcut(rfm['Frequency'].rank(method='first'), 4, labels=[1, 2, 3, 4])
    rfm['M'] = pd.qcut(rfm['Monetary'], 4, labels=[1, 2, 3, 4])
    rfm['RFM_Score'] = rfm['R'].astype(str) + rfm['F'].astype(str) + rfm['M'].astype(str)

    rfm['Segment'] = 'Others'
    rfm.loc[rfm['RFM_Score'] == '444', 'Segment'] = 'Best Customers'
    rfm.loc[rfm['RFM_Score'].str.startswith('4'), 'Segment'] = 'Recent Customers'
    rfm.loc[rfm['RFM_Score'].str.endswith('4'), 'Segment'] = 'High Spenders'
    
    return rfm

# === MAIN DATA ===
df = load_main_data()

# === SIDEBAR FILTER ===
st.sidebar.header("Filter Tanggal")
min_date = df['order_purchase_timestamp'].min().date()
max_date = df['order_purchase_timestamp'].max().date()

selected_date = st.sidebar.date_input(
    label="Pilih Rentang Tanggal",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date
)

if isinstance(selected_date, tuple) and len(selected_date) == 2:
    start_date, end_date = selected_date
    df = df[(df['order_purchase_timestamp'].dt.date >= start_date) & 
            (df['order_purchase_timestamp'].dt.date <= end_date)]

# === DASHBOARD ===
st.title("📊 E-commerce Dashboard")
st.markdown("---")

# === VISUALISASI 1: Produk Terlaris ===
st.subheader("1. Produk Paling Banyak Dibeli")
product_counts = df['product_category_name'].value_counts().head(10)
df_top = product_counts.reset_index()
df_top.columns = ['category', 'count']

fig1, ax1 = plt.subplots(figsize=(10, 6))
sns.barplot(data=df_top, x='count', y='category', hue='category', palette='viridis', dodge=False, legend=False)
ax1.set_xlabel("Jumlah Pembelian")
ax1.set_ylabel("Kategori Produk")
ax1.set_title("10 Kategori Produk Terbanyak Dibeli")
st.pyplot(fig1)

# === VISUALISASI 2: Metode Pembayaran ===
st.subheader("2. Distribusi Metode Pembayaran")
payment_counts = df['payment_type'].value_counts()
percentages = (payment_counts / payment_counts.sum()) * 100
labels = payment_counts.index.tolist()
colors = sns.color_palette('pastel')

fig2, ax2 = plt.subplots(figsize=(8, 8))
wedges, _ = ax2.pie(payment_counts, startangle=90, colors=colors, radius=0.7)
for i, (wedge, pct) in enumerate(zip(wedges, percentages)):
    theta = (wedge.theta2 + wedge.theta1) / 2.0
    radius = 0.45 + (i % 3) * 0.05
    x = radius * np.cos(np.deg2rad(theta))
    y = radius * np.sin(np.deg2rad(theta))
    ax2.text(x, y, f"{pct:.1f}%", ha='center', va='center', fontsize=10, weight='bold')
ax2.legend(wedges, labels, title="Metode", loc="center left", bbox_to_anchor=(1, 0, 0.5, 1), fontsize=9)
ax2.set_title("Distribusi Metode Pembayaran")
ax2.axis('equal')
st.pyplot(fig2)

# === VISUALISASI 3: Review ===
st.subheader("3. Distribusi Rating Pelanggan")
review_scores = df['review_score'].value_counts().sort_index()
df_review = review_scores.reset_index()
df_review.columns = ['score', 'count']

fig3, ax3 = plt.subplots(figsize=(8, 5))
sns.barplot(data=df_review, x='score', y='count', hue='score', palette='coolwarm', dodge=False, legend=False)
ax3.set_title("Distribusi Skor Review Pelanggan")
ax3.set_xlabel("Skor Review")
ax3.set_ylabel("Jumlah Review")
st.pyplot(fig3)

st.markdown("---")
st.caption("Dashboard interaktif berdasarkan filter tanggal pembelian")

# === ANALISIS LANJUTAN: RFM ===
st.header("📈 Analisis Lanjutan: Segmentasi Pelanggan (RFM)")
rfm = load_rfm_data()

# Visualisasi Segmentasi
st.subheader("Segmentasi Pelanggan Berdasarkan Skor RFM")
fig4, ax4 = plt.subplots(figsize=(10, 6))
sns.countplot(
    data=rfm,
    x='Segment',
    hue='Segment',
    order=rfm['Segment'].value_counts().index,
    palette='Set2',
    legend=False
)
ax4.set_xlabel("Segment")
ax4.set_ylabel("Jumlah Pelanggan")
ax4.set_title("Distribusi Segmentasi RFM")
st.pyplot(fig4)

# Ringkasan Statistik
st.subheader("Ringkasan Statistik Tiap Segmen")
segment_summary = rfm.groupby('Segment').agg({
    'Recency': 'mean',
    'Frequency': 'mean',
    'Monetary': ['mean', 'count']
}).round(1)
segment_summary.columns = ['Recency_Mean', 'Frequency_Mean', 'Monetary_Mean', 'Count']
segment_summary = segment_summary.sort_values(by='Monetary_Mean', ascending=False)
st.dataframe(segment_summary)