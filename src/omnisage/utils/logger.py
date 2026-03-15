# PROJECT_FOLDER/src/omnisage/utils/logger.py
"""
简洁高效的日志系统

设计原则：
- 单一application.log文件，自动按天轮转
- 结构化日志格式，易于区分系统/工作流/API日志  
- 减少文件数量，避免日志垃圾
- 兼容监控系统
"""

import logging
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional
from logging.handlers import TimedRotatingFileHandler

# 全局logger实例
_global_logger = None
_log_file_path = None

def setup_logger(name: str = "omnisage", level: int = logging.INFO) -> logging.Logger:
    """设置统一的应用日志系统"""
    global _global_logger, _log_file_path
    
    # 如果已存在，返回现有实例
    if _global_logger is not None:
        return _global_logger
    
    logger = logging.getLogger(name)
    logger.propagate = False
    
    # 清理现有处理器
    if logger.hasHandlers():
        logger.handlers.clear()

    # 确定日志目录
    if os.path.exists("/app"):
        logs_dir = Path("/app/logs")  # Docker环境
    else:
        # 查找项目根目录
        current_path = Path(__file__).resolve()
        project_root = current_path
        while project_root.parent != project_root:
            # Check for common project root indicators
            if (project_root / "pyproject.toml").exists() or \
               (project_root / ".git").exists() or \
               (project_root / "setup.py").exists():
                break
            project_root = project_root.parent
        logs_dir = project_root / "logs"
    
    logs_dir.mkdir(exist_ok=True)
    _log_file_path = logs_dir / "application.log"

    logger.setLevel(level)

    # 统一格式：时间 [级别] 消息
    formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")

    # 文件处理器：每天轮转，保留7天
    file_handler = TimedRotatingFileHandler(
        _log_file_path,
        when='midnight',
        interval=1,
        backupCount=7,
        encoding='utf-8'
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    # 控制台处理器
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    _global_logger = logger
    logger.info(f"⚙️  日志系统已启动: {_log_file_path.name} (自动轮转，保留7天)")
    return logger

def get_logger(name: str = None) -> logging.Logger:
    """获取logger实例"""
    global _global_logger
    
    if _global_logger is not None:
        return _global_logger
    
    return setup_logger(name or "omnisage")

def log_workflow_message(workflow_id: str, stage: str, message: str, level_str: str = "info", logger_instance: logging.Logger = None) -> None:
    """工作流专用日志"""
    # 确保level_str是字符串类型
    if not isinstance(level_str, str):
        level_str = "info"  # 默认级别
    
    # 转换字符串级别到整数
    level_mapping = {
        "debug": logging.DEBUG,
        "info": logging.INFO,
        "warning": logging.WARNING,
        "error": logging.ERROR,
        "critical": logging.CRITICAL
    }
    level = level_mapping.get(level_str.lower(), logging.INFO)
    
    logger_to_use = logger_instance if logger_instance else get_logger()
    formatted_message = f"🔄 [{workflow_id[:8]}] {stage}: {message}"
    logger_to_use.log(level, formatted_message)

def log_system_message(message: str, level: int = logging.INFO) -> None:
    """系统日志"""
    logger = get_logger()
    logger.log(level, f"⚙️  {message}")

def log_api_message(method: str, path: str, status: int, duration_ms: float) -> None:
    """API访问日志"""
    logger = get_logger()
    logger.info(f"🌐 {method} {path} -> {status} ({duration_ms:.1f}ms)")

# 向后兼容
def get_logger_for_workflow(workflow_id: str) -> logging.Logger:
    """向后兼容：返回统一logger"""
    return get_logger()