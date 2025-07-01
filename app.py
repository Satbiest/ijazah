# Rekomendasi Jurusan WebApp: Minat + Upload Ijazah (LLM List of Jurusan Indonesia)
# Dependencies: pip install streamlit easyocr sentence-transformers faiss-cpu requests opencv-python-headless

import streamlit as st
import easyocr
import tempfile
import numpy as np
from sentence_transformers import SentenceTransformer
import faiss
import re
import cv2

st.title("🎓 Rekomendasi Jurusan Berdasarkan Minat dan Nilai Ijazah")

# --- 1. Input dari Pengguna ---
minat_user = st.text_area("Tulis minat, keahlian, atau hobi kamu:", "Saya suka menggambar dan komputer")

uploaded_file = st.file_uploader("Upload Foto/Scan Ijazah Anda (format: .pdf/.docx)", type=["pdf", "docx"])

# --- 2. Daftar Jurusan dari LLM (Disusun manual atau hasil dari model LLM yang sudah dimurnikan) ---
jurusan_list = [
    {"nama": "Teknik Informatika", "deskripsi": "Mempelajari pemrograman, pengembangan perangkat lunak, dan sistem komputer."},
    {"nama": "Sistem Informasi", "deskripsi": "Mengkaji pengelolaan informasi berbasis teknologi dan bisnis."},
    {"nama": "Teknik Elektro", "deskripsi": "Mempelajari prinsip listrik, elektronika, dan sistem kendali."},
    {"nama": "Teknik Mesin", "deskripsi": "Ilmu teknik yang fokus pada desain dan produksi mesin."},
    {"nama": "Teknik Sipil", "deskripsi": "Berhubungan dengan pembangunan infrastruktur seperti jalan, jembatan, dan gedung."},
    {"nama": "Kedokteran", "deskripsi": "Ilmu medis dan praktik pengobatan terhadap manusia."},
    {"nama": "Farmasi", "deskripsi": "Ilmu mengenai obat-obatan, pengolahannya, dan penggunaannya."},
    {"nama": "Keperawatan", "deskripsi": "Fokus pada pelayanan kesehatan dan perawatan pasien."},
    {"nama": "Psikologi", "deskripsi": "Ilmu tentang perilaku dan mental manusia."},
    {"nama": "Hukum", "deskripsi": "Mempelajari sistem hukum, peraturan, dan penerapannya di masyarakat."},
    {"nama": "Ilmu Komunikasi", "deskripsi": "Fokus pada penyampaian informasi dan media massa."},
    {"nama": "Manajemen", "deskripsi": "Ilmu pengelolaan organisasi, SDM, dan keuangan."},
    {"nama": "Akuntansi", "deskripsi": "Ilmu mencatat, mengelola, dan menganalisis transaksi keuangan."},
    {"nama": "Ekonomi Pembangunan", "deskripsi": "Mempelajari aspek ekonomi makro dan mikro dalam pembangunan."},
    {"nama": "Pendidikan Guru Sekolah Dasar", "deskripsi": "Mempersiapkan calon guru SD yang profesional."},
    {"nama": "Pendidikan Matematika", "deskripsi": "Mengajarkan dan memahami konsep matematika untuk pendidikan."},
    {"nama": "Sastra Indonesia", "deskripsi": "Ilmu bahasa dan kesusastraan Indonesia."},
    {"nama": "Sastra Inggris", "deskripsi": "Mempelajari bahasa, sastra, dan budaya Inggris."},
    {"nama": "Desain Komunikasi Visual", "deskripsi": "Fokus pada desain grafis, komunikasi visual, dan estetika."},
    {"nama": "Arsitektur", "deskripsi": "Perencanaan dan perancangan bangunan dan lingkungan binaan."},
    {"nama": "Agroteknologi", "deskripsi": "Ilmu pertanian modern, budidaya, dan teknologi pangan."},
    {"nama": "Peternakan", "deskripsi": "Fokus pada produksi, perawatan, dan manajemen hewan ternak."},
    {"nama": "Perikanan", "deskripsi": "Mempelajari pengelolaan sumber daya ikan dan kelautan."},
    {"nama": "Ilmu Gizi", "deskripsi": "Ilmu nutrisi dan hubungannya dengan kesehatan manusia."},
]

# --- 3. Load NLP Model & Proses Jurusan ke Vector ---
@st.cache_resource
def init_model():
    return SentenceTransformer('paraphrase-MiniLM-L6-v2')

model = init_model()

jurusan_vectors = []
valid_jurusan = []

for jurusan in jurusan_list:
    try:
        desc = jurusan['deskripsi'].strip()
        if len(desc) < 5:
            continue
        embed = model.encode(desc)
        embed = np.array(embed, dtype='float32')
        if embed.ndim == 1:
            jurusan_vectors.append(embed)
            valid_jurusan.append(jurusan)
    except Exception as e:
        continue

if jurusan_vectors:
    jurusan_vectors = np.vstack(jurusan_vectors).astype('float32')
    index = faiss.IndexFlatL2(jurusan_vectors.shape[1])
    index.add(jurusan_vectors)
else:
    st.error("Gagal memproses data jurusan. Tidak ada deskripsi yang valid.")
    st.stop()

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
    elif diff < 0:
        combined_vector = combined_vector[:, :jurusan_vectors.shape[1]]

    # Rekomendasi
    D, I = index.search(combined_vector, k=5)
    st.subheader("🎯 Rekomendasi Jurusan untuk Anda:")
    for i in I[0]:
        jurusan = valid_jurusan[i]
        st.markdown(f"**{jurusan['nama']}**  ")
        st.caption(jurusan['deskripsi'])
