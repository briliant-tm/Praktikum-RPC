"""L1.5 - Server dimatikan saat client sedang berjalan.

Mode 'mentah' : tanpa penanganan error (untuk melihat exception aslinya).
Mode 'aman'   : dengan timeout, penanganan exception, dan retry berjeda.

Pemakaian:
    python l1_5_server_mati.py mentah [host]
    python l1_5_server_mati.py aman   [host]

Cara uji: jalankan server, jalankan client ini, lalu matikan server (Ctrl+C)
saat client masih mencetak hasil. Pada mode 'aman', jalankan server lagi untuk
melihat client pulih sendiri.
"""
import http.client
import socket
import sys
import time
import xmlrpc.client

mode = sys.argv[1] if len(sys.argv) > 1 else "mentah"
host = sys.argv[2] if len(sys.argv) > 2 else "localhost"
URL = f"http://{host}:8000/"


class TransportDenganTimeout(xmlrpc.client.Transport):
    """ServerProxy bawaan tidak punya parameter timeout; ini cara menambahkannya."""

    def __init__(self, timeout=3.0, **kw):
        super().__init__(**kw)
        self._timeout = timeout

    def make_connection(self, host):
        conn = super().make_connection(host)
        conn.timeout = self._timeout
        return conn


def mode_mentah():
    proxy = xmlrpc.client.ServerProxy(URL)
    i = 0
    while True:
        i += 1
        print(f"[{i}] tambah({i}, 1) = {proxy.tambah(i, 1)}")  # tidak ada try/except
        time.sleep(1)


def mode_aman(maks_ulang=5):
    proxy = xmlrpc.client.ServerProxy(URL, transport=TransportDenganTimeout(3.0))
    kesalahan_jaringan = (ConnectionError, socket.timeout, http.client.HTTPException, OSError)
    i = 0
    while True:
        i += 1
        for percobaan in range(1, maks_ulang + 1):
            try:
                print(f"[{i}] tambah({i}, 1) = {proxy.tambah(i, 1)}")
                break
            except xmlrpc.client.Fault as e:
                print(f"[{i}] Error dari server (Fault): {e.faultString}")
                break
            except kesalahan_jaringan as e:
                jeda = min(0.5 * 2 ** (percobaan - 1), 4.0)
                print(f"[{i}] Percobaan {percobaan}/{maks_ulang} gagal "
                      f"({type(e).__name__}: {e}); ulang dalam {jeda} s")
                time.sleep(jeda)
        else:
            print(f"[{i}] Server tetap tidak merespons setelah {maks_ulang} percobaan. Berhenti.")
            return
        time.sleep(1)


if __name__ == "__main__":
    try:
        mode_aman() if mode == "aman" else mode_mentah()
    except KeyboardInterrupt:
        print("\nClient dihentikan.")
