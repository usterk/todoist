import logging
from datetime import datetime
from typing import Optional, Union

from fastapi import Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

# Fix import path from app.db.database to app.database.database
from app.database.database import get_db
from app.models.user import User, ApiKey
from app.auth.auth import get_current_user, get_current_user_from_token

logger = logging.getLogger(__name__)

async def get_current_user_optional(
    request: Request = None,
    token: str = None,
    x_api_key: str = None,
    db: Session = Depends(get_db)
) -> Optional[User]:
    """
    Check for a valid authentication token but don't raise an exception if missing.
    
    This is a variant of get_current_user that returns None instead of raising
    an exception when no valid authentication is provided.
    
    Args:
        request: FastAPI request object
        token: JWT token string (optional)
        x_api_key: API key string (optional)
        db: Database session
        
    Returns:
        User: Authenticated user or None if no valid authentication
    """
    try:
        user_id = await get_current_user(request=request, token=token, x_api_key=x_api_key, db=db)
        return user_id
    except HTTPException:
        return None

def get_current_user_from_api_key(request: Request, db: Session = Depends(get_db)) -> User:
    """
    Extract and validate API key from request headers.
    
    Args:
        request: FastAPI request object
        db: Database session
        
    Returns:
        User: The authenticated user
        
    Raises:
        HTTPException: If API key is missing, invalid, revoked or user not found
    """
    # Extract API key from header
    api_key_value = request.headers.get("x-api-key")
    if not api_key_value:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API key not found",
            headers={"WWW-Authenticate": "ApiKey"},
        )
    
    try:
        # Find API key in database
        api_key = db.query(ApiKey).filter(ApiKey.key_value == api_key_value).first()
        if not api_key:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid API key",
                headers={"WWW-Authenticate": "ApiKey"},
            )
        
        # Check if API key is revoked
        if api_key.revoked:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="API key has been revoked",
                headers={"WWW-Authenticate": "ApiKey"},
            )
        
        # Find associated user
        user = db.query(User).get(api_key.user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found",
                headers={"WWW-Authenticate": "ApiKey"},
            )
        
        # Update last_used timestamp for the API key
        api_key.last_used = datetime.utcnow()
        db.commit()
        
        return user
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing API key: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing API key: {str(e)}"
        )

def get_current_user_with_api_key_fallback(
    request: Request,
    db: Session = Depends(get_db),
    jwt_user: Optional[User] = Depends(get_current_user_optional),
) -> User:
    """
    Attempt to authenticate with JWT first, then fall back to API key if JWT auth fails.
    
    Args:
        request: FastAPI request object
        db: Database session
        jwt_user: User from JWT authentication (optional)
        
    Returns:
        User: Authenticated user
        
    Raises:
        HTTPException: If both JWT and API key authentication fail
    """
    # If JWT authentication succeeded, use that user
    if jwt_user is not None:
        return jwt_user
    
    # Otherwise try API key authentication
    return get_current_user_from_api_key(request, db)

def get_current_user_authenticated(
    request: Request,
    token: str = None,
    x_api_key: str = None,
    db: Session = Depends(get_db)
) -> User:
    """
    Authenticate user with either JWT token or API key.
    
    This combines both authentication methods and allows either to be used.
    JWT token takes precedence if both are provided.
    
    Args:
        request: FastAPI request object
        token: JWT token string (optional)
        x_api_key: API key string (optional)
        db: Database session
        
    Returns:
        User: Authenticated user
        
    Raises:
        HTTPException: If authentication fails
    """
    # Try JWT authentication if token is provided
    if token:
        try:
            return get_current_user(request)
        except HTTPException:
            pass
    
    # Fall back to API key authentication if JWT fails or not provided
    if x_api_key or request.headers.get("x-api-key"):
        try:
            return get_current_user_from_api_key(request, db)
        except HTTPException:
            pass
    
    # If all authentication methods fail, raise unauthorized exception
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Authentication required",
        headers={"WWW-Authenticate": "Bearer or ApiKey"},
    )