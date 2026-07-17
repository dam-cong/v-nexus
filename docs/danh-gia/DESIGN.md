---
name: V-Nexus Tutor Design System
colors:
  surface: '#fbf8ff'
  surface-dim: '#d4d7ff'
  surface-bright: '#fbf8ff'
  surface-container-lowest: '#ffffff'
  surface-container-low: '#f4f2ff'
  surface-container: '#edecff'
  surface-container-high: '#e6e6ff'
  surface-container-highest: '#dee0ff'
  on-surface: '#0a144e'
  on-surface-variant: '#474553'
  inverse-surface: '#222b64'
  inverse-on-surface: '#f0efff'
  outline: '#787584'
  outline-variant: '#c8c4d5'
  surface-tint: '#574ebf'
  primary: '#35299d'
  on-primary: '#ffffff'
  primary-container: '#4d44b5'
  on-primary-container: '#c8c4ff'
  inverse-primary: '#c5c0ff'
  secondary: '#a43c20'
  on-secondary: '#ffffff'
  secondary-container: '#fd7e5c'
  on-secondary-container: '#701800'
  tertiary: '#004822'
  on-tertiary: '#ffffff'
  tertiary-container: '#006231'
  on-tertiary-container: '#53e389'
  error: '#ba1a1a'
  on-error: '#ffffff'
  error-container: '#ffdad6'
  on-error-container: '#93000a'
  primary-fixed: '#e3dfff'
  primary-fixed-dim: '#c5c0ff'
  on-primary-fixed: '#130068'
  on-primary-fixed-variant: '#3e34a6'
  secondary-fixed: '#ffdbd1'
  secondary-fixed-dim: '#ffb5a1'
  on-secondary-fixed: '#3c0800'
  on-secondary-fixed-variant: '#83250a'
  tertiary-fixed: '#6ffda0'
  tertiary-fixed-dim: '#4fe086'
  on-tertiary-fixed: '#00210d'
  on-tertiary-fixed-variant: '#005228'
  background: '#fbf8ff'
  on-background: '#0a144e'
  surface-variant: '#dee0ff'
typography:
  page-title:
    fontFamily: Outfit
    fontSize: 32px
    fontWeight: '700'
    lineHeight: '1.2'
  card-title-lg:
    fontFamily: Outfit
    fontSize: 26px
    fontWeight: '700'
    lineHeight: '1.3'
  card-title-sm:
    fontFamily: Outfit
    fontSize: 22px
    fontWeight: '700'
    lineHeight: '1.3'
  question-display:
    fontFamily: Outfit
    fontSize: 28px
    fontWeight: '700'
    lineHeight: '1.4'
  body:
    fontFamily: Outfit
    fontSize: 16px
    fontWeight: '400'
    lineHeight: '1.5'
  label:
    fontFamily: Outfit
    fontSize: 14px
    fontWeight: '600'
    lineHeight: '1.2'
  caption:
    fontFamily: Outfit
    fontSize: 13px
    fontWeight: '400'
    lineHeight: '1.4'
  page-title-mobile:
    fontFamily: Outfit
    fontSize: 24px
    fontWeight: '700'
    lineHeight: '1.2'
  question-display-mobile:
    fontFamily: Outfit
    fontSize: 22px
    fontWeight: '700'
    lineHeight: '1.4'
rounded:
  sm: 0.25rem
  DEFAULT: 0.5rem
  md: 0.75rem
  lg: 1rem
  xl: 1.5rem
  full: 9999px
spacing:
  base: 8px
  xs: 4px
  sm: 8px
  md: 16px
  lg: 24px
  xl: 32px
  xxl: 48px
  container-margin: 24px
  gutter: 20px
---

## Brand & Style
The design system is crafted for an adaptive learning environment tailored to primary students. The brand personality is **encouraging, vibrant, and structured**, balancing the excitement of discovery with the clarity required for educational focus.

