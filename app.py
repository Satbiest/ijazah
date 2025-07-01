# app.py
import streamlit as st
import easyocr
import tempfile
import re

st.set_page_config(page_title="Ekstraksi Nilai Ijazah", layout="centered")
st.title("📄 Ekstraksi Nama dan Nilai dari Ijazah")

uploaded_file = st.file_uploader("Upload Gambar Ijazah (JPG/PNG)", type=["jpg", "jpeg", "png"])

if uploaded_file:
    # Simpan file sementara
    with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp_file:
        tmp_file.write(uploaded_file.read())
        image_path = tmp_file.name

    st.image(image_path, caption="Ijazah yang Diupload", use_column_width=True)
    st.info("🔍 Sedang memproses gambar dengan OCR...")

    # Jalankan EasyOCR
    reader = easyocr.Reader(['id'])
    result = reader.readtext(image_path, detail=0)
    text_lines = [line.strip() for line in result if line.strip()]
    full_text = " ".join(text_lines)

    # --- Ekstraksi Nama ---
    nama_match = re.search(r'Nama[:\s]+([A-Z\s_]{3,})', full_text, re.IGNORECASE)
    if nama_match:
        nama = nama_match.group(1).replace("_", " ").title()
        st.success(f"👤 Nama: **{nama}**")
    else:
        st.warning("⚠️ Nama tidak ditemukan.")

    # --- Ekstraksi Nilai Pelajaran ---
    st.markdown("### 📘 Daftar Nilai")
    nilai_dict = {}

    for line in text_lines:
        if re.search(r'[A-Za-z]', line) and re.search(r'\d', line):
            match = re.search(r'([A-Za-z\s\.\-]{3,})[^0-9]*([0-9]{2,5}[,.]?[0-9]{0,2})', line)
            if match:
                mapel = match.group(1).strip().title()
                nilai_raw = match.group(2).replace(",", ".")

                try:
                    nilai_float = float(nilai_raw)
                    # Koreksi nilai besar seperti 8129 -> 81.29
                    if nilai_float > 100 and len(str(int(nilai_float))) >= 4:
                        nilai_float = float(str(int(nilai_float))[:2] + "." + str(int(nilai_float))[2:])

                    if 0 <= nilai_float <= 100:
                        nilai_dict[mapel] = round(nilai_float, 2)
                except:
                    continue

    if nilai_dict:
        for k, v in nilai_dict.items():
            st.write(f"**{k}** : {v}")
    else:
        st.warning("❌ Tidak ditemukan nilai pelajaran yang valid.")
