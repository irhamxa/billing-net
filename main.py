import os
import pandas as pd
from datetime import datetime, timedelta

FOLDER = "data"
FILE_ADMIN = "data/admin.csv"
FILE_PAKET = "data/paket.csv"
FILE_PELANGGAN = "data/pelanggan.csv"
FILE_PEMBAYARAN = "data/pembayaran.csv"

HEADER_ADMIN = ("username", "password")
HEADER_PAKET = ("id_paket", "nama_paket", "harga")
HEADER_PELANGGAN = ("id_pelanggan", "username", "password", "nama",
                    "alamat", "no_hp", "id_paket", "tanggal_daftar", "tanggal_berakhir")
HEADER_PEMBAYARAN = ("id_tagihan", "id_pelanggan", "bulan", "tahun",
                     "id_paket", "nominal", "status", "tanggal_b"
                     "ayar")

MASA_AKTIF = 30 
HARI_TAGIHAN = 7
BATAS_TELAT = 10  


# buat file kalau belum ada
def buat_file(namafile, header, isi):
    if not os.path.exists(namafile):
        with open(namafile, "w") as file:
            file.write(",".join(header) + "\n")
        with open(namafile, "a") as file:
            for baris in isi:
                file.write(baris + "\n")


def buat_file_awal():
    if not os.path.exists(FOLDER):
        os.makedirs(FOLDER)

    admin_awal = ["admin,admin123"]
    paket_awal = ["PKT01,Paket 10 Mbps,100000",
                  "PKT02,Paket 20 Mbps,150000",
                  "PKT03,Paket 30 Mbps,200000"]

    buat_file(FILE_ADMIN, HEADER_ADMIN, admin_awal)
    buat_file(FILE_PAKET, HEADER_PAKET, paket_awal)
    buat_file(FILE_PELANGGAN, HEADER_PELANGGAN, [])
    buat_file(FILE_PEMBAYARAN, HEADER_PEMBAYARAN, [])


# fungsi baca csv jadi dataframe
def baca(namafile):
    try:
        return pd.read_csv(namafile, dtype=str)
    except FileNotFoundError:
        print("File tidak ditemukan, membuat ulang file...")
        buat_file_awal()
        return pd.read_csv(namafile, dtype=str)


# fungsi simpan df ke csv
def simpan(df, namafile):
    df.to_csv(namafile, index=False)


def garis(panjang=70):
    print("-" * panjang)


def judul(teks):
    print("\n" + "=" * 70)
    print(teks.center(70))
    print("=" * 70)


def format_rupiah(angka):
    angka = int(angka)
    teks = f"{angka:,}".replace(",", ".")
    return "Rp" + teks


# input yang tidak boleh kosong
def input_wajib(pertanyaan):
    while True:
        nilai = input(pertanyaan).strip()
        if nilai != "":
            return nilai
        print("Input tidak boleh kosong!")


# fungsi pilihan fitur
def pilih_nomor(pertanyaan, jumlah):
    pilihan = input(pertanyaan).strip()
    if pilihan.isdigit() and 1 <= int(pilihan) <= jumlah:
        return int(pilihan) - 1
    print("Pilihan tidak valid!")
    return -1


# fungsi generate id
def buat_id(awalan, df, kolom):
    nomor_max = 0
    for id_lama in df[kolom]:
        angka = id_lama[len(awalan):]
        if angka.isdigit() and int(angka) > nomor_max:
            nomor_max = int(angka)
    return awalan + str(nomor_max + 1).zfill(2)


# fungsi id pelanggan (riwayat bayar pelanggan yang sudah dihapus ikut dicek)
def buat_id_pelanggan(pelanggan):
    bayar = baca(FILE_PEMBAYARAN)
    nomor_max = 0
    for df in (pelanggan, bayar):
        for id_lama in df["id_pelanggan"]:
            angka = id_lama[3:]
            if angka.isdigit() and int(angka) > nomor_max:
                nomor_max = int(angka)
    return "PLG" + str(nomor_max + 1).zfill(2)


def waktu_sekarang():
    sekarang = datetime.now()
    tanggal = sekarang.strftime("%Y-%m-%d")
    return tanggal, str(sekarang.month), str(sekarang.year)   # tuple


# tanggal hari ini (bentuk date, bisa dihitung selisihnya)
def hari_ini():
    return datetime.now().date()


# ubah teks "2026-11-20" jadi date
def ke_tanggal(teks):
    if teks == "-":
        return hari_ini()
    return datetime.strptime(teks, "%Y-%m-%d").date()


# sisa hari masa aktif. 0 atau negatif = masa aktif sudah habis
def hitung_sisa_hari(teks):
    return (ke_tanggal(teks) - hari_ini()).days


# cari baris pertama yang isinya cocok
def cari_index(df, kolom, nilai):
    for i in range(len(df)):
        if df.iloc[i][kolom] == nilai:
            return i
    return -1


# tambah data
def tambah_baris(df, baris):
    baru = pd.DataFrame([baris])
    if len(df) == 0:
        return baru
    return pd.concat([df, baru], ignore_index=True)


def ambil_nama_paket(id_paket):
    paket = baca(FILE_PAKET)
    k = cari_index(paket, "id_paket", id_paket)
    if k == -1:
        return "-"
    return paket.iloc[k]["nama_paket"]


def tampil_paket(paket):
    garis()
    print(f"{'No':<4}{'ID':<8}{'Nama Paket':<25}{'Harga/Bulan':<15}")
    garis()
    for i in range(len(paket)):
        print(f"{i + 1:<4}{paket.iloc[i]['id_paket']:<8}"
              f"{paket.iloc[i]['nama_paket']:<25}"
              f"{format_rupiah(paket.iloc[i]['harga']):<15}")
    garis()



