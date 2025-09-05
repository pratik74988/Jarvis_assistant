import spacy
import time
import chromadb
import json
import os
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

# ---------------- Setup ----------------
nlp = spacy.load("en_core_web_sm")
embedder = SentenceTransformer("all-MiniLM-L6-v2")

# Persistent ChromaDB
client = chromadb.PersistentClient(path="./jarvis_memory_db")
collection = client.get_or_create_collection("jarvis_long_term")
print("Created/using CHROMADB with persistent storage")

# ---------------- Short-Term Memory ----------------
MAX_TURNS = 6
HISTORY_FILE = "./jarvis_short_term_memory.json"

def load_history():
    """Load short-term memory from file"""
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, "r") as f:
                return json.load(f)
        except:
            return []
    return []

def save_history():
    """Save short-term memory to file"""
    try:
        with open(HISTORY_FILE, "w") as f:
            json.dump(history, f, indent=2)
    except Exception as e:
        print(f"Error saving history: {e}")

# Initialize history from file
history = load_history()

def add_to_history(role, content):
    history.append({"role": role, "content": content})
    if len(history) > MAX_TURNS * 2:
        history.pop(0)
    save_history()

def get_context():
    return history[-MAX_TURNS * 2:]

# ---------------- Extract Important Parts ----------------
def extract_important_parts(text, max_words=20):
    doc = nlp(text)
    keywords = set()

    for ent in doc.ents:
        keywords.add(ent.text)
    for token in doc:
        if token.pos_ in ("NOUN", "PROPN", "VERB"):
            keywords.add(token.text)

    short_text = " ".join(list(keywords)[:max_words])
    return short_text.strip()

# ---------------- Should Store ----------------
def should_store(text):
    text_lower = text.lower()
    if "remember" in text_lower or "note" in text_lower:
        return True
    doc = nlp(text)
    if len(list(doc.ents)) > 0:
        return True
    return False

# ---------------- Long-Term Memory Store ----------------
def store_long_term_memory(text, role="user"):
    if is_duplicate(text):
        print(f"[SKIP] Already stored: {text}")
        return

    embedding = embedder.encode([text])[0].tolist()
    collection.add(
        documents=[text],
        embeddings=[embedding],
        metadatas=[{
            "role": role,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        }],
        ids=[str(hash(text))]
    )
    print(f"[MEMORY STORED] {text}")

# ---------------- Check Duplicate ----------------
def is_duplicate(text):
    embedding = embedder.encode([text])[0].tolist()
    results = collection.query(query_embeddings=[embedding], n_results=1)

    if results["documents"] and results["documents"][0]:
        score = cosine_similarity([embedding], [results["embeddings"][0][0]])[0][0]
        return score > 0.90  # treat as duplicate if >90% similar
    return False

# ---------------- Recall Memory ----------------
def recall_long_term_memory(query, top_k=3):
    embedding = embedder.encode([query])[0].tolist()
    results = collection.query(query_embeddings=[embedding], n_results=top_k)
    return results["documents"]


#----------- should trigger screenshot mechanism or not ------------
def should_trigger_screen_mechanism( text: str) ->bool:
    text_lower = text.lower()

    screentshot_keywords = [
        "screenshot", "capture screen", "snap my screen", 
        "take my screen", "print screen", "need help with screen",
        "what am i seeing"
    ]
    if any (k in text_lower for k in screenshot_keywords):
        return True

    doc = nlp(text)
    if any(tok.lemma_ in ("screenshot", "help with screen")for tok in doc):
        return True
    
    return False
