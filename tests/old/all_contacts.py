import requests

url = "http://127.0.0.1:8000/contacts/"
token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ2cm9rbW9pdEBnbWFpbC5jb20iLCJleHAiOjE3MTA4NjcxOTJ9.NbHlSk0Ndpf7rM5jdUUkNxGIa1420jNprbxOXtEaXik"  

headers = {
    "Authorization": f"Bearer {token}"
}

response = requests.get(url, headers=headers)

if response.status_code == 200:
    contacts = response.json()
    print("Список контактов:")
    for contact in contacts:
        print(contact)
else:
    print(f"Произошла ошибка: {response.status_code}")
