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
	EXPANSION_DIRECTIONS,
	WIDGET_APPEARANCE_DELAY_MIN, WIDGET_APPEARANCE_DELAY_MAX,
	WIDGET_UNLOCK_THRESHOLD_MIN, WIDGET_UNLOCK_THRESHOLD_MAX,
	MENU_ITEM_SIZE_MIN, MENU_ITEM_SIZE_MAX
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
		
		# Sync widget appearance movement threshold with dwell detection
		if self.ui_manager and hasattr(self.ui_manager, 'cursor_movement_detector'):
			self.ui_manager.cursor_movement_detector.set_movement_threshold(clamped_value)
		
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
	
	def update_auto_start_enabled(self, enabled: bool) -> tuple[bool, str]:
		"""
		Update auto-start setting and apply immediately.
		
		Args:
			enabled: Whether app should start automatically on login
			
		Returns:
			Tuple of (success: bool, error_message: str). error_message is empty on success.
		"""
		self.settings['auto_start_enabled'] = enabled
		
		# Apply auto-start configuration immediately
		success, error_message = self._apply_auto_start_setting(enabled)
		
		if success:
			self.logger.info(f"Auto-start enabled: {enabled}")
		
		return success, error_message

	def _apply_auto_start_setting(self, enabled: bool) -> tuple[bool, str]:
		"""
		Apply auto-start setting to the operating system.
		Currently supports Linux (XDG autostart), Windows (Task Scheduler), and macOS (launchd).
		
		Args:
			enabled: Whether to enable or disable auto-start
			
		Returns:
			Tuple of (success: bool, error_message: str). error_message is empty on success.
		"""
		import os
		import platform
		if platform.system() == 'Linux':
			return self._apply_linux_autostart(enabled)
		elif platform.system() == 'Windows':
			return self._apply_windows_autostart(enabled)
		elif platform.system() == 'Darwin':
			return self._apply_macos_autostart(enabled)
		else:
			error_message = f"Auto-start not supported on {platform.system()}"
			self.logger.warning(error_message)
			return False, error_message
			
	def _apply_linux_autostart(self, enabled: bool) -> tuple[bool, str]:
		"""
		Apply Linux XDG autostart configuration.
		
		Args:
			enabled: Whether to enable or disable auto-start
			
		Returns:
			Tuple of (success: bool, error_message: str). error_message is empty on success.
		"""
		import os
		
		autostart_dir = os.path.expanduser("~/.config/autostart")
		autostart_file = os.path.join(autostart_dir, "dwellpy.desktop")
		desktop_file = os.path.expanduser("~/.local/share/applications/dwellpy.desktop")
		
		try:
			if enabled:
				# Create autostart directory if it doesn't exist
				os.makedirs(autostart_dir, exist_ok=True)
				
				# Check if the main desktop file exists
				if os.path.exists(desktop_file):
					# Copy the main desktop file to autostart
					import shutil
					shutil.copy2(desktop_file, autostart_file)
					self.logger.info(f"Auto-start enabled: copied {desktop_file} to {autostart_file}")
				else:
					# Create a basic autostart entry using the current executable path
					import sys
					
					# Get the executable path
					if getattr(sys, 'frozen', False):
						# Running as PyInstaller executable
						executable_path = sys.executable
					else:
						# Running as Python script - use python with the main script
						main_script = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'main.py')
						executable_path = f"{sys.executable} {main_script}"
					
					autostart_content = f"""[Desktop Entry]
Type=Application
Name=Dwellpy
Comment=Accessibility dwell clicker for motor disabilities
Exec={executable_path}
Icon=accessibility
Terminal=false
NoDisplay=false
Hidden=false
X-GNOME-Autostart-enabled=true
StartupNotify=false
Categories=Accessibility;Utility;
Keywords=accessibility;dwell;click;motor;disability;
"""
					with open(autostart_file, 'w', encoding='utf-8') as f:
						f.write(autostart_content)
					self.logger.info(f"Auto-start enabled: created {autostart_file} with executable: {executable_path}")
				return True, ""
			else:
				# Remove autostart file
				if os.path.exists(autostart_file):
					os.remove(autostart_file)
					self.logger.info(f"Auto-start disabled: removed {autostart_file}")
				return True, ""
		except Exception as e:
			error_message = f"Failed to configure auto-start: {str(e)}"
			self.logger.error(f"Error applying auto-start setting: {e}", exc_info=True)
			return False, error_message
	
	def _apply_windows_autostart(self, enabled: bool) -> tuple[bool, str]:
		"""
		Apply Windows auto-start configuration using Task Scheduler COM interface.
		Creates a scheduled task with highest privileges for optimal accessibility support.
		
		Args:
			enabled: Whether to enable or disable auto-start
			
		Returns:
			Tuple of (success: bool, error_message: str). error_message is empty on success.
		"""
		import os
		import sys
		import win32com.client
		
		task_name = "Dwellpy"
		try:
			if enabled:
				# Create a permanent batch file for all installation types
				# This provides a consistent, reliable approach that works for:
				# - PyInstaller executables
				# - Source installs 
				# - Pip installs
				batch_dir = os.path.join(os.path.expanduser("~"), ".dwellpy")
				os.makedirs(batch_dir, exist_ok=True)
				batch_file = os.path.join(batch_dir, "dwellpy_autostart.bat")
				vbs_file = os.path.join(batch_dir, "dwellpy_autostart.vbs")
						# Determine the appropriate command based on installation type
				if getattr(sys, 'frozen', False):
					# PyInstaller executable - run the exe directly
					command = sys.executable
				else:
					# Source install or pip install - use python -m dwellpy
					command = f'{sys.executable} -m dwellpy'
				
				# Create VBScript that runs the command completely silently (no window at all)
				# In VBScript, we need to escape quotes by doubling them
				escaped_command = command.replace('"', '""')
				vbs_content = f'CreateObject("Wscript.Shell").Run """{escaped_command}""", 0, False'
				
				# Write the VBScript file
				with open(vbs_file, 'w') as f:
					f.write(vbs_content)
				
				# Create a batch file that calls the VBScript (for fallback)
				batch_content = f'@echo off\ncscript //nologo "{vbs_file}"\n'
				
				# Write the batch file
				with open(batch_file, 'w') as f:
					f.write(batch_content)
				
				# Use the VBScript file for Task Scheduler (most reliable)
				exec_path = vbs_file
				start_dir = batch_dir
				arguments = ""
				
				try:
					# Initialize the scheduler
					scheduler = win32com.client.Dispatch('Schedule.Service')
					scheduler.Connect()
					
					# Get the root task folder
					root_folder = scheduler.GetFolder('\\')
					
					# Create a new task definition
					task_def = scheduler.NewTask(0)
					
					# Set registration info
					task_def.RegistrationInfo.Description = 'Dwellpy Auto-start'
					task_def.RegistrationInfo.Author = 'code0nwheels'
					task_def.Principal.UserId = ""  # Empty string means current user
					
					# Set principal (run with highest privileges)
					task_def.Principal.RunLevel = 1  # 1 = Highest privileges
					
					# Set task settings
					task_def.Settings.Enabled = True
					task_def.Settings.StartWhenAvailable = True
					task_def.Settings.DisallowStartIfOnBatteries = False
					task_def.Settings.StopIfGoingOnBatteries = False
					task_def.Settings.ExecutionTimeLimit = "PT0S"  # No time limit
					
					# Create a logon trigger
					trigger = task_def.Triggers.Create(9)  # 9 = TASK_TRIGGER_LOGON
					trigger.Enabled = True
					
					# Create the action
					action = task_def.Actions.Create(0)  # 0 = TASK_ACTION_EXEC
					action.Path = exec_path
					action.Arguments = arguments
					action.WorkingDirectory = start_dir  # Set working directory to executable/script directory
					
					# Register the task (create or update if exists)
					root_folder.RegisterTaskDefinition(
						task_name,
						task_def,
						6,  # 6 = TASK_CREATE_OR_UPDATE
						None,  # User - defaults to current user
						None,  # Password
						3      # 3 = TASK_LOGON_INTERACTIVE_TOKEN
					)
					
					self.logger.info(f"Auto-start enabled: created scheduled task '{task_name}' using VBScript: {exec_path}")
					return True, ""
					
				except Exception as e:
					user_message = f"Failed to enable auto-start using Windows Task Scheduler.\n\nError details: {str(e)}"
					self.logger.error(f"Error creating Windows scheduled task: {e}", exc_info=True)
					return False, user_message
			else:
				# Remove the scheduled task
				try:
					# Initialize the scheduler
					scheduler = win32com.client.Dispatch('Schedule.Service')
					scheduler.Connect()
					root_folder = scheduler.GetFolder('\\')
					
					# Check if the task exists before trying to delete
					try:
						root_folder.DeleteTask(task_name, 0)
						self.logger.info(f"Auto-start disabled: removed scheduled task '{task_name}'")
								# Also clean up batch and VBScript files if they exist
						batch_dir = os.path.join(os.path.expanduser("~"), ".dwellpy")
						batch_file = os.path.join(batch_dir, "dwellpy_autostart.bat")
						vbs_file = os.path.join(batch_dir, "dwellpy_autostart.vbs")
						
						# Clean up batch file
						if os.path.exists(batch_file):
							try:
								os.remove(batch_file)
								self.logger.info(f"Auto-start disabled: cleaned up batch file {batch_file}")
							except Exception as cleanup_error:
								self.logger.warning(f"Could not clean up batch file {batch_file}: {cleanup_error}")
						
						# Clean up VBScript file
						if os.path.exists(vbs_file):
							try:
								os.remove(vbs_file)
								self.logger.info(f"Auto-start disabled: cleaned up VBScript file {vbs_file}")
							except Exception as cleanup_error:
								self.logger.warning(f"Could not clean up VBScript file {vbs_file}: {cleanup_error}")
						
						return True, ""
					except Exception as e:
						# Task might not exist, which is fine
						if "cannot find" in str(e).lower() or "not found" in str(e).lower():
							self.logger.info(f"Auto-start disabled: scheduled task '{task_name}' was not found (already disabled)")
									# Still try to clean up batch and VBScript files if they exist
							batch_dir = os.path.join(os.path.expanduser("~"), ".dwellpy")
							batch_file = os.path.join(batch_dir, "dwellpy_autostart.bat")
							vbs_file = os.path.join(batch_dir, "dwellpy_autostart.vbs")
							
							# Clean up batch file
							if os.path.exists(batch_file):
								try:
									os.remove(batch_file)
									self.logger.info(f"Auto-start disabled: cleaned up batch file {batch_file}")
								except Exception as cleanup_error:
									self.logger.warning(f"Could not clean up batch file {batch_file}: {cleanup_error}")
							
							# Clean up VBScript file
							if os.path.exists(vbs_file):
								try:
									os.remove(vbs_file)
									self.logger.info(f"Auto-start disabled: cleaned up VBScript file {vbs_file}")
								except Exception as cleanup_error:
									self.logger.warning(f"Could not clean up VBScript file {vbs_file}: {cleanup_error}")
							
							return True, ""
						else:
							# Re-raise other errors
							user_message = f"Failed to disable auto-start.\n\nError details: {str(e)}"
							self.logger.error(f"Error removing scheduled task: {e}", exc_info=True)
							return False, user_message
				except Exception as e:
					user_message = f"An unexpected error occurred while disabling auto-start.\n\nError details: {str(e)}"
					self.logger.error(f"Error removing Windows scheduled task: {e}", exc_info=True)
					return False, user_message
		except PermissionError as e:
			user_message = "Permission denied when configuring auto-start.\n\nPlease run Dwellpy as Administrator to modify scheduled tasks."
			self.logger.error(f"Permission denied when configuring Windows auto-start. Please run Dwellpy as Administrator to modify scheduled tasks. Error: {e}")
			return False, user_message
		except win32com.client.pywintypes.com_error as e:
			user_message = f"COM error when configuring auto-start. Error code: {e.hresult}\n\nPlease run Dwellpy as Administrator to modify scheduled tasks."
			self.logger.error(f"COM error when configuring Windows auto-start: {e}", exc_info=True)
			return False, user_message
		except Exception as e:
			user_message = f"An unexpected error occurred while configuring auto-start.\n\nError details: {str(e)}"
			self.logger.error(f"Error applying Windows auto-start setting: {e}", exc_info=True)
			return False, user_message

	def _apply_macos_autostart(self, enabled: bool) -> tuple[bool, str]:
		"""
		Apply macOS auto-start configuration using launchd.
		Creates a Launch Agent plist file for user login.
		
		Args:
			enabled: Whether to enable or disable auto-start
			
		Returns:
			Tuple of (success: bool, error_message: str). error_message is empty on success.
		"""
		import os
		import sys
		import plistlib
		
		launchagents_dir = os.path.expanduser("~/Library/LaunchAgents")
		plist_filename = "com.dwellpy.accessibility.plist"
		plist_path = os.path.join(launchagents_dir, plist_filename)
		
		try:
			if enabled:
				# Get the executable path
				if getattr(sys, 'frozen', False):
					# Running as PyInstaller executable
					executable_path = sys.executable
					program_arguments = [executable_path]
				else:
					# Running as Python script - use python with the main script
					main_script = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'main.py')
					program_arguments = [sys.executable, main_script]
				
				# Create launch agent plist data
				plist_data = {
					'Label': 'com.dwellpy.accessibility',
					'ProgramArguments': program_arguments,
					'RunAtLoad': True,
					'KeepAlive': False,
					'ProcessType': 'Interactive'  # Allows GUI applications
				}
				
				# Ensure the LaunchAgents directory exists
				os.makedirs(launchagents_dir, exist_ok=True)
				
				# Write the plist file
				with open(plist_path, 'wb') as f:
					plistlib.dump(plist_data, f)
				
				self.logger.info(f"Auto-start enabled: created Launch Agent at {plist_path} with executable: {' '.join(program_arguments)}")
			else:
				# Remove the plist file
				if os.path.exists(plist_path):
					os.remove(plist_path)
					self.logger.info(f"Auto-start disabled: removed Launch Agent {plist_path}")
				else:
					self.logger.info(f"Auto-start disabled: Launch Agent {plist_path} was not found (already disabled)")
					
		except Exception as e:
			self.logger.error(f"Error applying macOS auto-start setting: {e}", exc_info=True)
	
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
	
	def update_widget_appearance_delay(self, delay: float) -> None:
		"""
		Update widget appearance delay setting.
		
		Args:
			delay: Time in seconds to wait before showing widgets after cursor stops
		"""
		# Clamp delay between min and max values
		clamped_delay = max(WIDGET_APPEARANCE_DELAY_MIN, min(WIDGET_APPEARANCE_DELAY_MAX, delay))
		self.settings['widget_appearance_delay'] = clamped_delay
		
		# Apply widget appearance delay change immediately if UI manager is available
		if self.ui_manager:
			self.ui_manager.apply_widget_appearance_settings()
		
		self.logger.debug(f"Widget appearance delay updated to: {clamped_delay} seconds")
	
	def update_widget_unlock_threshold(self, threshold: int) -> None:
		"""
		Update widget unlock threshold setting.
		
		Args:
			threshold: Distance in pixels cursor must move from widget before it starts following again
		"""
		# Import constants for validation
		from ..config.constants import WIDGET_UNLOCK_THRESHOLD_MIN, WIDGET_UNLOCK_THRESHOLD_MAX
		
		# Clamp threshold between min and max values
		clamped_threshold = max(WIDGET_UNLOCK_THRESHOLD_MIN, min(WIDGET_UNLOCK_THRESHOLD_MAX, threshold))
		self.settings['widget_unlock_threshold'] = clamped_threshold
		
		# Apply threshold change immediately if UI manager is available
		if self.ui_manager:
			self.ui_manager.set_unlock_threshold(clamped_threshold)
		
		self.logger.debug(f"Unlock threshold updated to: {clamped_threshold}px")

	def update_menu_item_size(self, size: int) -> None:
		"""
		Update menu item size setting and apply immediately.
		
		Args:
			size: New menu item size in pixels
		"""
		clamped_size = clamp_value(size, MENU_ITEM_SIZE_MIN, MENU_ITEM_SIZE_MAX)
		self.settings['menu_item_size'] = clamped_size
		
		# Apply size change immediately if UI manager is available
		if self.ui_manager:
			self.ui_manager.update_menu_item_size(clamped_size)
		
		self.logger.info(f"Menu item size updated to: {clamped_size}px")