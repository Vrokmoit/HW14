import requests

token = "your_access_token_here"

url = 'http://localhost:8000/contacts/10'
headers = {"Authorization": f"Bearer {token}"}

response = requests.get(url, headers=headers)

if response.status_code == 200:
    print(response.json())  # Вывести ответ в формате JSON
else:
    print(f"Статус код: {response.status_code}. Контакт не найден.")
