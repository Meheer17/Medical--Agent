from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from database import get_db
from models import User
from schemas import (
    UserRegister, UserLogin, Token, UserResponse, ErrorResponse,
    DoctorProfile, PatientProfile, LabProfile
)
from auth import PasswordUtil, JWTUtil
from dependencies import get_current_active_user

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
async def signup(user_data: UserRegister, db: Session = Depends(get_db)):
    """
    Register a new user (Signup)
    
    - **email**: Valid email address (unique)
    - **username**: Username for login (3-50 chars, unique)
    - **password**: Strong password (minimum 8 chars)
    - **full_name**: Optional full name
    """
    try:
        # Check if email already exists
        existing_email = db.query(User).filter(User.email == user_data.email).first()
        if existing_email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered",
            )
        
        # Check if username already exists
        existing_username = db.query(User).filter(User.username == user_data.username).first()
        if existing_username:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already taken",
            )
        
        # Create new user
        hashed_password = PasswordUtil.hash_password(user_data.password)
        
        db_user = User(
            email=user_data.email,
            username=user_data.username,
            hashed_password=hashed_password,
            full_name=user_data.full_name,
            role=user_data.role,
        )
        
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        
        return db_user
        
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Error creating user. Please try again.",
        )

@router.post(
    "/login",
    response_model=Token,
    responses={
        401: {"model": ErrorResponse, "description": "Invalid credentials"},
        404: {"model": ErrorResponse, "description": "User not found"}
    }
)
async def login(user_data: UserLogin, db: Session = Depends(get_db)):
    """
    User login - returns JWT access token
    
    - **email**: Registered email address
    - **password**: Account password
    
    Returns access token and user information
    """
    # Find user by email
    user = db.query(User).filter(User.email == user_data.email).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
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
    
    # Generate JWT token with role
    access_token = JWTUtil.create_access_token(data={
        "sub": user.email,
        "role": user.role.value
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
async def refresh_token(token: str, db: Session = Depends(get_db)):
    """
    Refresh JWT access token
    
    - **token**: Current valid JWT token
    
    Returns new access token
    """
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
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User account is deactivated",
        )
    
    # Generate new token with role
    new_access_token = JWTUtil.create_access_token(data={
        "sub": user.email,
        "role": user.role.value
    })
    
    return {
        "access_token": new_access_token,
        "token_type": "bearer",
        "user": user
    }

@router.get("/profile", tags=["authentication"])
async def get_profile(current_user: User = Depends(get_current_active_user)):
    """
    Get user profile based on role
    
    Returns different profile information based on user role:
    - **doctor**: Doctor profile with license and specialization info
    - **patient**: Patient profile with verification status
    - **lab**: Lab profile with lab-specific info
    """
    if current_user.role.value == "doctor":
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
    elif current_user.role.value == "patient":
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
    elif current_user.role.value == "lab":
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
