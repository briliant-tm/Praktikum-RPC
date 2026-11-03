"""L2.3 - Client LAMA: memakai stub versi 1 (tanpa field prodi) terhadap server baru.

Jalankan dari folder praktikum2 (stub v1 ada di sini), sementara server_v2.py
berjalan di folder l2_3_kompatibilitas.
"""
import sys

import grpc

import akademik_pb2 as pb
import akademik_pb2_grpc as pb_grpc

alamat = sys.argv[1] if len(sys.argv) > 1 else "localhost:50051"

with grpc.insecure_channel(alamat) as channel:
    stub = pb_grpc.LayananNilaiStub(channel)
    try:
        mhs = stub.GetMahasiswa(pb.MahasiswaRequest(nim="2023001"), timeout=5)
        print(f"{mhs.nama} - IPK {mhs.ipk}")
        print("Atribut yang dikenal stub lama:", [f.name for f in mhs.DESCRIPTOR.fields])
        print("Byte mentah balasan (termasuk field 4 yang tidak dikenal):")
        print(" ", mhs.SerializeToString())
        ada = b"Informatika" in mhs.SerializeToString()
        print("Field 4 yang tidak dikenal tetap terbawa saat diserialisasi ulang:", ada)
    except grpc.RpcError as e:
        print(f"Gagal: {e.code().name} - {e.details()}")
