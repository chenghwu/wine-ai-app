import os
import psutil
import logging

logger = logging.getLogger(__name__)

def log_memory(tag: str = ""):
    process = psutil.Process(os.getpid())
    mem_mb = process.memory_info().rss / (1024 * 1024)
    logger.info(f"[MEMORY] {tag} - {mem_mb:.2f} MiB")