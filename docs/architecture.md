# Dwellpy Architecture Documentation

This document provides an overview of Dwellpy's architecture, design patterns, and recent improvements.

## Overview

Dwellpy is designed as a modular, accessibility-first application that provides dwell-clicking functionality for users with motor disabilities. The architecture emphasizes:

- **Modularity**: Clear separation of concerns with focused, manageable components
- **Accessibility**: Dwell-friendly interfaces and assistive technology compatibility
- **Maintainability**: Clean, readable code with logical organization
- **Extensibility**: Easy to add new features and settings

## Core Architecture

### High-Level Structure

```
dwellpy/
├── bootstrap/           # Application startup and initialization
├── core/               # Core functionality (dwell detection, input handling)
├── ui/                 # User interface components
├── managers/           # Application state and lifecycle management
├── config/             # Configuration and constants
└── utils/              # Utility functions and helpers
```

### Key Design Principles

1. **Separation of Concerns**: Each module has a specific responsibility
2. **Dependency Injection**: Managers are injected into components that need them
3. **Event-Driven Architecture**: UI components communicate through events
4. **Accessibility First**: All interfaces designed for dwell interaction
5. **Cross-Platform Compatibility**: Consistent behavior across Windows, macOS, and Linux

## Component Details

### Bootstrap (`dwellpy/bootstrap/`)

Responsible for application startup and component initialization.

**Key Responsibilities:**
- Parse command-line arguments
- Initialize core components
- Set up dependency injection
- Handle application lifecycle

### Core (`dwellpy/core/`)

Contains the fundamental functionality that makes dwell-clicking work.

**Components:**
- **`click_manager.py`**: Executes mouse clicks and drag operations
- **`dwell_algorithm.py`**: Implements dwell detection algorithms
- **`input_manager.py`**: Handles input device tracking and position monitoring
- **`detection/`**: Dwell detection components and movement analysis

**Key Features:**
- Real-time cursor position tracking
- Configurable dwell detection sensitivity
- Support for multiple click types (left, right, double, drag)
- Movement detection for widget visibility

### UI (`dwellpy/ui/`)

User interface components with a focus on accessibility and dwell interaction.

**Main Components:**
- **`ui_manager.py`**: Main UI orchestration and window management
- **`components/`**: Modular UI components
  - `cursor_movement_detector.py`: Cursor movement analysis
  - `ui_contraction.py`: UI contraction/expansion logic
  - `menu_drawing.py`: Menu widget drawing
  - `scroll_drawing.py`: Scroll widget drawing
- **`menu_widget.py`**: Floating menu widget implementation
- **`scroll_widget.py`**: Floating scroll widget implementation
- **`dialogs/`**: Settings and configuration dialogs

#### Settings Dialog Architecture (Recent Improvement)

The settings dialog has been successfully modularized from a single 1,451-line file into a well-organized, maintainable structure with improved accessibility and user experience:

```
dwellpy/ui/dialogs/settings/
├── components/           # Reusable UI components
│   ├── ui_components.py  # UI helper functions (headers, buttons, styling)
│   ├── event_handlers.py # Event handling logic and hover functionality
│   └── __init__.py
├── tabs/                 # Individual settings tabs
│   ├── dwell_movement_tab.py    # Dwell timing and movement settings
│   ├── visual_feedback_tab.py   # Transparency and click feedback
│   ├── scroll_widget_tab.py     # Scroll widget configuration
│   ├── menu_widget_tab.py       # Menu item size settings
│   ├── general_tab.py           # Startup and UI behavior
│   └── __init__.py
└── settings_dialog.py    # Main dialog orchestrator (~300 lines)
```

**Benefits of the new structure:**
- **Maintainability**: Each tab is a focused, manageable module (~100-150 lines each)
- **Reusability**: UI components and event handlers can be shared across tabs
- **Organization**: Related functionality is logically grouped into 3 main tabs (Behavior, Visual, Widgets)
- **Preserved Functionality**: All original features maintained with improved organization
- **Developer Experience**: Easier to locate and modify specific settings
- **Accessibility**: Enhanced keyboard navigation, tooltips, and consistent sizing
- **User Experience**: More compact layout with better visual hierarchy

**Design Patterns Used:**
- **Component Pattern**: Reusable UI components (headers, buttons, sliders)
- **Event Handler Pattern**: Centralized event handling with hover functionality
- **Tab Pattern**: Each settings category in its own focused module
- **Orchestrator Pattern**: Main dialog coordinates tab creation and signal connections
- **Accessibility Pattern**: Consistent sizing, keyboard navigation, and visual feedback

