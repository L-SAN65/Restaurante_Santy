---
name: Haute Management
colors:
  surface: '#fbf9f4'
  surface-dim: '#dbdad5'
  surface-bright: '#fbf9f4'
  surface-container-lowest: '#ffffff'
  surface-container-low: '#f5f3ee'
  surface-container: '#f0eee9'
  surface-container-high: '#eae8e3'
  surface-container-highest: '#e4e2dd'
  on-surface: '#1b1c19'
  on-surface-variant: '#46474a'
  inverse-surface: '#30312e'
  inverse-on-surface: '#f2f1ec'
  outline: '#76777b'
  outline-variant: '#c7c6ca'
  surface-tint: '#5f5e5f'
  primary: '#000000'
  on-primary: '#ffffff'
  primary-container: '#1b1b1c'
  on-primary-container: '#858384'
  inverse-primary: '#c8c6c7'
  secondary: '#735c00'
  on-secondary: '#ffffff'
  secondary-container: '#fed65b'
  on-secondary-container: '#745c00'
  tertiary: '#000000'
  on-tertiary: '#ffffff'
  tertiary-container: '#1c1b19'
  on-tertiary-container: '#868380'
  error: '#ba1a1a'
  on-error: '#ffffff'
  error-container: '#ffdad6'
  on-error-container: '#93000a'
  primary-fixed: '#e5e2e3'
  primary-fixed-dim: '#c8c6c7'
  on-primary-fixed: '#1b1b1c'
  on-primary-fixed-variant: '#474647'
  secondary-fixed: '#ffe088'
  secondary-fixed-dim: '#e9c349'
  on-secondary-fixed: '#241a00'
  on-secondary-fixed-variant: '#574500'
  tertiary-fixed: '#e6e2de'
  tertiary-fixed-dim: '#cac6c2'
  on-tertiary-fixed: '#1c1b19'
  on-tertiary-fixed-variant: '#484644'
  background: '#fbf9f4'
  on-background: '#1b1c19'
  surface-variant: '#e4e2dd'
typography:
  display-lg:
    fontFamily: Playfair Display
    fontSize: 48px
    fontWeight: '700'
    lineHeight: '1.2'
    letterSpacing: -0.02em
  headline-lg:
    fontFamily: Playfair Display
    fontSize: 32px
    fontWeight: '600'
    lineHeight: '1.3'
  headline-lg-mobile:
    fontFamily: Playfair Display
    fontSize: 24px
    fontWeight: '600'
    lineHeight: '1.3'
  headline-md:
    fontFamily: Playfair Display
    fontSize: 24px
    fontWeight: '500'
    lineHeight: '1.4'
  body-lg:
    fontFamily: Inter
    fontSize: 18px
    fontWeight: '400'
    lineHeight: '1.6'
  body-md:
    fontFamily: Inter
    fontSize: 16px
    fontWeight: '400'
    lineHeight: '1.5'
  body-sm:
    fontFamily: Inter
    fontSize: 14px
    fontWeight: '400'
    lineHeight: '1.5'
  label-md:
    fontFamily: Inter
    fontSize: 14px
    fontWeight: '600'
    lineHeight: '1'
    letterSpacing: 0.05em
  label-sm:
    fontFamily: Inter
    fontSize: 12px
    fontWeight: '500'
    lineHeight: '1'
rounded:
  sm: 0.25rem
  DEFAULT: 0.5rem
  md: 0.75rem
  lg: 1rem
  xl: 1.5rem
  full: 9999px
spacing:
  unit: 8px
  container-max: 1440px
  gutter: 24px
  margin-desktop: 40px
  margin-mobile: 16px
---

## Brand & Style

The design system is engineered for the high-end hospitality sector, where precision meets prestige. It balances the operational rigor required for kitchen and floor management with the aesthetic refinement of a luxury dining experience.

The design style is **Corporate Modern with a Minimalist touch**. It avoids unnecessary ornamentation, focusing instead on generous whitespace, high-quality typography, and a "Tonal Layering" approach. The interface should feel as organized and deliberate as a Michelin-starred kitchen, evoking a sense of calm authority and effortless efficiency. High-end hospitality users should feel they are using a tool that matches the caliber of their service.

## Colors

