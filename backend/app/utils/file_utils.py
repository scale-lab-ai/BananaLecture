import os
import shutil
import uuid
import hashlib
from pathlib import Path
from typing import Optional, List, Union, Dict, Any
import logging

logger = logging.getLogger(__name__)


def ensure_directory_exists(directory: Union[str, Path]) -> Path:
    """确保目录存在，如果不存在则创建"""
    dir_path = Path(directory)
    dir_path.mkdir(parents=True, exist_ok=True)
    return dir_path

def generate_unique_id() -> str:
    """生成唯一ID"""
    return str(uuid.uuid4())

def safe_filename(filename: str) -> str:
    """生成安全的文件名，移除或替换不安全的字符"""
    # 定义不安全的字符
    unsafe_chars = '<>:"/\\|?*'
    
    # 替换不安全的字符
    safe_name = ''.join(c if c not in unsafe_chars else '_' for c in filename)
    
    # 移除前后空格和点
    safe_name = safe_name.strip(' .')
    
    # 如果文件名为空，使用默认名称
    if not safe_name:
        safe_name = "unnamed_file"
    
    return safe_name

def delete_directory(directory: Union[str, Path], ignore_errors: bool = False) -> bool:
    """删除目录及其内容"""
    try:
        dir_path = Path(directory)
        if dir_path.exists() and dir_path.is_dir():
            shutil.rmtree(dir_path, ignore_errors=ignore_errors)
            return True
        return False
    except Exception as e:
        logger.error(f"Error deleting directory {directory}: {str(e)}")
        return False


def validate_file_type(file_path: Union[str, Path], allowed_extensions: List[str]) -> bool:
    """验证文件类型是否在允许的扩展名列表中"""
    file_ext = Path(file_path).suffix.lower()
    return file_ext.lower() in [ext.lower() if ext.startswith('.') else f'.{ext.lower()}' for ext in allowed_extensions]


def save_upload_file(upload_file, destination: Union[str, Path]) -> bool:
    """保存上传的文件"""
    try:
        dest_path = Path(destination)
        
        # 确保目标目录存在
        ensure_directory_exists(dest_path.parent)
        
        # 保存文件
        with open(dest_path, "wb") as buffer:
            shutil.copyfileobj(upload_file.file, buffer)
        
        return True
    except Exception as e:
        logger.error(f"Error saving upload file to {destination}: {str(e)}")
        return False
    finally:
        upload_file.file.close()