def buat_tagihan(id_pel):
    pelanggan = baca(FILE_PELANGGAN)
    p = cari_index(pelanggan, "id_pelanggan", id_pel)
    if p == -1:
        return

    id_paket = pelanggan.iloc[p]["id_paket"]
    if id_paket == "-":
        return
    if hitung_sisa_hari(pelanggan.iloc[p]["tanggal_berakhir"]) > HARI_TAGIHAN:
        return

    bayar = baca(FILE_PEMBAYARAN)
    for i in range(len(bayar)):
        if bayar.iloc[i]["id_pelanggan"] == id_pel and bayar.iloc[i]["status"] == "Belum Lunas":
            return

    paket = baca(FILE_PAKET)
    k = cari_index(paket, "id_paket", id_paket)
    if k == -1:
        return

    tanggal, bulan, tahun = waktu_sekarang()
    tagihan = {
        "id_tagihan": buat_id("TGH", bayar, "id_tagihan"),
        "id_pelanggan": id_pel,
        "bulan": bulan,
        "tahun": tahun,
        "id_paket": id_paket,
        "nominal": paket.iloc[k]["harga"],
        "status": "Belum Lunas",
        "tanggal_bayar": "-",
    }
    bayar = tambah_baris(bayar, tagihan)
    simpan(bayar, FILE_PEMBAYARAN)


# hapus akun pelanggan + tagihan yang belum lunas (riwayat lunas tetap disimpan)
def hapus_data_pelanggan(id_pel):
    pelanggan = baca(FILE_PELANGGAN)
    bayar = baca(FILE_PEMBAYARAN)
    pelanggan = pelanggan[pelanggan["id_pelanggan"] != id_pel]
    bayar = bayar[~((bayar["id_pelanggan"] == id_pel) &
                    (bayar["status"] == "Belum Lunas"))]
    simpan(pelanggan, FILE_PELANGGAN)
    simpan(bayar, FILE_PEMBAYARAN)


# hentikan langganan
def hentikan_langganan(id_pel):
    pelanggan = baca(FILE_PELANGGAN)
    p = cari_index(pelanggan, "id_pelanggan", id_pel)
    pelanggan.at[p, "id_paket"] = "-"
    pelanggan.at[p, "tanggal_berakhir"] = "-"
    simpan(pelanggan, FILE_PELANGGAN)

    bayar = baca(FILE_PEMBAYARAN)
    bayar = bayar[~((bayar["id_pelanggan"] == id_pel) &
                    (bayar["status"] == "Belum Lunas"))]
    simpan(bayar, FILE_PEMBAYARAN)

# FITUR PELANGGAN

# registrasi
def registrasi():
    judul("REGISTRASI AKUN PELANGGAN")
    pelanggan = baca(FILE_PELANGGAN)

    while True:
        username = input_wajib("Username: ").lower()
        if username in pelanggan["username"].values:
            print("Username sudah dipakai!")
        else:
            break

    while True:
        password = input("Password (min 6 karakter): ")
        if len(password) >= 6:
            break
        print("Password minimal 6 karakter!")

    nama = input_wajib("Nama lengkap: ").title()
    alamat = input_wajib("Alamat: ").title()

    while True:
        no_hp = input("No HP: ")
        if no_hp.isdigit() and len(no_hp) >= 10:
            break
        print("No HP harus angka dan minimal 10 digit!")

    id_pel = buat_id_pelanggan(pelanggan)
    tanggal, bulan, tahun = waktu_sekarang()

    data_baru = {
        "id_pelanggan": id_pel,
        "username": username,
        "password": password,
        "nama": nama,
        "alamat": alamat,
        "no_hp": no_hp,
        "id_paket": "-",
        "tanggal_daftar": tanggal,
        "tanggal_berakhir": "-",
    }
    pelanggan = tambah_baris(pelanggan, data_baru)
    simpan(pelanggan, FILE_PELANGGAN)

    print("\nRegistrasi berhasil! ID Anda:", id_pel)
    print("Silakan login, lalu pilih paket di menu Layanan.")


# login pelanggan
def login_pelanggan():
    judul("LOGIN PELANGGAN")
    username = input("Username: ").strip().lower()
    password = input("Password: ").strip()
    pelanggan = baca(FILE_PELANGGAN)

    for i in range(len(pelanggan)):
        if (pelanggan.iloc[i]["username"] == username and
                pelanggan.iloc[i]["password"] == password):
            print("Login berhasil! Selamat datang,", pelanggan.iloc[i]["nama"])
            return pelanggan.iloc[i]["id_pelanggan"]

    print("Username atau password salah!")
    return ""


# lihat tagihan pelanggan
def lihat_tagihan(id_pel):
    buat_tagihan(id_pel)
    judul("TAGIHAN")
    pelanggan = baca(FILE_PELANGGAN)
    bayar = baca(FILE_PEMBAYARAN)
    p = cari_index(pelanggan, "id_pelanggan", id_pel)
    id_paket = pelanggan.iloc[p]["id_paket"]

    if id_paket == "-":
        print("Status langganan : Belum berlangganan")
        print("Silakan pilih paket di menu Layanan.")
        return

    berakhir = pelanggan.iloc[p]["tanggal_berakhir"]
    sisa = hitung_sisa_hari(berakhir)
    print("Paket       :", ambil_nama_paket(id_paket))
    if sisa > 0:
        print("Masa aktif  :", berakhir, f"({sisa} hari lagi)")
    else:
        print("Masa aktif  : Belum aktif / sudah habis, silakan bayar tagihan")
    garis()

    tagihan = bayar[(bayar["id_pelanggan"] == id_pel) & (bayar["status"] == "Belum Lunas")]

    if len(tagihan) == 0:
        print("Tidak ada tagihan. Terima kasih!")
        return

    print(f"{'ID':<8}{'Terbit':<12}{'Nominal':<16}{'Status':<12}")
    garis()
    for i in range(len(tagihan)):
        terbit = tagihan.iloc[i]["bulan"] + "/" + tagihan.iloc[i]["tahun"]
        print(f"{tagihan.iloc[i]['id_tagihan']:<8}{terbit:<12}"
              f"{format_rupiah(tagihan.iloc[i]['nominal']):<16}"
              f"{tagihan.iloc[i]['status']:<12}")
    garis()
    total = tagihan["nominal"].astype(int).sum()
    print("Total tagihan:", format_rupiah(total))


