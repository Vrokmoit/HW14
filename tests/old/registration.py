import requests

# URL маршруту для реєстрації користувача
url = "http://localhost:8000/register/"

# Дані для реєстрації користувача
user_data = {
    "email": "vrokmoit.cattus@gmail.com",
    "password": "password"
}

# Виконання запиту POST
response = requests.post(url, json=user_data)

# Виведення результату запиту
print(response.status_code)
print(response.json())
