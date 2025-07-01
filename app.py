import streamlit as st
import easyocr
import tempfile
import numpy as np
import re
from pdf2image import convert_from_path
import os

st.title("📄 Ekstraksi Nilai dari Ijazah PDF/Gambar")

uploaded_file = st.file_uploader("Upload Ijazah (PDF/Gambar)", type=["pdf", "jpg", "png"])

reader = easyocr.Reader(['id'])

def extract_text_from_image(path):
    result = reader.readtext(path, detail=0)
    return "\n".join(result)

def extract_text_from_pdf(path):
    # Konversi semua halaman PDF ke gambar
    images = convert_from_path(path)
    text_result = []
    for page_img in images:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as temp_img_file:
            page_img.save(temp_img_file.name, "JPEG")
            ocr_result = extract_text_from_image(temp_img_file.name)
            text_result.append(ocr_result)
    return "\n".join(text_result)

if uploaded_file:
    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        tmp.write(uploaded_file.read())
        file_path = tmp.name

    st.info("🔍 Sedang memproses teks dengan OCR...")

    if uploaded_file.name.endswith(".pdf"):
        text = extract_text_from_pdf(file_path)
    else:
        text = extract_text_from_image(file_path)

    st.text_area("📄 Teks yang berhasil diekstrak:", text, height=300)

    # Ekstraksi nilai mapel
    nilai_mapel = {}
    for line in text.splitlines():
        match = re.search(r'(Matematika|Fisika|Kimia|Biologi|B\.?Indonesia|B\.?Inggris)[^0-9]*([0-9]{2,3})', line, re.IGNORECASE)
        if match:
            mapel = match.group(1).replace('.', '').strip()
            nilai = int(match.group(2))
            nilai_mapel[mapel] = nilai

    st.success(f"📘 Nilai berhasil diambil: {nilai_mapel}")
