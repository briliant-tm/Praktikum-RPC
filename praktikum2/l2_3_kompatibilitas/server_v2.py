"""L2.3 - Server versi baru (Mahasiswa punya field prodi).

Jalankan SETELAH server versi 1 dihentikan (port sama), atau pakai --port lain.
"""
import argparse
from concurrent import futures

import grpc

import akademik_pb2 as pb
import akademik_pb2_grpc as pb_grpc

DATA = {"2023001": ("Andi", 3.26, "Informatika"), "2023002": ("Sari", 3.68, "Informatika")}


class LayananNilai(pb_grpc.LayananNilaiServicer):
    def GetMahasiswa(self, request, context):
        if request.nim not in DATA:
            context.abort(grpc.StatusCode.NOT_FOUND, f"NIM {request.nim} tidak ditemukan")
        nama, ipk, prodi = DATA[request.nim]
        return pb.Mahasiswa(nim=request.nim, nama=nama, ipk=ipk, prodi=prodi)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--port", type=int, default=50051)
    a = ap.parse_args()
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=4))
    pb_grpc.add_LayananNilaiServicer_to_server(LayananNilai(), server)
    server.add_insecure_port(f"[::]:{a.port}")
    server.start()
    print(f"Server v2 (dengan field prodi) berjalan di port {a.port}...")
    try:
        server.wait_for_termination()
    except KeyboardInterrupt:
        server.stop(grace=1)