The visual style follows a **Modern EdTech** aesthetic, utilizing a "Soft-Ui" approach. It combines high-quality white space with playful accents to reduce cognitive load while maintaining a friendly atmosphere. Surfaces are clean and layered, using a depth model that feels tangible but digital-native. The interface should evoke a sense of progress and confidence, using soft curves and approachable layouts to make complex learning tasks feel achievable.

## Colors
This design system utilizes a high-contrast palette optimized for readability and emotional engagement. 

- **Primary Purple** is the anchor for navigation and primary actions, representing growth and wisdom.
- **Coral Accent** is reserved for highlights, progress indicators, and "aha!" moments to maintain high energy.
- **Neutral Scales** prioritize a deep navy-blue for text rather than pure black to keep the interface feeling soft and sophisticated.
- **Functional Colors** (Green/Amber/Red) use paired background tints to create clear, accessible feedback loops for student answers and system alerts.

## Typography
The **Outfit** typeface is the sole font family for this design system. Its geometric yet open letterforms ensure maximum legibility for younger readers.

- **Headlines:** Use Bold weights for all titles to create a clear visual hierarchy.
- **Questions:** Content intended for student consumption (the "Question Display" role) should always use increased line height to assist with tracking and comprehension.
- **Responsive Handling:** On mobile devices, page titles and large question text should scale down to prevent excessive wrapping while maintaining bold weight for emphasis.

## Layout & Spacing
This design system uses an **8px base spacing scale**. Layouts should be constructed on a 12-column fluid grid for desktop and a 4-column fluid grid for mobile.

- **Dashboard Layout:** Standardize a left-hand navigation rail (280px) with a fluid main content area.
- **Card Spacing:** Use `lg` (24px) padding inside cards to give educational content room to breathe.
- **Vertical Rhythm:** Maintain consistent `xl` (32px) spacing between distinct sections (e.g., between a progress bar and the question block).

## Elevation & Depth
Depth is conveyed through **Lavender-Gray Ambient Shadows**. These shadows should be soft, diffused, and slightly tinted with the primary purple to maintain color harmony with the background.

- **Level 1 (Cards/Inputs):** `0px 4px 20px rgba(77, 68, 181, 0.05)`
- **Level 2 (Buttons/Active States):** `0px 8px 24px rgba(77, 68, 181, 0.12)`
- **Interaction:** Upon hover, interactive elements should slightly increase their shadow spread to simulate a "lift" toward the user.

## Shapes
The shape language is notably **rounded and friendly**, removing sharp corners to create a safe-feeling environment. 

- **Cards:** Utilize a generous 20px radius to frame content as distinct, approachable units.
- **Inputs:** Use a 12px radius to differentiate functional data-entry areas from larger content containers.
- **Pill Shapes:** Applied to buttons to maximize the "clickability" and distinguish them clearly from other UI elements.

## Components

### Buttons
- **Primary:** Pill-shaped, Primary Purple background, White text. Min-height: 48px.
- **Secondary:** Pill-shaped, Light Purple background, Primary Purple text.
- **State Changes:** Hover states transition to Purple Hover. Active states use a subtle 2px vertical offset.

### Answer Options
- Large, selectable containers with a 16px radius. 
- **Default:** White background, 1px Border (#EDEDF5).
- **Selected:** 2px Primary Purple border with Light Purple background.
- **Correct/Incorrect:** Shift background and border to Success or Error color scales respectively.

### Cards
- White background, 20px radius, and Soft Lavender-Gray shadow.
- Header sections within cards should use a subtle 1px bottom border.

### Input Fields
- 12px radius, 1px Border (#EDEDF5), 16px horizontal padding.
- Focus state: Border changes to Primary Purple with a 4px soft outer glow.

### Chips & Badges
- Used for subject tags or status. Use semi-transparent versions of the primary/secondary colors with 12px font-size Bold.

### Progress Bars
- 12px height, fully rounded tracks. Use Coral Accent for the progress fill to draw attention to completion status.

### Icons
- Use **Line Icons** with a consistent 2px stroke width. Icons should be colored in Primary Purple or Secondary Text depending on their importance.