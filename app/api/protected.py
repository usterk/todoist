"""
Protected endpoints requiring authentication.

These endpoints are used for testing authentication functionality
and serve as examples of secure routes requiring authorization.
"""

from typing import Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session

from app.models.user import User
from app.auth.auth import get_current_user, get_current_user_from_token, get_current_user_from_api_key, oauth2_scheme
from app.database.database import get_db
from app.schemas.user import UserResponse

router = APIRouter(
    prefix="/protected",
    tags=["protected"],
    responses={401: {"description": "Authentication failed"}}
)


@router.get(
    "",
    summary="Protected endpoint",
    description="Endpoint that requires any authentication method (JWT token or API key)",
)
async def protected_endpoint(
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Protected endpoint that requires authentication.
    
    This endpoint can be accessed using either a valid JWT token 
    or a valid API key.
    
    Args:
        current_user: The authenticated user (from token or API key)
        
    Returns:
        dict: Information about the authenticated user
        
    Raises:
        HTTPException: If authentication fails (401 Unauthorized)
    """
    # Sprawdź czy użytkownik istnieje
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return {
        "message": "You have access to this protected endpoint",
        "user_id": current_user.id,
        "username": current_user.username,
        "email": current_user.email,
    }


@router.get(
    "/users/me",
    summary="Get current user information",
    description="Returns information about the authenticated user",
    response_model=UserResponse,
)
async def get_current_user_info(
    current_user: User = Depends(get_current_user)
) -> UserResponse:
    """
    Get current user information.
    
    This endpoint returns information about the currently authenticated user.
    It can be accessed using either a valid JWT token or a valid API key.
    
    Args:
        current_user: The authenticated user
        
    Returns:
        UserResponse: Information about the authenticated user
        
    Raises:
        HTTPException: If authentication fails (401 Unauthorized)
    """
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return current_user


@router.get(
    "/jwt-only",
    summary="JWT-only protected endpoint",
    description="Endpoint that requires JWT token authentication only",
)
async def jwt_only_endpoint(
    request: Request,
    token: Optional[str] = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    JWT-only protected endpoint.
    
    This endpoint can only be accessed using a valid JWT token, 
    API keys are not accepted.
    
    Args:
        request: The request object
        token: JWT token from Authorization header
        db: Database session
        
    Returns:
        dict: Information about the authenticated user
        
    Raises:
        HTTPException: If authentication fails (401 Unauthorized)
    """
    # Check if token exists
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="JWT token required for this endpoint",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    # Try to get user from token
    try:
        user = await get_current_user_from_token(token=token, db=db)
        
        return {
            "message": "You have access to this JWT-only protected endpoint",
            "user_id": user.id,
            "username": user.username,
            "email": user.email,
            "auth_method": "JWT token",
        }
    except HTTPException as e:
        # Przepuszczamy wyjątki HTTPException bez zmian
        raise e
    except Exception as e:
        # Dla innych wyjątków tworzymy specjalną wiadomość
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"JWT token authentication failed: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )


@router.get(
    "/api-key-only",
    summary="API key-only protected endpoint",
    description="Endpoint that requires API key authentication only",
)
async def api_key_only_endpoint(
    api_key_user: User = Depends(get_current_user_from_api_key)
) -> Dict[str, Any]:
    """
    API key-only protected endpoint.
    
    This endpoint can only be accessed using a valid API key,
    JWT tokens are not accepted.
    
    Args:
        api_key_user: The authenticated user (from API key)
        
    Returns:
        dict: Information about the authenticated user
        
    Raises:
        HTTPException: If authentication fails (401 Unauthorized)
    """
    if not api_key_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API key authentication required",
        )
    
    return {
        "message": "You have access to this API key-only protected endpoint",
        "user_id": api_key_user.id,
        "username": api_key_user.username,
        "email": api_key_user.email,
        "auth_method": "API key",
    }