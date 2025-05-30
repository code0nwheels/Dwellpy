"""Settings management for the Dwellpy application."""

import json
import os
import logging
from typing import Any, Dict, Optional
from PyQt6.QtGui import QGuiApplication

from ..config.constants import (
    DEFAULT_SETTINGS, SETTINGS_FILENAME,
    MIN_MOVE_LIMIT, MAX_MOVE_LIMIT,
    MIN_DWELL_TIME, MAX_DWELL_TIME,
    MIN_TRANSPARENCY, MAX_TRANSPARENCY,
    EXPANSION_DIRECTIONS
)
from ..utils.helpers import get_settings_file_path, get_screen_center, clamp_value
from ..ui.dialogs.settings_dialog import SettingsDialog


class SettingsManager:
    """
    Manages application settings and persistence.
    
    This class handles:
    - Loading and saving settings to disk
    - Providing settings access interface
    - Applying settings to other components
    - Managing the settings UI dialog
    """
    
    def __init__(self, dwell_detector):
        """
        Initialize the settings manager.
        
        Args:
            dwell_detector: The DwellDetector instance to configure
        """
        self.logger = logging.getLogger(__name__)
        self.dwell_detector = dwell_detector
        self.settings_dialog: Optional[SettingsDialog] = None
        
        # Initialize settings with defaults
        self.settings: Dict[str, Any] = DEFAULT_SETTINGS.copy()
        
        # Reference to UI manager for immediate updates (set by UI manager)
        self.ui_manager = None
        
        # Load settings from disk
        self.load_settings()
        
        # Apply loaded settings to detector
        self.apply_detector_settings()
        
        self.logger.info("Settings manager initialized")
    
    def get_setting(self, key: str, default: Any = None) -> Any:
        """
        Get a setting value with optional default fallback.
        
        Args:
            key: Setting key to retrieve
            default: Default value if key doesn't exist
            
        Returns:
            The setting value or default
        """
        return self.settings.get(key, default)
    
    def set_setting(self, key: str, value: Any) -> None:
        """
        Set a setting value.
        
        Args:
            key: Setting key to set
            value: Value to set
        """
        old_value = self.settings.get(key)
        self.settings[key] = value
        self.logger.debug(f"Setting changed: {key} = {value} (was: {old_value})")
    
    def apply_detector_settings(self) -> None:
        """Apply current settings to the dwell detector."""
        # Apply movement limit
        move_limit = clamp_value(
            self.settings['move_limit'], 
            MIN_MOVE_LIMIT, 
            MAX_MOVE_LIMIT
        )
        self.dwell_detector.move_limit = move_limit
        
        # Apply dwell time
        dwell_time = clamp_value(
            self.settings['dwell_time'],
            MIN_DWELL_TIME,
            MAX_DWELL_TIME
        )
        self.dwell_detector.dwell_time = dwell_time
        self.dwell_detector.click_time = int(dwell_time / 0.1)
        
        self.logger.info(f"Applied settings to detector: move_limit={move_limit}px, dwell_time={dwell_time}s")
    
    def get_settings_file_path(self) -> str:
        """Get the path to the settings file."""
        return get_settings_file_path(SETTINGS_FILENAME)
    
    def load_settings(self) -> None:
        """Load settings from JSON file and apply them."""
        settings_file = self.get_settings_file_path()
        self.logger.info(f"Loading settings from: {settings_file}")
        
        try:
            if os.path.exists(settings_file):
                with open(settings_file, 'r', encoding='utf-8') as f:
                    loaded_settings = json.load(f)
                
                # Update settings with loaded values
                for key, value in loaded_settings.items():
                    if key in DEFAULT_SETTINGS:  # Only load known settings
                        self.settings[key] = value
                
                self.logger.info(f"Successfully loaded {len(loaded_settings)} settings")
            else:
                # Set default position near screen center for new installations
                center_x, center_y = get_screen_center()
                self.settings['window_position'] = (center_x - 150, center_y - 25)
                self.logger.info("No existing settings file found, using defaults")
                
        except Exception as e:
            # Reset to defaults on error
            self.settings = DEFAULT_SETTINGS.copy()
            self.logger.error(f"Error loading settings: {e}", exc_info=True)
            self.logger.info("Reset to default settings due to error")
    
    def save_settings(self) -> None:
        """Save current settings to JSON file."""
        settings_file = self.get_settings_file_path()
        
        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(settings_file), exist_ok=True)
            
            with open(settings_file, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, indent=2)
            
            self.logger.info(f"Settings saved to: {settings_file}")
                
        except Exception as e:
            self.logger.error(f"Error saving settings: {e}", exc_info=True)
    
    def open_setup(self, button_manager, parent_window=None) -> None:
        """
        Open the settings dialog.
        
        Args:
            button_manager: ButtonManager instance for button interactions
            parent_window: Parent window for the dialog
        """
        # Check if dialog is already open
        if self.settings_dialog is not None and self.settings_dialog.isVisible():
            # Bring existing dialog to front
            self.settings_dialog.raise_()
            self.settings_dialog.activateWindow()
            self.logger.debug("Settings dialog already open, bringing to front")
            return
        
        # Create new settings dialog
        self.settings_dialog = SettingsDialog(
            settings_manager=self,
            button_manager=button_manager,
            parent=parent_window
        )
        
        # Show the dialog
        self.settings_dialog.show()
        self.logger.info("Settings dialog opened")
    
    def close_setup(self) -> None:
        """Close the settings dialog if open."""
        if self.settings_dialog and self.settings_dialog.isVisible():
            self.settings_dialog.close()
            self.settings_dialog = None
            self.logger.info("Settings dialog closed")
    
    def update_move_limit(self, value: int) -> None:
        """
        Update move limit setting and apply immediately.
        
        Args:
            value: New move limit value in pixels
        """
        clamped_value = clamp_value(value, MIN_MOVE_LIMIT, MAX_MOVE_LIMIT)
        self.settings['move_limit'] = clamped_value
        self.dwell_detector.move_limit = clamped_value
        self.logger.info(f"Move limit updated to: {clamped_value}px")
    
    def update_dwell_time(self, value: float) -> None:
        """
        Update dwell time setting and apply immediately.
        
        Args:
            value: New dwell time value in seconds
        """
        clamped_value = clamp_value(value, MIN_DWELL_TIME, MAX_DWELL_TIME)
        self.settings['dwell_time'] = clamped_value
        self.dwell_detector.dwell_time = clamped_value
        self.dwell_detector.click_time = int(clamped_value / 0.1)
        self.logger.info(f"Dwell time updated to: {clamped_value}s")
    
    def update_transparency_enabled(self, enabled: bool) -> None:
        """
        Update transparency enabled setting and apply immediately.
        
        Args:
            enabled: Whether transparency is enabled
        """
        self.settings['transparency_enabled'] = enabled
        
        # Apply transparency change immediately if UI manager is available
        if self.ui_manager:
            self.ui_manager.apply_transparency_settings()
        
        self.logger.info(f"Transparency enabled: {enabled}")
    
    def update_transparency_level(self, level: int) -> None:
        """
        Update transparency level setting and apply immediately.
        
        Args:
            level: Transparency level as percentage (0-100)
        """
        clamped_level = clamp_value(level, MIN_TRANSPARENCY, MAX_TRANSPARENCY)
        self.settings['transparency_level'] = clamped_level
        
        # Apply transparency change immediately if UI manager is available
        if self.ui_manager:
            self.ui_manager.apply_transparency_settings()
        
        self.logger.debug(f"Transparency level updated to: {clamped_level}%")
    
    def update_scroll_enabled(self, enabled: bool) -> None:
        """
        Update scroll widget enabled setting and apply immediately.
        
        Args:
            enabled: Whether scroll widget is enabled
        """
        self.settings['scroll_enabled'] = enabled
        
        # Apply scroll widget change immediately if UI manager is available
        if self.ui_manager:
            self.ui_manager.apply_scroll_settings()
        
        self.logger.info(f"Scroll widget enabled: {enabled}")
    
    def update_scroll_speed(self, interval: int) -> None:
        """
        Update scroll speed setting and apply immediately.
        
        Args:
            interval: Scroll interval in milliseconds (lower = faster)
        """
        # Clamp interval between 20ms and 200ms
        clamped_interval = max(20, min(200, interval))
        self.settings['scroll_speed'] = clamped_interval
        
        # Apply scroll speed change immediately if UI manager is available
        if self.ui_manager:
            self.ui_manager.apply_scroll_settings()
        
        self.logger.debug(f"Scroll speed updated to: {clamped_interval}ms interval")
    
    def update_scroll_amount(self, amount: int) -> None:
        """
        Update scroll amount setting.
        
        Args:
            amount: Number of lines to scroll per interval
        """
        # Clamp amount between 1 and 10
        clamped_amount = max(1, min(10, amount))
        self.settings['scroll_amount'] = clamped_amount
        
        # Apply scroll amount change immediately if UI manager is available
        if self.ui_manager:
            self.ui_manager.apply_scroll_settings()
        
        self.logger.debug(f"Scroll amount updated to: {clamped_amount} lines")
    
    def update_scroll_opacity(self, base: int, hover: int) -> None:
        """
        Update scroll widget opacity settings.
        
        Args:
            base: Base opacity percentage
            hover: Hover opacity percentage
        """
        self.settings['scroll_opacity_base'] = clamp_value(base, 10, 100)
        self.settings['scroll_opacity_hover'] = clamp_value(hover, 10, 100)
        
        # Apply opacity change immediately if UI manager is available
        if self.ui_manager:
            self.ui_manager.apply_scroll_settings()
        
        self.logger.debug(f"Scroll opacity updated: base={base}%, hover={hover}%")
    
    def update_default_active(self, active: bool) -> None:
        """
        Update default active state setting.
        
        Args:
            active: Whether app should start active by default
        """
        self.settings['default_active'] = active
        self.logger.info(f"Default active state updated to: {active}")
    
    def update_visible_clicks_enabled(self, enabled: bool) -> None:
        """
        Update visible clicks enabled setting.
        
        Args:
            enabled: Whether visible click feedback is enabled
        """
        self.settings['visible_clicks_enabled'] = enabled
        self.logger.info(f"Visible clicks enabled: {enabled}")
    
    def update_contract_ui_enabled(self, enabled: bool) -> None:
        """
        Update UI contraction enabled setting and apply immediately.
        
        Args:
            enabled: Whether UI contraction is enabled
        """
        self.settings['contract_ui_enabled'] = enabled
        
        # Apply contraction change immediately if UI manager is available
        if self.ui_manager:
            self.ui_manager.apply_contraction_settings()
        
        self.logger.info(f"UI contraction enabled: {enabled}")
    
    def update_expansion_direction(self, direction: str) -> None:
        """
        Update UI expansion direction setting and apply immediately.
        
        Args:
            direction: Expansion direction ('auto', 'horizontal', 'vertical')
        """
        valid_directions = ['auto', 'horizontal', 'vertical']
        
        if direction in valid_directions:
            self.settings['expansion_direction'] = direction
            
            # Apply expansion direction change immediately if UI manager is available
            if self.ui_manager:
                self.ui_manager.apply_expansion_settings()
            
            self.logger.info(f"UI expansion direction updated to: {direction}")
        else:
            self.logger.warning(f"Invalid expansion direction: {direction}")
    
    def reset_to_defaults(self) -> None:
        """Reset all settings to their default values."""
        # Keep current window position
        current_position = self.settings.get('window_position')
        
        # Reset to defaults
        self.settings = DEFAULT_SETTINGS.copy()
        
        # Restore window position if it existed
        if current_position:
            self.settings['window_position'] = current_position
        
        # Apply settings to detector
        self.apply_detector_settings()
        
        # Apply transparency settings if UI manager available
        if self.ui_manager:
            self.ui_manager.apply_transparency_settings()
            self.ui_manager.apply_scroll_settings()
            self.ui_manager.apply_contraction_settings()
            self.ui_manager.apply_expansion_settings()
        
        self.logger.info("Settings reset to defaults")
    
    def get_all_settings(self) -> Dict[str, Any]:
        """
        Get a copy of all current settings.
        
        Returns:
            Dictionary containing all current settings
        """
        return self.settings.copy()
    
    def update_window_position(self, x: int, y: int) -> None:
        """
        Update the window position setting.
        
        Args:
            x: Window x coordinate
            y: Window y coordinate
        """
        self.settings['window_position'] = (x, y)
        self.logger.debug(f"Window position updated to: ({x}, {y})")
        # Note: We don't auto-save here to avoid excessive disk writes
        # Window position is saved when the app closes or settings dialog closes