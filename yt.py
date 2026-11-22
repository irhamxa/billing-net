import csv
import os

nama_file = "data_pelanggan_wifi.csv"

paket_wifi = {
    "1": ["Basic", 10, 100000],
    "2": ["Standard", 20, 150000],
    "3": ["Premium", 50, 250000],
    "4": ["Ultimate", 100, 350000]
}


# Membuat file CSV
def buat_file():
    if not os.path.exists(nama_file):
        with open(nama_file, "w", newline="") as file:
            kolom = ["ID", "Nama", "Username", "Password",
                     "Paket", "Kecepatan", "Biaya",
                     "Status Tagihan"]
            writer = csv.DictWriter(file, fieldnames=kolom)
            writer.writeheader()


# Membaca data pelanggan
def baca_data():
    with open(nama_file, "r") as file:
        return list(csv.DictReader(file))


# Menyimpan data pelanggan
def simpan_data(data):
    with open(nama_file, "w", newline="") as file:
        kolom = ["ID", "Nama", "Username", "Password",
                 "Paket", "Kecepatan", "Biaya",
                 "Status Tagihan"]
        writer = csv.DictWriter(file, fieldnames=kolom)
        writer.writeheader()
        writer.writerows(data)


# Menampilkan pilihan paket
def tampilkan_paket():
    print("\n===== PILIHAN PAKET WIFI =====")
    for nomor, paket in paket_wifi.items():
        print(nomor, paket[0], "-", paket[1],
              "Mbps - Rp", paket[2])


# CREATE: Registrasi akun
def registrasi():
    data = baca_data()

    print("\n===== REGISTRASI =====")
    nama = input("Nama lengkap: ")
    username = input("Username: ")
    password = input("Password: ")

    if not nama.strip() or not username.strip() or not password.strip():
        print("Semua data harus diisi!")
        return

    for p in data:
        if p["Username"].lower() == username.lower():
            print("Username sudah digunakan!")
            return

    tampilkan_paket()
    pilihan = input("Pilih paket (1-4): ")

    if pilihan not in paket_wifi:
        print("Pilihan paket tidak valid!")
        return

    paket = paket_wifi[pilihan]

    pelanggan = {
        "ID": "WIFI" + str(len(data) + 1).zfill(3),
        "Nama": nama,
        "Username": username,
        "Password": password,
        "Paket": paket[0],
        "Kecepatan": paket[1],
        "Biaya": paket[2],
        "Status Tagihan": "Belum Lunas"
    }

    data.append(pelanggan)
    simpan_data(data)

    print("Registrasi berhasil!")
    print("ID Pelanggan:", pelanggan["ID"])


# Login pelanggan
def login():
    data = baca_data()

    print("\n===== LOGIN PELANGGAN =====")
    username = input("Username: ")
    password = input("Password: ")

    for p in data:
        if p["Username"] == username and p["Password"] == password:
            print("Login berhasil!")
            menu_pelanggan(p["ID"])
            return

    print("Username atau password salah!")


# READ: Melihat tagihan
def cek_tagihan(id_pelanggan):
    data = baca_data()

    for p in data:
        if p["ID"] == id_pelanggan:
            print("\n===== INFORMASI TAGIHAN =====")
            print("Nama:", p["Nama"])
            print("ID:", p["ID"])
            print("Paket:", p["Paket"])
            print("Kecepatan:", p["Kecepatan"], "Mbps")
            print("Biaya: Rp", p["Biaya"])
            print("Status:", p["Status Tagihan"])
            return


# UPDATE: Upgrade paket
def upgrade_paket(id_pelanggan):
    data = baca_data()

    for p in data:
        if p["ID"] == id_pelanggan:
            tampilkan_paket()
            pilihan = input("Pilih paket baru: ")

            if pilihan not in paket_wifi:
                print("Paket tidak valid!")
                return

            paket = paket_wifi[pilihan]

            if paket[2] <= int(p["Biaya"]):
                print("Pilih paket yang lebih tinggi!")
                return

            p["Paket"] = paket[0]
            p["Kecepatan"] = paket[1]
            p["Biaya"] = paket[2]
            p["Status Tagihan"] = "Belum Lunas"

            simpan_data(data)
            print("Upgrade paket berhasil!")
            return


# UPDATE: Mengubah password
def ubah_password(id_pelanggan):
    data = baca_data()

    for p in data:
        if p["ID"] == id_pelanggan:
            password = input("Password baru: ")

            if not password.strip():
                print("Password tidak boleh kosong!")
                return

            p["Password"] = password
            simpan_data(data)
            print("Password berhasil diubah!")
            return


# DELETE: Berhenti berlangganan
def berhenti_langganan(id_pelanggan):
    data = baca_data()

    for p in data:
        if p["ID"] == id_pelanggan:
            konfirmasi = input(
                "Yakin berhenti berlangganan? (y/n): "
            )

            if konfirmasi.lower() == "y":
                data.remove(p)
                simpan_data(data)
                print("Langganan berhasil dihentikan!")
            else:
                print("Pembatalan berhasil!")
            return


# Menu pelanggan
def menu_pelanggan(id_pelanggan):
    while True:
        print("\n===== MENU BILLINGNET =====")
        print("1. Cek Tagihan")
        print("2. Upgrade Paket")
        print("3. Ubah Password")
        print("4. Berhenti Berlangganan")
        print("5. Logout")

        pilihan = input("Pilih menu: ")

        if pilihan == "1":
            cek_tagihan(id_pelanggan)
        elif pilihan == "2":
            upgrade_paket(id_pelanggan)
        elif pilihan == "3":
            ubah_password(id_pelanggan)
        elif pilihan == "4":
            berhenti_langganan(id_pelanggan)
            data = baca_data()
            if not any(p["ID"] == id_pelanggan for p in data):
                break
        elif pilihan == "5":
            break
        else:
            print("Pilihan tidak valid!")


# Program utama
def main():
    buat_file()

    while True:
        print("\n==============================")
        print("       BILLINGNET WIFI")
        print("==============================")
        print("1. Registrasi")
        print("2. Login")
        print("3. Keluar")

        pilihan = input("Pilih menu: ")

        if pilihan == "1":
            registrasi()
        elif pilihan == "2":
            login()
        elif pilihan == "3":
            print("Terima kasih telah menggunakan BillingNet!")
            break
        else:
            print("Pilihan tidak valid!")


main()

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