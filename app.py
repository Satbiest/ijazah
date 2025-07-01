import streamlit as st
import easyocr
import tempfile
import re

st.title("📄 Ekstraksi Otomatis Nilai dari Ijazah (Tanpa Pola Tetap)")

uploaded_file = st.file_uploader("Upload Gambar Ijazah (JPG/PNG)", type=["jpg", "jpeg", "png"])

if uploaded_file:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp_file:
        tmp_file.write(uploaded_file.read())
        image_path = tmp_file.name

    st.image(image_path, caption="Ijazah yang Diupload", use_column_width=True)
    st.info("🔍 Sedang memproses OCR...")

    reader = easyocr.Reader(['id'])
    result = reader.readtext(image_path, detail=0)
    full_text = " ".join(result)

    # Ekstrak nama siswa
    nama = ""
    nama_match = re.search(r'Nama\s*([A-Z_ ]{3,})', full_text)
    if nama_match:
        nama = nama_match.group(1).replace("_", " ").title()

    st.subheader("📘 Hasil Ekstraksi:")
    if nama:
        st.write(f"**Nama:** {nama}")

    # Ekstrak semua baris yang mirip "mapel nilai"
    st.write("**Daftar Nilai:**")

    nilai_dict = {}
    for line in result:
        line = line.strip()
        # Cari baris yang mengandung teks + angka
        match = re.search(r'([A-Za-z\s\.\-]+)[^\d]*([0-9]{2,4}[,.]?[0-9]{0,2})', line)
        if match:
            nama_mapel = match.group(1).strip().title()
            nilai = match.group(2).replace(',', '.')
            try:
                nilai = float(nilai)
                if 0 <= nilai <= 100:  # nilai wajar
                    nilai_dict[nama_mapel] = nilai
            except:
                pass

    if nilai_dict:
        for mapel, nilai in nilai_dict.items():
            st.write(f"**{mapel}** : {nilai}")
    else:
        st.warning("⚠️ Tidak ditemukan nilai yang valid.")
