from pathlib import Path
from typing import List, Optional, TYPE_CHECKING
import logging
import asyncio

from pdf2image import convert_from_path, pdfinfo_from_path
from pdf2image.exceptions import (
    PDFInfoNotInstalledError,
    PDFPageCountError,
    PDFSyntaxError
)
from PIL import Image

from app.models import Image as AppImage, TaskStatus
from app.utils.file_utils import generate_unique_id
from app.core.path_manager import PathManager

if TYPE_CHECKING:
    from app.services.task_service import TaskService

logger = logging.getLogger(__name__)


class PDFService:
    """PDF处理服务类"""
    
    def __init__(self, path_manager: Optional[PathManager] = None):
        """Initialize PDF service
        
        Args:
            path_manager: Path manager instance, if None uses global instance
        """
        self.path_manager = path_manager or PathManager()
    
    def get_image_path(self, project_id: str, page_number: int) -> Optional[Path]:
        """Get PNG image path for specified project and page (for PPT composition)

        Args:
            project_id: Project ID
            page_number: Page number (starting from 1)

        Returns:
            PNG image file path, returns None if file doesn't exist
        """
        try:
            image_path = self.path_manager.get_project_image_file(project_id, page_number, "png")

            if image_path.exists():
                return image_path
            return None
        except Exception as e:
            logger.error(f"获取PNG图片路径失败: {str(e)}")
            return None

    def get_webp_image_path(self, project_id: str, page_number: int) -> Optional[Path]:
        """Get WebP image path for specified project and page (for frontend transfer)

        Args:
            project_id: Project ID
            page_number: Page number (starting from 1)

        Returns:
            WebP image file path, returns None if file doesn't exist
        """
        try:
            webp_path = self.path_manager.get_project_image_file(project_id, page_number, "webp")

            if webp_path.exists():
                return webp_path
            return None
        except Exception as e:
            logger.error(f"获取WebP图片路径失败: {str(e)}")
            return None

    def convert_png_to_webp(self, project_id: str, page_number: int) -> Optional[Path]:
        """Convert PNG image to WebP format (backward compatibility)

        Args:
            project_id: Project ID
            page_number: Page number (starting from 1)

        Returns:
            Generated WebP image file path, returns None if PNG doesn't exist
        """
        try:
            png_path = self.get_image_path(project_id, page_number)
            if not png_path:
                logger.warning(f"PNG image doesn't exist: project={project_id}, page={page_number}")
                return None

            webp_path = self.path_manager.get_project_image_file(project_id, page_number, "webp")

            with Image.open(png_path) as image:
                webp_image = image.convert("RGB")
                webp_image.save(webp_path.as_posix(), "WEBP", quality=85, optimize=True)

            logger.info(f"已转换PNG到WebP: {png_path} -> {webp_path}")
            return webp_path
        except Exception as e:
            logger.error(f"PNG转WebP失败: {str(e)}")
            return None

    async def convert_pdf_to_images_with_progress(self, project_id: str, pdf_path: str, task_id: str, task_service: 'TaskService') -> List[AppImage]:
        """Convert PDF file to images with progress tracking

        Args:
            project_id: Project ID
            pdf_path: PDF file path
            task_id: Task ID for progress tracking
            task_service: Task service instance

        Returns:
            List of generated image objects

        Raises:
            Exception: Raises exception on conversion failure
        """
        try:
            pdf_path: Path = Path(pdf_path)
            images_dir = self.path_manager.get_project_images_dir(project_id)

            # Get total page count in thread pool
            pdf_info = await asyncio.to_thread(pdfinfo_from_path, pdf_path.as_posix())
            total_pages = pdf_info['Pages']

            logger.info(f"Starting PDF conversion with progress tracking: {total_pages} pages")

            # Update task status to running
            task_service.update_task_status(task_id, TaskStatus.RUNNING)

            image_objects = []

            # Process each page individually
            for page_num in range(1, total_pages + 1):
                formatted_page_num = str(page_num).zfill(3)

                png_path = images_dir / f"page_{formatted_page_num}.png"
                webp_path = images_dir / f"page_{formatted_page_num}.webp"

                # Convert single page in thread pool
                page_images = await asyncio.to_thread(
                    convert_from_path,
                    pdf_path.as_posix(),
                    first_page=page_num,
                    last_page=page_num,
                    dpi=72,
                    fmt="png"
                )

                if len(page_images) == 0:
                    raise Exception(f"Failed to convert page {page_num}")

                image = page_images[0]

                # Save PNG in thread pool
                await asyncio.to_thread(image.save, png_path.as_posix(), "PNG")

                # Save WebP in thread pool
                webp_image = image.convert("RGB")
                await asyncio.to_thread(webp_image.save, webp_path.as_posix(), "WEBP", quality=85, optimize=True)

                # Create image object
                image_obj = AppImage(
                    id=generate_unique_id(),
                    img_path=str(png_path.relative_to(self.path_manager.get_projects_dir()))
                )

                image_objects.append(image_obj)

                # Update task progress
                task_service.increment_task_progress(task_id)
                logger.info(f"Converted page {page_num}/{total_pages}: PNG -> {png_path}, WebP -> {webp_path}")

                # Yield control to event loop to allow other requests to be processed
                await asyncio.sleep(0)

            # Mark task as completed
            task_service.update_task_status(task_id, TaskStatus.COMPLETED, progress=1.0)

            logger.info(f"PDF conversion completed, generated {len(image_objects)} images")
            return image_objects

        except PDFInfoNotInstalledError:
            error_msg = "未找到Poppler工具，请确保已安装Poppler"
            logger.error(error_msg)
            task_service.update_task_status(task_id, TaskStatus.FAILED, error_message=error_msg)
            raise Exception(error_msg)
        except PDFPageCountError:
            error_msg = f"无法读取PDF页数: {pdf_path}"
            logger.error(error_msg)
            task_service.update_task_status(task_id, TaskStatus.FAILED, error_message=error_msg)
            raise Exception(error_msg)
        except PDFSyntaxError:
            error_msg = f"PDF文件损坏或格式错误: {pdf_path}"
            logger.error(error_msg)
            task_service.update_task_status(task_id, TaskStatus.FAILED, error_message=error_msg)
            raise Exception(error_msg)
        except Exception as e:
            error_msg = f"PDF转换失败: {str(e)}"
            logger.error(error_msg)
            task_service.update_task_status(task_id, TaskStatus.FAILED, error_message=error_msg)
            raise Exception(error_msg)