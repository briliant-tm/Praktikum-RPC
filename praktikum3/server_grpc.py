"""Praktikum 3 - Server gRPC dengan Transfer (deduplikasi, balasan lambat acak).

Opsi (semua punya nilai bawaan yang sama dengan modul):
    --port 50051        port server
    --workers 10        jumlah thread pekerja (L3.4)
    --delay-getmhs 0    jeda buatan pada GetMahasiswa, detik (L3.4: pakai 0.1)
    --delay-prob 0.3    peluang balasan Transfer ditunda (0 untuk mematikan)
    --delay-detik 3     lama penundaan balasan Transfer
    --tanpa-lock        menonaktifkan LOCK pada Transfer (L3.3)
    --jendela-race 0    jeda (detik) antara membaca dan menulis saldo; hanya untuk
                        memperlebar peluang race condition saat --tanpa-lock
"""
import argparse
import contextlib
import random
import threading
import time
from concurrent import futures

import grpc

import akademik_pb2 as pb
import akademik_pb2_grpc as pb_grpc

DATA = {
    "2023001": {"nama": "Andi", "nilai": {"Basis Data": 85.0, "Jaringan": 78.0}},
    "2023002": {"nama": "Sari", "nilai": {"Basis Data": 92.0}},
}

SALDO = {"A": 1000.0, "B": 500.0}
PROSES = {}  # request_id -> StatusResponse yang sudah dikirim
LOCK = threading.Lock()


class LayananNilai(pb_grpc.LayananNilaiServicer):
    def __init__(self, nama_server, delay_getmhs=0.0, delay_prob=0.3, delay_detik=3.0,
                 pakai_lock=True, jendela_race=0.0):
        self.nama_server = nama_server
        self.delay_getmhs = delay_getmhs
        self.delay_prob = delay_prob
        self.delay_detik = delay_detik
        self.jendela_race = jendela_race
        # Tanpa lock: with-block tetap ada, tetapi tidak melindungi apa pun.
        self.kunci = LOCK if pakai_lock else contextlib.nullcontext()

    # ---------------- RPC dari Praktikum 2 ----------------
    def GetMahasiswa(self, request, context):
        if self.delay_getmhs:
            time.sleep(self.delay_getmhs)
        context.set_trailing_metadata((("x-server", self.nama_server),))
        mhs = DATA.get(request.nim)
        if mhs is None:
            context.abort(grpc.StatusCode.NOT_FOUND, f"NIM {request.nim} tidak ditemukan")
        daftar = list(mhs["nilai"].values())
        ipk = sum(daftar) / len(daftar) / 25 if daftar else 0.0  # konversi sederhana 0-100 ke 0-4
        return pb.Mahasiswa(nim=request.nim, nama=mhs["nama"], ipk=round(ipk, 2))

    def TambahNilai(self, request, context):
        if not 0 <= request.nilai <= 100:
            context.abort(grpc.StatusCode.INVALID_ARGUMENT, "Nilai harus 0-100")
        mhs = DATA.setdefault(request.nim, {"nama": "(baru)", "nilai": {}})
        mhs["nilai"][request.matkul] = request.nilai
        return pb.StatusResponse(sukses=True, pesan="Nilai tersimpan")

    def StreamNilai(self, request, context):
        mhs = DATA.get(request.nim)
        if mhs is None:
            context.abort(grpc.StatusCode.NOT_FOUND, "NIM tidak ditemukan")
        for matkul, nilai in mhs["nilai"].items():
            yield pb.Nilai(matkul=matkul, nilai=nilai)
            time.sleep(0.5)

    # ---------------- Praktikum 3 ----------------
    def Transfer(self, request, context):
        if not request.request_id:
            context.abort(grpc.StatusCode.INVALID_ARGUMENT, "request_id wajib diisi")
        if request.dari not in SALDO or request.ke not in SALDO:
            context.abort(grpc.StatusCode.INVALID_ARGUMENT, "Rekening tidak dikenal")
        if request.jumlah <= 0:
            context.abort(grpc.StatusCode.INVALID_ARGUMENT, "Jumlah harus positif")

        with self.kunci:
            if request.request_id in PROSES:  # permintaan duplikat
                return PROSES[request.request_id]
            saldo_dari = SALDO[request.dari]  # baca
            if saldo_dari < request.jumlah:
                hasil = pb.StatusResponse(sukses=False, pesan="Saldo tidak cukup")
            else:
                if self.jendela_race:
                    time.sleep(self.jendela_race)  # hanya untuk memperlebar celah race (L3.3)
                SALDO[request.dari] = saldo_dari - request.jumlah  # tulis
                SALDO[request.ke] += request.jumlah
                hasil = pb.StatusResponse(sukses=True, pesan=f"Saldo kini {SALDO}")
            PROSES[request.request_id] = hasil

        if random.random() < self.delay_prob:
            time.sleep(self.delay_detik)  # simulasi balasan terlambat: transfer SUDAH terjadi
        return hasil

    def GetSaldo(self, request, context):
        return pb.SaldoResponse(saldo=dict(SALDO))


def serve(a):
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=a.workers))
    layanan = LayananNilai(
        nama_server=f"port-{a.port}",
        delay_getmhs=a.delay_getmhs,
        delay_prob=a.delay_prob,
        delay_detik=a.delay_detik,
        pakai_lock=not a.tanpa_lock,
        jendela_race=a.jendela_race,
    )
    pb_grpc.add_LayananNilaiServicer_to_server(layanan, server)
    server.add_insecure_port(f"[::]:{a.port}")
    server.start()
    print(f"Server gRPC berjalan di port {a.port} | workers={a.workers} | "
          f"lock={'MATI' if a.tanpa_lock else 'aktif'} | delay-prob={a.delay_prob}", flush=True)
    try:
        server.wait_for_termination()
    except KeyboardInterrupt:
        print("\nServer dihentikan.")
        server.stop(grace=1)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--port", type=int, default=50051)
    ap.add_argument("--workers", type=int, default=10)
    ap.add_argument("--delay-getmhs", type=float, default=0.0)
    ap.add_argument("--delay-prob", type=float, default=0.3)
    ap.add_argument("--delay-detik", type=float, default=3.0)
    ap.add_argument("--tanpa-lock", action="store_true")
    ap.add_argument("--jendela-race", type=float, default=0.0)
    serve(ap.parse_args())
