"""Input manager for the Dwellpy application."""

from PyQt6.QtCore import QObject, QTimer, pyqtSignal, QThread
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QCursor
from pynput.mouse import Controller
import time

class InputWorker(QObject):
    """
    Worker object that runs in a separate thread to poll for mouse position.
    It emits a signal when the position changes.
    """
    position_changed = pyqtSignal(tuple)

    def __init__(self, poll_interval=0.02):
        super().__init__()
        self.mouse = Controller()
        self._running = False
        self.poll_interval = poll_interval
        self.last_position = None

    def run(self):
        """Main worker loop."""
        self._running = True
        while self._running:
            try:
                pos = self.mouse.position
                if pos != self.last_position:
                    self.last_position = pos
                    self.position_changed.emit(pos)
            except Exception:
                # This can happen if the mouse controller has issues
                pass
            time.sleep(self.poll_interval)

    def stop(self):
        """Stop the worker loop."""
        self._running = False

class InputManager:
    """
    Manages mouse position tracking in a background thread and provides
    updates to the main application at a controlled interval.
    """
    def __init__(self):
        self.on_position_update = None
        self.ui_manager = None
        self._latest_position = None

        # Setup worker and thread for high-frequency polling
        self.thread = QThread()
        self.worker = InputWorker()
        self.worker.moveToThread(self.thread)
        self.worker.position_changed.connect(self._cache_position)
        self.thread.started.connect(self.worker.run)
        
        # Setup a timer on the main thread to process updates at a fixed rate
        self.processing_timer = QTimer()
        self.processing_timer.setInterval(100)  # Process updates every 100ms
        self.processing_timer.timeout.connect(self._process_latest_position)
            
    def _cache_position(self, position: tuple[int, int]):
        """Cache the most recent position from the worker thread."""
        self._latest_position = position

    def _process_latest_position(self):
        """
        Process the cached mouse position. This is called by the QTimer
        on the main thread.
        """
        if self._latest_position is None:
            return
            
        # Notify the dwell detector
        if self.on_position_update:
            self.on_position_update(self._latest_position)
        
        # Notify the UI manager for widget updates
        if self.ui_manager:
            # These methods should be thread-safe or queued by Qt's event loop
            # if they perform UI updates.
            self.ui_manager.update_movement_detection(self._latest_position)
            self.ui_manager.update_scroll_widget_position(self._latest_position)
            self.ui_manager.update_menu_widget_position(self._latest_position)
            
    def start(self):
        """Start the background polling thread and the processing timer."""
        if not self.thread.isRunning():
            self.thread.start()
        self.processing_timer.start()
        
    def stop(self):
        """Stop the thread and the timer."""
        if self.thread.isRunning():
            self.worker.stop()
            self.thread.quit()
            self.thread.wait()
        self.processing_timer.stop()