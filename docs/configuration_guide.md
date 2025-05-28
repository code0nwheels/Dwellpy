# Configuration Guide

This guide explains how to adjust Dwellpy's settings for your specific needs.

## Opening Settings

Click the **SETUP** button on the Dwellpy toolbar to open the settings dialog.

## Core Settings

### Move Limit (3-20 pixels)
**What it does**: Maximum distance your cursor can move while still "dwelling" in one spot.

**How to adjust**: Use the slider or hover over the +/- buttons.

**Recommended values**:
- **3-8 pixels**: Good cursor control (regular mouse, precise head tracker)
- **8-15 pixels**: Head tracker users, minor tremors
- **12-20 pixels**: Hand tremors, cerebral palsy, less precise control

**Tips**:
- Start with 8-10 pixels and adjust from there
- Too low = hard to dwell (keeps resetting)
- Too high = accidental clicks when moving between targets

### Dwell Time (0.1-2.0 seconds)
**What it does**: How long you must hold your cursor in position before a click happens.

**How to adjust**: Use the slider or hover over the +/- buttons.

**Recommended values**:
- **0.1-0.5 seconds**: Quick response, less fatigue
- **0.5-0.8 seconds**: Balanced (good for most head tracker users)
- **0.8-2.0 seconds**: Prevents accidental clicks, gives time to move away

**Tips**:
- Shorter times = faster but more accidental clicks
- Longer times = slower but more deliberate
- Most users find 0.6-0.8 seconds works well

## Visual Settings

### Window Transparency
**Enable window transparency**: Makes the toolbar see-through when your cursor isn't over it.

**Transparency level**: How see-through the toolbar becomes (10-90%).

**Why use it**: Reduces visual clutter while keeping the toolbar accessible.

**Recommended**: Enable at 70% transparency for most users.

### Visible Clicks
**What it does**: Shows a brief visual animation (expanding circle) at the location where clicks are performed.

**Colors by click type**:
- **Blue**: Left clicks
- **Green**: Right clicks  
- **White**: Double clicks and middle clicks
- **Red**: Drag actions (both down and up)

**When to enable**: 
- Learning to use Dwellpy effectively
- Confirming clicks are happening where expected
- Troubleshooting click accuracy issues
- Presentations or demonstrations

**When to disable**: 
- Reduces visual distractions during regular use
- Gaming or video applications where animations might interfere
- Battery optimization on portable devices

**Default setting**: Enabled

### Start Active on Launch
**What it does**: Automatically turns on dwell clicking when Dwellpy starts.

**When to enable**: If you always want dwell clicking active immediately.

**When to disable**: If you prefer to manually turn it on when needed.

## Scroll Widget Settings

### Enable Scroll Widget
**What it does**: Shows/hides the floating scroll helper that follows your cursor.

**When to enable**: For reading documents, browsing web pages, or working with long content.

**When to disable**: When using on-screen keyboards or other tools that might conflict.

### Scroll Speed (1-10)
**What it does**: Controls how fast scrolling happens when you hover over the scroll arrows.

**Scale**: 1 = slowest (200ms between scrolls), 10 = fastest (20ms between scrolls)

**Recommended values**:
- **1-3**: Slow, controlled scrolling for precise reading
- **4-6**: Medium speed for general use
- **7-10**: Fast scrolling for quickly moving through content

## Click Mode Settings

### Understanding Click Modes
Dwellpy has two types of click modes:

- **Default Mode (Blue button)**: LEFT click - your primary click type, always returns to this
- **Temporary Mode (Red button)**: Used once, then returns to LEFT click

### How to Use Modes
1. **Use temporary mode**: Click any mode button other than LEFT (turns red)
2. **Make temporary permanent**: Click the same red button again (stays red until used)
3. **Return to LEFT**: All modes return to LEFT click after being used once

The default mode is always LEFT click and cannot be changed.

## Condition-Specific Recommendations

### Head Tracker Users
```
Move Limit: 10-15 pixels
Dwell Time: 0.5-0.8 seconds
Scroll Speed: 3-5
Transparency: Enabled at 70%
Visible Clicks: Enabled (helpful for learning)
Auto Collapse: Enabled
Expansion Direction: Auto
```

**Why**: Head trackers have natural small movements, so higher move limit prevents constant resets. Medium dwell time balances speed with accuracy. Auto collapse reduces visual clutter while maintaining quick access.

### Hand Tremors/Cerebral Palsy
```
Move Limit: 12-20 pixels
Dwell Time: 0.3-0.6 seconds (adjust based on tremor frequency)
Scroll Speed: 2-4
Transparency: Enabled at 60-80%
Visible Clicks: Enabled (confirms successful clicks)
Auto Collapse: Disabled (keeps controls always visible)
```

**Why**: Higher move limit accommodates tremor movement. Dwell time may need to be shorter if maintaining position is difficult. Keep UI expanded for easier target acquisition.

