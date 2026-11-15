import os
import pandas as pd
from datetime import datetime

FOLDER = "data"
FILE_ADMIN = "data/admin.csv"
FILE_PAKET = "data/paket.csv"
FILE_PELANGGAN = "data/pelanggan.csv"
FILE_PEMBAYARAN = "data/pembayaran.csv"

HEADER_ADMIN = ("username", "password")
HEADER_PAKET = ("id_paket", "nama_paket", "harga")
HEADER_PELANGGAN = ("id_pelanggan", "username", "password", "nama",
                    "alamat", "no_hp", "id_paket", "tanggal_daftar")
HEADER_PEMBAYARAN = ("id_tagihan", "id_pelanggan", "bulan", "tahun",
                     "id_paket", "nominal", "status", "tanggal_b"
                     "ayar")
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

#fungsi baca csv jadi dataframe
def baca(namafile):
    try:
        return pd.read_csv(namafile, dtype=str)
    except FileNotFoundError:
        print("File tidak ditemukan, membuat ulang file...")
        buat_file_awal()
        return pd.read_csv(namafile, dtype=str)

#fungsi simpan df ke csv
def simpan(df, namafile):
    df.to_csv(namafile, index=False)



def garis():
    print("-" * 70)


def judul(teks):
    print("\n" + "=" * 70)
    print(teks.center(70))
    print("=" * 70)


def format_rupiah(angka):
    angka = int(angka)
    teks = f"{angka:,}".replace(",", ".")
    return "Rp" + teks

#fungsi pilihan fitur
def pilih_nomor(pertanyaan, jumlah):
    pilihan = input(pertanyaan).strip()
    if pilihan.isdigit() and 1 <= int(pilihan) <= jumlah:
        return int(pilihan) - 1
    print("Pilihan tidak valid!")
    return -1

#fungsi genberate id
def buat_id(awalan, df, kolom):
    nomor_max = 0
    for id_lama in df[kolom]:
        angka = id_lama[len(awalan):]                     
        if angka.isdigit() and int(angka) > nomor_max:
            nomor_max = int(angka)
    return awalan + str(nomor_max + 1).zfill(2)

#fungsi id pelanggan
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

#cari baris pertama yang isinya cocok
def cari_index(df, kolom, nilai):
    for i in range(len(df)):
        if df.iloc[i][kolom] == nilai:
            return i
    return -1

#tambah data
def tambah_baris(df, baris):
    baru = pd.DataFrame([baris])
    if len(df) == 0:
        return baru
    return pd.concat([df, baru], ignore_index=True)


def tampil_paket(paket):
    garis()
    print(f"{'No':<4}{'ID':<8}{'Nama Paket':<25}{'Harga/Bulan':<15}")
    garis()
    for i in range(len(paket)):
        print(f"{i + 1:<4}{paket.iloc[i]['id_paket']:<8}"
              f"{paket.iloc[i]['nama_paket']:<25}"
              f"{format_rupiah(paket.iloc[i]['harga']):<15}")
    garis()


def buat_tagihan_bulan_ini(id_pel):
    tanggal, bulan, tahun = waktu_sekarang()
    bayar = baca(FILE_PEMBAYARAN)

    for i in range(len(bayar)):
        if (bayar.iloc[i]["id_pelanggan"] == id_pel and
                bayar.iloc[i]["bulan"] == bulan and
                bayar.iloc[i]["tahun"] == tahun):
            return                                         

    pelanggan = baca(FILE_PELANGGAN)
    paket = baca(FILE_PAKET)
    p = cari_index(pelanggan, "id_pelanggan", id_pel)
    id_paket = pelanggan.iloc[p]["id_paket"]
    k = cari_index(paket, "id_paket", id_paket)
    harga = paket.iloc[k]["harga"]

    tagihan = {
        "id_tagihan": buat_id("TGH", bayar, "id_tagihan"),
        "id_pelanggan": id_pel,
        "bulan": bulan,
        "tahun": tahun,
        "id_paket": id_paket,
        "nominal": harga,
        "status": "Belum Lunas",
        "tanggal_bayar": "-",
    }
    bayar = tambah_baris(bayar, tagihan)
    simpan(bayar, FILE_PEMBAYARAN)

#hapus data pelanggan
def hapus_data_pelanggan(id_pel):
    pelanggan = baca(FILE_PELANGGAN)
    bayar = baca(FILE_PEMBAYARAN)
    pelanggan = pelanggan[pelanggan["id_pelanggan"] != id_pel]
    bayar = bayar[~((bayar["id_pelanggan"] == id_pel) &
                    (bayar["status"] == "Belum Lunas"))]
    simpan(pelanggan, FILE_PELANGGAN)
    simpan(bayar, FILE_PEMBAYARAN)

#FITUR PELANGGAN

