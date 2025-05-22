import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

st.set_page_config(page_title="E-commerce Dashboard", layout="wide")

@st.cache_data

def load_data():
    df = pd.read_csv("main_data.csv", parse_dates=['order_purchase_timestamp'])
    return df

# Load dataset
df = load_data()

# Sidebar filter
st.sidebar.header("Filter")

min_date = df['order_purchase_timestamp'].min().date()
max_date = df['order_purchase_timestamp'].max().date()

selected_date = st.sidebar.date_input(
    label="Pilih rentang tanggal",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date
)

# Filter berdasarkan tanggal
if isinstance(selected_date, tuple) and len(selected_date) == 2:
    start_date, end_date = selected_date
    df = df[(df['order_purchase_timestamp'].dt.date >= start_date) &
            (df['order_purchase_timestamp'].dt.date <= end_date)]

st.title("📊 E-commerce Dashboard")
st.markdown("---")

# 1. Produk paling banyak dibeli
st.subheader("1. Produk Paling Banyak Dibeli")
product_counts = df['product_category_name'].value_counts().head(10)
fig1, ax1 = plt.subplots()
sns.barplot(x=product_counts.values, y=product_counts.index, ax=ax1, palette="Blues_d")
ax1.set_xlabel("Jumlah Pembelian")
ax1.set_ylabel("Kategori Produk")
st.pyplot(fig1)

# 2. Pola penggunaan metode pembayaran
st.subheader("2. Pola Penggunaan Metode Pembayaran")
payment_counts = df['payment_type'].value_counts()
fig2, ax2 = plt.subplots()
sns.barplot(x=payment_counts.values, y=payment_counts.index, ax=ax2, palette="Greens_d")
ax2.set_xlabel("Jumlah Transaksi")
ax2.set_ylabel("Metode Pembayaran")
st.pyplot(fig2)

# 3. Tingkat kepuasan pelanggan
st.subheader("3. Tingkat Kepuasan Pelanggan Berdasarkan Rating")
review_scores = df['review_score'].value_counts().sort_index()
fig3, ax3 = plt.subplots()
sns.barplot(x=review_scores.index, y=review_scores.values, ax=ax3, palette="Oranges")
ax3.set_xlabel("Skor Review")
ax3.set_ylabel("Jumlah")
st.pyplot(fig3)

st.markdown("---")
st.caption("Interaktif berdasarkan filter tanggal pembelian")
