"""L2.2 - Demo otomatis ruang diskusi dengan 3 client (thread) sekaligus.

Berguna untuk tangkapan layar tanpa membuka banyak terminal. Server harus sudah jalan.
"""
import sys
import threading
import time

import grpc

import akademik_pb2 as pb
import akademik_pb2_grpc as pb_grpc

alamat = sys.argv[1] if len(sys.argv) > 1 else "localhost:50051"
CETAK = threading.Lock()

# (nama, jeda mulai, daftar pesan)
SKENARIO = [
    ("Andi", 0.0, ["Halo semuanya", "Siapa yang sudah selesai Praktikum 2?"]),
    ("Sari", 0.6, ["Halo Andi, aku baru sampai L2.2", "Bidirectional streaming-nya seru ya"]),
    ("Budi", 1.2, ["Numpang gabung, ada yang bisa jelasin stub?"]),
]


def peserta(nama, mulai, pesan_pesan):
    time.sleep(mulai)

    def kirim():
        yield pb.Pesan(pengirim="sistem", isi=f"{nama} bergabung")
        for isi in pesan_pesan:
            time.sleep(1.0)
            yield pb.Pesan(pengirim=nama, isi=isi)
        time.sleep(2.0)  # tunggu balasan peserta lain sebelum menutup stream

    with grpc.insecure_channel(alamat) as channel:
        stub = pb_grpc.LayananNilaiStub(channel)
        try:
            for p in stub.Diskusi(kirim()):
                with CETAK:
                    print(f"  (layar {nama:<4}) menerima -> [{p.pengirim}] {p.isi}")
        except grpc.RpcError as e:
            with CETAK:
                print(f"  (layar {nama}) berakhir: {e.code().name}")


if __name__ == "__main__":
    threads = [threading.Thread(target=peserta, args=s) for s in SKENARIO]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    print("Demo selesai.")