# fungsi riwayat pembayaran
def riwayat_pembayaran(id_pel):
    judul("RIWAYAT PEMBAYARAN")
    bayar = baca(FILE_PEMBAYARAN)
    riwayat = bayar[(bayar["id_pelanggan"] == id_pel) & (bayar["status"] == "Lunas")]

    if len(riwayat) == 0:
        print("Belum ada pembayaran.")
        return

    print(f"{'ID':<8}{'Terbit':<12}{'Nominal':<16}{'Tgl Bayar':<12}")
    garis()
    total = 0
    for i in range(len(riwayat)):
        terbit = riwayat.iloc[i]["bulan"] + "/" + riwayat.iloc[i]["tahun"]
        nominal = int(riwayat.iloc[i]["nominal"])
        total = total + nominal
        print(f"{riwayat.iloc[i]['id_tagihan']:<8}{terbit:<12}"
              f"{format_rupiah(nominal):<16}{riwayat.iloc[i]['tanggal_bayar']:<12}")
    garis()
    print("Total dibayar:", format_rupiah(total))

# submenu
def menu_tagihan(id_pel):
    kembali = False
    while not kembali:
        lihat_tagihan(id_pel)
        print("\n[1] Bayar Tagihan")
        print("[2] Riwayat Pembayaran")
        print("[3] Kembali")
        pilihan = input("Pilih menu: ").strip()

        if pilihan == "1":
            bayar_tagihan(id_pel)
        elif pilihan == "2":
            riwayat_pembayaran(id_pel)
        elif pilihan == "3":
            kembali = True
        else:
            print("Pilihan tidak valid!")


# pilih paket
def pilih_paket(id_pel):
    judul("PILIH PAKET")
    pelanggan = baca(FILE_PELANGGAN)
    paket = baca(FILE_PAKET)
    p = cari_index(pelanggan, "id_pelanggan", id_pel)

    if pelanggan.iloc[p]["id_paket"] != "-":
        print("Anda sudah berlangganan:", ambil_nama_paket(pelanggan.iloc[p]["id_paket"]))
        print("Untuk mengganti paket, gunakan menu Upgrade Paket.")
        return

    if len(paket) == 0:
        print("Belum ada paket tersedia. Hubungi admin.")
        return

    tampil_paket(paket)
    nomor = pilih_nomor("Pilih nomor paket: ", len(paket))
    if nomor == -1:
        return

    tanggal, bulan, tahun = waktu_sekarang()
    pelanggan.at[p, "id_paket"] = paket.iloc[nomor]["id_paket"]
    pelanggan.at[p, "tanggal_berakhir"] = tanggal      # tanggal daftar paket = patokan jatuh tempo
    simpan(pelanggan, FILE_PELANGGAN)
    buat_tagihan(id_pel)

    print("Anda memilih", paket.iloc[nomor]["nama_paket"])
    print("Tagihan sudah dibuat. Bayar di menu Lihat Tagihan agar layanan aktif",
          MASA_AKTIF, "hari.")

#ganti password pelanggan
def ganti_password(id_pel):
    judul("GANTI PASSWORD")
    pelanggan = baca(FILE_PELANGGAN)
    i = cari_index(pelanggan, "id_pelanggan", id_pel)

    lama = input("Password lama: ").strip()
    if lama != pelanggan.iloc[i]["password"]:
        print("Password lama salah!")
        return

    baru = input("Password baru (min 6 karakter): ").strip()
    if len(baru) < 6 or baru == lama:
        print("Password baru minimal 6 karakter dan tidak boleh sama dengan yang lama!")
        return

    pelanggan.at[i, "password"] = baru                     
    simpan(pelanggan, FILE_PELANGGAN)
    print("Password berhasil diubah!")

