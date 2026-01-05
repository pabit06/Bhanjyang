# Keyboard Navigation Guide
# (किबोर्ड नेभिगेसन गाइड)

**Project:** Bhanjyang Cooperative Website  
**Version:** 1.0  
**Last Updated:** 2025-01-05

---

## 📖 Overview

This guide explains the keyboard navigation features planned for the Bhanjyang Cooperative website. Keyboard navigation allows users to interact with the website using only their keyboard, which is essential for:

- **Accessibility** - Users with motor disabilities or visual impairments
- **Efficiency** - Power users who prefer keyboard over mouse
- **WCAG Compliance** - Meeting web accessibility standards

---

## 🎯 Goals

1. **Full Keyboard Accessibility** - All interactive elements accessible via keyboard
2. **Intuitive Navigation** - Natural keyboard patterns (Arrow keys, Tab, Enter, Escape)
3. **Keyboard Shortcuts** - Quick actions for common tasks
4. **Focus Management** - Clear visual indicators of focused elements
5. **Screen Reader Support** - Compatible with assistive technologies

---

## ⌨️ Keyboard Navigation Patterns

### Basic Navigation

#### Tab Navigation
- **Tab** - Move forward through interactive elements
- **Shift+Tab** - Move backward through interactive elements
- **Tab Order** - Logical order following visual layout

#### Arrow Key Navigation
- **↑ / ↓** - Navigate through vertical lists (articles, events, etc.)
- **← / →** - Navigate through horizontal lists (categories, filters, etc.)
- **Home** - Jump to first item
- **End** - Jump to last item

#### Enter Key
- **Enter** - Activate focused element (links, buttons, cards)
- **Enter** - Submit forms
- **Enter** - Open dropdowns/menus

#### Escape Key
- **Esc** - Close modals/dialogs
- **Esc** - Close dropdowns/menus
- **Esc** - Clear search input
- **Esc** - Cancel form editing

---

## 🚀 Keyboard Shortcuts

### Global Shortcuts

| Shortcut | Action | Description |
|----------|--------|-------------|
| `?` | Show Help | Display keyboard shortcuts help modal |
| `/` | Focus Search | Focus the search input field |
| `Esc` | Close | Close modals, dropdowns, or clear input |
| `Home` | Top | Scroll to top of page |
| `End` | Bottom | Scroll to bottom of page |
| `Ctrl+K` / `Cmd+K` | Quick Search | Open quick search (if implemented) |

### Navigation Shortcuts (Vim-style)

| Shortcut | Action | Description |
|----------|--------|-------------|
| `g` then `h` | Go Home | Navigate to home page |
| `g` then `n` | Go News | Navigate to news page |
| `g` then `e` | Go Events | Navigate to events page |
| `g` then `s` | Go Services | Navigate to services page |
| `g` then `a` | Go About | Navigate to about page |
| `g` then `c` | Go Contact | Navigate to contact page |

### Content Navigation

| Shortcut | Action | Description |
|----------|--------|-------------|
| `j` / `↓` | Next Item | Navigate to next article/event/item |
| `k` / `↑` | Previous Item | Navigate to previous article/event/item |
| `o` / `Enter` | Open | Open focused article/event/item |
| `s` | Share | Share current article/event |
| `c` | Comment | Focus comment form (if available) |

### Form Navigation

| Shortcut | Action | Description |
|----------|--------|-------------|
| `Tab` | Next Field | Move to next form field |
| `Shift+Tab` | Previous Field | Move to previous form field |
| `Enter` | Submit | Submit form (if valid) |
| `Esc` | Cancel | Clear/reset form |

---

## 🎨 Focus Indicators

### Visual Focus
- **Focus Ring** - 2px solid outline around focused elements
- **Focus Color** - `#16a34a` (deuraligreen) for consistency
- **Focus Offset** - 2px gap between element and focus ring
- **Smooth Transitions** - Animated focus changes

### Focus States
- **Visible** - Always visible when element is focused
- **High Contrast** - Meets WCAG contrast requirements
- **Consistent** - Same style across all pages

---

## 📱 App-Specific Navigation

### News Events App

#### Article List Page
- **Arrow Keys** - Navigate through article cards
- **Enter** - Open focused article
- **Tab** - Navigate through filters and pagination
- **Esc** - Clear search/filters

#### Article Detail Page
- **← / →** - Navigate to previous/next article
- **Tab** - Navigate through content sections
- **Enter** - Submit comment
- **Esc** - Close share modal

#### Event List Page
- **Arrow Keys** - Navigate through event cards
- **Enter** - Open focused event
- **Tab** - Navigate through filters
- **Esc** - Clear filters

