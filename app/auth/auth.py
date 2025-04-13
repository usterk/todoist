"""
Authentication utilities for JWT tokens and password handling.
"""

from datetime import datetime, timedelta
from typing import Optional, Union
import logging

from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy import text
from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException, status, Request, Header
from fastapi.security import OAuth2PasswordBearer

from app.database.database import get_db
from app.models.user import User

# Configure logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)  # Set to INFO to see important logs

# Security configuration
SECRET_KEY = "temporarysecretkey"  # Should be replaced with env variable
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 password bearer scheme for token extraction
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/login", auto_error=False)


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
        data.update({"sub": str(user_id)})  # Convert user_id to string for consistent handling
        
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    
    # Log token creation for debugging
    logger.debug(f"Generated token for user_id: {user_id} with expiry: {expire}")
    
    return encoded_jwt


async def get_current_user_from_token(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> Optional[User]:
    """
    Get the current authenticated user from a JWT token.
    
    Args:
        token: JWT token from the Authorization header
        db: Database session
        
    Returns:
        Optional[User]: The authenticated user or None if no token provided
        
    Raises:
        HTTPException: If token is invalid or user not found
    """
    if token is None:
        return None

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # Log token validation attempt for debugging
        logger.info(f"Validating token: {token[:10]}...")
        
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        logger.debug(f"Token payload: {payload}")
        
        user_id_str = payload.get("sub")
        
        if user_id_str is None:
            logger.warning("Token missing 'sub' claim")
            raise credentials_exception
            
        # Convert user_id from string to int
        try:
            user_id = int(user_id_str)
            logger.debug(f"Extracted user_id: {user_id}")
        except ValueError:
            logger.warning(f"Invalid user_id format: {user_id_str}")
            raise credentials_exception
            
    except JWTError as e:
        logger.warning(f"JWT validation error: {str(e)}")
        raise credentials_exception
        
    user = db.query(User).filter(User.id == user_id).first()
    
    if user is None:
        logger.warning(f"No user found for ID: {user_id}")
        raise credentials_exception
        
    logger.info(f"Authentication successful for user: {user.username}")
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
        logger.debug("No API key provided")
        return None
    
    try:
        # Look up the API key in the database
        logger.info(f"Validating API key: {x_api_key[:10]}...")
        
        # Use safe query parameters to avoid SQL injection
        stmt = text("SELECT user_id FROM api_keys WHERE key_value = :key AND revoked = 0")
        result = db.execute(stmt, {"key": x_api_key}).first()
        
        if not result:
            logger.warning(f"Invalid API key: {x_api_key[:10]}...")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid API key",
            )
        
        user_id = result[0]
        logger.debug(f"API key matches user_id: {user_id}")
        
        # Get the associated user
        user = db.query(User).filter(User.id == user_id).first()
        
        if not user:
            logger.warning(f"No user found for API key user_id: {user_id}")
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
        
        logger.info(f"API key authentication successful for user: {user.username}")
        return user
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing API key: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing API key: {str(e)}"
        )


async def get_current_user(
    request: Request,
    token: str = Depends(oauth2_scheme),
    x_api_key: Optional[str] = Header(None),
    db: Session = Depends(get_db)
) -> User:
    """
    Get the authenticated user from either JWT token or API key.
    This function serves as a unified authentication middleware.
    
    Priority:
    1. JWT token (if valid)
    2. API key (if valid)
    
    Args:
        request: The request object
        token: JWT token from Authorization header
        x_api_key: API key from x-api-key header
        db: Database session
        
    Returns:
        User: The authenticated user
        
    Raises:
        HTTPException: If no valid authentication method is provided
    """
    user = None
    token_error = False
    
    # Try JWT token first
    if token:
        try:
            # Decode JWT token
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            user_id_str = payload.get("sub")
            
            if user_id_str:
                # Get user by ID
                user_id = int(user_id_str)
                user = db.query(User).filter(User.id == user_id).first()
                
                if user:
                    logger.info(f"JWT token authentication successful for user: {user.username}")
                    return user
        except Exception as e:
            logger.warning(f"JWT token validation failed: {str(e)}")
            token_error = True
    
    # Try API key if JWT failed
    if x_api_key:
        try:
            # Look up API key
            stmt = text("SELECT user_id FROM api_keys WHERE key_value = :key AND revoked = 0")
            result = db.execute(stmt, {"key": x_api_key}).first()
            
            if result:
                user_id = result[0]
                user = db.query(User).filter(User.id == user_id).first()
                
                if user:
                    # Update last used timestamp
                    db.execute(
                        text("UPDATE api_keys SET last_used = :now WHERE key_value = :key"),
                        {"now": datetime.utcnow(), "key": x_api_key}
                    )
                    db.commit()
                    
                    logger.info(f"API key authentication successful for user: {user.username}")
                    return user
        except Exception as e:
            logger.warning(f"API key validation failed: {str(e)}")
    
    # If we get here, neither authentication method was successful
    logger.warning("Authentication required but no valid auth method found")
    
    # Używamy różnych komunikatów w zależności od tego, co się wydarzyło
    if token_error:
        # Jeśli był token, ale był niepoprawny
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    elif token or x_api_key:
        # Jeśli był token lub klucz API, ale nie znaleziono użytkownika
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    else:
        # Jeśli w ogóle nie było autoryzacji
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )


# Alias for backward compatibility
get_current_user_from_jwt = get_current_user_from_token