#upgrade paket
def ganti_paket(id_pel):
    judul("UPGRADE / GANTI PAKET")
    pelanggan = baca(FILE_PELANGGAN)
    paket = baca(FILE_PAKET)
    p = cari_index(pelanggan, "id_pelanggan", id_pel)

    tampil_paket(paket)
    k_lama = cari_index(paket, "id_paket", pelanggan.iloc[p]["id_paket"])
    if k_lama != -1:
        print("Paket Anda sekarang:", paket.iloc[k_lama]["nama_paket"])
    else:
        print("Paket Anda sekarang:", pelanggan.iloc[p]["id_paket"])
    nomor = pilih_nomor("Pilih nomor paket baru: ", len(paket))
    if nomor == -1:
        return

    id_baru = paket.iloc[nomor]["id_paket"]
    harga_baru = paket.iloc[nomor]["harga"]
    if id_baru == pelanggan.iloc[p]["id_paket"]:
        print("Anda sudah memakai paket ini.")
        return

    pelanggan.at[p, "id_paket"] = id_baru
    simpan(pelanggan, FILE_PELANGGAN)

    # Hitung yang sudah dibayar bulan ini, lalu cari tagihan belum lunas
    tanggal, bulan, tahun = waktu_sekarang()
    bayar = baca(FILE_PEMBAYARAN)

    total_lunas = 0
    index_belum = -1
    for i in range(len(bayar)):
        if (bayar.iloc[i]["id_pelanggan"] == id_pel and
                bayar.iloc[i]["bulan"] == bulan and
                bayar.iloc[i]["tahun"] == tahun):
            if bayar.iloc[i]["status"] == "Lunas":
                total_lunas = total_lunas + int(bayar.iloc[i]["nominal"])
            else:
                index_belum = i

    selisih = int(harga_baru) - total_lunas      # harga paket baru - yang sudah dibayar

    if selisih > 0:
        if index_belum != -1:
            bayar.at[index_belum, "id_paket"] = id_baru
            bayar.at[index_belum, "nominal"] = str(selisih)
        else:
            tagihan_selisih = {
                "id_tagihan": buat_id("TGH", bayar, "id_tagihan"),
                "id_pelanggan": id_pel,
                "bulan": bulan,
                "tahun": tahun,
                "id_paket": id_baru,
                "nominal": str(selisih),
                "status": "Belum Lunas",
                "tanggal_bayar": "-",
            }
            bayar = tambah_baris(bayar, tagihan_selisih)
        print("Tagihan bulan ini disesuaikan. Selisih yang harus dibayar:",
              format_rupiah(selisih))
    elif index_belum != -1:
        bayar = bayar.drop(index_belum).reset_index(drop=True)
        print("Tagihan belum lunas bulan ini dibatalkan (pembayaran sebelumnya sudah cukup).")
    simpan(bayar, FILE_PEMBAYARAN)

    print("Paket berhasil diganti ke", paket.iloc[nomor]["nama_paket"])


# fungsi bayar tagihan
def bayar_tagihan(id_pel):
    judul("BAYAR TAGIHAN")
    bayar = baca(FILE_PEMBAYARAN)

    daftar = []
    for i in range(len(bayar)):
        if bayar.iloc[i]["id_pelanggan"] == id_pel and bayar.iloc[i]["status"] == "Belum Lunas":
            daftar.append(i)

    if len(daftar) == 0:
        print("Tidak ada tagihan yang harus dibayar.")
        return

    for no in range(len(daftar)):
        i = daftar[no]
        print(f"[{no + 1}] {bayar.iloc[i]['id_tagihan']} | "
              f"{bayar.iloc[i]['bulan']}/{bayar.iloc[i]['tahun']} | "
              f"{format_rupiah(bayar.iloc[i]['nominal'])}")

    nomor = pilih_nomor("Pilih tagihan yang dibayar: ", len(daftar))
    if nomor == -1:
        return

    i = daftar[nomor]
    konfirmasi = input("Yakin bayar? (y/n): ").strip().lower()
    if konfirmasi != "y":
        print("Pembayaran dibatalkan.")
        return

    tanggal, bulan, tahun = waktu_sekarang()
    bayar.at[i, "status"] = "Lunas"
    bayar.at[i, "tanggal_bayar"] = tanggal
    simpan(bayar, FILE_PEMBAYARAN)

    # perpanjang masa aktif 30 hari
    pelanggan = baca(FILE_PELANGGAN)
    p = cari_index(pelanggan, "id_pelanggan", id_pel)
    berakhir_lama = ke_tanggal(pelanggan.iloc[p]["tanggal_berakhir"])
    berakhir_baru = berakhir_lama + timedelta(days=MASA_AKTIF)
    pelanggan.at[p, "tanggal_berakhir"] = berakhir_baru.strftime("%Y-%m-%d")
    simpan(pelanggan, FILE_PELANGGAN)

    print("Pembayaran berhasil! Status: Lunas,", tanggal)
    print("Jatuh tempo berikutnya:", berakhir_baru.strftime("%Y-%m-%d"))
    if berakhir_baru <= hari_ini():
        print("Masih ada tagihan periode berikutnya, cek menu Lihat Tagihan.")

# upgrade / ganti paket
def ganti_paket(id_pel):
    judul("UPGRADE / GANTI PAKET")
    pelanggan = baca(FILE_PELANGGAN)
    paket = baca(FILE_PAKET)
    p = cari_index(pelanggan, "id_pelanggan", id_pel)

    id_lama = pelanggan.iloc[p]["id_paket"]
    if id_lama == "-":
        print("Anda belum berlangganan. Silakan pilih paket di menu Pilih Paket.")
        return

    berakhir = pelanggan.iloc[p]["tanggal_berakhir"]
    sisa = hitung_sisa_hari(berakhir)
    if sisa > 0:
        print("Paket belum bisa diganti!")
        print("Masa aktif paket Anda sampai", berakhir, f"({sisa} hari lagi).")
        print("Paket baru bisa diganti setelah masa aktif habis dan sebelum")
        print("membayar perpanjangan.")
        return

    tampil_paket(paket)
    print("Paket Anda sekarang:", ambil_nama_paket(id_lama))
    nomor = pilih_nomor("Pilih nomor paket baru: ", len(paket))
    if nomor == -1:
        return

    id_baru = paket.iloc[nomor]["id_paket"]
    harga_baru = paket.iloc[nomor]["harga"]
    if id_baru == id_lama:
        print("Anda sudah memakai paket ini.")
        return

    pelanggan.at[p, "id_paket"] = id_baru
    simpan(pelanggan, FILE_PELANGGAN)

    # tagihan yang belum lunas ikut pindah ke paket baru
    bayar = baca(FILE_PEMBAYARAN)
    for i in range(len(bayar)):
        if bayar.iloc[i]["id_pelanggan"] == id_pel and bayar.iloc[i]["status"] == "Belum Lunas":
            bayar.at[i, "id_paket"] = id_baru
            bayar.at[i, "nominal"] = harga_baru
    simpan(bayar, FILE_PEMBAYARAN)
    buat_tagihan(id_pel)        

    print("Paket berhasil diganti ke", paket.iloc[nomor]["nama_paket"])
    print("Tagihan perpanjangan sudah disesuaikan. Bayar di menu Lihat Tagihan.")


