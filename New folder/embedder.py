from sentence_transformers import SentenceTransformer

# You can use 'allenai-specter' for scientific papers if you have internet, or a smaller model for speed.
model = SentenceTransformer('all-MiniLM-L6-v2')

def embed_text(text):
    return model.encode([text])[0]

def chunk_text(text, chunk_size=500):
    # Simple chunking by words
    words = text.split()
    chunks = []
    for i in range(0, len(words), chunk_size):
        chunk = " ".join(words[i:i+chunk_size])
        chunks.append(chunk)
    return chunks