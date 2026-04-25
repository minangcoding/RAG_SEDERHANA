from flask import Flask, request, jsonify
import os
import requests
from groq import Groq
from pinecone import Pinecone

app = Flask(__name__)

# Inisialisasi API Keys dari Environment Variables Vercel
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
PINECONE_API_KEY = os.environ.get("PINECONE_API_KEY")
HF_TOKEN = os.environ.get("HF_TOKEN")
PINECONE_HOST = os.environ.get("PINECONE_HOST") # Contoh: my-index-1234.svc.pinecone.io

# Setup Clients
groq_client = Groq(api_key=GROQ_API_KEY)
pc = Pinecone(api_key=PINECONE_API_KEY)
index = pc.Index(host=PINECONE_HOST)

def get_embedding(text):
    # Menggunakan Hugging Face API agar ringan (tidak makan storage server)
    api_url = "https://api-inference.huggingface.co/pipeline/feature-extraction/sentence-transformers/all-MiniLM-L6-v2"
    headers = {"Authorization": f"Bearer {HF_TOKEN}"}
    response = requests.post(api_url, headers=headers, json={"inputs": text})
    return response.json()

@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.json
    user_query = data.get('query', '')
    
    if not user_query:
        return jsonify({"error": "Query kosong"}), 400

    try:
        # 1. Ubah pertanyaan user jadi Vector
        query_vector = get_embedding(user_query)

        # 2. Cari data yang mirip di Pinecone
        search_result = index.query(
            vector=query_vector,
            top_k=3,
            include_metadata=True
        )

        # 3. Kumpulkan teks konteks dari hasil pencarian
        contexts = [match['metadata']['text'] for match in search_result['matches']]
        context_text = "\n---\n".join(contexts)

        # 4. Kirim Konteks + Pertanyaan ke Groq (Llama 3)
        system_prompt = f"Anda adalah asisten cerdas. Jawab pertanyaan berdasarkan konteks berikut saja:\n\n{context_text}"
        
        chat_completion = groq_client.chat.completions.create(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_query}
            ],
            model="llama3-8b-8192",
            temperature=0.3,
        )

        answer = chat_completion.choices[0].message.content
        return jsonify({"answer": answer})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Vercel membutuhkan ini
if __name__ == '__main__':
    app.run(debug=True)