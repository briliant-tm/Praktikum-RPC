"""L2.1 - Client streaming: KirimBanyakNilai.

Mengirim banyak NilaiRequest dalam satu pemanggilan. Satu data sengaja di luar
rentang (150) untuk memperlihatkan bahwa server menolaknya.
"""
import sys

import grpc

import akademik_pb2 as pb
import akademik_pb2_grpc as pb_grpc

alamat = sys.argv[1] if len(sys.argv) > 1 else "localhost:50051"

DAFTAR = [
    ("2023001", "Struktur Data", 90.0),
    ("2023001", "Pemrograman Web", 82.5),
    ("2023002", "Jaringan", 88.0),
    ("2023002", "Komputasi Paralel", 95.0),
    ("2023003", "Basis Data", 76.0),
    ("2023003", "Data Salah", 150.0),   # ditolak server
]


def hasilkan_nilai():
    for nim, matkul, nilai in DAFTAR:
        print(f"  mengirim: {nim} | {matkul} | {nilai}")
        yield pb.NilaiRequest(nim=nim, matkul=matkul, nilai=nilai)


with grpc.insecure_channel(alamat) as channel:
    stub = pb_grpc.LayananNilaiStub(channel)
    try:
        print(f"Mengirim {len(DAFTAR)} nilai dalam satu stream...")
        balasan = stub.KirimBanyakNilai(hasilkan_nilai(), timeout=10)
        print(f"Balasan server: sukses={balasan.sukses}, pesan='{balasan.pesan}'")

        print("\nVerifikasi lewat StreamNilai untuk NIM 2023001:")
        for n in stub.StreamNilai(pb.MahasiswaRequest(nim="2023001"), timeout=10):
            print(f"  {n.matkul}: {n.nilai}")
    except grpc.RpcError as e:
        print(f"Gagal: {e.code().name} - {e.details()}")
