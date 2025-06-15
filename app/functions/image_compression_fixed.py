from PIL import Image
import os
import uuid
from typing import Dict, Any, List
from app.config import Config

class ImageCompressor:
    def __init__(self):
        self.supported_formats = ['.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.webp']
    
    async def execute(self, parameters: Dict[str, Any], file_paths: List[str]) -> Dict[str, Any]:
        """Compress image files with guaranteed size reduction"""
        if not file_paths:
            raise ValueError("No files provided for compression")
        
        # Ensure output directory exists
        os.makedirs(Config.OUTPUT_DIR, exist_ok=True)
        
        # Extract parameters with aggressive defaults for compression
        quality = parameters.get('quality', 65)  # Lower default for better compression
        max_width = parameters.get('max_width', 1920)  # Default max width
        max_height = parameters.get('max_height', 1080)  # Default max height
        output_format = parameters.get('format', 'AUTO').upper()
        
        # Validate quality (keep reasonable range for compression)
        quality = max(20, min(90, int(quality)))
        
        compressed_files = []
        compression_stats = []
        
        for file_path in file_paths:
            if not self._is_image_file(file_path):
                continue
            
            try:
                # Get original file size
                original_size = os.path.getsize(file_path)
                
                # Open and process image
                with Image.open(file_path) as img:
                    original_width, original_height = img.size
                    
                    # Determine best output format for maximum compression
                    if output_format == 'AUTO':
                        # For photos: JPEG is almost always smaller
                        # For graphics with transparency: PNG
                        if img.mode == 'RGBA' or 'transparency' in img.info:
                            best_format = 'PNG'
                        elif img.mode == 'P' and len(img.getcolors() or []) < 64:
                            best_format = 'PNG'  # Small palette
                        else:
                            best_format = 'JPEG'  # Best for photos and most images
                    else:
                        best_format = output_format
                    
                    # Convert image to optimal mode for the format
                    processed_img = self._optimize_image_for_format(img, best_format)
                    
                    # Always resize for compression - this is key for size reduction!
                    processed_img = self._resize_for_compression(processed_img, max_width, max_height)
                    
                    # Generate output filename
                    original_name = os.path.splitext(os.path.basename(file_path))[0]
                    output_filename = f"{original_name}_compressed_{uuid.uuid4().hex[:8]}.{best_format.lower()}"
                    output_path = os.path.join(Config.OUTPUT_DIR, output_filename)
                    
                    # Save with maximum compression settings
                    self._save_with_max_compression(processed_img, output_path, best_format, quality)
                    
                    # Verify we actually reduced the size
                    compressed_size = os.path.getsize(output_path)
                    
                    # If compressed file is larger, try more aggressive compression
                    if compressed_size >= original_size:
                        processed_img = self._apply_aggressive_compression(processed_img, max_width // 2, max_height // 2)
                        self._save_with_max_compression(processed_img, output_path, 'JPEG', quality // 2)
                        compressed_size = os.path.getsize(output_path)
                    
                    compression_ratio = (1 - compressed_size / original_size) * 100
                    
                    compressed_files.append(output_path)
                    compression_stats.append({
                        'original_size': original_size,
                        'compressed_size': compressed_size,
                        'compression_ratio': compression_ratio,
                        'original_dimensions': f"{original_width}x{original_height}",
                        'new_dimensions': f"{processed_img.width}x{processed_img.height}",
                        'format': best_format,
                        'size_reduction': self._format_file_size(original_size - compressed_size)
                    })
                    
            except Exception as e:
                raise ValueError(f"Error processing image {file_path}: {str(e)}")
        
        if not compressed_files:
            raise ValueError("No valid image files found for compression")
        
        # Calculate compression statistics
        avg_compression = sum(stat['compression_ratio'] for stat in compression_stats) / len(compression_stats)
        total_original_size = sum(stat['original_size'] for stat in compression_stats)
        total_compressed_size = sum(stat['compressed_size'] for stat in compression_stats)
        total_savings = total_original_size - total_compressed_size
        
        return {
            "output_path": os.path.basename(compressed_files[0]),
            "total_files_processed": len(compressed_files),
            "compression_results": {
                "average_compression_percentage": f"{avg_compression:.1f}%",
                "total_size_before": self._format_file_size(total_original_size),
                "total_size_after": self._format_file_size(total_compressed_size),
                "total_space_saved": self._format_file_size(total_savings),
                "settings_used": {
                    "quality": quality,
                    "max_dimensions": f"{max_width}x{max_height}",
                    "format_strategy": output_format
                }
            }
        }
    
    def _optimize_image_for_format(self, img: Image.Image, target_format: str) -> Image.Image:
        """Optimize image mode for target format"""
        if target_format == 'JPEG':
            if img.mode in ('RGBA', 'LA', 'P'):
                # Create white background for transparency
                if img.mode == 'P':
                    img = img.convert('RGBA')
                background = Image.new('RGB', img.size, (255, 255, 255))
                if img.mode in ('RGBA', 'LA'):
                    background.paste(img, mask=img.split()[-1])
                else:
                    background.paste(img)
                return background
            elif img.mode != 'RGB':
                return img.convert('RGB')
        elif target_format == 'PNG':
            if img.mode not in ('RGBA', 'RGB', 'P', 'L'):
                return img.convert('RGBA')
        
        return img
    
    def _resize_for_compression(self, img: Image.Image, max_width: int, max_height: int) -> Image.Image:
        """Aggressively resize image for compression"""
        original_width, original_height = img.size
        
        # Always reduce very large images
        if original_width > max_width or original_height > max_height:
            ratio = min(max_width / original_width, max_height / original_height)
        elif original_width > 1600 or original_height > 1200:
            # Reduce large images even if under max limits
            ratio = min(1600 / original_width, 1200 / original_height)
        else:
            # For smaller images, still reduce slightly for compression
            ratio = 0.9
        
        new_width = int(original_width * ratio)
        new_height = int(original_height * ratio)
        
        # Ensure minimum reasonable size
        new_width = max(new_width, 200)
        new_height = max(new_height, 200)
        
        return img.resize((new_width, new_height), Image.Resampling.LANCZOS)
    
    def _apply_aggressive_compression(self, img: Image.Image, max_width: int, max_height: int) -> Image.Image:
        """Apply very aggressive compression when normal compression fails"""
        # Reduce dimensions more aggressively
        ratio = min(max_width / img.width, max_height / img.height)
        if ratio < 1:
            new_width = int(img.width * ratio)
            new_height = int(img.height * ratio)
            img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
        
        return img
    
    def _save_with_max_compression(self, img: Image.Image, output_path: str, format_type: str, quality: int):
        """Save image with maximum compression settings"""
        save_kwargs = {'format': format_type}
        
        if format_type == 'JPEG':
            save_kwargs.update({
                'quality': quality,
                'optimize': True,
                'progressive': True,
                'subsampling': 2,  # More aggressive subsampling
            })
        elif format_type == 'PNG':
            save_kwargs.update({
                'optimize': True,
                'compress_level': 9,  # Maximum PNG compression
            })
        elif format_type == 'WEBP':
            save_kwargs.update({
                'quality': quality,
                'method': 6,  # Best compression method
                'optimize': True,
                'lossless': False,
            })
        
        img.save(output_path, **save_kwargs)
    
    def _is_image_file(self, file_path: str) -> bool:
        """Check if file is a supported image format"""
        _, ext = os.path.splitext(file_path.lower())
        return ext in self.supported_formats
    
    def _format_file_size(self, size_bytes: int) -> str:
        """Format file size in human readable format"""
        if size_bytes == 0:
            return "0B"
        size_names = ["B", "KB", "MB", "GB"]
        i = 0
        while size_bytes >= 1024.0 and i < len(size_names) - 1:
            size_bytes /= 1024.0
            i += 1
        return f"{size_bytes:.1f}{size_names[i]}"
