from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from PyPDF2 import PdfReader
from utils.core import get_pdf_text, get_text_chunks, get_vector_store, get_conversational_chain
from langchain_community.embeddings import HuggingFaceBgeEmbeddings
from fastapi.responses import JSONResponse
import os
import shutil

router = APIRouter()

# Globals to store uploaded PDF vectorstore
vectorstore = None

@router.post("/upload_pdf/", tags=["PDF"])
async def upload_pdf(pdf: UploadFile = File(...)):
    global vectorstore

    if pdf.content_type != 'application/pdf':
        raise HTTPException(status_code=400, detail="Only PDFs are allowed")

    pdf_path = f"temp_{pdf.filename}"
    with open(pdf_path, "wb") as f:
        shutil.copyfileobj(pdf.file, f)

    try:
        text = get_pdf_text(pdf_path)
        chunks = get_text_chunks(text)

        embeddings = HuggingFaceBgeEmbeddings(model_name="BAAI/bge-small-en-v1.5")
        vectorstore = get_vector_store(chunks, embeddings)
    finally:
        os.remove(pdf_path)

    return {"message": "PDF processed and embeddings stored."}

@router.post("/ask_question/", tags=["QA"])
async def ask_question(question: str = Form(...)):
    global vectorstore
    print(f"Received question: {question}")

    if vectorstore is None:
        raise HTTPException(status_code=500, detail="Vector store not initialized. Upload PDF first.")

    try:
        # Limit documents to avoid token overload
        docs = vectorstore.similarity_search(question, k=3)
        print(f"Retrieved {len(docs)} relevant docs")

        # Combine and truncate for safety
        combined_docs = " ".join([doc.page_content for doc in docs])[:2500]

        chain = get_conversational_chain()
        response = chain.invoke({
            "input_documents": docs,
            "context": combined_docs,
            "question": question
        })

        # Support both string and dict output
        return {"answer": response['output_text'] if isinstance(response, dict) else response}

    except Exception as e:
        print(f"Error during question answering: {e}")
        return JSONResponse(status_code=500, content={"error": str(e)})
