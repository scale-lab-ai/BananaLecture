import os
import json
from pathlib import Path
from typing import List, Optional, Dict, Any, Literal
import logging
from datetime import datetime
import asyncio

from app.models import Script, DialogueItem, Project, Image
from app.utils.file_utils import generate_unique_id, ensure_directory
from pydantic import BaseModel, Field
from pydantic_ai import Agent, BinaryContent
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.providers.openai import OpenAIProvider
from app.config import config_manager

logger = logging.getLogger(__name__)


class DialogueItemAI(BaseModel):
    """对话项模型 - 继承自 BaseModel，Pydantic AI 会自动验证"""
    role: Literal["旁白", "大雄", "哆啦A梦", "道具", "其他男声", "其他女声", "其他"] = Field(..., description="说话的角色名称")
    content: str = Field(..., description="口播稿具体内容")
    emotion: Literal["auto", "happy", "sad", "angry", "fearful", "disgusted", "surprised", "neutral", "fluent"] = Field("auto", description="对话的情感, 若未表现出明显情感, 则为auto")
    speed: Literal["慢", "正常", "快"] = Field("正常", description="对话的语速")


class ScriptService:
    """脚本处理服务类"""
    
    def __init__(self, storage_dir: Optional[str] = None):
        """初始化脚本服务
        
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
        
        # 初始化AI代理
        self._init_agent()
    
    def _init_agent(self):
        """初始化AI代理"""
        config = config_manager.get_config()
        
        model = OpenAIChatModel(
            config.env.LLM_OPENAI_MODEL, 
            provider=OpenAIProvider(
                api_key=config.env.LLM_OPENAI_API_KEY,
                base_url=config.env.LLM_OPENAI_BASE_URL
            )
        )
        
        self.agent = Agent(
            model=model,
            output_type=List[DialogueItemAI],  # 返回对话列表
            system_prompt="""你是一个专业的口播稿生成助手,你需要根据已经生成的口播稿上下文,将提供的图片转换为生动有趣的对话稿。

要求：
1. 角色可以是旁白、大雄、哆啦A梦等，确保角色与对话内容严格对齐
2. 内容要简洁明了，适合口头表达
3. 语言要生动有趣，吸引听众
4. 为每个对话项设置合适的情感和语速

