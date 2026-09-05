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
# 📖 BACA DATA — BERDASARKAN POSISI KOLOM
# ==============================================
@st.cache_data
def baca_data():
    df = pd.read_csv(
        "data_laporan.csv",
        sep=",",
        encoding="utf-8",
        on_bad_lines="skip",
        low_memory=False
    )
    
    # Tampilkan nama kolom agar bisa diperiksa
    kolom_ada = list(df.columns)
    st.info(f"📋 Kolom terbaca: {kolom_ada[:10]}")  # tampilkan 10 kolom pertama
    
    # Cari kolom tanggal — dengan berbagai kemungkinan nama
    nama_kolom = list(df.columns)
    kolom_tanggal = None
    kolom_jumlah = None
    kolom_jenis = None
    
    for i, nm in enumerate(nama_kolom):
        if str(nm).strip().lower() in ["tanggal", "tgl", "date"]:
            kolom_tanggal = nm
        if str(nm).strip().lower() in ["jumlah", "nilai", "total"]:
            kolom_jumlah = nm
        if str(nm).strip().lower() in ["jenis", "tipe"]:
            kolom_jenis = nm
    
    # Kalau tidak ketemu nama kolom, pakai posisi
    if kolom_tanggal is None and len(nama_kolom) >= 3:
        kolom_tanggal = nama_kolom[2]  # posisi kolom tanggal
    if kolom_jumlah is None and len(nama_kolom) >= 9:
        kolom_jumlah = nama_kolom[8]   # posisi kolom jumlah
    
    # Proses tanggal
    df["tanggal"] = pd.to_datetime(df[kolom_tanggal], errors="coerce")
    df["jumlah"] = pd.to_numeric(df[kolom_jumlah], errors="coerce").fillna(0)
    
    if kolom_jenis:
        df["jenis"] = df[kolom_jenis].astype(str)
    else:
        df["jenis"] = "DONASI"  # nilai bawaan
    
    df["tahun"] = df["tanggal"].dt.year
    df["bulan"] = df["tanggal"].dt.strftime("%Y-%m")
    
    return df

st.info("🔄 Sedang memuat data...")
df = baca_data()

# Periksa apakah tanggal terbaca
if df["tanggal"].isna().sum() == len(df):
    st.error("❌ Kolom tanggal belum terbaca dengan benar!")
    st.write("📋 5 Baris pertama berkas Anda:")
    st.dataframe(df.head(5))
    st.stop()

st.success(f"✅ DATA SIAP! Total {len(df):,} baris | {df['tanggal'].min().date()} s/d {df['tanggal'].max().date()}")
st.markdown("---")

# ==============================================
# 🔍 FILTER
# ==============================================
st.sidebar.header("🔍 PILIH DATA")
jenis_unik = sorted(df["jenis"].dropna().unique())
jenis_pilih = st.sidebar.multiselect("Jenis Data", jenis_unik, default=jenis_unik)

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
total_kotak = df_filter[df_filter["jenis"].str.contains("KOTAK|kotak", case=False, na=False)]["jumlah"].sum()
total_semua = df_filter["jumlah"].sum()
jumlah_transaksi = len(df_filter)

col1.metric("💰 TOTAL DONASI", f"Rp {total_donasi:,.0f}")
col2.metric("📦 TOTAL KOTAK AMAL", f"Rp {total_kotak:,.0f}")
col3.metric("🏆 TOTAL KESELURUHAN", f"Rp {total_semua:,.0f}")
col4.metric("👥 JUMLAH TRANSAKSI", f"{jumlah_transaksi:,}")

st.markdown("---")

# ==============================================
# 📊 GRAFIK PER BULAN
# ==============================================
st.subheader("📊 PERKEMBANGAN PER BULAN")
per_bulan = df_filter.groupby(["bulan", "jenis"])["jumlah"].sum().reset_index()
fig = px.bar(per_bulan, x="bulan", y="jumlah", color="jenis", barmode="group", text_auto=",.0f")
st.plotly_chart(fig, use_container_width=True)

st.markdown("---")
st.success("✅ LAPORAN SIAP! 🎉")
