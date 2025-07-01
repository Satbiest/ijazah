import streamlit as st
import easyocr
import tempfile
import re

st.title("📄 Ekstraksi Nilai Mata Pelajaran dari Ijazah")

uploaded_file = st.file_uploader("Upload Gambar Ijazah (JPG/PNG)", type=["jpg", "jpeg", "png"])

# Cleaning text OCR
def clean_text_list(text_lines):
    return [t.strip() for t in text_lines if t.strip() != ""]

# Ekstraksi mapel dan nilai (tanpa keyword)
def extract_mapel_nilai(text_lines):
    hasil = []
    gabungan = " ".join(text_lines)

    # Pola: nama mapel lalu nilai
    pattern = r'([A-Za-z\s\/\.\-]+?)\s*[:\-]?\s*([0-9]{2,3}[,.]?[0-9]{0,2})'
    matches = re.findall(pattern, gabungan)

    for mapel, nilai in matches:
        # Bersihkan mapel
        mapel = re.sub(r"^[\.\d\s]+", "", mapel)  # Hapus titik/angka di awal
        mapel = re.sub(r"[^A-Za-z\s]", "", mapel)  # Hapus simbol aneh
        mapel = mapel.strip().title()

        # Filter jika bukan mapel (mengandung kata noise)
        if any(k in mapel.lower() for k in ["rata", "tahun", "nama", "tempat", "lahir", "nip", "mei", "induk"]):
            continue

        # Konversi nilai
        nilai = nilai.replace(",", ".")
        try:
            nilai_float = float(nilai)
            if 10 <= nilai_float <= 100:  # Hanya nilai masuk akal
                hasil.append((mapel, nilai_float))
        except:
            continue

    return hasil

# Main
if uploaded_file:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp_file:
        tmp_file.write(uploaded_file.read())
        file_path = tmp_file.name

    st.image(file_path, caption="Ijazah yang Diupload", use_column_width=True)
    st.info("🔍 Sedang memproses gambar dengan OCR...")

    reader = easyocr.Reader(['id'], gpu=False)
    result = reader.readtext(file_path, detail=0)
    cleaned = clean_text_list(result)

    nilai_terekstrak = extract_mapel_nilai(cleaned)

    st.subheader("📘 Nilai Mata Pelajaran Dikenali:")
    if nilai_terekstrak:
        for nama, nilai in nilai_terekstrak:
            st.write(f"**{nama}** : {nilai}")
    else:
        st.warning("⚠️ Tidak ditemukan nilai mata pelajaran yang valid.")