注意事项:
1. 道具为特殊role，当且仅当哆啦A梦首次掏出道具时，添加角色为道具内容为道具名称的对话，后续出现时无需重复添加(**仅添加一次即可**)
2. 图片中所有出现的公式与数学符号均转化为Latex格式,并都用$$包裹,如$$E = m \\times c^2$$与$$1-\\epsilon$$""",
        )
    
    async def _retry_with_exponential_backoff(self, coro, max_retries: int = 3, base_delay: float = 5.0):
        """带指数退避的重试机制
        
        Args:
            coro: 异步协程函数
            max_retries: 最大重试次数，默认为3
            base_delay: 基础延迟时间（秒），默认为5
            
        Returns:
            协程执行结果
            
        Raises:
            Exception: 重试次数耗尽后抛出异常
        """
        last_exception = None
        
        for attempt in range(1, max_retries + 1):
            try:
                return await coro
            except Exception as e:
                last_exception = e
                logger.warning(f"第 {attempt} 次尝试失败: {str(e)}")
                
                if attempt < max_retries:
                    delay = base_delay
                    logger.info(f"等待 {delay} 秒后进行第 {attempt + 1} 次重试...")
                    await asyncio.sleep(delay)
                else:
                    logger.error(f"重试次数耗尽，最终失败: {str(e)}")
                    raise
    
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
        """
        获取上下文信息，即之前页面的脚本内容
        
        Args:
            project_id: 项目ID
            page_number: 当前页码
            
        Returns:
            上下文字符串
        """
        context = ""
        
        # 获取脚本目录
        scripts_dir = self.storage_dir / project_id / "scripts"
        
        # 遍历之前页面的脚本文件
        for i in range(1, page_number):
            script_file = scripts_dir / f"script_{i:03d}.json"
            if script_file.exists():
                try:
                    with open(script_file, 'r', encoding='utf-8') as f:
                        script_data = json.load(f)
                        
                    # 转换为易读的文本格式
                    for dialogue in script_data.get("dialogues", []):
                        context += f"{dialogue.get('role', '')}: {dialogue.get('content', '')}\n"
                        
                except Exception as e:
                    logger.error(f"读取脚本文件 {script_file} 失败: {str(e)}")
        
        return context
    
    async def generate_script_for_page(self, project_id: str, page_number: int, task_id: Optional[str] = None) -> Script:
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
            # 检查页码是否有效
            if page_number < 1:
                raise ValueError("页码必须大于0")
            
            # 获取项目目录
            project_dir = self.storage_dir / project_id
            if not project_dir.exists():
                raise ValueError(f"项目目录不存在: {project_dir}")
            
            # 检查该页面是否已有脚本，如果有则删除所有对话项
            existing_script = self.get_script(project_id, page_number)
            if existing_script and existing_script.dialogues:
                logger.info(f"页面 {page_number} 已有脚本，正在删除 {len(existing_script.dialogues)} 个对话项")
                # 复制对话ID列表，避免在迭代过程中修改列表
                dialogue_ids = [dialogue.id for dialogue in existing_script.dialogues]
                for dialogue_id in dialogue_ids:
                    self.delete_dialogue_by_id(project_id, page_number, dialogue_id)
            
            # 获取图片文件
            images_dir = project_dir / "images"
            # 查找匹配的图片文件，使用3位数字格式
            image_files = list(images_dir.glob(f"page_{page_number:03d}.png"))
            if not image_files:
                raise ValueError(f"图片文件不存在: page_{page_number:03d}.png")
            image_file = image_files[0]
            
            # 获取上下文信息
            context = self._get_context(project_id, page_number)
            
            # 构建提示
            if context:
                prompt = f"已经生成的口播稿如下:\n{context}\n\n请根据上下文,为这张图片生成口播稿"
            else:
                prompt = "这是一张封面,请给出它生成介绍性的口播稿,不要出现道具角色"
            
            # 获取图片字节流
            image_bytes = self._encode_image(image_file)
            
            # 使用AI代理生成对话
            async def run_agent():
                return await self.agent.run([
                    prompt,
                    BinaryContent(
                        media_type="image/png",
                        data=image_bytes
                    )
                ])
            
            result = await self._retry_with_exponential_backoff(run_agent)
            
            # 获取对话列表
            dialogues_data: List[DialogueItemAI] = result.output
            
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
        """保存脚本到文件
        
        Args:
            project_id: 项目ID
            script: 脚本对象
        """
        # 创建脚本目录
        scripts_dir = self.storage_dir / project_id / "scripts"
        ensure_directory(scripts_dir)
        
        # 保存脚本文件，使用Pydantic的model_dump_json方法
        script_file = scripts_dir / f"script_{script.page_number:03d}.json"
        with open(script_file, 'w', encoding='utf-8') as f:
            f.write(script.model_dump_json(ensure_ascii=False, indent=2))
    
    def get_script(self, project_id: str, page_number: int) -> Optional[Script]:
        """获取指定页面的脚本
        
        Args:
            project_id: 项目ID
            page_number: 页码
            
        Returns:
            脚本对象，如果不存在则返回None
        """
        try:
            # 获取脚本文件
            scripts_dir = self.storage_dir / project_id / "scripts"
            script_file = scripts_dir / f"script_{page_number:03d}.json"
            
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
                    self._regenerate_page_audio_after_deletion(project_id, page_number)
                    
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
            self._regenerate_page_audio_after_move(project_id, page_number)
            
            return script.dialogues[current_index if direction == 'up' else current_index - 1]
            
        except Exception as e:
            logger.error(f"移动对话项失败: {str(e)}")
            return None
    
    def _delete_dialogue_audio(self, project_id: str, page_number: int, dialogue_id: str) -> None:
        """删除对话项对应的音频文件
        
        Args:
            project_id: 项目ID
            page_number: 页码
            dialogue_id: 对话项ID
        """
        try:
            # 构建音频文件路径
            audio_file_path = self.storage_dir / project_id / "audio" / f"page_{page_number:03d}" / f"{dialogue_id}.mp3"
            
            # 如果音频文件存在，则删除
            if audio_file_path.exists():
                audio_file_path.unlink()
                logger.info(f"已删除对话音频文件: {audio_file_path}")
            
        except Exception as e:
            logger.error(f"删除对话音频文件失败: {str(e)}")
    
    def _regenerate_page_audio_after_move(self, project_id: str, page_number: int) -> None:
        """移动对话项后重新合并页面音频文件
        
        Args:
            project_id: 项目ID
            page_number: 页码
        """
        try:
            # 导入AudioService
            from app.services.audio_service import AudioService
            
            # 获取脚本文件
            scripts_dir = self.storage_dir / project_id / "scripts"
            script_file = scripts_dir / f"script_{page_number:03d}.json"
            
            if not script_file.exists():
                logger.warning(f"脚本文件不存在: {script_file}")
                return
            
            # 读取脚本文件
            with open(script_file, 'r', encoding='utf-8') as f:
                script_json = f.read()
            
            # 解析脚本
            script = Script.model_validate_json(script_json)
            
            # 创建页面音频目录
            page_audio_dir = self.storage_dir / project_id / "audio" / f"page_{page_number:03d}"
            
            audio_files = []
            
            # 开场音频路径
            project_root = Path(__file__).parent.parent.parent
            begin_audio_path = project_root / "backend" / "assets" / "cues.mp3"
            
            # 如果是第一页，先添加begin.mp3
            if page_number == 1 and begin_audio_path.exists():
                begin_audio_file = page_audio_dir / "beigin.mp3"
                if begin_audio_file.exists():
                    audio_files.append(str(begin_audio_file))
            
            # 按新顺序收集所有已存在的对话音频文件
            for dialogue in script.dialogues:
                dialogue_audio_path = page_audio_dir / f"{dialogue.id}.mp3"
                if dialogue_audio_path.exists():
                    audio_files.append(str(dialogue_audio_path))
            
            # 如果有音频文件，合并它们
            if audio_files:
                # 创建音频目录
                audio_dir = self.storage_dir / project_id / "audio"
                
                # 页面音频文件路径
                page_output_path = audio_dir / f"page_{page_number:03d}.mp3"
                
                audio_service = AudioService()
                
                # 直接调用同步函数
                audio_service.merge_audio_files(audio_files, str(page_output_path))
                logger.info(f"已重新合并页面 {page_number} 的音频: {page_output_path}")
            else:
                logger.warning(f"页面 {page_number} 没有找到任何音频文件")
                
        except Exception as e:
            logger.error(f"重新合并页面音频失败: {str(e)}")
    
    def _regenerate_page_audio_after_deletion(self, project_id: str, page_number: int) -> None:
        """删除对话项后重新合并页面音频文件
        
        Args:
            project_id: 项目ID
            page_number: 页码
        """
        try:
            # 导入AudioService
            from app.services.audio_service import AudioService
            
            # 获取脚本文件
            scripts_dir = self.storage_dir / project_id / "scripts"
            script_file = scripts_dir / f"script_{page_number:03d}.json"
            
            if not script_file.exists():
                logger.warning(f"脚本文件不存在: {script_file}")
                return
            
            # 读取脚本文件
            with open(script_file, 'r', encoding='utf-8') as f:
                script_json = f.read()
            
            # 解析脚本
            script = Script.model_validate_json(script_json)
            
            # 创建页面音频目录
            page_audio_dir = self.storage_dir / project_id / "audio" / f"page_{page_number:03d}"
            
            audio_files = []
            
            # 开场音频路径
            project_root = Path(__file__).parent.parent.parent.parent
            begin_audio_path = project_root / "backend" / "assets" / "cues.mp3"
            
            # 如果是第一页，先添加begin.mp3
            if page_number == 1 and begin_audio_path.exists():
                begin_audio_file = page_audio_dir / "beigin.mp3"
                if begin_audio_file.exists():
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
                
                # 页面音频文件路径
                page_output_path = audio_dir / f"page_{page_number:03d}.mp3"
                
                audio_service = AudioService()
                
                # 直接调用同步函数
                audio_service.merge_audio_files(audio_files, str(page_output_path))
                logger.info(f"已重新合并页面 {page_number} 的音频: {page_output_path}")
            else:
                logger.warning(f"页面 {page_number} 没有找到任何音频文件")
                
        except Exception as e:
            logger.error(f"重新合并页面音频失败: {str(e)}")
    
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
            project_dir = self.storage_dir / project_id
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
            
            # 计算总页数
            total_pages = len(image_files)
            
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