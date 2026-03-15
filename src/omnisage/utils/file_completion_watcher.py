"""
文件完成检测监视器 - Phase 2
专门解决94%进度卡住问题的核心组件
"""

import asyncio
import json
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional, Callable, Set
from datetime import datetime, timezone
from dataclasses import dataclass
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileModifiedEvent, FileCreatedEvent

from ..utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class FileWatchConfig:
    """文件监视配置"""
    workflow_id: str
    output_dir: Path
    expected_files: List[str]
    critical_files: List[str]  # 必须存在的关键文件
    min_file_size: int = 100   # 最小文件大小（字节）
    stability_delay: int = 5   # 文件稳定等待时间（秒）
    max_watch_time: int = 7200 # 最大监视时间（秒）


@dataclass
class FileStatus:
    """文件状态信息"""
    exists: bool
    size: int
    last_modified: Optional[datetime]
    is_stable: bool  # 文件是否稳定（不再变化）
    content_hash: Optional[str] = None


@dataclass
class CompletionEvent:
    """完成事件信息"""
    workflow_id: str
    timestamp: datetime
    completion_type: str  # 'partial', 'critical', 'full'
    completed_files: List[str]
    file_details: Dict[str, FileStatus]
    trigger_reason: str


class OutputFileWatcher(FileSystemEventHandler):
    """输出文件系统监视器"""
    
    def __init__(self, config: FileWatchConfig, callback: Callable[[CompletionEvent], None]):
        self.config = config
        self.callback = callback
        self.file_states: Dict[str, FileStatus] = {}
        self.stability_tasks: Dict[str, asyncio.Task] = {}
        self.last_check_time = datetime.now(timezone.utc)
        
    def on_created(self, event):
        """文件创建事件"""
        if not event.is_directory:
            file_path = Path(event.src_path)
            if self._is_monitored_file(file_path):
                logger.info(f"📁 检测到文件创建: {file_path.name}")
                asyncio.create_task(self._handle_file_change(file_path))
    
    def on_modified(self, event):
        """文件修改事件"""
        if not event.is_directory:
            file_path = Path(event.src_path)
            if self._is_monitored_file(file_path):
                logger.debug(f"📝 检测到文件修改: {file_path.name}")
                asyncio.create_task(self._handle_file_change(file_path))
    
    def _is_monitored_file(self, file_path: Path) -> bool:
        """检查是否是监视的文件"""
        return file_path.name in self.config.expected_files
    
    async def _handle_file_change(self, file_path: Path):
        """处理文件变化"""
        try:
            file_name = file_path.name
            
            # 更新文件状态
            await self._update_file_status(file_path)
            
            # 取消之前的稳定性检查任务
            if file_name in self.stability_tasks:
                self.stability_tasks[file_name].cancel()
            
            # 启动新的稳定性检查任务
            self.stability_tasks[file_name] = asyncio.create_task(
                self._check_file_stability(file_path)
            )
            
        except Exception as e:
            logger.error(f"处理文件变化失败 {file_path}: {e}")
    
    async def _update_file_status(self, file_path: Path):
        """更新文件状态信息"""
        try:
            file_name = file_path.name
            
            if file_path.exists():
                stat = file_path.stat()
                status = FileStatus(
                    exists=True,
                    size=stat.st_size,
                    last_modified=datetime.fromtimestamp(stat.st_mtime, timezone.utc),
                    is_stable=False
                )
            else:
                status = FileStatus(
                    exists=False,
                    size=0,
                    last_modified=None,
                    is_stable=False
                )
            
            self.file_states[file_name] = status
            
        except Exception as e:
            logger.error(f"更新文件状态失败 {file_path}: {e}")
    
    async def _check_file_stability(self, file_path: Path):
        """检查文件是否稳定（不再变化）"""
        try:
            file_name = file_path.name
            
            # 等待文件稳定
            await asyncio.sleep(self.config.stability_delay)
            
            # 重新检查文件状态
            if file_path.exists():
                current_stat = file_path.stat()
                stored_status = self.file_states.get(file_name)
                
                if stored_status and stored_status.last_modified:
                    current_modified = datetime.fromtimestamp(current_stat.st_mtime, timezone.utc)
                    
                    # 如果修改时间和大小都没变，认为文件稳定
                    if (current_modified == stored_status.last_modified and 
                        current_stat.st_size == stored_status.size and
                        current_stat.st_size >= self.config.min_file_size):
                        
                        # 标记为稳定
                        self.file_states[file_name].is_stable = True
                        logger.info(f"✅ 文件已稳定: {file_name} ({current_stat.st_size} bytes)")
                        
                        # 检查是否触发完成事件
                        await self._check_completion_conditions()
            
            # 清理任务
            if file_name in self.stability_tasks:
                del self.stability_tasks[file_name]
                
        except asyncio.CancelledError:
            # 任务被取消，正常情况
            pass
        except Exception as e:
            logger.error(f"检查文件稳定性失败 {file_path}: {e}")
    
    async def _check_completion_conditions(self):
        """检查完成条件并触发事件"""
        try:
            stable_files = [
                name for name, status in self.file_states.items()
                if status.exists and status.is_stable
            ]
            
            critical_files_ready = all(
                name in stable_files for name in self.config.critical_files
            )
            
            all_files_ready = all(
                name in stable_files for name in self.config.expected_files
            )
            
            # 确定完成类型和是否触发事件
            completion_type = None
            trigger_reason = None
            
            if all_files_ready:
                completion_type = "full"
                trigger_reason = "all_expected_files_completed"
            elif critical_files_ready:
                completion_type = "critical"  
                trigger_reason = "critical_files_completed"
            elif len(stable_files) >= len(self.config.expected_files) * 0.7:
                completion_type = "partial"
                trigger_reason = "majority_files_completed"
            
            # 触发完成事件
            if completion_type:
                event = CompletionEvent(
                    workflow_id=self.config.workflow_id,
                    timestamp=datetime.now(timezone.utc),
                    completion_type=completion_type,
                    completed_files=stable_files,
                    file_details=self.file_states.copy(),
                    trigger_reason=trigger_reason
                )
                
                logger.info(f"🎯 触发文件完成事件: {self.config.workflow_id} - {completion_type}")
                self.callback(event)
            
        except Exception as e:
            logger.error(f"检查完成条件失败: {e}")


