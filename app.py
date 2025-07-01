# Rekomendasi Jurusan WebApp: Minat + Upload Ijazah (Scrape Semua PDDikti)
# Dependencies: pip install streamlit easyocr sentence-transformers faiss-cpu requests beautifulsoup4 opencv-python-headless

import streamlit as st
import easyocr
import tempfile
import numpy as np
import requests
from bs4 import BeautifulSoup
from sentence_transformers import SentenceTransformer
import faiss
import re
import cv2

st.title("🎓 Rekomendasi Jurusan Berdasarkan Minat dan Nilai Ijazah")

# --- 1. Input dari Pengguna ---
minat_user = st.text_area("Tulis minat, keahlian, atau hobi kamu:", "Saya suka menggambar dan komputer")

uploaded_file = st.file_uploader("Upload Foto/Scan Ijazah Anda (format: .jpg/.png)", type=["jpg", "png"])

# --- 2. Ambil Semua Data Jurusan dari PDDikti (Scrape Per Halaman) ---
@st.cache_data(ttl=86400)
def scrape_jurusan_all():
    base_url = "https://pddikti.kemdiktisaintek.go.id/program-studi?page="
    all_data = []

    for page in range(1, 1000):  # batas aman hingga 1000 halaman
        url = f"{base_url}{page}"
        r = requests.get(url)
        soup = BeautifulSoup(r.text, "html.parser")
        items = soup.find_all("div", class_="card-body")

        if not items:
            break

        for card in items:
            title = card.find("h5")
            if title:
                nama_jurusan = title.text.strip()
                desc = card.find("p").text.strip() if card.find("p") else "Deskripsi tidak tersedia"
                all_data.append({"nama": nama_jurusan, "deskripsi": desc})

    return all_data

jurusan_list = scrape_jurusan_all()

# --- 3. Load NLP Model & Proses Jurusan ke Vector ---
@st.cache_resource
def init_model():
    return SentenceTransformer('paraphrase-MiniLM-L6-v2')

model = init_model()

jurusan_vectors = []
for jurusan in jurusan_list:
    embed = model.encode(jurusan['deskripsi'])
    jurusan_vectors.append(embed)

jurusan_vectors = np.vstack(jurusan_vectors).astype('float32')
index = faiss.IndexFlatL2(jurusan_vectors.shape[1])
index.add(jurusan_vectors)

# --- 4. Proses Input Siswa dan Rekomendasi ---
if uploaded_file:
    with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
        tmp_file.write(uploaded_file.read())
        path = tmp_file.name

    # OCR nilai
    st.info("🔍 Membaca nilai dari ijazah...")
    reader = easyocr.Reader(['id'])
    result = reader.readtext(path, detail=0)
    nilai_mapel = {}
    for line in result:
        match = re.search(r'(Matematika|Fisika|Kimia|Biologi|B.Indonesia|B.Inggris)[^0-9]*([0-9]{2,3})', line, re.IGNORECASE)
        if match:
            mapel = match.group(1).strip()
            nilai = int(match.group(2))
            nilai_mapel[mapel] = nilai

    st.success(f"📘 Nilai berhasil diambil: {nilai_mapel}")

    # Vektorisasi
    nilai_vector = np.array([nilai_mapel.get(m, 0) for m in ["Matematika", "Fisika", "Kimia"]], dtype=np.float32)
    minat_vector = model.encode(minat_user)
    combined_vector = np.concatenate((nilai_vector, minat_vector)).astype('float32').reshape(1, -1)

    # Padding agar dimensi cocok
    diff = jurusan_vectors.shape[1] - combined_vector.shape[1]
    if diff > 0:
        combined_vector = np.pad(combined_vector, ((0, 0), (0, diff)), mode='constant')

    # Rekomendasi
    D, I = index.search(combined_vector, k=5)
    st.subheader("🎯 Rekomendasi Jurusan untuk Anda:")
    for i in I[0]:
        jurusan = jurusan_list[i]
        st.markdown(f"**{jurusan['nama']}**  ")
        st.caption(jurusan['deskripsi'])

