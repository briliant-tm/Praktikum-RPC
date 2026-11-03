"""L1.4 - Mengukur waktu 100 kali pemanggilan tambah() lewat XML-RPC dan lokal.

Pemakaian:
    python l1_4_benchmark.py 192.168.1.10     # server di komputer lain (yang diminta modul)
    python l1_4_benchmark.py                  # server di localhost (pembanding)
"""
import sys
import time
import xmlrpc.client

N = 100
host = sys.argv[1] if len(sys.argv) > 1 else "localhost"


def tambah_lokal(a, b):
    return a + b


def ukur_lokal():
    mulai = time.perf_counter()
    for i in range(N):
        tambah_lokal(i, i + 1)
    return time.perf_counter() - mulai


def ukur_rpc(proxy):
    mulai = time.perf_counter()
    for i in range(N):
        proxy.tambah(i, i + 1)
    return time.perf_counter() - mulai


if __name__ == "__main__":
    proxy = xmlrpc.client.ServerProxy(f"http://{host}:8000/")  # verbose dimatikan
    try:
        proxy.tambah(1, 1)  # pemanasan: koneksi pertama biasanya lebih lambat
    except (ConnectionError, OSError) as e:
        sys.exit(f"Tidak dapat terhubung ke {host}:8000 -> {type(e).__name__}: {e}")

    t_lokal = ukur_lokal()
    t_rpc = ukur_rpc(proxy)

    print(f"Server              : {host}:8000")
    print(f"Jumlah pemanggilan  : {N}")
    print(f"Fungsi lokal        : {t_lokal * 1000:10.4f} ms total | {t_lokal / N * 1e6:12.2f} us/panggilan")
    print(f"XML-RPC             : {t_rpc * 1000:10.4f} ms total | {t_rpc / N * 1e3:12.4f} ms/panggilan")
    if t_lokal > 0:
        print(f"RPC lebih lambat    : {t_rpc / t_lokal:,.0f} kali dibanding panggilan lokal")
