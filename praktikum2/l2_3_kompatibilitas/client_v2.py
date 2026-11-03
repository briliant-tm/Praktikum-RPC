"""L2.3 - Client versi baru (stub sudah digenerate ulang, tahu field prodi).

Dipakai juga untuk uji arah sebaliknya: client baru terhadap server lama (v1).
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
        print(f"{mhs.nama} - IPK {mhs.ipk} - prodi: {mhs.prodi!r}")
        print(f"Field prodi terisi? {mhs.prodi != ''}")
    except grpc.RpcError as e:
        print(f"Gagal: {e.code().name} - {e.details()}")
