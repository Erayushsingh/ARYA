from docx import Document
from reportlab.lib.pagesizes import letter, A4, legal
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.units import inch
import os
import uuid
from typing import Dict, Any, List
from app.config import Config

class WordToPdfConverter:
    def __init__(self):
        self.supported_formats = ['.docx']
        self.page_sizes = {
            'A4': A4,
            'LETTER': letter,
            'LEGAL': legal
        }
    
    async def execute(self, parameters: Dict[str, Any], file_paths: List[str]) -> Dict[str, Any]:
        """Convert Word documents to PDF"""
        if not file_paths:
            raise ValueError("No files provided for conversion")
        
        # Extract parameters with defaults
        page_size = parameters.get('page_size', 'A4').upper()
        orientation = parameters.get('orientation', 'portrait').lower()
        margin = parameters.get('margin', 50)
          # Validate page size
        if page_size not in self.page_sizes:
            page_size = 'A4'
        
        converted_files = []
        
        for file_path in file_paths:
            if not self._is_word_file(file_path):
                continue
            
            try:
                # Read Word document
                doc = Document(file_path)
                
                # Generate output filename
                original_name = os.path.splitext(os.path.basename(file_path))[0]
                output_filename = f"{original_name}_converted_{uuid.uuid4().hex[:8]}.pdf"
                output_path = os.path.join(Config.OUTPUT_DIR, output_filename)
                
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
                
                # Build content
                story = []
                styles = getSampleStyleSheet()
                
                # Create custom styles
                title_style = ParagraphStyle(
                    'CustomTitle',
                    parent=styles['Heading1'],
                    fontSize=16,
                    spaceAfter=30,
                )
                
                normal_style = ParagraphStyle(
                    'CustomNormal',
                    parent=styles['Normal'],
                    fontSize=11,
                    spaceAfter=12,
                )
                
                # Process Word document content
                for paragraph in doc.paragraphs:
                    if paragraph.text.strip():
                        # Determine style based on content
                        if len(paragraph.text) < 100 and paragraph.text.isupper():
                            # Likely a title
                            p = Paragraph(paragraph.text, title_style)
                        else:
                            p = Paragraph(paragraph.text, normal_style)
                        
                        story.append(p)
                        story.append(Spacer(1, 6))
                
                # Build PDF
                pdf_doc.build(story)
                converted_files.append(output_path)
                
            except Exception as e:
                raise ValueError(f"Error converting Word document {file_path}: {str(e)}")
        
        if not converted_files:
            raise ValueError("No valid Word documents found for conversion")
        
        return {
            "output_path": os.path.basename(converted_files[0]),
            "total_files_processed": len(converted_files),
            "conversion_settings": {
                "page_size": page_size,
                "orientation": orientation,
                "margin": margin
            }
        }
    
    def _is_word_file(self, file_path: str) -> bool:
        """Check if file is a supported Word document format"""
        _, ext = os.path.splitext(file_path.lower())
        return ext in self.supported_formats
