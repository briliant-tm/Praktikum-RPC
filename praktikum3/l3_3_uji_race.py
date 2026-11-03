"""L3.3 - 50 transfer dari 10 thread client secara bersamaan.

Jalankan server dalam keadaan baru:
    python server_grpc.py --delay-prob 0 --tanpa-lock --jendela-race 0.005    # tanpa LOCK
    python server_grpc.py --delay-prob 0                                      # dengan LOCK (pembanding)
lalu:
    python l3_3_uji_race.py
"""
import argparse
import concurrent.futures
import sys
import uuid

import grpc

import akademik_pb2 as pb
import akademik_pb2_grpc as pb_grpc
from klien_transfer import ambil_saldo

ap = argparse.ArgumentParser()
ap.add_argument("--n", type=int, default=50)
ap.add_argument("--thread", type=int, default=10)
ap.add_argument("--jumlah", type=float, default=10.0)
ap.add_argument("--alamat", default="localhost:50051")
a = ap.parse_args()

with grpc.insecure_channel(a.alamat) as channel:
    stub = pb_grpc.LayananNilaiStub(channel)
    try:
        awal = ambil_saldo(stub)
    except grpc.RpcError as e:
        sys.exit(f"Server tidak dapat dihubungi: {e.code().name}")

    def satu_transfer(_):
        # ID unik untuk setiap transfer: ini 50 transfer berbeda, bukan retry
        req = pb.TransferRequest(request_id=str(uuid.uuid4()), dari="A", ke="B", jumlah=a.jumlah)
        return stub.Transfer(req, timeout=15).sukses

    with concurrent.futures.ThreadPoolExecutor(max_workers=a.thread) as pool:
        hasil = list(pool.map(satu_transfer, range(a.n)))

    akhir = ambil_saldo(stub)

total_awal, total_akhir = sum(awal.values()), sum(akhir.values())
harapan_a = awal["A"] - a.n * a.jumlah
harapan_b = awal["B"] + a.n * a.jumlah
print(f"{a.n} transfer dari {a.thread} thread | server melaporkan sukses: {sum(hasil)} dari {a.n}")
print(f"Saldo awal  : {awal} | total {total_awal}")
print(f"Saldo akhir : {akhir} | total {total_akhir}")
print(f"Harapan     : {{'A': {harapan_a}, 'B': {harapan_b}}} | total {total_awal}")
print(f"Total saldo tetap {total_awal}? {total_akhir == total_awal}")
print("HASIL:", "KONSISTEN" if akhir == {"A": harapan_a, "B": harapan_b} else "TIDAK KONSISTEN (race condition terjadi)")
