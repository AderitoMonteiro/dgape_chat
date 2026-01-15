import os
from pypdf import PdfReader
from sentence_transformers import SentenceTransformer
import faiss

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
DOCS_PATH = os.path.join(BASE_DIR, "data", "legislacao")

model = SentenceTransformer("all-MiniLM-L6-v2")

def load_documents():
    texts = []
    print("A carregar documentos de:", DOCS_PATH)

    for file in os.listdir(DOCS_PATH):
        if file.endswith(".pdf"):
            reader = PdfReader(os.path.join(DOCS_PATH, file))
            print("Ficheiro:", file)
            text = ""
            for page in reader.pages:
                if page.extract_text():
                    text += page.extract_text() + "\n"
            texts.append(text)
    return texts

def split_text(text, size=800, overlap=100):
    chunks = []
    start = 0
    while start < len(text):
        end = start + size
        chunks.append(text[start:end])
        start = end - overlap
    return chunks

def build_index():
    documents = load_documents()
    chunks = []

    for doc in documents:
        chunks.extend(split_text(doc))

    embeddings = model.encode(chunks)
    index = faiss.IndexFlatL2(len(embeddings[0]))
    index.add(embeddings)

    return index, chunks

def search(question, index, chunks, k=4):
    q_emb = model.encode([question])
    _, idx = index.search(q_emb, k)
    return [chunks[i] for i in idx[0]]

def build_prompt(context, question):
    return f"""
Responde APENAS com base no contexto abaixo.
Indica o artigo ou norma quando possível.
Se não existir base legal, responde claramente que não existe.
Nao precise dizer que nao foi especificada no contexto.

CONTEXTO:
{context}

PERGUNTA:
{question}
"""
