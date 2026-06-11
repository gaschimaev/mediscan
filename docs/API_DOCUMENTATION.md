# Dokumentasi API AImediScan

## 1. Deskripsi API

AImediScan menggunakan backend berbasis FastAPI untuk menangani upload gambar, analisis awal menggunakan AI, penyimpanan file ke Azure Blob Storage, serta penyimpanan hasil analisis ke database MySQL.

Backend API berjalan pada port `8000`.

---

## 2. Base URL

### Production

```text
http://34.236.244.119:8000
```

### Local Development

```text
http://localhost:8000
```

Dokumentasi Swagger dapat diakses melalui:

```text
Production:
http://34.236.244.119:8000/docs

Local:
http://localhost:8000/docs
```

Health check API dapat diakses melalui:

```text
Production:
http://34.236.244.119:8000/api/health

Local:
http://localhost:8000/api/health
```

---

## 3. Daftar Endpoint

| Method | Endpoint                   | Keterangan                                            |
| ------ | -------------------------- | ----------------------------------------------------- |
| GET    | `/`                        | Root endpoint untuk mengecek API                      |
| GET    | `/api/health`              | Mengecek status backend, AI token, dan database       |
| POST   | `/api/upload`              | Upload gambar, analisis AI, simpan ke Azure dan MySQL |
| GET    | `/api/history`             | Mengambil riwayat analisis                            |
| DELETE | `/api/history/{record_id}` | Menghapus satu data riwayat                           |

---

## 4. Root Endpoint

### Endpoint

```http
GET /
```

### Production

```http
GET http://34.236.244.119:8000/
```

### Local

```http
GET http://localhost:8000/
```

### Fungsi

Digunakan untuk mengecek apakah API utama berjalan.

### Contoh Response

```json
{
  "message": "MediScan API berjalan ✅",
  "docs": "/docs"
}
```

---

## 5. Health Check

### Endpoint

```http
GET /api/health
```

### Production

```http
GET http://34.236.244.119:8000/api/health
```

### Local

```http
GET http://localhost:8000/api/health
```

### Fungsi

Digunakan untuk mengecek status backend, koneksi token Hugging Face, dan database.

### Contoh Response

```json
{
  "status": "ok",
  "hf_connected": true,
  "database": "mysql",
  "db_name": "mediscan"
}
```

### Keterangan Field

| Field        | Keterangan                                    |
| ------------ | --------------------------------------------- |
| status       | Status backend                                |
| hf_connected | Menunjukkan apakah token Hugging Face terbaca |
| database     | Jenis database yang digunakan                 |
| db_name      | Nama database                                 |

---

## 6. Upload dan Analisis Gambar

### Endpoint

```http
POST /api/upload
```

### Production

```http
POST http://34.236.244.119:8000/api/upload
```

### Local

```http
POST http://localhost:8000/api/upload
```

### Fungsi

Endpoint ini digunakan untuk menerima file gambar dari frontend, mengupload file ke Azure Blob Storage, melakukan analisis menggunakan AI, lalu menyimpan hasilnya ke database MySQL.

### Request

Tipe request:

```text
multipart/form-data
```

Parameter:

| Key  | Type | Wajib | Keterangan                            |
| ---- | ---- | ----- | ------------------------------------- |
| file | File | Ya    | File gambar JPG, JPEG, PNG, atau WEBP |

### Validasi File

- Format yang diterima: JPG, JPEG, PNG, WEBP.
- Ukuran maksimal file: 10 MB.

### Contoh Response

```json
{
  "id": "2ab258b2-83d0-4c2d-bf4f-1a3d0b638ba1",
  "filename": "doterb1.png",
  "file_url": "https://aimediscanstorage.blob.core.windows.net/uploads/aimediscan/uploads/d49c92f6.png",
  "status": "Kritis",
  "diagnosis": "Terdeteksi lesi yang perlu pemeriksaan dokter segera.",
  "confidence": 97.5,
  "detail": "File: doterb1.png | Ukuran: 1792 KB | Azure: tersimpan",
  "created_at": "2026-06-10 22:33:16"
}
```

### Keterangan Response

| Field      | Keterangan                                      |
| ---------- | ----------------------------------------------- |
| id         | ID unik hasil analisis                          |
| filename   | Nama file yang diupload                         |
| file_url   | URL file yang tersimpan di Azure Blob Storage   |
| status     | Status hasil analisis                           |
| diagnosis  | Hasil diagnosis awal                            |
| confidence | Tingkat keyakinan hasil analisis                |
| detail     | Detail ukuran file dan status penyimpanan Azure |
| created_at | Waktu analisis dilakukan                        |

---

## 7. Riwayat Analisis

### Endpoint

```http
GET /api/history
```

### Production

```http
GET http://34.236.244.119:8000/api/history
```

### Local

```http
GET http://localhost:8000/api/history
```

### Fungsi

Digunakan untuk mengambil data riwayat analisis dari database MySQL.

### Contoh Response

```json
[
  {
    "id": "2ab258b2-83d0-4c2d-bf4f-1a3d0b638ba1",
    "filename": "doterb1.png",
    "file_url": "https://aimediscanstorage.blob.core.windows.net/uploads/aimediscan/uploads/d49c92f6.png",
    "status": "Kritis",
    "diagnosis": "Terdeteksi lesi yang perlu pemeriksaan dokter segera.",
    "confidence": 97.5,
    "detail": "File: doterb1.png | Ukuran: 1792 KB | Azure: tersimpan",
    "created_at": "2026-06-10 22:33:16"
  }
]
```

---

## 8. Hapus Riwayat

### Endpoint

```http
DELETE /api/history/{record_id}
```

### Production

```http
DELETE http://34.236.244.119:8000/api/history/{record_id}
```

### Local

```http
DELETE http://localhost:8000/api/history/{record_id}
```

### Fungsi

Digunakan untuk menghapus satu data riwayat analisis berdasarkan ID.

### Path Parameter

| Parameter | Keterangan                         |
| --------- | ---------------------------------- |
| record_id | ID data analisis yang akan dihapus |

### Contoh Response

```json
{
  "deleted": "2ab258b2-83d0-4c2d-bf4f-1a3d0b638ba1"
}
```

---

## 9. Environment Variable API

Backend membutuhkan environment variable berikut:

```env
HF_TOKEN=your_huggingface_token

DB_HOST=your_database_host
DB_PORT=3306
DB_NAME=mediscan
DB_USER=your_database_user
DB_PASSWORD=your_database_password

AZURE_STORAGE_CONNECTION_STRING=your_azure_connection_string
AZURE_CONTAINER_NAME=uploads
```

---

## 10. Dokumentasi Swagger

FastAPI menyediakan dokumentasi otomatis melalui Swagger UI.

Akses Swagger:

```text
Production:
http://34.236.244.119:8000/docs

Local:
http://localhost:8000/docs
```

Melalui Swagger UI, endpoint dapat diuji langsung tanpa Postman.
