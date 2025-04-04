import numpy as np
from llm.ollama_client import OllamaClient
import pickle

class EmbeddingModel:
    """
    Model for generating and comparing text embeddings.
    """
    
    def __init__(self, model_name="llama3"):
        """
        Initialize the embedding model.
        
        Args:
            model_name: Name of the model to use for embeddings
        """
        self.client = OllamaClient(model_name)
    
    def generate_embedding(self, text):
        """
        Generate an embedding vector for the given text.
        
        Args:
            text: Text to embed
            
        Returns:
            Embedding vector as a list of floats
        """
        embedding = self.client.get_embedding(text)
        
        # Convert to numpy array for easier manipulation
        return np.array(embedding).astype(np.float32)
    
    def calculate_similarity(self, embedding1, embedding2):
        """
        Calculate cosine similarity between two embeddings.
        
        Args:
            embedding1: First embedding vector
            embedding2: Second embedding vector
            
        Returns:
            Similarity score between 0 and 1
        """
        # Ensure the embeddings are numpy arrays
        if not isinstance(embedding1, np.ndarray):
            embedding1 = np.array(embedding1)
        
        if not isinstance(embedding2, np.ndarray):
            embedding2 = np.array(embedding2)
        
        # Calculate cosine similarity
        norm1 = np.linalg.norm(embedding1)
        norm2 = np.linalg.norm(embedding2)
        
        if norm1 == 0 or norm2 == 0:
            return 0  # Avoid division by zero
        
        return np.dot(embedding1, embedding2) / (norm1 * norm2)
    
    def serialize_embedding(self, embedding):
        """
        Serialize an embedding for storage.
        
        Args:
            embedding: Embedding vector
            
        Returns:
            Serialized embedding as bytes
        """
        return pickle.dumps(embedding)
    
    def deserialize_embedding(self, serialized_embedding):
        """
        Deserialize an embedding from storage.
        
        Args:
            serialized_embedding: Serialized embedding bytes
            
        Returns:
            Embedding vector
        """
        return pickle.loads(serialized_embedding)
