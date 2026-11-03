"""L2.2 - Client interaktif untuk ruang diskusi (bidirectional streaming).

Pemakaian (buka 2 terminal atau lebih):
    python l2_2_client_diskusi.py Andi
    python l2_2_client_diskusi.py Sari
Ketik pesan lalu Enter. Ketik /keluar untuk keluar.
"""
import queue
import sys
import threading

import grpc

import akademik_pb2 as pb
import akademik_pb2_grpc as pb_grpc

nama = sys.argv[1] if len(sys.argv) > 1 else "Anonim"
alamat = sys.argv[2] if len(sys.argv) > 2 else "localhost:50051"
keluar = queue.Queue()


def pesan_keluar():
    yield pb.Pesan(pengirim="sistem", isi=f"{nama} bergabung ke diskusi")
    while True:
        isi = keluar.get()
        if isi is None:
            return
        yield pb.Pesan(pengirim=nama, isi=isi)


def terima(aliran):
    try:
        for p in aliran:
            print(f"\n[{p.pengirim}] {p.isi}\n> ", end="", flush=True)
    except grpc.RpcError as e:
        if e.code() != grpc.StatusCode.CANCELLED:
            print(f"\nKoneksi berakhir: {e.code().name}")


with grpc.insecure_channel(alamat) as channel:
    stub = pb_grpc.LayananNilaiStub(channel)
    aliran = stub.Diskusi(pesan_keluar())
    pembaca = threading.Thread(target=terima, args=(aliran,), daemon=True)
    pembaca.start()
    print(f"Terhubung sebagai {nama}. Ketik pesan, atau /keluar untuk berhenti.")
    try:
        while True:
            baris = input("> ").strip()
            if baris == "/keluar":
                break
            if baris:
                keluar.put(baris)
    except (KeyboardInterrupt, EOFError):
        pass
    keluar.put(None)
    pembaca.join(timeout=2)
    print("Keluar dari diskusi.")
