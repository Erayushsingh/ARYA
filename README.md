# 🤖 ARYA - Advanced AI-Powered Platform

**ARYA** is a cutting-edge FastAPI application that combines the power of AI with intuitive file processing capabilities and in various tasks. Using natural language prompts, users can describe what they want to do with their files, and the AI automatically determines and executes the appropriate function.

## ✨ Key Features

### 🧠 **AI-Powered Intelligence**
- **Google Gemini 2.0-Flash Integration** - Advanced prompt parsing and function calling
- **Sarvam AI Integration** - Multilingual speech-to-text and text-to-speech
- **Natural Language Processing** - Describe tasks in plain English (or 12+ Indian languages)
- **Smart Function Detection** - Automatically chooses the right tool for the job

### 🎤 **Advanced Speech Capabilities**
- **Speech-to-Text** - Convert audio to text in 12+ Indian languages + English
- **Text-to-Speech** - Generate natural speech from text in multiple languages
- **Auto Language Detection** - Automatically detects spoken language
- **Real-time Processing** - Instant voice recognition using Web Speech API

### 🌐 **Multilingual Support**
- **100+ Languages** - Complete Google Translate integration
- **Indian Language Focus** - Native support for Hindi, Gujarati, Tamil, Telugu, Bengali, Marathi, and more
- **Quick Language Switching** - One-click language change buttons
- **Native Script Display** - Text appears in original scripts (हिंदी, ગુજરાતી, தமிழ், etc.)

### 📁 **Comprehensive File Processing**
- **Image Processing** - Compression, format conversion, PDF creation
- **Document Conversion** - Word to PDF with customizable settings
- **Archive Management** - Extract, analyze, and process ZIP files
- **Text Operations** - Find and replace across multiple files
- **Smart Analysis** - Detailed file content analysis and reporting


## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Google Gemini API key
- Sarvam AI API key (for speech features)

### Installation & Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd ARYA
   ```

2. **Use the automated start script** (Recommended)
   ```bash
   chmod +x start.sh
   ./start.sh
   ```
   
   **Or set up manually:**
   ```bash
   # Create virtual environment
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   
   # Install dependencies
   pip install -r requirements.txt
   
   # Create directories
   mkdir -p app/file_handler/uploads app/file_handler/outputs
   ```

3. **Configure environment variables**
   Create a `.env` file in the project root:
   ```env
   # API Keys
   GOOGLE_GEMINI_KEY=your-google-gemini-api-key
   SARVAM_API_KEY=your-sarvam-api-key
   
   # Server Configuration
   HOST=0.0.0.0
   PORT=8001
   DEBUG=True
   
   # File Upload Settings
   MAX_FILE_SIZE=50MB
   ALLOWED_EXTENSIONS=.jpg,.jpeg,.png,.bmp,.tiff,.webp,.docx,.zip,.wav,.mp3,.flac,.aac,.m4a,.ogg,.pdf,.txt
   
   # Function Settings
   DEFAULT_IMAGE_QUALITY=85
   DEFAULT_PAGE_SIZE=A4
   DEFAULT_ORIENTATION=portrait
   ```

4. **Start the application**
   ```bash
   python main.py
   ```

5. **Open your browser**
   Navigate to `http://localhost:8001`

## 🛠️ Available Functions

### 📸 **Image Processing**
- **Compression** - Reduce file sizes with quality control
- **Format Conversion** - Convert between JPG, PNG, WebP, etc.
- **Resize** - Adjust dimensions while maintaining aspect ratio
- **Optimization** - Smart compression for web use

**Example Prompts:**
```
"Compress these images to 80% quality"
"Resize these photos to 1920x1080"
"Convert PNG images to JPG format"
"Optimize these images for web use"
```

### 📄 **Document Conversion**
- **Word to PDF** - Convert .docx files with custom settings
- **Image to PDF** - Combine multiple images into PDF
- **Page Settings** - A4, Letter, Legal sizes with custom margins
- **Orientation** - Portrait or landscape layouts

**Example Prompts:**
```
"Convert this Word document to PDF"
"Create a PDF from these photos"
"Make a landscape PDF with A4 pages"
"Convert documents with 1-inch margins"
```

