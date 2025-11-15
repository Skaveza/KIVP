"""
File Upload Utilities
"""

import os
import uuid
from pathlib import Path
from typing import Optional
from fastapi import UploadFile, HTTPException
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)


def get_upload_path(user_id: str) -> Path:
    """Get upload directory path for a user"""
    upload_dir = Path(settings.UPLOAD_DIR) / str(user_id)
    upload_dir.mkdir(parents=True, exist_ok=True)
    return upload_dir


def validate_file_extension(filename: str) -> bool:
    """Validate file extension"""
    extension = filename.rsplit('.', 1)[-1].lower()
    return extension in settings.allowed_extensions_list


def validate_file_size(file_size: int) -> bool:
    """Validate file size"""
    return file_size <= settings.MAX_FILE_SIZE


async def save_upload_file(
    file: UploadFile,
    user_id: str
) -> tuple[str, str, int]:
    """
    Save uploaded file and return (filename, filepath, size).
    """
    
    # Validate extension
    if not validate_file_extension(file.filename):
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type. Allowed: {', '.join(settings.allowed_extensions_list)}"
        )
    
    # Read file to check size
    contents = await file.read()
    file_size = len(contents)
    
    # Validate size
    if not validate_file_size(file_size):
        raise HTTPException(
            status_code=400,
            detail=f"File too large. Maximum size: {settings.MAX_FILE_SIZE / 1024 / 1024:.1f}MB"
        )
    
    # Generate unique filename
    extension = file.filename.rsplit('.', 1)[-1].lower()
    unique_filename = f"{uuid.uuid4()}.{extension}"
    
    # Get upload path
    upload_dir = get_upload_path(user_id)
    file_path = upload_dir / unique_filename
    
    # Save file
    try:
        with open(file_path, 'wb') as f:
            f.write(contents)
        
        logger.info(f"Saved file: {file_path} ({file_size} bytes)")
        
        return file.filename, str(file_path), file_size
    
    except Exception as e:
        logger.error(f"Failed to save file: {e}")
        raise HTTPException(status_code=500, detail="Failed to save file")


def delete_file(file_path: str) -> bool:
    """Delete a file from storage"""
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
            logger.info(f"Deleted file: {file_path}")
            return True
        return False
    except Exception as e:
        logger.error(f"Failed to delete file {file_path}: {e}")
        return False
