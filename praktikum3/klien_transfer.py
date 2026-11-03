"""Praktikum 3 - Client dengan timeout dan retry (exponential backoff).

transfer_dengan_retry() mengikuti modul. Parameter uuid_baru_tiap_percobaan=True
dipakai pada L3.2 untuk memperlihatkan bahaya retry tanpa ID permintaan yang tetap.
"""
import time
import uuid

import grpc

import akademik_pb2 as pb

STATISTIK = {"retry": 0}  # jumlah percobaan ulang selama proses berjalan


def transfer_dengan_retry(stub, dari, ke, jumlah, maks=3, timeout=2.0,
                          uuid_baru_tiap_percobaan=False, tampilkan=True):
    rid = str(uuid.uuid4())  # ID sama untuk setiap percobaan
    for percobaan in range(1, maks + 1):
        if uuid_baru_tiap_percobaan:
            rid = str(uuid.uuid4())  # SALAH: server menganggap setiap percobaan sebagai transfer baru
        try:
            req = pb.TransferRequest(request_id=rid, dari=dari, ke=ke, jumlah=jumlah)
            return stub.Transfer(req, timeout=timeout)
        except grpc.RpcError as e:
            bisa_ulang = e.code() in (grpc.StatusCode.DEADLINE_EXCEEDED,
                                      grpc.StatusCode.UNAVAILABLE)
            if not bisa_ulang or percobaan == maks:
                raise
            STATISTIK["retry"] += 1
            jeda = 0.5 * 2 ** (percobaan - 1)
            if tampilkan:
                print(f"Percobaan {percobaan} gagal ({e.code().name}), ulang dalam {jeda} s", flush=True)
            time.sleep(jeda)


def ambil_saldo(stub):
    return dict(stub.GetSaldo(pb.SaldoRequest(), timeout=5).saldo)
