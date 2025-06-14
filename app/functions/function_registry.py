from typing import Dict, Any, List
from app.functions.image_compression import ImageCompressor
from app.functions.word_to_pdf import WordToPdfConverter
from app.functions.image_to_pdf import ImageToPdfConverter
from app.functions.file_extractor import FileExtractor
from app.functions.text_replacer import TextReplacer

class FunctionRegistry:
    def __init__(self):
        self.functions = {
            "compress_image": ImageCompressor(),
            "word_to_pdf": WordToPdfConverter(),
            "image_to_pdf": ImageToPdfConverter(),
            "extract_files": FileExtractor(),
            "replace_text": TextReplacer()
        }
    
    async def execute_function(self, function_name: str, parameters: Dict[str, Any], file_paths: List[str]) -> Dict[str, Any]:
        """Execute the specified function with given parameters"""
        if function_name not in self.functions:
            raise ValueError(f"Function '{function_name}' not found")
        
        function_instance = self.functions[function_name]
        return await function_instance.execute(parameters, file_paths)
    
    def get_available_functions(self) -> List[str]:
        """Get list of available function names"""
        return list(self.functions.keys())
