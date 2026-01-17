# Frontend Improvement Plan (frontend सुधार योजना)

This document outlines a strategic plan to modernize, optimize, and maintain the frontend of the Bhanjyang Cooperative application.

## 1. Architecture & Code Organization
### Current State
- Use of Django Templates with `partials`.
- Tailwind CSS for styling.
- Inline JavaScript in templates (e.g., `_header.html`).
- Hardcoded contact information (phone, email) in multiple templates.

### Action Items
- **Externalize JavaScript**: Move inline scripts from `_header.html` (and others) to dedicated files in `static/js/components/`.
  - *Benefit*: Better caching, easier debugging, cleaner HTML.
- **Context Processors for Global Data**: Move hardcoded values (Phone: `9856083101`, Email: `info@bhanjyang.coop.np`) to a Django Context Processor.
  - *Benefit*: Update contact info in one place, reflects globally.
- **Component Library**: Create reusable templates in `templates/components/` for repeated UI elements:
  - `buttons.html`
  - `section_heading.html`
  - `info_card.html`
  - *Benefit*: Consistency in design (padding, fonts, colors) across pages.

## 2. UI/UX Modernization
### Current State
- Clean look with `bhanjyangred` and `deuraligreen` colors.
- Animations using GSAP and CSS transitions.
- Responsive design.

### Action Items
- **Micro-Interactions**: Add subtle hover/focus effects to all interactive elements (buttons, links, inputs) to provide immediate feedback.
- **Skeleton Loaders**: Implement skeleton loading screens for any content loaded asynchronously (if applicable) to reduce perceived load time.
- **Unified Design System**: Ensure strict adherence to `design-system/tokens.css` to avoid "magic values" in Tailwind classes.

## 3. Accessibility (a11y)
### Current State
- Basic semantic HTML.
- `alt` tags on images.

### Action Items
- **ARIA Attributes**: Ensure dropdowns in `_header.html` manage `aria-expanded` and `aria-haspopup` states dynamically via JS.
- **Keyboard Navigation**: Verify that all dropdowns and modals (search, mobile menu) are fully navigational via `Tab` and `Esc` keys.
- **Contrast Check**: Audit text colors against backgrounds (especially custom green/red) to meet WCAG AA standards.

## 4. Performance Optimization
### Current State
- Static files served via Django.
- Tailwind JIT/CLI used.

### Action Items
- **Image Optimization**: Ensure all logos and banners are in modern formats (WebP) or compressed.
- **Lazy Loading**: Verify `loading="lazy"` is on all non-hero images (Header logo has it, checking others).
- **Critical CSS**: Ensure the Tailwind build process effectively purges unused styles.

## 5. Specific File refactoring
### `templates/partials/_header.html`
- **Refactor**: Extract the `<script>` block at the bottom to `static/js/components/header.js`.
- **Logic**: Simplify the mobile menu toggle logic and ensure it traps focus when open (for accessibility).

### `templates/partials/_footer.html`
- **Refactor**: Use the new Context Processor variables for address/phone/email.

## 6. Implementation Timeline (Proposed)
1.  **Week 1**: Setup Context Processors & Refactor Header JS.
2.  **Week 2**: Componentize Buttons and Cards; Audit Colors.
3.  **Week 3**: Performance Tuning (Images, Caching policies).

---
*Note: This plan aligns with the project's goal of a premium, responsive, and user-friendly interface.*