### 🗃️ **Archive Management**
- **File Extraction** - Unzip and analyze archive contents
- **Content Analysis** - Detailed reports on file types and sizes
- **Text Processing** - Handle CSV, JSON, text, and code files
- **Smart Categorization** - Organize extracted files by type

**Example Prompts:**
```
"Extract all files from this ZIP archive"
"Analyze the contents of this archive"
"Unzip and categorize these files"
"Extract and summarize archive data"
```

### ✏️ **Text Operations**
- **Find & Replace** - Update text across multiple files
- **Case Sensitivity** - Flexible matching options
- **Batch Processing** - Handle multiple files simultaneously
- **Safe Updates** - Preview changes before applying

**Example Prompts:**
```
"Replace 'IITM' with 'IIT Madras' in all files"
"Find and replace 'old text' with 'new text'"
"Update company name in all documents"
"Change keywords case-sensitively"
```

### 🎤 **Speech Processing**
- **Speech-to-Text** - Transcribe audio in 12+ languages
- **Text-to-Speech** - Generate natural speech audio
- **Language Detection** - Automatic language identification
- **High Quality** - Professional-grade audio processing

**Example Prompts:**
```
"Convert this audio to text in Hindi"
"Transcribe this speech in Gujarati"
"Generate speech from this text in Tamil"
"Convert English audio to text"
```

## 🌍 Supported Languages

### 🇮🇳 **Indian Languages**
| Language | Native Name | Speech Support | UI Support |
|----------|-------------|---------------|------------|
| Hindi | हिंदी | ✅ | ✅ |
| Gujarati | ગુજરાતી | ✅ | ✅ |
| Tamil | தமிழ் | ✅ | ✅ |
| Telugu | తెలుగు | ✅ | ✅ |
| Bengali | বাংলা | ✅ | ✅ |
| Marathi | मराठी | ✅ | ✅ |
| Punjabi | ਪੰਜਾਬੀ | ✅ | ✅ |
| Kannada | ಕನ್ನಡ | ✅ | ✅ |
| Malayalam | മലയാളം | ✅ | ✅ |
| Odia | ଓଡ଼ିଆ | ✅ | ✅ |
| Assamese | অসমীয়া | ✅ | ✅ |
| English | English | ✅ | ✅ |

### 🌍 **International Languages**
- **European**: Spanish, French, German, Italian, Portuguese, Russian, Dutch, Swedish, Polish, etc.
- **Asian**: Chinese, Japanese, Korean, Thai, Vietnamese, Indonesian, etc.
- **Middle Eastern**: Arabic, Persian, Turkish, Hebrew, etc.
- **African**: Swahili, Zulu, Afrikaans, Amharic, etc.
- **And 90+ more languages via Google Translate**

## 🏗️ Project Architecture

```
ARYA/
├─ main.py                     # FastAPI application entry point
├─ requirements.txt            # Python dependencies
├─ start.sh                    # Automated setup script
├─ .env                        # Environment configuration
├─ app/
   ├── config.py              # Configuration management
   ├── client/                # AI service integrations
   │   ├── gemini_client.py   # Google Gemini AI
   │   └── sarvam_client.py   # Sarvam AI services
   ├── functions/             # Core functionality
   │   ├── function_registry.py
   │   ├── image_compression.py
   │   ├── word_to_pdf.py
   │   ├── image_to_pdf.py
   │   ├── file_extractor.py
   │   ├── text_replacer.py
   │   ├── speech_to_text.py
   │   └── text_to_speech.py
   ├── file_handler/          # File management
   │   ├── file_manager.py
   │   ├── uploads/           # User uploads
   │   └── outputs/           # Processed files
   ├── models/                # Data schemas
   │   └── schemas.py
   ├── templates/             # HTML templates
   │   └── index.html
   └── static/                # Frontend assets
       ├── style.css
       ├── script.js
       └── favicon.ico


## 🔧 API Endpoints

### Core Endpoints
- `GET /` - Main web interface
- `POST /process` - Process files with AI function calling
- `GET /download/{file_path}` - Download processed files
- `GET /test` - System health check

### Speech & Translation
- `POST /api/sarvam-speech-to-text` - Speech-to-text conversion
- `POST /api/translate` - Text translation services

## 🛡️ Security & Privacy

### Data Protection
- **Local Processing** - Files processed locally, not stored in cloud
- **Temporary Storage** - Automatic cleanup of uploaded files
- **API Key Security** - Credentials stored in environment variables
- **No Data Collection** - No user data stored permanently

### Privacy Features
- **Speech Processing** - Audio processed in real-time, not stored
- **Secure Uploads** - File validation and sanitization
- **Local AI** - Gemini API calls for function parsing only
- **Transparent Operations** - Clear logging of all operations

## 🎯 Use Cases

### 👨‍💼 **Business Applications**
- **Document Processing** - Convert, compress, and organize business documents
- **Multilingual Communication** - Process documents in multiple languages
- **Archive Management** - Extract and analyze business data from archives
- **Content Creation** - Generate speech content for presentations

### 🎓 **Educational Use**
- **Language Learning** - Practice speaking and listening in Indian languages
- **Document Management** - Process academic papers and assignments
- **Research Support** - Extract and analyze research data
- **Accessibility** - Voice input for users with disabilities

### 👨‍💻 **Development & IT**
- **File Processing Automation** - Batch process development assets
- **Documentation** - Convert and optimize technical documents
- **Code Analysis** - Extract and analyze code from archives
- **Deployment Support** - Process files for web deployment

## 🔍 Testing

### Run Tests
```bash
# Test core functionality
python test_functions.py

