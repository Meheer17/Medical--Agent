from fastapi import Depends, HTTPException, status
from starlette.requests import Request
from database import get_db
from models import UserRole
from auth import JWTUtil

class DictWrapper(dict):
    """Dictionary subclass enabling attribute-style access (e.g. obj.key)"""
    def __getattr__(self, name):
        try:
            return self[name]
        except KeyError:
            raise AttributeError(f"'DictWrapper' object has no attribute '{name}'")

    def __setattr__(self, name, value):
        self[name] = value

async def get_current_user(
    request: Request,
    db = Depends(get_db)
) -> DictWrapper:
    """
    Dependency to get current authenticated user from JWT token
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
    
    user_dict = await db.users.find_one({"email": email})
    
    if not user_dict:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )
    
    user = DictWrapper(user_dict)
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is deactivated",
        )
    
    return user

async def get_current_active_user(
    current_user: DictWrapper = Depends(get_current_user),
) -> DictWrapper:
    """Ensure current user is active"""
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is deactivated",
        )
    return current_user

def get_user_with_role(required_roles: list[UserRole]):
    """Factory function to create a dependency that checks user role"""
    async def verify_role(
        current_user: DictWrapper = Depends(get_current_active_user),
    ) -> DictWrapper:
        if current_user.role not in required_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"User role '{current_user.role}' is not authorized. Required roles: {', '.join([r.value for r in required_roles])}",
            )
        return current_user
    
    return verify_role

async def get_doctor_user(
    current_user: DictWrapper = Depends(get_user_with_role([UserRole.DOCTOR])),
) -> DictWrapper:
    return current_user

async def get_patient_user(
    current_user: DictWrapper = Depends(get_user_with_role([UserRole.PATIENT])),
) -> DictWrapper:
    return current_user

async def get_lab_user(
    current_user: DictWrapper = Depends(get_user_with_role([UserRole.LAB])),
) -> DictWrapper:
    return current_user
