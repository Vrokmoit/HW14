import unittest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from ..contactpr.models import Base, Contact, User

class TestModels(unittest.TestCase):

    def setUp(self):
        # Підключення до бази даних SQLite у пам'яті
        engine = create_engine('sqlite:///:memory:')
        Session = sessionmaker(bind=engine)
        self.session = Session()

        # Створення таблиць у базі даних
        Base.metadata.create_all(engine)

    def tearDown(self):
        # Закриття сесії та очистка бази даних
        self.session.close_all()
        Base.metadata.drop_all(self.session.bind)

    def test_contact_model(self):
        # Arrange
        contact_data = {
            "first_name": "John",
            "last_name": "Doe",
            "email": "john@example.com",
            "phone_number": "123456789",
            "birthday": "1990-01-01",
            "additional_data": "Some additional data",
            "owner_id": 1
        }

        # Act
        contact = Contact(**contact_data)
        self.session.add(contact)
        self.session.commit()

        # Assert
        self.assertIsNotNone(contact.id)
        self.assertEqual(contact.first_name, "John")
        self.assertEqual(contact.last_name, "Doe")
        self.assertEqual(contact.email, "john@example.com")
        self.assertEqual(contact.phone_number, "123456789")
        self.assertEqual(contact.birthday, "1990-01-01")
        self.assertEqual(contact.additional_data, "Some additional data")
        self.assertEqual(contact.owner_id, 1)

    def test_user_model(self):
        # Arrange
        user_data = {
            "email": "test@example.com",
            "hashed_password": "hashed_password",
            "avatar_url": "https://example.com/avatar.png",
            "confirmed": True
        }

        # Act
        user = User(**user_data)
        self.session.add(user)
        self.session.commit()

        # Assert
        self.assertIsNotNone(user.id)
        self.assertEqual(user.email, "test@example.com")
        self.assertEqual(user.hashed_password, "hashed_password")
        self.assertEqual(user.avatar_url, "https://example.com/avatar.png")
        self.assertTrue(user.confirmed)

if __name__ == '__main__':
    unittest.main()
