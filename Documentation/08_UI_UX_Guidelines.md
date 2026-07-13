# 08_UI_UX_Guidelines.md

# FinanceFlow AI – UI/UX Guidelines

Version: 1.0

---

# Design Philosophy

FinanceFlow AI should feel like a premium B2B SaaS product used daily by finance teams.

Primary inspirations:

- Stripe Dashboard
- Linear
- Vercel
- Notion

Focus on clarity over decoration.

---

# Design Principles

1. Information first.
2. Every status is immediately understandable.
3. Keep visual hierarchy strong.
4. Minimize clicks.
5. Show progress during long-running operations.
6. Use whitespace generously.

---

# Color Palette

| Purpose | Color |
|---|---|
| Primary | Blue 600 |
| Success | Green 600 |
| Warning | Amber 500 |
| Error | Red 600 |
| Info | Sky 500 |
| Background | Slate 50 |
| Card | White |
| Border | Slate 200 |

Dark mode

- Background: Slate 950
- Cards: Slate 900
- Border: Slate 800

---

# Typography

Headings

- Inter
- 700 weight

Body

- Inter
- 400–500

Monospace

- JetBrains Mono

---

# Spacing Scale

4px

8px

12px

16px

24px

32px

48px

64px

Use 8-point grid throughout.

---

# Border Radius

Buttons

8px

Cards

12px

Dialogs

16px

---

# Shadows

Cards

Small elevation only.

Avoid heavy shadows.

---

# Navigation

Sidebar

- Dashboard
- Upload
- History

Top Bar

- Search
- Theme Toggle
- User Menu (future)

---

# Dashboard

Layout

```text
-------------------------------------------------
Metric Cards (4)

Approval Chart | Processing Trend

Recent Invoices Table
-------------------------------------------------
```

Metric cards

- Total
- Approved
- Pending
- Rejected

---

# Upload Experience

Empty State

"Drop your invoice here"

Supported

- PDF

Visual feedback

- Drag hover
- Upload progress
- Success toast
- Failure toast

---

# Processing Timeline

Represent each stage as:

✓ Completed

⏳ Running

○ Pending

Stages

- Upload
- Detection
- Extraction
- Gemini
- Validation
- Decision
- Saved

Animate transitions using Framer Motion.

---

# Status Badges

Approved

Green

Pending

Amber

Rejected

Red

Digital

Blue

Scanned

Purple

---

# Tables

Use:

- Sticky headers
- Zebra hover
- Search
- Pagination
- Sortable columns

Columns

Invoice

Vendor

PO

Status

Type

Date

---

# Invoice Details

Split layout

Left

PDF Viewer

Right

Decision Card

Extracted Fields

Business Rules

Timeline

AI Explanation

---

# Forms

Use React Hook Form.

Validation

Inline messages.

Disable submit during processing.

---

# Empty States

Dashboard

"No invoices processed yet."

History

"No matching invoices."

---

# Error States

Display

- Friendly title
- Technical reason
- Retry button

---

# Loading States

Use skeleton loaders.

Never leave blank screens.

---

# Icons

Lucide Icons

Examples

Upload

File

Clock

Check

Alert Triangle

Search

---

# Charts

Recharts

Charts

- Area Chart
- Pie Chart
- Bar Chart

Avoid 3D charts.

---

# Motion

Maximum animation duration

300ms

Use

- Fade
- Slide
- Scale

Avoid excessive effects.

---

# Accessibility

- WCAG AA contrast
- Keyboard navigation
- Visible focus states
- Semantic HTML
- ARIA labels where needed

---

# Acceptance Criteria

- Consistent spacing
- Responsive layout
- Accessible forms
- Unified color system
- Clear processing states
- Premium SaaS appearance

---

# Antigravity Build Prompt

Implement the UI using these design guidelines.

Requirements:

- Tailwind CSS
- shadcn/ui
- Lucide Icons
- Framer Motion
- Recharts

Prioritize clarity, consistency, responsiveness, and enterprise aesthetics over visual complexity.
