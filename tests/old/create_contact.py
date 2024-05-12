import requests

def create_contact(data, token):
    url = "http://127.0.0.1:8000/contacts/"
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.post(url, json=data, headers=headers)

    if response.status_code == 200:
        print("Контакт успішно створено:", response.json())
    else:
        print("Виникла помилка:", response.status_code)
        print("Текст помилки:", response.text)

data = {
    "first_name": "Fjkjk",
    "last_name": "SLLDLSDLS",
    "email": "test@gmail.com",
    "phone_number": "+380498309364",
    "birthday": "1973-11-26",
    "additional_data": ""
}
create_contact(data, "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ2cm9rbW9pdEBnbWFpbC5jb20iLCJleHAiOjE3MTA4NjcxOTJ9.NbHlSk0Ndpf7rM5jdUUkNxGIa1420jNprbxOXtEaXik")
