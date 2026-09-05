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
# 📖 BACA DATA — DIPERBAIKI FORMATNYA!
# ==============================================
@st.cache_data
def baca_data():
    df = pd.read_csv(
        "data_laporan.csv",
        sep=",",               # ← pemisah koma (standar CSV hasil gabungan)
        encoding="utf-8",
        on_bad_lines="skip",
        low_memory=False
    )
    df["tanggal"] = pd.to_datetime(df["tanggal"], errors="coerce")
    df["tahun"] = df["tanggal"].dt.year
    df["bulan"] = df["tanggal"].dt.strftime("%Y-%m")
    return df

st.info("🔄 Sedang memuat data... mohon sabar sebentar...")
df = baca_data()

if df["tanggal"].isna().all():
    st.error("❌ Tanggal belum terbaca dengan benar!")
    st.dataframe(df.head(3))  # ← tampilkan contoh agar bisa diperiksa
    st.stop()

st.success(f"✅ DATA SIAP! Total {len(df):,} baris | {df['tanggal'].min().date()} s/d {df['tanggal'].max().date()}")
st.markdown("---")

# ==============================================
# 🔍 FILTER
# ==============================================
st.sidebar.header("🔍 PILIH DATA")

jenis_pilih = ["DONASI", "KOTAK AMAL"]
if "jenis" in df.columns:
    jenis_unik = sorted(df["jenis"].dropna().unique())
    jenis_pilih = st.sidebar.multiselect("Jenis Data", jenis_unik, default=jenis_unik)

tahun_tersedia = sorted(df["tahun"].dropna().unique().astype(int))
bulan_tersedia = sorted(df["bulan"].dropna().unique())
tahun_pilih = st.sidebar.multiselect("Pilih Tahun", tahun_tersedia, default=tahun_tersedia)
bulan_pilih = st.sidebar.multiselect("Pilih Bulan", bulan_tersedia, default=bulan_tersedia)

df_filter = df[
    (df["tahun"].isin(tahun_pilih)) &
    (df["bulan"].isin(bulan_pilih))
]
if "jenis" in df.columns:
    df_filter = df_filter[df_filter["jenis"].isin(jenis_pilih)]

# ==============================================
# 💵 RINGKASAN ANGKA
# ==============================================
col1, col2, col3, col4 = st.columns(4)
if "jenis" in df.columns:
    total_donasi = df_filter[df_filter["jenis"]=="DONASI"]["jumlah"].sum()
    total_kotak = df_filter[df_filter["jenis"]=="KOTAK AMAL"]["jumlah"].sum()
else:
    total_donasi = df_filter["jumlah"].sum()
    total_kotak = 0

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
if "jenis" in df.columns:
    per_bulan = df_filter.groupby(["bulan", "jenis"])["jumlah"].sum().reset_index()
    fig = px.bar(per_bulan, x="bulan", y="jumlah", color="jenis", barmode="group", text_auto=",.0f")
else:
    per_bulan = df_filter.groupby("bulan")["jumlah"].sum().reset_index()
    fig = px.bar(per_bulan, x="bulan", y="jumlah", text_auto=",.0f")
st.plotly_chart(fig, use_container_width=True)

if "kategori" in df.columns:
    st.subheader("📊 PER KATEGORI")
    per_kategori = df_filter.groupby("kategori")["jumlah"].sum().reset_index()
    per_kategori = per_kategori.query("jumlah > 0")
    if len(per_kategori) > 0:
        fig = px.bar(per_kategori, x="kategori", y="jumlah", color="kategori", text_auto=",.0f")
        fig.update_layout(showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

if "akad" in df.columns:
    st.subheader("📊 PER JENIS AKAD")
    per_akad = df_filter.groupby("akad")["jumlah"].sum().reset_index()
    per_akad = per_akad.query("jumlah > 0")
    if len(per_akad) > 0:
        fig = px.bar(per_akad, x="akad", y="jumlah", color="akad", text_auto=",.0f")
        fig.update_layout(showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

if "cabang" in df.columns:
    st.subheader("🏢 PER CABANG")
    per_cabang = df_filter.groupby("cabang")["jumlah"].sum().reset_index()
    per_cabang = per_cabang.query("jumlah > 0")
    if len(per_cabang) > 0:
        fig = px.bar(per_cabang, x="cabang", y="jumlah", color="cabang", text_auto=",.0f")
        fig.update_layout(showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

st.markdown("---")
st.success("✅ LAPORAN SIAP! 🎉")
