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
    if pd.isna(x):
        return 0
    teks = str(x).replace(",", "").replace(".", "").replace("Rp", "").strip()
    try:
        return float(teks)
    except:
        return 0

# ==============================================
# 📖 BACA BERKAS DONASI (tdonasi)
# ==============================================
def baca_donasi(berkas):
    try:
        df = pd.read_csv(
            berkas,
            sep='"',               # ← Pemisah tanda kutip
            on_bad_lines="skip",
            encoding="utf-8",
            low_memory=False
        )
        # Bersihkan nama kolom & ambil yang penting
        df = df.iloc[:, [2, 3, 8, 9, 10, 17, 19, 5]].copy()
        df.columns = ["tanggal", "nama", "jumlah", "satuan", "cabang", "kategori", "akad", "kota"]
        
        df["tanggal"] = pd.to_datetime(df["tanggal"].astype(str).str.replace("\\", ""), errors="coerce")
        df["jumlah"] = df["jumlah"].apply(bersihkan_angka)
        df["satuan"] = df["satuan"].astype(str).str.replace("\\", "").str.strip()
        df = df[(df["satuan"].str.contains("Rupiah", case=False, na=True))].copy()
        
        df["tahun"] = df["tanggal"].dt.year
        df["bulan"] = df["tanggal"].dt.strftime("%Y-%m")
        df["jenis"] = "DONASI"
        return df
    except Exception as e:
        st.warning(f"⚠️ {berkas.name}: {str(e)[:80]}...")
        return None

# ==============================================
# 📖 BACA BERKAS KOTAK AMAL (tkotakamal)
# ==============================================
def baca_kotakamal(berkas):
    try:
        df = pd.read_csv(
            berkas,
            sep='"',               # ← Pemisah tanda kutip
            on_bad_lines="skip",
            encoding="utf-8",
            low_memory=False
        )
        # Posisi kolom berbeda dengan tdonasi!
        df = df.iloc[:, [2, 3, 10, 7, 8, 4]].copy()
        df.columns = ["tanggal", "nama", "jumlah", "kategori", "akad", "cabang"]
        df["satuan"] = "Rupiah"
        
        df["tanggal"] = pd.to_datetime(df["tanggal"].astype(str).str.replace("\\", ""), errors="coerce")
        df["jumlah"] = df["jumlah"].apply(bersihkan_angka)
        
        df["tahun"] = df["tanggal"].dt.year
        df["bulan"] = df["tanggal"].dt.strftime("%Y-%m")
        df["jenis"] = "KOTAK AMAL"
        return df
    except Exception as e:
        st.warning(f"⚠️ {berkas.name}: {str(e)[:80]}...")
        return None

# ==============================================
# 📤 PILIH BERKAS CSV
# ==============================================
st.header("📤 PILIH BERKAS CSV ANDA")
st.info("Pilih SEMUA berkas: tdonasi_*.csv DAN tkotakamal_*.csv")

berkas_list = st.file_uploader(
    "Pilih Semua Berkas CSV",
    type=["csv"],
    accept_multiple_files=True,
    help="Pilih tdonasi_...csv DAN tkotakamal_...csv sekaligus"
)

if not berkas_list:
    st.info("👆 Silakan pilih berkas CSV di atas")
    st.stop()

# ==============================================
# 🔄 PROSES SEMUA BERKAS
# ==============================================
semua_donasi = []
semua_kotak = []

st.info(f"📂 {len(berkas_list)} berkas dipilih → sedang diproses...")

for berkas in berkas_list:
    nama = berkas.name.lower()
    if nama.startswith("tdonasi_"):
        df = baca_donasi(berkas)
        if df is not None and len(df) > 0:
            semua_donasi.append(df)
            st.write(f"✅ {berkas.name} → {len(df):,} baris")
    elif nama.startswith("tkotakamal_"):
        df = baca_kotakamal(berkas)
        if df is not None and len(df) > 0:
            semua_kotak.append(df)
            st.write(f"✅ {berkas.name} → {len(df):,} baris")
    else:
        st.info(f"ℹ️ Lewati: {berkas.name}")

# Gabungkan semua
semua = []
if len(semua_donasi) > 0:
    semua.extend(semua_donasi)
if len(semua_kotak) > 0:
    semua.extend(semua_kotak)

if len(semua) == 0:
    st.error("❌ Tidak ada data yang berhasil dibaca!")
    st.stop()

df = pd.concat(semua, ignore_index=True)
st.success(f"✅ SELESAI! Total {len(df):,} baris data | {df['tanggal'].min().date()} s/d {df['tanggal'].max().date()}")
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
st.success("✅ SELESAI! 🎉")
