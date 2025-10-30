#!/usr/bin/env python3
"""
FleetManager Pro - Professional Telematics Solution
Run this file to start the application: python main.py
"""

import os
import sys

# Change to backend/app directory and add to path
backend_app_path = os.path.join(os.path.dirname(__file__), 'backend', 'app')
os.chdir(backend_app_path)
sys.path.insert(0, backend_app_path)

# Import and run the application
from main import create_app
from seed import seed

def main():
    print("=" * 50)
    print("  TruckTrace - Starting Application")
    print("=" * 50)
    
    # Initialize database and seed data
    try:
        print("Initializing database...")
        seed()
        print("[OK] Database initialized with sample data")
    except Exception as e:
        print(f"[ERROR] Database initialization failed: {e}")
        return
    
    # Create and run Flask app
    try:
        app = create_app()
        print("\n[STARTING] TruckTrace...")
        print("[DASHBOARD] http://localhost:8080")
        print("[API TEST] http://localhost:8080/api-test")
        print("[INFO] Press Ctrl+C to stop\n")
        
        app.run(host='0.0.0.0', port=8080, debug=True)
        
    except KeyboardInterrupt:
        print("\n[STOPPED] TruckTrace stopped")
    except Exception as e:
        print(f"[ERROR] Application failed to start: {e}")

if __name__ == '__main__':
    main()