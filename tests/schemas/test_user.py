"""
Tests for user schemas validators.
"""

import pytest
from pydantic import ValidationError
from app.schemas.user import UserBase, UserCreate, UserUpdate, UserLogin

def test_user_create_validation():
    """Test validation in UserCreate schema"""
    # Test valid user creation data
    valid_user = UserCreate(
        username="validuser",
        email="valid@example.com",
        password="ValidPassword123"
    )
    
    assert valid_user.username == "validuser"
    assert valid_user.email == "valid@example.com"
    assert valid_user.password == "ValidPassword123"
    
    # Test invalid password without digit
    with pytest.raises(ValidationError) as exc:
        UserCreate(
            username="testuser",
            email="test@example.com",
            password="InvalidPassword"
        )
    assert "Password must contain at least one digit" in str(exc.value)
    
    # Test invalid password without uppercase
    with pytest.raises(ValidationError) as exc:
        UserCreate(
            username="testuser",
            email="test@example.com",
            password="invalidpassword123"
        )
    assert "Password must contain at least one uppercase letter" in str(exc.value)
    
    # Test invalid password without lowercase
    with pytest.raises(ValidationError) as exc:
        UserCreate(
            username="testuser",
            email="test@example.com",
            password="INVALIDPASSWORD123"
        )
    assert "Password must contain at least one lowercase letter" in str(exc.value)

def test_user_update_validation():
    """Test validation in UserUpdate schema"""
    # Test valid update data
    valid_update = UserUpdate(
        username="newusername",
        email="new@example.com",
        password="NewPassword123"
    )
    
    assert valid_update.username == "newusername"
    assert valid_update.email == "new@example.com"
    assert valid_update.password == "NewPassword123"
    
    # Test with only some fields
    partial_update = UserUpdate(username="onlyusername")
    assert partial_update.username == "onlyusername"
    assert partial_update.email is None
    assert partial_update.password is None
    
    # Test password None validation - pokrycie przypadku, gdy None jest przekazywane do walidatora
    null_password_update = UserUpdate(
        username="updateuser",
        email="update@example.com",
        password=None
    )
    assert null_password_update.password is None
    
    # Test invalid password without digit when provided
    with pytest.raises(ValidationError) as exc:
        UserUpdate(password="InvalidPassword")
    assert "Password must contain at least one digit" in str(exc.value)
    
    # Test invalid password without uppercase when provided
    with pytest.raises(ValidationError) as exc:
        UserUpdate(password="invalidpassword123")
    assert "Password must contain at least one uppercase letter" in str(exc.value)
    
    # Test invalid password without lowercase when provided
    with pytest.raises(ValidationError) as exc:
        UserUpdate(password="INVALIDPASSWORD123")
    assert "Password must contain at least one lowercase letter" in str(exc.value)

def test_user_login_validation():
    """Test validation in UserLogin schema"""
    # Test valid login data
    valid_login = UserLogin(
        email="login@example.com",
        password="LoginPassword123"
    )
    
    assert valid_login.email == "login@example.com"
    assert valid_login.password == "LoginPassword123"
    
    # Test invalid email
    with pytest.raises(ValidationError) as exc:
        UserLogin(
            email="invalid_email",  # Not a valid email format
            password="LoginPassword123"
        )
    assert "value is not a valid email address" in str(exc.value)