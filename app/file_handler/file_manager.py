import aiofiles
import os
import uuid
from fastapi import UploadFile
from typing import List

class FileManager:
    def __init__(self):
        self.upload_dir = "app/file_handler/uploads"
        self.output_dir = "app/file_handler/outputs"
        
        # Create directories if they don't exist
        os.makedirs(self.upload_dir, exist_ok=True)
        os.makedirs(self.output_dir, exist_ok=True)
    
    async def save_upload(self, file: UploadFile) -> str:
        """Save uploaded file and return the file path"""
        # Generate unique filename
        file_extension = os.path.splitext(file.filename)[1]
        unique_filename = f"{uuid.uuid4()}{file_extension}"
        file_path = os.path.join(self.upload_dir, unique_filename)
        
        # Save file
        async with aiofiles.open(file_path, 'wb') as f:
            content = await file.read()
            await f.write(content)
        
        return file_path
    
    def get_output_path(self, filename: str) -> str:
        """Get path for output file"""
        return os.path.join(self.output_dir, filename)
    
    def cleanup_old_files(self, max_age_hours: int = 24):
        """Clean up old files to save disk space"""
        import time
        current_time = time.time()
        
        for directory in [self.upload_dir, self.output_dir]:
            for filename in os.listdir(directory):
                file_path = os.path.join(directory, filename)
                if os.path.isfile(file_path):
                    file_age = current_time - os.path.getctime(file_path)
                    if file_age > max_age_hours * 3600:
                        os.remove(file_path)
    
    def get_file_info(self, file_path: str) -> dict:
        """Get information about a file"""
        if not os.path.exists(file_path):
            return None
        
        stat = os.stat(file_path)
        return {
            "size": stat.st_size,
            "extension": os.path.splitext(file_path)[1],
            "basename": os.path.basename(file_path)
        }
