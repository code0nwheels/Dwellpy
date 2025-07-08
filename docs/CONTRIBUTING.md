# Contributing to Dwellpy

Thank you for your interest in contributing to Dwellpy! This project was created by and for the disability community, and we welcome contributions that make accessibility technology better for everyone.

## How to Contribute

### Report Bugs

Found a bug? Please search existing issues first, then create a new one with:
- Clear description of the problem
- Steps to reproduce
- Your system information (OS, Python version, etc.)
- Expected vs. actual behavior

[Create a bug report](https://github.com/code0nwheels/dwellpy/issues/new)

### Improve Documentation

Help make our guides clearer:
- Fix typos or unclear instructions
- Add missing information
- Improve setup guides for your platform

### Suggest Features
- Open a [GitHub Issue](https://github.com/code0nwheels/dwellpy/issues) with the "enhancement" label
- Describe the accessibility need the feature would address
- Explain how it would help users with disabilities

## Development Setup

### Prerequisites
- Python 3.9 or higher
- Git

### Setup Steps
1. **Fork and clone the repository**:
   ```bash
   git clone https://github.com/YOUR_USERNAME/dwellpy.git
   cd dwellpy
   ```

2. **Create a virtual environment**:
   ```bash
   python -m venv venv
   
   # Activate it:
   # Windows:
   venv\Scripts\activate
   # macOS/Linux:
   source venv/bin/activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Run from source**:
   ```bash
   python -m dwellpy.main
   ```

### Development Tools
- **Code style**: Write clean, readable Python code
- **Testing**: Manual testing for now (automated tests welcome!)
- **Documentation**: Update docs when changing functionality

## Code Guidelines

### Architecture Overview
Dwellpy follows a modular architecture with clear separation of concerns:

- **Bootstrap**: Application startup and initialization logic
- **Core**: Core functionality including dwell detection, input handling, and click execution
- **UI**: User interface components with modular drawing and interaction logic
- **Managers**: Application state management and lifecycle components
- **Config**: Configuration constants and settings definitions

When contributing, please follow the existing modular structure and place new functionality in the appropriate module.

### Python Style
- Write clean, readable code
- Use meaningful variable names
- Add docstrings to functions and classes
- Keep functions focused and small
- Try to follow Python best practices

### Example:
```python
def calculate_dwell_threshold(sensitivity: int, user_capability: str) -> float:
    """
    Calculate appropriate dwell time based on user needs.
    
    Args:
        sensitivity: User-configured sensitivity (1-10)
        user_capability: Type of motor capability ("precise", "tremor", "fatigue")
        
    Returns:
        Appropriate dwell time in seconds
    """
    # Implementation here
```

### UI Components
- Use descriptive names for UI elements
- Include accessibility features (screen reader compatibility where applicable)
- Test with different input methods (mouse, head tracker, eye tracker)
- Ensure high contrast for visibility

### Accessibility First
Remember that Dwellpy users may have:
- Limited motor control
- Vision impairments
- Cognitive differences
- Fatigue issues

Design accordingly:
- Clear, large buttons
- Simple interfaces
- Helpful error messages
- Sensible defaults

## Pull Request Process

### Before Submitting
1. **Test thoroughly** on your platform
2. **Check existing issues** to see if your change addresses one
3. **Update documentation** if you're changing functionality
4. **Keep changes focused** - one feature/fix per PR

### PR Guidelines
1. **Use a clear title**: "Fix scroll widget positioning on multi-monitor setups"
2. **Describe the change**: What problem does this solve?
3. **List testing done**: What platforms/scenarios did you test?
4. **Reference issues**: Use "Fixes #123" to link to issues

### Example PR Description
```
## Problem
Scroll widget appears off-screen on multi-monitor setups with different DPI scaling.

## Solution  
- Added DPI-aware coordinate conversion
- Improved monitor detection logic
- Added bounds checking for widget positioning

## Testing
- Tested on Windows 11 with 2 monitors (different DPI)
- Tested on macOS with external monitor
- Verified single monitor setups still work correctly

Fixes #45
```

## Issue Guidelines

### Bug Reports
Include:
- **OS and version**: Windows 11, macOS 12.3, Ubuntu 22.04, etc.
- **Python version**: Output of `python --version`
- **Dwellpy version**: From pip or git commit
- **Input device**: Mouse, head tracker, eye tracker, etc.
- **Steps to reproduce**: Numbered list
- **Expected vs actual behavior**
- **Error messages**: Full text, not screenshots

### Feature Requests
Include:
- **Accessibility need**: What disability/condition would this help?
- **Use case**: Specific scenario where this would be useful
- **Proposed solution**: How you think it should work
- **Alternatives considered**: Other ways to solve the problem

## Community Guidelines

### Be Respectful
- Use inclusive language
- Assume good intentions
- Focus on the technical merits of ideas
- Remember many users have disabilities that affect communication

### Be Patient
- Contributors may be using assistive technology
- Response times may vary due to health conditions
- Provide clear, helpful feedback on PRs

### Be Helpful
- Answer questions when you can
- Help test changes on different platforms
- Share your expertise with accessibility tools

## Recognition

All contributors will be:
- Listed in the project's contributors section
- Credited in release notes for significant contributions
- Invited to provide input on major feature decisions

## Getting Help

- **General questions**: [GitHub Discussions](https://github.com/code0nwheels/dwellpy/discussions)
- **Development help**: Create an issue with "question" label
- **Accessibility guidance**: We're happy to help with accessibility best practices

## Code of Conduct

This project follows a simple principle: **Make technology more accessible for everyone.**

We expect all contributors to:
- Treat others with respect and kindness
- Welcome newcomers and help them contribute
- Focus on what's best for the accessibility community
- Communicate clearly and helpfully

Unacceptable behavior includes harassment, discrimination, or making the project less accessible to people with disabilities.

---

Thank you for contributing to Dwellpy! Together we can make computing more accessible for everyone.