"""Test script to debug backend invoice upload pipeline."""

import os
from fastapi.testclient import TestClient
from backend.main import app

def run_test():
    client = TestClient(app)
    
    file_path = os.path.join("test_invoices", "01_Happy_Path_AWS.pdf")
    if not os.path.exists(file_path):
        print(f"Error: {file_path} not found. Run generate_edge_cases.py first.")
        return
        
    print(f"Uploading {file_path} to TestClient...")
    with open(file_path, "rb") as f:
        response = client.post(
            "/api/v1/invoices/upload",
            files={"file": (os.path.basename(file_path), f, "application/pdf")}
        )
        
    print("Status Code:", response.status_code)
    print("Response JSON:")
    print(response.json())

if __name__ == "__main__":
    run_test()
