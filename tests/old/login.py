import requests


user_credentials = {
    "email": "vrokmoit@gmail.com",
    "password": "password"
}


response = requests.post("http://localhost:8000/login/", json=user_credentials)


if response.status_code == 200:
    access_token = response.json()["access_token"]
    print("Вхід виконано. Токен доступу:", access_token)
else:
    print("Помилка входу. Статус-код:", response.status_code)
