# app.py
import streamlit as st
import easyocr
import re
import tempfile

st.title("📄 Ekstraksi Nilai Ijazah (Gambar)")

uploaded_file = st.file_uploader("Upload Gambar Ijazah (JPG/PNG)", type=["jpg", "jpeg", "png"])

if uploaded_file:
    # Simpan gambar sementara
    with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp_file:
        tmp_file.write(uploaded_file.read())
        image_path = tmp_file.name

    st.image(image_path, caption="Ijazah yang Diupload", use_column_width=True)
    st.info("🔍 Sedang memproses teks dengan OCR...")

    # Proses OCR
    reader = easyocr.Reader(['id'])
    result = reader.readtext(image_path, detail=0)
    
    # Tampilkan hasil teks
    st.subheader("📝 Teks yang berhasil diekstrak:")
    st.write("\n".join(result))

    # Ekstrak nilai pelajaran
    nilai_mapel = {}
    for line in result:
        match = re.search(r'(Matematika|Fisika|Kimia|Biologi|B\.?Indonesia|B\.?Inggris)[^0-9]*([0-9]{2,3})', line, re.IGNORECASE)
        if match:
            mapel = match.group(1).replace(".", "").strip()
            nilai = int(match.group(2))
            nilai_mapel[mapel] = nilai

    st.success(f"📘 Nilai berhasil diambil: {nilai_mapel}")