### Managers (`dwellpy/managers/`)

Application state management and lifecycle components.

**Components:**
- **`button_manager.py`**: Button state and command management
- **`settings_manager.py`**: Settings persistence and management
- **`window_manager.py`**: Window positioning and management
- **`exit_manager.py`**: Application exit handling
- **`lifecycle/`**: Application lifecycle components
  - `component_initializer.py`: Component initialization and dependency injection

**Key Features:**
- Persistent settings storage
- Cross-platform window management
- Graceful application shutdown
- Component lifecycle management

### Config (`dwellpy/config/`)

Configuration constants and settings definitions.

**Components:**
- **`constants.py`**: Application-wide constants and default values
- **`__init__.py`**: Configuration package exports

**Key Constants:**
- UI dimensions and styling
- Default settings values
- Platform-specific configurations
- Accessibility-related constants

### Utils (`dwellpy/utils/`)

Utility functions and helpers used throughout the application.

**Components:**
- **`helpers.py`**: General utility functions
- **`logging_config.py`**: Logging configuration
- **`__init__.py`**: Utility package exports

## Data Flow

### Application Startup
1. **Bootstrap** initializes core components
2. **Component Initializer** sets up dependency injection
3. **UI Manager** creates main interface
4. **Settings Manager** loads saved configuration
5. **Input Manager** begins cursor tracking

### Dwell Detection Flow
1. **Input Manager** tracks cursor position
2. **Dwell Algorithm** analyzes movement patterns
3. **UI Manager** updates widget visibility
4. **Button Manager** handles hover states
5. **Click Manager** executes actions when dwell threshold reached

### Settings Management Flow
1. **Settings Dialog** presents organized interface
2. **Tab Modules** handle specific setting categories
3. **Event Handlers** process user interactions
4. **Settings Manager** persists changes
5. **UI Components** apply new settings immediately

## Design Patterns

### Dependency Injection
Managers are injected into components that need them, promoting loose coupling and testability.

```python
class DwellClickerUI:
    def __init__(self, click_manager, dwell_detector, button_manager, window_manager):
        self.click_manager = click_manager
        self.dwell_detector = dwell_detector
        # ... other dependencies
```

### Event-Driven Architecture
UI components communicate through events rather than direct method calls.

```python
# Event handling in settings tabs
self.slider.valueChanged.connect(self.event_handlers.update_value)
self.checkbox.toggled.connect(self.event_handlers.on_toggle)
```

### Component Pattern
Reusable UI components with consistent styling and behavior.

```python
# Shared UI components
from .components.ui_components import create_section_header, create_adjustment_button
```

### Observer Pattern
Settings changes are observed and applied immediately throughout the application.

```python
# Settings manager notifies components of changes
self.settings_manager.set_setting('dwell_time', new_value)
# UI components automatically update
```

## Accessibility Features

### Dwell-Friendly Design
- Large, easy-to-target buttons
- Hover functionality for fine adjustments
- Clear visual feedback
- Configurable sensitivity

### Assistive Technology Support
- High contrast interfaces
- Screen reader compatibility (where applicable)
- Keyboard navigation support
- Customizable timing and sensitivity

### Cross-Platform Compatibility
- Consistent behavior across operating systems
- Platform-specific optimizations
- Native look and feel integration

## Performance Considerations

### Real-Time Processing
- Efficient cursor position tracking
- Optimized dwell detection algorithms
- Minimal UI update overhead

### Memory Management
- Proper cleanup of timers and resources
- Efficient widget positioning calculations
- Smart caching of frequently accessed settings

### Responsiveness
- Non-blocking UI operations
- Smooth animations and transitions
- Immediate feedback for user actions

## Testing Strategy

### Current Testing
- Manual testing across platforms
- Accessibility testing with assistive technologies
- Performance testing with various input devices

### Future Testing Plans
- Automated unit tests for core components
- Integration tests for UI workflows
- Accessibility compliance testing
- Performance benchmarking

## Future Architecture Considerations

### Planned Improvements
- Enhanced modularity for additional features
- Improved error handling and recovery
- Better internationalization support
- Advanced accessibility features

### Scalability
- Plugin architecture for custom click types
- Extensible settings system
- Modular widget system
- Configuration import/export capabilities

## Conclusion

Dwellpy's architecture emphasizes modularity, accessibility, and maintainability. The recent settings dialog modularization demonstrates the project's commitment to code quality and developer experience while preserving all functionality for end users.

The architecture provides a solid foundation for future enhancements while maintaining the accessibility-first approach that makes Dwellpy valuable for users with motor disabilities. 