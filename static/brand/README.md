# Assertly Brand Assets

## 📁 Brand Package Contents

### Logo Files
- `logo.svg` - Full logo with text (200x200px)
- `logo-icon.svg` - Icon only (64x64px)
- `logo-dark.svg` - Dark theme version
- `logo.png` - Raster version (512x512px)
- `logo-icon.png` - Icon raster (64x64px)

### Color Palettes
- `brand-colors.css` - CSS custom properties
- `colors-light.css` - Light theme colors
- `colors-dark.css` - Dark theme colors
- `colors-print.css` - Print-optimized colors

### Typography
- `fonts.css` - Web font definitions
- `typography.css` - Text styles and hierarchy
- `Inter-Regular.woff2` - Primary font
- `JetBrainsMono-Regular.woff2` - Monospace font

### Guidelines
- `brand-guidelines.md` - Complete brand guidelines
- `usage-examples.html` - Usage examples
- `color-palette.html` - Color palette showcase

## 🎨 Quick Usage

### HTML
```html
<!-- Full Logo -->
<img src="/static/brand/logo.svg" alt="Assertly" width="200" height="200">

<!-- Icon Only -->
<img src="/static/brand/logo-icon.svg" alt="Assertly" width="64" height="64">

<!-- Dark Theme -->
<img src="/static/brand/logo-dark.svg" alt="Assertly" width="200" height="200">
```

### CSS
```css
/* Import brand colors */
@import url('/static/css/brand-colors.css');

/* Use brand colors */
.my-element {
  color: var(--assertly-blue);
  background: var(--assertly-gradient-primary);
}

/* Use brand classes */
<button class="btn-assertly">Get Started</button>
<div class="card-assertly">Content</div>
```

### JavaScript
```javascript
// Theme-aware logo switching
function updateLogo(theme) {
  const logo = document.getElementById('logo');
  if (theme === 'dark') {
    logo.src = '/static/brand/logo-dark.svg';
  } else {
    logo.src = '/static/brand/logo.svg';
  }
}
```

## 📐 Logo Specifications

### Clear Space
- Minimum clear space: 2x logo height
- Never place text or elements closer than this

### Minimum Sizes
- Digital: 24px height minimum
- Print: 0.5" height minimum
- Favicon: 32x32px

### Usage Rules
- ✅ Use on light backgrounds
- ✅ Maintain aspect ratio
- ✅ Use full color when possible
- ❌ Don't stretch or distort
- ❌ Don't change colors
- ❌ Don't use on busy backgrounds

## 🎨 Color Usage

### Primary Colors
- **Assertly Blue**: `#0ea5e9` - Primary actions, links, highlights
- **Assertly Blue Dark**: `#0284c7` - Hover states, emphasis
- **Assertly Blue Light**: `#38bdf8` - Subtle accents, backgrounds

### Secondary Colors
- **Success Green**: `#22c55e` - Success states, positive actions
- **Warning Orange**: `#f59e0b` - Warnings, attention
- **Error Red**: `#ef4444` - Errors, destructive actions

### Neutral Colors
- **Text Primary**: `#0f172a` - Main text content
- **Text Secondary**: `#475569` - Supporting text
- **Text Muted**: `#94a3b8` - Disabled text, captions

## 📝 Typography

### Primary Font: Inter
- **Weights**: 300, 400, 500, 600, 700, 800
- **Usage**: Headings, body text, UI elements
- **Fallback**: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif

### Monospace Font: JetBrains Mono
- **Weights**: 400, 500
- **Usage**: Code, technical content, data
- **Fallback**: 'Fira Code', 'Monaco', 'Cascadia Code', monospace

## 🚀 Implementation Examples

### React Component
```jsx
import { useState, useEffect } from 'react';

function AssertlyLogo({ theme = 'light', size = 'medium' }) {
  const [logoSrc, setLogoSrc] = useState('/static/brand/logo.svg');
  
  useEffect(() => {
    setLogoSrc(theme === 'dark' ? '/static/brand/logo-dark.svg' : '/static/brand/logo.svg');
  }, [theme]);
  
  const sizes = {
    small: { width: 32, height: 32 },
    medium: { width: 64, height: 64 },
    large: { width: 128, height: 128 }
  };
  
  return (
    <img 
      src={logoSrc} 
      alt="Assertly" 
      {...sizes[size]}
      className="logo-assertly"
    />
  );
}
```

### Vue Component
```vue
<template>
  <img 
    :src="logoSrc" 
    alt="Assertly" 
    :width="size.width"
    :height="size.height"
    class="logo-assertly"
  />
</template>

<script>
export default {
  name: 'AssertlyLogo',
  props: {
    theme: {
      type: String,
      default: 'light'
    },
    size: {
      type: String,
      default: 'medium'
    }
  },
  computed: {
    logoSrc() {
      return this.theme === 'dark' 
        ? '/static/brand/logo-dark.svg' 
        : '/static/brand/logo.svg';
    }
  }
}
</script>
```

### CSS Classes
```css
/* Brand button styles */
.btn-assertly {
  background: var(--assertly-gradient-primary);
  color: white;
  border: none;
  padding: 0.75rem 1.5rem;
  border-radius: 0.5rem;
  font-weight: 600;
  transition: all 0.2s ease;
}

/* Brand card styles */
.card-assertly {
  background: var(--assertly-bg-primary);
  border: 1px solid var(--assertly-border);
  border-radius: 1rem;
  box-shadow: var(--assertly-shadow-sm);
}

/* Brand typography */
.text-assertly {
  font-family: 'Inter', sans-serif;
  color: var(--assertly-text-primary);
}
```

## 📱 Responsive Usage

### Mobile
- Use icon-only logo for small screens
- Minimum size: 24px height
- Ensure touch targets are at least 44px

### Tablet
- Use full logo when space allows
- Minimum size: 32px height
- Consider icon + text layout

### Desktop
- Use full logo with tagline
- Minimum size: 48px height
- Full brand experience

## 🎯 Brand Consistency

### Do's
- ✅ Use official brand colors
- ✅ Maintain proper clear space
- ✅ Use approved fonts
- ✅ Follow accessibility guidelines
- ✅ Test across devices and themes

### Don'ts
- ❌ Don't modify logo colors
- ❌ Don't stretch or distort logos
- ❌ Don't use unapproved fonts
- ❌ Don't ignore accessibility
- ❌ Don't use outdated assets

## 📞 Support

### Brand Questions
- Email: brand@assertly.com
- Slack: #brand-questions
- Documentation: [Brand Guidelines](https://docs.assertly.com/brand)

### Asset Requests
- New formats: brand@assertly.com
- Custom sizes: brand@assertly.com
- Special usage: legal@assertly.com

### Updates
- Subscribe to brand updates
- Follow brand changes
- Get notified of new assets

---

**Last Updated**: September 2024  
**Version**: 1.0.0  
**Maintained by**: Assertly Brand Team