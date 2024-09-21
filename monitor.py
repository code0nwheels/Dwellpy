# monitor.py
import time
import math

class Monitor:
    def start_monitoring(self):
        self.dwell_start_time = None
        self.dwell_triggered = False
        self.initial_dwell_position = None
        self.monitor_mouse()

    def monitor_mouse(self):
        current_time = time.perf_counter()
        current_position = self.mouse_controller.position

        # Handle move mode
        if self.moving:
            # Move the window to follow the cursor
            self.root.geometry(f"+{current_position[0]-self.move_offset_x}+{current_position[1]-self.move_offset_y}")

        # Dwell detection logic
        if self.is_running or self.is_cursor_over_app():
            if self.dwell_start_time is None:
                # Start a new dwell period
                self.dwell_start_time = current_time
                self.initial_dwell_position = current_position
                self.dwell_triggered = False
            else:
                # Check if cursor has moved beyond the radius
                if self.initial_dwell_position is not None and self.has_cursor_moved(current_position, self.initial_dwell_position):
                    # Cursor moved; reset dwell detection
                    self.dwell_start_time = None
                    self.dwell_triggered = False
                    self.initial_dwell_position = None
                elif not self.dwell_triggered and (current_time - self.dwell_start_time) >= self.dwell_time:
                    # Dwell time met; trigger action
                    self.trigger_action()
                    self.dwell_triggered = True
        else:
            # Reset dwell detection
            self.dwell_start_time = None
            self.dwell_triggered = False
            self.initial_dwell_position = None

        # Schedule the next call to monitor_mouse
        self.root.after(10, self.monitor_mouse)

    def has_cursor_moved(self, current_pos, initial_pos):
        if initial_pos is None:
            return False
        dist = math.hypot(current_pos[0] - initial_pos[0], current_pos[1] - initial_pos[1])
        return dist > self.radius

    def is_cursor_over_app(self):
        x, y = self.mouse_controller.position
        # Determine which widgets to consider
        if self.is_running:
            # Application is running; consider all visible widgets
            widgets_to_check = self.get_visible_widgets(self.root)
        else:
            # Application is off; only consider the toggle button
            widgets_to_check = [self.toggle_button]

        for widget in widgets_to_check:
            widget_x = widget.winfo_rootx()
            widget_y = widget.winfo_rooty()
            widget_width = widget.winfo_width()
            widget_height = widget.winfo_height()
            if widget_x <= x <= widget_x + widget_width and widget_y <= y <= widget_y + widget_height:
                return True
        return False

    def get_visible_widgets(self, parent):
        widgets = []
        for widget in parent.winfo_children():
            if widget.winfo_viewable():
                widgets.append(widget)
                # Recursively check for child widgets
                widgets.extend(self.get_visible_widgets(widget))
        return widgets
# monitor.py
import time
import math

class Monitor:
    def start_monitoring(self):
        self.dwell_start_time = None
        self.dwell_triggered = False
        self.initial_dwell_position = None
        self.monitor_mouse()

    def monitor_mouse(self):
        current_time = time.perf_counter()
        current_position = self.mouse_controller.position

        # Handle move mode
        if self.moving:
            # Move the window to follow the cursor
            self.root.geometry(f"+{current_position[0]-self.move_offset_x}+{current_position[1]-self.move_offset_y}")

        # Dwell detection logic
        if self.is_running or self.is_cursor_over_app():
            if self.dwell_start_time is None:
                # Start a new dwell period
                self.dwell_start_time = current_time
                self.initial_dwell_position = current_position
                self.dwell_triggered = False
            else:
                # Check if cursor has moved beyond the radius
                if self.initial_dwell_position is not None and self.has_cursor_moved(current_position, self.initial_dwell_position):
                    # Cursor moved; reset dwell detection
                    self.dwell_start_time = None
                    self.dwell_triggered = False
                    self.initial_dwell_position = None
                elif not self.dwell_triggered and (current_time - self.dwell_start_time) >= self.dwell_time:
                    # Dwell time met; trigger action
                    self.trigger_action()
                    self.dwell_triggered = True
        else:
            # Reset dwell detection
            self.dwell_start_time = None
            self.dwell_triggered = False
            self.initial_dwell_position = None

        # Schedule the next call to monitor_mouse
        self.root.after(10, self.monitor_mouse)

    def has_cursor_moved(self, current_pos, initial_pos):
        if initial_pos is None:
            return False
        dist = math.hypot(current_pos[0] - initial_pos[0], current_pos[1] - initial_pos[1])
        return dist > self.radius

    def is_cursor_over_app(self):
        x, y = self.mouse_controller.position
        # Determine which widgets to consider
        if self.is_running:
            # Application is running; consider all visible widgets
            widgets_to_check = self.get_visible_widgets(self.root)
        else:
            # Application is off; only consider the toggle button
            widgets_to_check = [self.toggle_button]

        for widget in widgets_to_check:
            widget_x = widget.winfo_rootx()
            widget_y = widget.winfo_rooty()
            widget_width = widget.winfo_width()
            widget_height = widget.winfo_height()
            if widget_x <= x <= widget_x + widget_width and widget_y <= y <= widget_y + widget_height:
                return True
        return False

    def get_visible_widgets(self, parent):
        widgets = []
        for widget in parent.winfo_children():
            if widget.winfo_viewable():
                widgets.append(widget)
                # Recursively check for child widgets
                widgets.extend(self.get_visible_widgets(widget))
        return widgets
