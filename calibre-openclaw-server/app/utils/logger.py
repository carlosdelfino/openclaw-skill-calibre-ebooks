import logging
import gzip
import shutil
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional
import json

from app.config import settings


class JSONFormatter(logging.Formatter):
    """Custom JSON formatter for structured logging."""
    
    def format(self, record: logging.LogRecord) -> str:
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }
        
        # Add extra fields if present
        if hasattr(record, 'endpoint'):
            log_data['endpoint'] = record.endpoint
        if hasattr(record, 'method'):
            log_data['method'] = record.method
        if hasattr(record, 'params'):
            log_data['params'] = record.params
        if hasattr(record, 'ip'):
            log_data['ip'] = record.ip
        if hasattr(record, 'duration'):
            log_data['duration'] = record.duration
        if hasattr(record, 'status_code'):
            log_data['status_code'] = record.status_code
        
        # Add exception info if present
        if record.exc_info:
            log_data['exception'] = self.formatException(record.exc_info)
        
        return json.dumps(log_data)


def setup_logger(name: str = "calibre_openclaw") -> logging.Logger:
    """Setup logger with daily rotation and compression."""
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    
    # Create log directory if it doesn't exist
    log_dir = settings.log_dir_path
    log_dir.mkdir(parents=True, exist_ok=True)
    
    # Remove old log files and compress
    cleanup_old_logs(log_dir)
    
    # Create daily log file
    log_file = log_dir / f"{datetime.now().strftime('%Y-%m-%d')}.log"
    
    # File handler with JSON formatter
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(JSONFormatter())
    logger.addHandler(file_handler)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(JSONFormatter())
    logger.addHandler(console_handler)
    
    return logger


def cleanup_old_logs(log_dir: Path):
    """Compress and remove old log files based on retention policy."""
    cutoff_date = datetime.now() - timedelta(days=settings.LOG_RETENTION_DAYS)
    
    for log_file in log_dir.glob("*.log"):
        file_date = datetime.strptime(log_file.stem, "%Y-%m-%d")
        
        if file_date < cutoff_date:
            if settings.LOG_COMPRESS:
                # Compress the file
                compressed_file = log_dir / f"{log_file.stem}.log.gz"
                with open(log_file, 'rb') as f_in:
                    with gzip.open(compressed_file, 'wb') as f_out:
                        shutil.copyfileobj(f_in, f_out)
                log_file.unlink()
            else:
                # Just remove the file
                log_file.unlink()
    
    # Remove compressed files older than retention period
    for compressed_file in log_dir.glob("*.log.gz"):
        file_date = datetime.strptime(compressed_file.stem.split('.')[0], "%Y-%m-%d")
        if file_date < cutoff_date:
            compressed_file.unlink()


def get_logger(name: Optional[str] = None) -> logging.Logger:
    """Get or create a logger instance."""
    if name is None:
        name = "calibre_openclaw"
    return logging.getLogger(name)
