import json
import requests
import time

class OllamaClient:
    """
    Client for interacting with Ollama API for LLM generations.
    """
    
    def __init__(self, model_name="llama3", base_url="http://localhost:11434"):
        """
        Initialize the Ollama client.
        
        Args:
            model_name: Name of the model to use (default: llama3)
            base_url: Base URL for the Ollama API
        """
        self.model_name = model_name
        self.base_url = base_url
        self.generation_endpoint = f"{base_url}/api/generate"
        self.embedding_endpoint = f"{base_url}/api/embeddings"
    
    def generate(self, prompt, system_prompt=None):
        """
        Generate text using the Ollama API.
        
        Args:
            prompt: The user prompt text
            system_prompt: Optional system prompt to guide the LLM
            
        Returns:
            Generated text string
        """
        try:
            headers = {"Content-Type": "application/json"}
            
            payload = {
                "model": self.model_name,
                "prompt": prompt,
                "stream": False
            }
            
            if system_prompt:
                payload["system"] = system_prompt
            
            response = requests.post(
                self.generation_endpoint,
                headers=headers,
                json=payload
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get('response', '')
            else:
                print(f"Error: Ollama API returned status code {response.status_code}")
                print(f"Response: {response.text}")
                return "Sorry, I couldn't generate a response at this time."
        
        except Exception as e:
            print(f"Error generating text with Ollama: {str(e)}")
            return "Sorry, there was an error communicating with the language model."
    
    def get_embedding(self, text):
        """
        Get embeddings for text using the Ollama API.
        
        Args:
            text: Text to embed
            
        Returns:
            Vector embedding as a list of floats
        """
        try:
            headers = {"Content-Type": "application/json"}
            
            payload = {
                "model": self.model_name,
                "prompt": text
            }
            
            response = requests.post(
                self.embedding_endpoint,
                headers=headers,
                json=payload
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get('embedding', [])
            else:
                print(f"Error: Ollama API returned status code {response.status_code}")
                print(f"Response: {response.text}")
                return []
        
        except Exception as e:
            print(f"Error getting embeddings with Ollama: {str(e)}")
            return []
