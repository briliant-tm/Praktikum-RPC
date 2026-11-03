"""L2.4 - Membandingkan ukuran pesan Protobuf dan XML-RPC untuk data yang sama.

Tidak memerlukan server. Data: Mahasiswa(nim='2023001', nama='Andi', ipk=3.26),
yaitu hasil GetMahasiswa("2023001") pada server Praktikum 2.
"""
import xmlrpc.client

import akademik_pb2 as pb

mhs = pb.Mahasiswa(nim="2023001", nama="Andi", ipk=3.26)
ukuran_pb = len(mhs.SerializeToString())

# Padanan XML-RPC: balasan berisi struct dengan 3 anggota.
data = {"nim": "2023001", "nama": "Andi", "ipk": 3.26}
xml = xmlrpc.client.dumps((data,), methodresponse=True)
ukuran_xml = len(xml.encode("utf-8"))

# Permintaan (request) juga dibandingkan
req_pb = len(pb.MahasiswaRequest(nim="2023001").SerializeToString())
req_xml = len(xmlrpc.client.dumps(("2023001",), methodname="GetMahasiswa").encode("utf-8"))

print("Pesan Protobuf (bytes):", mhs.SerializeToString())
print("\nPesan XML-RPC:")
print(xml)
print("-" * 52)
print(f"{'':<22}{'Protobuf':>10}{'XML-RPC':>10}{'Rasio':>9}")
print(f"{'Balasan (Mahasiswa)':<22}{ukuran_pb:>10}{ukuran_xml:>10}{ukuran_xml / ukuran_pb:>8.1f}x")
print(f"{'Permintaan (NIM)':<22}{req_pb:>10}{req_xml:>10}{req_xml / req_pb:>8.1f}x")
print(f"\nProtobuf lebih kecil {100 - ukuran_pb / ukuran_xml * 100:.1f}% pada balasan.")
