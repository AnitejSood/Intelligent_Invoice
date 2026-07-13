"""Test HTTP upload directly to running uvicorn server."""

import os
import requests

def run_test():
    file_path = os.path.join("test_invoices", "01_Happy_Path_AWS.pdf")
    if not os.path.exists(file_path):
        print(f"Error: {file_path} not found.")
        return
        
    url = "http://localhost:8000/api/v1/invoices/upload"
    print(f"Uploading {file_path} to {url}...")
    
    with open(file_path, "rb") as f:
        try:
            response = requests.post(
                url,
                files={"file": (os.path.basename(file_path), f, "application/pdf")}
            )
            print("Status Code:", response.status_code)
            print("Response text:")
            print(response.text)
        except Exception as e:
            print("HTTP Request Failed:", e)

if __name__ == "__main__":
    run_test()
