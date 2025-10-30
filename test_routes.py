#!/usr/bin/env python3
"""
Quick test to verify routes are working
"""
import sys
import os

# Add backend/app to path
backend_app_path = os.path.join(os.path.dirname(__file__), 'backend', 'app')
sys.path.insert(0, backend_app_path)
os.chdir(backend_app_path)

from main import create_app

def test_routes():
    app = create_app()
    
    with app.test_client() as client:
        # Test main routes
        routes_to_test = [
            '/',
            '/dashboard', 
            '/ai-dashboard',
            '/system-status',
            '/assistant',
            '/api-test'
        ]
        
        print("Testing routes:")
        for route in routes_to_test:
            try:
                response = client.get(route)
                status = "OK" if response.status_code == 200 else f"ERROR {response.status_code}"
                print(f"  {route:<20} {status}")
            except Exception as e:
                print(f"  {route:<20} ERROR: {e}")
        
        # Test chatbot API
        try:
            response = client.post('/api/chatbot', 
                                 json={'message': 'test'}, 
                                 content_type='application/json')
            status = "OK" if response.status_code == 200 else f"ERROR {response.status_code}"
            print(f"  /api/chatbot         {status}")
        except Exception as e:
            print(f"  /api/chatbot         ERROR: {e}")

if __name__ == '__main__':
    test_routes()