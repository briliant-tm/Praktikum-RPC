"""L2.5 - Pemanggilan asinkron dengan stub.GetMahasiswa.future().

Bandingkan 10 panggilan berurutan (sinkron) dengan 10 panggilan sekaligus (future).
Agar bedanya terlihat, jalankan server dengan jeda buatan:
    python server_grpc.py --delay-getmhs 0.3
"""
import sys
import time

import grpc

import akademik_pb2 as pb
import akademik_pb2_grpc as pb_grpc

alamat = sys.argv[1] if len(sys.argv) > 1 else "localhost:50051"
JUMLAH = 10
# 9 NIM valid (bergantian) dan 1 NIM tidak ada, untuk melihat error pada .result()
NIM = ["2023001", "2023002"] * 4 + ["2023001", "9999"]

with grpc.insecure_channel(alamat) as channel:
    stub = pb_grpc.LayananNilaiStub(channel)
    try:
        # --- sinkron ---
        mulai = time.perf_counter()
        for nim in NIM:
            try:
                stub.GetMahasiswa(pb.MahasiswaRequest(nim=nim), timeout=10)
            except grpc.RpcError:
                pass
        t_sinkron = time.perf_counter() - mulai

        # --- asinkron ---
        mulai = time.perf_counter()
        futures_list = [stub.GetMahasiswa.future(pb.MahasiswaRequest(nim=nim), timeout=10) for nim in NIM]
        t_kirim = time.perf_counter() - mulai
        print(f"{JUMLAH} permintaan dikirim dalam {t_kirim * 1000:.1f} ms (belum menunggu hasil)")

        for i, f in enumerate(futures_list, 1):
            try:
                m = f.result()
                print(f"  [{i:2}] {m.nim} {m.nama} IPK {m.ipk}")
            except grpc.RpcError as e:
                print(f"  [{i:2}] ERROR {e.code().name}: {e.details()}")
        t_async = time.perf_counter() - mulai

        print(f"\nSinkron (berurutan): {t_sinkron:.3f} s")
        print(f"Asinkron (future)  : {t_async:.3f} s")
        if t_async > 0:
            print(f"Percepatan         : {t_sinkron / t_async:.1f}x")
    except grpc.RpcError as e:
        print(f"Gagal: {e.code().name} - {e.details()}")
