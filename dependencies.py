from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer
from starlette.requests import Request
from sqlalchemy.orm import Session

from database import get_db
from models import User, UserRole
from auth import JWTUtil

security = HTTPBearer()

async def get_current_user(
    request: Request,
    db: Session = Depends(get_db)
) -> User:
    """
    Dependency to get current authenticated user from JWT token
    
    Args:
        request: HTTP request
        db: Database session
    
    Returns:
        Current user object
    
    Raises:
        HTTPException: If token is invalid or user not found
    """
    auth_header = request.headers.get("Authorization")
    
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid authorization header",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    token = auth_header.split(" ")[1]
    
    try:
        email = JWTUtil.get_email_from_token(token)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user = db.query(User).filter(User.email == email).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is deactivated",
        )
    
    return user

async def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    Dependency to ensure current user is active
    
    Args:
        current_user: Current authenticated user
    
    Returns:
        Current active user
    
    Raises:
        HTTPException: If user is not active
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is deactivated",
        )
    return current_user

def get_user_with_role(required_roles: list[UserRole]):
    """
    Factory function to create a dependency that checks user role
    
    Args:
        required_roles: List of allowed roles
    
    Returns:
        Async dependency function
    """
    async def verify_role(
        current_user: User = Depends(get_current_active_user),
    ) -> User:
        """
        Verify that current user has one of the required roles
        
        Args:
            current_user: Current authenticated user
        
        Returns:
            Current user if role is authorized
        
        Raises:
            HTTPException: If user role is not authorized
        """
        if current_user.role not in required_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"User role '{current_user.role}' is not authorized. Required roles: {', '.join([r.value for r in required_roles])}",
            )
        return current_user
    
    return verify_role

# Specific role dependencies
async def get_doctor_user(
    current_user: User = Depends(get_user_with_role([UserRole.DOCTOR])),
) -> User:
    """Dependency for doctor-only endpoints"""
    return current_user

async def get_patient_user(
    current_user: User = Depends(get_user_with_role([UserRole.PATIENT])),
) -> User:
    """Dependency for patient-only endpoints"""
    return current_user

async def get_lab_user(
    current_user: User = Depends(get_user_with_role([UserRole.LAB])),
) -> User:
    """Dependency for lab-only endpoints"""
    return current_user

