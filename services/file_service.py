import hashlib
from typing import BinaryIO
import os


class FileService:
    
    @staticmethod
    def calculate_hash(file_path: str, algorithm: str = "sha256") -> str:

        hash_obj = hashlib.new(algorithm)
        
        with open(file_path, 'rb') as f:
            while chunk := f.read(8192):
                hash_obj.update(chunk)
        
        return hash_obj.hexdigest()
    
    @staticmethod
    def calculate_partial_hash(file_path: str, bytes_to_read: int = 8192, algorithm: str = "sha256") -> str:
       
        hash_obj = hashlib.new(algorithm)
        
        with open(file_path, 'rb') as f:
            chunk = f.read(bytes_to_read)
            hash_obj.update(chunk)
        
        return hash_obj.hexdigest()
    
    @staticmethod
    def calculate_stream_hash(stream: BinaryIO, algorithm: str = "sha256") -> str:
        hash_obj = hashlib.new(algorithm)
        
        while chunk := stream.read(8192):
            hash_obj.update(chunk)
        
        return hash_obj.hexdigest()
    
    @staticmethod
    def get_file_signature(file_path: str) -> dict:

        
        file_size = os.path.getsize(file_path)
        file_hash = FileService.calculate_hash(file_path)
        
        return {
            "file_size": file_size,
            "file_hash": file_hash
        }
