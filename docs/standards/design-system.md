# Design System Standards - Margin, Border, Padding

## Overview
This document defines the standardized spacing, border, and padding rules for the Bhanjyang Cooperative project to ensure visual consistency across all pages.

## 1. Section Padding

### Vertical Padding (py-*)
- **Hero Sections**: `py-16 sm:py-20 lg:py-24` (64px → 80px → 96px)
- **Regular Sections**: `py-16` (64px) or `py-20` (80px)
- **Small Sections**: `py-12` (48px) or `py-8` (32px)

### Horizontal Padding (px-*)
- **Section Level**: `px-4 sm:px-6 lg:px-8` (16px → 24px → 32px)
- **Container Level**: `px-4 sm:px-6 lg:px-8` (16px → 24px → 32px)

## 2. Card Padding

### Standard Cards
- **Padding**: `p-6` (24px all sides)
- **Border Radius**: `rounded-lg` (8px)
- **Shadow**: `shadow-md` or `shadow-lg`

### Featured Cards
- **Padding**: `p-8` (32px all sides)
- **Border Radius**: `rounded-2xl` (16px)
- **Shadow**: `shadow-lg` or `shadow-xl`

### Small Cards
- **Padding**: `p-4` (16px all sides)
- **Border Radius**: `rounded-lg` (8px)
- **Shadow**: `shadow-sm` or `shadow-md`

## 3. Border Styles

### Accent Borders (Top Border)
- **Style**: `border-t-4` (4px top border)
- **Colors**: 
  - `border-deuraligreen` (primary accent)
  - `border-bhanjyangred` (secondary accent)

### Standard Borders
- **Style**: `border` (1px all sides)
- **Color**: `border-gray-200` or `border-gray-300`

### Emphasis Borders
- **Style**: `border-2` (2px all sides)
- **Color**: Context-specific (e.g., `border-white` for CTAs)

## 4. Border Radius

### Standard Elements
- **Cards**: `rounded-lg` (8px)
- **Buttons**: `rounded-lg` (8px) or `rounded-full` (pill shape)
- **Inputs**: `rounded-lg` (8px)

### Featured Elements
- **Large Cards**: `rounded-2xl` (16px)
- **Hero CTAs**: `rounded-2xl` (16px) or `rounded-3xl` (24px)
- **Special Cards**: `rounded-3xl` (24px)

### Circular Elements
- **Icons**: `rounded-full` (9999px)
- **Avatars**: `rounded-full` (9999px)

## 5. Margin Spacing

### Vertical Margins (mb-*, mt-*)
- **Tight**: `mb-2` or `mt-2` (8px)
- **Small**: `mb-4` or `mt-4` (16px)
- **Medium**: `mb-6` or `mt-6` (24px)
- **Large**: `mb-8` or `mt-8` (32px)
- **Extra Large**: `mb-12` or `mt-12` (48px)
- **Section Spacing**: `mb-16` or `mt-16` (64px)

### Horizontal Margins (mx-*, ml-*, mr-*)
- **Auto Center**: `mx-auto`
- **Small**: `mx-2` or `ml-2` (8px)
- **Medium**: `mx-4` or `ml-4` (16px)

## 6. Button Padding

### Primary Buttons
- **Padding**: `py-3 px-8` (12px vertical, 32px horizontal)
- **Border Radius**: `rounded-full` or `rounded-lg`
- **Font**: `font-bold` or `font-semibold`

### Secondary Buttons
- **Padding**: `py-2 px-4` (8px vertical, 16px horizontal)
- **Border Radius**: `rounded-lg`
- **Font**: `font-semibold` or `font-medium`

### Small Buttons
- **Padding**: `py-1.5 px-3` (6px vertical, 12px horizontal)
- **Border Radius**: `rounded-md` or `rounded-lg`
- **Font**: `font-medium`

## 7. Input/Form Padding

### Standard Inputs
- **Padding**: `px-4 py-3` (16px horizontal, 12px vertical)
- **Border**: `border border-gray-300`
- **Border Radius**: `rounded-lg` (8px)
- **Focus**: `focus:ring-2 focus:ring-deuraligreen`

### Textarea
- **Padding**: `px-4 py-3` (same as inputs)
- **Border**: `border border-gray-300`
- **Border Radius**: `rounded-lg` (8px)

## 8. Gap Spacing (Grid/Flex)

### Grid Gaps
- **Small**: `gap-4` (16px)
- **Medium**: `gap-6` (24px)
- **Large**: `gap-8` (32px)
- **Extra Large**: `gap-12` (48px)

### Flex Gaps
- **Tight**: `gap-2` (8px)
- **Small**: `gap-4` (16px)
- **Medium**: `gap-6` (24px)

## 9. Shadow Standards

### Card Shadows
- **Standard**: `shadow-md` or `shadow-lg`
- **Hover**: `hover:shadow-lg` or `hover:shadow-xl`
- **Featured**: `shadow-xl` or `shadow-2xl`

## 10. Responsive Breakpoints

- **Mobile**: `< 640px` (default, no prefix)
- **Tablet**: `sm:` (≥ 640px)
- **Desktop**: `md:` (≥ 768px)
- **Large Desktop**: `lg:` (≥ 1024px)
- **XL Desktop**: `xl:` (≥ 1280px)

## Implementation Checklist

- [x] Section horizontal padding: `px-4 sm:px-6 lg:px-8`
- [ ] Section vertical padding: Standardize to `py-16` or `py-20`
- [ ] Card padding: Standardize to `p-6` (standard) or `p-8` (featured)
- [ ] Border radius: Standardize to `rounded-lg` (standard) or `rounded-2xl` (featured)
- [ ] Border styles: Standardize accent borders to `border-t-4`
- [ ] Margin spacing: Use consistent scale (mb-4, mb-6, mb-8, mb-12, mb-16)
- [ ] Button padding: Standardize to `py-3 px-8` (primary) or `py-2 px-4` (secondary)
- [ ] Input padding: Standardize to `px-4 py-3`
- [ ] Gap spacing: Use consistent scale (gap-4, gap-6, gap-8)

## Notes

- Always use responsive padding for sections and containers
- Maintain visual hierarchy with consistent spacing scale
- Use accent borders (`border-t-4`) for card differentiation
- Follow the 8px base unit for spacing (4px, 8px, 16px, 24px, 32px, 48px, 64px)

