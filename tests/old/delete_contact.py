import requests

def delete_contact(contact_id, token):
    url = f"http://127.0.0.1:8000/contacts/{contact_id}"
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.delete(url, headers=headers)
    
    if response.status_code == 200:
        print("Контакт успішно видалено")
    elif response.status_code == 404:
        print("Контакт не знайдено")
    else:
        print("Помилка:", response.status_code)

delete_contact(8, "ваш_токен_доступу")
