"""Lifecycle management module for application startup, shutdown, and cleanup."""

from .application_lifecycle import ApplicationLifecycle
from .component_initializer import ComponentInitializer

__all__ = ['ApplicationLifecycle', 'ComponentInitializer'] 