The palette is anchored by **Deep Charcoal**, used for primary navigation and text to establish grounding. **Warm Gold** is applied sparingly as a signature accent for primary actions, critical brand moments, and premium status indicators. 

For the UI background, a soft **Cream (#F9F7F2)** reduces eye strain compared to pure white, providing a sophisticated "paper" quality. Semantic colors for success, warning, and error are slightly desaturated to maintain the professional aesthetic while remaining highly legible. Interactive states for Deep Charcoal elements should shift toward a lighter graphite, while Warm Gold elements should utilize a deeper bronze for hover states.

## Typography

This design system uses a dual-font strategy to separate brand storytelling from operational utility. 

**Playfair Display** is reserved for high-level headings, page titles, and luxury touchpoints (e.g., Guest Profiles, Wine Lists). It provides the "editorial" feel of a high-end menu.

**Inter** is the workhorse for all functional UI elements. Its high x-height and neutral character ensure that data-heavy views like Kitchen Display Systems (KDS) and Point of Sale (POS) terminals remain legible under pressure. Labels and table headers should utilize the `label-md` style with slight letter-spacing and uppercase styling to provide clear structural hierarchy in complex tables.

## Layout & Spacing

The layout follows a **Fixed Grid** model for administrative and desktop views to maintain a structured, professional dashboard feel, while transitioning to a fluid model for tablet-based POS interfaces.

The spacing rhythm is based on an **8px base unit**. 
- **Desktop:** 12-column grid, 24px gutters, 40px outer margins.
- **Tablet (Landscape):** 12-column grid, 16px gutters, 24px margins.
- **Mobile:** 4-column grid, 16px gutters, 16px margins.

In data-heavy views like the KDS, spacing can be compressed to a 4px scale to maximize information density without sacrificing the touch targets required for kitchen staff.

## Elevation & Depth

Hierarchy is achieved through **Tonal Layers** and **Ambient Shadows**. Instead of heavy shadows, this design system uses soft, diffused shadows with a slight Deep Charcoal tint to simulate natural light.

1.  **Level 0 (Base):** The Cream background (#F9F7F2).
2.  **Level 1 (Cards/Containers):** Pure White (#FFFFFF) with a 1px border (#E5E1D8). No shadow.
3.  **Level 2 (Modals/Dropdowns):** Pure White with a 12px blur, 15% opacity shadow.
4.  **Level 3 (Urgent Overlays):** Pure White with a 24px blur, 20% opacity shadow.

Interactive elements like buttons use a subtle 2px "lift" shadow on hover to provide tactile feedback.

## Shapes

The shape language is **Rounded**, striking a balance between the friendliness of hospitality and the sharpness of professional software. 

- **Standard Buttons & Inputs:** 0.5rem (8px) corner radius.
- **Large Cards & Containers:** 1rem (16px) corner radius.
- **Chips & Badges:** Full-pill shape for status indicators to contrast against rectangular data cells.

Borders should be kept thin (1px) and use a light neutral tone to maintain a clean, high-end appearance.

## Components

### Buttons
- **Primary:** Deep Charcoal background, White text. High contrast, authoritative.
- **Secondary (Action):** Warm Gold background, Deep Charcoal text. Reserved for the "Primary CTA" on a page (e.g., "Complete Order").
- **Ghost:** Transparent background with 1px Deep Charcoal border. Used for secondary actions.

### Input Fields
Inputs use a white background with a 1px border (#E5E1D8). On focus, the border transitions to Deep Charcoal. Labels always sit above the field in `label-sm` style.

### Cards
Cards are the primary container for the UI. They should have a 1px border and no shadow unless they are meant to be "draggable" or "floating" (like a guest check in a POS view).

### Chips & Status
- **Seating Status:** Use the pill-shape with a subtle background tint and dark text of the corresponding semantic color (e.g., Light Green background with Emerald Green text).

### KDS Tickets
Kitchen tickets should use a "stacked" approach with a Deep Charcoal header for the table/order number, a white body for items, and a Warm Gold footer for time-elapsed indicators.

### Tables
Data tables should use "Border-bottom" styling only. Row hover states should use a very subtle cream tint (#F1EFE9) to help eye-tracking in dense guest lists or inventory reports.