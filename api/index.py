from fastapi import FastAPI, File, UploadFile, Form
from fastapi.responses import HTMLResponse
from starlette.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
import io
import os
import shutil

app = FastAPI()

# Load templates untuk HTML
templates = Jinja2Templates(directory="templates")

# Folder untuk menyimpan file yang diunggah
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.get("/", response_class=HTMLResponse)
async def home():
    with open("templates/index.html", "r") as f:
        return HTMLResponse(content=f.read())

@app.post("/upload/")
async def upload_file(file: UploadFile = File(...)):
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Load file ke dalam DataFrame
    if file.filename.endswith('.csv'):
        df = pd.read_csv(file_path)
    elif file.filename.endswith('.xlsx'):
        df = pd.read_excel(file_path)
    else:
        return {"error": "Format file tidak didukung. Gunakan CSV atau Excel."}

    # Analisis Data
    summary = df.describe().to_html()
    correlation_matrix = df.corr().to_html()
    
    # Simpan heatmap korelasi sebagai gambar
    plt.figure(figsize=(8, 6))
    sns.heatmap(df.corr(), annot=True, cmap='coolwarm', fmt='.2f')
    heatmap_path = os.path.join(UPLOAD_DIR, "heatmap.png")
    plt.savefig(heatmap_path)
    
    return templates.TemplateResponse("index.html", {
        "request": {},
        "summary": summary,
        "correlation_matrix": correlation_matrix,
        "heatmap": f"/static/heatmap.png"
    })
