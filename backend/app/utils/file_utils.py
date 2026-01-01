import os
import shutil
import uuid
import hashlib
from pathlib import Path
from typing import Optional, List, Union, Dict, Any
import logging

logger = logging.getLogger(__name__)


def ensure_directory(directory: Union[str, Path]) -> Path:
    """确保目录存在，如果不存在则创建"""
    return ensure_directory_exists(directory)


def ensure_directory_exists(directory: Union[str, Path]) -> Path:
    """确保目录存在，如果不存在则创建"""
    dir_path = Path(directory)
    dir_path.mkdir(parents=True, exist_ok=True)
    return dir_path


def generate_unique_id() -> str:
    """生成唯一ID"""
    return str(uuid.uuid4())


def generate_file_hash(file_path: Union[str, Path]) -> str:
    """生成文件的哈希值"""
    hash_md5 = hashlib.md5()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()


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


def get_file_extension(filename: str) -> str:
    """获取文件扩展名（包含点）"""
    return Path(filename).suffix.lower()


def create_project_directory(project_id: str, base_dir: Union[str, Path] = None) -> Dict[str, Path]:
    """创建项目目录结构"""
    if base_dir is None:
        base_dir = Path.cwd() / "storage" / "projects"
    else:
        base_dir = Path(base_dir)
    
    project_dir = base_dir / project_id
    
    # 创建项目子目录
    directories = {
        "project": project_dir,
        "images": project_dir / "images",
        "scripts": project_dir / "scripts",
        "audio": project_dir / "audio"
    }
    
    for dir_path in directories.values():
        ensure_directory_exists(dir_path)
    
    return directories


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


def copy_file(src: Union[str, Path], dst: Union[str, Path]) -> bool:
    """复制文件"""
    try:
        src_path = Path(src)
        dst_path = Path(dst)
        
        # 确保目标目录存在
        ensure_directory_exists(dst_path.parent)
        
        # 复制文件
        shutil.copy2(src_path, dst_path)
        return True
    except Exception as e:
        logger.error(f"Error copying file from {src} to {dst}: {str(e)}")
        return False


def move_file(src: Union[str, Path], dst: Union[str, Path]) -> bool:
    """移动文件"""
    try:
        src_path = Path(src)
        dst_path = Path(dst)
        
        # 确保目标目录存在
        ensure_directory_exists(dst_path.parent)
        
        # 移动文件
        shutil.move(str(src_path), str(dst_path))
        return True
    except Exception as e:
        logger.error(f"Error moving file from {src} to {dst}: {str(e)}")
        return False


def get_file_size(file_path: Union[str, Path]) -> int:
    """获取文件大小（字节）"""
    try:
        return Path(file_path).stat().st_size
    except Exception as e:
        logger.error(f"Error getting file size for {file_path}: {str(e)}")
        return 0


def format_file_size(size_bytes: int) -> str:
    """格式化文件大小为人类可读的格式"""
    if size_bytes == 0:
        return "0B"
    
    size_names = ["B", "KB", "MB", "GB", "TB"]
    i = 0
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1
    
    return f"{size_bytes:.2f}{size_names[i]}"


def validate_file_type(file_path: Union[str, Path], allowed_extensions: List[str]) -> bool:
    """验证文件类型是否在允许的扩展名列表中"""
    file_ext = get_file_extension(str(file_path))
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


def paginate_results(items: List[Any], page: int, size: int) -> Dict[str, Any]:
    """对结果进行分页"""
    if page < 1:
        page = 1
    if size < 1:
        size = 10
    
    start = (page - 1) * size
    end = start + size
    
    total = len(items)
    items_page = items[start:end]
    
    return {
        "items": items_page,
        "pagination": {
            "page": page,
            "size": size,
            "total": total,
            "pages": (total + size - 1) // size
        }
    }