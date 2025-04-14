"""
Authentication endpoints for user registration and login.
"""

from datetime import timedelta
import secrets
import string
import logging  # Dodany import loggera
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.user import User, ApiKey
from app.schemas.user import UserCreate, UserResponse, UserLogin, Token, ApiKeyCreate, ApiKeyResponse
from app.auth.auth import authenticate_user, create_access_token, get_password_hash, get_current_user, ACCESS_TOKEN_EXPIRE_MINUTES

# Konfiguracja loggera
logger = logging.getLogger(__name__)

router = APIRouter(
    tags=["authentication"],
    responses={
        401: {"description": "Authentication failed"},
        400: {"description": "Bad request - validation error"}
    }
)


@router.post(
    "/register", 
    response_model=UserResponse, 
    status_code=status.HTTP_201_CREATED,
    responses={
        201: {
            "description": "User successfully registered",
            "content": {
                "application/json": {
                    "example": {
                        "id": 1,
                        "username": "johndoe",
                        "email": "john@example.com",
                        "created_at": "2025-04-13T12:00:00"
                    }
                }
            }
        },
        400: {
            "description": "Registration failed",
            "content": {
                "application/json": {
                    "examples": {
                        "email_exists": {
                            "summary": "Email already registered",
                            "value": {"detail": "Email already registered"}
                        },
                        "username_exists": {
                            "summary": "Username already taken",
                            "value": {"detail": "Username already taken"}
                        }
                    }
                }
            }
        }
    }
)
async def register_user(user_data: UserCreate, db: Session = Depends(get_db)) -> UserResponse:
    """
    Register a new user.
    
    Creates a new user account with the provided information. The password 
    is securely hashed using bcrypt before storage.
    
    Args:
        user_data: User registration data (username, email, password)
        db: Database session
        
    Returns:
        UserResponse: Newly created user object (without sensitive data)
        
    Raises:
        HTTPException: 
            400 Bad Request - If username or email already exists
            422 Unprocessable Entity - If input validation fails
    """
    # Check if user with this email already exists
    existing_email = db.query(User).filter(User.email == user_data.email).first()
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
        
    # Check if user with this username already exists
    existing_username = db.query(User).filter(User.username == user_data.username).first()
    if existing_username:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already taken"
        )
    
    # Hash password with bcrypt
    hashed_password = get_password_hash(user_data.password)
    
    # Create new user
    new_user = User(
        username=user_data.username,
        email=user_data.email,
        password_hash=hashed_password
    )
    
    # Store user data in database
    try:
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create user: {str(e)}"
        )
    
    return new_user


@router.post(
    "/login", 
    response_model=Token,
    responses={
        200: {
            "description": "Successful login",
            "content": {
                "application/json": {
                    "example": {
                        "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                        "token_type": "bearer",
                        "user": {
                            "id": 1,
                            "username": "johndoe",
                            "email": "john@example.com"
                        }
                    }
                }
            }
        },
        401: {
            "description": "Authentication failed",
            "content": {
                "application/json": {
                    "example": {"detail": "Incorrect email or password"}
                }
            }
        }
    }
)
async def login_for_access_token(
    user_credentials: UserLogin,
    db: Session = Depends(get_db)
) -> dict:
    """
    Authenticate user and return access token.
    
    This endpoint verifies the user credentials and generates a JWT token
    for authenticated API access. The token includes the user ID and has
    an expiration time.
    
    Args:
        user_credentials: User login credentials (email and password)
        db: Database session
        
    Returns:
        dict: JWT access token, token type, and user information
        
    Raises:
        HTTPException: If authentication fails (401 Unauthorized)
    """
    # Authenticate user
    user = authenticate_user(db, user_credentials.email, user_credentials.password)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    # Generate access token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        user_id=user.id,  # Używamy user_id bezpośrednio zamiast data={"sub": user.id}
        expires_delta=access_token_expires
    )
    
    # Return token and user info
    return {
        "access_token": access_token, 
        "token_type": "bearer",
        "user": user
    }


@router.post(
    "/apikey/generate",
    response_model=ApiKeyResponse,
    responses={
        201: {"description": "API key successfully generated"},
        401: {"description": "Authentication failed"},
    },
    status_code=status.HTTP_201_CREATED
)
async def generate_api_key(
    api_key_create: ApiKeyCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> ApiKeyResponse:
    """
    Generate a new API key for the authenticated user.
    
    This endpoint requires authentication and generates a new API key
    associated with the authenticated user. The API key can be used
    for programmatic access to the API without login.
    
    Args:
        api_key_create: Optional API key metadata like description
        current_user: The authenticated user (from JWT token)
        db: Database session
        
    Returns:
        ApiKeyResponse: The newly generated API key
        
    Raises:
        HTTPException: If authentication fails (401 Unauthorized)
    """
    # Generate a secure random API key
    alphabet = string.ascii_letters + string.digits
    key_value = ''.join(secrets.choice(alphabet) for _ in range(32))
    
    # Create a new API key record
    new_api_key = ApiKey(
        user_id=current_user.id,
        key_value=key_value,
        description=api_key_create.description
    )
    
    # Store in database
    try:
        db.add(new_api_key)
        db.commit()
        db.refresh(new_api_key)
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate API key: {str(e)}"
        )
    
    return new_api_key


@router.post(
    "/apikey/revoke/{key_id}",
    status_code=status.HTTP_200_OK,
    responses={
        200: {"description": "API key successfully revoked"},
        401: {"description": "Authentication failed"},
        404: {"description": "API key not found"},
    }
)
async def revoke_api_key(
    key_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> dict:
    """
    Revoke an existing API key.
    
    This endpoint allows users to revoke an API key, preventing its
    further use for authentication.
    
    Args:
        key_id: ID of the API key to revoke
        current_user: The authenticated user (from JWT token)
        db: Database session
        
    Returns:
        dict: Success message
        
    Raises:
        HTTPException: 
            401 Unauthorized - If authentication fails
            404 Not Found - If the API key does not exist or doesn't belong to the user
    """
    # Find the API key belonging to the current user
    api_key = db.query(ApiKey).filter(
        ApiKey.id == key_id,
        ApiKey.user_id == current_user.id
    ).first()
    
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="API key not found"
        )
    
    # Revoke the API key
    api_key.revoked = True
    
    try:
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to revoke API key: {str(e)}"
        )
    
    return {"message": "API key successfully revoked"}