### Fatigue/Weakness Conditions
```
Move Limit: 8-12 pixels
Dwell Time: 0.1-0.5 seconds
Scroll Speed: 6-8
Start Active: Enabled
Visible Clicks: Enabled
Auto Collapse: Enabled
Expansion Direction: Auto
```

**Why**: Shorter dwell time reduces sustained effort needed. Faster scroll speed for efficiency. Auto-start eliminates need to manually activate. Auto collapse reduces cognitive load.

### Eye Tracking Integration
```
Move Limit: 15-20 pixels
Dwell Time: 0.8-1.2 seconds
Scroll Speed: 2-3
Visible Clicks: Disabled (reduces eye strain)
Auto Collapse: Enabled
Expansion Direction: Horizontal (easier eye movement patterns)
```

**Why**: Eye trackers can be less precise than other input methods. Longer dwell time prevents accidental activation from brief glances. Horizontal layout supports natural left-right eye scanning.

## Troubleshooting Settings

### Too Many Accidental Clicks
- Increase Dwell Time (try +0.2 seconds)
- Decrease Move Limit (try -2 pixels)
- Check if scroll widget is interfering

### Clicks Not Registering
- Decrease Dwell Time (try -0.2 seconds)  
- Increase Move Limit (try +3 pixels)
- Ensure transparency isn't too high

### Difficulty with Precision Tasks
- Temporarily switch to a different mode for precision work
- Consider lowering Move Limit for detailed tasks
- Use scroll widget for document navigation instead of precise scrolling

### Performance Issues
- Disable transparency if using older hardware
- Reduce scroll speed if system feels sluggish
- Close other accessibility tools that might conflict
- Disable visible clicks if experiencing frame rate issues in applications

### UI Responsiveness Issues
- If auto collapse interferes with workflow, disable it in settings
- Try different expansion directions if UI expands in wrong direction
- Ensure cursor movement isn't triggering constant collapse/expand cycles

### Visual Feedback Problems
- Disable visible clicks if animations cause seizures or motion sensitivity
- Adjust expansion direction if UI blocks important screen areas
- Consider transparency settings if collapsed UI is hard to see

## Advanced Tips

### Quick Settings Changes
You can hover over the +/- buttons in settings to adjust values quickly without dragging sliders.

### Testing Your Settings
After changing settings:
1. Try clicking on different sized targets
2. Test scrolling through a document
3. Try precision tasks like selecting text
4. Adjust as needed

### Backup Your Configuration
Your settings are saved automatically, but if you find settings that work well, note them down in case you need to reinstall.

**Future Enhancement**: Multiple user profiles for different activities (reading vs. productivity) would be a useful addition.

## Quick Reference

| Task | Move Limit | Dwell Time | Visible Clicks | Auto Collapse | Notes |
|------|------------|------------|----------------|---------------|-------|
| General use | 8-12px | 0.6-0.8s | Enabled | Enabled | Balanced settings |
| Reading/browsing | 10-15px | 0.4-0.6s | Enabled | Enabled | Enable scroll widget |
| Precision work | 5-8px | 0.8-1.0s | Enabled | Disabled | Temporary mode helpful |
| Gaming | 6-10px | 0.3-0.5s | Disabled | Disabled | Fast response needed |
| Drawing/design | 3-6px | 1.0-1.5s | Enabled | Disabled | Maximum precision |
| Learning/training | 8-12px | 0.8-1.2s | Enabled | Disabled | Visual feedback helpful |

Remember: These are starting points. Everyone's needs are different, so experiment to find what works best for you.

## UI Behavior Settings

### Auto Collapse UI
**What it does**: Automatically shrinks the Dwellpy toolbar to a single button when your cursor moves away from it.

**How it works**: 
- When enabled, the toolbar contracts to a small button showing current status after 1 second
- The contracted button shows current mode (e.g., "LEFT", "OFF", "DRAG*" for temporary mode)
- Hover over the contracted button to expand back to full toolbar
- Auto-expands when cursor returns to the area

**When to enable**:
- Reduce screen clutter during regular computer use
- Maximize available screen real estate
- Minimize visual distractions while keeping Dwellpy accessible

**When to disable**:
- Prefer having all controls always visible
- Frequently switch between click modes
- Using touch screen or other direct input methods

**Default setting**: Disabled

### Expansion Direction
**What it controls**: Which direction the UI expands when auto-collapse is enabled.

**Options**:
- **Auto (Default)**: Automatically chooses the best direction based on screen position and available space
- **Horizontal**: Always expands left-to-right (traditional toolbar layout)
- **Vertical**: Always expands top-to-bottom (column layout)

**Auto mode logic**:
- Analyzes available screen space in all directions
- Prefers horizontal expansion when space permits
- Falls back to vertical if horizontal space is limited
- Considers screen edges and multi-monitor setups

**When to use specific directions**:
- **Horizontal**: Wide screens, traditional desktop layouts
- **Vertical**: Narrow screens, side-mounted positioning, ultrawide monitors
- **Auto**: Most users - let Dwellpy choose the optimal layout

**Note**: This setting only applies when "Contract UI when cursor is outside" is enabled.