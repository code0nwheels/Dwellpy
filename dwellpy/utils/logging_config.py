"""Logging configuration for Dwellpy application."""

import logging
import logging.handlers
import os
import sys
import platform
from pathlib import Path


def get_log_directory():
    """Get the appropriate log directory for the current OS."""
    system = platform.system()
    
    if system == "Windows":
        # Windows: %APPDATA%\Dwellpy\logs\
        appdata = os.environ.get('APPDATA')
        if appdata:
            log_dir = Path(appdata) / "Dwellpy" / "logs"
        else:
            # Fallback to user directory
            log_dir = Path.home() / "AppData" / "Roaming" / "Dwellpy" / "logs"
    
    elif system == "Darwin":  # macOS
        # macOS: ~/Library/Application Support/Dwellpy/logs/
        log_dir = Path.home() / "Library" / "Application Support" / "Dwellpy" / "logs"
    
    else:  # Linux and other Unix-like systems
        # Linux: ~/.local/share/Dwellpy/logs/
        xdg_data_home = os.environ.get('XDG_DATA_HOME')
        if xdg_data_home:
            log_dir = Path(xdg_data_home) / "Dwellpy" / "logs"
        else:
            log_dir = Path.home() / ".local" / "share" / "Dwellpy" / "logs"
    
    return log_dir


def setup_logging(log_level=logging.INFO):
    """
    Set up logging configuration for the Dwellpy application.
    
    Args:
        log_level: The logging level (default: INFO)
    """
    # Get log directory and create it if it doesn't exist
    log_dir = get_log_directory()
    log_dir.mkdir(parents=True, exist_ok=True)
    
    # Main log file path
    log_file = log_dir / "dwellpy.log"
    
    # Create root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    
    # Clear any existing handlers
    root_logger.handlers.clear()
    
    # Create rotating file handler
    # Max file size: 1MB, keep 5 backup files (total ~5MB max)
    file_handler = logging.handlers.RotatingFileHandler(
        filename=log_file,
        maxBytes=1024 * 1024,  # 1MB
        backupCount=5,
        encoding='utf-8'
    )
    file_handler.setLevel(log_level)
    
    # Create console handler for development/debugging
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.WARNING)  # Only warnings and errors to console
    
    # Create formatters
    file_formatter = logging.Formatter(
        fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    console_formatter = logging.Formatter(
        fmt='%(levelname)s - %(name)s - %(message)s'
    )
    
    # Set formatters
    file_handler.setFormatter(file_formatter)
    console_handler.setFormatter(console_formatter)
    
    # Add handlers to root logger
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)
    
    # Set specific logger levels for different modules
    setup_module_loggers()
    
    # Log the setup completion
    logger = logging.getLogger(__name__)
    logger.info(f"Logging initialized - Log directory: {log_dir}")
    logger.info(f"Log level: {logging.getLevelName(log_level)}")
    logger.info(f"Platform: {platform.system()} {platform.release()}")
    
    return log_dir


def setup_module_loggers():
    """Configure specific loggers for different modules."""
    # Core module loggers
    logging.getLogger('dwellpy.core').setLevel(logging.INFO)
    logging.getLogger('dwellpy.ui').setLevel(logging.INFO)
    logging.getLogger('dwellpy.managers').setLevel(logging.INFO)
    
    # More verbose logging for important components
    logging.getLogger('dwellpy.core.dwell_algorithm').setLevel(logging.DEBUG)
    logging.getLogger('dwellpy.core.click_manager').setLevel(logging.INFO)
    
    # Reduce verbosity for Qt and other external libraries
    logging.getLogger('PyQt6').setLevel(logging.WARNING)
    logging.getLogger('pynput').setLevel(logging.WARNING)


def get_logger(name):
    """
    Get a logger for a specific module.
    
    Args:
        name: The logger name (typically __name__)
        
    Returns:
        logging.Logger: Configured logger instance
    """
    return logging.getLogger(name)


def log_application_start(version):
    """Log application startup information."""
    logger = get_logger('dwellpy.main')
    logger.info("=" * 50)
    logger.info(f"Dwellpy v{version} starting up")
    logger.info(f"Python version: {sys.version}")
    logger.info(f"Platform: {platform.platform()}")
    logger.info(f"Working directory: {os.getcwd()}")
    logger.info("=" * 50)


def log_application_shutdown():
    """Log application shutdown information."""
    logger = get_logger('dwellpy.main')
    logger.info("Dwellpy application shutting down")
    logger.info("=" * 50)


def log_error_with_traceback(logger, message, exc_info=True):
    """
    Log an error with full traceback information.
    
    Args:
        logger: The logger instance
        message: Error message
        exc_info: Whether to include exception info (default: True)
    """
    logger.error(message, exc_info=exc_info)


def set_log_level(level):
    """
    Change the logging level for all handlers.
    
    Args:
        level: New logging level (e.g., logging.DEBUG, logging.INFO)
    """
    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    
    # Update file handler level
    for handler in root_logger.handlers:
        if isinstance(handler, logging.handlers.RotatingFileHandler):
            handler.setLevel(level)
    
    logger = get_logger(__name__)
    logger.info(f"Log level changed to: {logging.getLevelName(level)}") 