# 2D to 3D Room Model - VR/AR Project

This project explores converting multiple 2D room images into a 3D model for VR/AR applications.

It includes experiments with:

- KIRI Engine API
- Apple Object Capture / RealityKit
- COLMAP
- Meshroom / AliceVision exploration

---

## Running This Project Locally

This repository does not include private room images, generated model outputs, or API keys.

To run this project on your own system, you will need:

- Your own room images
- Python 3
- Xcode/macOS for Apple Object Capture
- A KIRI Engine API key if testing the KIRI workflow

---

## 1. Clone the Repository

```bash
git clone <repo-url>
cd 2D-to-3D-Room-Model
```

---

## 2. KIRI Engine Setup

KIRI Engine is a web/API-based reconstruction tool. It can generate a 3D model without requiring a local NVIDIA GPU.

### Requirements

- Python 3
- KIRI Engine API key
- 20 to 300 room images
- Images in `.jpg`, `.jpeg`, or `.png` format

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Create `.env` File

Create a `.env` file in the project root.

Use `.env.example` as a reference:

```text
KIRI_API_KEY=your_api_key_here
```

Do not upload your `.env` file to GitHub.

### Add Images

Create a `Test` folder in the project root and add a room folder inside it.

Example:

```text
Test/
├── Room1/
│   ├── image1.jpg
│   ├── image2.jpg
│   ├── image3.jpg
│   └── ...
└── Output/
```

### Run the KIRI Script

```bash
python3 kiri_engine/kiri_engine.py
```

The script will ask for the room folder name.

For example, if your images are inside:

```text
Test/Room1
```

enter:

```text
Room1
```

The output will be saved automatically in:

```text
Test/Output/Room1_output
```

The generated model should include a `.glb` file, which can be opened in Blender.

---

## 3. Apple Object Capture Setup

Apple Object Capture is a Mac-compatible option that uses Apple’s RealityKit photogrammetry workflow.

### Requirements

- macOS
- Xcode
- A Mac that supports `PhotogrammetrySession`
- Room images in a local folder

### How to Run

Open the Xcode project inside:

```text
apple_object_capture/
```

In Xcode, go to:

```text
Product → Scheme → Edit Scheme → Run → Arguments
```

Add three arguments:

```text
Input image folder path
Output .usdz file path
Detail level
```

Example:

```text
/Users/yourname/Desktop/Room1
/Users/yourname/Desktop/output/Room1_apple.usdz
full
```

Detail options include:

```text
preview
reduced
medium
full
raw
```

The output will be a `.usdz` file. It can be opened on Mac and can also be imported into Blender for inspection.

---

## 4. COLMAP Notes

COLMAP was tested as a free photogrammetry tool.

COLMAP was able to complete sparse reconstruction, but dense reconstruction could not be completed on my Mac because it required NVIDIA CUDA support.

If using COLMAP on another system, an NVIDIA GPU with CUDA support may be needed for the full dense reconstruction pipeline.

---

## Repository Structure

```text
2D-to-3D-Room-Model/
│
├── README.md
├── requirements.txt
├── .env.example
├── .gitignore
│
├── kiri_engine/
│   ├── kiri_engine.py
│   └── test_kiri_connection.py
│
├── COLMAP/
│   └── COLMAP scripts/notes
│
└── apple_object_capture/
    └── Apple Object Capture Xcode project
```

---

# Project Progress Report

## Goal

The goal of this part of the VR/AR project was to test whether multiple 2D images of a room could be converted into a usable 3D model.

The general workflow is:

```text
Room images → 3D reconstruction tool → 3D model output → Blender/viewer
```

---

## Tools That Had Mac/GPU Limitations

I first explored tools like Meshroom and AliceVision because they are commonly used for photogrammetry. However, these tools were not straightforward to run on Mac and had GPU/CUDA-related limitations.

I also tried checking other systems, including a Windows laptop and a remote/Linux setup, but they also did not have an NVIDIA GPU. Because of this, those options could not solve the main CUDA issue.

---

## COLMAP Test

I then tested COLMAP because it is free and can run on Mac.

COLMAP was able to complete the sparse reconstruction step. It used the room images and generated a sparse point cloud, which showed that the images had enough overlap for the software to understand the rough 3D structure of the room.

However, I could not continue to the full reconstruction pipeline. The next step was dense reconstruction, but COLMAP required CUDA. Since Mac does not support NVIDIA CUDA, I could not generate the dense point cloud or final mesh on my system.

Current COLMAP status:

```text
Sparse reconstruction: completed
Dense reconstruction: blocked because CUDA/NVIDIA GPU is unavailable
Final model through COLMAP: not completed
```

---

## KIRI Engine Test

Because of the local system limitations, I tested KIRI Engine as a safer alternative.

I wrote a Python script that:

1. Uploads room images to the KIRI Engine API
2. Waits for the model to finish processing
3. Downloads the output zip file
4. Extracts the final model files

This worked successfully. I was able to generate a `.glb` 3D model from the room images and open it in Blender.

The result is not perfect, but the room layout, furniture, and textures are visible, so it is a useful first working result.

However, KIRI Engine is not fully free. It provides limited free credits/calls, but continued use may require payment. Because of this, it is useful for testing, but it may not be the best long-term solution.

Current KIRI Engine status:

```text
Image upload: completed
Model generation: completed
GLB model downloaded: completed
Model opened in Blender: completed
```

---

## Apple Object Capture Test

I also tested Apple Object Capture as a Mac-compatible option.

For this, I created a Swift command-line project in Xcode using Apple’s Object Capture/RealityKit workflow. This generated a `.usdz` file from the room images.

The `.usdz` model could be opened, rotated, and inspected from different angles. This was useful because Apple Object Capture runs on Mac and does not require NVIDIA CUDA.

The result captured the room visually, including walls, furniture, and textures. However, it is still not a clean architectural 3D model. Also, when the `.usdz` model is opened in Blender, the quality/appearance changes, so I need to investigate whether this is due to Blender import settings, texture handling, or the file format.

Current Apple Object Capture status:

```text
USDZ model generated: completed
Model opened and inspected: completed
Blender import quality issue: needs further testing
```

---

## Current Status

```text
Meshroom/AliceVision: explored, but not suitable for current Mac setup
Windows/Linux testing: blocked because NVIDIA GPU was unavailable

COLMAP sparse reconstruction: completed
COLMAP dense reconstruction: blocked because CUDA/NVIDIA GPU is unavailable

KIRI Engine model generation: completed successfully
GLB model opened in Blender: completed

Apple Object Capture test: completed
USDZ model generated: completed
USDZ model opened and inspected: completed
Blender import quality issue: needs further testing
```

---

## Next Steps

The next step is to test with more images and compare the quality of the results.

I want to check whether adding more good-quality photos improves the Apple Object Capture output.

I also need to investigate why the `.usdz` model looks different or lower quality when opened in Blender. This may require testing Blender import settings, checking texture handling, or converting the file format before importing it into Blender.

Other next steps include:

1. Testing another room with KIRI Engine
2. Testing Apple Object Capture with more images
3. Comparing `.glb` and `.usdz` outputs
4. Improving the Blender import/viewing workflow
5. Exploring more free or Mac-compatible reconstruction options

---

## Notes

Private image folders, generated model outputs, API keys, and environment files are not included in this repository.

The `.env.example` file is provided only as a template. Users need to add their own KIRI Engine API key if they want to test the KIRI workflow.
