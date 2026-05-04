# Qt Designer - Complete UI Building Guide

## Overview

This guide walks you through building the NeuroSight AI interface using Qt Designer's drag-and-drop interface.

**Time Required**: ~30 minutes  
**Qt Version**: 5.12+ or 6.x  
**Prerequisites**: Qt Creator installed

## Opening Qt Designer

### Method 1: From Qt Creator
1. Open Qt Creator
2. File → Open File or Project
3. Select `ui/mainwindow.ui`
4. Double-click or press Enter
5. Qt Designer opens with the UI editor

### Method 2: Standalone Qt Designer
1. Launch Qt Designer directly
2. File → Open
3. Navigate to `ui/mainwindow.ui`

## UI Layout Map

```
┌─────────────────────────────────────────────────────────┐
│  HEADER FRAME (Dark Blue Background)                   │
│  NeuroSight AI | Intelligent Alzheimer Detection | v1.0 │
├──────────────────────┬──────────────────────────────────┤
│                      │                                  │
│  LEFT PANEL          │      RIGHT PANEL                 │
│  ┌────────────────┐  │  ┌──────────────────────────┐   │
│  │ Upload Area    │  │  │ Analyze Button (GREEN)   │   │
│  │ (Drag & Drop)  │  │  └──────────────────────────┘   │
│  ├────────────────┤  │  ┌──────────────────────────┐   │
│  │ Browse Button  │  │  │ Progress Bar             │   │
│  ├────────────────┤  │  └──────────────────────────┘   │
│  │ File Path      │  │  ┌──────────────────────────┐   │
│  ├────────────────┤  │  │ Results Group Box        │   │
│  │                │  │  │  • Disease Stage        │   │
│  │ Image Preview  │  │  │  • Confidence Score     │   │
│  │                │  │  │  • Heatmap Display      │   │
│  │                │  │  └──────────────────────────┘   │
│  │                │  │  ┌──────────────────────────┐   │
│  │                │  │  │ Status Message           │   │
│  └────────────────┘  │  └──────────────────────────┘   │
│                      │                                  │
├──────────────────────┴──────────────────────────────────┤
│ FOOTER (Light Gray) - Disclaimer Message               │
└──────────────────────────────────────────────────────────┘
```

## Step-by-Step UI Building

### Part 1: Header Section

#### Step 1.1: Add Header Frame
1. **From Object/Class column**: Drag `QFrame` onto the form
2. **Properties Panel** (right side):
   - Object Name: `headerFrame`
   - Minimum Height: `60`
   - StyleSheet: 
     ```css
     QFrame { 
         background-color: #1e3a5f; 
         border-bottom: 2px solid #2c5aa0; 
     }
     ```

#### Step 1.2: Add Layouts to Header
1. Right-click on `headerFrame` → Lay Out → Lay Out in Horizontal Layout
2. Or drag `Horizontal Layout` onto the frame

#### Step 1.3: Add Title Label
1. Drag `QLabel` into the header layout
2. Properties:
   - Object Name: `titleLabel`
   - Text: `NeuroSight AI`
   - Alignment: Left
   - Font Size: 24, Bold
   - StyleSheet:
     ```css
     QLabel { color: white; font-size: 24px; font-weight: bold; }
     ```

#### Step 1.4: Add Subtitle Label
1. Drag another `QLabel` into header
2. Properties:
   - Object Name: `subtitleLabel`
   - Text: `Intelligent Alzheimer Detection System`
   - Font Size: 12
   - StyleSheet:
     ```css
     QLabel { color: #a0c4f7; font-size: 12px; margin-left: 20px; }
     ```

#### Step 1.5: Add Horizontal Spacer
1. Drag `Horizontal Spacer` between subtitle and version labels
2. This pushes the version label to the right

#### Step 1.6: Add Version Label
1. Drag `QLabel` for version
2. Properties:
   - Object Name: `versionLabel`
   - Text: `v1.0.0`
   - StyleSheet: `QLabel { color: #7a98b3; font-size: 10px; }`

---

### Part 2: Main Content Area (Splitter)

#### Step 2.1: Add Splitter
1. Drag `QSplitter` (horizontal) below the header
2. Properties:
   - Object Name: `mainSplitter`
   - Orientation: Horizontal
   - Size Policy: Expanding/Expanding

---

### Part 3: Left Panel (Upload Section)

#### Step 3.1: Create Left Widget
1. Drag `QWidget` into left side of splitter
2. Properties:
   - Object Name: `leftPanel`
3. Right-click → Lay Out → Lay Out in Vertical Layout

#### Step 3.2: Add Upload Group Box
1. Drag `QGroupBox` into left panel
2. Properties:
   - Object Name: `uploadGroup`
   - Title: `MRI Image Upload`
   - Minimum Height: 200
3. Right-click → Lay Out → Lay Out in Vertical Layout

#### Step 3.3: Add Drag & Drop Frame
1. Inside uploadGroup, drag `QFrame`
2. Properties:
   - Object Name: `dragDropFrame`
   - Minimum Height: 150
   - StyleSheet:
     ```css
     QFrame { 
         border: 2px dashed #4a9eff; 
         background-color: #f0f7ff; 
         border-radius: 8px; 
     }
     ```
