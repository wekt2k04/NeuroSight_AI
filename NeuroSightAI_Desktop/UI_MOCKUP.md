# NeuroSight AI - Visual UI Mockup

## Desktop Interface Layout (1200x800)

```
┌──────────────────────────────────────────────────────────────────────────────────────┐
│ ◉ ◉ ◉                                                                                │
├──────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                       │
│  NeuroSight AI                        Intelligent Alzheimer Detection System     v1.0 │
│                                                                                       │
├─────────────────────────────────────┬─────────────────────────────────────────────────┤
│                                     │                                                 │
│   LEFT PANEL                        │  RIGHT PANEL                                   │
│   ═══════════════════════════════════════════════════════════════════════════════════ │
│                                     │                                                 │
│   MRI Image Upload                  │  ┌───────────────────────────────────────────┐ │
│   ─────────────────                 │  │  🚀  Analyze Image                        │ │
│                                     │  └───────────────────────────────────────────┘ │
│   ┏━━━━━━━━━━━━━━━━━━━━━━━┓        │                                                 │
│   ┃                       ┃        │  ████████████████░░░░ 50%                      │
│   ┃  📁 Drag & Drop      ┃        │                                                 │
│   ┃    MRI Image Here    ┃        │  Analysis Results                               │
│   ┃    or Click Browse   ┃        │  ─────────────────                              │
│   ┃                       ┃        │                                                 │
│   ┗━━━━━━━━━━━━━━━━━━━━━━━┛        │  Disease Stage: Mild Demented                  │
│                                     │  ┌───────────────────────────────────────────┐ │
│   ┌─────────────────────────┐      │  │  Mild Demented                              │ │
│   │  Browse Files           │      │  └───────────────────────────────────────────┘ │
│   └─────────────────────────┘      │                                                 │
│                                     │  Confidence: 87.5%                              │
│   File: .../patient_001.jpg         │                                                 │
│                                     │  ┌───────────────────────────────────────────┐ │
│   Image Preview                     │  │     [CLASS ACTIVATION MAP]                │ │
│   ───────────────                   │  │                                             │ │
│                                     │  │      🔴🟠🟡 Heatmap                        │ │
│   ┌──────────────────────┐          │  │      (Red = High activation)                │ │
│   │                      │          │  │      (Blue = Low activation)                │ │
│   │   [MRI Image]        │          │  │                                             │ │
│   │   (Grayscale)        │          │  │                                             │ │
│   │                      │          │  └───────────────────────────────────────────┘ │
│   │                      │          │                                                 │
│   │                      │          │  ✓ Analysis complete. Mild Demented detected   │
│   │                      │          │    with 87.5% confidence.                      │
│   │                      │          │                                                 │
│   └──────────────────────┘          │                                                 │
│                                     │                                                 │
│                                     │                                                 │
│                                     │                                                 │
├─────────────────────────────────────┴─────────────────────────────────────────────────┤
│ ⚕️  Disclaimer: NeuroSight AI is an aid-to-diagnosis tool. Final diagnosis remains   │
│ the responsibility of qualified medical professionals.                                │
└──────────────────────────────────────────────────────────────────────────────────────┘
```

## Detailed Component Views

