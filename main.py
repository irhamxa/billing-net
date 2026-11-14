import os
import csv
import sys
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
                     "id_paket", "nominal", "status", "tanggal_bayar")