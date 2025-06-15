import os
import zipfile
import shutil
import uuid
import re
from typing import Dict, Any, List
from app.config import Config

class TextReplacer:
    """Replace text in ZIP archive files"""
    
    async def execute(self, parameters: Dict[str, Any], file_paths: List[str]) -> Dict[str, Any]:
        """Execute the text replacement function"""
        if not file_paths:
            raise ValueError("No files provided for text replacement")
            
        # Get the first ZIP file
        zip_files = [f for f in file_paths if f.lower().endswith('.zip')]
        if not zip_files:
            raise ValueError("No ZIP files found for text replacement")
          # Get parameters
        find_text = parameters.get("find_text", "")
        replace_text = parameters.get("replace_text", "")
        case_sensitive = parameters.get("case_sensitive", False)
        
        if not find_text:
            raise ValueError("Find text parameter is required")
        
        zip_path = zip_files[0]
        replace_id = uuid.uuid4().hex[:8]
        extract_folder = f"text_replaced_{replace_id}"
        output_dir = os.path.join(Config.OUTPUT_DIR, extract_folder)
        
        # Create output directory
        os.makedirs(output_dir, exist_ok=True)
        
        # Extract and process files
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(output_dir)
        
        # Replace text in text files
        modified_files = []
        for root, _, files in os.walk(output_dir):
            for file in files:
                file_path = os.path.join(root, file)
                if self._is_text_file(file_path):
                    if self._replace_text_in_file(file_path, find_text, replace_text, case_sensitive):
                        rel_path = os.path.relpath(file_path, output_dir)
                        modified_files.append(rel_path)
          # Create summary file
        summary_file = f"replacement_summary_{replace_id}.txt"
        summary_path = os.path.join(Config.OUTPUT_DIR, summary_file)
        
        with open(summary_path, 'w') as f:
            f.write(f"Text Replacement Summary\n")
            f.write(f"=======================\n")
            f.write(f"Source: {os.path.basename(zip_path)}\n")
            f.write(f"Find text: '{find_text}'\n")
            f.write(f"Replace text: '{replace_text}'\n")
            f.write(f"Case sensitive: {case_sensitive}\n")
            f.write(f"Modified files: {len(modified_files)}\n\n")
            f.write("Files modified:\n")
            for file in modified_files:
                f.write(f"- {file}\n")
        
        return {
            "output_path": summary_file,
            "modified_folder": extract_folder,
            "modified_files": len(modified_files)
        }
    
    def _is_text_file(self, file_path):
        """Check if file is a text file based on extension"""
        text_extensions = ['.txt', '.html', '.css', '.js', '.py', '.java', '.xml', '.json', '.md']
        _, ext = os.path.splitext(file_path.lower())
        return ext in text_extensions
        
    def _replace_text_in_file(self, file_path, find_text, replace_text, case_sensitive):
        """Replace text in a file"""
        try:
            with open(file_path, 'r', errors='ignore') as f:
                content = f.read()
                
            flags = 0 if case_sensitive else re.IGNORECASE
            new_content, count = re.subn(re.escape(find_text), replace_text, content, flags=flags)
            
            if count > 0:
                with open(file_path, 'w') as f:
                    f.write(new_content)
                return True
            return False
        except Exception:
            return False
