import easyocr
import fitz  # pip install pymupdf
import docx2txt
from PIL import Image
import numpy as np
import re
import tempfile
import streamlit as st

reader = easyocr.Reader(['id'])

uploaded_file = st.file_uploader("Upload Ijazah (pdf, docx, jpg, png)", type=["pdf", "docx", "jpg", "png"])

def extract_text_from_image(path):
    result = reader.readtext(path, detail=0)
    return "\n".join(result)

def extract_text_from_pdf(path):
    doc = fitz.open(path)
    text_result = []
    for page in doc:
        text_result.append(page.get_text())
    return "\n".join(text_result)

def extract_text_from_docx(path):
    return docx2txt.process(path)

if uploaded_file:
    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        tmp.write(uploaded_file.read())
        file_path = tmp.name

    st.info("🔍 Sedang memproses teks dengan OCR...")

    if uploaded_file.name.endswith(".jpg") or uploaded_file.name.endswith(".png"):
        text = extract_text_from_image(file_path)
    elif uploaded_file.name.endswith(".pdf"):
        text = extract_text_from_pdf(file_path)
    elif uploaded_file.name.endswith(".docx"):
        text = extract_text_from_docx(file_path)
    else:
        st.error("Format file tidak didukung.")
        st.stop()

    st.text_area("📄 Teks yang berhasil diekstrak:", text, height=300)

    # Ekstrak nilai (Matematika, Fisika, dll)
    nilai_mapel = {}
    for line in text.splitlines():
        match = re.search(r'(Matematika|Fisika|Kimia|Biologi|B\.?Indonesia|B\.?Inggris)[^0-9]*([0-9]{2,3})', line, re.IGNORECASE)
        if match:
            mapel = match.group(1).replace('.', '').strip()
            nilai = int(match.group(2))
            nilai_mapel[mapel] = nilai

    st.success(f"📘 Nilai berhasil diambil: {nilai_mapel}")
