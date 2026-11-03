"""Pertanyaan analisis Praktikum 3: deduplikasi yang tahan restart server.

Masalah : PROSES (dict di memori) hilang saat server restart, sehingga retry dengan
          request_id lama dianggap permintaan baru -> transfer ganda.
Perbaikan: simpan request_id di basis data PADA TRANSAKSI YANG SAMA dengan perubahan
          saldo. Kunci PRIMARY KEY menolak request_id yang sama, dan karena satu
          transaksi, keduanya berhasil bersama atau batal bersama.

Demo ini berdiri sendiri (tidak butuh gRPC) dan mensimulasikan restart dengan
menutup lalu membuka ulang koneksi database.
"""
import os
import sqlite3

DB = os.path.join(os.path.dirname(os.path.abspath(__file__)), "bank_demo.db")


def buka():
    db = sqlite3.connect(DB)
    db.execute("CREATE TABLE IF NOT EXISTS saldo (rek TEXT PRIMARY KEY, nilai REAL NOT NULL)")
    db.execute("CREATE TABLE IF NOT EXISTS diproses (request_id TEXT PRIMARY KEY, hasil TEXT NOT NULL)")
    db.execute("INSERT OR IGNORE INTO saldo VALUES ('A', 1000.0), ('B', 500.0)")
    db.commit()
    return db


def transfer(db, request_id, dari, ke, jumlah):
    try:
        with db:  # satu transaksi: commit jika sukses, rollback jika ada exception
            sudah = db.execute("SELECT hasil FROM diproses WHERE request_id = ?", (request_id,)).fetchone()
            if sudah:
                return f"(duplikat, dijawab ulang) {sudah[0]}"
            saldo = db.execute("SELECT nilai FROM saldo WHERE rek = ?", (dari,)).fetchone()[0]
            if saldo < jumlah:
                hasil = "Saldo tidak cukup"
            else:
                db.execute("UPDATE saldo SET nilai = nilai - ? WHERE rek = ?", (jumlah, dari))
                db.execute("UPDATE saldo SET nilai = nilai + ? WHERE rek = ?", (jumlah, ke))
                hasil = "Transfer berhasil"
            db.execute("INSERT INTO diproses VALUES (?, ?)", (request_id, hasil))
            return hasil
    except sqlite3.IntegrityError:
        return "(duplikat bersamaan ditolak oleh PRIMARY KEY)"


def tampil(db):
    return dict(db.execute("SELECT rek, nilai FROM saldo").fetchall())


if __name__ == "__main__":
    if os.path.exists(DB):
        os.remove(DB)
    db = buka()
    print("Awal                  :", tampil(db))
    print("Transfer id=abc-123   :", transfer(db, "abc-123", "A", "B", 10))
    print("Saldo                 :", tampil(db))

    db.close()
    print("\n--- server restart (koneksi ditutup lalu dibuka lagi) ---\n")
    db = buka()
    print("Retry id=abc-123      :", transfer(db, "abc-123", "A", "B", 10))
    print("Saldo (tidak berubah) :", tampil(db))
    db.close()
    os.remove(DB)
