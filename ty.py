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