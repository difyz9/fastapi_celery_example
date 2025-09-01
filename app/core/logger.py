"""
日志配置模块
"""
import logging
import sys
from pathlib import Path
from typing import Optional
from app.core.config import settings


def setup_logging():
    """配置应用日志"""
    # 创建日志目录
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    # 配置根日志记录器
    logging.basicConfig(
        level=getattr(logging, settings.LOG_LEVEL),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler(log_dir / "app.log", encoding='utf-8')
        ]
    )


def get_logger(name: Optional[str] = None) -> logging.Logger:
    """
    获取配置好的日志记录器
    
    Args:
        name: 日志记录器名称，如果为None则使用调用模块的名称
        
    Returns:
        logging.Logger: 配置好的日志记录器
    """
    return logging.getLogger(name or __name__)