# berhenti langganan
def berhenti_langganan(id_pel):
    judul("BERHENTI LANGGANAN")
    pelanggan = baca(FILE_PELANGGAN)
    p = cari_index(pelanggan, "id_pelanggan", id_pel)

    if pelanggan.iloc[p]["id_paket"] == "-":
        print("Anda belum berlangganan paket apa pun.")
        return

    sisa = hitung_sisa_hari(pelanggan.iloc[p]["tanggal_berakhir"])
    print("Paket Anda:", ambil_nama_paket(pelanggan.iloc[p]["id_paket"]))
    if sisa > 0:
        print("Sisa masa aktif", sisa, "hari akan hangus (tidak ada pengembalian dana).")
    print("Paket Anda akan dihentikan.")
    print("Akun Anda tetap ada, bisa berlangganan lagi kapan saja.")
    konfirmasi = input("Yakin berhenti berlangganan? (y/n): ").strip().lower()
    if konfirmasi != "y":
        print("Dibatalkan.")
        return

    hentikan_langganan(id_pel)
    print("Langganan berhasil dihentikan. Terima kasih!")


# submenu
def menu_layanan(id_pel):
    kembali = False
    while not kembali:
        judul("LAYANAN")
        print("[1] Pilih Paket")
        print("[2] Upgrade Paket")
        print("[3] Berhenti Langganan")
        print("[4] Kembali")
        pilihan = input("Pilih menu: ").strip()

        if pilihan == "1":
            pilih_paket(id_pel)
        elif pilihan == "2":
            ganti_paket(id_pel)
        elif pilihan == "3":
            berhenti_langganan(id_pel)
        elif pilihan == "4":
            kembali = True
        else:
            print("Pilihan tidak valid!")


# ganti password pelanggan
def ganti_password(id_pel):
    judul("GANTI PASSWORD")
    pelanggan = baca(FILE_PELANGGAN)
    i = cari_index(pelanggan, "id_pelanggan", id_pel)

    lama = input("Password lama: ").strip()
    if lama != pelanggan.iloc[i]["password"]:
        print("Password lama salah!")
        return

    baru = input("Password baru (min 6 karakter): ").strip()
    if len(baru) < 6 or baru == lama:
        print("Password baru minimal 6 karakter dan tidak boleh sama dengan yang lama!")
        return

    pelanggan.at[i, "password"] = baru
    simpan(pelanggan, FILE_PELANGGAN)
    print("Password berhasil diubah!")

# hapus akun pelanggan (harus berhenti langganan dulu)
def hapus_akun(id_pel):
    judul("HAPUS AKUN")
    pelanggan = baca(FILE_PELANGGAN)
    p = cari_index(pelanggan, "id_pelanggan", id_pel)

    if pelanggan.iloc[p]["id_paket"] != "-":
        print("Akun belum bisa dihapus karena Anda masih berlangganan.")
        print("Berhenti langganan dulu di menu Layanan.")
        return False

    print("Akun Anda akan dihapus permanen dan tidak bisa dikembalikan.")
    print("(Riwayat pembayaran yang sudah lunas tetap diarsipkan.)")
    password = input("Masukkan password untuk konfirmasi: ").strip()
    if password != pelanggan.iloc[p]["password"]:
        print("Password salah! Penghapusan dibatalkan.")
        return False

    konfirmasi = input("Yakin hapus akun? (y/n): ").strip().lower()
    if konfirmasi != "y":
        print("Dibatalkan.")
        return False

    hapus_data_pelanggan(id_pel)
    print("Akun berhasil dihapus. Terima kasih!")
    return True

# navigasi pelanggan
def menu_pelanggan(id_pel):
    aktif = True
    while aktif:
        judul("MENU PELANGGAN")
        print("[1] Lihat Tagihan")
        print("[2] Layanan")
        print("[3] Ganti Password")
        print("[4] Hapus Akun")
        print("[5] Logout")
        pilihan = input("Pilih menu: ").strip()

        if pilihan == "1":
            menu_tagihan(id_pel)
        elif pilihan == "2":
            menu_layanan(id_pel)
        elif pilihan == "3":
            ganti_password(id_pel)
        elif pilihan == "4":
            if hapus_akun(id_pel):
                aktif = False
        elif pilihan == "5":
            print("Anda sudah logout.")
            aktif = False
        else:
            print("Pilihan tidak valid!")

# FITUR ADMIN

# login admin
def login_admin():
    judul("LOGIN ADMIN")
    username = input("Username: ").strip().lower()
    password = input("Password: ").strip()
    admin = baca(FILE_ADMIN)

    for i in range(len(admin)):
        if admin.iloc[i]["username"] == username and admin.iloc[i]["password"] == password:
            print("Login admin berhasil!")
            return username

    print("Username atau password admin salah!")
    return ""


# fungsi ganti password
def ganti_password_admin(username):
    judul("GANTI PASSWORD ADMIN")
    admin = baca(FILE_ADMIN)
    i = cari_index(admin, "username", username)

    lama = input("Password lama: ").strip()
    if lama != admin.iloc[i]["password"]:
        print("Password lama salah!")
        return

    baru = input("Password baru (min 6 karakter): ").strip()
    if len(baru) < 6 or baru == lama:
        print("Password baru minimal 6 karakter dan tidak boleh sama dengan yang lama!")
        return

    admin.at[i, "password"] = baru
    simpan(admin, FILE_ADMIN)
    print("Password admin berhasil diubah!")


