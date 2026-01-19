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
    procedimentos legais, reclamações, recursos, eleições, artigo.
    Recenseamento Eleitoral na Diáspora atraves do PortalConsular.
    O que e o recenseamento eleitoral na diáspora atraves do portal consular.
    Quem pode recensear-se.
    Como sei se estou recenseado.
    Ate quando posso inscrever-me.
    Como validar documentos emitidos fora de Cabo Verde.
    Onde faço a inscrição.
    Que documentos são necessários.
    Como são tratadas reclamações.
    Quanto custa o recenseamento.
    Como garanto a segurança dos meus dados.
    Quais são os principais benefícios do recenseamento via Portal Consular.
    É possível fazer recenseamento fora das embaixadas e consulados.
    Quem contactar em caso dúvidas.
    Como faço para acessar o Portal Consular.
    O que fazer se não encontrar meu registo na pesquisa.
    Preciso apresentar comprovativo de residência no estrangeiro.
    Posso reutilizar dados biometricos já recolhidos.
    O que fazer se não for possível recolher biometria por deficiência.
    Qual a diferença entre transferência e atualização de dados.   
    Posso fazer o recenseamento junto com o pedido de passaporte ou CNI.
    Quanto tempo demora para o recenseamento ser aprovado.
    Como proceder em caso de eliminação do pedido por falta de documentação.
    O que fazer se perder o comprovante (verbete) de inscrição.
    O que e a CRE (Comissão de Recenseamento Eleitoral) e qual sua função.
    Posso recensear-me se estiver temporariamente fora do país de residência.
    Existe atendimento presencial para dúvidas sobre o recenseamento online.
    Quais são os princípios do recenseamento.
    O que e necessário para transferir o recenseamento para outra localidade dentro
do mesmo país.
    O que acontece se eu tentar recensear-me em mais de um local.
    Como proceder em caso de mudança de nome (por casamento, por exemplo).
    O que e um pedido de atualização e quando devo utilizá-lo.
    Quem fiscaliza este processo.
    Como posso saber o consulado mais próximo de mim.
    O que fazer se meus dados estiverem errados.
    Posso votar online depois de recensear-me.
    O que e a BDRE.
    Quais países concentram mais eleitores cabo-verdianos.
    O recenseamento e obrigatório.
    O que acontece se eu não me recensear.
    Posso recensear-me se tiver dupla nacionalidade.
    Como funciona a atualização dos cadernos eleitorais.
    Posso alterar meu local de voto.
    Quem administra a Base de Dados do Recenseamento Eleitoral (BDRE).
    Posso recensear-me fora do prazo.
    Como funciona o recenseamento para cidadãos que vivem em áreas sem
consulado.
    O sistema envia notificações após a conclusão do recenseamento.
    Posso usar documento digital (ex.: versão eletrônica do CNI).
    É necessário apresentar foto recente para atualização.
    Como validar documentos emitidos fora de Cabo Verde.
    Como proceder se meu nome não aparece nos cadernos eleitorais mesmo após
recenseamento.
   Existe atendimento telefônico para dúvidas.
   Há suporte em outros idiomas alem do português.
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

 Se a informação não existir no contexto, responde apenas:
"Não existe informação disponível no contexto fornecido."

CONTEXTO:
{context}

PERGUNTA:
{question}
"""
