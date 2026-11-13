import os
import csv
import sys
from datetime import datetime

folder_utama = os.path.join(os.path.dirname(__file__))
file_admin = os.path.join(folder_utama, 'admin.csv')
file_pelanggan = os.path.join(folder_utama, 'pelanggan.csv')
file_paket = os.path.join(folder_utama, 'paket.csv')
file_pembayaran = os.path.join(folder_utama, 'pembayaran.csv')

header_admin = ['username', 'password']
header_pelanggan = ["id_pelanggan", "username", "password", "nama", "alamat", "no_hp", "id_paket", "tanggal_daftar"]
header_paket = ['id_paket', 'nama', 'harga']
header_pembayaran = ['id_pembayaran', 'id_pelanggan','bulan', 'tahun', 'id_paket', 'nominal', 'status', 'tanggal_pembayaran', 'jumlah']