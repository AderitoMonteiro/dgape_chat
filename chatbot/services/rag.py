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

def normalize_question(question):
    return f"""
    Pergunta jurídica eleitoral:
    {question}
    Contexto: legislação eleitoral, prazos, direitos do eleitor,
    procedimentos legais, reclamações, recursos, eleições, artigo. voto antecipado,como proceder em caso de querer voto antecipado,
    locais de votação, documentos necessários. como votar, elegibilidade, candidaturas,
    financiamento de campanhas, conduta eleitoral, fiscalização, apuração de votos,
    como contestar resultados eleitorais. como denunciar irregularidades eleitorais.
    como obter informações sobre eleições. como participar como voluntário em campanhas eleitorais.
    como acompanhar notícias sobre eleições,como entender o sistema eleitoral,como funciona o processo eleitoral,
    como são organizadas as eleições,quais são os tipos de eleições,quais são os órgãos eleitorais,
    quais são os direitos e deveres dos eleitores,quais são as penalidades por infrações eleitorais,
    quais são os prazos para cada etapa do processo eleitoral,como funcionam as urnas, como é feita a apuração dos votos,
    .
 """


def search(question, index, chunks, k=4):
    # 🔹 normalizar/enriquecer a pergunta
    normalized_question = normalize_question(question)

    # 🔹 criar embedding da pergunta enriquecida
    q_emb = model.encode([normalized_question], normalize_embeddings=True)

    # 🔹 procurar no índice vetorial
    _, idx = index.search(q_emb, k)

    return [chunks[i] for i in idx[0]]


def build_prompt(context, question):
    return f"""
            Responde APENAS com base no contexto abaixo.
            
            REGRAS OBRIGATÓRIAS:
            - NÃO menciones artigos, números, FAQs, leis, normas ou referências.
            - NÃO cites fontes entre parênteses.
            - NÃO uses expressões como "artigo X", "FAQ Y", "segundo a lei".
            - Responde apenas de forma clara, direta e explicativa.
            - Se a informação não existir no contexto, responde apenas:
            - Não existe informação disponível no contexto fornecido."


CONTEXTO:
{context}

PERGUNTA:
{question}
"""
