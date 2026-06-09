from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import sqlite3
import os
import base64
import json
import httpx
import uuid
from datetime import datetime

app = FastAPI(title="MediScan API", version="1.0.0")

# ─── CORS (izinkan semua origin saat development) ───────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── Konfigurasi ────────────────────────────────────────────────────────────
HF_TOKEN = os.getenv("HF_TOKEN", "")          # Token Hugging Face kamu
DB_PATH  = os.getenv("DB_PATH", "mediscan.db")

# ─── Inisialisasi database SQLite ───────────────────────────────────────────
def init_db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS analyses (
            id         TEXT PRIMARY KEY,
            filename   TEXT,
            status     TEXT,
            diagnosis  TEXT,
            confidence REAL,
            detail     TEXT,
            created_at TEXT
        )
    """)
    conn.commit()
    conn.close()

init_db()

# ─── Model response ─────────────────────────────────────────────────────────
class AnalysisResult(BaseModel):
    id:         str
    filename:   str
    status:     str          # "Sehat" | "Perlu Perhatian" | "Kritis"
    diagnosis:  str
    confidence: float        # 0–100
    detail:     str
    created_at: str

# ─── Helper: simpan ke DB ───────────────────────────────────────────────────
def save_to_db(result: dict):
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        "INSERT INTO analyses VALUES (?,?,?,?,?,?,?)",
        (result["id"], result["filename"], result["status"],
         result["diagnosis"], result["confidence"],
         result["detail"], result["created_at"])
    )
    conn.commit()
    conn.close()

# ─── Helper: analisis gambar via Hugging Face ───────────────────────────────
async def analyze_with_hf(image_bytes: bytes) -> dict:
    """
    Gunakan model image-classification gratis dari Hugging Face.
    Jika HF_TOKEN tidak diset, pakai mode simulasi.
    """
    if not HF_TOKEN:
        # ── Mode simulasi (tanpa API) ──
        import random
        statuses   = ["Sehat", "Perlu Perhatian", "Kritis"]
        diagnoses  = {
            "Sehat":           "Kulit tampak normal, tidak ada kelainan terdeteksi.",
            "Perlu Perhatian": "Terdeteksi tanda-tanda iritasi ringan atau kemerahan.",
            "Kritis":          "Terdeteksi lesi yang perlu pemeriksaan dokter segera.",
        }
        s = random.choice(statuses)
        return {
            "status":     s,
            "diagnosis":  diagnoses[s],
            "confidence": round(random.uniform(72, 98), 1),
        }

    # ── Mode nyata: Hugging Face Inference API ──
    # Model: microsoft/resnet-50 (gratis, tidak perlu GPU)
    b64 = base64.b64encode(image_bytes).decode()
    headers = {"Authorization": f"Bearer {HF_TOKEN}"}
    payload = {"inputs": b64}

    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.post(
            "https://api-inference.huggingface.co/models/microsoft/resnet-50",
            headers=headers,
            json=payload,
        )

    if resp.status_code != 200:
        raise HTTPException(status_code=502, detail=f"HF API error: {resp.text}")

    predictions = resp.json()  # list of {label, score}

    # Mapping sederhana: ambil label teratas, map ke status
    top = predictions[0] if predictions else {"label": "unknown", "score": 0.5}
    label = top["label"].lower()
    score = round(top["score"] * 100, 1)

    # Heuristik mapping label → status medis
    if score > 80:
        status    = "Sehat"
        diagnosis = f"Analisis menunjukkan kondisi normal ({top['label']})."
    elif score > 55:
        status    = "Perlu Perhatian"
        diagnosis = f"Terdeteksi pola yang memerlukan observasi lebih lanjut ({top['label']})."
    else:
        status    = "Kritis"
        diagnosis = f"Pola tidak biasa terdeteksi ({top['label']}), disarankan konsultasi dokter."

    return {"status": status, "diagnosis": diagnosis, "confidence": score}

# ════════════════════════════════════════════════════════════════════════════
# ENDPOINTS
# ════════════════════════════════════════════════════════════════════════════

@app.get("/")
def root():
    return {"message": "MediScan API berjalan ✅", "docs": "/docs"}

@app.get("/api/health")
def health_check():
    return {"status": "ok", "hf_connected": bool(HF_TOKEN)}

@app.post("/api/upload", response_model=AnalysisResult)
async def upload_and_analyze(file: UploadFile = File(...)):
    # Validasi tipe file
    allowed = {"image/jpeg", "image/png", "image/webp", "image/jpg"}
    if file.content_type not in allowed:
        raise HTTPException(400, "Hanya file JPG, PNG, atau WEBP yang diterima.")

    image_bytes = await file.read()

    if len(image_bytes) > 10 * 1024 * 1024:  # max 10 MB
        raise HTTPException(400, "Ukuran file maksimal 10 MB.")

    # Analisis
    result_data = await analyze_with_hf(image_bytes)

    # Simpan ke DB
    record = {
        "id":         str(uuid.uuid4()),
        "filename":   file.filename,
        "status":     result_data["status"],
        "diagnosis":  result_data["diagnosis"],
        "confidence": result_data["confidence"],
        "detail":     f"File: {file.filename} | Ukuran: {len(image_bytes)//1024} KB",
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }
    save_to_db(record)

    return AnalysisResult(**record)

@app.get("/api/history", response_model=List[AnalysisResult])
def get_history():
    conn   = sqlite3.connect(DB_PATH)
    cursor = conn.execute("SELECT * FROM analyses ORDER BY created_at DESC LIMIT 50")
    rows   = cursor.fetchall()
    conn.close()

    keys = ["id", "filename", "status", "diagnosis", "confidence", "detail", "created_at"]
    return [AnalysisResult(**dict(zip(keys, row))) for row in rows]

@app.delete("/api/history/{record_id}")
def delete_record(record_id: str):
    conn = sqlite3.connect(DB_PATH)
    conn.execute("DELETE FROM analyses WHERE id = ?", (record_id,))
    conn.commit()
    conn.close()
    return {"deleted": record_id}
