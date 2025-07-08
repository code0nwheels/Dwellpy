"""Bootstrap module for platform-specific setup and initialization."""

from .platform_setup import setup_dpi_awareness, create_linux_desktop_file, setup_signal_handlers

__all__ = ['setup_dpi_awareness', 'create_linux_desktop_file', 'setup_signal_handlers'] 