import streamlit as st
from transformers import DonutProcessor, VisionEncoderDecoderModel
from PIL import Image
import tempfile
import torch

st.title("📄 Ekstraksi Nilai Mata Pelajaran dari Ijazah - Donut OCR")

uploaded_file = st.file_uploader("Upload Gambar Ijazah (JPG/PNG)", type=["jpg", "jpeg", "png"])

@st.cache_resource
def load_donut_model():
    processor = DonutProcessor.from_pretrained("naver-clova-ix/donut-base-finetuned-docvqa")
    model = VisionEncoderDecoderModel.from_pretrained("naver-clova-ix/donut-base-finetuned-docvqa")
    model.eval()
    return processor, model

if uploaded_file:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp_file:
        tmp_file.write(uploaded_file.read())
        file_path = tmp_file.name

    st.image(file_path, caption="Ijazah yang Diupload", use_column_width=True)
    st.info("🔍 Sedang memproses gambar dengan Donut OCR...")

    image = Image.open(file_path).convert("RGB")

    processor, model = load_donut_model()
    task_prompt = "<s_docvqa><s_question>Daftar nilai mata pelajaran ijazah</s_question><s_answer>"
    inputs = processor(image, task_prompt, return_tensors="pt")

    with torch.no_grad():
        outputs = model.generate(**inputs, max_length=512, num_beams=2)

    output_text = processor.batch_decode(outputs, skip_special_tokens=True)[0]

    st.subheader("📘 Hasil Ekstraksi Nilai (Donut OCR):")
    st.write(output_text)
