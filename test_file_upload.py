"""
Test script to upload a file to the backend
Run with: python test_file_upload.py
"""
import requests
import io

url = "http://127.0.0.1:8000/api/v1/send-brief"

# Create a simple text file in memory
file_content = b"This is a test file for the brief"
files = {
    "attachments": ("test_logo.png", file_content, "image/png")
}

# Form data
data = {
    "name": "Test User",
    "email": "test@test.com",
    "phone": "1234567890",
    "company": "Test Company",
    "projectName": "Test Project",
    "projectType": "website",
    "projectDescription": "This is a test project description",
    "features": '["User Authentication", "CMS", "Analytics"]',
    "budget": "r3",
    "timeline": "two_three_months",
    "locale": "en",
}

response = requests.post(url, data=data, files=files)
print(f"Status: {response.status_code}")
print(f"Response: {response.text}")