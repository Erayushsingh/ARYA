from PIL import Image
from reportlab.lib.pagesizes import letter, A4, legal
from reportlab.platypus import SimpleDocTemplate, Image as RLImage, PageBreak
from reportlab.lib.units import inch
import os
import uuid
from typing import Dict, Any, List
from app.config import Config

class ImageToPdfConverter:
    def __init__(self):
        self.supported_formats = ['.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.webp']
        self.page_sizes = {
            'A4': A4,
            'LETTER': letter,
            'LEGAL': legal
        }
    
    async def execute(self, parameters: Dict[str, Any], file_paths: List[str]) -> Dict[str, Any]:
        """Convert images to PDF"""
        if not file_paths:
            raise ValueError("No files provided for conversion")
        
        # Extract parameters with defaults
        page_size = parameters.get('page_size', 'A4').upper()
        orientation = parameters.get('orientation', 'portrait').lower()
        margin = parameters.get('margin', 50)
        
        # Validate page size
        if page_size not in self.page_sizes:
            page_size = 'A4'
        
        # Filter image files
        image_files = [f for f in file_paths if self._is_image_file(f)]        
        if not image_files:
            raise ValueError("No valid image files found for conversion")
        
        try:
            # Generate output filename
            output_filename = f"images_to_pdf_{uuid.uuid4().hex[:8]}.pdf"
            output_path = os.path.join(Config.OUTPUT_DIR, output_filename)
            
            # Ensure output directory exists
            os.makedirs(Config.OUTPUT_DIR, exist_ok=True)
            
            # Set up PDF document
            page_size_tuple = self.page_sizes[page_size]
            if orientation == 'landscape':
                page_size_tuple = (page_size_tuple[1], page_size_tuple[0])
            
            pdf_doc = SimpleDocTemplate(
                output_path,
                pagesize=page_size_tuple,
                rightMargin=margin,
                leftMargin=margin,
                topMargin=margin,
                bottomMargin=margin
            )
            
            # Calculate available space
            page_width = page_size_tuple[0] - 2 * margin
            page_height = page_size_tuple[1] - 2 * margin
            
            story = []
            
            for i, image_path in enumerate(image_files):
                try:
                    # Open image to get dimensions
                    with Image.open(image_path) as img:
                        img_width, img_height = img.size
                        
                        # Calculate scaling to fit page
                        width_ratio = page_width / img_width
                        height_ratio = page_height / img_height
                        scale_ratio = min(width_ratio, height_ratio, 1.0)  # Don't upscale
                        
                        # Calculate final dimensions
                        final_width = img_width * scale_ratio
                        final_height = img_height * scale_ratio
                        
                        # Convert image to RGB if necessary
                        if img.mode in ('RGBA', 'P'):
                            # Create a temporary RGB image
                            temp_path = f"temp_{uuid.uuid4().hex[:8]}.jpg"
                            temp_full_path = os.path.join(Config.OUTPUT_DIR, temp_path)
                            
                            rgb_img = img.convert('RGB')
                            rgb_img.save(temp_full_path, 'JPEG', quality=95)
                            
                            # Add to PDF
                            rl_image = RLImage(temp_full_path, width=final_width, height=final_height)
                            story.append(rl_image)
                            
                            # Clean up temp file
                            os.remove(temp_full_path)
                        else:
                            # Add image directly to PDF
                            rl_image = RLImage(image_path, width=final_width, height=final_height)
                            story.append(rl_image)
                    
                    # Add page break between images (except for the last one)
                    if i < len(image_files) - 1:
                        story.append(PageBreak())
                        
                except Exception as e:
                    print(f"Warning: Could not process image {image_path}: {str(e)}")
                    continue
            
            if not story:
                raise ValueError("No images could be processed")
            
            # Build PDF
            pdf_doc.build(story)
            
            return {
                "output_path": os.path.basename(output_path),
                "total_files_processed": len(image_files),
                "conversion_settings": {
                    "page_size": page_size,
                    "orientation": orientation,
                    "margin": margin
                }
            }
            
        except Exception as e:
            raise ValueError(f"Error converting images to PDF: {str(e)}")
    
    def _is_image_file(self, file_path: str) -> bool:
        """Check if file is a supported image format"""
        _, ext = os.path.splitext(file_path.lower())
        return ext in self.supported_formats
