import unittest
from unittest.mock import MagicMock, patch
from fastapi import HTTPException
from datetime import datetime, timedelta
from ..auth import create_user, authenticate_user, create_jwt_token, verify_password, create_email_token, get_current_user, get_email_from_token

class TestAuthentication(unittest.TestCase):

    def setUp(self):
        self.db = MagicMock()
        self.user_data = {"email": "test@example.com", "password": "testpassword"}

    @patch('auth.bcrypt')
    def test_create_user(self, mock_bcrypt):
        # Arrange
        mock_bcrypt.hashpw.return_value = b'hashed_password'
        self.db.query().filter().first.return_value = None

        # Act
        created_user = create_user(self.db, self.user_data)

        # Assert
        self.assertIsNotNone(created_user)
        self.assertEqual(created_user.email, self.user_data["email"])

    @patch('auth.bcrypt')
    def test_create_user_existing_email(self, mock_bcrypt):
        # Arrange
        mock_bcrypt.hashpw.return_value = b'hashed_password'
        self.db.query().filter().first.return_value = MagicMock()

        # Act & Assert
        with self.assertRaises(HTTPException):
            create_user(self.db, self.user_data)

    @patch('auth.bcrypt')
    def test_authenticate_user_valid_credentials(self, mock_bcrypt):
        # Arrange
        user = MagicMock()
        user.email = self.user_data["email"]
        user.hashed_password = b'hashed_password'
        self.db.query().filter().first.return_value = user
        mock_bcrypt.verify.return_value = True

        # Act
        authenticated_user = authenticate_user(self.db, self.user_data["email"], self.user_data["password"])

        # Assert
        self.assertIsNotNone(authenticated_user)
        self.assertEqual(authenticated_user.email, self.user_data["email"])

    @patch('auth.bcrypt')
    def test_authenticate_user_invalid_credentials(self, mock_bcrypt):
        # Arrange
        self.db.query().filter().first.return_value = None

        # Act & Assert
        with self.assertRaises(HTTPException):
            authenticate_user(self.db, "invalid_email@example.com", "invalid_password")

    def test_create_jwt_token(self):
        # Arrange
        data = {"sub": "test@example.com"}
        expires_delta = timedelta(minutes=30)

        # Act
        token = create_jwt_token(data, expires_delta)

        # Assert
        self.assertIsNotNone(token)

    @patch('auth.pwd_context')
    def test_verify_password_valid(self, mock_pwd_context):
        # Arrange
        hashed_password = b'hashed_password'
        plain_password = "testpassword"
        mock_pwd_context.verify.return_value = True

        # Act
        valid = verify_password(plain_password, hashed_password)

        # Assert
        self.assertTrue(valid)

    @patch('auth.pwd_context')
    def test_verify_password_invalid(self, mock_pwd_context):
        # Arrange
        hashed_password = b'hashed_password'
        plain_password = "invalidpassword"
        mock_pwd_context.verify.return_value = False

        # Act
        valid = verify_password(plain_password, hashed_password)

        # Assert
        self.assertFalse(valid)

    def test_get_current_user(self):
        # Arrange
        token = "test_token"
        db = MagicMock()
        user_data = {"sub": "test@example.com"}

        # Act
        with patch('auth.jwt') as mock_jwt:
            mock_jwt.decode.return_value = user_data
            db.query().filter().first.return_value = MagicMock(email=user_data["sub"])
            current_user = get_current_user(token, db)

        # Assert
        self.assertIsNotNone(current_user)
        self.assertEqual(current_user.email, user_data["sub"])

    def test_create_email_token(self):
        # Arrange
        user_data = {"sub": "test@example.com"}

        # Act
        token = create_email_token(user_data)

        # Assert
        self.assertIsNotNone(token)

    def test_get_email_from_token(self):
        # Arrange
        token = "test_token"
        user_data = {"sub": "test@example.com"}

        # Act
        with patch('auth.jwt') as mock_jwt:
            mock_jwt.decode.return_value = user_data
            email = get_email_from_token(token)

        # Assert
        self.assertEqual(email, user_data["sub"])


if __name__ == '__main__':
    unittest.main()
