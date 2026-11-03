"""L3.1 dan L3.2 - Uji 20 kali transfer 10 dari A ke B (berurutan).

    python l3_1_l3_2_uji_transfer.py --mode sama     # L3.1: ID permintaan sama untuk setiap percobaan
    python l3_1_l3_2_uji_transfer.py --mode baru     # L3.2: uuid baru di setiap percobaan

Jalankan server dalam keadaan baru (restart) sebelum tiap pengujian:
    python server_grpc.py
"""
import argparse
import sys

import grpc

import akademik_pb2_grpc as pb_grpc
from klien_transfer import STATISTIK, ambil_saldo, transfer_dengan_retry

ap = argparse.ArgumentParser()
ap.add_argument("--mode", choices=["sama", "baru"], default="sama")
ap.add_argument("--n", type=int, default=20)
ap.add_argument("--jumlah", type=float, default=10.0)
ap.add_argument("--alamat", default="localhost:50051")
a = ap.parse_args()

with grpc.insecure_channel(a.alamat) as channel:
    stub = pb_grpc.LayananNilaiStub(channel)
    try:
        awal = ambil_saldo(stub)
    except grpc.RpcError as e:
        sys.exit(f"Server tidak dapat dihubungi: {e.code().name}")

    print(f"Mode ID permintaan : {'SAMA tiap percobaan (L3.1)' if a.mode == 'sama' else 'BARU tiap percobaan (L3.2)'}")
    print(f"Saldo awal         : {awal} | total {sum(awal.values())}")
    sukses = gagal = 0
    for i in range(1, a.n + 1):
        try:
            transfer_dengan_retry(stub, "A", "B", a.jumlah, uuid_baru_tiap_percobaan=(a.mode == "baru"),
                                  tampilkan=False)
            sukses += 1
        except grpc.RpcError as e:
            gagal += 1
            print(f"  transfer #{i} dilaporkan GAGAL ke client: {e.code().name}")

    akhir = ambil_saldo(stub)
    kurang_a = awal["A"] - akhir["A"]
    harapan_a = a.n * a.jumlah
    print(f"\nTransfer dilaporkan sukses ke client : {sukses} dari {a.n} (gagal: {gagal})")
    print(f"Jumlah percobaan ulang (retry)       : {STATISTIK['retry']}")
    print(f"Saldo akhir                          : {akhir} | total {sum(akhir.values())}")
    print(f"Saldo A berkurang                    : {kurang_a} (seharusnya {harapan_a})")
    print(f"Total saldo tetap {sum(awal.values())}?              : {sum(akhir.values()) == sum(awal.values())}")
    if kurang_a == harapan_a:
        print("HASIL: A berkurang tepat sesuai jumlah transfer -> setiap transfer dieksekusi sekali.")
    else:
        selisih = (kurang_a - harapan_a) / a.jumlah
        print(f"HASIL: A berkurang {kurang_a - harapan_a:+} dari harapan (= {selisih:+.0f} transfer ganda).")
