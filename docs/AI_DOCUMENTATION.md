# Dokumentasi AI AImediScan

## 1. Deskripsi Integrasi AI

AImediScan menggunakan Artificial Intelligence untuk melakukan simulasi analisis awal terhadap gambar kulit atau luka yang diupload oleh pengguna. Integrasi AI dilakukan pada sisi backend menggunakan FastAPI.

Backend menerima gambar dari frontend, membaca gambar dalam bentuk byte, lalu mengirim data gambar ke layanan Hugging Face Inference API.

---

## 2. Layanan AI yang Digunakan

Layanan AI yang digunakan:

```text
Hugging Face Inference API
```

Model yang digunakan pada tahap pengujian:

```text
microsoft/resnet-50
```

Endpoint model:

```text
https://api-inference.huggingface.co/models/microsoft/resnet-50
```

Token Hugging Face disimpan menggunakan environment variable:

```env
HF_TOKEN=your_huggingface_token
```

Token tidak ditulis langsung pada source code dan tidak diupload ke GitHub.

---

## 3. Alur Kerja AI

Alur kerja AI pada AImediScan:

1. Pengguna mengupload gambar melalui frontend.
2. Frontend mengirim file ke backend melalui endpoint `/api/upload`.
3. Backend memvalidasi format dan ukuran file.
4. Backend menyimpan file ke Azure Blob Storage.
5. Backend mengirim gambar ke Hugging Face Inference API.
6. Hugging Face mengembalikan hasil prediksi.
7. Backend memetakan hasil prediksi menjadi status analisis.
8. Backend menyimpan hasil analisis ke MySQL.
9. Frontend menampilkan hasil analisis kepada pengguna.

---

## 4. Output AI

Output AI disederhanakan menjadi tiga kategori:

| Status          | Keterangan                                           |
| --------------- | ---------------------------------------------------- |
| Sehat           | Kondisi dianggap tidak menunjukkan risiko tinggi     |
| Perlu Perhatian | Kondisi perlu diamati lebih lanjut                   |
| Kritis          | Kondisi perlu pemeriksaan lanjutan oleh tenaga medis |

Contoh output hasil analisis:

```json
{
  "status": "Kritis",
  "diagnosis": "Terdeteksi lesi yang perlu pemeriksaan dokter segera.",
  "confidence": 97.5
}
```

---

## 5. Fallback AI

Backend dilengkapi fallback simulasi untuk menjaga kestabilan aplikasi saat demo.

Fallback digunakan jika:

- Token Hugging Face tidak tersedia.
- Hugging Face API tidak dapat diakses.
- Koneksi internet bermasalah.
- Response AI tidak sesuai format.
- Layanan Hugging Face sedang tidak tersedia.

Jika fallback berjalan, sistem tetap menghasilkan response analisis agar fitur aplikasi tidak berhenti.

---

## 6. Batasan AI

Model yang digunakan pada project ini berfungsi sebagai proof-of-concept integrasi AI dalam sistem cloud computing. Hasil analisis tidak digunakan sebagai diagnosis medis final.

Pernyataan batasan:

```text
Hasil analisis bersifat estimasi awal dan bukan pengganti diagnosis dokter atau tenaga medis profesional.
```

Hal ini penting karena diagnosis medis membutuhkan pemeriksaan langsung oleh tenaga medis serta penggunaan model AI yang benar-benar dilatih dan divalidasi pada dataset medis.

---

## 7. Keamanan Token AI

Token Hugging Face disimpan pada environment variable:

```env
HF_TOKEN=your_huggingface_token
```

Pada pengujian lokal, token disimpan di file `.env`. Pada deployment, token disimpan melalui GitHub Secrets atau environment variable server.

File `.env` tidak diupload ke repository GitHub.

---

## 8. Hubungan AI dengan Cloud Architecture

AI Service menjadi salah satu komponen dalam arsitektur cloud AImediScan. Backend bertugas sebagai penghubung antara frontend, Azure Blob Storage, MySQL, dan Hugging Face.

Alur integrasi:

```text
Frontend
↓
Backend FastAPI
↓
Azure Blob Storage
↓
Hugging Face AI
↓
MySQL Database
↓
Frontend Result
```

Dengan alur tersebut, AImediScan tidak hanya menampilkan aplikasi web, tetapi juga mengintegrasikan layanan AI eksternal ke dalam sistem berbasis cloud.
