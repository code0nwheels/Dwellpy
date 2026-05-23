"""Platform-specific bootstrap helpers."""

import sys

_dpi_awareness_set = False


def ensure_windows_dpi_awareness():
    """Configure per-monitor DPI awareness on Windows.

    Tries the newest API first and falls back to older ones. Safe to call
    multiple times; only the first call does work. Calling on non-Windows
    or where ctypes is unavailable is a no-op.
    """
    global _dpi_awareness_set
    if _dpi_awareness_set or sys.platform != "win32":
        return
    _dpi_awareness_set = True
    try:
        import ctypes
    except ImportError:
        return
    try:
        # SetProcessDpiAwarenessContext (Windows 10 1703+)
        ctypes.windll.user32.SetProcessDpiAwarenessContext(-4)  # PER_MONITOR_AWARE_V2
        return
    except Exception:
        pass
    try:
        # SetProcessDpiAwareness (Windows 8.1+)
        ctypes.windll.shcore.SetProcessDpiAwareness(2)  # PROCESS_PER_MONITOR_DPI_AWARE
        return
    except Exception:
        pass
    try:
        # SetProcessDPIAware (Windows Vista+)
        ctypes.windll.user32.SetProcessDPIAware()
    except Exception:
        pass
