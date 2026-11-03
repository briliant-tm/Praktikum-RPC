"""Praktikum 2 - Client gRPC (unary + server streaming), sesuai modul."""
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
        print(stub.TambahNilai(pb.NilaiRequest(nim="2023001", matkul="Komputasi Paralel", nilai=88),
                               timeout=5).pesan)
        for n in stub.StreamNilai(pb.MahasiswaRequest(nim="2023001"), timeout=10):
            print(f"  {n.matkul}: {n.nilai}")
        try:
            stub.GetMahasiswa(pb.MahasiswaRequest(nim="9999"), timeout=5)
        except grpc.RpcError as e:
            print("Error:", e.code(), e.details())
    except grpc.RpcError as e:
        print(f"Gagal menghubungi server {alamat}: {e.code().name} - {e.details()}")
