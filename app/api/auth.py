"""
Authentication endpoints for user registration and login.
"""

from datetime import timedelta, datetime  # Added datetime import
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
    summary="Generate API Key",
    description="Generate a new API key for the authenticated user. This key can be used for API authentication.",
    status_code=status.HTTP_201_CREATED,
    responses={
        201: {
            "description": "API key generated successfully",
            "content": {
                "application/json": {
                    "example": {
                        "id": 1,
                        "key_value": "a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6",
                        "description": "Integration for Project X",
                        "created_at": "2023-11-28T12:34:56.789012"
                    }
                }
            }
        },
        401: {"description": "Unauthorized - Authentication required"},
        404: {"description": "User not found"}
    }
)
async def create_api_key(
    api_key_data: ApiKeyCreate = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> ApiKeyResponse:
    """
    Generate a new API key for the authenticated user.
    
    - This endpoint requires authentication with a JWT token.
    - The generated API key can be used to authenticate API requests.
    - The API key does not expire unless revoked.
    - Optional description can be provided to identify the API key's purpose.
    
    Args:
        api_key_data: Optional API key creation data with description
        db: Database session
        current_user: The authenticated user
    
    Returns:
        ApiKeyResponse: The created API key with its unique value
    """
    user_id = current_user.id if isinstance(current_user, User) else current_user
    
    logging.info(f"Generating API key for user ID: {user_id}")
    
    # Verify user exists
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        logging.warning(f"User not found: {user_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Generate a secure random API key
    key_chars = string.ascii_letters + string.digits
    key_value = ''.join(secrets.choice(key_chars) for _ in range(32))
    
    # Create API key in database
    description = None
    if api_key_data:
        description = api_key_data.description
        
    api_key = ApiKey(
        user_id=user_id,
        key_value=key_value,
        description=description,
        last_used=None,
        created_at=datetime.utcnow(),
        revoked=False
    )
    
    try:
        db.add(api_key)
        db.commit()
        db.refresh(api_key)
    except Exception as e:
        db.rollback()
        logging.error(f"Failed to generate API key: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate API key: {str(e)}"
        )
    
    logging.info(f"API key generated successfully for user ID: {user_id}")
    
    return ApiKeyResponse(
        id=api_key.id,
        key_value=api_key.key_value,
        description=api_key.description,
        created_at=api_key.created_at
    )


@router.post(
    "/apikey/revoke/{key_id}",
    summary="Revoke API Key",
    description="Revoke an existing API key. Once revoked, the key cannot be used for authentication.",
    status_code=status.HTTP_200_OK,
    responses={
        200: {"description": "API key successfully revoked"},
        401: {"description": "Unauthorized - Authentication required"},
        403: {"description": "Forbidden - You can only revoke your own API keys"},
        404: {"description": "API key not found"}
    }
)
async def revoke_api_key(
    key_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> dict:
    """
    Revoke an existing API key.
    
    Args:
        key_id: ID of the API key to revoke
        db: Database session
        current_user: The authenticated user
        
    Returns:
        dict: Message confirming successful revocation
        
    Raises:
        HTTPException: If API key not found or belongs to another user
    """
    # Determine user_id from current_user
    user_id = current_user.id if isinstance(current_user, User) else current_user
    
    # Find the API key in the database
    api_key = db.query(ApiKey).filter(ApiKey.id == key_id).first()
    
    if not api_key:
        logging.warning(f"API key not found: {key_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="API key not found"
        )
    
    # Verify the API key belongs to the authenticated user
    if api_key.user_id != user_id:
        logging.warning(f"Unauthorized attempt to revoke API key: {key_id} by user: {user_id}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only revoke your own API keys"
        )
    
    # Revoke the API key
    api_key.revoked = True
    
    try:
        db.commit()
    except Exception as e:
        db.rollback()
        logging.error(f"Failed to revoke API key: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to revoke API key: {str(e)}"
        )
    
    logging.info(f"API key revoked: {key_id} by user: {user_id}")
    
    return {"message": "API key successfully revoked"}