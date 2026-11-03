# Praktikum RPC - Komputasi Paralel dan Terdistribusi

Briliant Arifin Putra Pratama | NIM 247006111012 | Kelas G

Semua kode diuji pada Python 3.10 ke atas. Perintah di bawah memakai PowerShell (Windows).

## 1. Instalasi

```powershell
python --version                      # minimal 3.10
python -m venv venv
venv\Scripts\activate                 # PowerShell; jika diblokir: Set-ExecutionPolicy -Scope Process Bypass
pip install -r requirements.txt
python generate_stubs.py              # membuat akademik_pb2.py dan akademik_pb2_grpc.py (Praktikum 2 dan 3)
```

Praktikum 1 hanya memakai pustaka bawaan Python, jadi tidak butuh stub.

## 2. Peta file terhadap latihan

| Latihan | File | Cara menjalankan |
|---|---|---|
| P1 Langkah 1-3, L1.1, L1.2 | `praktikum1/server_kalkulator.py`, `client_kalkulator.py` | server di terminal 1, client di terminal 2 |
| L1.3 | `praktikum1/l1_3_tipe_data.py` | server aktif, lalu jalankan skrip |
| L1.4 | `praktikum1/l1_4_benchmark.py [IP-server]` | dua komputer: `python l1_4_benchmark.py 192.168.x.x` |
| L1.5 | `praktikum1/l1_5_server_mati.py mentah` / `aman` | matikan server saat client berjalan |
| Analisis P1 | `praktikum1/l1_analisis_ukuran_xml.py` | tanpa server |
| P2 Langkah 1-4 | `praktikum2/akademik.proto`, `server_grpc.py`, `client_grpc.py` | server di terminal 1, client di terminal 2 |
| L2.1 | `praktikum2/l2_1_client_streaming.py` | server aktif |
| L2.2 | `praktikum2/l2_2_client_diskusi.py <nama>` atau `l2_2_demo_diskusi.py` | interaktif di 2+ terminal, atau demo otomatis |
| L2.3 | `praktikum2/l2_3_kompatibilitas/` + `praktikum2/l2_3_client_lama.py` | lihat bagian 4 |
| L2.4 | `praktikum2/l2_4_ukuran_pesan.py` | tanpa server |
| L2.5 | `praktikum2/l2_5_async.py` | server: `python server_grpc.py --delay-getmhs 0.3` |
| P3 Langkah 1-3 | `praktikum3/akademik.proto`, `server_grpc.py`, `klien_transfer.py` | |
| L3.1 / L3.2 | `praktikum3/l3_1_l3_2_uji_transfer.py --mode sama` / `--mode baru` | restart server sebelum tiap uji |
| L3.3 | `praktikum3/l3_3_uji_race.py` | server: `--delay-prob 0 --tanpa-lock --jendela-race 0.005` |
| L3.4 | `praktikum3/l3_4_benchmark.py` | menjalankan servernya sendiri; hasil: `hasil_l3_4.csv` dan `.png` |
| L3.5 | `praktikum3/klien_failover.py` atau `l3_5_demo_otomatis.py` | 2 server (50051, 50052) + client |
| Analisis P3 | `praktikum3/l3_analisis_dedup_sqlite.py` | tanpa server |

## 3. Dua komputer (L1.4)

Di komputer server, cari alamat IP dengan `ipconfig`, lalu buka port 8000 (PowerShell sebagai Administrator):

```powershell
New-NetFirewallRule -DisplayName "XMLRPC 8000" -Direction Inbound -Protocol TCP -LocalPort 8000 -Action Allow
```

Di komputer client: `python l1_4_benchmark.py <IP-server>`. Hapus aturan setelah selesai:
`Remove-NetFirewallRule -DisplayName "XMLRPC 8000"`.

## 4. L2.3 (kompatibilitas Protobuf), urutan langkah

```powershell
# a) Client LAMA terhadap server BARU
cd praktikum2\l2_3_kompatibilitas
python server_v2.py                    # terminal 1 (hentikan server_grpc.py dulu, port sama)
cd ..
python l2_3_client_lama.py             # terminal 2, memakai stub versi 1

# b) Client BARU terhadap server baru, lalu terhadap server lama
cd l2_3_kompatibilitas
python client_v2.py                    # server_v2 aktif
# hentikan server_v2, jalankan ..\server_grpc.py, lalu:
python client_v2.py                    # field prodi kosong karena server lama tidak mengirimnya
```

## 5. Catatan tambahan terhadap modul

- Opsi baris perintah pada server (`--workers`, `--delay-getmhs`, `--tanpa-lock`, dll.) hanya cara
  menjalankan variasi percobaan tanpa mengedit kode. Nilai bawaannya sama dengan modul.
- RPC `GetSaldo` pada Praktikum 3 tambahan dari saya, agar saldo akhir bisa diperiksa dengan benar
  (balasan duplikat mengembalikan pesan lama, jadi pesan terakhir bukan saldo terkini).
- Hasil pengukuran (L1.4, L3.4) bergantung pada komputer masing-masing. Jalankan ulang di perangkat sendiri.
