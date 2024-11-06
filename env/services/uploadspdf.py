from fastapi import  HTTPException
from pathlib import Path
import shutil
import datetime
import fitz  # PyMuPDF
from llama_index.core import SimpleDirectoryReader, VectorStoreIndex

data_directory = Path("uploads")
index_directory = Path("index")
data_directory.mkdir(exist_ok=True)
index_directory.mkdir(exist_ok=True)


def uploadfile(file):
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Only PDF files are allowed.")
    
    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    filename = f"{timestamp}_{file.filename}"
    file_path = data_directory / filename

    with file_path.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    extracted_text = extract_text_from_pdf(file_path)
    index_file_path = index_directory / filename
    index_text_with_llamaindex(extracted_text, index_file_path)

    return {"message": "PDF uploaded and indexed successfully", "filename": filename, "index_path": str(index_file_path)}


def extract_text_from_pdf(pdf_path):
    extracted_text = ""
    with fitz.open(pdf_path) as pdf:
        for page_num in range(pdf.page_count):
            page = pdf[page_num]
            extracted_text += page.get_text()
    return extracted_text

def index_text_with_llamaindex(text, output_path):
    temp_text_file = index_directory / "temp_text.txt"
    with temp_text_file.open("w", encoding='utf-8') as f:
        f.write(text)
    
    documents = SimpleDirectoryReader(input_files=[str(temp_text_file)]).load_data()
    index = VectorStoreIndex.from_documents(documents)
    index.storage_context.persist(persist_dir=str(output_path))
    
    temp_text_file.unlink()