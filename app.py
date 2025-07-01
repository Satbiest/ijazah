import streamlit as st
import easyocr
import tempfile
import re

st.title("📄 Ekstraksi Nilai Mata Pelajaran dari Ijazah")

uploaded_file = st.file_uploader("Upload Gambar Ijazah (JPG/PNG)", type=["jpg", "jpeg", "png"])

def clean_text_list(text_lines):
    """Gabungkan teks OCR dan hilangkan baris kosong"""
    return [t.strip() for t in text_lines if t.strip() != ""]

def extract_mapel_nilai(text_lines):
    hasil = []
    gabungan = " ".join(text_lines)

    # Regex: teks + angka yang bisa berupa nilai
    pattern = r'([A-Za-z\s\/\.\-]{3,})\s*[:\-]?\s*([0-9]{2,3}[,.]?[0-9]{0,2})'
    matches = re.findall(pattern, gabungan)

    for mapel, nilai in matches:
        mapel = mapel.strip().replace("  ", " ")
        nilai = nilai.replace(",", ".").strip()
        try:
            float_nilai = float(nilai)
            if 10 <= float_nilai <= 100:  # nilai valid
                hasil.append((mapel.title(), float_nilai))
        except:
            continue

    return hasil

if uploaded_file:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp_file:
        tmp_file.write(uploaded_file.read())
        file_path = tmp_file.name

    st.image(file_path, caption="Ijazah yang Diupload", use_column_width=True)
    st.info("🔍 Memproses gambar dengan EasyOCR...")

    reader = easyocr.Reader(['id'], gpu=False)
    result = reader.readtext(file_path, detail=0)
    cleaned = clean_text_list(result)

    nilai_terekstrak = extract_mapel_nilai(cleaned)

    st.subheader("📘 Nilai Mata Pelajaran:")
    if nilai_terekstrak:
        for nama, nilai in nilai_terekstrak:
            st.write(f"**{nama}** : {nilai}")
    else:
        st.warning("⚠️ Tidak ditemukan nilai mata pelajaran yang valid.")