### 1. Header Section
```
┌─────────────────────────────────────────────────────────────────────┐
│  [DARK BLUE BACKGROUND - #1e3a5f]                                  │
│                                                                     │
│  🧠  NeuroSight AI          Intelligent Alzheimer Detection    v1.0 │
│      (white, 24px bold)     (light blue, 12px)               (grey) │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### 2. Left Panel - Upload Section
```
┌──────────────────────────────┐
│ 📋 MRI Image Upload          │
├──────────────────────────────┤
│                              │
│  ┏━━━━━━━━━━━━━━━━━━━━━━━┓  │
│  ┃ Dashed Border         ┃  │
│  ┃ Blue (#4a9eff)        ┃  │
│  ┃ Light Blue Background ┃  │
│  ┃                       ┃  │
│  ┃  📁 Drag & Drop MRI   ┃  │
│  ┃  Image Here           ┃  │
│  ┃  or Click to Browse   ┃  │
│  ┃                       ┃  │
│  ┗━━━━━━━━━━━━━━━━━━━━━━━┛  │
│                              │
│  ┌──────────────────────────┐ │
│  │ Browse Files   [BUTTON]  │ │
│  └──────────────────────────┘ │
│  (Green background, white text)│
│                              │
│  File: No file selected      │
│  (small gray text)           │
└──────────────────────────────┘
```

### 3. Image Preview Section
```
┌──────────────────────────────┐
│ 🖼️  Image Preview            │
├──────────────────────────────┤
│                              │
│  ┌──────────────────────────┐ │
│  │  [MRI IMAGE]             │ │
│  │                          │ │
│  │  Grayscale Brain Scan    │ │
│  │                          │ │
│  │  Displayed at ~250x250px │ │
│  │                          │ │
│  └──────────────────────────┘ │
│  (Light gray background)     │
│                              │
└──────────────────────────────┘
```

### 4. Right Panel - Analysis Button
```
┌────────────────────────────────────┐
│  ┌────────────────────────────────┐ │
│  │  🚀  Analyze Image             │ │
│  │     (Green #2ecc71)            │ │
│  │     Height: 60px               │ │
│  │     Bold 16px text             │ │
│  │     White text                 │ │
│  └────────────────────────────────┘ │
│     Hover: Darker green            │
│     Disabled: Gray                 │
└────────────────────────────────────┘
```

### 5. Progress Bar
```
┌────────────────────────────────────┐
│  ████████████████░░░░░░░░░░░░ 50%   │
│  (Blue chunk, light background)    │
└────────────────────────────────────┘
```

### 6. Results Display
```
┌────────────────────────────────────┐
│ 📊 Analysis Results                │
├────────────────────────────────────┤
│                                    │
│ Disease Stage: Mild Demented       │
│                                    │
│ ┌──────────────────────────────┐   │
│ │ Mild Demented               │   │
│ │ (Blue border, gray background) │   │
│ └──────────────────────────────┘   │
│                                    │
│ Confidence: 87.5%                  │
│ (Green text, bold)                 │
│                                    │
│ ┌──────────────────────────────┐   │
│ │  [CLASS ACTIVATION MAP]      │   │
│ │                              │   │
│ │   🔴🟠🟡🟢🔵               │   │
│ │   Red = High Activation      │   │
│ │   Blue = Low Activation      │   │
│ │                              │   │
│ │   (Heatmap overlay on MRI)   │   │
│ │                              │   │
│ └──────────────────────────────┘   │
│                                    │
│ ✓ Analysis complete. Mild          │
│   Demented detected with 87.5%     │
│   confidence.                      │
│ (Green background, success style)  │
│                                    │
└────────────────────────────────────┘
```

### 7. Footer Section
```
┌──────────────────────────────────────────────────────────────────┐
│  ⚕️  Disclaimer: NeuroSight AI is an aid-to-diagnosis tool.     │
│  Final diagnosis remains the responsibility of qualified          │
│  medical professionals.                                           │
│  (Light gray background, small gray text)                         │
└──────────────────────────────────────────────────────────────────┘
```

## Color Scheme

| Component | Color | Hex Code | Usage |
|-----------|-------|----------|-------|
| Primary Header | Dark Navy Blue | #1e3a5f | Header background |
| Secondary Blue | Sky Blue | #4a9eff | Buttons, highlights |
| Success Green | Light Green | #2ecc71 | Analyze button |
| Accent Blue | Royal Blue | #3498db | Progress bar |
| Text Primary | Dark Gray | #2c3e50 | Main text |
| Text Secondary | Medium Gray | #666666 | Secondary text |
| Background Light | Very Light Gray | #f5f5f5 | Panels background |
| Border | Light Gray | #cccccc | Borders |
| Success Message | Light Green | #f0fff4 | Success backgrounds |

## State Changes

### Initial State
```
┌────────────────────────────────────┐
│ [ Browse Files ]                   │
│ File: No file selected             │
│                                    │
│ [Disabled] Analyze Image           │
│ (Gray, not clickable)              │
│                                    │
│ [Progress bar hidden]              │
│ Disease Stage: -                   │
│ Confidence: -                      │
└────────────────────────────────────┘
```

### After File Selected
```
┌────────────────────────────────────┐
│ [ Browse Files ]                   │
│ File: .../patient_mri_001.jpg      │
│ [MRI Preview Visible]              │
│                                    │
│ [Enabled] 🚀 Analyze Image         │
│ (Green, clickable)                 │
│                                    │
│ Disease Stage: -                   │
│ Confidence: -                      │
└────────────────────────────────────┘
```

### During Processing
```
┌────────────────────────────────────┐
│ [ Browse Files ] [DISABLED]        │
│ [Disabled] Analyze Image           │
│                                    │
│ ████████░░░░░░░░░░░░ Processing..  │
│                                    │
│ Processing image with ML model...  │
│ (Status message)                   │
└────────────────────────────────────┘
```

### After Analysis
```
┌────────────────────────────────────┐
│ [ Browse Files ]                   │
│ [Enabled] Analyze Image            │
│                                    │
│ ████████████████████████ 100%      │
│                                    │
│ Disease Stage: Mild Demented       │
│ Confidence: 87.5%                  │
│ [Heatmap Visible]                  │
│                                    │
│ ✓ Analysis complete...             │
│ (Green success message)            │
└────────────────────────────────────┘
```

## Responsive Behavior

### Minimum Size: 1000x700
- Buttons and text remain readable
- Splitter proportions maintained

### Maximum Size: Full screen
- Left/Right panel ratio: 40/60
- Content scales proportionally

## Accessibility Features

- **High Contrast**: Text colors meet WCAG AA standards
- **Font Sizes**: Minimum 11px for readability
- **Button Sizes**: Minimum 45px height for touch targets
- **Keyboard Support**: Tab navigation through controls
- **Tooltips**: Hover text on buttons explains actions

## Interaction Flow Diagram

```
START
  │
  ├─ Display empty form
  │
  ├─ User Action: Drag & drop or click Browse
  │  │
  │  └─ Load image path
  │     Display preview
  │     Enable Analyze button
  │
  ├─ User Action: Click Analyze
  │  │
  │  ├─ Disable buttons
  │  ├─ Show progress bar
  │  └─ Send to Python model
  │
  ├─ Python Processing
  │  │
  │  ├─ Load model
  │  ├─ Preprocess image
  │  ├─ Inference
  │  ├─ Generate heatmap
  │  └─ Return JSON
  │
  ├─ Receive Results
  │  │
  │  ├─ Parse JSON
  │  ├─ Display diagnosis
  │  ├─ Display confidence
  │  ├─ Display heatmap
  │  ├─ Update status
  │  ├─ Complete progress (100%)
  │  └─ Re-enable buttons
  │
  └─ User can: Analyze again or Upload new image
```

---

**This mockup represents the final UI design.**  
Use the UI_DESIGNER_GUIDE.md to implement this in Qt Designer.

**Last Updated**: May 2026