#### Search Page
- **/** - Focus search input (when page loads)
- **Arrow Keys** - Navigate through search results
- **Enter** - Submit search or open result
- **Esc** - Clear search

### Gallery App

#### Image Grid
- **Arrow Keys** - Navigate through images
- **Enter** - Open image in lightbox
- **Tab** - Navigate through filters
- **Esc** - Close lightbox

### Services App

#### Service Cards
- **Arrow Keys** - Navigate through service cards
- **Enter** - Open service details
- **Tab** - Navigate through categories

### Contact App

#### Contact Form
- **Tab** - Navigate through form fields
- **Enter** - Submit form
- **Esc** - Clear form

---

## 🔧 Implementation Details

### Core Infrastructure

#### File Structure
```
apps/
  core/
    static/
      core/
        js/
          keyboard_navigation.js      # Core navigation system
          keyboard_shortcuts.js       # Shortcut handlers
          focus_management.js         # Focus utilities
        css/
          keyboard_navigation.css     # Focus styles
```

#### Key Features
- **Event Delegation** - Efficient event handling
- **Configurable** - Easy to customize per app
- **Accessible** - ARIA attributes and screen reader support
- **Cross-browser** - Works in all modern browsers

### Integration

#### Base Template
```html
<!-- In base.html -->
<script src="{% static 'core/js/keyboard_navigation.js' %}"></script>
<link rel="stylesheet" href="{% static 'core/css/keyboard_navigation.css' %}">
```

#### App-Specific
```html
<!-- In app templates -->
<script src="{% static 'news_events/js/keyboard_navigation.js' %}"></script>
```

---

## ♿ Accessibility Features

### ARIA Attributes
- `aria-label` - Descriptive labels for screen readers
- `aria-describedby` - Additional descriptions
- `aria-expanded` - Dropdown/menu state
- `aria-hidden` - Hide decorative elements
- `role` - Semantic roles for elements

### Screen Reader Support
- **Announcements** - Live regions for dynamic content
- **Landmarks** - Proper page structure
- **Labels** - All interactive elements labeled
- **States** - Current state announced

### Keyboard-Only Users
- **No Mouse Required** - All features accessible via keyboard
- **Logical Tab Order** - Natural reading order
- **Skip Links** - Jump to main content
- **Focus Traps** - Contain focus within modals

---

## 🧪 Testing

### Manual Testing
1. **Tab Navigation** - Test all interactive elements
2. **Arrow Keys** - Test list/grid navigation
3. **Enter Key** - Test activation of elements
4. **Escape Key** - Test closing modals/dropdowns
5. **Shortcuts** - Test all keyboard shortcuts
6. **Focus Indicators** - Verify visible focus

### Automated Testing
- **Unit Tests** - Test keyboard event handlers
- **Integration Tests** - Test full navigation flows
- **Accessibility Tests** - WCAG compliance checks

### Browser Testing
- **Chrome** - Latest version
- **Firefox** - Latest version
- **Safari** - Latest version
- **Edge** - Latest version

### Screen Reader Testing
- **NVDA** - Windows screen reader
- **JAWS** - Windows screen reader
- **VoiceOver** - macOS/iOS screen reader

---

## 📚 Resources

### Documentation
- [WCAG 2.1 Guidelines](https://www.w3.org/WAI/WCAG21/quickref/)
- [ARIA Authoring Practices](https://www.w3.org/WAI/ARIA/apg/)
- [Keyboard Navigation Best Practices](https://webaim.org/techniques/keyboard/)

### Tools
- [WAVE](https://wave.webaim.org/) - Web accessibility evaluation
- [axe DevTools](https://www.deque.com/axe/devtools/) - Accessibility testing
- [Lighthouse](https://developers.google.com/web/tools/lighthouse) - Accessibility audit

---

## 🐛 Known Issues

*None yet - Implementation in progress*

---

## 📝 Changelog

### Version 1.0 (2025-01-05)
- Initial documentation
- Planned features and shortcuts
- Implementation roadmap

---

## 💡 Tips for Users

### Getting Started
1. **Press `?`** - See all available keyboard shortcuts
2. **Use Tab** - Navigate through interactive elements
3. **Use Arrow Keys** - Navigate through lists and grids
4. **Use Enter** - Activate focused elements
5. **Use Escape** - Close modals or clear inputs

### Best Practices
- **Learn Shortcuts** - Start with global shortcuts (`?`, `/`, `Esc`)
- **Use Tab Order** - Follow the natural tab order
- **Watch Focus** - Look for the green focus ring
- **Practice** - Try keyboard-only navigation regularly

---

## 🤝 Contributing

If you find issues or have suggestions for keyboard navigation:

1. **Report Issues** - Create an issue with details
2. **Suggest Improvements** - Share your ideas
3. **Test Features** - Help test new features
4. **Document** - Help improve documentation

---

**Status:** Planning Phase  
**Next Update:** After Phase 1 implementation

