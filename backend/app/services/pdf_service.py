import os
from pathlib import Path
from typing import List, Optional
import logging

from pdf2image import convert_from_path
from pdf2image.exceptions import (
    PDFInfoNotInstalledError,
    PDFPageCountError,
    PDFSyntaxError
)
from PIL import Image

from app.models import Image as AppImage
from app.utils.file_utils import generate_unique_id, ensure_directory

logger = logging.getLogger(__name__)


class PDFService:
    """PDF处理服务类"""
    
    def __init__(self, storage_dir: Optional[str] = None):
        """初始化PDF服务
        
        Args:
            storage_dir: 存储目录，默认为当前工作目录下的storage/projects
        """
        if storage_dir is None:
            # 默认存储目录为项目根目录下的storage/projects
            self.storage_dir = Path.cwd() / "storage" / "projects"
        else:
            self.storage_dir = Path(storage_dir)
        
        # 确保存储目录存在
        self.storage_dir.mkdir(parents=True, exist_ok=True)
    
    def get_image_path(self, project_id: str, page_number: int) -> Optional[Path]:
        """获取指定项目和页码的图片路径
        
        Args:
            project_id: 项目ID
            page_number: 页码（从1开始）
            
        Returns:
            图片文件路径，如果文件不存在则返回None
        """
        try:
            # 构建图片路径
            image_path = self.storage_dir / project_id / "images" / f"page_{page_number:03d}.png"
            
            # 检查文件是否存在
            if image_path.exists():
                return image_path
            return None
        except Exception as e:
            logger.error(f"获取图片路径失败: {str(e)}")
            return None
    
    def convert_pdf_to_images(self, project_id: str, pdf_path: str) -> List[AppImage]:
        """将PDF文件转换为图片
        
        Args:
            project_id: 项目ID
            pdf_path: PDF文件路径
            
        Returns:
            生成的图片对象列表
            
        Raises:
            Exception: 转换失败时抛出异常
        """
        try:
            # 转换为Path对象
            pdf_path: Path = Path(pdf_path)
            
            # 创建图片存储目录
            images_dir = self.storage_dir / project_id / "images"
            ensure_directory(images_dir)
            
            # 使用pdf2image转换PDF为图片
            images = convert_from_path(
                pdf_path.as_posix(),
                dpi=72,
                fmt="png",
                thread_count=8  # 利用8个线程并行处理
            )
            
            image_objects = []
            
            # 遍历每一页图片
            for i, image in enumerate(images, 1):
                # 格式化页码为3位数字，确保排序正确
                formatted_page_num = str(i).zfill(3)
                
                # 生成图片文件路径
                image_path = images_dir / f"page_{formatted_page_num}.png"
                
                # 保存图片
                image.save(image_path.as_posix(), "PNG")
                
                # 创建图片对象
                image_obj = AppImage(
                    id=generate_unique_id(),
                    img_path=str(image_path.relative_to(self.storage_dir))
                )
                
                image_objects.append(image_obj)
                logger.info(f"已保存页面 {i} 到 {image_path}")
            
            logger.info(f"PDF转换完成，共生成 {len(image_objects)} 张图片")
            return image_objects
            
        except PDFInfoNotInstalledError:
            error_msg = "未找到Poppler工具，请确保已安装Poppler"
            logger.error(error_msg)
            raise Exception(error_msg)
        except PDFPageCountError:
            error_msg = f"无法读取PDF页数: {pdf_path}"
            logger.error(error_msg)
            raise Exception(error_msg)
        except PDFSyntaxError:
            error_msg = f"PDF文件损坏或格式错误: {pdf_path}"
            logger.error(error_msg)
            raise Exception(error_msg)
        except Exception as e:
            error_msg = f"PDF转换失败: {str(e)}"
            logger.error(error_msg)
            raise Exception(error_msg)