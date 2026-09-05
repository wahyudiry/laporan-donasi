import pandas as pd

# ==============================================
# 🔑 LOKASI FOLDER BERKAS CSV ANDA
# ==============================================
folder = "D:/Data_Donasi/"

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
# 📖 BACA & GABUNGKAN SEMUA BERKAS DONASI
# ==============================================
# DAFTAR NAMA BERKAS DONASI — tambah/kurangi sesuai yang Anda miliki!
daftar_donasi = [
    "tdonasi_2024-01.csv",
    "tdonasi_2024-02.csv",
    "tdonasi_2024-03.csv",
    "tdonasi_2024-04.csv",
    "tdonasi_2024-05.csv",
    "tdonasi_2024-06.csv",
    "tdonasi_2024-07.csv",
    "tdonasi_2024-08.csv",
    "tdonasi_2024-09.csv",
    "tdonasi_2024-10.csv",
    "tdonasi_2024-11.csv",
    "tdonasi_2024-12.csv",
    "tdonasi_2025-01.csv",
    "tdonasi_2025-02.csv",
    "tdonasi_2025-03.csv",
    "tdonasi_2025-04.csv",
    "tdonasi_2025-05.csv",
    "tdonasi_2025-06.csv",
    "tdonasi_2025-07.csv",
    # Tambahkan baris di atas untuk bulan berikutnya
]

# DAFTAR NAMA BERKAS KOTAK AMAL
daftar_kotak = [
    "tkotakamal_2024-01.csv",
    "tkotakamal_2024-02.csv",
    "tkotakamal_2024-03.csv",
    "tkotakamal_2024-04.csv",
    "tkotakamal_2024-05.csv",
    "tkotakamal_2024-06.csv",
    "tkotakamal_2024-07.csv",
    "tkotakamal_2024-08.csv",
    "tkotakamal_2024-09.csv",
    "tkotakamal_2024-10.csv",
    "tkotakamal_2024-11.csv",
    "tkotakamal_2024-12.csv",
    "tkotakamal_2025-01.csv",
    "tkotakamal_2025-02.csv",
    "tkotakamal_2025-03.csv",
    "tkotakamal_2025-04.csv",
    # Tambahkan baris di atas untuk bulan berikutnya
]

# ==============================================
# 🔄 PROSES SEMUA BERKAS
# ==============================================
semua_data = []

print("🔄 SEDANG MEMPROSES BERKAS DONASI...")
for nama in daftar_donasi:
    try:
        lokasi = folder + nama
        df = pd.read_csv(lokasi, sep='"', on_bad_lines="skip", encoding="utf-8", low_memory=False)
        df = df.iloc[:, [2, 3, 8, 9, 10, 17, 19, 5]].copy()
        df.columns = ["tanggal", "nama", "jumlah", "satuan", "cabang", "kategori", "akad", "kota"]
        df["tanggal"] = pd.to_datetime(df["tanggal"].astype(str).str.replace("\\", ""), errors="coerce")
        df["jumlah"] = df["jumlah"].apply(bersihkan_angka)
        df = df[df["jumlah"] > 0].copy()
        df["jenis"] = "DONASI"
        df["tahun"] = df["tanggal"].dt.year
        df["bulan"] = df["tanggal"].dt.strftime("%Y-%m")
        semua_data.append(df)
        print(f"✅ {nama} → {len(df):,} baris")
    except Exception as e:
        print(f"⚠️ {nama}: {str(e)[:60]}")

print("\n🔄 SEDANG MEMPROSES BERKAS KOTAK AMAL...")
for nama in daftar_kotak:
    try:
        lokasi = folder + nama
        df = pd.read_csv(lokasi, sep='"', on_bad_lines="skip", encoding="utf-8", low_memory=False)
        df = df.iloc[:, [2, 3, 10, 7, 8, 4]].copy()
        df.columns = ["tanggal", "nama", "jumlah", "kategori", "akad", "cabang"]
        df["tanggal"] = pd.to_datetime(df["tanggal"].astype(str).str.replace("\\", ""), errors="coerce")
        df["jumlah"] = df["jumlah"].apply(bersihkan_angka)
        df = df[df["jumlah"] > 0].copy()
        df["jenis"] = "KOTAK AMAL"
        df["satuan"] = "Rupiah"
        df["tahun"] = df["tanggal"].dt.year
        df["bulan"] = df["tanggal"].dt.strftime("%Y-%m")
        semua_data.append(df)
        print(f"✅ {nama} → {len(df):,} baris")
    except Exception as e:
        print(f"⚠️ {nama}: {str(e)[:60]}")

# ==============================================
# 💾 GABUNGKAN & SIMPAN BERKAS BARU
# ==============================================
if len(semua_data) == 0:
    print("\n❌ TIDAK ADA DATA YANG BERHASIL DIBACA!")
else:
    df_gabung = pd.concat(semua_data, ignore_index=True)
    df_gabung.to_csv("data_laporan.csv", index=False, encoding="utf-8")
    print(f"\n🎉 ✅ SELESAI!")
    print(f"📊 TOTAL DATA: {len(df_gabung):,} baris")
    print(f"📅 PERIODE: {df_gabung['tanggal'].min().date()} s/d {df_gabung['tanggal'].max().date()}")
    print(f"💾 BERKAS TERSIMPAN: data_laporan.csv")
