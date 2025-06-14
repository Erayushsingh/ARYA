import os
import zipfile
import shutil
import uuid
from typing import Dict, Any, List

class FileExtractor:
    """Extract files from ZIP archives"""
    
    async def execute(self, parameters: Dict[str, Any], file_paths: List[str]) -> Dict[str, Any]:
        """Execute the file extraction function"""
        if not file_paths:
            raise ValueError("No files provided for extraction")
            
        # Get the first ZIP file
        zip_files = [f for f in file_paths if f.lower().endswith('.zip')]
        if not zip_files:
            raise ValueError("No ZIP files found for extraction")
        
        zip_path = zip_files[0]
        extract_id = uuid.uuid4().hex[:8]
        extract_folder = f"extracted_{extract_id}"
        output_dir = os.path.join("app/file_handler/outputs", extract_folder)
        
        # Create output directory
        os.makedirs(output_dir, exist_ok=True)
        
        # Extract files
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(output_dir)
        
        # Create summary file
        summary_file = f"file_extraction_summary_{extract_id}.txt"
        summary_path = os.path.join("app/file_handler/outputs", summary_file)
        
        extracted_files = []
        for root, _, files in os.walk(output_dir):
            for file in files:
                rel_path = os.path.relpath(os.path.join(root, file), output_dir)
                extracted_files.append(rel_path)
        
        with open(summary_path, 'w') as f:
            f.write(f"Extraction Summary\n")
            f.write(f"=================\n")
            f.write(f"Source: {os.path.basename(zip_path)}\n")
            f.write(f"Extracted files: {len(extracted_files)}\n\n")
            f.write("Files:\n")
            for file in extracted_files:
                f.write(f"- {file}\n")
        
        return {
            "output_path": summary_file,
            "extracted_folder": extract_folder
        }
