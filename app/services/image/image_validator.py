import io
from PIL import Image
from typing import Optional, Tuple
import logging

logger = logging.getLogger(__name__)

# Configuration
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
MIN_IMAGE_SIZE = (100, 100)
MAX_IMAGE_SIZE = (4096, 4096)
ALLOWED_FORMATS = {'JPEG', 'PNG', 'WEBP'}
ALLOWED_MIME_TYPES = {'image/jpeg', 'image/png', 'image/webp'}

class ImageValidationError(Exception):
    pass

def validate_image_file(file_content: bytes, filename: str, content_type: str) -> dict:
    """
    Validate uploaded image file for security and format compliance.
    
    Returns:
        dict: Validation result with image info
    
    Raises:
        ImageValidationError: If validation fails
    """
    # Check file size
    if len(file_content) > MAX_FILE_SIZE:
        raise ImageValidationError(f"File too large. Maximum size is {MAX_FILE_SIZE // (1024*1024)}MB")
    
    if len(file_content) == 0:
        raise ImageValidationError("Empty file")
    
    # Check MIME type
    if content_type not in ALLOWED_MIME_TYPES:
        raise ImageValidationError(f"Invalid file type. Allowed types: {', '.join(ALLOWED_MIME_TYPES)}")
    
    try:
        # Load and validate image
        image = Image.open(io.BytesIO(file_content))
        
        # Verify it's actually an image
        image.verify()
        
        # Reload image (verify() can only be called once)
        image = Image.open(io.BytesIO(file_content))
        
        # Check format
        if image.format not in ALLOWED_FORMATS:
            raise ImageValidationError(f"Invalid image format. Allowed formats: {', '.join(ALLOWED_FORMATS)}")
        
        # Check dimensions
        width, height = image.size
        if width < MIN_IMAGE_SIZE[0] or height < MIN_IMAGE_SIZE[1]:
            raise ImageValidationError(f"Image too small. Minimum size: {MIN_IMAGE_SIZE[0]}x{MIN_IMAGE_SIZE[1]}")
        
        if width > MAX_IMAGE_SIZE[0] or height > MAX_IMAGE_SIZE[1]:
            raise ImageValidationError(f"Image too large. Maximum size: {MAX_IMAGE_SIZE[0]}x{MAX_IMAGE_SIZE[1]}")
        
        # Return validation info
        return {
            'valid': True,
            'format': image.format,
            'size': (width, height),
            'mode': image.mode,
            'file_size': len(file_content),
            'has_transparency': image.mode in ('RGBA', 'LA', 'P')
        }
        
    except Exception as e:
        if isinstance(e, ImageValidationError):
            raise
        logger.error(f"Image validation failed for {filename}: {e}")
        raise ImageValidationError("Invalid or corrupted image file")

def sanitize_filename(filename: str) -> str:
    """
    Sanitize uploaded filename to prevent path traversal attacks.
    """
    import re
    import os
    
    # Get just the filename without path
    filename = os.path.basename(filename)
    
    # Remove or replace dangerous characters
    filename = re.sub(r'[^\w\-_\.]', '_', filename)
    
    # Ensure reasonable length
    if len(filename) > 100:
        name, ext = os.path.splitext(filename)
        filename = name[:90] + ext
    
    return filename or "uploaded_image.jpg"