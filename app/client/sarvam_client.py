from sarvamai import SarvamAI
import os
import asyncio
import base64
from typing import Dict, Any, List
from app.config import Config

class SarvamClient:
    """Client for Sarvam AI services"""
    
    def __init__(self):
        """Initialize Sarvam AI client"""
        self.client = SarvamAI(
            api_subscription_key=Config.SARVAM_API_KEY
        )
        
        # Supported languages for speech-to-text
        self.supported_languages = {
            'hindi': 'hi-IN',
            'gujarati': 'gu-IN',
            'punjabi': 'pa-IN',
            'marathi': 'mr-IN',
            'bengali': 'bn-IN',
            'tamil': 'ta-IN',
            'telugu': 'te-IN',
            'kannada': 'kn-IN',
            'malayalam': 'ml-IN',
            'odia': 'or-IN',
            'assamese': 'as-IN',
            'english': 'en-IN'
        }        # Supported audio formats
        self.supported_audio_formats = ['.wav', '.mp3', '.m4a', '.flac', '.aac']
        self.experimental_formats = ['.webm', '.ogg']  # May work but not officially supported
    async def speech_to_text(self, audio_file_path: str, language: str = 'auto', model: str = 'saarika:v2') -> Dict[str, Any]:
        """
        Convert speech to text using Sarvam AI with automatic language detection
        
        Args:
            audio_file_path: Path to the audio file
            language: Language name (e.g., 'hindi', 'gujarati', 'english', 'auto' for detection)
            model: Model to use for transcription
            
        Returns:
            Dictionary with transcription results including detected language in native script
        """
        try:
            print(f"🎤 Starting speech-to-text transcription...")
            print(f"📁 Audio file: {audio_file_path}")
            print(f"🌐 Language setting: {language}")
            print(f"🤖 Model: {model}")
            
            # Check if file exists
            if not os.path.exists(audio_file_path):
                raise FileNotFoundError(f"Audio file not found: {audio_file_path}")
            
            # Check file format
            file_ext = os.path.splitext(audio_file_path)[1].lower()
            if file_ext not in self.supported_audio_formats:
                if file_ext in self.experimental_formats:
                    print(f"⚠️ Warning: Using experimental format {file_ext}. May not work reliably.")
                else:
                    raise ValueError(f"Unsupported audio format: {file_ext}. Supported formats: {self.supported_audio_formats}")
            
            # Handle automatic language detection
            if language.lower() == 'auto':
                print("🔍 Auto-detecting language and transcribing in native script...")
                return await self._auto_detect_and_transcribe(audio_file_path, model)
            else:
                # Use specified language
                language_code = self.supported_languages.get(language.lower(), 'hi-IN')
                print(f"Using specified language: {language} ({language_code})")
                return await self._transcribe_with_language(audio_file_path, language_code, model, language)
                
        except Exception as e:
            print(f"❌ Error in speech-to-text: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'transcribed_text': "",
                'text': "",
                'language': 'unknown',
                'language_code': 'unknown',
                'confidence': 0.0,
                'audio_file': audio_file_path
            }
    
    async def _auto_detect_and_transcribe(self, audio_file_path: str, model: str) -> Dict[str, Any]:
        """
        Auto-detect language and transcribe in native script
        """
        # Languages to try in priority order with their native names
        detection_languages = [
            ('hindi', 'hi-IN', 'हिंदी'),
            ('gujarati', 'gu-IN', 'ગુજરાતી'), 
            ('tamil', 'ta-IN', 'தமிழ்'),
            ('telugu', 'te-IN', 'తెలుగు'),
            ('bengali', 'bn-IN', 'বাংলা'),
            ('marathi', 'mr-IN', 'मराठी'),
            ('punjabi', 'pa-IN', 'ਪੰਜਾਬੀ'),
            ('kannada', 'kn-IN', 'ಕನ್ನಡ'),
            ('malayalam', 'ml-IN', 'മലയാളം'),
            ('odia', 'or-IN', 'ଓଡ଼ିଆ'),
            ('assamese', 'as-IN', 'অসমীয়া'),
            ('english', 'en-IN', 'English')
        ]
        
        best_result = None
        best_confidence = 0.0
        
        print(f"🔍 Trying {len(detection_languages)} languages for detection...")
        
        for lang_name, lang_code, lang_display in detection_languages:
            try:
                print(f"   🧪 Testing {lang_display} ({lang_code})...")
                
                with open(audio_file_path, "rb") as audio_file:
                    response = self.client.speech_to_text.transcribe(
                        file=audio_file,
                        model=model,
                        language_code=lang_code
                    )
                
                # Extract transcription
                transcribed_text = self._extract_text_from_response(response)
                
                # Calculate confidence based on text characteristics
                confidence = self._calculate_language_confidence(transcribed_text, lang_name, lang_code)
                
                print(f"   📝 Result: '{transcribed_text[:50]}...' (confidence: {confidence:.3f})")
                
                if confidence > best_confidence and transcribed_text.strip():
                    best_confidence = confidence
                    best_result = {
                        'success': True,
                        'transcribed_text': transcribed_text,
                        'text': transcribed_text,
                        'language': lang_display,
                        'language_code': lang_code,
                        'confidence': confidence,
                        'detected_script': self._detect_script(transcribed_text),
                        'audio_file': audio_file_path
                    }
                    print(f"   ✅ New best result: {lang_display} (confidence: {confidence:.3f})")
                
            except Exception as e:
                print(f"   ❌ Failed for {lang_display}: {str(e)}")
                continue
        
        if best_result:
            print(f"🎯 Final detection: {best_result['language']} with confidence {best_result['confidence']:.3f}")
            print(f"📝 Native script transcript: {best_result['transcribed_text']}")
            return best_result
        else:
            print("❌ No successful transcription found")
            return {
                'success': False,
                'error': 'Failed to detect language or transcribe audio',
                'transcribed_text': "",
                'text': "",
                'language': 'Unknown',
                'language_code': 'unknown',
                'confidence': 0.0,
                'audio_file': audio_file_path
            }
    
    async def _transcribe_with_language(self, audio_file_path: str, language_code: str, model: str, language_name: str) -> Dict[str, Any]:
        """
        Transcribe with a specific language
        """
        try:
            with open(audio_file_path, "rb") as audio_file:
                response = self.client.speech_to_text.transcribe(
                    file=audio_file,
                    model=model,
                    language_code=language_code
                )
            
            transcribed_text = self._extract_text_from_response(response)
            
            return {
                'success': True,
                'transcribed_text': transcribed_text,
                'text': transcribed_text,
                'language': language_name,
                'language_code': language_code,
                'confidence': getattr(response, 'confidence', 0.9),
                'detected_script': self._detect_script(transcribed_text),
                'audio_file': audio_file_path
            }
            
        except Exception as e:
            raise Exception(f"Transcription failed for {language_name}: {str(e)}")
    
    def _extract_text_from_response(self, response) -> str:
        """Extract text from Sarvam AI response"""
        if hasattr(response, 'transcript'):
            return response.transcript
        elif hasattr(response, 'text'):
            return response.text
        elif isinstance(response, dict):
            return response.get('transcript', response.get('text', str(response)))
        else:
            return str(response)
    
    def _calculate_language_confidence(self, text: str, language: str, language_code: str) -> float:
        """
        Calculate confidence based on script characteristics and text quality
        """
        if not text or not text.strip():
            return 0.0
        
        base_confidence = 0.5  # Base confidence
        script_bonus = 0.0
        
        # Check for language-specific scripts (this is key for native script detection)
        if language_code == 'hi-IN' and any('\u0900' <= char <= '\u097F' for char in text):  # Devanagari
            script_bonus = 0.4
            print(f"   ✨ Detected Hindi Devanagari script in: {text[:30]}...")
        elif language_code == 'gu-IN' and any('\u0A80' <= char <= '\u0AFF' for char in text):  # Gujarati
            script_bonus = 0.4
            print(f"   ✨ Detected Gujarati script in: {text[:30]}...")
        elif language_code == 'ta-IN' and any('\u0B80' <= char <= '\u0BFF' for char in text):  # Tamil
            script_bonus = 0.4
            print(f"   ✨ Detected Tamil script in: {text[:30]}...")
        elif language_code == 'te-IN' and any('\u0C00' <= char <= '\u0C7F' for char in text):  # Telugu
            script_bonus = 0.4
            print(f"   ✨ Detected Telugu script in: {text[:30]}...")
        elif language_code == 'bn-IN' and any('\u0980' <= char <= '\u09FF' for char in text):  # Bengali
            script_bonus = 0.4
            print(f"   ✨ Detected Bengali script in: {text[:30]}...")
        elif language_code == 'mr-IN' and any('\u0900' <= char <= '\u097F' for char in text):  # Marathi (Devanagari)
            script_bonus = 0.3
            print(f"   ✨ Detected Marathi Devanagari script in: {text[:30]}...")
        elif language_code == 'pa-IN' and any('\u0A00' <= char <= '\u0A7F' for char in text):  # Punjabi
            script_bonus = 0.4
            print(f"   ✨ Detected Punjabi script in: {text[:30]}...")
        elif language_code == 'kn-IN' and any('\u0C80' <= char <= '\u0CFF' for char in text):  # Kannada
            script_bonus = 0.4
            print(f"   ✨ Detected Kannada script in: {text[:30]}...")
        elif language_code == 'ml-IN' and any('\u0D00' <= char <= '\u0D7F' for char in text):  # Malayalam
            script_bonus = 0.4
            print(f"   ✨ Detected Malayalam script in: {text[:30]}...")
        elif language_code == 'en-IN' and text.isascii():  # English
            script_bonus = 0.2
            print(f"   ✨ Detected English script in: {text[:30]}...")
        
        # Length bonus (longer text is generally more reliable)
        length_bonus = min(0.1, len(text.strip()) / 100)
        
        final_confidence = min(1.0, base_confidence + script_bonus + length_bonus)
        return final_confidence
    
    def _detect_script(self, text: str) -> str:
        """Detect the script used in the text"""
        if not text:
            return "Unknown"
        
        # Check for different scripts
        if any('\u0900' <= char <= '\u097F' for char in text):
            return "Devanagari (Hindi/Marathi)"
        elif any('\u0A80' <= char <= '\u0AFF' for char in text):
            return "Gujarati"
        elif any('\u0B80' <= char <= '\u0BFF' for char in text):
            return "Tamil"
        elif any('\u0C00' <= char <= '\u0C7F' for char in text):
            return "Telugu"
        elif any('\u0980' <= char <= '\u09FF' for char in text):
            return "Bengali"
        elif any('\u0A00' <= char <= '\u0A7F' for char in text):
            return "Punjabi"
        elif any('\u0C80' <= char <= '\u0CFF' for char in text):
            return "Kannada"
        elif any('\u0D00' <= char <= '\u0D7F' for char in text):
            return "Malayalam"
        elif any('\u0B00' <= char <= '\u0B7F' for char in text):
            return "Odia"
        elif text.isascii():
            return "Latin (English)"
        else:
            return "Mixed/Other"
    
    async def text_to_speech(self, text: str, language: str = 'hindi', output_path: str = None) -> Dict[str, Any]:
        """
        Convert text to speech using Sarvam AI
        
        Args:
            text: Text to convert to speech
            language: Language for speech synthesis
            output_path: Path to save the audio file (optional)
            
        Returns:
            Dictionary with TTS results
        """
        try:
            # Get language code
            language_code = self.supported_languages.get(language.lower(), 'hi-IN')
            
            print(f"Converting text to speech...")
            print(f"Text: {text[:50]}{'...' if len(text) > 50 else ''}")
            print(f"Language: {language} ({language_code})")
              # Perform text-to-speech conversion
            response = self.client.text_to_speech.convert(
                text=text,
                target_language_code=language_code
            )
            
            print(f"Text-to-speech conversion completed successfully")
            
            # Handle the response - SarvamAI returns a response with 'audios' attribute containing base64 strings
            audio_data = None
            if hasattr(response, 'audios') and response.audios:
                # Get the first audio from the list (there's usually only one)
                base64_audio = response.audios[0]
                # Decode base64 to bytes
                audio_data = base64.b64decode(base64_audio)
                print(f"Decoded audio data from base64 ({len(base64_audio)} chars -> {len(audio_data)} bytes)")
            elif hasattr(response, 'audio_data'):
                audio_data = response.audio_data
            elif hasattr(response, 'audio'):
                audio_data = response.audio
            elif isinstance(response, dict):
                if 'audios' in response and response['audios']:
                    base64_audio = response['audios'][0]
                    audio_data = base64.b64decode(base64_audio)
                else:
                    audio_data = response.get('audio_data', response.get('audio', None))
            else:
                # If response is bytes directly
                audio_data = response if isinstance(response, bytes) else None
            
            if audio_data is None:
                raise ValueError("No audio data received from Sarvam AI API")
            
            # Save audio file if output_path is provided
            saved_file = None
            if output_path:
                with open(output_path, 'wb') as f:
                    f.write(audio_data)
                saved_file = output_path
                print(f"Audio saved to: {output_path} ({len(audio_data)} bytes)")
            
            return {
                'success': True,
                'audio_data': audio_data,
                'language': language,
                'language_code': language_code,
                'text': text,
                'output_file': saved_file,
                'raw_response': response
            }
            
        except Exception as e:
            print(f"Error in text-to-speech: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'audio_data': None,
                'language': language,
                'language_code': language_code if 'language_code' in locals() else 'unknown',
                'text': text,
                'output_file': None            }
    
    def get_supported_languages(self) -> Dict[str, str]:
        """Get list of supported languages"""
        return self.supported_languages.copy()
    
    def get_supported_audio_formats(self) -> List[str]:
        """Get list of supported audio formats"""
        return self.supported_audio_formats.copy()
    
    async def translate_text(self, text: str, source_language: str = "auto", target_language: str = "hi-IN", speaker_gender: str = "Male") -> Dict[str, Any]:
        """
        Translate text between languages using Sarvam AI
        
        Args:
            text: Text to translate
            source_language: Source language code (e.g., 'en-IN', 'auto')
            target_language: Target language code (e.g., 'hi-IN', 'gu-IN')
            speaker_gender: Speaker gender for TTS compatibility
            
        Returns:
            Dictionary with translation results
        """
        try:
            # Use Sarvam AI translation API
            response = self.client.text.translate(
                input=text,
                source_language_code=source_language,
                target_language_code=target_language,
                speaker_gender=speaker_gender
            )
            
            # Process the response
            if hasattr(response, 'translated_text') or hasattr(response, 'translation'):
                translated_text = getattr(response, 'translated_text', None) or getattr(response, 'translation', None)
                return {
                    'success': True,
                    'translated_text': translated_text,
                    'original_text': text,
                    'source_language': source_language,
                    'target_language': target_language,
                    'confidence': getattr(response, 'confidence', 1.0)
                }
            else:
                # Handle different response formats
                translated_text = str(response) if response else text
                return {
                    'success': True,
                    'translated_text': translated_text,
                    'original_text': text,
                    'source_language': source_language,
                    'target_language': target_language,
                    'confidence': 1.0
                }
                
        except Exception as e:
            print(f"Translation error: {str(e)}")
            return {
                'success': False,
                'error': f'Translation failed: {str(e)}',
                'original_text': text,
                'source_language': source_language,
                'target_language': target_language,
                'translated_text': text  # Fallback to original text
            }
    
    def get_language_mapping(self) -> Dict[str, str]:
        """
        Get mapping of Google Translate language codes to Sarvam AI language codes
        
        Returns:
            Dictionary mapping Google Translate codes to Sarvam AI codes
        """
        return {
            'en': 'en-IN',
            'hi': 'hi-IN',
            'gu': 'gu-IN',
            'pa': 'pa-IN',
            'mr': 'mr-IN',
            'bn': 'bn-IN',
            'ta': 'ta-IN',
            'te': 'te-IN',
            'kn': 'kn-IN',
            'ml': 'ml-IN',            'or': 'or-IN',
            'as': 'as-IN'
        }
