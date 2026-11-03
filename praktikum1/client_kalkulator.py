"""Praktikum 1 - Client XML-RPC (kalkulator) + pengujian L1.1 dan L1.2.

Pemakaian:
    python client_kalkulator.py                 # server di localhost
    python client_kalkulator.py 192.168.1.10    # server di komputer lain
"""
import sys
import xmlrpc.client

host = sys.argv[1] if len(sys.argv) > 1 else "localhost"
# verbose=True mencetak pesan HTTP + XML (untuk Langkah 3 pada modul)
proxy = xmlrpc.client.ServerProxy(f"http://{host}:8000/", verbose=True)

try:
    print("Daftar method:", proxy.system.listMethods())
    print("5 + 3 =", proxy.tambah(5, 3))
    print("4 x 7 =", proxy.kali(4, 7))

    try:
        print(proxy.bagi(10, 0))
    except xmlrpc.client.Fault as e:
        print("Error dari server:", e.faultString)

    # ---- L1.1 ----
    print("2 ^ 10 =", proxy.pangkat(2, 10))
    print("akar(144) =", proxy.akar(144))
    try:
        print(proxy.akar(-4))
    except xmlrpc.client.Fault as e:
        print("Error dari server:", e.faultString)

    # ---- L1.2 ----
    print("statistik =", proxy.statistik([4, 8, 15, 16, 23, 42]))

except (ConnectionError, OSError) as e:
    print(f"Tidak dapat terhubung ke server {host}:8000 -> {type(e).__name__}: {e}")
