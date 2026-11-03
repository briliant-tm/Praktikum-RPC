"""Praktikum 2 - Server gRPC LayananNilai.

Berisi RPC dari modul (GetMahasiswa, TambahNilai, StreamNilai) ditambah
KirimBanyakNilai (L2.1) dan Diskusi (L2.2).

Opsi:
    --port 50051            port server
    --workers 10            jumlah thread pekerja
    --delay-getmhs 0.0      jeda buatan (detik) pada GetMahasiswa, untuk L2.5
"""
import argparse
import queue
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
DATA_LOCK = threading.Lock()


class RuangDiskusi:
    """Menyimpan satu antrian pesan keluar untuk setiap client yang sedang terhubung."""

    def __init__(self):
        self._kunci = threading.Lock()
        self._antrian = set()

    def masuk(self):
        q = queue.Queue()
        with self._kunci:
            self._antrian.add(q)
        return q

    def keluar(self, q):
        with self._kunci:
            self._antrian.discard(q)

    def siarkan(self, pesan, kecuali):
        """Teruskan pesan ke semua client lain (pengirim tidak menerima pesannya sendiri)."""
        with self._kunci:
            tujuan = [q for q in self._antrian if q is not kecuali]
        for q in tujuan:
            q.put(pesan)

    def jumlah(self):
        with self._kunci:
            return len(self._antrian)


RUANG = RuangDiskusi()


class LayananNilai(pb_grpc.LayananNilaiServicer):
    def __init__(self, delay_getmhs=0.0):
        self.delay_getmhs = delay_getmhs

    # ---------------- unary ----------------
    def GetMahasiswa(self, request, context):
        if self.delay_getmhs:
            time.sleep(self.delay_getmhs)
        with DATA_LOCK:
            mhs = DATA.get(request.nim)
            if mhs is None:
                context.abort(grpc.StatusCode.NOT_FOUND, f"NIM {request.nim} tidak ditemukan")
            daftar = list(mhs["nilai"].values())
            nama = mhs["nama"]
        ipk = sum(daftar) / len(daftar) / 25 if daftar else 0.0  # konversi sederhana 0-100 ke 0-4
        return pb.Mahasiswa(nim=request.nim, nama=nama, ipk=round(ipk, 2))

    def TambahNilai(self, request, context):
        if not 0 <= request.nilai <= 100:
            context.abort(grpc.StatusCode.INVALID_ARGUMENT, "Nilai harus 0-100")
        with DATA_LOCK:
            mhs = DATA.setdefault(request.nim, {"nama": "(baru)", "nilai": {}})
            mhs["nilai"][request.matkul] = request.nilai
        return pb.StatusResponse(sukses=True, pesan="Nilai tersimpan")

    # ---------------- server streaming ----------------
    def StreamNilai(self, request, context):
        with DATA_LOCK:
            mhs = DATA.get(request.nim)
            salinan = dict(mhs["nilai"]) if mhs else None
        if salinan is None:
            context.abort(grpc.StatusCode.NOT_FOUND, "NIM tidak ditemukan")
        for matkul, nilai in salinan.items():
            yield pb.Nilai(matkul=matkul, nilai=nilai)
            time.sleep(0.5)  # simulasi data dikirim bertahap

    # ---------------- client streaming (L2.1) ----------------
    def KirimBanyakNilai(self, request_iterator, context):
        tersimpan = 0
        ditolak = 0
        for req in request_iterator:
            if not 0 <= req.nilai <= 100:
                ditolak += 1
                continue
            with DATA_LOCK:
                mhs = DATA.setdefault(req.nim, {"nama": "(baru)", "nilai": {}})
                mhs["nilai"][req.matkul] = req.nilai
            tersimpan += 1
        pesan = f"{tersimpan} nilai tersimpan"
        if ditolak:
            pesan += f", {ditolak} ditolak (di luar 0-100)"
        return pb.StatusResponse(sukses=tersimpan > 0, pesan=pesan)

    # ---------------- bidirectional streaming (L2.2) ----------------
    def Diskusi(self, request_iterator, context):
        antrian_saya = RUANG.masuk()

        def baca_pesan_masuk():
            try:
                for pesan in request_iterator:
                    RUANG.siarkan(pesan, kecuali=antrian_saya)
            except grpc.RpcError:
                pass  # client terputus
            finally:
                antrian_saya.put(None)  # tanda selesai

        threading.Thread(target=baca_pesan_masuk, daemon=True).start()
        try:
            while context.is_active():
                try:
                    pesan = antrian_saya.get(timeout=0.5)
                except queue.Empty:
                    continue
                if pesan is None:
                    break
                yield pesan
        finally:
            RUANG.keluar(antrian_saya)


def serve(port, workers, delay_getmhs):
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=workers))
    pb_grpc.add_LayananNilaiServicer_to_server(LayananNilai(delay_getmhs), server)
    server.add_insecure_port(f"[::]:{port}")
    server.start()
    print(f"Server gRPC berjalan di port {port} (workers={workers})... (Ctrl+C untuk berhenti)")
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
    a = ap.parse_args()
    serve(a.port, a.workers, a.delay_getmhs)