# tambah paket
def tambah_paket():
    judul("TAMBAH PAKET")
    paket = baca(FILE_PAKET)
    nama = input_wajib("Nama paket: ").title()

    while True:
        harga = input("Harga per bulan (angka): ").strip()
        if harga.isdigit() and int(harga) > 0:
            break
        print("Harga harus angka lebih dari 0!")

    id_baru = buat_id("PKT", paket, "id_paket")
    paket = tambah_baris(paket, {"id_paket": id_baru, "nama_paket": nama,
                                 "harga": str(int(harga))})
    simpan(paket, FILE_PAKET)
    print("Paket berhasil ditambahkan dengan ID:", id_baru)


# ubah paket
def ubah_paket():
    judul("UBAH PAKET")
    paket = baca(FILE_PAKET)
    tampil_paket(paket)
    nomor = pilih_nomor("Pilih nomor paket: ", len(paket))
    if nomor == -1:
        return

    print("Kosongkan (Enter) jika tidak ingin mengubah.")
    nama = input("Nama baru: ").strip()
    harga = input("Harga baru: ").strip()

    if nama != "":
        paket.at[nomor, "nama_paket"] = nama.title()
    if harga != "":
        if harga.isdigit() and int(harga) > 0:
            paket.at[nomor, "harga"] = str(int(harga))
        else:
            print("Harga tidak valid, harga tidak diubah.")

    simpan(paket, FILE_PAKET)
    print("Paket berhasil diperbarui!")


# hapus paket
def hapus_paket():
    judul("HAPUS PAKET")
    paket = baca(FILE_PAKET)
    pelanggan = baca(FILE_PELANGGAN)
    tampil_paket(paket)
    nomor = pilih_nomor("Pilih nomor paket: ", len(paket))
    if nomor == -1:
        return

    id_paket = paket.iloc[nomor]["id_paket"]
    if id_paket in pelanggan["id_paket"].values:
        print("Paket tidak bisa dihapus karena masih dipakai pelanggan!")
        return

    konfirmasi = input("Yakin hapus paket ini? (y/n): ").strip().lower()
    if konfirmasi != "y":
        print("Dibatalkan.")
        return

    paket = paket.drop(nomor)
    simpan(paket, FILE_PAKET)
    print("Paket berhasil dihapus!")


# fitur kelola paket
def menu_paket():
    selesai = False
    while not selesai:
        judul("KELOLA PAKET")
        print("[1] Lihat Paket")
        print("[2] Tambah Paket")
        print("[3] Ubah Paket")
        print("[4] Hapus Paket")
        print("[5] Kembali")
        pilihan = input("Pilih menu: ").strip()

        if pilihan == "1":
            tampil_paket(baca(FILE_PAKET))
        elif pilihan == "2":
            tambah_paket()
        elif pilihan == "3":
            ubah_paket()
        elif pilihan == "4":
            hapus_paket()
        elif pilihan == "5":
            selesai = True
        else:
            print("Pilihan tidak valid!")

# fungsi lihat daftar pelanggan
def lihat_semua_pelanggan():
    judul("DAFTAR SEMUA PELANGGAN")
    pelanggan = baca(FILE_PELANGGAN)
    paket = baca(FILE_PAKET)

    if len(pelanggan) == 0:
        print("Belum ada pelanggan.")
        return

    gabung = pd.merge(pelanggan, paket, on="id_paket", how="left")
    gabung["nama_paket"] = gabung["nama_paket"].fillna("-")     # belum berlangganan

    print(f"{'ID':<8}{'Username':<11}{'Password':<11}{'Nama':<18}{'No HP':<13}{'Paket':<18}{'Aktif s/d':<12}")
    garis(91)
    for i in range(len(gabung)):
        print(f"{gabung.iloc[i]['id_pelanggan']:<8}{gabung.iloc[i]['username']:<11}"
              f"{gabung.iloc[i]['password']:<11}{gabung.iloc[i]['nama']:<18}"
              f"{gabung.iloc[i]['no_hp']:<13}{gabung.iloc[i]['nama_paket']:<18}"
              f"{gabung.iloc[i]['tanggal_berakhir']:<12}")
    garis(91)
    print("Total pelanggan:", len(gabung))


