"""
结构化日志系统
"""

import logging
import sys
from pathlib import Path
from typing import Optional

from app.core.config import settings

# 创建日志目录
log_dir = Path(settings.LOG_DIR)
log_dir.mkdir(exist_ok=True)


def get_logger(name: str) -> logging.Logger:
    """获取配置好的日志记录器"""
    
    logger = logging.getLogger(name)
    
    # 避免重复添加处理器
    if logger.hasHandlers():
        return logger
    
    logger.setLevel(settings.LOG_LEVEL)
    
    # ============================================================
    # 控制台处理器 (标准输出)
    # ============================================================
    
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(settings.LOG_LEVEL)
    
    console_formatter = logging.Formatter(
        fmt='%(asctime)s | %(name)s | %(levelname)-8s | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)
    
    # ============================================================
    # 文件处理器 (日志文件)
    # ============================================================
    
    log_file = log_dir / f"{name.split('.')[-1]}.log"
    
    try:
        file_handler = logging.FileHandler(
            log_file,
            encoding='utf-8',
            mode='a'
        )
        file_handler.setLevel(settings.LOG_LEVEL)
        
        file_formatter = logging.Formatter(
            fmt='%(asctime)s | %(name)s | %(levelname)-8s | %(funcName)s:%(lineno)d | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)
    except IOError as e:
        logger.warning(f"无法创建日志文件 {log_file}: {e}")
    
    # 防止日志传播到根logger
    logger.propagate = False
    
    return logger


# 创建全局日志记录器
logger = get_logger("office_assistant")