3. Right-click → Lay Out → Lay Out in Vertical Layout

#### Step 3.4: Add Drag & Drop Label
1. Drag `QLabel` into dragDropFrame
2. Properties:
   - Object Name: `dragDropLabel`
   - Text: `📁 Drag & Drop MRI Image Here\nor Click to Browse`
   - Alignment: Center
   - WordWrap: true
   - StyleSheet:
     ```css
     QLabel { 
         color: #4a9eff; 
         font-size: 14px; 
         font-weight: bold; 
     }
     ```

#### Step 3.5: Add Upload Button
1. Below dragDropFrame, drag `QPushButton`
2. Properties:
   - Object Name: `uploadButton`
   - Text: `Browse Files`
   - Minimum Height: 45
   - Font: Bold, 12px
   - StyleSheet:
     ```css
     QPushButton { 
         background-color: #4a9eff; 
         color: white; 
         font-weight: bold; 
         border: none; 
         border-radius: 5px;
     }
     QPushButton:hover { background-color: #2e7fd9; }
     QPushButton:pressed { background-color: #1e5fa8; }
     ```

#### Step 3.6: Add File Path Label
1. Below uploadButton, drag `QLabel`
2. Properties:
   - Object Name: `imagePathLabel`
   - Text: `No file selected`
   - WordWrap: true
   - Minimum Height: 25
   - StyleSheet: `QLabel { color: #666; font-size: 10px; padding: 5px; }`

#### Step 3.7: Add Preview Group Box
1. Drag `QGroupBox` into left panel
2. Properties:
   - Object Name: `previewGroup`
   - Title: `Image Preview`
   - Minimum Height: 350
3. Right-click → Lay Out → Lay Out in Vertical Layout

#### Step 3.8: Add Image Preview Label
1. Inside previewGroup, drag `QLabel`
2. Properties:
   - Object Name: `imagePreviewLabel`
   - Text: `Image preview will appear here`
   - Alignment: Center
   - Minimum Height: 300
   - StyleSheet:
     ```css
     QLabel { 
         background-color: #f5f5f5; 
         border: 1px solid #ddd; 
         border-radius: 5px; 
         color: #999; 
     }
     ```

#### Step 3.9: Add Spacer to Left Panel
1. Drag `Vertical Spacer` to bottom of left panel
2. This pushes content to top

---

### Part 4: Right Panel (Results Section)

#### Step 4.1: Create Right Widget
1. Drag `QWidget` into right side of splitter
2. Properties:
   - Object Name: `rightPanel`
3. Right-click → Lay Out → Lay Out in Vertical Layout

#### Step 4.2: Add Analyze Button
1. At top of right panel, drag `QPushButton`
2. Properties:
   - Object Name: `analyzeButton`
   - Text: `🚀 Analyze Image`
   - Minimum Height: 60
   - Font: Bold, 16px
   - StyleSheet:
     ```css
     QPushButton { 
         background-color: #2ecc71; 
         color: white; 
         font-weight: bold; 
         font-size: 16px;
         border: none; 
         border-radius: 5px;
     }
     QPushButton:hover { background-color: #27ae60; }
     QPushButton:disabled { background-color: #bdc3c7; }
     ```

#### Step 4.3: Add Progress Bar
1. Below analyzeButton, drag `QProgressBar`
2. Properties:
   - Object Name: `progressBar`
   - Value: 0
   - Minimum: 0
   - Maximum: 100
   - StyleSheet:
     ```css
     QProgressBar {
         border: 1px solid #bdc3c7;
         border-radius: 5px;
         text-align: center;
     }
     QProgressBar::chunk {
         background-color: #3498db;
         border-radius: 3px;
     }
     ```

#### Step 4.4: Add Results Group Box
1. Drag `QGroupBox` into right panel
2. Properties:
   - Object Name: `resultsGroup`
   - Title: `Analysis Results`
3. Right-click → Lay Out → Lay Out in Vertical Layout

#### Step 4.5: Add Disease Stage Result Label
1. Inside resultsGroup, drag `QLabel`
2. Properties:
   - Object Name: `resultLabel`
   - Text: `Disease Stage: -`
   - Minimum Height: 30
   - StyleSheet: `QLabel { font-size: 16px; font-weight: bold; color: #2c3e50; padding: 10px; }`

#### Step 4.6: Add Disease Stage Display
1. Drag `QLineEdit` below resultLabel
2. Properties:
   - Object Name: `diseaseStageLabel`
   - PlaceholderText: `Result will appear here`
   - ReadOnly: true
   - Minimum Height: 40
   - StyleSheet:
     ```css
     QLineEdit { 
         border: 2px solid #3498db; 
         border-radius: 5px; 
         padding: 10px; 
         background-color: #ecf0f1;
         font-size: 14px;
         font-weight: bold;
         color: #2980b9;
     }
     ```

