from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import os
import base64
import httpx
import uuid
import pymysql
from dotenv import load_dotenv
from datetime import datetime
from azure.storage.blob import BlobServiceClient, ContentSettings

load_dotenv()

app = FastAPI(title="MediScan API", version="1.0.0")

# ─── CORS ───────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── Konfigurasi ────────────────────────────────────────────────────────────
HF_TOKEN = os.getenv("HF_TOKEN", "")

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = int(os.getenv("DB_PORT", 3306))
DB_NAME = os.getenv("DB_NAME", "mediscan")
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")

AZURE_STORAGE_CONNECTION_STRING = os.getenv("AZURE_STORAGE_CONNECTION_STRING", "")
AZURE_CONTAINER_NAME = os.getenv("AZURE_CONTAINER_NAME", "uploads")


# ─── Koneksi Database MySQL ─────────────────────────────────────────────────
def get_db_connection():
    return pymysql.connect(
        host=DB_HOST,
        port=DB_PORT,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME,
        cursorclass=pymysql.cursors.DictCursor
    )


# ─── Inisialisasi Database MySQL ────────────────────────────────────────────
def init_db():
    conn = pymysql.connect(
        host=DB_HOST,
        port=DB_PORT,
        user=DB_USER,
        password=DB_PASSWORD,
        cursorclass=pymysql.cursors.DictCursor
    )

    try:
        with conn.cursor() as cursor:
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_NAME}")
            cursor.execute(f"USE {DB_NAME}")
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS analyses (
                    id VARCHAR(100) PRIMARY KEY,
                    filename VARCHAR(255),
                    file_url TEXT,
                    status VARCHAR(50),
                    diagnosis TEXT,
                    confidence FLOAT,
                    detail TEXT,
                    created_at DATETIME
                )
            """)
        conn.commit()
    finally:
        conn.close()


init_db()


# ─── Model Response ─────────────────────────────────────────────────────────
class AnalysisResult(BaseModel):
    id: str
    filename: str
    file_url: Optional[str] = None
    status: str
    diagnosis: str
    confidence: float
    detail: str
    created_at: str


# ─── Helper: Simpan ke Database ─────────────────────────────────────────────
def save_to_db(result: dict):
    conn = get_db_connection()

    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                INSERT INTO analyses
                (id, filename, file_url, status, diagnosis, confidence, detail, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                result["id"],
                result["filename"],
                result.get("file_url", ""),
                result["status"],
                result["diagnosis"],
                result["confidence"],
                result["detail"],
                result["created_at"]
            ))
        conn.commit()
    finally:
        conn.close()

def upload_to_azure_blob(filename: str, image_bytes: bytes, content_type: str) -> str:
    """
    Upload file gambar ke Azure Blob Storage.
    Mengembalikan URL file dari Azure.
    """

    if not AZURE_STORAGE_CONNECTION_STRING:
        print("AZURE_STORAGE_CONNECTION_STRING belum diatur.")
        return ""

    try:
        blob_service_client = BlobServiceClient.from_connection_string(
            AZURE_STORAGE_CONNECTION_STRING
        )

        file_ext = filename.split(".")[-1] if "." in filename else "jpg"
        blob_name = f"aimediscan/uploads/{uuid.uuid4()}.{file_ext}"

        blob_client = blob_service_client.get_blob_client(
            container=AZURE_CONTAINER_NAME,
            blob=blob_name
        )

        blob_client.upload_blob(
            image_bytes,
            overwrite=True,
            content_settings=ContentSettings(content_type=content_type)
        )

        return blob_client.url

    except Exception as e:
        print("AZURE UPLOAD ERROR:", str(e))
        return ""
        
# ─── Helper: Analisis Gambar via Hugging Face ───────────────────────────────
async def analyze_with_hf(image_bytes: bytes) -> dict:
    """
    Analisis gambar menggunakan Hugging Face.
    Jika Hugging Face gagal diakses, sistem otomatis fallback ke mode simulasi.
    """

    def simulation_result():
        import random

        statuses = ["Sehat", "Perlu Perhatian", "Kritis"]
        diagnoses = {
            "Sehat": "Kulit tampak normal, tidak ada kelainan terdeteksi.",
            "Perlu Perhatian": "Terdeteksi tanda-tanda iritasi ringan atau kemerahan.",
            "Kritis": "Terdeteksi lesi yang perlu pemeriksaan dokter segera.",
        }

        s = random.choice(statuses)

        return {
            "status": s,
            "diagnosis": diagnoses[s],
            "confidence": round(random.uniform(72, 98), 1),
        }

    if not HF_TOKEN:
        return simulation_result()

    headers = {
        "Authorization": f"Bearer {HF_TOKEN}",
        "Content-Type": "application/octet-stream"
    }

    try:
        async with httpx.AsyncClient(timeout=60) as client:
            resp = await client.post(
                "https://api-inference.huggingface.co/models/microsoft/resnet-50",
                headers=headers,
                content=image_bytes,
            )

        if resp.status_code != 200:
            print("HF API ERROR:", resp.status_code, resp.text)
            return simulation_result()

        predictions = resp.json()

        if not isinstance(predictions, list) or len(predictions) == 0:
            print("HF RESPONSE TIDAK SESUAI:", predictions)
            return simulation_result()

        top = predictions[0]
        label = top.get("label", "unknown")
        score = round(float(top.get("score", 0.5)) * 100, 1)

        if score > 80:
            status = "Sehat"
            diagnosis = f"Analisis menunjukkan kondisi normal ({label})."
        elif score > 55:
            status = "Perlu Perhatian"
            diagnosis = f"Terdeteksi pola yang memerlukan observasi lebih lanjut ({label})."
        else:
            status = "Kritis"
            diagnosis = f"Pola tidak biasa terdeteksi ({label}), disarankan konsultasi dokter."

        return {
            "status": status,
            "diagnosis": diagnosis,
            "confidence": score
        }

    except Exception as e:
        print("HF EXCEPTION:", str(e))
        return simulation_result()


# ════════════════════════════════════════════════════════════════════════════
# ENDPOINTS
# ════════════════════════════════════════════════════════════════════════════

@app.get("/")
def root():
    return {
        "message": "MediScan API berjalan ✅",
        "docs": "/docs"
    }


@app.get("/api/health")
def health_check():
    return {
        "status": "ok",
        "hf_connected": bool(HF_TOKEN),
        "database": "mysql",
        "db_name": DB_NAME
    }


@app.post("/api/upload", response_model=AnalysisResult)
async def upload_and_analyze(file: UploadFile = File(...)):
    allowed = {"image/jpeg", "image/png", "image/webp", "image/jpg"}

    if file.content_type not in allowed:
        raise HTTPException(
            status_code=400,
            detail="Hanya file JPG, PNG, atau WEBP yang diterima."
        )

    image_bytes = await file.read()

    if len(image_bytes) > 10 * 1024 * 1024:
        raise HTTPException(
            status_code=400,
            detail="Ukuran file maksimal 10 MB."
        )

    file_url = upload_to_azure_blob(
        filename=file.filename,
        image_bytes=image_bytes,
        content_type=file.content_type
    )

    result_data = await analyze_with_hf(image_bytes)

    record = {
        "id": str(uuid.uuid4()),
        "filename": file.filename,
        "file_url": file_url,
        "status": result_data["status"],
        "diagnosis": result_data["diagnosis"],
        "confidence": result_data["confidence"],
        "detail": f"File: {file.filename} | Ukuran: {len(image_bytes)//1024} KB | Azure: {'tersimpan' if file_url else 'gagal/tidak aktif'}",
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }

    save_to_db(record)

    return AnalysisResult(**record)


@app.get("/api/history", response_model=List[AnalysisResult])
def get_history():
    conn = get_db_connection()

    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT id, filename, file_url, status, diagnosis, confidence, detail, created_at
                FROM analyses
                ORDER BY created_at DESC
                LIMIT 50
            """)
            rows = cursor.fetchall()

        results = []

        for row in rows:
            if row.get("created_at"):
                row["created_at"] = row["created_at"].strftime("%Y-%m-%d %H:%M:%S")

            results.append(row)

        return results

    finally:
        conn.close()


@app.delete("/api/history/{record_id}")
def delete_record(record_id: str):
    conn = get_db_connection()

    try:
        with conn.cursor() as cursor:
            cursor.execute(
                "DELETE FROM analyses WHERE id = %s",
                (record_id,)
            )

        conn.commit()

        return {
            "deleted": record_id
        }

    finally:
        conn.close()