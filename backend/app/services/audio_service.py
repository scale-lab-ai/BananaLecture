import shutil
from typing import List, Optional
import logging
from io import BytesIO
from pathlib import Path

from pydub import AudioSegment

from app.models import DialogueItem, Script
from app.core.path_manager import PathManager
from app.core.audio_client import AudioClient
from app.config import config_manager

logger = logging.getLogger(__name__)


class AudioService:
    """音频处理服务类"""

    def __init__(self):
        """Initialize audio service

        Args:
            path_manager: Path manager instance
            audio_client: Audio client instance for AI interaction
        """
        self.path_manager = PathManager()
        self.audio_client = AudioClient()

    async def __aenter__(self):
        """异步上下文管理器入口"""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """异步上下文管理器出口"""
        await self.audio_client.__aexit__(exc_type, exc_val, exc_tb)

    async def _merge_audio_with_gadgets(self, audio_bytes: bytes) -> bytes:
        """Merge audio with gadget sound effect

        Args:
            audio_bytes: Original audio byte data

        Returns:
            Merged audio byte data
        """
        try:
            gadgets_audio_path = self.path_manager.get_gadgets_audio_path()
            gadgets_audio = AudioSegment.from_mp3(str(gadgets_audio_path))
            audio = AudioSegment.from_mp3(BytesIO(audio_bytes))
            combined_audio = gadgets_audio + audio

            buffer = BytesIO()
            combined_audio.export(buffer, format="mp3")
            return buffer.getvalue()
        except Exception as e:
            logger.error(f"合并道具音频失败: {e}")
            return audio_bytes

    async def _generate_single_dialogue_audio(self, 
        dialogue: DialogueItem
    ) -> Optional[bytes]:
        """Generate audio bytes for a single dialogue item

        Args:
            dialogue: Dialogue item object

        Returns:
            Audio bytes if successful, None otherwise
        """
        try:
            audio_bytes = await self.audio_client.generate_audio(dialogue.content, dialogue.role, dialogue.emotion, dialogue.speed)

            if audio_bytes is None:
                logger.error(f"音频生成失败，对话ID: {dialogue.id}")
                return None

            if dialogue.role == "道具" and config_manager.get_current_group() == "Doraemon":
                audio_bytes = await self._merge_audio_with_gadgets(audio_bytes)

            return audio_bytes
        except Exception as e:
            logger.error(f"生成单个对话音频失败: {str(e)}")
            return None

    async def generate_audio_for_dialogue(
        self, dialogue: DialogueItem, project_id: str, page_number: int, regenerate_page_audio: bool = True
    ) -> str:
        """Generate audio for a single dialogue item, with option to regenerate page audio

        Args:
            dialogue: Dialogue item object
            project_id: Project ID
            page_number: Page number
            regenerate_page_audio: Whether to regenerate page audio for consistency, default True

        Returns:
            Generated audio file path

        Raises:
            Exception: Raises exception on generation failure
        """
        try:
            page_audio_dir = self.path_manager.get_project_page_audio_dir(project_id, page_number)
            audio_file_path = page_audio_dir / f"{dialogue.id}.mp3"

            audio_bytes = await self._generate_single_dialogue_audio(dialogue)
            if audio_bytes is None:
                raise Exception("音频生成失败，API请求重试次数耗尽")

            with open(audio_file_path, "wb") as f:
                f.write(audio_bytes)

            logger.info(f"已为对话 {dialogue.id} 生成音频: {audio_file_path}")

            if regenerate_page_audio:
                self._regenerate_page_audio(project_id, page_number)

            return str(audio_file_path)

        except Exception as e:
            logger.error(f"生成音频失败: {str(e)}")
            raise Exception(f"生成音频失败: {str(e)}")

    def _read_script(self, project_id: str, page_number: int) -> Optional[Script]:
        """Read and parse script file

        Args:
            project_id: Project ID
            page_number: Page number

        Returns:
            Script object, None if not exists or on error
        """
        try:
            script_file = self.path_manager.get_project_script_file(project_id, page_number)
            if not script_file.exists():
                return None

            with open(script_file, "r", encoding="utf-8") as f:
                script_json = f.read()

            return Script.model_validate_json(script_json)
        except Exception as e:
            logger.error(f"Failed to read script file: {str(e)}")
            return None

    def _get_page_audio_files_ordered(
        self, project_id: str, page_number: int, script: Optional[Script] = None
    ) -> List[str]:
        """Collect all audio files for a page in order

        Args:
            project_id: Project ID
            page_number: Page number
            script: Script object, will be read if not provided

        Returns:
            List of audio file paths
        """
        audio_files = []

        try:
            if script is None:
                script = self._read_script(project_id, page_number)
            if script is None:
                return audio_files

            page_audio_dir = self.path_manager.get_project_page_audio_dir(project_id, page_number)

            if page_number == 1 and config_manager.get_current_group() == "Doraemon":
                begin_audio_file = page_audio_dir / "begin.mp3"
                if begin_audio_file.exists():
                    audio_files.append(str(begin_audio_file))

            for dialogue in script.dialogues:
                dialogue_audio_path = page_audio_dir / f"{dialogue.id}.mp3"
                if dialogue_audio_path.exists():
                    audio_files.append(str(dialogue_audio_path))

        except Exception as e:
            logger.error(f"Failed to collect page audio files: {str(e)}")

        return audio_files

    def merge_page_audio_files(
        self, project_id: str, page_number: int, audio_files: Optional[List[str]] = None
    ) -> Optional[str]:
        """Merge audio files for a page and save to output path

        Args:
            project_id: Project ID
            page_number: Page number
            audio_files: List of audio file paths to merge, will collect if not provided

        Returns:
            Output file path if successful, None otherwise
        """
        try:
            if audio_files is None:
                script = self._read_script(project_id, page_number)
                audio_files = self._get_page_audio_files_ordered(project_id, page_number, script)

            if not audio_files:
                return None

            audio_dir = self.path_manager.get_project_audio_dir(project_id)
            page_output_path = audio_dir / f"page_{page_number:03d}.mp3"

            self.merge_audio_files(audio_files, str(page_output_path))
            logger.info(f"Merged audio for page {page_number}: {page_output_path}")
            return str(page_output_path)
        except Exception as e:
            logger.error(f"Failed to merge page audio files: {str(e)}")
            return None

    def _regenerate_page_audio(self, project_id: str, page_number: int) -> None:
        """Regenerate page audio

        Args:
            project_id: Project ID
            page_number: Page number

        Raises:
            Exception: Raises exception on generation failure
        """
        try:
            result = self.merge_page_audio_files(project_id, page_number)
            if result is None:
                logger.warning(f"Page {page_number} has no audio files found")
        except Exception as e:
            logger.error(f"Failed to regenerate page audio: {str(e)}")
            raise Exception(f"Failed to regenerate page audio: {str(e)}")

    def merge_audio_files(self, audio_files: List[str], output_path: str) -> None:
        """合并多个音频文件为一个

        Args:
            audio_files: 要合并的音频文件列表
            output_path: 输出文件路径
        """
        if not audio_files:
            return

        try:
            combined = AudioSegment.empty()
            for audio_file in audio_files:
                audio = AudioSegment.from_mp3(audio_file)
                combined += audio

            combined.export(output_path, format="mp3")
            logger.info(f"成功合并音频: {output_path}")
        except Exception as e:
            logger.error(f"合并音频失败: {e}")
            raise
    
    def merge_audio_files(self, audio_files: List[str], output_path: str) -> None:
        """
        合并多个音频文件为一个
        
        Args:
            audio_files: 要合并的音频文件列表
            output_path: 输出文件路径
        """
        if not audio_files:
            return
            
        try:
            combined = AudioSegment.empty()
            for audio_file in audio_files:
                audio = AudioSegment.from_mp3(audio_file)
                combined += audio
            
            combined.export(output_path, format="mp3")
            logger.info(f"成功合并音频: {output_path}")
        except Exception as e:
            logger.error(f"合并音频失败: {e}")
            raise
    
    async def generate_audio_for_page(self, project_id: str, page_number: int, task_id: Optional[str] = None) -> str:
        """Generate audio for specified page

        Args:
            project_id: Project ID
            page_number: Page number
            task_id: Task ID for progress tracking

        Returns:
            Generated page audio file path

        Raises:
            Exception: Raises exception on generation failure
        """
        try:
            script = self._read_script(project_id, page_number)
            if script is None:
                raise ValueError(f"Script file not found for page {page_number}")

            page_audio_dir = self.path_manager.get_project_page_audio_dir(project_id, page_number)

            audio_files = []

            if page_number == 1 and config_manager.get_current_group() == "Doraemon":
                begin_audio_path = self.path_manager.get_cues_audio_path()
                if begin_audio_path.exists():
                    begin_audio_file = page_audio_dir / "begin.mp3"
                    if not begin_audio_file.exists():
                        shutil.copy(str(begin_audio_path), str(begin_audio_file))
                    audio_files.append(str(begin_audio_file))
                    logger.info(f"Added opening audio: {begin_audio_file}")

            for dialogue in script.dialogues:
                try:
                    audio_file_path = await self.generate_audio_for_dialogue(dialogue, project_id, page_number, regenerate_page_audio=False)
                    audio_files.append(audio_file_path)

                    if task_id:
                        from app.services.task_service import TaskService
                        task_service = TaskService()
                        task_service.increment_task_progress(task_id)

                except Exception as e:
                    logger.error(f"Failed to generate audio for dialogue {dialogue.id}: {str(e)}")
                    continue

            if audio_files:
                result = self.merge_page_audio_files(project_id, page_number, audio_files)
                if result:
                    return result
                raise ValueError(f"Failed to merge audio for page {page_number}")
            else:
                raise ValueError(f"Page {page_number} has no successfully generated audio files")

        except Exception as e:
            logger.error(f"Failed to generate page audio: {str(e)}")
            raise Exception(f"Failed to generate page audio: {str(e)}")
    
    async def batch_generate_audio(self, project_id: str, task_id: Optional[str] = None) -> List[str]:
        """Batch generate audio
        
        Args:
            project_id: Project ID
            task_id: Task ID for progress tracking
            
        Returns:
            List of generated page audio file paths
            
        Raises:
            Exception: Raises exception on generation failure
        """
        try:
            # Get project directory
            project_dir = self.path_manager.get_project_dir(project_id)
            if not project_dir.exists():
                raise ValueError(f"Project directory not found: {project_dir}")
            
            # Get scripts directory
            scripts_dir = self.path_manager.get_project_scripts_dir(project_id)
            if not scripts_dir.exists():
                raise ValueError(f"Scripts directory not found: {scripts_dir}")
            
            # Get all script files
            script_files = sorted(scripts_dir.glob("script_*.json"))
            if not script_files:
                raise ValueError("No script files found")
            
            # Generate list of audio file paths
            audio_files = []
            
            # Generate audio page by page
            for script_file in script_files:
                # Extract page number from filename
                page_number = int(script_file.stem.split("_")[1])
                
                # Generate page audio
                page_audio_path = await self.generate_audio_for_page(project_id, page_number)
                audio_files.append(page_audio_path)

                # Update task progress
                if task_id:
                    from app.services.task_service import TaskService
                    task_service = TaskService()
                    task_service.increment_task_progress(task_id)
            
            logger.info(f"Batch generated {len(audio_files)} page audio files for project {project_id}")
            return audio_files
            
        except Exception as e:
            logger.error(f"Failed to batch generate audio: {str(e)}")
            raise Exception(f"Failed to batch generate audio: {str(e)}")
    
    def get_audio_file_path(self, project_id: str, page_number: int) -> Optional[bytes]:
        """Get page audio file content
        
        Args:
            project_id: Project ID
            page_number: Page number
            
        Returns:
            Audio file content (bytes), returns None if not exists
        """
        audio_file = self.path_manager.get_project_page_audio_file(project_id, page_number)
        if audio_file.exists():
            with open(audio_file, "rb") as f:
                return f.read()
        return None
    
    def get_dialogue_audio_file_path(self, project_id: str, page_number: int, dialogue_id: str) -> Optional[bytes]:
        """Get dialogue audio file content
        
        Args:
            project_id: Project ID
            page_number: Page number
            dialogue_id: Dialogue ID
            
        Returns:
            Audio file content (bytes), returns None if not exists
        """
        audio_file = self.path_manager.get_project_dialogue_audio_file(project_id, page_number, dialogue_id)
        if audio_file.exists():
            with open(audio_file, "rb") as f:
                return f.read()
        return None