#### Step 4.7: Add Confidence Label
1. Drag `QLabel` below diseaseStageLabel
2. Properties:
   - Object Name: `confidenceLabel`
   - Text: `Confidence: -`
   - Minimum Height: 25
   - StyleSheet: `QLabel { font-size: 14px; color: #27ae60; padding: 10px; font-weight: bold; }`

#### Step 4.8: Add Heatmap Label
1. Drag `QLabel` below confidenceLabel
2. Properties:
   - Object Name: `heatmapLabel`
   - Text: `Class Activation Map (CAM) will appear here`
   - Alignment: Center
   - Minimum Height: 250
   - StyleSheet:
     ```css
     QLabel { 
         background-color: #f5f5f5; 
         border: 1px solid #ddd; 
         border-radius: 5px; 
         color: #999; 
     }
     ```

#### Step 4.9: Add Status Message Label
1. At bottom of right panel, drag `QLabel`
2. Properties:
   - Object Name: `statusLabel`
   - Text: `Ready. Upload an MRI image to begin analysis.`
   - WordWrap: true
   - Minimum Height: 40
   - StyleSheet:
     ```css
     QLabel { 
         color: #27ae60; 
         font-weight: bold; 
         font-size: 11px;
         padding: 10px;
         background-color: #f0fff4;
         border-radius: 5px;
     }
     ```

---

### Part 5: Footer Section

#### Step 5.1: Add Footer Frame
1. Drag `QFrame` below the main splitter
2. Properties:
   - Object Name: `footerFrame`
   - Minimum Height: 50
   - StyleSheet:
     ```css
     QFrame { 
         background-color: #ecf0f1; 
         border-top: 1px solid #bdc3c7; 
         padding: 10px; 
     }
     ```
3. Right-click → Lay Out → Lay Out in Horizontal Layout

#### Step 5.2: Add Disclaimer Label
1. Drag `QLabel` into footerFrame
2. Properties:
   - Object Name: `footerLabel`
   - Text: `⚕️ Disclaimer: NeuroSight AI is an aid-to-diagnosis tool. Final diagnosis remains the responsibility of qualified medical professionals.`
   - WordWrap: true
   - StyleSheet: `QLabel { color: #7f8c8d; font-size: 10px; }`

---

## UI Components Checklist

### Header Section
- ✅ headerFrame (QFrame)
- ✅ titleLabel (QLabel)
- ✅ subtitleLabel (QLabel)
- ✅ versionLabel (QLabel)

### Left Panel
- ✅ leftPanel (QWidget)
- ✅ uploadGroup (QGroupBox)
  - ✅ dragDropFrame (QFrame)
    - ✅ dragDropLabel (QLabel)
  - ✅ uploadButton (QPushButton)
  - ✅ imagePathLabel (QLabel)
- ✅ previewGroup (QGroupBox)
  - ✅ imagePreviewLabel (QLabel)

### Right Panel
- ✅ rightPanel (QWidget)
- ✅ analyzeButton (QPushButton)
- ✅ progressBar (QProgressBar)
- ✅ resultsGroup (QGroupBox)
  - ✅ resultLabel (QLabel)
  - ✅ diseaseStageLabel (QLineEdit)
  - ✅ confidenceLabel (QLabel)
  - ✅ heatmapLabel (QLabel)
  - ✅ statusLabel (QLabel)

### Footer Section
- ✅ footerFrame (QFrame)
- ✅ footerLabel (QLabel)

---

## Saving and Compiling

### Save UI File
1. File → Save or Ctrl+S
2. Verify `ui/mainwindow.ui` is updated

### Generate C++ Header
1. In Qt Creator, right-click .ui file
2. Select "Edit with Designer"
3. Designer automatically generates `ui_mainwindow.h`

### Verify Integration
1. In Qt Creator, build the project (Ctrl+B)
2. Check for compilation errors
3. If errors occur:
   - Verify object names match C++ code
   - Check property names spelling
   - Regenerate ui_mainwindow.h

---

## Testing the UI

### Run Application
1. Click Run (Ctrl+R) in Qt Creator
2. Verify all elements appear correctly
3. Test button functionality

### Common Issues & Fixes

| Issue | Fix |
|-------|-----|
| Buttons too small | Increase Minimum Height property |
| Text cut off | Enable WordWrap or increase size |
| Colors look wrong | Update StyleSheet property |
| Layout broken | Right-click frame → Clear Layout, then re-apply |
| Labels not aligned | Set Alignment property to "Center" |

---

## Advanced Customization

### Adding Custom Stylesheets
1. In Qt Designer, right-click form
2. Select "Edit Stylesheet"
3. Add custom CSS rules
4. Click OK to apply

### Resizing Panels
1. Select `mainSplitter`
2. Drag the divider between panels
3. Set desired proportions

### Adding Tooltips
1. Select any widget
2. In Properties → toolTip
3. Add helpful text

---

## Next Steps

1. Save the .ui file
2. Build in Qt Creator
3. The C++ code automatically connects to UI elements via object names
4. Run the application to test
5. Customize styling as needed

**All .ui file is already provided in `ui/mainwindow.ui`**  
You can import it directly or follow this guide to create your own.

---

**Last Updated**: May 2026  
**Qt Version**: 5.12+ / 6.x Compatible
