import requests
import json

# Read the example file
with open('examples/chart_reports.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# Send request using requests library
response = requests.post(
    'http://localhost:8000/generate',
    json=data,
    headers={'Content-Type': 'application/json'}
)

print(f"Status Code: {response.status_code}")
print(f"Response: {response.text}")