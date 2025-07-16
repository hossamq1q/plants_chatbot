import openai
from pathlib import Path
from dotenv import load_dotenv
import faiss
import time
import os
import numpy as np
import json
from typing import List, Dict, Any
from .prompt import system_prompt
import asyncio


env_path = Path("D:/Artificial intelligence/nlp/plants_chatpot/.env")
index_dir = Path("D:/Artificial intelligence/nlp/plants_chatpot/index")

index_path = index_dir / "index.faiss"
chunks_path = index_dir / "chunks.json"

load_dotenv(env_path)
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
openai.api_key = OPENAI_API_KEY
index = faiss.read_index(str(index_path))
with open(chunks_path, 'r') as f:
        chunks = json.load(f)

def get_embedding(text: str, model="text-embedding-3-small", max_retries: int = 3):
        for attempt in range(max_retries):
            try:
                text = text.replace("\n", " ")
                response = openai.embeddings.create(
                    input=[text],
                    model=model
                )
                return response.data[0].embedding
            except Exception as e:
                if attempt == max_retries - 1:
                    print(f"Final error getting embedding: {e}")
                    return None
                print(f"Error getting embedding (attempt {attempt + 1}): {e}")
                time.sleep(2 ** attempt)
                

def get_related_chunks(query: str, k: int = 5) -> List[Dict[str, Any]]:
        query_vector = get_embedding(query)
        if not query_vector:
            return []
            
        distances, indices = index.search(np.array([query_vector]).astype('float32'), k)
        
        results = []
        for i, idx in enumerate(indices[0]):
            if idx < len(chunks):
                results.append({
                    'chunk': chunks[idx],
                    'distance': float(distances[0][i])
                })
            
        return results   
    
async def get_response(query: str, k: int = 3, temperature: float = 0.7) -> str:
    relevant_chunks = await asyncio.to_thread(get_related_chunks, query, k)
    if not relevant_chunks:
        return "Sorry, I couldn't find relevant information."

    context = "\n\n".join([chunk['chunk'] for chunk in relevant_chunks])

    try:
        response = await asyncio.to_thread(
            openai.chat.completions.create,
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Context:\n{context}\n\nQuestion: {query}"}
            ],
            temperature=temperature,
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"Error getting response: {e}")
        return "Sorry, an error occurred while getting the answer. Please try again."                 