# Test audio format handling
python test_audio_format_handling.py

# Test API endpoints
curl http://localhost:8001/test
```

### Manual Testing
1. **Upload Test Files** - Try different file types and sizes
2. **Voice Input** - Test speech recognition in different languages
3. **Language Switching** - Verify translation functionality
4. **Mobile Testing** - Test responsive design on mobile devices

## 🚀 Deployment

### Local Development
```bash
# Development mode with auto-reload
uvicorn main:app --host 0.0.0.0 --port 8001 --reload
```

### Production Deployment
```bash
# Production mode
uvicorn main:app --host 0.0.0.0 --port 8001 --workers 4
```

### Docker Support
```dockerfile
FROM python:3.11
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8001
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8001"]
```

## 🤝 Contributing

1. **Fork the repository**
2. **Create a feature branch** (`git checkout -b feature/amazing-feature`)
3. **Commit your changes** (`git commit -m 'Add amazing feature'`)
4. **Push to the branch** (`git push origin feature/amazing-feature`)
5. **Open a Pull Request**


## 📝 License

This project is open source and available under the [MIT License](LICENSE).

## 🙏 Acknowledgments

- **Google Gemini AI** - For advanced language processing
- **Sarvam AI** - For Indian language speech capabilities
- **Google Translate** - For multilingual interface support
- **FastAPI** - For the robust web framework
- **Tailwind CSS** - For modern UI styling

## 📞 Support

### Documentation
- 📚 [Sarvam Integration Guide](SARVAM_INTEGRATION_GUIDE.md)
- 🎤 [Speech Input Guide](SPEECH_INPUT_COMPLETE.md)
- 🌐 [Google Translate Integration](GOOGLE_TRANSLATE_INTEGRATION.md)
- ✅ [Implementation Details](IMPLEMENTATION_COMPLETE.md)

### Getting Help
- 🐛 **Issues** - Report bugs and request features via GitHub Issues
- 💬 **Discussions** - Join community discussions
- 📧 **Contact** - Reach out for enterprise support

---

## 🎉 **Ready to Transform Your File Processing Experience!**

### 🌟 **What Makes ARYA Special:**
- **🧠 AI-Powered** - Just describe what you want in natural language
- **🗣️ Voice-Enabled** - Speak your requests in any Indian language
- **🌍 Globally Accessible** - Interface available in 100+ languages
- **⚡ Lightning Fast** - Process files in seconds, not minutes
- **🎨 Beautiful Design** - Modern, intuitive, and responsive

### 🚀 **Start Processing Files Like Never Before:**
1. **Visit** `http://localhost:8001`
2. **Speak or Type** your request in any language
3. **Upload** your files with drag & drop
4. **Watch** AI work its magic
5. **Download** your processed results

**Experience the future of file processing today!** ✨
