"""
Authentication utilities for JWT tokens and password handling.
"""

from datetime import datetime, timedelta
from typing import Optional, Union

from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy import text
from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException, status, Request, Header
from fastapi.security import OAuth2PasswordBearer

from app.database.database import get_db
from app.models.user import User

# Security configuration
SECRET_KEY = "temporarysecretkey"  # Should be replaced with env variable
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 password bearer scheme for token extraction
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/login")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plain password against its hashed version.
    
    Args:
        plain_password: The plain text password to check
        hashed_password: The stored hashed password
        
    Returns:
        bool: True if password matches, False otherwise
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """
    Hash a password using bcrypt.
    
    Args:
        password: The plain text password to hash
        
    Returns:
        str: Hashed password
    """
    return pwd_context.hash(password)


def authenticate_user(db: Session, email: str, password: str) -> Union[User, bool]:
    """
    Authenticate a user by email and password.
    
    Args:
        db: Database session
        email: User's email
        password: User's password
        
    Returns:
        Union[User, bool]: User object if authentication succeeds, False otherwise
    """
    user = db.query(User).filter(User.email == email).first()
    if not user or not verify_password(password, user.password_hash):
        return False
    return user


def create_access_token(*, data: dict = None, user_id: int = None, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a JWT access token.
    
    Args:
        data: Data to encode in the token
        user_id: User ID to encode in the token (alternative to data)
        expires_delta: Optional expiration time override
        
    Returns:
        str: Encoded JWT token
    """
    if data is None:
        data = {}
    
    if user_id is not None:
        data.update({"sub": user_id})
        
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    
    return encoded_jwt


async def get_current_user_from_token(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    """
    Get the current authenticated user from a JWT token.
    
    Args:
        token: JWT token from the Authorization header
        db: Database session
        
    Returns:
        User: The authenticated user
        
    Raises:
        HTTPException: If token is invalid or user not found
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: int = payload.get("sub")
        
        if user_id is None:
            raise credentials_exception
            
    except JWTError:
        raise credentials_exception
        
    user = db.query(User).filter(User.id == user_id).first()
    
    if user is None:
        raise credentials_exception
        
    return user


async def get_current_user_from_api_key(
    x_api_key: Optional[str] = Header(None),
    db: Session = Depends(get_db)
) -> Optional[User]:
    """
    Get the current authenticated user from an API key.
    
    Args:
        x_api_key: API key from the x-api-key header
        db: Database session
        
    Returns:
        Optional[User]: The authenticated user or None if no API key provided
        
    Raises:
        HTTPException: If API key is invalid or revoked
    """
    if not x_api_key:
        return None
    
    try:
        # We need to import the ApiKey model here to avoid circular imports
        from sqlalchemy import select
        from sqlalchemy.orm import Session
        
        # Look up the API key in the database
        stmt = text("SELECT user_id FROM api_keys WHERE key_value = :key AND revoked = 0")
        result = db.execute(stmt, {"key": x_api_key}).first()
        
        if not result:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid API key",
            )
        
        user_id = result[0]
        
        # Get the associated user
        user = db.query(User).filter(User.id == user_id).first()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User associated with API key not found",
            )
        
        # Update the last_used timestamp
        db.execute(
            text("UPDATE api_keys SET last_used = :now WHERE key_value = :key"),
            {"now": datetime.utcnow(), "key": x_api_key}
        )
        db.commit()
        
        return user
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing API key: {str(e)}"
        )


async def get_current_user(
    request: Request,
    token_user: Optional[User] = Depends(get_current_user_from_token),
    api_key_user: Optional[User] = Depends(get_current_user_from_api_key),
) -> User:
    """
    Get the authenticated user from either JWT token or API key.
    This function serves as a unified authentication middleware.
    
    Priority:
    1. JWT token (if valid)
    2. API key (if valid)
    
    Args:
        request: The request object
        token_user: User authenticated via JWT token
        api_key_user: User authenticated via API key
        
    Returns:
        User: The authenticated user
        
    Raises:
        HTTPException: If no valid authentication method is provided
    """
    # Check if we have a user from token or API key
    if token_user:
        return token_user
    
    if api_key_user:
        return api_key_user
    
    # If we get here, neither authentication method was successful
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Authentication required",
        headers={"WWW-Authenticate": "Bearer"},
    )


# Alias for backward compatibility
get_current_user_from_jwt = get_current_user_from_token