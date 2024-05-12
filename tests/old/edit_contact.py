import requests

url = "http://127.0.0.1:8000/contacts/10"  
data = {
    "first_name": "ДFDFDа",
    "last_name": "FDFFDFDF",
    "email": "-",
    "phone_number": "+2323434432",
    "birthday": "2001-03-19",
    "additional_data": "" 
}

# Ваш JWT токен
access_token = "your_access_token_here"

# Створення заголовка з токеном доступу
headers = {
    "Authorization": f"Bearer {access_token}",
    "Content-Type": "application/json"
}

# Відправлення PUT-запиту з даними та токеном доступу у заголовку
response = requests.put(url, json=data, headers=headers)

print(response.status_code)
print(response.json())
