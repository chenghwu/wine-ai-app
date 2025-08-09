import pytest
import io
from PIL import Image
from app.services.image.image_validator import validate_image_file, ImageValidationError
from app.services.image.image_processor import ImageProcessor

class TestImageValidation:
    
    def create_test_image(self, width=500, height=500, format='JPEG'):
        """Create a test image for validation tests."""
        image = Image.new('RGB', (width, height), color='white')
        buffer = io.BytesIO()
        image.save(buffer, format=format)
        return buffer.getvalue()
    
    def test_validate_valid_image(self):
        """Test validation of a valid image."""
        image_bytes = self.create_test_image()
        result = validate_image_file(image_bytes, 'test.jpg', 'image/jpeg')
        
        assert result['valid'] is True
        assert result['format'] == 'JPEG'
        assert result['size'] == (500, 500)
        assert result['file_size'] == len(image_bytes)
    
    def test_validate_empty_file(self):
        """Test validation of empty file."""
        with pytest.raises(ImageValidationError, match="Empty file"):
            validate_image_file(b'', 'test.jpg', 'image/jpeg')
    
    def test_validate_invalid_mime_type(self):
        """Test validation with invalid MIME type."""
        image_bytes = self.create_test_image()
        with pytest.raises(ImageValidationError, match="Invalid file type"):
            validate_image_file(image_bytes, 'test.txt', 'text/plain')
    
    def test_validate_too_small_image(self):
        """Test validation of image that's too small."""
        image_bytes = self.create_test_image(width=50, height=50)
        with pytest.raises(ImageValidationError, match="Image too small"):
            validate_image_file(image_bytes, 'test.jpg', 'image/jpeg')
    
    def test_validate_corrupted_image(self):
        """Test validation of corrupted image data."""
        with pytest.raises(ImageValidationError, match="Invalid or corrupted"):
            validate_image_file(b'not an image', 'test.jpg', 'image/jpeg')

class TestImageProcessor:
    
    def create_test_image(self, width=1000, height=800):
        """Create a test PIL image."""
        return Image.new('RGB', (width, height), color='red')
    
    def test_resize_image(self):
        """Test image resizing functionality."""
        processor = ImageProcessor()
        image = self.create_test_image(width=2000, height=1500)
        
        resized = processor.resize_image(image, max_dimension=1920)
        
        # Should maintain aspect ratio
        assert max(resized.size) == 1920
        assert resized.size[0] / resized.size[1] == 2000 / 1500
    
    def test_resize_small_image_unchanged(self):
        """Test that small images are not upscaled."""
        processor = ImageProcessor()
        image = self.create_test_image(width=500, height=400)
        
        resized = processor.resize_image(image, max_dimension=1920)
        
        # Should remain unchanged
        assert resized.size == (500, 400)
    
    def test_convert_to_base64(self):
        """Test base64 conversion."""
        processor = ImageProcessor()
        image = self.create_test_image()
        
        base64_str = processor.convert_to_base64(image)
        
        assert isinstance(base64_str, str)
        assert len(base64_str) > 0
        # Base64 strings are typically much longer than original dimensions
        assert len(base64_str) > 100
    
    def test_process_for_analysis(self):
        """Test complete image processing pipeline."""
        processor = ImageProcessor()
        
        # Create test image bytes
        image = self.create_test_image(width=2500, height=2000)
        buffer = io.BytesIO()
        image.save(buffer, format='JPEG')
        image_bytes = buffer.getvalue()
        
        base64_result, metadata = processor.process_for_analysis(image_bytes)
        
        assert isinstance(base64_result, str)
        assert len(base64_result) > 0
        assert metadata['original_size'] == (2500, 2000)
        assert metadata['enhancement_applied'] is True
        assert max(metadata['processed_size']) <= 1920  # Should be resized
    
    def test_create_thumbnail(self):
        """Test thumbnail creation."""
        processor = ImageProcessor()
        
        # Create test image bytes
        image = self.create_test_image()
        buffer = io.BytesIO()
        image.save(buffer, format='JPEG')
        image_bytes = buffer.getvalue()
        
        thumbnail_b64 = processor.create_thumbnail(image_bytes, size=(100, 100))
        
        assert isinstance(thumbnail_b64, str)
        assert len(thumbnail_b64) > 0