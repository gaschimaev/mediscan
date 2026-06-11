# AImediScan - Cloud Based Skin Health Analysis

AImediScan adalah aplikasi berbasis web untuk simulasi analisis awal kesehatan kulit menggunakan Artificial Intelligence. Aplikasi ini mendukung Sustainable Development Goals (SDGs) bidang kesehatan dengan menyediakan fitur upload gambar kulit atau luka, analisis awal berbasis AI, penyimpanan file ke cloud storage, serta riwayat hasil analisis.

> Catatan: Hasil analisis pada aplikasi ini bersifat estimasi awal dan bukan pengganti diagnosis dokter atau tenaga medis profesional.

---

## URL Deployment

Aplikasi AImediScan sudah dideploy menggunakan AWS sebagai layanan utama compute dan Azure Blob Storage sebagai layanan object storage.

### Production URL

```text
Frontend:
http://34.206.64.59

Backend API:
http://34.236.244.119:8000

API Documentation:
http://34.236.244.119:8000/docs

Health Check:
http://34.236.244.119:8000/api/health
```

### Local Development URL

```text
Frontend:
http://localhost:8080

Backend API:
http://localhost:8000

API Documentation:
http://localhost:8000/docs

Health Check:
http://localhost:8000/api/health
```

Catatan: URL production menggunakan IP public AWS. Jika server AWS diganti atau IP berubah, maka URL production perlu disesuaikan kembali.

---

## Fitur Utama

* Upload gambar kulit atau luka.
* Analisis awal menggunakan AI Hugging Face.
* Penyimpanan file upload ke Azure Blob Storage.
* Penyimpanan hasil analisis ke database MySQL.
* Riwayat analisis pengguna.
* Backend API menggunakan FastAPI.
* Frontend berbasis HTML, CSS, dan JavaScript.
* Containerization menggunakan Docker.
* Deployment diarahkan ke AWS.
* Object storage menggunakan Azure sebagai implementasi multi-cloud.

---

## Arsitektur Sistem

Alur sistem AImediScan:

```text
User
↓
Frontend Web
↓
Backend API FastAPI
↓
AI Service Hugging Face
↓
Azure Blob Storage
↓
MySQL Database
```

Penjelasan singkat:

1. User mengupload gambar melalui frontend.
2. Frontend mengirim gambar ke backend melalui endpoint API.
3. Backend memvalidasi file gambar.
4. Backend mengupload file ke Azure Blob Storage.
5. Azure mengembalikan `file_url`.
6. Backend mengirim gambar ke AI Hugging Face untuk dianalisis.
7. Hasil analisis dan `file_url` disimpan ke MySQL.
8. Frontend menampilkan hasil analisis dan riwayat.

---

## Multi-Cloud Architecture

Project ini menggunakan konsep multi-cloud:

| Komponen             | Cloud / Teknologi  |
| -------------------- | ------------------ |
| Compute / Deployment | AWS                |
| Object Storage       | Azure Blob Storage |
| Database             | MySQL              |
| AI Service           | Hugging Face       |
| CI/CD                | GitHub Actions     |
| Container            | Docker             |

Azure Blob Storage digunakan sebagai object storage untuk menyimpan file gambar yang diupload user. Container yang digunakan bernama:

```text
uploads
```

File disimpan dalam struktur:

```text
uploads/aimediscan/uploads/
```

Dengan pendekatan ini, aplikasi utama berjalan pada AWS, sedangkan penyimpanan file menggunakan Azure. Hal ini menunjukkan implementasi multi-cloud karena compute dan object storage berada pada cloud provider yang berbeda.

---

## Teknologi yang Digunakan

### Frontend

* HTML
* CSS
* JavaScript
* Nginx untuk container frontend

### Backend

* Python
* FastAPI
* Uvicorn
* PyMySQL
* Azure Storage Blob SDK
* HTTPX
* Hugging Face Inference API

### Database

* MySQL

### Cloud dan DevOps

* AWS EC2
* Azure Blob Storage
* Docker
* Docker Compose
* GitHub Actions

---

## Struktur Folder

```text
MEDISCAN-MAIN/
├── backend/
│   ├── .env.example
│   ├── .dockerignore
│   ├── Dockerfile
│   ├── main.py
│   └── requirements.txt
│
├── frontend/
│   ├── .dockerignore
│   ├── Dockerfile
│   └── index.html
│
├── database/
│   └── mediscan.sql
│
├── docs/
│   ├── API_DOCUMENTATION.md
│   └── AI_DOCUMENTATION.md
│
├── docker-compose.yml
├── README.md
└── .gitignore
```

---

## Environment Variable

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

File `.env` tidak boleh diupload ke GitHub. File yang boleh diupload hanya `.env.example`.

---

## Cara Menjalankan Aplikasi

### 1. Menjalankan Secara Lokal

Pastikan Docker Desktop sudah berjalan, lalu jalankan perintah berikut dari root project:

```bash
docker compose up --build
```

Akses aplikasi lokal melalui:

```text
Frontend:
http://localhost:8080

Backend:
http://localhost:8000

Swagger API Docs:
http://localhost:8000/docs
```

### 2. Akses Aplikasi Hasil Deployment

Aplikasi yang sudah dideploy dapat diakses melalui:

```text
Frontend:
http://34.206.64.59

Backend API:
http://34.236.244.119:8000

Swagger API Docs:
http://34.236.244.119:8000/docs
```

Backend production berjalan pada AWS, sedangkan file gambar hasil upload disimpan pada Azure Blob Storage.

---

## Endpoint Utama

| Method | Endpoint                   | Fungsi                     |
| ------ | -------------------------- | -------------------------- |
| GET    | `/`                        | Mengecek API utama         |
| GET    | `/api/health`              | Mengecek status backend    |
| POST   | `/api/upload`              | Upload dan analisis gambar |
| GET    | `/api/history`             | Mengambil riwayat analisis |
| DELETE | `/api/history/{record_id}` | Menghapus riwayat analisis |

Dokumentasi lengkap API tersedia pada:

```text
docs/API_DOCUMENTATION.md
```

---

## Dokumentasi AI

AImediScan menggunakan Hugging Face Inference API sebagai layanan AI. Dokumentasi lengkap integrasi AI tersedia pada:

```text
docs/AI_DOCUMENTATION.md
```

---

## Status Implementasi

| Komponen           | Status                                    |
| ------------------ | ----------------------------------------- |
| Frontend           | Selesai                                   |
| Backend API        | Selesai                                   |
| Database MySQL     | Selesai                                   |
| Azure Blob Storage | Selesai                                   |
| AI Hugging Face    | Selesai                                   |
| Docker Container   | Selesai                                   |
| Multi-Cloud        | Selesai                                   |
| CI/CD              | Disiapkan melalui GitHub Actions          |
| CDN                | Disiapkan melalui CloudFront / Cloudflare |

---

## Catatan Keamanan

* Token Hugging Face tidak disimpan langsung pada source code.
* Azure connection string tidak disimpan langsung pada source code.
* File `.env` tidak diupload ke GitHub.
* Credential disimpan melalui environment variable atau GitHub Secrets.
* Untuk production, akses file Azure sebaiknya menggunakan private container atau SAS URL.
