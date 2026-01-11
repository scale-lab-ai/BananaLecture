import json
from pathlib import Path
from typing import List, Optional
from datetime import datetime
import logging

from app.models import Script, DialogueItem
from app.utils.file_utils import generate_unique_id
from app.core.path_manager import PathManager
from app.core.script_client import ScriptClient, DialogueItemAI

logger = logging.getLogger(__name__)


class ScriptService:
    """脚本处理服务类"""

    def __init__(self):
        """
        Initialize script service

        Args:
            path_manager: Path manager instance.
            script_client: Script client instance for AI interaction.
        """
        self.path_manager = PathManager()
        self.script_client = ScriptClient()

    def _encode_image(self, image_path: Path) -> bytes:
        """
        将图片文件编码为字节流

        Args:
            image_path: 图片文件路径

        Returns:
            图片的字节流
        """
        with open(image_path, "rb") as image_file:
            return image_file.read()

    def _get_context(self, project_id: str, page_number: int) -> str:
        """Get context information, i.e., script content from previous pages

        Args:
            project_id: Project ID
            page_number: Current page number

        Returns:
            Context string
        """
        if page_number <= 1:
            return ""

        try:
            scripts_dir = self.path_manager.get_project_scripts_dir(project_id)
            context_parts = []

            for i in range(1, page_number):
                script_file = scripts_dir / f"script_{i:03d}.json"
                if script_file.exists():
                    with open(script_file, "r", encoding="utf-8") as f:
                        script_data = json.load(f)
                    for dialogue in script_data.get("dialogues", []):
                        role = dialogue.get("role", "")
                        content = dialogue.get("content", "")
                        context_parts.append(f"{role}: {content}")

            return "\n".join(context_parts)
        except Exception as e:
            logger.error(f"Failed to read script file: {str(e)}")
            return ""

    async def generate_script_for_page(self, project_id: str, page_number: int,
                                       task_id: Optional[str] = None) -> Script:
        """为指定页面生成脚本

        Args:
            project_id: 项目ID
            page_number: 页码
            task_id: 任务ID，用于进度追踪

        Returns:
            生成的脚本对象

        Raises:
            Exception: 生成失败时抛出异常
        """
        try:
            # Check if page number is valid
            if page_number < 1:
                raise ValueError("Page number must be greater than 0")

            # Get project directory
            project_dir = self.path_manager.get_project_dir(project_id)
            if not project_dir.exists():
                raise ValueError(f"Project directory not found: {project_dir}")

            # Check if page already has script, if so delete all dialogue items
            existing_script = self.get_script(project_id, page_number)
            if existing_script and existing_script.dialogues:
                logger.info(
                    f"Page {page_number} already has script, deleting {len(existing_script.dialogues)} dialogue items")
                # Copy dialogue ID list to avoid modifying list during iteration
                dialogue_ids = [dialogue.id for dialogue in existing_script.dialogues]
                for dialogue_id in dialogue_ids:
                    self.delete_dialogue_by_id(project_id, page_number, dialogue_id)

            # Get image files
            images_dir = self.path_manager.get_project_images_dir(project_id)
            # Find matching image file, using 3-digit format
            image_files = list(images_dir.glob(f"page_{page_number:03d}.png"))
            if not image_files:
                raise ValueError(f"Image file not found: page_{{page_number:03d}}.png")
            image_file = image_files[0]

            # Get total page count
            all_image_files = sorted(images_dir.glob("page_*.png"))
            total_pages = len(all_image_files)

            # 获取上下文信息
            context = self._get_context(project_id, page_number)

            # 构建提示
            prompt = ""
            if context:
                prompt += f"已经生成的口播稿如下:\n{context}\n\n"

            if page_number == 1:
                prompt += "这是封面页。请生成介绍性的口播稿"
            elif page_number == total_pages:
                prompt += "这是结束页。请生成总结性的口播稿"
            else:
                prompt += f"这是第{page_number}/{total_pages}页。请根据上下文为这张图片生成口播稿"

            # 获取图片字节流
            image_bytes = self._encode_image(image_file)

            # Use AI client to generate dialogues
            dialogues_data: List[DialogueItemAI] = await self.script_client.generate_script_for_image(
                prompt=prompt, image_bytes=image_bytes
            )

            # 转换为DialogueItem对象
            dialogues = []
            for dialogue_data in dialogues_data:
                dialogue = DialogueItem(
                    id=generate_unique_id(),
                    role=dialogue_data.role,
                    content=dialogue_data.content,
                    emotion=dialogue_data.emotion,
                    speed=dialogue_data.speed
                )
                dialogues.append(dialogue)

            # 创建脚本对象
            script = Script(
                id=generate_unique_id(),
                page_number=page_number,
                dialogues=dialogues
            )

            # 保存脚本到文件
            self._save_script(project_id, script)

            logger.info(f"已为页面 {page_number} 生成脚本（共{len(dialogues)}段对话）")
            return script

        except Exception as e:
            logger.error(f"生成脚本失败: {str(e)}")
            raise Exception(f"生成脚本失败: {str(e)}")
            
    def _save_script(self, project_id: str, script: Script) -> None:
        """Save script to file
        
        Args:
            project_id: Project ID
            script: Script object
        """
        # Create scripts directory
        scripts_dir = self.path_manager.get_project_scripts_dir(project_id)
        
        # Save script file, using Pydantic's model_dump_json method
        script_file = scripts_dir / f"script_{script.page_number:03d}.json"
        with open(script_file, 'w', encoding='utf-8') as f:
            f.write(script.model_dump_json(ensure_ascii=False, indent=2))
    
    def get_script(self, project_id: str, page_number: int) -> Optional[Script]:
        """Get script for specified page
        
        Args:
            project_id: Project ID
            page_number: Page number
            
        Returns:
            Script object, returns None if doesn't exist
        """
        try:
            # Get script file
            script_file = self.path_manager.get_project_script_file(project_id, page_number)
            
            if not script_file.exists():
                return None
            
            # 读取脚本文件
            with open(script_file, 'r', encoding='utf-8') as f:
                script_json = f.read()
            
            # 使用Pydantic的parse_raw方法解析JSON
            script = Script.model_validate_json(script_json)
            
            return script
            
        except Exception as e:
            logger.error(f"获取脚本失败: {str(e)}")
            return None
    
    def update_script_by_page_number(self, project_id: str, page_number: int, dialogues: List[DialogueItem]) -> Optional[Script]:
        """根据页码更新脚本
        
        Args:
            project_id: 项目ID
            page_number: 页码
            dialogues: 新的对话列表
            
        Returns:
            更新后的脚本对象，如果失败则返回None
        """
        try:
            # 获取现有脚本
            script = self.get_script(project_id, page_number)
            if not script:
                return None
            
            # 更新对话列表
            script.dialogues = dialogues
            
            # 保存更新后的脚本
            self._save_script(project_id, script)
            
            return script
            
        except Exception as e:
            logger.error(f"更新脚本失败: {str(e)}")
            return None
    
    def update_dialogue_by_id(self, project_id: str, page_number: int, dialogue_id: str, 
                            role: str, content: str, emotion: str, speed: str) -> Optional[DialogueItem]:
        """根据对话ID更新对话项
        
        Args:
            project_id: 项目ID
            page_number: 页码
            dialogue_id: 对话项ID
            role: 角色名称
            content: 对话内容
            emotion: 情感
            speed: 语速
            
        Returns:
            更新后的对话项对象，如果失败则返回None
        """
        try:
            # 获取现有脚本
            script = self.get_script(project_id, page_number)
            if not script:
                return None
            
            # 查找并更新对话项
            for dialogue in script.dialogues:
                if dialogue.id == dialogue_id:
                    dialogue.role = role
                    dialogue.content = content
                    dialogue.emotion = emotion
                    dialogue.speed = speed
                    dialogue.updated_at = datetime.now()
                    
                    # 保存更新后的脚本
                    self._save_script(project_id, script)
                    
                    return dialogue
            
            # 未找到对话项
            return None
            
        except Exception as e:
            logger.error(f"更新对话项失败: {str(e)}")
            return None
    
    def add_dialogue_to_page(self, project_id: str, page_number: int, 
                           role: str, content: str, emotion: str, speed: str) -> Optional[DialogueItem]:
        """向指定页面添加对话项
        
        Args:
            project_id: 项目ID
            page_number: 页码
            role: 角色名称
            content: 对话内容
            emotion: 情感
            speed: 语速
            
        Returns:
            新添加的对话项对象，如果失败则返回None
        """
        try:
            # 获取现有脚本
            script = self.get_script(project_id, page_number)
            if not script:
                return None
            
            # 创建新对话项
            new_dialogue = DialogueItem(
                id=generate_unique_id(),
                role=role,
                content=content,
                emotion=emotion,
                speed=speed
            )
            
            # 添加到脚本
            script.dialogues.append(new_dialogue)
            
            # 保存更新后的脚本
            self._save_script(project_id, script)
            
            return new_dialogue
            
        except Exception as e:
            logger.error(f"添加对话项失败: {str(e)}")
            return None
    
    def delete_dialogue_by_id(self, project_id: str, page_number: int, dialogue_id: str) -> Optional[DialogueItem]:
        """根据对话ID删除对话项
        
        Args:
            project_id: 项目ID
            page_number: 页码
            dialogue_id: 对话项ID
            
        Returns:
            被删除的对话项对象，如果失败则返回None
        """
        try:
            # 获取现有脚本
            script = self.get_script(project_id, page_number)
            if not script:
                return None
            
            # 查找并删除对话项
            for i, dialogue in enumerate(script.dialogues):
                if dialogue.id == dialogue_id:
                    # 保存被删除的对话项
                    deleted_dialogue = dialogue
                    
                    # 从列表中删除
                    script.dialogues.pop(i)
                    
                    # 保存更新后的脚本
                    self._save_script(project_id, script)
                    
                    # 尝试删除对应的音频文件
                    self._delete_dialogue_audio(project_id, page_number, dialogue_id)
                    
                    # 尝试重新生成页面音频
                    self._regenerate_page_audio(project_id, page_number)
                    
                    return deleted_dialogue
            
            # 未找到对话项
            return None
            
        except Exception as e:
            logger.error(f"删除对话项失败: {str(e)}")
            return None
    
    def move_dialogue_by_id(self, project_id: str, page_number: int, dialogue_id: str, direction: str) -> Optional[DialogueItem]:
        """根据对话ID移动对话项
        
        Args:
            project_id: 项目ID
            page_number: 页码
            dialogue_id: 对话项ID
            direction: 移动方向，'up'表示上移，'down'表示下移
            
        Returns:
            被移动的对话项对象，如果失败则返回None
        """
        try:
            # 获取现有脚本
            script = self.get_script(project_id, page_number)
            if not script:
                return None
            
            # 查找对话项索引
            current_index = -1
            for i, dialogue in enumerate(script.dialogues):
                if dialogue.id == dialogue_id:
                    current_index = i
                    break
            
            if current_index == -1:
                return None
            
            # 检查移动方向的有效性
            if direction == 'up':
                if current_index == 0:
                    return script.dialogues[current_index]
                # 交换位置
                script.dialogues[current_index], script.dialogues[current_index - 1] = \
                    script.dialogues[current_index - 1], script.dialogues[current_index]
            elif direction == 'down':
                if current_index == len(script.dialogues) - 1:
                    return script.dialogues[current_index]
                # 交换位置
                script.dialogues[current_index], script.dialogues[current_index + 1] = \
                    script.dialogues[current_index + 1], script.dialogues[current_index]
            else:
                return None
            
            # 更新移动项的updated_at时间戳
            script.dialogues[current_index].updated_at = datetime.now()
            if direction == 'up':
                script.dialogues[current_index - 1].updated_at = datetime.now()
            else:
                script.dialogues[current_index + 1].updated_at = datetime.now()
            
            # 保存更新后的脚本
            self._save_script(project_id, script)
            
            # 重新生成页面音频
            self._regenerate_page_audio(project_id, page_number)
            
            return script.dialogues[current_index if direction == 'up' else current_index - 1]
            
        except Exception as e:
            logger.error(f"移动对话项失败: {str(e)}")
            return None
    
    def _delete_dialogue_audio(self, project_id: str, page_number: int, dialogue_id: str) -> None:
        """Delete audio file for dialogue item

        Args:
            project_id: Project ID
            page_number: Page number
            dialogue_id: Dialogue ID
        """
        try:
            audio_file_path = self.path_manager.get_project_dialogue_audio_file(project_id, page_number, dialogue_id)

            if audio_file_path.exists():
                audio_file_path.unlink()
                logger.info(f"Deleted dialogue audio file: {audio_file_path}")

        except Exception as e:
            logger.error(f"Failed to delete dialogue audio file: {str(e)}")

    def _regenerate_page_audio(self, project_id: str, page_number: int) -> None:
        """Regenerate page audio file after dialogue modification (move/delete)

        Args:
            project_id: Project ID
            page_number: Page number
        """
        try:
            from app.services.audio_service import AudioService

            audio_service = AudioService()
            audio_service._regenerate_page_audio(project_id, page_number)

        except Exception as e:
            logger.error(f"Failed to regenerate page audio after modification: {str(e)}")
    
    async def batch_generate_scripts(self, project_id: str, task_id: Optional[str] = None) -> List[Script]:
        """批量生成脚本
        
        Args:
            project_id: 项目ID
            task_id: 任务ID，用于进度追踪
            
        Returns:
            生成的脚本列表
            
        Raises:
            Exception: 生成失败时抛出异常
        """
        try:
            # 获取项目目录
            project_dir = self.path_manager.get_project_dir(project_id)
            if not project_dir.exists():
                raise ValueError(f"项目目录不存在: {project_dir}")
            
            # 获取图片目录
            images_dir = project_dir / "images"
            if not images_dir.exists():
                raise ValueError(f"图片目录不存在: {images_dir}")
            
            # 获取所有图片文件
            image_files = sorted(images_dir.glob("page_*.png"))
            if not image_files:
                raise ValueError("没有找到图片文件")
            
            # 生成脚本列表
            scripts = []
            
            # 逐页生成脚本
            for i, image_file in enumerate(image_files):
                page_number = i + 1
                
                # 生成脚本
                script = await self.generate_script_for_page(project_id, page_number, task_id)
                scripts.append(script)
                
                # 更新任务进度
                if task_id:
                    from app.services.task_service import TaskService
                    task_service = TaskService()
                    task_service.increment_task_progress(task_id)
            
            logger.info(f"已为项目 {project_id} 批量生成 {len(scripts)} 个脚本")
            return scripts
            
        except Exception as e:
            logger.error(f"批量生成脚本失败: {str(e)}")
            raise Exception(f"批量生成脚本失败: {str(e)}")
