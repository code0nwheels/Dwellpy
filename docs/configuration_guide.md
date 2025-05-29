# Configuration Guide

This guide explains how to adjust Dwellpy's settings for your specific needs.

## Opening Settings

Click the **SETUP** button on the Dwellpy toolbar to open the settings dialog. The settings are organized into four main tabs for easy navigation:

- **🎯 Dwell**: Movement detection and timing settings
- **👁️ Visual**: Appearance and click feedback options  
- **📜 Scroll**: Scroll widget configuration
- **⚙️ General**: Startup and UI behavior settings

## Dwell Tab

The Dwell tab contains the core settings that control how dwell clicking works.

### Movement Detection
This section controls how much your cursor can move while still counting as "dwelling" in one spot.

#### Move Limit (3-20 pixels)
**What it does**: Maximum distance your cursor can move while still "dwelling" in one spot.

**How to adjust**: Use the slider or hover over the +/- buttons for quick adjustment.

**Recommended values**:
- **3-8 pixels**: Good cursor control (regular mouse, precise head tracker)
- **8-15 pixels**: Head tracker users, minor tremors
- **12-20 pixels**: Hand tremors, cerebral palsy, less precise control

**Tips**:
- Start with 8-10 pixels and adjust from there
- Too low = hard to dwell (keeps resetting)
- Too high = accidental clicks when moving between targets

### Dwell Timing
This section controls how long you must hold your cursor still before a click happens.

#### Dwell Time (0.1-2.0 seconds)
**What it does**: How long you must hold your cursor in position before a click happens.

**How to adjust**: Use the slider or hover over the +/- buttons for quick adjustment.

**Recommended values**:
- **0.1-0.5 seconds**: Quick response, less fatigue
- **0.5-0.8 seconds**: Balanced (good for most head tracker users)
- **0.8-2.0 seconds**: Prevents accidental clicks, gives time to move away

**Tips**:
- Shorter times = faster but more accidental clicks
- Longer times = slower but more deliberate
- Most users find 0.6-0.8 seconds works well

## Visual Tab

The Visual tab contains settings for how Dwellpy looks and provides visual feedback.

### Window Appearance
This section controls how the Dwellpy toolbar looks and behaves.

#### Window Transparency
**Enable window transparency**: Makes the toolbar see-through when your cursor isn't over it.

**Transparency level**: How see-through the toolbar becomes (10-90%).

**Why use it**: Reduces visual clutter while keeping the toolbar accessible.

**Recommended**: Enable at 70% transparency for most users.

### Click Feedback
This section controls visual indicators to show where and what type of clicks are performed.

#### Visible Clicks
**What it does**: Shows a brief visual animation (expanding circle) at the location where clicks are performed.

**When to enable**: 
- Learning to use Dwellpy effectively
- Confirming clicks are happening where expected
- Troubleshooting click accuracy issues
- Presentations or demonstrations
- Want distinctive visual confirmation that differs from system feedback

**When to disable**: 
- Reduces visual distractions during regular use
- Gaming or video applications where animations might interfere
- Battery optimization on portable devices
- Motion sensitivity or seizure concerns

**Default setting**: Enabled

#### Click Colors
**What it does**: Customize the colors used for visible click feedback animations for each action type.

