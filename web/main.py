import sys
import os

# Add project root to path so we can import from src and web
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from web.app import app

if __name__ == "__main__":
    print("Starting the Telecom Revenue Forecasting Web App from main.py...")
    app.run(debug=False, port=5000)
