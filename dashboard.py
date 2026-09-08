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
# 🧹 FUNGSI BERSIHKAN
# ==============================================
def bersihkan_teks(x):
    if pd.isna(x): return ""
    return str(x).replace('"', '').replace("\\", "").strip()

def bersihkan_angka(x):
    if pd.isna(x): return 0
    teks = str(x).replace('"', '').replace("\\", "").replace(",", "").replace(".", "").strip()
    try: return float(teks)
    except: return 0

# ==============================================
# 📖 BACA DATA — DENGAN PEMISAH YANG BENAR!
# ==============================================
@st.cache_data
def baca_data():
    df = pd.read_csv(
        "data_laporan.csv",
        sep=",",              # ← Sesuai berkas yang disimpan
        encoding="utf-8",
        on_bad_lines="skip",
        low_memory=False
    )
    
    st.info(f"📋 Jumlah kolom terbaca: {len(df.columns)}")
    st.info(f"📋 Nama kolom: {list(df.columns[:10])}")
    
    # ✅ Ambil berdasarkan NAMA kolom (sesuai kode yang menyimpan data)
    if "tanggal" in df.columns:
        df["tanggal"] = pd.to_datetime(df["tanggal"], errors="coerce")
        st.success(f"✅ Kolom tanggal terbaca! Contoh: {df['tanggal'].dropna().iloc[0] if len(df['tanggal'].dropna())>0 else 'tidak ada'}")
    else:
        st.error("❌ Kolom 'tanggal' TIDAK DITEMUKAN!")
        st.write("Kolom yang tersedia:", list(df.columns))
        st.stop()
    
    if "jumlah" in df.columns:
        df["jumlah"] = df["jumlah"].apply(bersihkan_angka)
        st.success(f"✅ Kolom jumlah terbaca! Total: Rp {df['jumlah'].sum():,.0f}")
    else:
        st.error("❌ Kolom 'jumlah' TIDAK DITEMUKAN!")
        st.stop()
    
    if "jenis" in df.columns:
        df["jenis"] = df["jenis"].astype(str)
    else:
        df["jenis"] = "DONASI"
    
    df["tahun"] = df["tanggal"].dt.year
    df["bulan"] = df["tanggal"].dt.strftime("%Y-%m")
    
    return df

st.info("🔄 Sedang memuat data...")
df = baca_data()

# Periksa data tanggal
if df["tanggal"].isna().sum() == len(df):
    st.error("❌ SEMUA tanggal tidak terbaca!")
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
