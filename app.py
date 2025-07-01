# pip install streamlit easyocr opencv-python-headless

import streamlit as st
import easyocr
import tempfile
import re

st.title("📄 Pembaca Nilai dari Ijazah")

uploaded_file = st.file_uploader("Upload Foto/Scan Ijazah (format: PDF/DOCX)", type=["pdf", "docx])

if uploaded_file:
    with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
        tmp_file.write(uploaded_file.read())
        path = tmp_file.name

    # Proses OCR
    st.info("🔍 Sedang memproses teks dengan OCR...")
    reader = easyocr.Reader(['id'])
    result = reader.readtext(path, detail=0)

    st.subheader("📃 Teks Hasil OCR:")
    st.write(result)

    # Ekstrak nilai dari teks
    nilai_mapel = {}
    for line in result:
        match = re.search(r'(Matematika|Fisika|Kimia|Biologi|B\.?Indonesia|B\.?Inggris)[^\d]*([0-9]{2,3})', line, re.IGNORECASE)
        if match:
            mapel = match.group(1).replace("B.", "Bahasa ").strip()
            nilai = int(match.group(2))
            nilai_mapel[mapel] = nilai

    st.subheader("📘 Nilai yang Terdeteksi:")
    if nilai_mapel:
        st.json(nilai_mapel)
    else:
        st.warning("⚠️ Tidak ditemukan nilai yang valid. Pastikan gambar jelas dan format ijazah standar.")