# status pembayaran pelanggan
def status_pembayaran():
    judul("STATUS PEMBAYARAN PELANGGAN")
    pelanggan = baca(FILE_PELANGGAN)
    if len(pelanggan) == 0:
        print("Belum ada pelanggan.")
        return

    for i in range(len(pelanggan)):
        buat_tagihan(pelanggan.iloc[i]["id_pelanggan"])      # pastikan tagihan terbaru sudah ada
    bayar = baca(FILE_PEMBAYARAN)

    jumlah_lunas = 0
    jumlah_belum = 0
    jumlah_tidak = 0
    jumlah_telat = 0
    tunggakan = 0

    print(f"{'ID':<8}{'Nama':<20}{'Status':<20}{'Tunggakan':<14}{'Aktif s/d':<12}{'Keterangan':<16}")
    garis(90)

    for i in range(len(pelanggan)):                          
        belum_pel = 0
        for j in range(len(bayar)):                          
            if (bayar.iloc[j]["id_pelanggan"] == pelanggan.iloc[i]["id_pelanggan"] and
                    bayar.iloc[j]["status"] == "Belum Lunas"):
                belum_pel = belum_pel + int(bayar.iloc[j]["nominal"])

        keterangan = "-"
        if pelanggan.iloc[i]["id_paket"] == "-":
            status = "Tidak Berlangganan"
            jumlah_tidak = jumlah_tidak + 1
        elif belum_pel > 0:
            status = "Belum Lunas"
            jumlah_belum = jumlah_belum + 1

            telat = -hitung_sisa_hari(pelanggan.iloc[i]["tanggal_berakhir"])
            if telat >= BATAS_TELAT:
                keterangan = "Telat " + str(telat) + " hari!"
                jumlah_telat = jumlah_telat + 1
        else:
            status = "Lunas"
            jumlah_lunas = jumlah_lunas + 1

        tunggakan = tunggakan + belum_pel

        print(f"{pelanggan.iloc[i]['id_pelanggan']:<8}{pelanggan.iloc[i]['nama']:<20}"
              f"{status:<20}{format_rupiah(belum_pel):<14}"
              f"{pelanggan.iloc[i]['tanggal_berakhir']:<12}{keterangan:<16}")

    # pendapatan bulan ini
    bulan_ini = waktu_sekarang()[0][:7]
    pendapatan = 0
    for j in range(len(bayar)):
        if bayar.iloc[j]["status"] == "Lunas" and bayar.iloc[j]["tanggal_bayar"][:7] == bulan_ini:
            pendapatan = pendapatan + int(bayar.iloc[j]["nominal"])

    garis(90)
    print(f"Lunas              : {jumlah_lunas} orang")
    print(f"Belum Lunas        : {jumlah_belum} orang")
    print(f"Tidak Berlangganan : {jumlah_tidak} orang")
    print(f"Pendapatan masuk bulan ini : {format_rupiah(pendapatan)}")
    print(f"Total tunggakan            : {format_rupiah(tunggakan)}")

    if jumlah_telat > 0:
        print(f"\nPERLU TINDAK LANJUT: {jumlah_telat} pelanggan sudah lewat batas telat {BATAS_TELAT} hari.")
        print("Pilih: dimatikan (Cari Pelanggan > Berhentikan) atau diteruskan jika ada janji bayar.")

def rekap_pendapatan():
    judul("REKAP PENDAPATAN")
    bayar = baca(FILE_PEMBAYARAN)
    lunas = bayar[bayar["status"] == "Lunas"]

    if len(lunas) == 0:
        print("Belum ada pembayaran yang tercatat.")
        return

    nama_bulan = ["Januari", "Februari", "Maret", "April", "Mei", "Juni",
                  "Juli", "Agustus", "September", "Oktober", "November", "Desember"]

    daftar_tahun = []
    for i in range(len(lunas)):
        tahun = lunas.iloc[i]["tanggal_bayar"][:4]
        if tahun not in daftar_tahun:
            daftar_tahun.append(tahun)
    daftar_tahun.sort()

    print("Tahun yang tersedia:", ", ".join(daftar_tahun))
    pilih_tahun = input("Masukkan tahun (kosongkan untuk semua tahun): ").strip()
    if pilih_tahun != "" and pilih_tahun not in daftar_tahun:
        print("Tahun tidak ada dalam data!")
        return

    rekap = {}
    for i in range(len(lunas)):
        tgl = lunas.iloc[i]["tanggal_bayar"]
        if pilih_tahun != "" and tgl[:4] != pilih_tahun:
            continue
        periode = tgl[:7]
        nominal = int(lunas.iloc[i]["nominal"])
        if periode not in rekap:
            rekap[periode] = [0, 0]
        rekap[periode][0] = rekap[periode][0] + 1
        rekap[periode][1] = rekap[periode][1] + nominal

    print(f"\n{'Periode':<22}{'Transaksi':<12}{'Pendapatan':<16}")
    garis()
    total_transaksi = 0
    total_uang = 0
    for periode in sorted(rekap.keys()):
        tahun = periode[:4]
        bulan = nama_bulan[int(periode[5:7]) - 1]
        jumlah = rekap[periode][0]
        uang = rekap[periode][1]
        total_transaksi = total_transaksi + jumlah
        total_uang = total_uang + uang
        print(f"{bulan + ' ' + tahun:<22}{jumlah:<12}{format_rupiah(uang):<16}")
    garis()

    if pilih_tahun == "":
        print("Total semua tahun")
    else:
        print("Total tahun", pilih_tahun)
    print("Jumlah transaksi :", total_transaksi)
    print("Total pendapatan :", format_rupiah(total_uang)) 

    # tampilkan detail satu pelanggan
def tampil_detail_pelanggan(id_pel):
    buat_tagihan(id_pel)
    pelanggan = baca(FILE_PELANGGAN)
    bayar = baca(FILE_PEMBAYARAN)
    i = cari_index(pelanggan, "id_pelanggan", id_pel)

    print("\n" + "#" * 70)
    print("ID            :", id_pel)
    print("Username      :", pelanggan.iloc[i]["username"])
    print("Password      :", pelanggan.iloc[i]["password"])
    print("Nama          :", pelanggan.iloc[i]["nama"])
    print("Alamat        :", pelanggan.iloc[i]["alamat"])
    print("No HP         :", pelanggan.iloc[i]["no_hp"])
    print("Paket         :", ambil_nama_paket(pelanggan.iloc[i]["id_paket"]))
    print("Aktif sampai  :", pelanggan.iloc[i]["tanggal_berakhir"])
    print("Tgl Daftar    :", pelanggan.iloc[i]["tanggal_daftar"])

    print("\nStatus & riwayat pembayaran:")
    ada_tagihan = False
    ada_belum = False
    for j in range(len(bayar)):
        if bayar.iloc[j]["id_pelanggan"] == id_pel:
            ada_tagihan = True
            if bayar.iloc[j]["status"] == "Belum Lunas":
                ada_belum = True
            print(f"  {bayar.iloc[j]['id_tagihan']} | "
                  f"{bayar.iloc[j]['bulan']}/{bayar.iloc[j]['tahun']} | "
                  f"{format_rupiah(bayar.iloc[j]['nominal'])} | "
                  f"{bayar.iloc[j]['status']} | {bayar.iloc[j]['tanggal_bayar']}")
    if not ada_tagihan:
        print("  Belum ada tagihan.")

    # keterangan telat
    if pelanggan.iloc[i]["id_paket"] != "-" and ada_belum:
        telat = -hitung_sisa_hari(pelanggan.iloc[i]["tanggal_berakhir"])
        if telat >= BATAS_TELAT:
            print("\n>> Telat bayar", telat, "hari! Tentukan: dimatikan atau diteruskan.")


