import logging
logger = logging.getLogger(__name__)

def log_skipped(reason: str, url: str):
    logger.warning(f"[SKIPPED] {reason} - {url}")
