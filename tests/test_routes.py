from fastapi.testclient import TestClient
from ..main import app
from ..contactpr.database import engine, SessionLocal, get_db


client = TestClient(app)

def override_get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

def test_create_contact():
    # Arrange
    contact_data = {
        "first_name": "John",
        "last_name": "Doe",
        "email": "john.doe@example.com",
        "phone_number": "1234567890",
        "birthday": "1990-01-01",
        "additional_data": "Additional info"
    }
    
    # Act
    response = client.post("/contacts/", json=contact_data)
    created_contact = response.json()
    
    # Assert
    assert response.status_code == 200
    assert created_contact["first_name"] == contact_data["first_name"]
    assert created_contact["last_name"] == contact_data["last_name"]
    assert created_contact["email"] == contact_data["email"]
    assert created_contact["phone_number"] == contact_data["phone_number"]
    assert created_contact["birthday"] == contact_data["birthday"]
    assert created_contact["additional_data"] == contact_data["additional_data"]

