"""
增强的WebSocket管理器 - Phase 2
解决94%卡住问题和状态更新延迟
"""

import asyncio
import json
import logging
from typing import Dict, Any, Optional, List, Set
from datetime import datetime, timezone
from pathlib import Path

from ..core.state_machine import WorkflowStateMachine, WorkflowState, StageState
from ..utils.logger import get_logger

logger = get_logger(__name__)


class EnhancedWebSocketManager:
    """
    增强的WebSocket状态推送管理器
    
    新功能：
    1. 文件完成检测自动推送
    2. 状态转换验证
    3. 优先级消息合并
    4. 详细进度信息
    """
    
    def __init__(self):
        self.connections: Dict[str, Any] = {}
        self.workflow_watchers: Dict[str, Set[str]] = {}
        self.file_watchers: Dict[str, asyncio.Task] = {}
        self.message_queue: Dict[str, List[Dict]] = {}
        
    async def broadcast_state_update(self, workflow_id: str, update: Dict[str, Any]):
        """
        增强状态推送，包含更多状态信息
        🔧 解决94%进度卡住问题的关键方法
        """
        try:
            # 获取工作流状态机实例
            state_machine = await self._get_workflow_state_machine(workflow_id)
            
            # 增强状态更新信息
            enhanced_update = {
                **update,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "workflow_id": workflow_id,
                # 🔧 新增字段解决94%问题
                "total_stages": len(update.get("stages", [])),
                "completed_stages": self._count_completed_stages(update.get("stages", [])),
                "files_generated": await self._check_output_files(workflow_id),
                "file_completion_status": await self._get_file_completion_status(workflow_id),
                # 状态转换信息
                "state_transition": {
                    "previous_state": update.get("previous_status"),
                    "current_state": update.get("status"),
                    "is_valid": self._validate_state_transition(
                        update.get("previous_status"),
                        update.get("status")
                    ),
                    "transition_time": datetime.now(timezone.utc).isoformat()
                },
                # 详细进度信息
                "progress_details": {
                    "calculated_progress": self._calculate_enhanced_progress(update),
                    "stage_breakdown": self._get_stage_breakdown(update.get("stages", [])),
                    "estimated_completion": self._estimate_completion_time(update)
                }
            }
            
            # 🎯 文件完成覆盖逻辑 - 解决94%卡住问题
            if enhanced_update["files_generated"]:
                enhanced_update["progress"] = 100.0
                enhanced_update["progress_override_reason"] = "files_completed"
                logger.info(f"📁 文件检测完成，工作流 {workflow_id} 进度覆盖为100%")
            
            # 广播消息
            await self._broadcast_to_workflow(workflow_id, {
                "type": "status_update",
                "data": enhanced_update
            })
            
            # 启动文件监视器（如果还没有）
            if workflow_id not in self.file_watchers and update.get("status") == "running":
                await self._start_file_watcher(workflow_id)
            
        except Exception as e:
            logger.error(f"增强状态推送失败: {e}")
            # 发送错误状态
            await self._broadcast_to_workflow(workflow_id, {
                "type": "status_error",
                "error": str(e),
                "timestamp": datetime.now(timezone.utc).isoformat()
            })

    async def _check_output_files(self, workflow_id: str) -> bool:
        """
        检查输出文件是否已生成完成
        🎯 解决94%卡住问题的核心逻辑
        """
        try:
            # 假设工作流输出目录结构
            output_dir = Path(f"./outputs/{workflow_id}")
            
            expected_files = [
                "novel.md",           # 主要输出：小说文本
                "outline.yaml",       # 大纲文件  
                "context_plan.json",  # 上下文规划
                "macguffin_objects.json"  # MacGuffin对象
            ]
            
            if not output_dir.exists():
                return False
            
            completed_files = []
            for file_name in expected_files:
                file_path = output_dir / file_name
                if file_path.exists() and file_path.stat().st_size > 0:
                    completed_files.append(file_name)
            
            # 至少需要主要文件存在
            critical_files = ["novel.md", "outline.yaml"]
            has_critical_files = all(f in completed_files for f in critical_files)
            
            if has_critical_files:
                logger.info(f"✅ 关键文件检测完成 {workflow_id}: {completed_files}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"文件检测失败 {workflow_id}: {e}")
            return False

    async def _get_file_completion_status(self, workflow_id: str) -> Dict[str, Any]:
        """获取详细的文件完成状态"""
        try:
            output_dir = Path(f"./outputs/{workflow_id}")
            
            file_status = {}
            expected_files = ["novel.md", "outline.yaml", "context_plan.json", "macguffin_objects.json"]
            
            for file_name in expected_files:
                file_path = output_dir / file_name
                if file_path.exists():
                    stat = file_path.stat()
                    file_status[file_name] = {
                        "exists": True,
                        "size": stat.st_size,
                        "modified": datetime.fromtimestamp(stat.st_mtime, timezone.utc).isoformat(),
                        "is_complete": stat.st_size > 100  # 简单的完成性检查
                    }
                else:
                    file_status[file_name] = {
                        "exists": False,
                        "size": 0,
                        "modified": None,
                        "is_complete": False
                    }
            
            return {
                "files": file_status,
                "completion_rate": len([f for f in file_status.values() if f["is_complete"]]) / len(expected_files),
                "last_check": datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            logger.error(f"获取文件状态失败: {e}")
            return {"error": str(e)}

    async def _start_file_watcher(self, workflow_id: str):
        """
        启动文件监视器任务
        监控输出文件生成，实时推送完成状态
        """
        async def file_watch_task():
            logger.info(f"🔍 启动文件监视器: {workflow_id}")
            check_count = 0
            max_checks = 120  # 最多检查2小时（每分钟一次）
            
            while check_count < max_checks:
                try:
                    files_ready = await self._check_output_files(workflow_id)
                    
                    if files_ready:
                        # 文件就绪，发送完成通知
                        await self._broadcast_to_workflow(workflow_id, {
                            "type": "files_completed",
                            "data": {
                                "workflow_id": workflow_id,
                                "files_generated": True,
                                "progress_override": 100.0,
                                "completion_time": datetime.now(timezone.utc).isoformat(),
                                "file_status": await self._get_file_completion_status(workflow_id)
                            }
                        })
                        
                        logger.info(f"🎯 文件完成通知已发送: {workflow_id}")
                        break
                    
                    check_count += 1
                    await asyncio.sleep(60)  # 每分钟检查一次
                    
                except Exception as e:
                    logger.error(f"文件监视器错误 {workflow_id}: {e}")
                    await asyncio.sleep(30)  # 错误时短暂等待后继续
            
            # 清理监视器
            if workflow_id in self.file_watchers:
                del self.file_watchers[workflow_id]
            
            logger.info(f"🔍 文件监视器结束: {workflow_id}")
        
        # 启动异步任务
        task = asyncio.create_task(file_watch_task())
        self.file_watchers[workflow_id] = task

    def _validate_state_transition(self, from_state: Optional[str], to_state: Optional[str]) -> bool:
        """
        验证状态转换的合法性
        基于后端状态机的转换规则
        """
        if not from_state or not to_state:
            return True  # 初始状态或缺少信息时通过
        
        # 允许的工作流状态转换（与state_machine.py保持一致）
        allowed_transitions = {
            "pending": ["running", "cancelled"],
            "running": ["paused", "completed", "failed", "cancelled"],
            "paused": ["running", "cancelled"],
            "completed": [],  # 终态
            "failed": ["running"],  # 允许重试
            "cancelled": []   # 终态
        }
        
        valid = to_state in allowed_transitions.get(from_state, [])
        
        if not valid:
            logger.warning(f"⚠️  无效状态转换: {from_state} -> {to_state}")
        
        return valid

    def _count_completed_stages(self, stages: List[Dict]) -> int:
        """计算已完成的阶段数量"""
        return len([s for s in stages if s.get("status") in ["completed", "skipped"]])

    def _calculate_enhanced_progress(self, update: Dict[str, Any]) -> float:
        """
        增强的进度计算
        考虑阶段权重和文件完成状态
        """
        stages = update.get("stages", [])
        if not stages:
            return update.get("progress", 0.0)
        
        total_weight = 0.0
        completed_weight = 0.0
        
        # 计算加权进度
        for stage in stages:
            weight = stage.get("weight", 1.0)
            total_weight += weight
            
            if stage.get("status") == "completed":
                completed_weight += weight
            elif stage.get("status") == "skipped":
                completed_weight += weight  # 跳过视为完成
            elif stage.get("status") == "running":
                stage_progress = stage.get("progress", 50.0)  # 运行中默认50%
                completed_weight += weight * (stage_progress / 100.0)
        
        if total_weight == 0:
            return 0.0
        
        return min(100.0, (completed_weight / total_weight) * 100.0)

    def _get_stage_breakdown(self, stages: List[Dict]) -> List[Dict]:
        """获取详细的阶段分解信息"""
        breakdown = []
        
        for stage in stages:
            breakdown.append({
                "stage_id": stage.get("stage_id"),
                "stage_name": stage.get("stage_name", stage.get("stage_id")),
                "status": stage.get("status"),
                "progress": stage.get("progress", 0.0),
                "weight": stage.get("weight", 1.0),
                "start_time": stage.get("start_time"),
                "end_time": stage.get("end_time"),
                "estimated_duration": stage.get("estimated_duration")
            })
        
        return breakdown

    def _estimate_completion_time(self, update: Dict[str, Any]) -> Optional[str]:
        """估算完成时间"""
        try:
            stages = update.get("stages", [])
            if not stages:
                return None
            
            completed_stages = [s for s in stages if s.get("status") == "completed" and s.get("start_time") and s.get("end_time")]
            pending_stages = [s for s in stages if s.get("status") in ["waiting", "running"]]
            
            if not completed_stages or not pending_stages:
                return None
            
            # 计算平均阶段耗时
            total_duration = 0
            for stage in completed_stages:
                start = datetime.fromisoformat(stage["start_time"].replace("Z", "+00:00"))
                end = datetime.fromisoformat(stage["end_time"].replace("Z", "+00:00"))
                duration = (end - start).total_seconds()
                total_duration += duration
            
            avg_duration = total_duration / len(completed_stages)
            
            # 估算剩余时间
            remaining_seconds = avg_duration * len(pending_stages)
            estimated_completion = datetime.now(timezone.utc).timestamp() + remaining_seconds
            
            return datetime.fromtimestamp(estimated_completion, timezone.utc).isoformat()
            
        except Exception as e:
            logger.error(f"估算完成时间失败: {e}")
            return None

    async def _get_workflow_state_machine(self, workflow_id: str) -> Optional[WorkflowStateMachine]:
        """获取工作流状态机实例"""
        try:
            # 尝试从持久化存储加载
            from ..core.state_machine import restore_workflow_state_machine
            return restore_workflow_state_machine(workflow_id)
        except Exception as e:
            logger.warning(f"无法加载状态机 {workflow_id}: {e}")
            return None

    async def _broadcast_to_workflow(self, workflow_id: str, message: Dict[str, Any]):
        """向工作流的所有订阅者广播消息"""
        try:
            subscribers = self.workflow_watchers.get(workflow_id, set())
            
            if not subscribers:
                logger.debug(f"工作流 {workflow_id} 没有订阅者")
                return
            
            message_json = json.dumps(message)
            successful_sends = 0
            
            for session_id in list(subscribers):  # 创建副本以避免修改过程中的集合变化
                try:
                    connection = self.connections.get(session_id)
                    if connection and connection.get("websocket"):
                        websocket = connection["websocket"]
                        await websocket.send_text(message_json)
                        successful_sends += 1
                except Exception as e:
                    logger.warning(f"发送消息到 {session_id} 失败: {e}")
                    # 移除无效连接
                    self._remove_connection(session_id)
            
            logger.debug(f"消息广播完成: {workflow_id}, 成功发送: {successful_sends}/{len(subscribers)}")
            
        except Exception as e:
            logger.error(f"广播消息失败: {e}")

    def _remove_connection(self, session_id: str):
        """移除无效连接"""
        if session_id in self.connections:
            connection = self.connections.pop(session_id)
            workflow_id = connection.get("workflow_id")
            
            if workflow_id and workflow_id in self.workflow_watchers:
                self.workflow_watchers[workflow_id].discard(session_id)

    async def cleanup_file_watchers(self):
        """清理所有文件监视器"""
        for workflow_id, task in list(self.file_watchers.items()):
            try:
                task.cancel()
                await task
            except asyncio.CancelledError:
                pass
            except Exception as e:
                logger.error(f"清理文件监视器失败 {workflow_id}: {e}")
        
        self.file_watchers.clear()


# 全局增强WebSocket管理器实例
enhanced_websocket_manager = EnhancedWebSocketManager()