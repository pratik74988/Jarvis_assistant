import spacy
import time 
import chromadb
from sentence_transformers import SentenceTransformer

nlp = spacy.load("en_core_web_sm")
embedder = SentenceTransformer("all-MiniLM-L6-v2")

client = chromadb.Client()
collection = client.create_collection("jarvis_long_term") 

#------Short Term Memmory--------
MAX_TURNS = 6
history = []

def add_to_history (role, content):
    history.append({"role": role, "content": content})
    if len(history)>MAX_TURNS*2:
        history.pop(0)
def get_context ():
    return history[-MAX_TURNS*2:]

def extract_important_parts(text, max_words = 20):
    doc = nlp(text)
    keywords = set()

    for ent in doc.ents:
        keywords.add(ent.text)
    for token in doc:
        if token.pos_ in ("NOUN", "PROPN", "VERB"):
            keywords.add(token.text)
    
    short_text = " ".join(list(keywords)[:max_words])
    return short_text.strip()

#-------- IMPORTANCE CHECKER ------------
def should_store(text):
    text_lower = text.lower()
    if "remember" in text_lower or "note" in text_lower:
        return True
    doc = nlp(text)
    if len(list(doc.ents)) > 0:
        return True
    return False


#--------------Vector DB store-------------

def store_long_term_memory(text, role="user"):
    
    if is_duplicate(text):
        print(f"[SKIP] Already stored: {text}")
        return

    embedding = embedder.encode()
    collection.add(
        documents=[text],
        embeddings=[embedding],
        metadatas=[{
            "role": role,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        }],
        ids = [str(hash(text))] # Unique ID based on text
    )
    print(f"[MEMORY STORED] {text}")

#checking if memory already exists
def is_duplicate(text):
    embedding = embedder.encode([text])[0].tolist()
    results = collection.query(
        query_embeddings=[embedding],
        n_results=1
    )
    if results["documents"] and results["documents"][0]:
        # Check similarity manually
        from sklearn.metrics.pairwise import cosine_similarity
        score = cosine_similarity(
            [embedding],
            [results["embeddings"][0][0]]
        )[0][0]
        return score > 0.90  # 90% similar → treat as duplicate
    return False

def recall_long_term_memory(query, top_k=3):
    embedding = embedder.encode([query])[0].tolist()
    results = collection.query(
        query_embeddings=[embedding],
        n_results=top_k
    )
    return results["documents"]