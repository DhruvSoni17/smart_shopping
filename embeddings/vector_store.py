import numpy as np
from embeddings.embedding_model import EmbeddingModel
from database.db_manager import DatabaseManager

class VectorStore:
    """
    Store and retrieve vector embeddings for semantic search.
    """
    
    def __init__(self):
        """Initialize the vector store."""
        self.db = DatabaseManager()
        self.embedding_model = EmbeddingModel()
    
    def store_embedding(self, entity_type, entity_id, vector):
        """
        Store an embedding vector for an entity.
        
        Args:
            entity_type: Type of entity ('customer' or 'product')
            entity_id: ID of the entity
            vector: Embedding vector
            
        Returns:
            Embedding ID
        """
        # Serialize the vector for storage
        serialized_vector = self.embedding_model.serialize_embedding(vector)
        
        # Store in database
        embedding_id = self.db.store_embedding(entity_type, entity_id, serialized_vector)
        
        return embedding_id
    
    def get_embedding(self, embedding_id):
        """
        Get an embedding by ID.
        
        Args:
            embedding_id: ID of the embedding
            
        Returns:
            Embedding vector or None if not found
        """
        embedding_data = self.db.get_embedding(embedding_id)
        
        if embedding_data:
            serialized_vector = embedding_data.get('vector')
            return self.embedding_model.deserialize_embedding(serialized_vector)
        
        return None
    
    def search_similar_entities(self, query_vector, entity_type, limit=10, threshold=0.7):
        """
        Search for entities similar to the query vector.
        
        Args:
            query_vector: Query embedding vector
            entity_type: Type of entity to search for ('customer' or 'product')
            limit: Maximum number of results to return
            threshold: Minimum similarity score threshold
            
        Returns:
            List of (entity_id, similarity_score) tuples
        """
        # In a real system, this would use approximate nearest neighbor search
        # For the hackathon, we'll use a simple linear search
        
        query = "SELECT id, entity_id, vector FROM embeddings WHERE entity_type = ?"
        results = self.db.execute_query(query, (entity_type,))
        
        similarities = []
        
        for result in results:
            embedding_id = result['id']
            entity_id = result['entity_id']
            serialized_vector = result['vector']
            
            vector = self.embedding_model.deserialize_embedding(serialized_vector)
            similarity = self.embedding_model.calculate_similarity(query_vector, vector)
            
            if similarity >= threshold:
                similarities.append((entity_id, similarity))
        
        # Sort by similarity (descending) and limit results
        sorted_similarities = sorted(similarities, key=lambda x: x[1], reverse=True)
        return sorted_similarities[:limit]