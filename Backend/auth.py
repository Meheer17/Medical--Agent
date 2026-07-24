from datetime import datetime, timedelta, timezone
from typing import Optional
from jose import JWTError, jwt
import bcrypt
from config import settings

class PasswordUtil:
    """Utility class for password operations"""
    
    @staticmethod
    def hash_password(password: str) -> str:
        """Hash a password using bcrypt"""
        salt = bcrypt.gensalt(rounds=12)
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')
    
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verify a plain password against a hashed password"""
        return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

class JWTUtil:
    """Utility class for JWT token operations"""
    
    @staticmethod
    def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
        """
        Create a JWT access token
        
        Args:
            data: Dictionary containing claims (e.g., {"sub": "user_email", "role": "patient"})
            expires_delta: Optional custom expiration time
        
        Returns:
            Encoded JWT token
        """
        to_encode = data.copy()
        
        if expires_delta:
            expire = datetime.now(timezone.utc) + expires_delta
        else:
            expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        
        to_encode.update({"exp": expire})
        
        encoded_jwt = jwt.encode(
            to_encode,
            settings.SECRET_KEY,
            algorithm=settings.ALGORITHM
        )
        return encoded_jwt
    
    @staticmethod
    def verify_token(token: str) -> dict:
        """
        Verify and decode a JWT token
        
        Args:
            token: JWT token string
        
        Returns:
            Decoded token payload as dictionary
        
        Raises:
            JWTError: If token is invalid or expired
        """
        try:
            payload = jwt.decode(
                token,
                settings.SECRET_KEY,
                algorithms=[settings.ALGORITHM]
            )
            return payload
        except JWTError:
            raise JWTError("Invalid token")
    
    @staticmethod
    def get_email_from_token(token: str) -> str:
        """
        Extract email from token
        
        Args:
            token: JWT token string
        
        Returns:
            Email address from token
        
        Raises:
            JWTError: If token is invalid
        """
        payload = JWTUtil.verify_token(token)
        email: str = payload.get("sub")
        if email is None:
            raise JWTError("Could not validate credentials")
        return email
    
    @staticmethod
    def get_role_from_token(token: str) -> str:
        """
        Extract role from token
        
        Args:
            token: JWT token string
        
        Returns:
            Role from token
        
        Raises:
            JWTError: If token is invalid
        """
        payload = JWTUtil.verify_token(token)
        role: str = payload.get("role")
        if role is None:
            raise JWTError("Could not validate role")
        return role