class WorkflowFileCompletionWatcher:
    """
    工作流文件完成监视器
    🎯 专门解决94%进度卡住问题的核心类
    """
    
    def __init__(self):
        self.active_watchers: Dict[str, Dict[str, Any]] = {}  # workflow_id -> watcher_info
        self.completion_callbacks: Dict[str, List[Callable]] = {}
        
    async def start_watching(
        self, 
        workflow_id: str,
        output_dir: Optional[Path] = None,
        completion_callback: Optional[Callable[[CompletionEvent], None]] = None
    ) -> bool:
        """
        开始监视工作流文件完成
        
        Args:
            workflow_id: 工作流ID
            output_dir: 输出目录，如果不提供则使用默认路径
            completion_callback: 完成回调函数
        """
        try:
            if workflow_id in self.active_watchers:
                logger.warning(f"工作流 {workflow_id} 已在监视中")
                return True
            
            # 设置输出目录
            if not output_dir:
                output_dir = Path(f"./outputs/{workflow_id}")
            
            # 确保目录存在
            output_dir.mkdir(parents=True, exist_ok=True)
            
            # 配置监视参数
            config = FileWatchConfig(
                workflow_id=workflow_id,
                output_dir=output_dir,
                expected_files=[
                    "novel.md",              # 主要输出文件
                    "outline.yaml",          # 大纲文件
                    "context_plan.json",     # 上下文规划
                    "macguffin_objects.json", # MacGuffin对象
                    "chapter_summaries.json", # 章节摘要（可选）
                    "character_profiles.json" # 角色档案（可选）
                ],
                critical_files=["novel.md", "outline.yaml"],  # 关键文件
                min_file_size=100,
                stability_delay=5,
                max_watch_time=7200  # 2小时
            )
            
            # 创建完成事件回调
            def handle_completion(event: CompletionEvent):
                asyncio.create_task(self._handle_completion_event(event))
            
            # 创建文件系统监视器
            event_handler = OutputFileWatcher(config, handle_completion)
            observer = Observer()
            observer.schedule(event_handler, str(output_dir), recursive=False)
            observer.start()
            
            # 创建超时任务
            timeout_task = asyncio.create_task(
                self._handle_watch_timeout(workflow_id, config.max_watch_time)
            )
            
            # 存储监视器信息
            self.active_watchers[workflow_id] = {
                "config": config,
                "observer": observer,
                "event_handler": event_handler,
                "timeout_task": timeout_task,
                "start_time": datetime.now(timezone.utc)
            }
            
            # 注册完成回调
            if completion_callback:
                if workflow_id not in self.completion_callbacks:
                    self.completion_callbacks[workflow_id] = []
                self.completion_callbacks[workflow_id].append(completion_callback)
            
            logger.info(f"🔍 开始监视工作流文件完成: {workflow_id}")
            logger.info(f"📂 监视目录: {output_dir}")
            logger.info(f"📋 期望文件: {config.expected_files}")
            logger.info(f"🔑 关键文件: {config.critical_files}")
            
            # 立即进行一次检查
            await self._perform_initial_check(workflow_id)
            
            return True
            
        except Exception as e:
            logger.error(f"启动文件监视失败 {workflow_id}: {e}")
            return False
    
    async def stop_watching(self, workflow_id: str) -> bool:
        """停止监视工作流文件"""
        try:
            if workflow_id not in self.active_watchers:
                logger.warning(f"工作流 {workflow_id} 未在监视中")
                return True
            
            watcher_info = self.active_watchers[workflow_id]
            
            # 停止文件系统监视器
            if "observer" in watcher_info:
                watcher_info["observer"].stop()
                watcher_info["observer"].join()
            
            # 取消超时任务
            if "timeout_task" in watcher_info:
                watcher_info["timeout_task"].cancel()
            
            # 清理回调
            if workflow_id in self.completion_callbacks:
                del self.completion_callbacks[workflow_id]
            
            # 移除监视器
            del self.active_watchers[workflow_id]
            
            logger.info(f"🛑 停止监视工作流文件: {workflow_id}")
            return True
            
        except Exception as e:
            logger.error(f"停止文件监视失败 {workflow_id}: {e}")
            return False
    
    async def _perform_initial_check(self, workflow_id: str):
        """执行初始文件检查"""
        try:
            watcher_info = self.active_watchers.get(workflow_id)
            if not watcher_info:
                return
            
            config = watcher_info["config"]
            event_handler = watcher_info["event_handler"]
            
            # 检查所有期望的文件
            for file_name in config.expected_files:
                file_path = config.output_dir / file_name
                await event_handler._update_file_status(file_path)
            
            # 检查是否已经有文件完成
            await event_handler._check_completion_conditions()
            
        except Exception as e:
            logger.error(f"初始文件检查失败 {workflow_id}: {e}")
    
    async def _handle_completion_event(self, event: CompletionEvent):
        """处理完成事件"""
        try:
            workflow_id = event.workflow_id
            
            logger.info(f"🎉 文件完成事件: {workflow_id}")
            logger.info(f"📋 完成类型: {event.completion_type}")
            logger.info(f"📁 已完成文件: {event.completed_files}")
            logger.info(f"🔍 触发原因: {event.trigger_reason}")
            
            # 调用所有注册的回调函数
            callbacks = self.completion_callbacks.get(workflow_id, [])
            for callback in callbacks:
                try:
                    if asyncio.iscoroutinefunction(callback):
                        await callback(event)
                    else:
                        callback(event)
                except Exception as e:
                    logger.error(f"完成回调执行失败: {e}")
            
            # 对于关键文件完成或全部完成，停止监视
            if event.completion_type in ["critical", "full"]:
                await self.stop_watching(workflow_id)
            
        except Exception as e:
            logger.error(f"处理完成事件失败: {e}")
    
    async def _handle_watch_timeout(self, workflow_id: str, timeout_seconds: int):
        """处理监视超时"""
        try:
            await asyncio.sleep(timeout_seconds)
            
            logger.warning(f"⏰ 文件监视超时: {workflow_id} ({timeout_seconds}秒)")
            
            # 执行最后一次检查
            await self._perform_initial_check(workflow_id)
            
            # 停止监视
            await self.stop_watching(workflow_id)
            
        except asyncio.CancelledError:
            # 正常取消，不需要处理
            pass
        except Exception as e:
            logger.error(f"处理监视超时失败 {workflow_id}: {e}")
    
    def get_watching_status(self, workflow_id: str) -> Optional[Dict[str, Any]]:
        """获取监视状态"""
        watcher_info = self.active_watchers.get(workflow_id)
        if not watcher_info:
            return None
        
        config = watcher_info["config"]
        event_handler = watcher_info["event_handler"]
        
        return {
            "workflow_id": workflow_id,
            "is_active": True,
            "start_time": watcher_info["start_time"].isoformat(),
            "output_dir": str(config.output_dir),
            "expected_files": config.expected_files,
            "critical_files": config.critical_files,
            "file_states": {
                name: {
                    "exists": status.exists,
                    "size": status.size,
                    "is_stable": status.is_stable,
                    "last_modified": status.last_modified.isoformat() if status.last_modified else None
                }
                for name, status in event_handler.file_states.items()
            },
            "completed_files": [
                name for name, status in event_handler.file_states.items()
                if status.exists and status.is_stable
            ]
        }
    
    def list_active_watchers(self) -> List[str]:
        """列出所有活跃的监视器"""
        return list(self.active_watchers.keys())
    
    async def cleanup_all_watchers(self):
        """清理所有监视器"""
        workflow_ids = list(self.active_watchers.keys())
        for workflow_id in workflow_ids:
            await self.stop_watching(workflow_id)


# 全局文件完成监视器实例
file_completion_watcher = WorkflowFileCompletionWatcher()