import yaml
import os
from pathlib import Path


class Config:
    """
    Configuration manager for the Smart Shopping application.
    """
    
    def __init__(self, config_path='config.yaml'):
        """
        Initialize configuration manager.
        
        Args:
            config_path: Path to configuration YAML file
        """
        self.config_path = config_path
        self.config = self._load_config()
    
    def _load_config(self):
        """Load configuration from file or create default."""
        if os.path.exists(self.config_path):
            with open(self.config_path, 'r') as f:
                return yaml.safe_load(f)
        else:
            # Create default config
            default_config = {
                "server": {
                    "host": "0.0.0.0",
                    "port": 8000
                },
                "database": {
                    "path": "data/smart_shopping.db"
                },
                "ollama": {
                    "base_url": "http://localhost:11434",
                    "model": "llama3"
                },
                "logging": {
                    "level": "INFO",
                    "file": "logs/smart_shopping.log"
                }
            }
            
            # Save default config
            self.save_config(default_config)
            
            return default_config
    
    def get(self, key, default=None):
        """
        Get configuration value.
        
        Args:
            key: Configuration key (can use dot notation for nested keys)
            default: Default value if key not found
            
        Returns:
            Configuration value or default
        """
        keys = key.split('.')
        value = self.config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def set(self, key, value):
        """
        Set configuration value.
        
        Args:
            key: Configuration key (can use dot notation for nested keys)
            value: Value to set
            
        Returns:
            True if successful, False otherwise
        """
        keys = key.split('.')
        config = self.config
        
        # Navigate to the parent of the target key
        for i in range(len(keys) - 1):
            k = keys[i]
            if k not in config:
                config[k] = {}
            config = config[k]
        
        # Set the value
        config[keys[-1]] = value
        
        # Save the updated config
        self.save_config(self.config)
        
        return True
        
    def save_config(self, config):
        """
        Save configuration to file.
        
        Args:
            config: Configuration dictionary to save
        """
        # Ensure directory exists
        Path(self.config_path).parent.mkdir(parents=True, exist_ok=True)
        
        with open(self.config_path, 'w') as f:
            yaml.dump(config, f)