# meme_fns/components.py

from meme_fns.intent_classifier import classify_intent
from meme_fns.smart_meme_rag_manager import SmartMemeRAGManager, MemeSelector
from meme_fns.memes_list import meme_examples

from sentence_transformers import SentenceTransformer
import faiss
import numpy as np

class Embedder:
    def __init__(self):
        self.model = SentenceTransformer('all-MiniLM-L6-v2')

    def embed(self, text: str) -> np.ndarray:
        return self.model.encode([text])[0]

class Retriever:
    def __init__(self):
        self.memes = []  # Store memes directly
        self.embeddings = []
        self.embedder = None

    def add_documents(self, memes: list, embedder: Embedder):
        self.memes = memes
        self.embedder = embedder
        self.embeddings = [embedder.embed(m['caption']) for m in memes]

    def retrieve(self, query_vec: np.ndarray, top_k=10) -> list:
        if not self.embeddings:
            return []
        
        # Compute simple L2 distance manually
        distances = []
        for idx, emb in enumerate(self.embeddings):
            dist = np.linalg.norm(emb - query_vec)
            distances.append((dist, idx))
        
        # Sort by distance (smallest first)
        distances.sort(key=lambda x: x[0])
        top_indices = [idx for _, idx in distances[:top_k]]
        return [self.memes[idx] for idx in top_indices]

def get_default_embedder():
    return Embedder()

def get_default_retriever():
    return Retriever()

def get_default_selector(retriever):
    return MemeSelector(strategy="weighted", retriever=retriever)

def get_rag_manager():
    emb = get_default_embedder()
    ret = get_default_retriever()
    sel = get_default_selector(ret)
    ret.add_documents(meme_examples, emb)
    return SmartMemeRAGManager(emb, ret, sel)
