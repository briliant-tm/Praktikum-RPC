"""Praktikum 1 - Server XML-RPC (kalkulator).

Berisi fungsi dasar dari modul (tambah, kali, bagi) ditambah fungsi untuk
latihan L1.1 (pangkat, akar), L1.2 (statistik), dan L1.3 (info_tipe, waktu_server).
"""
import datetime
import math
from xmlrpc.server import SimpleXMLRPCServer


def tambah(a, b):
    return a + b


def kali(a, b):
    return a * b


def bagi(a, b):
    if b == 0:
        raise ValueError("Pembagian dengan nol")
    return a / b


# ---- L1.1 ----
def pangkat(a, b):
    return a ** b


def akar(x):
    if x < 0:
        raise ValueError("Akar dari bilangan negatif tidak didefinisikan")
    return math.sqrt(x)


# ---- L1.2 ----
def statistik(daftar):
    if not daftar:
        raise ValueError("Daftar tidak boleh kosong")
    return {
        "min": min(daftar),
        "max": max(daftar),
        "rata2": sum(daftar) / len(daftar),
    }


# ---- L1.3 ----
def info_tipe(x):
    """Mengembalikan tipe Python dan isi parameter sebagaimana diterima server."""
    return {
        "tipe": f"{type(x).__module__}.{type(x).__name__}",
        "isi": repr(x),
    }


def waktu_server():
    """Mengembalikan objek datetime dari server (untuk melihat marshalling arah balasan)."""
    return datetime.datetime.now()


if __name__ == "__main__":
    server = SimpleXMLRPCServer(("0.0.0.0", 8000), allow_none=True, logRequests=True)
    server.register_introspection_functions()
    for fungsi in (tambah, kali, bagi, pangkat, akar, statistik, info_tipe, waktu_server):
        server.register_function(fungsi, fungsi.__name__)
    print("Server XML-RPC berjalan di port 8000... (Ctrl+C untuk berhenti)")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nServer dihentikan.")
