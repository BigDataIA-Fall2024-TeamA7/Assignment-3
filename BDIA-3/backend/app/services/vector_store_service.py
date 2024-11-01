from llama_index import VectorStoreIndex, Document as LlamaDocument
from typing import List, Dict
import pickle

class VectorStoreService:
    def __init__(self):
        self.document_indices: Dict[str, VectorStoreIndex] = {}
        self.research_notes_indices: Dict[str, VectorStoreIndex] = {}

    async def create_document_index(self, document_id: str, content: str):
        """Create or update document index"""
        documents = [LlamaDocument(text=content)]
        self.document_indices[document_id] = VectorStoreIndex.from_documents(documents)

    async def create_research_notes_index(self, document_id: str, notes: List[str]):
        """Create or update research notes index"""
        documents = [LlamaDocument(text=note) for note in notes]
        self.research_notes_indices[document_id] = VectorStoreIndex.from_documents(documents)

    async def search_document(self, document_id: str, query: str, top_k: int = 5):
        """Search through document content"""
        if document_id not in self.document_indices:
            return []
        
        query_engine = self.document_indices[document_id].as_query_engine()
        response = query_engine.query(query)
        return response.source_nodes[:top_k]

    async def search_research_notes(self, document_id: str, query: str, top_k: int = 5):
        """Search through research notes"""
        if document_id not in self.research_notes_indices:
            return []
        
        query_engine = self.research_notes_indices[document_id].as_query_engine()
        response = query_engine.query(query)
        return response.source_nodes[:top_k]
    

    def save_indices(self, path: str):
        """Save indices to disk"""
        with open(path, 'wb') as f:
            pickle.dump({
                'documents': self.document_indices,
                'notes': self.research_notes_indices
            }, f)

    def load_indices(self, path: str):
        """Load indices from disk"""
        with open(path, 'rb') as f:
            indices = pickle.load(f)
            self.document_indices = indices['documents']
            self.research_notes_indices = indices['notes']

    async def chunk_document(self, content: str) -> List[Dict]:
        """Chunk document for efficient processing"""
        chunks = []
        current_chunk = ""
        current_size = 0
        
        for line in content.split('\n'):
            line_size = len(line.split())
            if current_size + line_size > self.chunk_size:
                chunks.append({
                "content": current_chunk,
                "size": current_size
            })
            current_chunk = line
            current_size = line_size
        else:
            current_chunk += f"\n{line}"
            current_size += line_size
            
        if current_chunk:
            chunks.append({
                "content": current_chunk,
                "size": current_size
            })
        
        return chunks

async def update_document_chunks(self, document_id: str, chunks: List[Dict]):
    """Update document chunks in cache"""
    self.document_chunks[document_id] = chunks
    await self.create_document_index(document_id, chunks)