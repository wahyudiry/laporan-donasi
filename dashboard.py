import pandas as pd
import plotly.express as px
import streamlit as st

# ==============================================
# 🔑 PENGATURAN HALAMAN
# ==============================================
st.set_page_config(page_title="Laporan Donasi & Kotak Amal", page_icon="📊", layout="wide")
st.title("📊 LAPORAN DONASI & KOTAK AMAL")
st.markdown("---")

# ==============================================
# 📖 BACA DATA LANGSUNG DARI BERKAS
# ==============================================
@st.cache_data
def baca_data():
    df = pd.read_csv("data_laporan.csv", encoding="utf-8")
    df["tanggal"] = pd.to_datetime(df["tanggal"], errors="coerce")
    df["tahun"] = df["tanggal"].dt.year
    df["bulan"] = df["tanggal"].dt.strftime("%Y-%m")
    return df

st.info("🔄 Sedang memuat data...")
df = baca_data()
st.success(f"✅ DATA SIAP! Total {len(df):,} baris | {df['tanggal'].min().date()} s/d {df['tanggal'].max().date()}")
st.markdown("---")

# ==============================================
# 🔍 FILTER
# ==============================================
st.sidebar.header("🔍 PILIH DATA")
jenis_pilih = st.sidebar.multiselect("Jenis Data", sorted(df["jenis"].unique()), default=sorted(df["jenis"].unique()))
tahun_tersedia = sorted(df["tahun"].dropna().unique().astype(int))
bulan_tersedia = sorted(df["bulan"].dropna().unique())

tahun_pilih = st.sidebar.multiselect("Pilih Tahun", tahun_tersedia, default=tahun_tersedia)
bulan_pilih = st.sidebar.multiselect("Pilih Bulan", bulan_tersedia, default=bulan_tersedia)

df_filter = df[
    (df["jenis"].isin(jenis_pilih)) &
    (df["tahun"].isin(tahun_pilih)) &
    (df["bulan"].isin(bulan_pilih))
]

# ==============================================
# 💵 RINGKASAN ANGKA
# ==============================================
col1, col2, col3, col4 = st.columns(4)
total_donasi = df_filter[df_filter["jenis"]=="DONASI"]["jumlah"].sum()
total_kotak = df_filter[df_filter["jenis"]=="KOTAK AMAL"]["jumlah"].sum()
total_semua = df_filter["jumlah"].sum()
jumlah_transaksi = len(df_filter)

col1.metric("💰 TOTAL DONASI", f"Rp {total_donasi:,.0f}")
col2.metric("📦 TOTAL KOTAK AMAL", f"Rp {total_kotak:,.0f}")
col3.metric("🏆 TOTAL KESELURUHAN", f"Rp {total_semua:,.0f}")
col4.metric("👥 JUMLAH TRANSAKSI", f"{jumlah_transaksi:,}")

st.markdown("---")

# ==============================================
# 📊 GRAFIK
# ==============================================

st.subheader("📊 PERKEMBANGAN PER BULAN")
per_bulan = df_filter.groupby(["bulan", "jenis"])["jumlah"].sum().reset_index()
fig = px.bar(per_bulan, x="bulan", y="jumlah", color="jenis", barmode="group",
             text_auto=",.0f", title="Total Donasi & Kotak Amal per Bulan")
st.plotly_chart(fig, use_container_width=True)

st.subheader("📊 DONASI PER KATEGORI")
per_kategori = df_filter.groupby("kategori")["jumlah"].sum().reset_index()
per_kategori = per_kategori.query("jumlah > 0")
fig = px.bar(per_kategori, x="kategori", y="jumlah", color="kategori",
             text_auto=",.0f", title="Total per Kategori")
fig.update_layout(showlegend=False)
st.plotly_chart(fig, use_container_width=True)

st.subheader("📊 PER JENIS AKAD")
per_akad = df_filter.groupby("akad")["jumlah"].sum().reset_index()
per_akad = per_akad.query("jumlah > 0")
fig = px.bar(per_akad, x="akad", y="jumlah", color="akad",
             text_auto=",.0f", title="Total per Jenis Akad")
fig.update_layout(showlegend=False)
st.plotly_chart(fig, use_container_width=True)

st.subheader("🏢 PER CABANG/KANTOR")
per_cabang = df_filter.groupby("cabang")["jumlah"].sum().reset_index()
per_cabang = per_cabang.query("jumlah > 0")
fig = px.bar(per_cabang, x="cabang", y="jumlah", color="cabang",
             text_auto=",.0f", title="Total per Cabang/Kantor")
fig.update_layout(showlegend=False)
st.plotly_chart(fig, use_container_width=True)

st.markdown("---")
st.success("✅ LAPORAN SIAP DIBAGIKAN! 🎉")
st.info("📤 Kirim tautan ini ke atasan — langsung muncul laporan tanpa upload berkas!")
