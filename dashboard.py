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
# 📖 BACA DATA — BACA TANGGAL DARI KOLOM ASLI
# ==============================================
@st.cache_data
def baca_data():
    # Baca berkas CSV dengan pemisah koma
    df = pd.read_csv(
        "data_laporan.csv",
        sep=",",
        encoding="utf-8",
        on_bad_lines="skip",
        low_memory=False
    )
    
    st.info(f"📋 Jumlah kolom terbaca: {len(df.columns)}")
    
    # === Cari kolom tanggal & BERSIHKAN DARI GARIS MIRING ===
    if "tanggal" in df.columns:
        # Hapus garis miring & spasi kosong, lalu ubah jadi tanggal
        df["tanggal_bersih"] = df["tanggal"].astype(str).str.replace(r"[\\s'\"-]", "", regex=True).str.strip()
        # Coba baca dengan berbagai format
        df["tanggal"] = pd.to_datetime(df["tanggal_bersih"], format="%Y-%m-%d", errors="coerce")
        df["tanggal"] = df["tanggal"].fillna(pd.to_datetime(df["tanggal_bersih"], errors="coerce"))
        
        jumlah_tanggal_benar = df["tanggal"].notna().sum()
        st.info(f"📅 Tanggal terbaca benar: {jumlah_tanggal_benar:,} baris")
        
        if jumlah_tanggal_benar > 0:
            contoh = df[df["tanggal"].notna()]["tanggal"].iloc[0].date()
            st.success(f"✅ Contoh tanggal: {contoh}")
    else:
        st.error("❌ Kolom 'tanggal' TIDAK DITEMUKAN!")
        st.write("Kolom yang tersedia:", list(df.columns))
        st.stop()
    
    # === Baca jumlah ===
    if "jumlah" in df.columns:
        df["jumlah"] = pd.to_numeric(df["jumlah"], errors="coerce").fillna(0)
        st.success(f"✅ Total nilai: Rp {df['jumlah'].sum():,.0f}")
    else:
        st.error("❌ Kolom 'jumlah' TIDAK DITEMUKAN!")
        st.stop()
    
    # === Baca jenis ===
    if "jenis" in df.columns:
        df["jenis"] = df["jenis"].astype(str).str.strip()
    else:
        df["jenis"] = "DONASI"
    
    # === Buat kolom tahun & bulan ===
    df["tahun"] = df["tanggal"].dt.year
    df["bulan"] = df["tanggal"].dt.strftime("%Y-%m")
    
    return df

st.info("🔄 Sedang memuat data...")
df = baca_data()

# Periksa apakah ada tanggal yang terbaca
jumlah_tanggal_benar = df["tanggal"].notna().sum()
if jumlah_tanggal_benar == 0:
    st.error("❌ TANGGAL MASIH TIDAK TERBACA!")
    st.write("📋 5 Baris pertama kolom tanggal:")
    st.dataframe(df[["tanggal", "tanggal_bersih"]].head(10))
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
