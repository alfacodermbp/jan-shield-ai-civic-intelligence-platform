---
name: Civic Intelligence System
colors:
  surface: '#fcf8fa'
  surface-dim: '#dcd9db'
  surface-bright: '#fcf8fa'
  surface-container-lowest: '#ffffff'
  surface-container-low: '#f6f3f5'
  surface-container: '#f0edef'
  surface-container-high: '#eae7e9'
  surface-container-highest: '#e4e2e4'
  on-surface: '#1b1b1d'
  on-surface-variant: '#45464d'
  inverse-surface: '#303032'
  inverse-on-surface: '#f3f0f2'
  outline: '#76777d'
  outline-variant: '#c6c6cd'
  surface-tint: '#565e74'
  primary: '#000000'
  on-primary: '#ffffff'
  primary-container: '#131b2e'
  on-primary-container: '#7c839b'
  inverse-primary: '#bec6e0'
  secondary: '#0051d5'
  on-secondary: '#ffffff'
  secondary-container: '#316bf3'
  on-secondary-container: '#fefcff'
  tertiary: '#000000'
  on-tertiary: '#ffffff'
  tertiary-container: '#271901'
  on-tertiary-container: '#98805d'
  error: '#ba1a1a'
  on-error: '#ffffff'
  error-container: '#ffdad6'
  on-error-container: '#93000a'
  primary-fixed: '#dae2fd'
  primary-fixed-dim: '#bec6e0'
  on-primary-fixed: '#131b2e'
  on-primary-fixed-variant: '#3f465c'
  secondary-fixed: '#dbe1ff'
  secondary-fixed-dim: '#b4c5ff'
  on-secondary-fixed: '#00174b'
  on-secondary-fixed-variant: '#003ea8'
  tertiary-fixed: '#fcdeb5'
  tertiary-fixed-dim: '#dec29a'
  on-tertiary-fixed: '#271901'
  on-tertiary-fixed-variant: '#574425'
  background: '#fcf8fa'
  on-background: '#1b1b1d'
  surface-variant: '#e4e2e4'
typography:
  headline-h1:
    fontFamily: Inter
    fontSize: 40px
    fontWeight: '700'
    lineHeight: 48px
    letterSpacing: -0.02em
  headline-h1-mobile:
    fontFamily: Inter
    fontSize: 30px
    fontWeight: '700'
    lineHeight: 36px
    letterSpacing: -0.02em
  headline-h2:
    fontFamily: Inter
    fontSize: 30px
    fontWeight: '600'
    lineHeight: 38px
    letterSpacing: -0.01em
  headline-h3:
    fontFamily: Inter
    fontSize: 24px
    fontWeight: '600'
    lineHeight: 32px
    letterSpacing: -0.01em
  headline-h4:
    fontFamily: Inter
    fontSize: 20px
    fontWeight: '600'
    lineHeight: 28px
    letterSpacing: 0em
  body-lg:
    fontFamily: Inter
    fontSize: 18px
    fontWeight: '400'
    lineHeight: 28px
  body-md:
    fontFamily: Inter
    fontSize: 16px
    fontWeight: '400'
    lineHeight: 24px
  body-sm:
    fontFamily: Inter
    fontSize: 14px
    fontWeight: '400'
    lineHeight: 20px
  label-caps:
    fontFamily: Inter
    fontSize: 12px
    fontWeight: '600'
    lineHeight: 16px
    letterSpacing: 0.05em
  button-text:
    fontFamily: Inter
    fontSize: 14px
    fontWeight: '500'
    lineHeight: 20px
rounded:
  sm: 0.125rem
  DEFAULT: 0.25rem
  md: 0.375rem
  lg: 0.5rem
  xl: 0.75rem
  full: 9999px
spacing:
  unit: 4px
  xs: 4px
  sm: 8px
  md: 16px
  lg: 24px
  xl: 48px
  gutter: 24px
  margin-mobile: 16px
  margin-desktop: 40px
  container-max: 1440px
---

## Brand & Style
The design system is engineered for high-stakes civic technology, emphasizing authority, clarity, and unwavering reliability. The brand personality is **Institutional yet Innovative**, bridging the gap between traditional government stability and cutting-edge AI capabilities.

