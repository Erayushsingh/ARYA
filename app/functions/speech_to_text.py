import os
import uuid
from typing import Dict, Any, List
from app.client.sarvam_client import SarvamClient
from app.config import Config

class SpeechToTextConverter:
    """Convert speech/audio files to text using Sarvam AI"""
    
    def __init__(self):
        self.supported_formats = ['.wav', '.mp3', '.m4a', '.flac', '.aac']
        self.sarvam_client = SarvamClient()
    
    async def execute(self, parameters: Dict[str, Any], file_paths: List[str]) -> Dict[str, Any]:
        """Execute speech-to-text conversion"""
        if not file_paths:
            raise ValueError("No audio files provided for speech-to-text conversion")
        
        # Filter audio files
        audio_files = []
        for file_path in file_paths:
            file_ext = os.path.splitext(file_path)[1].lower()
            if file_ext in self.supported_formats:
                audio_files.append(file_path)
        
        if not audio_files:
            raise ValueError(f"No supported audio files found. Supported formats: {self.supported_formats}")
        
        # Extract parameters
        language = parameters.get('language', 'hindi').lower()
        model = parameters.get('model', 'saarika:v2')
        
        try:
            results = []
            all_transcripts = []
            
            for audio_file in audio_files:
                print(f"Processing audio file: {os.path.basename(audio_file)}")
                
                # Perform speech-to-text conversion
                result = await self.sarvam_client.speech_to_text(
                    audio_file_path=audio_file,
                    language=language,
                    model=model
                )
                
                results.append({
                    'file': os.path.basename(audio_file),
                    'success': result['success'],
                    'transcribed_text': result['transcribed_text'],
                    'error': result.get('error', None)
                })
                
                if result['success']:
                    all_transcripts.append(f"File: {os.path.basename(audio_file)}")
                    all_transcripts.append(f"Transcript: {result['transcribed_text']}")
                    all_transcripts.append("---")
            
            # Create output text file with all transcriptions
            output_filename = f"speech_to_text_{uuid.uuid4().hex[:8]}.txt"
            output_path = os.path.join(Config.OUTPUT_DIR, output_filename)
              # Ensure output directory exists
            os.makedirs(Config.OUTPUT_DIR, exist_ok=True)
            
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write("Speech-to-Text Transcription Results\n")
                f.write("=====================================\n\n")
                f.write(f"Language: {language}\n")
                f.write(f"Model: {model}\n")
                f.write(f"Total files processed: {len(audio_files)}\n\n")
                
                for result in results:
                    f.write(f"File: {result['file']}\n")
                    if result['success']:
                        f.write(f"Status: ✅ Success\n")
                        f.write(f"Transcript: {result['transcribed_text']}\n")
                    else:
                        f.write(f"Status: ❌ Failed\n")
                        f.write(f"Error: {result['error']}\n")
                    f.write("\n" + "="*50 + "\n\n")
            
            # Count successful conversions
            successful_count = sum(1 for r in results if r['success'])
            
            return {
                "success": True,
                "message": f"Successfully transcribed {successful_count} out of {len(audio_files)} audio files",
                "output_path": output_filename,
                "transcription_results": results,
                "language": language,
                "model": model
            }
            
        except Exception as e:
            raise Exception(f"Error in speech-to-text conversion: {str(e)}")
    
    def get_supported_languages(self) -> Dict[str, str]:
        """Get supported languages"""
        return self.sarvam_client.get_supported_languages()
    
    def get_supported_formats(self) -> List[str]:
        """Get supported audio formats"""
        return self.supported_formats.copy()
