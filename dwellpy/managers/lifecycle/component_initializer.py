#!/usr/bin/env python3
"""Component initialization and connection management for Dwellpy."""

import logging
from typing import Any

from ...core.dwell_algorithm import DwellDetector
from ...core.input_manager import InputManager
from ...core.click_manager import ClickManager
from ...managers.button_manager import ButtonManager
from ...managers.settings_manager import SettingsManager
from ...managers.window_manager import WindowManager
from ...managers.exit_manager import ExitManager
from ...ui.ui_manager import DwellClickerUI
from ...ui.click_feedback import ClickFeedbackManager
from ...config.constants import DEFAULT_MOVE_LIMIT, DEFAULT_DWELL_TIME


class ComponentInitializer:
    """Handles initialization and connection of all application components."""
    
    def __init__(self, logger: logging.Logger):
        """Initialize the component initializer."""
        self.logger = logger
        self.components = {}
    
    def initialize_managers(self) -> dict[str, Any]:
        """Initialize core managers and components."""
        self.logger.info("Initializing core managers...")
        
        # Create core managers
        button_manager = ButtonManager()
        detector = DwellDetector(
            radius=DEFAULT_MOVE_LIMIT, 
            dwell_time=DEFAULT_DWELL_TIME
        )
        input_manager = InputManager()
        click_manager = ClickManager()
        
        # Create click feedback manager
        feedback_manager = ClickFeedbackManager()
        
        # Connect feedback manager to click manager
        click_manager.feedback_manager = feedback_manager
        
        # Create settings manager (must be created before UI)
        settings_manager = SettingsManager(detector)
        
        # Connect settings manager to feedback manager
        feedback_manager.set_settings_manager(settings_manager)
        
        # Create window manager
        window_manager = WindowManager(settings_manager)
        
        # Store components
        self.components = {
            'button_manager': button_manager,
            'detector': detector,
            'input_manager': input_manager,
            'click_manager': click_manager,
            'feedback_manager': feedback_manager,
            'settings_manager': settings_manager,
            'window_manager': window_manager
        }
        
        self.logger.info("Core managers initialized successfully")
        return self.components
    
    def initialize_ui(self, components: dict[str, Any]) -> DwellClickerUI:
        """Initialize UI components."""
        self.logger.info("Initializing UI components...")
        
        # Create main UI
        ui = DwellClickerUI(
            components['click_manager'], 
            components['detector'],
            components['button_manager'],
            components['window_manager']
        )
        
        # Create exit manager after UI is created
        exit_manager = ExitManager(
            components['settings_manager'],
            components['button_manager'],
            ui.window
        )
        
        # Store exit manager
        self.components['exit_manager'] = exit_manager
        
        # Connect managers to UI
        ui.connect_managers(components['settings_manager'], exit_manager)
        
        # Register exit manager command with button manager
        components['button_manager'].register_command("EXIT", exit_manager.show_exit_dialog)
        
        # Register settings manager command with button manager
        components['button_manager'].register_command(
            "SETUP", 
            lambda: components['settings_manager'].open_setup(
                components['button_manager'], 
                ui.window
            )
        )
        
        self.logger.info("UI components initialized successfully")
        return ui
    
    def connect_components(self, ui: DwellClickerUI, components: dict[str, Any]) -> None:
        """Connect all application components together."""
        self.logger.info("Connecting application components...")
        
        # Connect UI to managers
        ui.connect_managers(components['settings_manager'], components['exit_manager'])
        
        # Register settings manager command with button manager
        components['button_manager'].register_command(
            "SETUP", 
            lambda: components['settings_manager'].open_setup(
                components['button_manager'], 
                ui.window
            )
        )
        
        # Setup input callback for position updates
        components['input_manager'].on_position_update = self._create_position_update_callback(
            components['detector'], ui
        )
        
        # Give input manager reference to UI for scroll widget updates
        components['input_manager'].ui_manager = ui
        
        self.logger.info("Component connections established")
    
    def configure_adaptive_polling(self, input_manager: InputManager, settings_manager: SettingsManager) -> None:
        """Configure adaptive polling parameters from settings."""
        # Default parameters
        normal_interval = 100  # ms
        idle_interval = 500    # ms
        idle_threshold = 10    # frames
        
        # Check if we should use settings values
        if settings_manager:
            # Use settings if available, otherwise use defaults
            normal_interval = settings_manager.get_setting('polling_normal_interval', normal_interval)
            idle_interval = settings_manager.get_setting('polling_idle_interval', idle_interval)
            idle_threshold = settings_manager.get_setting('polling_idle_threshold', idle_threshold)
        
        # Configure the input manager with these settings
        input_manager.configure_adaptive_polling(
            normal_interval=normal_interval,
            idle_interval=idle_interval,
            idle_threshold=idle_threshold
        )
        
        self.logger.debug(f"Configured adaptive polling: normal={normal_interval}ms, "
                         f"idle={idle_interval}ms, threshold={idle_threshold} frames")
    
    def _create_position_update_callback(self, detector: DwellDetector, ui: DwellClickerUI):
        """Create the position update callback function."""
        def on_position_update(position: tuple[int, int]) -> None:
            """
            Handle new mouse position data at regular intervals.
            
            This method is called by the InputManager every 100ms with the
            current mouse position. It processes the position through the dwell
            detection algorithm and handles any dwell events.
            
            Args:
                position: Current mouse position as (x, y) tuple
            """
            # Add position to detector's tracking history
            detector.add_position(position)
            
            # Check if a dwell event has been detected
            is_dwelling, dwell_center = detector.check_dwell()
            
            # Process dwell event if one occurred
            if is_dwelling and dwell_center:
                self.logger.debug(f"Dwell event detected at position: {dwell_center}")
                # Delegate dwell processing to the UI manager
                ui.process_dwell_event(dwell_center)
        
        return on_position_update 