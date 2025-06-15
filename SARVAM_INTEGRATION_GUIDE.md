# Sarvam AI Speech-to-Text Integration Guide

## Overview
The PROAGENT application now includes speech-to-text functionality powered by Sarvam AI. This feature allows users to convert audio files to text in multiple Indian languages.

## Features
- **Multi-language Support**: 12 Indian languages + English
- **Multiple Audio Formats**: WAV, MP3, M4A, FLAC, AAC
- **AI-Powered Prompt Parsing**: Natural language prompts
- **Seamless Integration**: Works with existing file upload system

## Supported Languages
| Language | Code | Language | Code |
|----------|------|----------|------|
| Hindi | hi-IN | Telugu | te-IN |
| Gujarati | gu-IN | Kannada | kn-IN |
| Punjabi | pa-IN | Malayalam | ml-IN |
| Marathi | mr-IN | Odia | or-IN |
| Bengali | bn-IN | Assamese | as-IN |
| Tamil | ta-IN | English | en-IN |

## How to Use

### 1. Through Web Interface
1. **Upload Audio File**: 
   - Drag and drop or select an audio file
   - Supported formats: `.wav`, `.mp3`, `.m4a`, `.flac`, `.aac`

2. **Enter Natural Language Prompt**:
   ```
   Examples:
   - "Convert this audio to text"
   - "Transcribe this speech in Hindi"
   - "Speech to text in Gujarati"
   - "Convert audio to text using saarika model"
   - "Transcribe this Tamil audio file"
   ```

3. **Process**: Click submit to convert audio to text

### 2. Prompt Examples
- **Basic**: "Convert audio to text"
- **With Language**: "Transcribe in Hindi", "Speech to text in Tamil"
- **With Model**: "Use saarika model for transcription"
- **Combined**: "Convert this Gujarati speech to text using saarika model"

### 3. API Parameters
The system automatically extracts:
- **Language**: From prompts like "in Hindi", "Tamil audio", etc.
- **Model**: Defaults to "saarika:v2" (Sarvam AI's speech model)
- **File Type**: Auto-detected from uploaded file

## Technical Implementation

### Architecture
```
User Upload → File Handler → Gemini AI (Prompt Parsing) → Sarvam AI (Speech-to-Text) → Text Output
```

### Key Components
1. **SarvamClient** (`app/client/sarvam_client.py`)
   - Handles Sarvam AI API communication
   - Manages language codes and model selection

2. **SpeechToTextConverter** (`app/functions/speech_to_text.py`)
   - Main conversion logic
   - File format validation
   - Error handling

3. **Function Registry** (`app/functions/function_registry.py`)
   - Registers speech-to-text function
   - Enables automatic prompt routing

4. **Gemini Integration** (`app/client/gemini_client.py`)
   - Parses natural language prompts
   - Extracts language and model preferences

### Configuration
- **API Key**: Set `SARVAM_API_KEY` in `.env` file
- **File Limits**: Configured in `MAX_FILE_SIZE`
- **Allowed Extensions**: Audio formats in `ALLOWED_EXTENSIONS`

## Error Handling
- **Missing Files**: Clear error message for no audio files
- **Unsupported Formats**: Lists supported formats
- **API Errors**: Detailed Sarvam AI error messages
- **Network Issues**: Retry logic and timeout handling

## Security
- **API Key Protection**: Stored in environment variables
- **File Validation**: Format and size checking
- **Cleanup**: Automatic temporary file removal

## Testing
Run the integration tests:
```bash
python test_sarvam_integration.py
```

Run the example demonstration:
```bash
python example_speech_to_text.py
```

## Usage Statistics
- **Languages**: 12 Indian languages + English
- **Audio Formats**: 5 supported formats
- **Model**: saarika:v2 (Sarvam AI)
- **Integration**: Seamless with existing workflow

## Next Steps
1. **Text-to-Speech**: Add TTS functionality
2. **Translation**: Add multi-language translation
3. **Batch Processing**: Support multiple audio files
4. **Custom Models**: Support for different Sarvam AI models

---

**Status**: ✅ **Ready for Production**
**Last Updated**: June 15, 2025
**Version**: 1.0
