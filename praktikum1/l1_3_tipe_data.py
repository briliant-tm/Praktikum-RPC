"""L1.3 - Mengirim datetime dan bilangan yang sangat besar lewat XML-RPC.

Pemakaian: python l1_3_tipe_data.py [host]
"""
import datetime
import sys
import xmlrpc.client

host = sys.argv[1] if len(sys.argv) > 1 else "localhost"
proxy = xmlrpc.client.ServerProxy(f"http://{host}:8000/")


def coba(judul, fungsi):
    print(f"\n=== {judul} ===")
    try:
        print("Hasil :", fungsi())
    except Exception as e:  # sengaja luas: yang diamati adalah jenis exception-nya
        print(f"Exception: {type(e).__name__}: {e}")


try:
    # 1. datetime dikirim ke server
    sekarang = datetime.datetime(2026, 10, 6, 14, 30, 0)
    print("XML untuk datetime:")
    print(xmlrpc.client.dumps((sekarang,), "info_tipe"))
    coba("datetime -> server", lambda: proxy.info_tipe(sekarang))

    # 2. datetime dikirim dari server (balasan)
    coba("datetime <- server", lambda: proxy.waktu_server())

    # 3. bilangan di dalam batas int 32-bit (2^31 - 1)
    coba("int 2^31 - 1", lambda: proxy.info_tipe(2**31 - 1))

    # 4. bilangan melebihi 2^31 - 1
    coba("int 2^31", lambda: proxy.info_tipe(2**31))
    coba("int 10^20", lambda: proxy.info_tipe(10**20))

    # 5. jalan keluar: kirim sebagai string atau float
    besar = 10**20
    coba("string '10^20'", lambda: proxy.info_tipe(str(besar)))
    coba("float 1e20", lambda: proxy.info_tipe(float(besar)))
    coba("string lalu dijumlahkan di client", lambda: int(proxy.info_tipe(str(besar))["isi"].strip("'")) + 1)

except (ConnectionError, OSError) as e:
    print(f"Tidak dapat terhubung ke server {host}:8000 -> {type(e).__name__}: {e}")
