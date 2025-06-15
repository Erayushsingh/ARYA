import os
import uuid
from typing import Dict, Any, List
from app.client.sarvam_client import SarvamClient
from app.config import Config

class TextToSpeechConverter:
    """Convert text to speech using Sarvam AI"""
    
    def __init__(self):
        self.supported_formats = ['.wav', '.mp3']  # Output formats
        self.sarvam_client = SarvamClient()
    
    async def execute(self, parameters: Dict[str, Any], file_paths: List[str]) -> Dict[str, Any]:
        """Execute text-to-speech conversion"""
        
        # Get text from parameters or extract from files
        text_to_convert = parameters.get('text', '')
        
        # If no text provided, try to extract from uploaded text files
        if not text_to_convert and file_paths:
            text_to_convert = await self._extract_text_from_files(file_paths)
        
        if not text_to_convert:
            raise ValueError("No text provided for text-to-speech conversion. Please provide text in the prompt or upload a text file.")
        
        # Extract parameters
        language = parameters.get('language', 'hindi').lower()
        output_format = parameters.get('format', 'wav').lower()
        
        # Validate output format
        if f'.{output_format}' not in self.supported_formats:
            output_format = 'wav'  # Default to wav
        
        try:
            # Generate unique filename
            output_filename = f"text_to_speech_{uuid.uuid4().hex[:8]}.{output_format}"
            output_path = os.path.join(Config.OUTPUT_DIR, output_filename)
            
            # Ensure output directory exists
            os.makedirs(Config.OUTPUT_DIR, exist_ok=True)
            
            print(f"Converting text to speech...")
            print(f"Text length: {len(text_to_convert)} characters")
            print(f"Language: {language}")
            print(f"Output format: {output_format}")
            
            # Perform text-to-speech conversion
            result = await self.sarvam_client.text_to_speech(
                text=text_to_convert,
                language=language,
                output_path=output_path
            )
            
            if result['success']:
                # Create a summary file with conversion details
                summary_filename = f"text_to_speech_summary_{uuid.uuid4().hex[:8]}.txt"
                summary_path = os.path.join(Config.OUTPUT_DIR, summary_filename)
                
                with open(summary_path, 'w', encoding='utf-8') as f:
                    f.write("Text-to-Speech Conversion Summary\n")
                    f.write("=================================\n\n")
                    f.write(f"Language: {result['language']} ({result['language_code']})\n")
                    f.write(f"Output Format: {output_format}\n")
                    f.write(f"Audio File: {output_filename}\n")
                    f.write(f"Text Length: {len(text_to_convert)} characters\n\n")
                    f.write("Original Text:\n")
                    f.write("-" * 50 + "\n")
                    f.write(text_to_convert)
                    f.write("\n" + "-" * 50 + "\n")
                    f.write("\n✅ Conversion completed successfully!")
                
                return {
                    "success": True,
                    "message": f"Successfully converted text to speech in {result['language']}",
                    "output_path": output_filename,
                    "summary_path": summary_filename,
                    "audio_file": output_filename,
                    "language": result['language'],
                    "language_code": result['language_code'],
                    "text_length": len(text_to_convert),
                    "format": output_format
                }
            else:
                raise Exception(f"Text-to-speech conversion failed: {result['error']}")
                
        except Exception as e:
            raise Exception(f"Error in text-to-speech conversion: {str(e)}")
    
    async def _extract_text_from_files(self, file_paths: List[str]) -> str:
        """Extract text from uploaded text files"""
        extracted_text = []
        
        for file_path in file_paths:
            try:
                # Check if it's a text file
                file_ext = os.path.splitext(file_path)[1].lower()
                if file_ext in ['.txt', '.md', '.py', '.js', '.html', '.css', '.json', '.xml']:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        extracted_text.append(f"Content from {os.path.basename(file_path)}:\n{content}\n")
                elif file_ext == '.docx':
                    # Try to extract from docx if python-docx is available
                    try:
                        from docx import Document
                        doc = Document(file_path)
                        content = '\n'.join([paragraph.text for paragraph in doc.paragraphs])
                        extracted_text.append(f"Content from {os.path.basename(file_path)}:\n{content}\n")
                    except ImportError:
                        print(f"Warning: Cannot extract text from {file_path} - python-docx not available")
            except Exception as e:
                print(f"Warning: Could not extract text from {file_path}: {str(e)}")
        
        return '\n\n'.join(extracted_text)
    
    def get_supported_languages(self) -> Dict[str, str]:
        """Get supported languages"""
        return self.sarvam_client.get_supported_languages()
    
    def get_supported_formats(self) -> List[str]:
        """Get supported output audio formats"""
        return self.supported_formats.copy()
