# view_memory.py
import chromadb

# connect to Chroma with persistent storage
client = chromadb.PersistentClient(path="./jarvis_memory_db")
collection = client.get_collection("jarvis_long_term")
print("found collection")

def show_memory():
    data = collection.get(include=["documents", "metadatas"])
    if not data["documents"]:
        print("[EMPTY] No memory stored yet.")
        return
    
    for i, doc in enumerate(data["documents"]):
        print(f"\n[{i+1}] {doc}")
        print(f"   Meta: {data['metadatas'][i]}")

if __name__ == "__main__":
    show_memory()