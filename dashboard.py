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
# 🧹 FUNGSI BERSIHKAN ANGKA
# ==============================================
def bersihkan_angka(x):
    if pd.isna(x): return 0
    teks = str(x).replace(",", "").replace(".", "").replace("Rp", "").strip()
    try: return float(teks)
    except: return 0

# ==============================================
# 📖 FUNGSI BACA BERKAS CSV
# ==============================================
def baca_berkas_csv(berkas):
    try:
        df = pd.read_csv(
            berkas,
            sep="\\",
            header=None,
            usecols=[2, 3, 14, 9, 10, 18, 20, 25],
            on_bad_lines="skip",
            encoding="utf-8",
            low_memory=False
        )
        df.columns = ["tanggal", "nama", "batal", "jumlah", "satuan", "kategori", "akad", "kotacabang"]
        
        df["tanggal"] = pd.to_datetime(df["tanggal"].astype(str).str.replace(",", ""), errors="coerce")
        df["jumlah"] = df["jumlah"].apply(bersihkan_angka)
        df["satuan"] = df["satuan"].astype(str).str.replace(",", "").str.strip()
        df["batal"] = pd.to_numeric(df["batal"], errors="coerce").fillna(0)
        df = df[(df["satuan"] == "Rupiah") & (df["batal"] == 0)].copy()
        
        df["tahun"] = df["tanggal"].dt.year
        df["bulan"] = df["tanggal"].dt.strftime("%Y-%m")
        return df
    except Exception as e:
        st.warning(f"⚠️ Gagal baca: {berkas.name} — {str(e)[:60]}...")
        return None

# ==============================================
# 📤 UPLOAD BERKAS DARI KOMPUTER ANDA
# ==============================================
st.header("📤 PILIH BERKAS CSV ANDA")
st.info("Pilih semua berkas CSV sekaligus → tdonasi_2024-01.csv, tdonasi_2024-02.csv ... dst")

berkas_list = st.file_uploader(
    "Pilih Berkas CSV",
    type=["csv"],
    accept_multiple_files=True,
    help="Pilih semua berkas tdonasi_*.csv sekaligus"
)

if not berkas_list:
    st.info("👆 Silakan pilih berkas CSV di atas untuk melihat laporan")
    st.stop()

# ==============================================
# 🔄 PROSES SEMUA BERKAS
# ==============================================
semua_data = []
st.info(f"📂 {len(berkas_list)} berkas dipilih → sedang diproses...")

for berkas in berkas_list:
    df = baca_berkas_csv(berkas)
    if df is not None and len(df) > 0:
        semua_data.append(df)
        st.write(f"✅ {berkas.name} → {len(df):,} baris")

if len(semua_data) == 0:
    st.error("❌ Tidak ada data yang berhasil dibaca!")
    st.stop()

# Gabungkan semua
df = pd.concat(semua_data, ignore_index=True)

st.success(f"✅ SELESAI! Total {len(df):,} baris data | {df['tanggal'].min().date()} s/d {df['tanggal'].max().date()}")
st.markdown("---")

# ==============================================
# 🔍 FILTER DATA
# ==============================================
st.sidebar.header("🔍 PILIH DATA")
tahun_tersedia = sorted(df["tahun"].dropna().unique().astype(int))
bulan_tersedia = sorted(df["bulan"].dropna().unique())

tahun_pilih = st.sidebar.multiselect("Pilih Tahun", tahun_tersedia, default=tahun_tersedia)
bulan_pilih = st.sidebar.multiselect("Pilih Bulan", bulan_tersedia, default=bulan_tersedia)

df_filter = df[(df["tahun"].isin(tahun_pilih)) & (df["bulan"].isin(bulan_pilih))]

# ==============================================
# 💵 RINGKASAN ANGKA
# ==============================================
col1, col2, col3 = st.columns(3)
total = df_filter["jumlah"].sum()
col1.metric("💰 TOTAL DONASI", f"Rp {total:,.0f}")
col2.metric("👥 JUMLAH TRANSAKSI", f"{len(df_filter):,}")
col3.metric("📅 JUMLAH BULAN", f"{df_filter['bulan'].nunique()} bulan")

st.markdown("---")

# ==============================================
# 📊 GRAFIK
# ==============================================

# Per Bulan
st.subheader("📊 PERKEMBANGAN DONASI PER BULAN")
per_bulan = df_filter.groupby("bulan")["jumlah"].sum().reset_index()
per_bulan = per_bulan.query("jumlah > 0")
fig = px.bar(per_bulan, x="bulan", y="jumlah", color="bulan", text_auto=",.0f", title="Total Donasi per Bulan")
fig.update_layout(showlegend=False)
st.plotly_chart(fig, width="stretch")

# Per Kategori
st.subheader("📊 DONASI PER KATEGORI")
per_kategori = df_filter.groupby("kategori")["jumlah"].sum().reset_index()
per_kategori = per_kategori.query("jumlah > 0")
fig = px.bar(per_kategori, x="kategori", y="jumlah", color="kategori", text_auto=",.0f", title="Total Donasi per Kategori")
fig.update_layout(showlegend=False)
st.plotly_chart(fig, width="stretch")

# Per Jenis Akad
st.subheader("📊 DONASI PER JENIS AKAD")
per_akad = df_filter.groupby("akad")["jumlah"].sum().reset_index()
per_akad = per_akad.query("jumlah > 0")
fig = px.bar(per_akad, x="akad", y="jumlah", color="akad", text_auto=",.0f", title="Total Donasi per Jenis Akad")
fig.update_layout(showlegend=False)
st.plotly_chart(fig, width="stretch")

# Per Cabang
st.subheader("🏢 DONASI PER CABANG")
per_cabang = df_filter.groupby("kotacabang")["jumlah"].sum().reset_index()
per_cabang = per_cabang.query("jumlah > 0")
fig = px.bar(per_cabang, x="kotacabang", y="jumlah", color="kotacabang", text_auto=",.0f", title="Total Donasi per Cabang")
fig.update_layout(showlegend=False)
st.plotly_chart(fig, width="stretch")

st.markdown("---")
st.success("✅ SELESAI! Data diproses dari berkas Anda! 🎉")
