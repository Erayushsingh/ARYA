from PIL import Image
import os
import uuid
from typing import Dict, Any, List

class ImageCompressor:
    def __init__(self):
        self.supported_formats = ['.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.webp']
    
    async def execute(self, parameters: Dict[str, Any], file_paths: List[str]) -> Dict[str, Any]:
        """Compress image files based on parameters"""
        if not file_paths:
            raise ValueError("No files provided for compression")
        
        # Extract parameters with defaults
        quality = parameters.get('quality', 85)
        max_width = parameters.get('max_width')
        max_height = parameters.get('max_height')
        output_format = parameters.get('format', 'JPEG').upper()
        
        # Validate quality
        quality = max(1, min(100, int(quality)))
        
        compressed_files = []
        
        for file_path in file_paths:
            if not self._is_image_file(file_path):
                continue
            
            try:
                # Open and process image
                with Image.open(file_path) as img:
                    # Convert to RGB if necessary for JPEG
                    if output_format == 'JPEG' and img.mode in ('RGBA', 'P'):
                        img = img.convert('RGB')
                    
                    # Resize if dimensions specified
                    if max_width or max_height:
                        img = self._resize_image(img, max_width, max_height)
                    
                    # Generate output filename
                    original_name = os.path.splitext(os.path.basename(file_path))[0]
                    output_filename = f"{original_name}_compressed_{uuid.uuid4().hex[:8]}.{output_format.lower()}"
                    output_path = os.path.join("app/file_handler/outputs", output_filename)
                    
                    # Save compressed image
                    save_kwargs = {'format': output_format}
                    if output_format == 'JPEG':
                        save_kwargs['quality'] = quality
                        save_kwargs['optimize'] = True
                    elif output_format == 'PNG':
                        save_kwargs['optimize'] = True
                    elif output_format == 'WEBP':
                        save_kwargs['quality'] = quality
                        save_kwargs['method'] = 6
                    
                    img.save(output_path, **save_kwargs)
                    compressed_files.append(output_path)
                    
            except Exception as e:
                raise ValueError(f"Error processing image {file_path}: {str(e)}")
        
        if not compressed_files:
            raise ValueError("No valid image files found for compression")
        
        # Return the first compressed file (or could return all)
        return {
            "output_path": os.path.basename(compressed_files[0]),
            "total_files_processed": len(compressed_files),
            "compression_settings": {
                "quality": quality,
                "format": output_format,
                "max_width": max_width,
                "max_height": max_height
            }
        }
    
    def _is_image_file(self, file_path: str) -> bool:
        """Check if file is a supported image format"""
        _, ext = os.path.splitext(file_path.lower())
        return ext in self.supported_formats
    
    def _resize_image(self, img: Image.Image, max_width: int = None, max_height: int = None) -> Image.Image:
        """Resize image while maintaining aspect ratio"""
        original_width, original_height = img.size
        
        # Calculate new dimensions
        if max_width and max_height:
            # Fit within both constraints
            ratio = min(max_width / original_width, max_height / original_height)
        elif max_width:
            ratio = max_width / original_width
        elif max_height:
            ratio = max_height / original_height
        else:
            return img
        
        # Only resize if we're making it smaller
        if ratio < 1:
            new_width = int(original_width * ratio)
            new_height = int(original_height * ratio)
            return img.resize((new_width, new_height), Image.Resampling.LANCZOS)
        
        return img
