from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status

from database import get_db, get_next_sequence_value
from schemas import (
    UserRegister, UserLogin, Token, UserResponse, ErrorResponse,
    DoctorProfile, PatientProfile, LabProfile
)
from auth import PasswordUtil, JWTUtil
from dependencies import get_current_active_user, DictWrapper

router = APIRouter(prefix="/api/auth", tags=["authentication"])

@router.post(
    "/signup",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        400: {"model": ErrorResponse, "description": "User already exists or invalid input"},
        201: {"model": UserResponse}
    }
)
async def signup(user_data: UserRegister, db = Depends(get_db)):
    """
    Register a new user (Signup)
    """
    # Check if email already exists
    existing_email = await db.users.find_one({"email": user_data.email})
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )
    
    # Check if username already exists
    existing_username = await db.users.find_one({"username": user_data.username})
    if existing_username:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already taken",
        )
    
    # Generate sequential int ID
    user_id = await get_next_sequence_value("users")
    hashed_password = PasswordUtil.hash_password(user_data.password)
    now = datetime.now(timezone.utc)

    user_doc = {
        "id": user_id,
        "email": user_data.email,
        "username": user_data.username,
        "hashed_password": hashed_password,
        "full_name": user_data.full_name,
        "role": user_data.role.value if hasattr(user_data.role, 'value') else user_data.role,
        "doctor_code": None,
        "linked_doctor_id": None,
        "phone": None,
        "address": None,
        "is_active": True,
        "is_verified": False,
        "created_at": now,
        "updated_at": now,
    }

    await db.users.insert_one(user_doc)
    return user_doc

@router.post(
    "/login",
    response_model=Token,
    responses={
        401: {"model": ErrorResponse, "description": "Invalid credentials"},
        404: {"model": ErrorResponse, "description": "User not found"}
    }
)
async def login(user_data: UserLogin, db = Depends(get_db)):
    """
    User login - returns JWT access token
    """
    user_doc = await db.users.find_one({"email": user_data.email})
    if not user_doc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user = DictWrapper(user_doc)
    
    # Verify password
    if not PasswordUtil.verify_password(user_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Check if user is active
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User account is deactivated",
        )
    
    role_str = user.role.value if hasattr(user.role, 'value') else str(user.role)
    access_token = JWTUtil.create_access_token(data={
        "sub": user.email,
        "role": role_str
    })
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user
    }

@router.post(
    "/refresh-token",
    response_model=Token,
    responses={
        401: {"model": ErrorResponse, "description": "Invalid token"}
    }
)
async def refresh_token(token: str, db = Depends(get_db)):
    """
    Refresh JWT access token
    """
    try:
        email = JWTUtil.get_email_from_token(token)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user_doc = await db.users.find_one({"email": email})
    if not user_doc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )
    
    user = DictWrapper(user_doc)
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User account is deactivated",
        )
    
    role_str = user.role.value if hasattr(user.role, 'value') else str(user.role)
    new_access_token = JWTUtil.create_access_token(data={
        "sub": user.email,
        "role": role_str
    })
    
    return {
        "access_token": new_access_token,
        "token_type": "bearer",
        "user": user
    }

@router.get("/profile", tags=["authentication"])
async def get_profile(current_user: DictWrapper = Depends(get_current_active_user)):
    """
    Get user profile based on role
    """
    role_val = current_user.role.value if hasattr(current_user.role, 'value') else str(current_user.role)
    role_lower = role_val.lower()

    if role_lower == "doctor":
        return {
            "role": "doctor",
            "profile": DoctorProfile(
                id=current_user.id,
                email=current_user.email,
                username=current_user.username,
                full_name=current_user.full_name,
                role=current_user.role,
                is_active=current_user.is_active,
                created_at=current_user.created_at,
            )
        }
    elif role_lower == "patient":
        return {
            "role": "patient",
            "profile": PatientProfile(
                id=current_user.id,
                email=current_user.email,
                username=current_user.username,
                full_name=current_user.full_name,
                role=current_user.role,
                is_active=current_user.is_active,
                is_verified=current_user.is_verified,
                created_at=current_user.created_at,
            )
        }
    elif role_lower == "lab":
        return {
            "role": "lab",
            "profile": LabProfile(
                id=current_user.id,
                email=current_user.email,
                username=current_user.username,
                full_name=current_user.full_name,
                role=current_user.role,
                is_active=current_user.is_active,
                created_at=current_user.created_at,
            )
        }
