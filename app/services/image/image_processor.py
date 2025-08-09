import io
import base64
from PIL import Image, ImageOps, ImageEnhance
from typing import Tuple, Optional
import logging

logger = logging.getLogger(__name__)

class ImageProcessor:
    """
    Modular image processing utilities for wine label analysis.
    """
    
    def __init__(self):
        self.max_dimension = 1920  # Max width/height for processed images
        self.quality = 85  # JPEG quality for compressed images
        
    def resize_image(self, image: Image.Image, max_dimension: Optional[int] = None) -> Image.Image:
        """
        Resize image while maintaining aspect ratio.
        """
        max_dim = max_dimension or self.max_dimension
        
        # Calculate new dimensions
        width, height = image.size
        if max(width, height) <= max_dim:
            return image
            
        if width > height:
            new_width = max_dim
            new_height = int((height * max_dim) / width)
        else:
            new_height = max_dim  
            new_width = int((width * max_dim) / height)
            
        return image.resize((new_width, new_height), Image.Resampling.LANCZOS)
    
    def enhance_for_ocr(self, image: Image.Image) -> Image.Image:
        """
        Enhance image for better OCR accuracy.
        """
        # Convert to RGB if needed
        if image.mode != 'RGB':
            image = image.convert('RGB')
            
        # Auto-orient based on EXIF data
        image = ImageOps.exif_transpose(image)
        
        # Enhance contrast for better text recognition
        enhancer = ImageEnhance.Contrast(image)
        image = enhancer.enhance(1.2)
        
        # Enhance sharpness
        enhancer = ImageEnhance.Sharpness(image)
        image = enhancer.enhance(1.1)
        
        return image
    
    def convert_to_base64(self, image: Image.Image, format: str = 'JPEG') -> str:
        """
        Convert PIL Image to base64 string.
        """
        buffer = io.BytesIO()
        
        # Ensure RGB mode for JPEG
        if format.upper() == 'JPEG' and image.mode != 'RGB':
            image = image.convert('RGB')
            
        image.save(buffer, format=format, quality=self.quality, optimize=True)
        buffer.seek(0)
        
        image_bytes = buffer.read()
        return base64.b64encode(image_bytes).decode('utf-8')
    
    def process_for_analysis(self, image_bytes: bytes) -> Tuple[str, dict]:
        """
        Process image for wine label analysis.
        
        Returns:
            Tuple[str, dict]: (base64_image, metadata)
        """
        try:
            # Load image
            image = Image.open(io.BytesIO(image_bytes))
            original_size = image.size
            
            # Enhance for OCR
            image = self.enhance_for_ocr(image)
            
            # Resize if needed
            image = self.resize_image(image)
            processed_size = image.size
            
            # Convert to base64
            base64_image = self.convert_to_base64(image)
            
            metadata = {
                'original_size': original_size,
                'processed_size': processed_size,
                'format': image.format or 'JPEG',
                'mode': image.mode,
                'enhancement_applied': True
            }
            
            logger.info(f"Image processed: {original_size} -> {processed_size}")
            return base64_image, metadata
            
        except Exception as e:
            logger.error(f"Image processing failed: {e}")
            raise ValueError(f"Failed to process image: {str(e)}")
    
    def create_thumbnail(self, image_bytes: bytes, size: Tuple[int, int] = (200, 200)) -> str:
        """
        Create thumbnail for image preview.
        """
        try:
            image = Image.open(io.BytesIO(image_bytes))
            image.thumbnail(size, Image.Resampling.LANCZOS)
            return self.convert_to_base64(image)
        except Exception as e:
            logger.error(f"Thumbnail creation failed: {e}")
            raise ValueError(f"Failed to create thumbnail: {str(e)}")
    
    def extract_text_regions(self, image: Image.Image) -> Image.Image:
        """
        Placeholder for future text region detection.
        For now, returns the original image.
        """
        # TODO: Implement text region detection using OpenCV or similar
        # This could help focus OCR on wine label text areas
        return image