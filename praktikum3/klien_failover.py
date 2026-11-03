"""L3.5 - Client dengan failover otomatis antar-server.

Pemakaian (3 terminal):
    T1: python server_grpc.py --port 50051 --delay-prob 0
    T2: python server_grpc.py --port 50052 --delay-prob 0
    T3: python klien_failover.py
Setelah beberapa baris tercetak, matikan server di T1 (Ctrl+C) dan amati client pindah ke 50052.
"""
import sys
import time

import grpc

import akademik_pb2 as pb
import akademik_pb2_grpc as pb_grpc


class KlienFailover:
    def __init__(self, daftar_alamat):
        self.alamat = list(daftar_alamat)
        self.channel = [grpc.insecure_channel(a) for a in self.alamat]
        self.stub = [pb_grpc.LayananNilaiStub(c) for c in self.channel]
        self.aktif = 0  # indeks server yang sedang dipakai

    def panggil(self, nama_rpc, request, timeout=2.0):
        """Panggil RPC unary; jika server UNAVAILABLE, coba server berikutnya."""
        n = len(self.stub)
        for geser in range(n):
            i = (self.aktif + geser) % n
            try:
                respons, call = getattr(self.stub[i], nama_rpc).with_call(request, timeout=timeout)
                if i != self.aktif:
                    print(f"  [FAILOVER] berpindah dari {self.alamat[self.aktif]} ke {self.alamat[i]}", flush=True)
                    self.aktif = i
                return respons, call
            except grpc.RpcError as e:
                if e.code() != grpc.StatusCode.UNAVAILABLE:
                    raise  # kesalahan aplikasi (NOT_FOUND, dll.) tidak perlu failover
                print(f"  [UNAVAILABLE] {self.alamat[i]} tidak dapat dihubungi", flush=True)
        raise ConnectionError("Semua server tidak tersedia")

    def tutup(self):
        for c in self.channel:
            c.close()


if __name__ == "__main__":
    alamat = sys.argv[1:] or ["localhost:50051", "localhost:50052"]
    klien = KlienFailover(alamat)
    try:
        for i in range(1, 31):
            try:
                mhs, call = klien.panggil("GetMahasiswa", pb.MahasiswaRequest(nim="2023001"))
                meta = dict(call.trailing_metadata() or ())
                print(f"[{i:2}] dijawab oleh {meta.get('x-server', '?'):<11} -> {mhs.nama}, IPK {mhs.ipk}", flush=True)
            except ConnectionError as e:
                print(f"[{i:2}] {e}", flush=True)
            time.sleep(1)
    except KeyboardInterrupt:
        pass
    finally:
        klien.tutup()
