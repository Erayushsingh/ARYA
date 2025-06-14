# LLM Function Calling FastAPI Application

This is a FastAPI application that implements intelligent function calling capabilities using LLM prompt parsing with Google Gemini API. Users can upload files and describe what they want to do in natural language, and the AI will automatically determine the correct function to execute.

## Features

- **🤖 Intelligent Function Calling**: Uses Gemini 2.0-flash to parse user prompts and determine the appropriate function
- **🖼️ Image Compression**: Compress images with customizable quality, dimensions, and format
- **📄 Word to PDF**: Convert Word documents (.docx) to PDF with various page settings
- **📸 Image to PDF**: Combine multiple images into a single PDF document
- **📦 File Extraction**: Extract and analyze all types of files from ZIP archives with detailed summaries
- **🔄 Text Replacement**: Find and replace text in all files within ZIP archives (case-sensitive or insensitive)
- **🌐 Web Interface**: User-friendly interface for uploading files and downloading results
- **📁 Modular Architecture**: Clean separation of concerns with dedicated folders for different functionalities

## Project Structure

```
├── main.py                 # FastAPI application entry point
├── requirements.txt        # Python dependencies
├── app/
│   ├── functions/          # Function implementations
│   │   ├── function_registry.py
│   │   ├── image_compression.py
│   │   ├── word_to_pdf.py
│   │   └── image_to_pdf.py
│   ├── client/             # LLM client setup
│   │   └── gemini_client.py
│   ├── file_handler/       # File management
│   │   ├── file_manager.py
│   │   ├── uploads/        # Uploaded files storage
│   │   └── outputs/        # Processed files storage
│   ├── models/             # Data models and schemas
│   │   └── schemas.py
│   ├── templates/          # HTML templates
│   │   └── index.html
│   └── static/             # Static files (CSS, JS)
│       ├── style.css
│       └── script.js
```

## Installation

1. **Clone or create the project directory**
2. **Create a virtual environment**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

## Quick Start

1. **Use the start script** (recommended):
   ```bash
   ./start.sh
   ```

   Or **manually**:
   ```bash
   source venv/bin/activate
   python main.py
   ```

2. **Open your browser** and navigate to `http://localhost:8001`

3. **Use the interface**:
   - Enter a prompt describing what you want to do (e.g., "Compress these images to 80% quality")
   - Upload your files (images, Word documents)
   - Click "Process Files"
   - Download the processed results

## Available Functions

### 1. Image Compression
- **Triggers**: "compress", "reduce size", "smaller", "optimize", "quality", "resize"
- **Supported formats**: JPG, JPEG, PNG, BMP, TIFF, WEBP
- **Parameters**: quality (1-100), max_width, max_height, output format

### 2. Word to PDF Conversion
- **Triggers**: "word to pdf", "docx to pdf", "convert word", "document to pdf"
- **Supported formats**: DOCX
- **Parameters**: page_size (A4, Letter, Legal), orientation (portrait, landscape), margin

### 4. File Extraction & Analysis
- **Triggers**: "extract files", "unzip files", "analyze archive", "extract data", "get files"
- **Supported formats**: ZIP archives containing any file types
- **Features**: 
  - Extracts all files from archives
  - Analyzes file types, sizes, and content
  - Special analysis for CSV, JSON, text, and code files
  - Provides detailed file structure reports
  - Supports multiple file formats (CSV, JSON, text, code files, images, documents)

### 5. Text Replacement
- **Triggers**: "replace text", "find and replace", "change keyword", "substitute text", "replace word"
- **Supported formats**: ZIP archives containing text files
- **Parameters**: old_keyword, new_keyword, case_sensitive (default: false)
- **Features**: Replaces text in all compatible files within archives

## Example Prompts

- "Compress these images to 70% quality for web use"
- "Convert this Word document to PDF format"
- "Create a PDF from these photos with A4 pages"
- "Extract all files from this zip archive"
- "Analyze the contents of this archive"
- "Replace 'IITM' with 'IIT Madras' in all files"
- "Find and replace 'old_text' with 'new_text' in the archive"
- "Reduce the file size of these images by half"
- "Make a landscape PDF from these images"

## API Endpoints

- `GET /` - Main web interface
- `POST /process` - Process files with LLM function calling
- `GET /download/{file_path}` - Download processed files

## Scripts

- `start.sh` - Complete setup and start script

## Technical Details

- **Framework**: FastAPI with async support
- **LLM**: Google Gemini 2.0-flash for prompt parsing
- **Image Processing**: Pillow (PIL)
- **PDF Generation**: ReportLab
- **Document Processing**: python-docx
- **Data Analysis**: pandas (for CSV processing)
- **Archive Handling**: zipfile (built-in Python library)
- **Frontend**: HTML5, Tailwind CSS, Vanilla JavaScript

## Development

The application uses a modular architecture:

- **Functions**: Each function is a separate class with an `execute` method
- **Registry**: Central registry for managing and executing functions
- **Client**: Handles LLM communication and prompt parsing
- **File Manager**: Manages file uploads, storage, and cleanup
- **Models**: Pydantic models for data validation

## Configuration

The Gemini API key is currently hardcoded in `app/client/gemini_client.py`. For production use, move this to environment variables:

```python
api_key = os.getenv('GOOGLE_GEMINI_KEY', 'your-api-key-here')
```

## License

This project is open source and available under the MIT License.
