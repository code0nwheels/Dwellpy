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
        
        # Adaptive polling state
        self.idle_count = 0
        self.last_processed_position = None
        self.normal_interval = 100  # ms
        self.idle_interval = 500    # ms
        self.idle_threshold = 10    # frames (= 1 second at 100ms)

        # Setup worker and thread for high-frequency polling
        self.thread = QThread()
        self.worker = InputWorker()
        self.worker.moveToThread(self.thread)
        self.worker.position_changed.connect(self._cache_position)
        self.thread.started.connect(self.worker.run)
        
        # Setup a timer on the main thread to process updates at a fixed rate
        self.processing_timer = QTimer()
        self.processing_timer.setInterval(self.normal_interval)  # Process updates every 100ms initially
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
            
        # Check if the position is unchanged compared to the last processed position
        position_changed = self._latest_position != self.last_processed_position
        
        # Manage the idle state and polling interval
        if position_changed:
            # Mouse has moved, reset idle counter and ensure normal polling rate
            self.idle_count = 0
            if self.processing_timer.interval() != self.normal_interval:
                self.processing_timer.setInterval(self.normal_interval)
        else:
            # Mouse hasn't moved, increment idle counter
            self.idle_count += 1
            # If we've been idle for a while and haven't already switched to idle rate
            if self.idle_count >= self.idle_threshold and self.processing_timer.interval() != self.idle_interval:
                self.processing_timer.setInterval(self.idle_interval)
        
        # Store the current position as the last processed position
        self.last_processed_position = self._latest_position
            
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

    def configure_adaptive_polling(self, normal_interval=100, idle_interval=500, idle_threshold=10):
        """
        Configure the adaptive polling parameters.
        
        Args:
            normal_interval (int): The polling interval in milliseconds when the user is active
            idle_interval (int): The polling interval in milliseconds when the user is idle
            idle_threshold (int): The number of frames of no movement before switching to idle rate
        """
        self.normal_interval = normal_interval
        self.idle_interval = idle_interval
        self.idle_threshold = idle_threshold
        
        # Update current timer interval if necessary
        if self.idle_count < self.idle_threshold:
            self.processing_timer.setInterval(self.normal_interval)
        else:
            self.processing_timer.setInterval(self.idle_interval)
    
    def is_idle(self):
        """
        Return whether the system currently considers the user to be idle.
        
        Returns:
            bool: True if idle, False if active
        """
        return self.idle_count >= self.idle_threshold
    
    def reset_idle_state(self):
        """
        Force a reset of the idle state, useful when the application responds
        to external events and wants to ensure normal polling rate.
        """
        self.idle_count = 0
        self.processing_timer.setInterval(self.normal_interval)