"""
API endpoints for user management.
"""

from typing import List, Optional, Union
from fastapi import APIRouter, Depends, HTTPException, Path, Query, status
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.user import User, ApiKey
from app.schemas.user import UserResponse, UserUpdate
from app.auth.auth import get_current_user, get_password_hash

router = APIRouter(
    prefix="/users",
    tags=["users"],
    responses={
        401: {"description": "Authentication failed"},
        403: {"description": "Insufficient permissions"},
        404: {"description": "User not found"}
    }
)


@router.get(
    "",
    response_model=List[UserResponse],
    summary="Get all users",
    description="Returns a paginated list of all users. Requires authentication.",
)
async def get_users(
    skip: int = Query(0, ge=0, description="Number of users to skip"),
    limit: int = Query(100, ge=1, le=100, description="Maximum number of users to return"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> List[UserResponse]:
    """
    Get a paginated list of all users.
    
    Args:
        skip: Number of users to skip (pagination offset)
        limit: Maximum number of users to return (pagination limit)
        current_user: The authenticated user
        db: Database session
        
    Returns:
        List[UserResponse]: List of user information objects
    """
    users = db.query(User).offset(skip).limit(limit).all()
    return users


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Get current user information",
    description="Returns information about the currently authenticated user.",
    responses={
        200: {"description": "User details retrieved successfully"}
    }
)
async def get_current_user_info(
    current_user: User = Depends(get_current_user)
) -> UserResponse:
    """
    Get information about the currently authenticated user.
    
    Args:
        current_user: The authenticated user
        
    Returns:
        UserResponse: Current user information
    """
    return current_user


@router.get(
    "/{user_id}",
    response_model=UserResponse,
    summary="Get a specific user",
    description="Returns details for a specific user by ID. Requires authentication.",
    responses={
        200: {"description": "User details retrieved successfully"},
        404: {"description": "User not found"}
    }
)
async def get_user(
    user_id: int = Path(..., title="The ID of the user to retrieve", ge=1),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> UserResponse:
    """
    Get details for a specific user by ID.
    
    Args:
        user_id: ID of the user to retrieve
        current_user: The authenticated user
        db: Database session
        
    Returns:
        UserResponse: User information
        
    Raises:
        HTTPException: If user not found (404)
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} not found"
        )
    return user


@router.put(
    "/{user_id}",
    response_model=UserResponse,
    summary="Update a user",
    description="Updates a user's information. Users can only update their own information unless they have admin privileges.",
    responses={
        200: {"description": "User updated successfully"},
        400: {"description": "Invalid input or username/email conflict"},
        403: {"description": "Not authorized to update this user"},
        404: {"description": "User not found"}
    }
)
async def update_user(
    user_data: UserUpdate,
    user_id: int = Path(..., title="The ID of the user to update", ge=1),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> UserResponse:
    """
    Update a user's information.
    
    Users can only update their own information unless they have admin privileges.
    If email or username is updated, checks for conflicts with existing users.
    
    Args:
        user_data: Updated user data (username, email, password)
        user_id: ID of the user to update
        current_user: The authenticated user
        db: Database session
        
    Returns:
        UserResponse: Updated user information
        
    Raises:
        HTTPException: 
            - If user not found (404)
            - If not authorized to update user (403)
            - If username or email conflicts with existing user (400)
    """
    # Check if user exists
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} not found"
        )
    
    # Authorization check - users can only update their own information
    # TODO: Add admin role check once role-based access is implemented
    if current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this user"
        )
    
    # Check for username/email conflicts if being updated
    if user_data.username and user_data.username != user.username:
        existing_user = db.query(User).filter(User.username == user_data.username).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already taken"
            )
    
    if user_data.email and user_data.email != user.email:
        existing_user = db.query(User).filter(User.email == user_data.email).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
    
    # Update user fields
    if user_data.username:
        user.username = user_data.username
    
    if user_data.email:
        user.email = user_data.email
    
    # Hash password if provided
    if user_data.password:
        user.password_hash = get_password_hash(user_data.password)
    
    # Save changes to database
    try:
        db.commit()
        db.refresh(user)
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update user: {str(e)}"
        )
    
    return user


@router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a user",
    description="Deletes a user account. Users can only delete their own account unless they have admin privileges.",
    responses={
        204: {"description": "User deleted successfully"},
        403: {"description": "Not authorized to delete this user"},
        404: {"description": "User not found"}
    }
)
async def delete_user(
    user_id: int = Path(..., title="The ID of the user to delete", ge=1),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete a user account.
    
    Users can only delete their own account unless they have admin privileges.
    
    Args:
        user_id: ID of the user to delete
        current_user: The authenticated user
        db: Database session
        
    Returns:
        None: 204 No Content on success
        
    Raises:
        HTTPException: 
            - If user not found (404)
            - If not authorized to delete user (403)
    """
    # Check if user exists
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} not found"
        )
    
    # Authorization check - users can only delete their own account
    # TODO: Add admin role check once role-based access is implemented
    if current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this user"
        )
    
    # Delete user from database
    try:
        # Delete associated API keys first to maintain referential integrity
        db.query(ApiKey).filter(ApiKey.user_id == user_id).delete(synchronize_session=False)
        
        # Delete the user
        db.delete(user)
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete user: {str(e)}"
        )
    
    return None
