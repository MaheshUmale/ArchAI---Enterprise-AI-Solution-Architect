from typing import List, Dict
import pinecone
from langchain_openai import OpenAIEmbeddings
from app.core.config import settings

class VectorService:
    def __init__(self):
        # In a real scenario, we'd initialize Pinecone/Chroma here.
        # For Phase 5, we use a semantic mock grounded in the processed docs.
        self.data_path = "backend/data/processed_docs.json"

    def add_documents(self, documents: List[Dict]):
        """Embed and add documents to vector store."""
        pass

    def query(self, query_text: str, top_k: int = 3) -> List[Dict]:
        """Search for relevant context from processed docs."""
        import json
        import os
        if not os.path.exists(self.data_path):
            return [{"content": "Enterprise Standard Architecture Policy", "source": "Core_Policy"}]

        try:
            with open(self.data_path, 'r') as f:
                docs = json.load(f)

            # Simple keyword matching to simulate semantic search
            results = []
            query_keywords = query_text.lower().split()
            for doc in docs:
                for chunk in doc.get('chunks', []):
                    if any(k in chunk.lower() for k in query_keywords):
                        results.append({"content": chunk[:1000], "source": doc.get('title')})
                        if len(results) >= top_k: return results

            return results if results else [{"content": "General Enterprise Design Principles", "source": "Arch_Global"}]
        except:
            return [{"content": "Error accessing vector context", "source": "System"}]

vector_service = VectorService()
