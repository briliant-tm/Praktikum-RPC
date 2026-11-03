"""L3.5 - Demo failover otomatis: menjalankan 2 server, mematikan server pertama di tengah jalan.

Berguna bila tidak ingin membuka 3 terminal. Hasil identik dengan skenario manual.
"""
import os
import subprocess
import sys
import time

import grpc

import akademik_pb2 as pb
from klien_failover import KlienFailover

FOLDER = os.path.dirname(os.path.abspath(__file__))
SERVER = os.path.join(FOLDER, "server_grpc.py")


def mulai(port):
    return subprocess.Popen([sys.executable, SERVER, "--port", str(port), "--delay-prob", "0"],
                            cwd=FOLDER, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def siap(alamat):
    with grpc.insecure_channel(alamat) as ch:
        grpc.channel_ready_future(ch).result(timeout=15)


if __name__ == "__main__":
    s1, s2 = mulai(50051), mulai(50052)
    try:
        siap("localhost:50051")
        siap("localhost:50052")
        klien = KlienFailover(["localhost:50051", "localhost:50052"])
        for i in range(1, 11):
            if i == 5:
                print(">>> Mematikan server 1 (port 50051) <<<", flush=True)
                s1.terminate()
                s1.wait(timeout=5)
            mhs, call = klien.panggil("GetMahasiswa", pb.MahasiswaRequest(nim="2023001"))
            meta = dict(call.trailing_metadata() or ())
            print(f"[{i:2}] dijawab oleh {meta.get('x-server', '?'):<11} -> {mhs.nama}, IPK {mhs.ipk}", flush=True)
            time.sleep(0.5)
        klien.tutup()
    finally:
        for p in (s1, s2):
            if p.poll() is None:
                p.terminate()
