# Configuration Guide

This guide explains how to adjust Dwellpy's settings for your specific needs.

## Floating Widgets

Dwellpy includes two floating widgets that appear when you pause your cursor:

### Menu Widget (Hamburger Menu)
A small circular hamburger menu (☰) that appears when you dwell (pause cursor) for the configured delay. Expands into a circular menu with all click modes, settings, and power options when hovered.

### Scroll Widget  
A floating scroll helper with up/down arrows that appears alongside the menu widget when you dwell. Allows easy scrolling without precise targeting of scroll bars.

Both widgets use the same appearance delay setting (configurable in the Scroll tab).

## Opening Settings

Click the **SETUP** button on the Dwellpy toolbar to open the settings dialog. The settings are organized into four main tabs for easy navigation:

- **Dwell**: Movement detection and timing settings
- **Visual**: Appearance and click feedback options  
- **Scroll**: Scroll widget configuration
- **General**: Startup and UI behavior settings

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

The Scroll tab contains settings for the floating scroll widget and menu widget appearance.

**Note on Widget Behavior**: The scroll and menu widgets are designed to work together. When the menu widget expands (by hovering over the hamburger icon), the scroll widget will automatically hide to reduce clutter, unless you are actively hovering over the scroll widget itself. It will reappear when the menu widget contracts.

### Scroll Widget
This section controls a floating scroll widget that appears near your cursor for easy scrolling.

#### Enable Scroll Widget
**What it does**: Shows/hides the floating scroll helper that appears when you dwell (pause cursor).

**When to enable**: For reading documents, browsing web pages, or working with long content.

**When to disable**: When using on-screen keyboards or other tools that might conflict.

### Menu Widget
This section controls the appearance and behavior of the hamburger menu widget.

#### Menu Item Size (30-100 pixels)
**What it does**: Controls the size of menu items in the expanded hamburger menu.

**Scale**: 30 = smallest items, 100 = largest items

**Recommended values**:
- **30-50**: Compact menu for smaller screens or when space is limited
- **50-70**: Standard size for most users (default: 50)
- **70-100**: Larger items for better visibility or accessibility needs

**When to adjust**:
- **Increase size**: If menu items are hard to see or click
- **Decrease size**: If the menu takes up too much screen space
- **Default (50)**: Good balance for most users

#### Scroll Speed (1-10)
**What it does**: Controls how fast scrolling happens when you hover over the scroll arrows.

**Scale**: 1 = slowest (200ms between scrolls), 10 = fastest (20ms between scrolls)

**Recommended values**:
- **1-3**: Slow, controlled scrolling for precise reading
- **4-6**: Medium speed for general use
- **7-10**: Fast scrolling for quickly moving through content

#### Widget Appearance Delay (0.1s - 1.0s)
**What it does**: Controls how long the cursor needs to remain still (dwell) before the menu and scroll widgets appear.

**Scale**: 0.1s = widgets appear very quickly, 1.0s = widgets wait longer before appearing

**Recommended values**:
- **0.1s - 0.3s**: Quick appearance for frequent widget use
- **0.4s - 0.6s**: Medium delay for balanced usage (default: 0.2s)
- **0.7s - 1.0s**: Longer delay to avoid widgets appearing during normal cursor movement

**When to adjust**:
- **Increase delay**: If widgets appear too often during normal computer use
- **Decrease delay**: If you want widgets to be more responsive when you stop moving the cursor
- **Default (0.2s)**: Good balance for most users

#### Widget Unlock Threshold (100px - 300px)
**What it does**: Controls the distance (in pixels) your cursor needs to move away from a widget before it "unlocks" and starts following the cursor again.

**Scale**: 100px = unlocks with a small movement, 300px = requires a larger movement to unlock.

**Recommended values**:
- **100px - 150px**: Widgets feel more "attached" to the cursor and follow it readily. Good for users who prefer responsive widgets.
- **150px - 200px**: A balanced setting that prevents accidental movement while still being easy to reposition (default: 150px).
- **200px - 300px**: Widgets are more "sticky" and stay in place until you make a very deliberate movement. Good for users who find the widgets move too often.

**When to adjust**:
- **Increase threshold**: If you find the widgets move too easily when you're trying to interact with them.
- **Decrease threshold**: If the widgets feel sluggish or hard to move.

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
Dwellpy provides different click modes that you can select as needed:

- **Default Mode (Blue button)**: Your primary click type that you return to after temporary mode usage
- **Temporary Mode (Red button)**: Used once, then returns to your default mode

### How to Use Modes
1. **Use temporary mode**: Click any mode button (turns red) - used once then returns to default
2. **Change default mode**: Click the same mode button again (turns blue and becomes your new default)
3. **Toggle scroll widget**: SCROLL button works differently - it simply toggles the scroll widget on/off

### Changing Your Default Mode
You can change which mode serves as your default (the one you return to after temporary usage):

1. Click any mode button (LEFT, DOUBLE, DRAG, RIGHT) twice
2. The button turns blue, indicating it's now your default mode
3. All temporary mode usage will now return to this mode instead of LEFT

**Example**: To make RIGHT click your default:
- Click RIGHT once (turns red, temporary)
- Click RIGHT again (turns blue, now your default)
- Future temporary mode usage returns to RIGHT instead of LEFT

**Note**: SCROLL is not a click mode - it's a toggle for the scroll widget and doesn't affect click mode behavior.

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