The visual style follows a **Modern Corporate** direction. It prioritizes information density without sacrificing legibility. The aesthetic is characterized by high-fidelity finishes: subtle borders, generous white space, and a systematic approach to depth. Every element is designed to feel intentional and "stable," evoking a sense of national-level security and data integrity.

## Colors
The palette is rooted in a **Deep Navy** primary to establish immediate authority and trust. **Slate Blue** serves as the functional action color, guiding users toward primary interactions.

The neutral system uses a "Cool Gray" scale to maintain a crisp, sterile environment suitable for data analysis. Semantic colors follow international standards for accessibility:
- **Critical Red**: Reserved for system failures, security breaches, or destructive actions.
- **Warning Orange**: Used for pending reviews or non-blocking alerts.
- **Success Green**: Indicates system health and completed verifications.
- **Info Blue**: Used for AI-generated insights and general data tooltips.

## Typography
**Inter** is utilized across all levels to ensure maximum legibility and a systematic, utilitarian feel. 

- **Headlines**: Use tighter letter spacing and heavier weights to anchor the page.
- **Body Text**: Optimized for long-form report reading with a standard 1.5x line height.
- **Labels**: Small-scale labels should use the `label-caps` style with increased letter spacing to distinguish metadata from content.
- **Hierarchy**: Always prioritize vertical rhythm; ensure a clear distinction between administrative headers and content sub-sections.

## Layout & Spacing
The design system employs a **12-column fluid grid** for desktop and a **4-column grid** for mobile. 

- **Structure**: Content is housed within a maximum width container of 1440px to prevent excessive line lengths on ultra-wide monitors.
- **Rhythm**: All spacing is derived from a 4px base unit. 
- **Data Density**: For data-intensive views (tables/dashboards), use `md` (16px) padding. For marketing or landing pages, elevate to `lg` (24px) or `xl` (48px) to increase "premium" feel through white space.

## Elevation & Depth
Depth is conveyed through a **Layered Surface** approach combined with refined, low-opacity shadows.

- **Level 0 (Background)**: `#F8FAFC` — The canvas for all content.
- **Level 1 (Cards/Surface)**: `#FFFFFF` — Use for primary content blocks. Includes a `1px` border of `#E2E8F0` and a subtle shadow (0px 1px 3px rgba(15, 23, 42, 0.08)).
- **Level 2 (Dropdowns/Modals)**: Raised surfaces with a more pronounced, diffused shadow (0px 10px 15px -3px rgba(15, 23, 42, 0.12)).
- **Interactions**: On hover, interactive cards should shift from a 1px border to a 1.5px border of the Primary Blue, without changing the elevation height.

## Shapes
The shape language is **Soft** and disciplined. 

- **Standard (0.25rem)**: Used for buttons, input fields, and checkboxes. This maintains a sharp, professional look that feels modern but not overly "consumer-grade."
- **Large (0.5rem)**: Used for content cards and containers.
- **Extra Large (0.75rem)**: Reserved for large-scale modals or main dashboard layout sections.

## Components

### Buttons
- **Primary**: Solid Deep Navy background, white text. No gradient.
- **Secondary**: Slate Blue outline (1px), Slate Blue text.
- **Ghost**: No background/border, Slate Blue text. Used for low-priority actions.

### Badges / Chips
- Use a light tint of the semantic color as the background (e.g., Success Green at 10% opacity) with the full-saturation color for the text. 
- Border-radius should be "rounded-lg" (0.5rem) to differentiate them from square buttons.

### Cards
- Always use a white background with a light gray border (`#E2E8F0`). 
- Titles within cards should use `headline-h4`.

### Input Fields
- **State**: Default border `#CBD5E1`. 
- **Focus**: 2px Slate Blue border with a 4px light blue outer glow (halo).
- **Label**: Always positioned above the input using `body-sm` weight 600.

### Data Tables
- Use a "Zebra Stripe" pattern with `#F8FAFC` on even rows.
- Header row must be sticky with a 2px bottom border of Deep Navy.
- Text in cells should utilize `body-sm`.