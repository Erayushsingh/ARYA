import google.generativeai as genai
import json
import os
import re
from typing import List, Dict, Any
from app.models.schemas import FunctionCall

class GeminiClient:
    def __init__(self):
        # Configure the Gemini API
        api_key = os.getenv('GOOGLE_GEMINI_API_KEY', "AIzaSyBTOnMrZ0rEEus9a4VQtap5hgRu8vdpjVg")
        genai.configure(api_key=api_key)
        
        # Initialize the model
        self.model = genai.GenerativeModel('gemini-2.0-flash-exp')
        
        # Define available functions for the LLM
        self.available_functions = {
            "compress_image": {
                "description": "Compress image files to reduce file size while maintaining quality",
                "parameters": {
                    "quality": "Image quality (1-100, default: 85)",
                    "max_width": "Maximum width in pixels (optional)",
                    "max_height": "Maximum height in pixels (optional)",
                    "format": "Output format (JPEG, PNG, WEBP)"
                },
                "triggers": ["compress", "reduce size", "smaller", "optimize", "quality", "resize"]
            },
            "word_to_pdf": {
                "description": "Convert Word documents (.docx) to PDF format",
                "parameters": {
                    "page_size": "Page size (A4, Letter, Legal)",
                    "orientation": "Page orientation (portrait, landscape)",
                    "margin": "Page margin in points"
                },
                "triggers": ["word to pdf", "docx to pdf", "convert word", "document to pdf"]
            },
            "image_to_pdf": {
                "description": "Convert image files to PDF format",
                "parameters": {
                    "page_size": "Page size (A4, Letter, Legal)",
                    "orientation": "Page orientation (portrait, landscape)",
                    "margin": "Page margin in points"
                },
                "triggers": ["image to pdf", "photo to pdf", "picture to pdf", "img to pdf"]
            },
            "extract_files": {
                "description": "Extract and analyze all types of files from zip archives",
                "parameters": {},
                "triggers": ["extract files", "unzip files", "get files", "extract data", "analyze archive", "extract csv", "unzip csv"]
            },
            "replace_text": {
                "description": "Extract archives and replace text/keywords in all files",
                "parameters": {
                    "old_keyword": "Text to find and replace",
                    "new_keyword": "Replacement text",
                    "case_sensitive": "Whether replacement should be case sensitive (default: false)"
                },
                "triggers": ["replace text", "find and replace", "change keyword", "substitute text", "replace word"]
            }
        }
    
    async def parse_prompt_for_function(self, prompt: str, file_paths: List[str]) -> FunctionCall:
        """Parse user prompt to determine which function to call and extract parameters"""
        
        # Create function descriptions for the prompt
        functions_desc = "\n".join([
            f"- {name}: {info['description']}"
            for name, info in self.available_functions.items()
        ])
        
        # Analyze file types if files are provided
        file_info = ""
        if file_paths:
            file_extensions = [os.path.splitext(path)[1].lower() for path in file_paths]
            file_info = f"\nUploaded files: {', '.join(file_extensions)}"
        
        system_prompt = f"""
You are a function calling assistant. Based on the user's prompt and uploaded files, determine which function to call and extract the appropriate parameters.

Available functions:
{functions_desc}

{file_info}

Respond with a JSON object containing:
- function_name: the exact function name to call
- parameters: a dictionary of parameters with their values
- confidence: a float between 0 and 1 indicating your confidence

Rules:
1. If the user mentions compression, size reduction, or quality, use "compress_image"
2. If the user mentions converting Word/DOCX to PDF, use "word_to_pdf"
3. If the user mentions converting images to PDF, use "image_to_pdf"
4. Extract specific parameters from the prompt (quality levels, sizes, formats)
5. Use reasonable defaults if parameters aren't specified
6. Consider the file types uploaded when making decisions

User prompt: "{prompt}"
"""
        
        try:
            response = self.model.generate_content(system_prompt)
            
            # Parse the JSON response
            response_text = response.text.strip()
            
            # Clean up the response to extract JSON
            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```")[0]
            elif "```" in response_text:
                response_text = response_text.split("```")[1].split("```")[0]
            
            function_data = json.loads(response_text)
            
            return FunctionCall(
                function_name=function_data["function_name"],
                parameters=function_data["parameters"],
                confidence=function_data["confidence"]
            )
            
        except Exception as e:
            # Fallback: Try to determine function based on keywords
            prompt_lower = prompt.lower()
            
            if any(trigger in prompt_lower for trigger in self.available_functions["compress_image"]["triggers"]):
                return FunctionCall(
                    function_name="compress_image",
                    parameters={"quality": 85, "format": "JPEG"},
                    confidence=0.7
                )
            elif any(trigger in prompt_lower for trigger in self.available_functions["word_to_pdf"]["triggers"]):
                return FunctionCall(
                    function_name="word_to_pdf",
                    parameters={"page_size": "A4", "orientation": "portrait"},
                    confidence=0.7
                )
            elif any(trigger in prompt_lower for trigger in self.available_functions["image_to_pdf"]["triggers"]):
                return FunctionCall(
                    function_name="image_to_pdf",
                    parameters={"page_size": "A4", "orientation": "portrait"},
                    confidence=0.7
                )
            elif any(trigger in prompt_lower for trigger in self.available_functions["extract_files"]["triggers"]):
                return FunctionCall(
                    function_name="extract_files",
                    parameters={},
                    confidence=0.7
                )
            elif any(trigger in prompt_lower for trigger in self.available_functions["replace_text"]["triggers"]):
                # Try to extract keywords from prompt
                old_keyword = "IITM"  # default
                new_keyword = "IIT Madras"  # default
                
                # Simple pattern matching for replacement
                replace_patterns = [
                    r'replace["\s]+([^"]+)["\s]+with["\s]+([^"]+)',
                    r'change["\s]+([^"]+)["\s]+to["\s]+([^"]+)',
                    r'substitute["\s]+([^"]+)["\s]+with["\s]+([^"]+)'
                ]
                
                for pattern in replace_patterns:
                    match = re.search(pattern, prompt_lower)
                    if match:
                        old_keyword = match.group(1).strip(' "\'')
                        new_keyword = match.group(2).strip(' "\'')
                        break
                
                return FunctionCall(
                    function_name="replace_text",
                    parameters={
                        "old_keyword": old_keyword,
                        "new_keyword": new_keyword,
                        "case_sensitive": False
                    },
                    confidence=0.7
                )
            else:
                # Default to image compression if files are uploaded
                return FunctionCall(
                    function_name="compress_image",
                    parameters={"quality": 85, "format": "JPEG"},
                    confidence=0.5
                )