**Available customizations**:
- **Left Click**: Color for standard left mouse clicks (default: bright green #00e676)
- **Right Click**: Color for context menu/right mouse clicks (default: orange #ff9800)
- **Double Click**: Color for double-click actions (default: pink/magenta #e91e63)
- **Drag Start**: Color shown when drag operation begins (default: purple #9c27b0)
- **Drag End**: Color shown when drag operation completes (default: darker purple #673ab7)
- **Middle Click**: Color for middle mouse button clicks (default: cyan #00bcd4)

**How to customize**:
1. Open settings with the **SETUP** button
2. Go to the **Visual** tab
3. In the "Click Feedback" section, click any color button to open a color picker
4. Choose your preferred color from the picker
5. Colors update immediately and are saved automatically

**Design tips**:
- Use high contrast colors that stand out against your typical background
- Consider accessibility - avoid color combinations that are hard to distinguish
- Different colors for different actions help identify which type of click occurred
- Bright, saturated colors are more visible during quick animations

**Default colors** are designed to be vibrant and distinct from typical system feedback, making it clear when Dwellpy is performing intentional actions rather than accidental system responses.

## Scroll Tab

The Scroll tab contains settings for the floating scroll widget.

### Scroll Widget
This section controls a floating scroll widget that appears near your cursor for easy scrolling.

#### Enable Scroll Widget
**What it does**: Shows/hides the floating scroll helper that follows your cursor.

**When to enable**: For reading documents, browsing web pages, or working with long content.

**When to disable**: When using on-screen keyboards or other tools that might conflict.

#### Scroll Speed (1-10)
**What it does**: Controls how fast scrolling happens when you hover over the scroll arrows.

**Scale**: 1 = slowest (200ms between scrolls), 10 = fastest (20ms between scrolls)

**Recommended values**:
- **1-3**: Slow, controlled scrolling for precise reading
- **4-6**: Medium speed for general use
- **7-10**: Fast scrolling for quickly moving through content

## General Tab

The General tab contains startup and UI behavior settings.

### Startup Behavior
This section controls how Dwellpy should behave when first launched.

#### Start Active on Launch
**What it does**: Automatically turns on dwell clicking when Dwellpy starts.

**When to enable**: If you always want dwell clicking active immediately.

**When to disable**: If you prefer to manually turn it on when needed.

### UI Behavior
This section controls how the toolbar behaves when you're not using it.

#### Auto Collapse UI
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

#### Expansion Direction
**What it controls**: Which direction the UI expands when auto-collapse is enabled.

**Options** (radio button selection):
- **Auto (recommended)**: Automatically chooses the best direction based on screen position and available space
- **Horizontal (left-to-right)**: Always expands left-to-right (traditional toolbar layout)
- **Vertical (top-to-bottom)**: Always expands top-to-bottom (column layout)

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

## Settings Navigation Tips

### Quick Adjustments
- **Hover over +/- buttons** in any tab for quick value adjustments (repeats every 0.5 seconds)
- **Use sliders** for more precise control
- **Color buttons** open color pickers immediately for customization

### Tab Organization
- **Dwell tab**: Start here for basic functionality setup
- **Visual tab**: Customize appearance and feedback
- **Scroll tab**: Configure scrolling helper
- **General tab**: Set startup and advanced UI behavior

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
Click Colors: Muted/darker colors if visible clicks enabled
Auto Collapse: Enabled
Expansion Direction: Horizontal (easier eye movement patterns)
```

**Why**: Eye trackers can be less precise than other input methods. Longer dwell time prevents accidental activation from brief glances. Horizontal layout supports natural left-right eye scanning. If using visible clicks, consider softer colors to reduce visual fatigue.

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
- Customize click colors if default colors clash with your applications or are hard to see
- Use darker/muted colors for extended use to reduce eye strain
- Choose high-contrast colors if you have difficulty seeing the feedback animations

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

| Task | Tab | Move Limit | Dwell Time | Visible Clicks | Click Colors | Auto Collapse | Notes |
|------|-----|------------|------------|----------------|--------------|---------------|-------|
| General use | Dwell/Visual | 8-12px | 0.6-0.8s | Enabled | Default/bright | Enabled | Balanced settings |
| Reading/browsing | All tabs | 10-15px | 0.4-0.6s | Enabled | Default/bright | Enabled | Enable scroll widget |
| Precision work | Dwell/Visual | 5-8px | 0.8-1.0s | Enabled | High-contrast | Disabled | Temporary mode helpful |
| Gaming | Dwell/Visual | 6-10px | 0.3-0.5s | Disabled | N/A | Disabled | Fast response needed |
| Drawing/design | Dwell/Visual | 3-6px | 1.0-1.5s | Enabled | Muted/subtle | Disabled | Maximum precision |
| Learning/training | All tabs | 8-12px | 0.8-1.2s | Enabled | Bright/distinct | Disabled | Visual feedback helpful |

**Settings Location Guide**:
- **Move Limit & Dwell Time**: Dwell tab
- **Visible Clicks & Click Colors**: Visual tab  
- **Auto Collapse & Expansion Direction**: General tab
- **Scroll Widget**: Scroll tab
- **Transparency**: Visual tab

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