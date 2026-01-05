import os
import json
import asyncio
from pathlib import Path
from typing import List, Optional, Dict, Any, Literal
import logging
import httpx
import binascii
from pydub import AudioSegment
from io import BytesIO

from app.models import DialogueItem, Script, TaskStatus
from app.utils.file_utils import generate_unique_id, ensure_directory
from app.config import config_manager

logger = logging.getLogger(__name__)


class AudioService:
    """音频处理服务类"""
    
    def __init__(self, storage_dir: Optional[str] = None):
        """初始化音频服务
        
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
        
        # 项目根目录
        self.project_root = Path(__file__).parent.parent.parent.parent
        
        # 加载配置
        config = config_manager.get_config()
        
        # 初始化MiniMax API配置
        self.group_id = config.env.MINIMAX_AUDIO_GROUP_ID
        self.api_key = config.env.MINIMAX_AUDIO_API_KEY
        self.model = config.env.MINIMAX_AUDIO_MODEL
        self.url = f"https://api.minimax.chat/v1/t2a_v2?GroupId={self.group_id}"
        
        # 加载角色配置
        self.role_voice_map = config.roles.mapping
        
        # 语速映射
        self.speed_map = {
            "慢": 0.8,
            "正常": 1.0,
            "快": 1.25
        }
        
        # 音频设置
        self.audio_setting = {
            "sample_rate": 32000,
            "bitrate": 128000,
            "format": "mp3"
        }
        
        # 基础payload模板
        self.base_payload = {
            "model": self.model,
            "timbre_weights": [
                {
                    "voice_id": "",  # 将在具体方法中设置
                    "weight": 100
                }
            ],
            "voice_setting": {
                "voice_id": "",
                "speed": 1.0,  # 将在具体方法中设置
                "pitch": 0,
                "vol": 1,
                "latex_read": True
            },
            "audio_setting": self.audio_setting,
            "language_boost": "auto"
        }
        
        # 创建httpx客户端
        self.client = httpx.AsyncClient(
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            },
            timeout=60.0
        )
    
    async def __aenter__(self):
        """异步上下文管理器入口"""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """异步上下文管理器出口"""
        await self.client.aclose()
    
    async def _build_payload(self, text: str, role: str, emotion: str, speed: str, is_daoju: bool = False) -> Dict[str, Any]:
        """构建请求payload
        
        Args:
            text: 文本内容
            role: 角色名称
            emotion: 情感
            speed: 语速
            is_daoju: 是否为道具
            
        Returns:
            构建好的payload
        """
        # 复制基础payload
        payload = json.loads(json.dumps(self.base_payload))
        
        # 设置文本
        payload["text"] = text
        
        # 设置角色
        if is_daoju:
            voice_id = self.role_voice_map.get("哆啦A梦", self.role_voice_map.get("其他", "Chinese (Mandarin)_Radio_Host"))
            payload["voice_setting"]["emotion"] = "happy"
            payload["voice_setting"]["latex_read"] = False
        else:
            voice_id = self.role_voice_map.get(role, self.role_voice_map.get("其他", "Chinese (Mandarin)_Radio_Host"))
            payload["voice_setting"]["latex_read"] = True
        
        # 设置语速
        payload["voice_setting"]["speed"] = self.speed_map.get(speed, 1.0)
        
        # 设置角色ID
        payload["timbre_weights"][0]["voice_id"] = voice_id
        
        # 只有当emotion不是"auto"时才添加emotion字段
        if emotion != "auto" and not is_daoju:
            payload["voice_setting"]["emotion"] = emotion
        
        return payload
    
    def _is_api_response_valid(self, result: Dict[str, Any]) -> tuple:
        """检查API响应是否有效
        
        Args:
            result: API响应结果
            
        Returns:
            (is_valid, error_message) 元组
        """
        if "base_resp" not in result:
            return False, "API响应中缺少'base_resp'字段"
        
        base_resp = result["base_resp"]
        status_code = base_resp.get("status_code", -1)
        status_msg = base_resp.get("status_msg", "")
        
        if status_code != 0:
            return False, f"API返回错误码 {status_code}: {status_msg}"
        
        if "data" not in result or result["data"] is None:
            return False, "API响应中缺少'data'字段或data为null"
        
        if "audio" not in result["data"]:
            return False, "API响应中缺少'audio'字段"
        
        return True, ""
    
    async def _request_audio(self, payload: Dict[str, Any]) -> Optional[bytes]:
        """发送请求获取音频数据
        
        Args:
            payload: 请求payload
            
        Returns:
            音频字节数据，失败时返回None
        """
        max_retries = 3
        base_delay = 5
        
        for attempt in range(1, max_retries + 1):
            try:
                response = await self.client.post(self.url, json=payload)
                response.raise_for_status()
                result = response.json()
                
                is_valid, error_message = self._is_api_response_valid(result)
                if not is_valid:
                    logger.warning(f"API响应验证失败（第{attempt}次尝试）: {error_message}")
                    
                    if attempt < max_retries:
                        await asyncio.sleep(base_delay)
                        continue
                    else:
                        logger.error(f"重试次数耗尽，API响应验证失败: {error_message}")
                        return None
                
                audio_bytes = binascii.unhexlify(result["data"]["audio"])
                await asyncio.sleep(5)
                return audio_bytes
                
            except httpx.HTTPError as e:
                logger.warning(f"HTTP请求失败（第{attempt}次尝试）: {str(e)}")
                
                if attempt < max_retries:
                    await asyncio.sleep(base_delay)
                else:
                    logger.error(f"重试次数耗尽，HTTP请求最终失败: {str(e)}")
                    return None
                    
            except (binascii.Error, ValueError, KeyError) as e:
                logger.warning(f"音频数据处理失败（第{attempt}次尝试）: {str(e)}")
                
                if attempt < max_retries:
                    await asyncio.sleep(base_delay)
                else:
                    logger.error(f"重试次数耗尽，音频数据处理最终失败: {str(e)}")
                    return None
        
        return None
    
    async def _merge_audio_with_daoju(self, audio_bytes: bytes) -> bytes:
        """将音频与道具音效合并
        
        Args:
            audio_bytes: 原始音频字节数据
            
        Returns:
            合并后的音频字节数据
        """
        try:
            # 道具音效路径
            daoju_audio_path = self.project_root / "backend" / "assets" / "gadgets.mp3"
            
            # 加载道具音效
            daoju_audio = AudioSegment.from_mp3(str(daoju_audio_path))
            
            # 将音频字节数据转换为AudioSegment
            audio = AudioSegment.from_mp3(BytesIO(audio_bytes))
            
            # 合并音频
            combined_audio = daoju_audio + audio
            
            # 将合并后的音频转换为字节数据
            buffer = BytesIO()
            combined_audio.export(buffer, format="mp3")
            return buffer.getvalue()
        except Exception as e:
            logger.error(f"合并道具音频失败: {e}")
            # 如果合并失败，返回原始音频
            return audio_bytes
    
    async def generate_audio_for_dialogue(self, dialogue: DialogueItem, project_id: str, page_number: int, regenerate_page_audio: bool = True) -> str:
        """为单个对话项生成音频，并可选择重新合成页面音频
        
        Args:
            dialogue: 对话项对象
            project_id: 项目ID
            page_number: 页码
            regenerate_page_audio: 是否重新生成页面音频以确保一致性，默认为True
            
        Returns:
            生成的音频文件路径
            
        Raises:
            Exception: 生成失败时抛出异常
        """
        try:
            # 创建页面音频目录
            page_audio_dir = self.storage_dir / project_id / "audio" / f"page_{page_number:03d}"
            ensure_directory(page_audio_dir)
            
            # 生成音频文件路径
            audio_file_path = page_audio_dir / f"{dialogue.id}.mp3"
            
            # 根据角色类型选择不同的生成方法
            is_daoju = dialogue.role == "道具"
            payload = await self._build_payload(
                dialogue.content, dialogue.role, dialogue.emotion, dialogue.speed, is_daoju
            )
            
            # 生成音频
            audio_bytes = await self._request_audio(payload)
            
            if audio_bytes is None:
                raise Exception("音频生成失败，API请求重试次数耗尽")
            
            # 如果是道具，添加道具音效
            if is_daoju:
                audio_bytes = await self._merge_audio_with_daoju(audio_bytes)
            
            # 保存音频文件
            with open(audio_file_path, "wb") as f:
                f.write(audio_bytes)
            
            logger.info(f"已为对话 {dialogue.id} 生成音频: {audio_file_path}")
            
            # 如果需要重新生成页面音频
            if regenerate_page_audio:
                self._regenerate_page_audio(project_id, page_number)
            
            return str(audio_file_path)
            
        except Exception as e:
            logger.error(f"生成音频失败: {str(e)}")
            raise Exception(f"生成音频失败: {str(e)}")
    
    def _regenerate_page_audio(self, project_id: str, page_number: int) -> None:
        """重新生成页面音频
        
        Args:
            project_id: 项目ID
            page_number: 页码
            
        Raises:
            Exception: 生成失败时抛出异常
        """
        try:
            # 获取脚本文件
            scripts_dir = self.storage_dir / project_id / "scripts"
            script_file = scripts_dir / f"script_{page_number:03d}.json"
            
            if not script_file.exists():
                raise ValueError(f"脚本文件不存在: {script_file}")
            
            # 读取脚本文件
            with open(script_file, 'r', encoding='utf-8') as f:
                script_json = f.read()
            
            # 解析脚本
            script = Script.model_validate_json(script_json)
            
            # 创建页面音频目录
            page_audio_dir = self.storage_dir / project_id / "audio" / f"page_{page_number:03d}"
            ensure_directory(page_audio_dir)
            
            audio_files = []
            
            # 开场音频路径
            begin_audio_path = self.project_root / "backend" / "assets" / "cues.mp3"
            
            # 如果是第一页，先添加begin.mp3
            if page_number == 1 and begin_audio_path.exists():
                begin_audio_file = page_audio_dir / "beigin.mp3"
                if not begin_audio_file.exists():
                    import shutil
                    shutil.copy(str(begin_audio_path), str(begin_audio_file))
                audio_files.append(str(begin_audio_file))
            
            # 收集所有已存在的对话音频文件
            for dialogue in script.dialogues:
                dialogue_audio_path = page_audio_dir / f"{dialogue.id}.mp3"
                if dialogue_audio_path.exists():
                    audio_files.append(str(dialogue_audio_path))
            
            # 如果有音频文件，合并它们
            if audio_files:
                # 创建音频目录
                audio_dir = self.storage_dir / project_id / "audio"
                ensure_directory(audio_dir)
                
                # 页面音频文件路径
                page_output_path = audio_dir / f"page_{page_number:03d}.mp3"
                
                # 合并音频文件
                self.merge_audio_files(audio_files, str(page_output_path))
                
                logger.info(f"已重新生成页面 {page_number} 的合并音频: {page_output_path}")
            else:
                logger.warning(f"页面 {page_number} 没有找到任何音频文件")
                
        except Exception as e:
            logger.error(f"重新生成页面音频失败: {str(e)}")
            raise Exception(f"重新生成页面音频失败: {str(e)}")
    
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
        """为指定页面生成音频
        
        Args:
            project_id: 项目ID
            page_number: 页码
            task_id: 任务ID，用于进度追踪
            
        Returns:
            生成的页面音频文件路径
            
        Raises:
            Exception: 生成失败时抛出异常
        """
        try:
            # 获取脚本文件
            scripts_dir = self.storage_dir / project_id / "scripts"
            script_file = scripts_dir / f"script_{page_number:03d}.json"
            
            if not script_file.exists():
                raise ValueError(f"脚本文件不存在: {script_file}")
            
            # 读取脚本文件
            with open(script_file, 'r', encoding='utf-8') as f:
                script_json = f.read()
            
            # 解析脚本
            script = Script.model_validate_json(script_json)
            
            # 创建页面音频目录
            page_audio_dir = self.storage_dir / project_id / "audio" / f"page_{page_number:03d}"
            ensure_directory(page_audio_dir)
            
            # 开场音频路径
            begin_audio_path = self.project_root / "backend" / "assets" / "cues.mp3"
            
            audio_files = []
            
            # 如果是第一页，先添加cues.mp3
            if page_number == 1 and begin_audio_path.exists():
                begin_audio_file = page_audio_dir / "beigin.mp3"
                # 复制cues.mp3到页面目录
                import shutil
                shutil.copy(str(begin_audio_path), str(begin_audio_file))
                audio_files.append(str(begin_audio_file))
                logger.info(f"已添加开场音频: {begin_audio_file}")
            
            # 为每个对话生成音频
            for dialogue in script.dialogues:
                try:
                    # 生成音频文件路径，不重新生成页面音频
                    audio_file_path = await self.generate_audio_for_dialogue(dialogue, project_id, page_number, regenerate_page_audio=False)
                    audio_files.append(audio_file_path)
                    
                    # 更新任务进度
                    if task_id:
                        from app.services.task_service import TaskService
                        task_service = TaskService()
                        task_service.increment_task_progress(task_id)
                        
                except Exception as e:
                    logger.error(f"为对话 {dialogue.id} 生成音频失败: {str(e)}")
                    continue
            
            # 合并当前页面的所有音频
            if audio_files:
                # 创建音频目录
                audio_dir = self.storage_dir / project_id / "audio"
                ensure_directory(audio_dir)
                
                # 页面音频文件路径
                page_output_path = audio_dir / f"page_{page_number:03d}.mp3"
                
                # 合并音频文件
                self.merge_audio_files(audio_files, str(page_output_path))
                
                logger.info(f"已为页面 {page_number} 生成合并音频: {page_output_path}")
                return str(page_output_path)
            else:
                raise ValueError(f"页面 {page_number} 没有成功生成任何音频文件")
                
        except Exception as e:
            logger.error(f"生成页面音频失败: {str(e)}")
            raise Exception(f"生成页面音频失败: {str(e)}")
    
    async def batch_generate_audio(self, project_id: str, task_id: Optional[str] = None) -> List[str]:
        """批量生成音频
        
        Args:
            project_id: 项目ID
            task_id: 任务ID，用于进度追踪
            
        Returns:
            生成的页面音频文件路径列表
            
        Raises:
            Exception: 生成失败时抛出异常
        """
        try:
            # 获取项目目录
            project_dir = self.storage_dir / project_id
            if not project_dir.exists():
                raise ValueError(f"项目目录不存在: {project_dir}")
            
            # 获取脚本目录
            scripts_dir = project_dir / "scripts"
            if not scripts_dir.exists():
                raise ValueError(f"脚本目录不存在: {scripts_dir}")
            
            # 获取所有脚本文件
            script_files = sorted(scripts_dir.glob("script_*.json"))
            if not script_files:
                raise ValueError("没有找到脚本文件")
            
            # 生成音频文件路径列表
            audio_files = []
            
            # 逐页生成音频
            for script_file in script_files:
                # 从文件名提取页码
                page_number = int(script_file.stem.split("_")[1])
                
                # 生成页面音频
                page_audio_path = await self.generate_audio_for_page(project_id, page_number)
                audio_files.append(page_audio_path)

                # 更新任务进度
                if task_id:
                    from app.services.task_service import TaskService
                    task_service = TaskService()
                    task_service.increment_task_progress(task_id)
            
            logger.info(f"已为项目 {project_id} 批量生成 {len(audio_files)} 个页面音频")
            return audio_files
            
        except Exception as e:
            logger.error(f"批量生成音频失败: {str(e)}")
            raise Exception(f"批量生成音频失败: {str(e)}")
    
    def get_audio_file_path(self, project_id: str, page_number: int) -> Optional[bytes]:
        """获取页面音频文件内容
        
        Args:
            project_id: 项目ID
            page_number: 页码
            
        Returns:
            音频文件内容(字节)，如果不存在则返回None
        """
        audio_file = self.storage_dir / project_id / "audio" / f"page_{page_number:03d}.mp3"
        if audio_file.exists():
            with open(audio_file, "rb") as f:
                return f.read()
        return None
    
    def get_dialogue_audio_file_path(self, project_id: str, page_number: int, dialogue_id: str) -> Optional[bytes]:
        """获取对话音频文件内容
        
        Args:
            project_id: 项目ID
            page_number: 页码
            dialogue_id: 对话ID
            
        Returns:
            音频文件内容(字节)，如果不存在则返回None
        """
        audio_file = self.storage_dir / project_id / "audio" / f"page_{page_number:03d}" / f"{dialogue_id}.mp3"
        if audio_file.exists():
            with open(audio_file, "rb") as f:
                return f.read()
        return None