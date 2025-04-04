import json
import datetime
from abc import ABC, abstractmethod
from database.db_manager import DatabaseManager
from llm.ollama_client import OllamaClient

class BaseAgent(ABC):
    """Base class for all agents in the Smart Shopping system."""
    
    def __init__(self, agent_name, model_name="llama3"):
        """Initialize the base agent with a name and model."""
        self.agent_name = agent_name
        self.db = DatabaseManager()
        self.llm = OllamaClient(model_name)
        self.memory = {}  # In-memory storage for short-term memory
    
    @abstractmethod
    def process(self, input_data):
        """Process input data and perform agent-specific tasks."""
        pass
    
    def store_memory(self, key, value):
        """Store a memory item in both short-term and long-term memory."""
        # Store in short-term memory (for current session)
        self.memory[key] = value
        
        # Store in long-term memory (database)
        self.db.store_agent_memory(
            self.agent_name,
            key,
            json.dumps(value) if not isinstance(value, str) else value
        )
    
    def recall_memory(self, key):
        """Recall a memory item from short-term memory or long-term memory."""
        # First check short-term memory
        if key in self.memory:
            return self.memory[key]
        
        # If not found, check long-term memory
        results = self.db.get_agent_memory(self.agent_name, key)
        if results:
            value = results[0]['memory_value']
            # If value is JSON, parse it
            try:
                value = json.loads(value)
            except json.JSONDecodeError:
                pass
            
            # Store in short-term memory for future quick access
            self.memory[key] = value
            return value
        
        return None
    
    def log_activity(self, activity_type, details):
        """Log agent activity."""
        timestamp = datetime.datetime.now().isoformat()
        log_entry = {
            "agent": self.agent_name,
            "activity": activity_type,
            "details": details,
            "timestamp": timestamp
        }
        print(f"Agent Log: {json.dumps(log_entry)}")
        # Could also store logs in database if needed
    
    def get_llm_response(self, prompt, system_prompt=None):
        """Get a response from the LLM."""
        return self.llm.generate(prompt, system_prompt)