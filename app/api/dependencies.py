import logging
from datetime import datetime
from typing import Optional

from fastapi import Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.user import User, ApiKey

# ...existing code...

def get_current_user_from_api_key(request: Request, db: Session = Depends(get_db)) -> User:
    """
    Get the current user from API key authentication.
    
    Args:
        request: The incoming request
        db: Database session
    
    Returns:
        User: The authenticated user
    
    Raises:
        HTTPException: If API key is missing, invalid, or revoked
    """
    api_key_header = request.headers.get("x-api-key")
    if not api_key_header:
        logging.warning("API key not found in request headers")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API key not found in request headers",
            headers={"WWW-Authenticate": "APIKey"},
        )
    
    # Find the API key in the database
    api_key = db.query(ApiKey).filter(ApiKey.key_value == api_key_header).first()
    
    if not api_key:
        logging.warning("Invalid API key provided")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key",
            headers={"WWW-Authenticate": "APIKey"},
        )
    
    if api_key.revoked:
        logging.warning(f"Attempt to use revoked API key: {api_key.id}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API key has been revoked",
            headers={"WWW-Authenticate": "APIKey"},
        )
    
    # Find the user associated with the API key
    user = db.query(User).get(api_key.user_id)
    
    if not user:
        logging.warning(f"User not found for API key: {api_key.id}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "APIKey"},
        )
    
    # Update the last_used timestamp
    api_key.last_used = datetime.utcnow()
    db.commit()
    
    logging.info(f"Successful API key authentication for user: {user.id}")
    return user

def get_current_user_with_api_key_fallback(
    request: Request,
    db: Session = Depends(get_db),
    jwt_user: Optional[User] = Depends(get_current_user_optional),
) -> User:
    """
    Try to authenticate with JWT token first, then fall back to API key.
    
    Args:
        request: The incoming request
        db: Database session
        jwt_user: User from JWT authentication (if available)
        
    Returns:
        User: The authenticated user
    """
    if jwt_user:
        return jwt_user
    
    # Fall back to API key authentication
    return get_current_user_from_api_key(request, db)

# Update the current authentication dependency
def get_current_user_authenticated(
    request: Request,
    db: Session = Depends(get_db),
) -> User:
    """
    Get the current authenticated user, trying both JWT and API key authentication.
    
    Args:
        request: The incoming request
        db: Database session
    
    Returns:
        User: The authenticated user
        
    Raises:
        HTTPException: If neither authentication method is successful
    """
    try:
        # Try JWT authentication first
        return get_current_user(request)
    except HTTPException as jwt_error:
        try:
            # Fall back to API key authentication
            return get_current_user_from_api_key(request, db)
        except HTTPException as api_key_error:
            # Neither authentication method worked
            logging.warning("Authentication failed: JWT and API key authentication both failed")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication failed",
                headers={"WWW-Authenticate": "Bearer, APIKey"},
            )