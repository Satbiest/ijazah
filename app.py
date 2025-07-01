import streamlit as st
import easyocr
import tempfile
import re

st.title("📄 Ekstraksi Nilai Mata Pelajaran dari Ijazah")

uploaded_file = st.file_uploader("Upload Gambar Ijazah (JPG/PNG)", type=["jpg", "jpeg", "png"])

def extract_mapel_nilai(lines):
    hasil = []
    prev_text = ""

    for line in lines:
        # Ubah koma jadi titik agar mudah dibaca sebagai float
        clean_line = line.replace(",", ".")
        
        # Cari nilai (angka 2-3 digit, opsional dengan desimal)
        nilai_match = re.findall(r'\b([0-9]{2,3}(?:\.[0-9]{1,2})?)\b', clean_line)
        
        if nilai_match:
            for nilai in nilai_match:
                # Ambil teks sebelumnya sebagai nama mapel (jika masuk akal)
                nama_mapel = prev_text.strip()
                if nama_mapel and len(nama_mapel) >= 3 and not nama_mapel.isdigit():
                    hasil.append((nama_mapel, float(nilai)))
        else:
            # Simpan baris sebelumnya jika bukan nilai
            prev_text = clean_line

    return hasil

if uploaded_file:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp_file:
        tmp_file.write(uploaded_file.read())
        file_path = tmp_file.name

    st.image(file_path, caption="Ijazah yang Diupload", use_column_width=True)
    st.info("🔍 Sedang memproses gambar dengan OCR...")

    reader = easyocr.Reader(['id'])
    result = reader.readtext(file_path, detail=0)

    st.subheader("📜 Hasil Teks OCR (Mentah):")
    st.write(result)

    nilai_terekstrak = extract_mapel_nilai(result)

    if nilai_terekstrak:
        st.success("📘 Nilai Mata Pelajaran yang Terdeteksi:")
        for nama, nilai in nilai_terekstrak:
            st.write(f"{nama} : {nilai}")
    else:
        st.warning("⚠️ Tidak ditemukan nilai mata pelajaran yang bisa dikenali.")

