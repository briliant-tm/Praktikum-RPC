"""Pertanyaan analisis Praktikum 1: ukuran pesan XML-RPC untuk tambah(5, 3).

Tidak memerlukan server; pesan dibuat dengan xmlrpc.client.dumps() yang sama
dengan yang dipakai ServerProxy.
"""
import xmlrpc.client

permintaan = xmlrpc.client.dumps((5, 3), methodname="tambah").encode("utf-8")
balasan = xmlrpc.client.dumps((8,), methodresponse=True).encode("utf-8")

# "Data sebenarnya": nama prosedur + kedua operand (sebagai teks) pada permintaan,
# dan hasil pada balasan.
data_permintaan = len("tambah") + len("5") + len("3")
data_balasan = len("8")

print("=== <methodCall> ===")
print(permintaan.decode())
print(f"Ukuran       : {len(permintaan)} byte")
print(f"Data nyata   : {data_permintaan} byte ('tambah' + '5' + '3')")
print(f"Overhead     : {len(permintaan) - data_permintaan} byte")
print(f"Persentase   : data {data_permintaan / len(permintaan) * 100:.1f}% | overhead {(1 - data_permintaan / len(permintaan)) * 100:.1f}%")

print("\n=== <methodResponse> ===")
print(balasan.decode())
print(f"Ukuran       : {len(balasan)} byte")
print(f"Data nyata   : {data_balasan} byte ('8')")
print(f"Overhead     : {len(balasan) - data_balasan} byte")
print(f"Persentase   : data {data_balasan / len(balasan) * 100:.1f}% | overhead {(1 - data_balasan / len(balasan)) * 100:.1f}%")

total = len(permintaan) + len(balasan)
data_total = data_permintaan + data_balasan
print(f"\nTotal satu pemanggilan (hanya body XML, tanpa header HTTP): {total} byte")
print(f"Data nyata {data_total} byte = {data_total / total * 100:.1f}% | overhead {(1 - data_total / total) * 100:.1f}%")
