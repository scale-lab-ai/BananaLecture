import json
from pathlib import Path
from typing import List, Optional, Dict, Any, Callable
import logging
from threading import Lock

from app.models import Task, TaskType, TaskStatus
from app.utils.file_utils import generate_unique_id
from app.core.path_manager import PathManager

logger = logging.getLogger(__name__)


class TaskService:
    """任务管理服务类"""
    
    def __init__(self, path_manager: Optional[PathManager] = None):
        """Initialize task service
        
        Args:
            path_manager: Path manager instance, if None uses global instance
        """
        self.path_manager = path_manager or PathManager()
        
        # In-memory task cache
        self._tasks: Dict[str, Task] = {}
        
        # Task lock, ensures thread safety
        self._lock = Lock()
        
        # Load existing tasks
        self._load_tasks()
    
    def _get_task_file_path(self, task_id: str) -> Path:
        """Get task data file path"""
        return self.path_manager.get_task_file(task_id)
    
    def _load_tasks(self) -> None:
        """从文件加载所有任务"""
        try:
            for task_file in self.path_manager.get_tasks_dir().glob("*.json"):
                with open(task_file, 'r', encoding='utf-8') as f:
                    task_data = json.load(f)
                
                # 使用Pydantic模型解析
                task = Task.model_validate(task_data)
                self._tasks[task.id] = task
                
            logger.info(f"已加载 {len(self._tasks)} 个任务")
        except Exception as e:
            logger.error(f"加载任务失败: {str(e)}")
    
    def _save_task(self, task: Task) -> None:
        """保存任务到文件"""
        try:
            task_file = self._get_task_file_path(task.id)
            with open(task_file, 'w', encoding='utf-8') as f:
                f.write(task.model_dump_json(ensure_ascii=False, indent=2))
        except Exception as e:
            logger.error(f"保存任务 {task.id} 失败: {str(e)}")
    
    def create_task(self, task_type: TaskType, total_steps: int = 0) -> Task:
        """创建新任务
        
        Args:
            task_type: 任务类型
            total_steps: 总步骤数
            
        Returns:
            创建的任务对象
        """
        with self._lock:
            task = Task(
                id=generate_unique_id(),
                type=task_type,
                status=TaskStatus.PENDING,
                progress=0.0,
                current_step=0,
                total_steps=total_steps
            )
            
            # 保存到内存和文件
            self._tasks[task.id] = task
            self._save_task(task)
            
            logger.info(f"已创建任务 {task.id}，类型: {task_type}")
            return task
    
    def get_task(self, task_id: str) -> Optional[Task]:
        """获取任务
        
        Args:
            task_id: 任务ID
            
        Returns:
            任务对象，如果不存在则返回None
        """
        with self._lock:
            return self._tasks.get(task_id)
    
    def update_task_status(self, task_id: str, status: TaskStatus, 
                          progress: Optional[float] = None,
                          current_step: Optional[int] = None,
                          error_message: Optional[str] = None) -> bool:
        """更新任务状态
        
        Args:
            task_id: 任务ID
            status: 新状态
            progress: 进度 (0.0-1.0)
            current_step: 当前步骤
            error_message: 错误信息
            
        Returns:
            是否更新成功
        """
        with self._lock:
            task = self._tasks.get(task_id)
            if not task:
                return False
            
            # 更新状态
            task.status = status
            
            # 更新进度
            if progress is not None:
                task.progress = max(0.0, min(1.0, progress))
            
            # 更新步骤
            if current_step is not None:
                task.current_step = max(0, current_step)
            
            # 更新错误信息
            if error_message is not None:
                task.error_message = error_message
            elif status == TaskStatus.RUNNING:
                # 清除之前的错误信息
                task.error_message = None
            
            # 更新时间戳
            task.update_timestamp()
            
            # 保存到文件
            self._save_task(task)
            
            logger.debug(f"已更新任务 {task_id} 状态为 {status}，进度: {task.progress:.2f}")
            return True
    
    def increment_task_progress(self, task_id: str) -> bool:
        """增加任务进度
        
        Args:
            task_id: 任务ID
            
        Returns:
            是否更新成功
        """
        with self._lock:
            task = self._tasks.get(task_id)
            if not task:
                return False
            
            # 增加当前步骤
            task.current_step += 1
            
            # 计算进度
            if task.total_steps > 0:
                task.progress = min(1.0, task.current_step / task.total_steps)
            
            # 更新时间戳
            task.update_timestamp()
            
            # 保存到文件
            self._save_task(task)
            
            logger.debug(f"任务 {task_id} 进度更新: {task.current_step}/{task.total_steps} ({task.progress:.2f})")
            return True
    
    def cancel_task(self, task_id: str) -> bool:
        """取消任务
        
        Args:
            task_id: 任务ID
            
        Returns:
            是否取消成功
        """
        with self._lock:
            task = self._tasks.get(task_id)
            if not task:
                return False
            
            # 只有pending或running状态的任务可以取消
            if task.status in [TaskStatus.PENDING, TaskStatus.RUNNING]:
                task.status = TaskStatus.FAILED
                task.error_message = "任务已取消"
                task.update_timestamp()
                
                # 保存到文件
                self._save_task(task)
                
                logger.info(f"已取消任务 {task_id}")
                return True
            
            return False
    
    def delete_task(self, task_id: str) -> bool:
        """删除任务
        
        Args:
            task_id: 任务ID
            
        Returns:
            是否删除成功
        """
        with self._lock:
            task = self._tasks.pop(task_id, None)
            if not task:
                return False
            
            # 删除文件
            try:
                task_file = self._get_task_file_path(task_id)
                if task_file.exists():
                    task_file.unlink()
                
                logger.info(f"已删除任务 {task_id}")
                return True
            except Exception as e:
                logger.error(f"删除任务文件失败: {str(e)}")
                return False
    
    def get_all_tasks(self) -> List[Task]:
        """获取所有任务
        
        Returns:
            任务列表
        """
        with self._lock:
            return list(self._tasks.values())
    
    def get_tasks_by_type(self, task_type: TaskType) -> List[Task]:
        """根据类型获取任务
        
        Args:
            task_type: 任务类型
            
        Returns:
            任务列表
        """
        with self._lock:
            return [task for task in self._tasks.values() if task.type == task_type]
    
    def get_running_tasks(self) -> List[Task]:
        """获取正在运行的任务
        
        Returns:
            任务列表
        """
        with self._lock:
            return [task for task in self._tasks.values() if task.status == TaskStatus.RUNNING]
    
    async def run_task_with_progress(self, task_id: str, coro, total_steps: int = 0) -> Any:
        """运行任务并自动更新进度
        
        Args:
            task_id: 任务ID
            coro: 要执行的协程
            total_steps: 总步骤数
            
        Returns:
            协程的结果
        """
        # 设置总步骤数
        if total_steps > 0:
            self.update_task_status(task_id, TaskStatus.RUNNING, total_steps=total_steps)
        else:
            self.update_task_status(task_id, TaskStatus.RUNNING)
        
        try:
            # 执行协程
            result = await coro
            
            # 标记任务完成
            self.update_task_status(task_id, TaskStatus.COMPLETED, progress=1.0)
            
            return result
        except Exception as e:
            # 标记任务失败
            self.update_task_status(task_id, TaskStatus.FAILED, error_message=str(e))
            raise