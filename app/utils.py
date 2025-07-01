import os
import fitz  # PyMuPDF to help extract text from pdf file
from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS
from sentence_transformers import SentenceTransformer
import faiss

# Load all PDF text extracting the text from the pdf for further process
def load_notes_from_folder(folder_path):
    texts = []
    for filename in os.listdir(folder_path):
        if filename.endswith(".pdf"):
            with fitz.open(os.path.join(folder_path, filename)) as doc:
                text = ""
                for page in doc:
                    text += page.get_text()
                texts.append(text)
    return texts

# Break text into chunks for easy embedding converson
def split_text(text, chunk_size=300):
    words = text.split()
    chunks = []
    for i in range(0, len(words), chunk_size):
        chunk = " ".join(words[i:i + chunk_size])
        chunks.append(chunk)
    return chunks

# Convert chunks to vector embeddings for similarity camparison
def embed_chunks(chunks):
    model = SentenceTransformer("all-MiniLM-L6-v2")
    embeddings = model.encode(chunks, show_progress_bar=True)
    return embeddings, model

# Create FAISS index to help compare embeddings
def create_faiss_index(embeddings):
    dimension = embeddings.shape[1]
    index = faiss.IndexFlatL2(dimension)
    index.add(embeddings)
    return index

#  Search for best matching chunks
def get_top_chunks(query, model, index, chunks, top_k=3):
    query_embedding = model.encode([query])
    distances, indices = index.search(query_embedding, top_k)
    top_chunks = [chunks[i] for i in indices[0]]
    return top_chunks
