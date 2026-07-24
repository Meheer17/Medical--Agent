"""
File storage utility for handling PDF uploads and downloads
"""
import os
import uuid
from pathlib import Path
from datetime import datetime
from fastapi import HTTPException, status

# Define storage directory
STORAGE_DIR = Path("reports")
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50 MB
ALLOWED_MIME_TYPES = ["application/pdf"]
ALLOWED_EXTENSIONS = [".pdf"]


class FileStorage:
    """Utility class for file operations"""
    
    @staticmethod
    def ensure_storage_directory():
        """Create storage directory if it doesn't exist"""
        STORAGE_DIR.mkdir(exist_ok=True)
    
    @staticmethod
    def generate_file_name(original_filename: str) -> str:
        """
        Generate a unique file name to prevent conflicts
        
        Args:
            original_filename: Original file name from upload
        
        Returns:
            Unique file name with timestamp and UUID
        """
        # Get file extension
        _, ext = os.path.splitext(original_filename)
        
        # Generate unique name: timestamp_uuid.ext
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        unique_id = str(uuid.uuid4())[:8]
        file_name = f"{timestamp}_{unique_id}{ext}"
        
        return file_name
    
    @staticmethod
    def validate_file(file_content: bytes, filename: str, mime_type: str):
        """
        Validate uploaded file
        
        Args:
            file_content: File content bytes
            filename: Original file name
            mime_type: MIME type of file
        
        Raises:
            HTTPException: If validation fails
        """
        # Check file extension
        _, ext = os.path.splitext(filename)
        if ext.lower() not in ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid file extension. Allowed: {', '.join(ALLOWED_EXTENSIONS)}"
            )
        
        # Check MIME type
        if mime_type not in ALLOWED_MIME_TYPES:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid MIME type. Allowed: {', '.join(ALLOWED_MIME_TYPES)}"
            )
        
        # Check file size
        if len(file_content) > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"File too large. Maximum size: {MAX_FILE_SIZE / (1024 * 1024)}MB"
            )
        
        # Check if file is not empty
        if len(file_content) == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File is empty"
            )
    
    @staticmethod
    def save_file(file_content: bytes, file_name: str) -> str:
        """
        Save file to storage directory
        
        Args:
            file_content: File content bytes
            file_name: File name to save as
        
        Returns:
            Relative file path
        
        Raises:
            HTTPException: If save operation fails
        """
        try:
            FileStorage.ensure_storage_directory()
            file_path = STORAGE_DIR / file_name
            
            with open(file_path, "wb") as f:
                f.write(file_content)
            
            return str(file_path)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to save file: {str(e)}"
            )
    
    @staticmethod
    def get_file(file_path: str) -> bytes:
        """
        Retrieve file from storage
        
        Args:
            file_path: Path to file
        
        Returns:
            File content bytes
        
        Raises:
            HTTPException: If file not found or read fails
        """
        try:
            # Prevent directory traversal attacks
            file_path = file_path.replace("..", "").lstrip("/")
            full_path = STORAGE_DIR / file_path
            
            # Verify file exists and is within STORAGE_DIR
            if not full_path.exists() or not full_path.is_file():
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="File not found"
                )
            
            # Verify file is within storage directory
            if not str(full_path.resolve()).startswith(str(STORAGE_DIR.resolve())):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Access denied"
                )
            
            with open(full_path, "rb") as f:
                return f.read()
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to read file: {str(e)}"
            )
    
    @staticmethod
    def delete_file(file_path: str) -> bool:
        """
        Delete file from storage
        
        Args:
            file_path: Path to file
        
        Returns:
            True if deleted successfully
        
        Raises:
            HTTPException: If delete operation fails
        """
        try:
            # Prevent directory traversal attacks
            file_path = file_path.replace("..", "").lstrip("/")
            full_path = STORAGE_DIR / file_path
            
            # Verify file exists and is within STORAGE_DIR
            if not full_path.exists():
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="File not found"
                )
            
            # Verify file is within storage directory
            if not str(full_path.resolve()).startswith(str(STORAGE_DIR.resolve())):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Access denied"
                )
            
            full_path.unlink()
            return True
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to delete file: {str(e)}"
            )
