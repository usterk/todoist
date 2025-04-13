"""
Authentication endpoints for user registration and login.
"""

from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.user import User
from app.schemas.user import UserCreate, UserResponse, UserLogin, Token
from app.auth.auth import authenticate_user, create_access_token, get_password_hash, ACCESS_TOKEN_EXPIRE_MINUTES

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
    user = authenticate_user(db, user_credentials.email, user_credentials.password)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.id}, 
        expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token, 
        "token_type": "bearer",
        "user": user
    }