"""Generate stub gRPC untuk semua file .proto di proyek ini.

Jalankan dari folder utama (yang berisi folder praktikum1, praktikum2, praktikum3):
    python generate_stubs.py
"""
import os
import subprocess
import sys

BASE = os.path.dirname(os.path.abspath(__file__))

# Folder yang berisi file .proto
TARGET = [
    os.path.join(BASE, "praktikum2"),
    os.path.join(BASE, "praktikum2", "l2_3_kompatibilitas"),
    os.path.join(BASE, "praktikum3"),
]


def generate(folder):
    proto = os.path.join(folder, "akademik.proto")
    if not os.path.isfile(proto):
        print(f"[LEWAT] {proto} tidak ditemukan")
        return False
    perintah = [
        sys.executable, "-m", "grpc_tools.protoc",
        f"-I{folder}",
        f"--python_out={folder}",
        f"--grpc_python_out={folder}",
        proto,
    ]
    hasil = subprocess.run(perintah, capture_output=True, text=True)
    if hasil.returncode != 0:
        print(f"[GAGAL] {folder}\n{hasil.stderr}")
        return False
    print(f"[OK]    {os.path.relpath(folder, BASE)} -> akademik_pb2.py, akademik_pb2_grpc.py")
    return True


if __name__ == "__main__":
    sukses = [generate(f) for f in TARGET]
    sys.exit(0 if all(sukses) else 1)