# admin menghentikan paket pelanggan
def berhentikan_pelanggan(id_pel):
    pelanggan = baca(FILE_PELANGGAN)
    p = cari_index(pelanggan, "id_pelanggan", id_pel)

    if pelanggan.iloc[p]["id_paket"] == "-":
        print("Pelanggan ini sedang tidak berlangganan.")
        return

    print("Paket pelanggan:", ambil_nama_paket(pelanggan.iloc[p]["id_paket"]))
    print("Paket pelanggan akan dihentikan. Akun pelanggan tetap ada.")
    konfirmasi = input("Yakin berhentikan pelanggan ini? (y/n): ").strip().lower()
    if konfirmasi != "y":
        print("Dibatalkan.")
        return

    hentikan_langganan(id_pel)
    print("Paket pelanggan berhasil dihentikan!")


#hapus akun pelanggan.
def hapus_pelanggan_admin(id_pel):
    print("Akun pelanggan akan dihapus permanen.")
    print("(Riwayat pembayaran yang sudah lunas tetap diarsipkan untuk rekap pendapatan.)")
    konfirmasi = input("Yakin hapus pelanggan ini? (y/n): ").strip().lower()
    if konfirmasi != "y":
        print("Dibatalkan.")
        return False

    hapus_data_pelanggan(id_pel)
    print("Pelanggan berhasil dihapus!")
    return True


# cari pelanggan
def cari_pelanggan():
    judul("CARI PELANGGAN")
    kata = input("Cari nama / username: ").strip().lower()
    pelanggan = baca(FILE_PELANGGAN)

    hasil = []                                   # index pelanggan yang cocok
    for i in range(len(pelanggan)):
        nama = pelanggan.iloc[i]["nama"]
        user = pelanggan.iloc[i]["username"]
        if kata in nama.lower() or kata in user.lower():
            hasil.append(i)

    if len(hasil) == 0:
        print("Pelanggan tidak ditemukan.")
        return

    nomor = 0
    if len(hasil) > 1:                           
        print("Ditemukan", len(hasil), "pelanggan:")
        for no in range(len(hasil)):
            i = hasil[no]
            print(f"[{no + 1}] {pelanggan.iloc[i]['id_pelanggan']} | "
                  f"{pelanggan.iloc[i]['nama']} | {pelanggan.iloc[i]['username']}")
        nomor = pilih_nomor("Pilih nomor pelanggan: ", len(hasil))
        if nomor == -1:
            return

    id_pel = pelanggan.iloc[hasil[nomor]]["id_pelanggan"]

    selesai = False
    while not selesai:
        tampil_detail_pelanggan(id_pel)
        print("\n[1] Berhentikan Pelanggan")
        print("[2] Hapus Pelanggan")
        print("[3] Keluar")
        pilihan = input("Pilih menu: ").strip()

        if pilihan == "1":
            berhentikan_pelanggan(id_pel)
        elif pilihan == "2":
            if hapus_pelanggan_admin(id_pel):
                selesai = True                   
        elif pilihan == "3":
            selesai = True
        else:
            print("Pilihan tidak valid!")


# menu admin
def menu_admin(username):
    aktif = True
    while aktif:
        judul("MENU ADMIN")
        print("[1] Kelola Paket")
        print("[2] Daftar Semua Pelanggan")
        print("[3] Status Pembayaran Pelanggan (Lunas / Belum Lunas)")
        print("[4] Cari Pelanggan (Berhentikan / Hapus)")
        print("[5] Rekap Pendapatan")
        print("[6] Ganti Password Admin")
        print("[7] Logout")
        pilihan = input("Pilih menu: ").strip()

        if pilihan == "1":
            menu_paket()
        elif pilihan == "2":
            lihat_semua_pelanggan()
        elif pilihan == "3":
            status_pembayaran()
        elif pilihan == "4":
            cari_pelanggan()
        elif pilihan == "5":
            rekap_pendapatan()
        elif pilihan == "6":
            ganti_password_admin(username)
        elif pilihan == "7":
            print("Admin logout.")
            aktif = False
        else:
            print("Pilihan tidak valid!")


# NAVIGASI UTAMA

# submenu login: admin / pelanggan
def menu_login():
    kembali = False
    while not kembali:
        judul("LOGIN")
        print("[1] Admin")
        print("[2] Pelanggan")
        print("[3] Kembali")
        pilihan = input("Pilih menu: ").strip()

        if pilihan == "1":
            username = login_admin()
            if username != "":
                menu_admin(username)
                kembali = True
        elif pilihan == "2":
            id_pel = login_pelanggan()
            if id_pel != "":
                menu_pelanggan(id_pel)
                kembali = True
        elif pilihan == "3":
            kembali = True
        else:
            print("Pilihan tidak valid!")


def main():
    buat_file_awal()
    berjalan = True

    while berjalan:
        judul("BILLING NET - RT/RW NET")
        print("[1] Registrasi Pelanggan")
        print("[2] Login")
        print("[3] Keluar")
        pilihan = input("Pilih menu: ").strip()

        if pilihan == "1":
            registrasi()
        elif pilihan == "2":
            menu_login()
        elif pilihan == "3":
            print("Terima kasih telah menggunakan Billing Net!")
            berjalan = False
        else:
            print("Pilihan tidak valid!")


main()