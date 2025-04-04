import argparse
import os
import yaml
import uvicorn
from pathlib import Path

from database.schema import create_database_schema
from database.seed_data import seed_database
from api.main import app


def setup_environment():
    """Set up the application environment."""
    
    # Ensure data directory exists
    Path("data").mkdir(exist_ok=True)
    
    # Create database schema if it doesn't exist
    create_database_schema()
    
    print("Environment setup complete.")


def load_config(config_path='config.yaml'):
    """Load configuration from YAML file."""
    if os.path.exists(config_path):
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)
    else:
        # Return default config
        return {
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
            }
        }


def save_config(config, config_path='config.yaml'):
    """Save configuration to YAML file."""
    with open(config_path, 'w') as f:
        yaml.dump(config, f)


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='Smart Shopping Application')
    
    parser.add_argument('--setup', action='store_true', help='Set up the environment')
    parser.add_argument('--seed', action='store_true', help='Seed the database with initial data')
    parser.add_argument('--serve', action='store_true', help='Start the API server')
    parser.add_argument('--customer-data', type=str, default='data/customer_data.csv', help='Path to customer data CSV file')
    parser.add_argument('--product-data', type=str, default='data/product_data.csv', help='Path to product data CSV file')
    
    return parser.parse_args()


def main():
    """Main application entry point."""
    args = parse_args()
    config = load_config()
    
    if args.setup:
        setup_environment()
    
    if args.seed:
        seed_database(args.customer_data, args.product_data)
    
    if args.serve:
        uvicorn.run(
            "api.main:app",
            host=config['server']['host'],
            port=config['server']['port'],
            reload=True
        )
    
    # If no action specified, print usage
    if not any([args.setup, args.seed, args.serve]):
        print("No action specified. Use --help for available options.")


if __name__ == "__main__":
    main()
