"""L3.4 - Throughput dan latensi GetMahasiswa untuk max_workers = 1, 4, 10.

Skrip ini menjalankan sendiri server untuk tiap nilai max_workers (port berbeda),
mengirim 200 pemanggilan dari 20 thread client, lalu menyimpan tabel (CSV) dan grafik (PNG)
di folder yang sama dengan skrip ini.

    python l3_4_benchmark.py
    python l3_4_benchmark.py --jeda-server 0.1 --total 200 --thread 20
"""
import argparse
import concurrent.futures
import csv
import os
import subprocess
import sys
import time

import grpc

import akademik_pb2 as pb
import akademik_pb2_grpc as pb_grpc

FOLDER = os.path.dirname(os.path.abspath(__file__))
SERVER = os.path.join(FOLDER, "server_grpc.py")
PORT_AWAL = 50061


def jalankan_server(workers, port, jeda):
    proc = subprocess.Popen(
        [sys.executable, SERVER, "--port", str(port), "--workers", str(workers),
         "--delay-getmhs", str(jeda), "--delay-prob", "0"],
        cwd=FOLDER, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )
    return proc


def tunggu_siap(alamat, batas=15):
    with grpc.insecure_channel(alamat) as ch:
        grpc.channel_ready_future(ch).result(timeout=batas)


def ukur(workers, port, total, thread, jeda):
    alamat = f"localhost:{port}"
    proc = jalankan_server(workers, port, jeda)
    try:
        tunggu_siap(alamat)
        with grpc.insecure_channel(alamat) as channel:
            stub = pb_grpc.LayananNilaiStub(channel)
            stub.GetMahasiswa(pb.MahasiswaRequest(nim="2023001"), timeout=30)  # pemanasan

            def satu_panggilan(_):
                t0 = time.perf_counter()
                stub.GetMahasiswa(pb.MahasiswaRequest(nim="2023001"), timeout=120)
                return time.perf_counter() - t0

            mulai = time.perf_counter()
            with concurrent.futures.ThreadPoolExecutor(max_workers=thread) as pool:
                latensi = list(pool.map(satu_panggilan, range(total)))
            waktu_total = time.perf_counter() - mulai
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()
    return waktu_total, total / waktu_total, sum(latensi) / len(latensi) * 1000


def gambar(baris, jalur_png, jeda, total, thread):
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError:
        print("matplotlib belum terpasang -> grafik dilewati (pip install matplotlib)")
        return
    label = [str(b["max_workers"]) for b in baris]
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(9, 3.8))
    ax1.bar(label, [b["throughput"] for b in baris], color="0.35", edgecolor="black", width=0.55)
    ax1.set_title("Throughput")
    ax1.set_xlabel("max_workers")
    ax1.set_ylabel("permintaan per detik")
    ax2.bar(label, [b["latensi_ms"] for b in baris], color="0.75", edgecolor="black", hatch="//", width=0.55)
    ax2.set_title("Latensi rata-rata")
    ax2.set_xlabel("max_workers")
    ax2.set_ylabel("milidetik")
    for ax, kunci in ((ax1, "throughput"), (ax2, "latensi_ms")):
        for i, b in enumerate(baris):
            ax.text(i, b[kunci], f"{b[kunci]:.1f}", ha="center", va="bottom", fontsize=9)
        ax.set_ylim(0, max(b[kunci] for b in baris) * 1.15)
    fig.suptitle(f"GetMahasiswa: {total} panggilan, {thread} thread client, jeda server {jeda} s", fontsize=10)
    fig.tight_layout()
    fig.savefig(jalur_png, dpi=150)
    print(f"Grafik disimpan : {jalur_png}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--total", type=int, default=200)
    ap.add_argument("--thread", type=int, default=20)
    ap.add_argument("--jeda-server", type=float, default=0.1)
    ap.add_argument("--workers", type=int, nargs="+", default=[1, 4, 10])
    a = ap.parse_args()

    baris = []
    print(f"{'max_workers':>11} {'Waktu total (s)':>16} {'Throughput (req/s)':>19} {'Latensi rata-rata (ms)':>23}")
    for i, w in enumerate(a.workers):
        waktu, thr, lat = ukur(w, PORT_AWAL + i, a.total, a.thread, a.jeda_server)
        baris.append({"max_workers": w, "waktu_total_s": round(waktu, 3),
                      "throughput": round(thr, 2), "latensi_ms": round(lat, 1)})
        print(f"{w:>11} {waktu:>16.3f} {thr:>19.2f} {lat:>23.1f}", flush=True)

    jalur_csv = os.path.join(FOLDER, "hasil_l3_4.csv")
    with open(jalur_csv, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["max_workers", "waktu_total_s", "throughput", "latensi_ms"])
        w.writeheader()
        w.writerows(baris)
    print(f"\nTabel disimpan  : {jalur_csv}")
    gambar(baris, os.path.join(FOLDER, "hasil_l3_4.png"), a.jeda_server, a.total, a.thread)
