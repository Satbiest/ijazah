# ekstraksi_nilai.py
import streamlit as st
import easyocr
import re
import tempfile

st.title("📄 Ekstraksi Nilai dan Nama dari Ijazah")

uploaded_file = st.file_uploader("Upload Gambar Ijazah (JPG/PNG)", type=["jpg", "jpeg", "png"])

def extract_info(text):
    result = {}

    # Ekstrak Nama
    nama_match = re.search(r'Nama\s+([A-Z_ ]+)', text)
    if nama_match:
        result['Nama'] = nama_match.group(1).replace('_', ' ').title()

    mapel_patterns = {
        'Matematika': r'Matematika.*?([0-9]{2}[,.]?[0-9]{0,2})',
        'Fisika': r'Fisika.*?([0-9]{2}[,.]?[0-9]{0,2})',
        'Kimia': r'Kimia.*?([0-9]{2}[,.]?[0-9]{0,2})',
        'Biologi': r'Biologi.*?([0-9]{2}[,.]?[0-9]{0,2})',
        'Bahasa Indonesia': r'Bahasa\s+Indonesia.*?([0-9]{2}[,.]?[0-9]{0,2})',
        'Bahasa Inggris': r'Bahasa\s+Inggris.*?([0-9]{2}[,.]?[0-9]{0,2})',
        'Bahasa Jawa': r'Bahasa\s+Jawa.*?([0-9]{2}[,.]?[0-9]{0,2})',
        'Bahasa Prancis': r'Prancis.*?([0-9]{2}[,.]?[0-9]{0,2})',
    }

    for mapel, pattern in mapel_patterns.items():
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            nilai = match.group(1).replace(',', '.')
            result[mapel] = float(nilai)

    return result

if uploaded_file:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp_file:
        tmp_file.write(uploaded_file.read())
        image_path = tmp_file.name

    st.image(image_path, caption="Ijazah Diupload", use_column_width=True)
    st.info("🔍 Memproses OCR...")

    reader = easyocr.Reader(['id'])
    ocr_result = reader.readtext(image_path, detail=0)
    full_text = " ".join(ocr_result)

    hasil = extract_info(full_text)

    if hasil:
        st.success("✅ Hasil Ekstraksi:")
        for k, v in hasil.items():
            st.write(f"**{k}** : {v}")
    else:
        st.warning("⚠️ Tidak dapat mengekstrak informasi yang valid dari gambar.")
