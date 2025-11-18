# Design Guidelines: Digital Soluctions Chat System

## Design Approach
**Reference-Based:** WhatsApp/Modern Mobile Chat Applications (e.g., WhatsApp Web, Telegram Web, Facebook Messenger)
- Mobile-first chat interface with professional business aesthetics
- Single-purpose: lead capture → AI conversation → redirection
- Premium feel with institutional branding

## Core Design Elements

### Typography
- **Primary Font:** Inter or similar clean sans-serif via Google Fonts
- **Hierarchy:**
  - Header/Brand: text-xl font-bold (20px)
  - Chat Messages: text-sm to text-base (14-16px)
  - User Input: text-base (16px)
  - Timestamps: text-xs text-gray-500 (12px)
  - Button Text: text-sm font-medium (14px)

### Layout System
**Tailwind Spacing Units:** Consistently use 2, 4, 6, 8, 12, 16 units
- Chat container: p-4
- Message bubbles: px-4 py-2, mb-2
- Input area: p-4
- Header: h-16 px-4
- Button spacing: gap-2

### Color Specifications (Per User Requirements)
- **Primary Blue:** #2563eb (bg-blue-600)
- **White:** #FFFFFF (bg-white, text-white)
- **Gray Scale:** 
  - Light backgrounds: bg-gray-50, bg-gray-100
  - Text secondary: text-gray-600, text-gray-500
  - Borders: border-gray-200

## Component Library

### Header Component
- Fixed top position (sticky top-0)
- Height: h-16
- Background: bg-blue-600 with slight shadow
- Logo/Brand: "Digital Soluctions" in white, bold
- Clean, minimalist design

### Chat Container
- Full viewport height on mobile (min-h-screen)
- Two-section layout:
  1. Messages area (flex-1, overflow-y-auto)
  2. Input area (fixed bottom)
- Background: bg-gray-50

### Message Bubbles
**User Messages (right-aligned):**
- Background: bg-blue-600
- Text: text-white
- Rounded: rounded-2xl rounded-br-sm
- Max width: max-w-[80%]
- Self-align: ml-auto

**Assistant Messages (left-aligned):**
- Background: bg-white
- Text: text-gray-800
- Rounded: rounded-2xl rounded-bl-sm
- Max width: max-w-[80%]
- Shadow: shadow-sm

**Shared Properties:**
- Padding: px-4 py-2
- Margin bottom: mb-2
- Smooth transitions: transition-all duration-200

### Input Area
- Fixed bottom position
- Background: bg-white
- Border top: border-t border-gray-200
- Shadow: shadow-lg
- Padding: p-4
- Layout: Flex row with input + send button

**Text Input:**
- Rounded: rounded-full
- Border: border-2 border-gray-200
- Padding: px-4 py-3
- Focus state: focus:border-blue-600 focus:ring-2 focus:ring-blue-100
- Placeholder: text-gray-400

**Send Button:**
- Background: bg-blue-600
- Icon or text: text-white
- Shape: Circular (rounded-full) or rounded-xl
- Size: w-12 h-12 or px-6 py-3
- Position: Fixed right in input container
- Hover: hover:bg-blue-700

### Form Components (Lead Capture)
When collecting name/phone before chat:
- Input fields: Full width inputs with same styling as chat input
- Labels: text-sm font-medium text-gray-700, mb-1
- Spacing between fields: space-y-4
- Submit button: Full width, bg-blue-600, rounded-xl, py-3

### Thank You Page
- Centered layout (flex items-center justify-center min-h-screen)
- Card container: bg-white, rounded-2xl, shadow-xl, p-8
- Success message: Large friendly typography
- CTA button: bg-blue-600, full width or prominent center
- Simple, clean design with whitespace

## Interaction Patterns

### Animations
**Sparingly used:**
- Message appearance: Fade-in from bottom (animate-slide-up)
- Typing indicator: Three animated dots when AI is responding
- Smooth scroll: Auto-scroll to latest message with smooth behavior
- Button feedback: Scale on click (active:scale-95)

### Scroll Behavior
- Auto-scroll to bottom on new message
- Smooth scrolling enabled
- Scroll padding at bottom for better UX

### Responsive Breakpoints
**Mobile (default, <768px):**
- Chat fills entire viewport
- Input always visible at bottom
- Messages width: max-w-[85%]

**Tablet/Desktop (≥768px):**
- Optional: Center chat in container with max-w-2xl
- Or maintain full-width for immersive experience
- Messages width: max-w-[70%]

## Visual Hierarchy
1. **Chat messages** are the primary focus (largest visual weight)
2. **Input area** secondary (always accessible, contrasting background)
3. **Header** tertiary (minimal but branded)
4. **Timestamps/metadata** minimal visual weight (small, gray)

## Images
No hero images required. This is a functional chat application.

**Logo/Branding:** Small "Digital Soluctions" logo or text in header (left-aligned, white on blue)

**Optional Icons:** 
- Send icon (paper plane or arrow)
- Typing indicator animation
- Success checkmark on thank you page

All icons from Font Awesome or Heroicons via CDN.

## Accessibility
- Input fields: Proper labels with for/id association
- Focus states: Clear blue ring on all interactive elements
- Color contrast: Ensure WCAG AA compliance (white on #2563eb passes)
- Keyboard navigation: Tab through input → send button
- Screen reader: ARIA labels on icon buttons

## Key Principles
1. **Mobile-First:** Design for phone screens, enhance for desktop
2. **Conversational Flow:** Natural chat progression with clear visual feedback
3. **Premium Polish:** Smooth animations, perfect spacing, professional color usage
4. **Minimal Distraction:** Focus on conversation, not decorative elements
5. **Speed & Clarity:** Fast load, instant feedback, clear CTAs