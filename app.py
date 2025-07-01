import streamlit as st
import easyocr
import tempfile
import re

st.title("📄 Ekstraksi Nilai Mata Pelajaran dari Ijazah")

uploaded_file = st.file_uploader("Upload Gambar Ijazah (JPG/PNG)", type=["jpg", "jpeg", "png"])

def extract_mapel_nilai(text_lines):
    hasil = []
    for line in text_lines:
        # Deteksi ada angka dan teks di satu baris (nilai dan nama mapel)
        match = re.findall(r'([A-Za-z\s\.]+)\s+([0-9]{2,3}[,.]?[0-9]{0,2})', line)
        for m in match:
            nama_mapel = m[0].strip().replace("  ", " ")
            nilai = m[1].replace(",", ".")
            try:
                hasil.append((nama_mapel, float(nilai)))
            except:
                continue
    return hasil

if uploaded_file:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp_file:
        tmp_file.write(uploaded_file.read())
        file_path = tmp_file.name

    st.image(file_path, caption="Ijazah yang Diupload", use_column_width=True)
    st.info("🔍 Sedang memproses dengan OCR...")

    reader = easyocr.Reader(['id'])
    result = reader.readtext(file_path, detail=0)
    
    st.subheader("📜 Hasil Teks OCR:")
    st.write(result)

    nilai_terekstrak = extract_mapel_nilai(result)

    if nilai_terekstrak:
        st.success("📘 Nilai Mata Pelajaran yang Ditemukan:")
        for nama, nilai in nilai_terekstrak:
            st.write(f"**{nama}** : {nilai}")
    else:
        st.warning("⚠️ Tidak ditemukan nilai mata pelajaran yang bisa dikenali.")
