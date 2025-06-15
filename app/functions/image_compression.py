from PIL import Image
import os
import uuid
from typing import Dict, Any, List
from app.config import Config

class ImageCompressor:
    def __init__(self):
        self.supported_formats = ['.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.webp']
    
    async def execute(self, parameters: Dict[str, Any], file_paths: List[str]) -> Dict[str, Any]:
        if not file_paths:
            raise ValueError("No files provided for compression")
        
        os.makedirs(Config.OUTPUT_DIR, exist_ok=True)
        
        quality = parameters.get('quality', 60)
        max_width = parameters.get('max_width', 1600)
        max_height = parameters.get('max_height', 1200)
        output_format = parameters.get('format', 'AUTO').upper()
        
        quality = max(25, min(85, int(quality)))
        
        compressed_files = []
        compression_results = []
        
        for file_path in file_paths:
            if not self._is_image_file(file_path):
                continue
            
            try:
                original_size = os.path.getsize(file_path)
                
                with Image.open(file_path) as img:
                    original_width, original_height = img.size
                    
                    if original_width > max_width or original_height > max_height:
                        img = self._resize_image(img, max_width, max_height)
                    
                    if output_format == 'AUTO':
                        if img.mode == 'RGBA' or 'transparency' in img.info:
                            best_format = 'PNG'
                        else:
                            best_format = 'JPEG'
                    else:
                        best_format = output_format
                    
                    if best_format == 'JPEG' and img.mode in ('RGBA', 'P', 'LA'):
                        background = Image.new('RGB', img.size, (255, 255, 255))
                        if img.mode == 'P':
                            img = img.convert('RGBA')
                        if img.mode in ('RGBA', 'LA'):
                            background.paste(img, mask=img.split()[-1])
                        img = background
                    
                    original_name = os.path.splitext(os.path.basename(file_path))[0]
                    output_filename = f"{original_name}_compressed_{uuid.uuid4().hex[:8]}.{best_format.lower()}"
                    output_path = os.path.join(Config.OUTPUT_DIR, output_filename)
                    
                    if best_format == 'JPEG':
                        img.save(output_path, format='JPEG', quality=quality, optimize=True)
                    elif best_format == 'PNG':
                        img.save(output_path, format='PNG', optimize=True, compress_level=9)
                    elif best_format == 'WEBP':
                        img.save(output_path, format='WEBP', quality=quality, optimize=True)
                    
                    compressed_size = os.path.getsize(output_path)
                    compression_ratio = ((original_size - compressed_size) / original_size) * 100
                    
                    compressed_files.append(output_path)
                    compression_results.append({
                        'original_file': os.path.basename(file_path),
                        'compressed_file': output_filename,
                        'original_size': self._format_size(original_size),
                        'compressed_size': self._format_size(compressed_size),
                        'compression_ratio': f"{compression_ratio:.1f}%",
                        'format': best_format
                    })
                    
            except Exception as e:
                original_name = os.path.splitext(os.path.basename(file_path))[0]
                error_filename = f"{original_name}_error_{uuid.uuid4().hex[:8]}.txt"
                error_path = os.path.join(Config.OUTPUT_DIR, error_filename)
                
                with open(error_path, 'w') as error_file:
                    error_file.write(f"Error compressing {file_path}: {str(e)}")
                
                compressed_files.append(error_path)
        
        if not compressed_files:
            raise ValueError("No valid image files were processed")
        
        return {
            'message': f"Successfully compressed {len(compression_results)} image(s)",
            'output_path': compressed_files[0] if len(compressed_files) == 1 else None,
            'compressed_files': compressed_files,
            'results': compression_results
        }
    
    def _resize_image(self, img: Image.Image, max_width: float, max_height: float) -> Image.Image:
        current_width, current_height = img.size
        max_width = int(max_width)
        max_height = int(max_height)
        
        width_ratio = max_width / current_width if current_width > max_width else 1
        height_ratio = max_height / current_height if current_height > max_height else 1
        scale_factor = min(width_ratio, height_ratio)
        
        if scale_factor < 1:
            new_width = max(int(current_width * scale_factor), 200)
            new_height = max(int(current_height * scale_factor), 200)
            return img.resize((new_width, new_height), Image.Resampling.LANCZOS)
        
        return img
    
    def _is_image_file(self, file_path: str) -> bool:
        _, ext = os.path.splitext(file_path.lower())
        return ext in self.supported_formats
    
    def _format_size(self, size_bytes: int) -> str:
        if size_bytes == 0:
            return "0B"
        
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f}{unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f}TB"
