
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
