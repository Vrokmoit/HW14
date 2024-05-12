import requests

# URL маршруту для пошуку контактів
url = "http://127.0.0.1:8000/contacts/search/"

# Параметр запиту (пошуковий запит)
query = "Дашенька"

# Ваш JWT токен
token = "ваш_токен_тут"

# Заголовок з токеном
headers = {"Authorization": f"Bearer {token}"}

# Створення запиту GET з параметром запиту та заголовком з токеном
response = requests.get(url, params={"query": query}, headers=headers)

# Перевірка статусу відповіді
if response.status_code == 200:
    # Результат успішний, виведемо дані контактів
    contacts = response.json()
    print("Результати пошуку:")
    for contact in contacts:
        print(contact)
else:
    # Відображення повідомлення про помилку
    print(f"Помилка: {response.status_code}")
