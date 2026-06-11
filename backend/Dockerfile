# Menggunakan image Python resmi yang ringan
FROM python:3.9-slim

# Menyiapkan folder kerja di dalam server
WORKDIR /app

# Menyalin daftar library yang dibutuhkan teman Anda
COPY requirements.txt .

# Meng-install library tersebut
RUN pip install --no-cache-dir -r requirements.txt

# Menyalin seluruh file backend (main.py, mediscan.db, dll)
COPY . .

# Menjalankan aplikasi. (Asumsi teman Anda memakai Uvicorn/FastAPI di port 8000)
# Jika teman Anda memakai Flask, perintahnya mungkin: CMD ["python", "main.py"]
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