#regristasi akun dan langganan
def registrasi():
    judul("REGISTRASI PELANGGAN BARU")
    pelanggan = baca(FILE_PELANGGAN)
    paket = baca(FILE_PAKET)

    if len(paket) == 0:
        print("Belum ada paket tersedia. Hubungi admin.")
        return

    while True:
        username = input("Username: ").lower()
        if username in pelanggan["username"].values:
            print("Username sudah dipakai!")
        else:
            break

    while True:
        password = input("Password (min 6 karakter): ")
        if len(password) >= 6:
            break
        print("Password minimal 6 karakter!")

    nama = input("Nama lengkap: ").title()
    alamat = input("Alamat: ").title()

    while True:
        no_hp = input("No HP: ")
        if no_hp.isdigit() and len(no_hp) >= 10:          
            break
        print("No HP harus angka dan minimal 10 digit!")

    print("\nPilihan paket:")
    tampil_paket(paket)
    nomor = -1
    while nomor == -1:
        nomor = pilih_nomor("Pilih nomor paket: ", len(paket))

    id_pel = buat_id_pelanggan(pelanggan)
    tanggal, bulan, tahun = waktu_sekarang()


    data_baru = {
        "id_pelanggan": id_pel,
        "username": username,
        "password": password,
        "nama": nama,
        "alamat": alamat,
        "no_hp": no_hp,
        "id_paket": paket.iloc[nomor]["id_paket"],
        "tanggal_daftar": tanggal,
    }
    pelanggan = tambah_baris(pelanggan, data_baru)
    simpan(pelanggan, FILE_PELANGGAN)
    buat_tagihan_bulan_ini(id_pel)

    print("\nRegistrasi berhasil! ID Anda:", id_pel)
    print("Tagihan bulan ini sudah dibuat.")


#login pelanggan
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

#fungsi riwayat pembayaran
def riwayat_pembayaran(id_pel):
    judul("RIWAYAT PEMBAYARAN")
    bayar = baca(FILE_PEMBAYARAN)
    riwayat = bayar[(bayar["id_pelanggan"] == id_pel) & (bayar["status"] == "Lunas")]

    if len(riwayat) == 0:
        print("Belum ada pembayaran.")
        return

    print(f"{'ID':<8}{'Periode':<12}{'Nominal':<16}{'Tgl Bayar':<12}")
    garis()
    total = 0
    for i in range(len(riwayat)):
        periode = riwayat.iloc[i]["bulan"] + "/" + riwayat.iloc[i]["tahun"]
        nominal = int(riwayat.iloc[i]["nominal"])
        total = total + nominal
        print(f"{riwayat.iloc[i]['id_tagihan']:<8}{periode:<12}"
              f"{format_rupiah(nominal):<16}{riwayat.iloc[i]['tanggal_bayar']:<12}")
    garis()
    print("Total dibayar:", format_rupiah(total))

#lihat tagihan pelanggan
def lihat_tagihan(id_pel):
    judul("TAGIHAN BELUM LUNAS")
    bayar = baca(FILE_PEMBAYARAN)

    tagihan = bayar[(bayar["id_pelanggan"] == id_pel) & (bayar["status"] == "Belum Lunas")]

    if len(tagihan) == 0:
        print("Tidak ada tagihan. Terima kasih!")
        return

    print(f"{'ID':<8}{'Periode':<12}{'Nominal':<16}{'Status':<12}")
    garis()
    for i in range(len(tagihan)):
        periode = tagihan.iloc[i]["bulan"] + "/" + tagihan.iloc[i]["tahun"]
        print(f"{tagihan.iloc[i]['id_tagihan']:<8}{periode:<12}"
              f"{format_rupiah(tagihan.iloc[i]['nominal']):<16}"
              f"{tagihan.iloc[i]['status']:<12}")
    garis()
    total = tagihan["nominal"].astype(int).sum()           
    print("Total tagihan:", format_rupiah(total))


#fungsi bayar tagihan
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
    print("Pembayaran berhasil! Status: Lunas,", tanggal)

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


#fungsi bayar tagihan
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
    print("Pembayaran berhasil! Status: Lunas,", tanggal)


#berhenti langganan
def berhenti_langganan(id_pel):
    judul("BERHENTI LANGGANAN")
    print("Akun dan tagihan yang belum lunas akan dihapus permanen!")
    print("(Riwayat pembayaran yang sudah lunas tetap diarsipkan.)")
    konfirmasi = input("Yakin berhenti? (y/n): ").strip().lower()
    if konfirmasi != "y":
        print("Dibatalkan.")
        return False

    hapus_data_pelanggan(id_pel)
    print("Akun berhasil dihapus. Terima kasih telah berlangganan!")
    return True


#navigasi pelanggan
def menu_pelanggan(id_pel):
    buat_tagihan_bulan_ini(id_pel)                         
    aktif = True
    while aktif:
        judul("MENU PELANGGAN")
        print("[1] Lihat Tagihan")
        print("[2] Bayar Tagihan")
        print("[3] Riwayat Pembayaran")
        print("[4] Upgrade / Ganti Paket")
        print("[5] Ganti Password")
        print("[6] Berhenti Langganan")
        print("[7] Logout")
        pilihan = input("Pilih menu: ").strip()

        if pilihan == "1":
            lihat_tagihan(id_pel)
        elif pilihan == "2":
            bayar_tagihan(id_pel)
        elif pilihan == "3":
            riwayat_pembayaran(id_pel)
        elif pilihan == "4":
            ganti_paket(id_pel)
        elif pilihan == "5":
            ganti_password(id_pel)
        elif pilihan == "6":
            if berhenti_langganan(id_pel):
                aktif = False
        elif pilihan == "7":
            print("Anda sudah logout.")
            aktif = False
        else:
            print("Pilihan tidak valid!")