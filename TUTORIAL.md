# 📖 Lunar LITE AI Aimbot - Complete Setup & Tutorial Guide

Welcome to the official setup and configuration tutorial for **Lunar LITE AI Aimbot**. This guide covers system requirements, installation, mouse driver DLL setup, GUI controls, sensitivity calibration, and troubleshooting.

---

## 🛠️ Requirements & System Prerequisites

Before running Lunar LITE AI, ensure your system meets the following requirements:

1. **Operating System**: Windows 10 / Windows 11 (64-bit).
2. **Python**: [Python 3.10 or 3.11](https://www.python.org/downloads/) (Make sure to check **"Add Python to PATH"** during installation).
3. **NVIDIA GPU & CUDA (Recommended for fast FPS)**:
   - Install **CUDA Toolkit 12.6** or 12.4 for GPU acceleration.
   - For CUDA 12.6 support, run:
     ```bash
     pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu126
     ```
   - *Note*: If GPU/CUDA is unavailable, Lunar LITE will automatically run safely in CPU mode (`half=False` precision).

---

## 🚀 Step-by-Step Installation

### 1. Extract Project Files
Download or clone the project repository into a local folder (e.g., `C:\LunarLITE`).

### 2. Install Dependencies
Double-click `install_requirements.bat` or open Command Prompt in the project folder and run:
```bash
pip install -r requirements.txt
```

---

## 🖱️ Mouse Input Drivers Setup (`ddxoft` / `win32` / `makcu`)

Lunar LITE supports three mouse movement methods:

### 1. `ddxoft` (Recommended - Hardware Level Input Simulation)
- **Included DLL**: `lib/mouse/dd40605x64.dll`
- **Setup Requirements**:
  1. Right-click `start.bat` and select **"Run as administrator"**.
  2. The `ddxoft` driver provides low-latency kernel-level mouse movements (`DD_movR`) and click events (`DD_btn`).
  3. If administrative privileges are missing or DLL initialization fails, Lunar LITE gracefully falls back to `win32`.

### 2. `win32` (Standard Windows Input API)
- Uses standard Windows `SendInput` and `mouse_event` APIs.
- Works out of the box on any Windows system without driver requirements.

### 3. `makcu` (Dual PC UDP Input)
- Ideal for dual-PC setups.
- Transmits relative movements over UDP to a secondary host running `lib/makcu_second_pc/listener.py`.

---

## 🖥️ Launching the Graphical User Interface (GUI)

Launch Lunar LITE using:
```bash
start.bat
```
or via terminal:
```bash
python lunar.py
```

This opens the **Lunar LITE AI Control Panel**:

---

## ⚙️ GUI Control Panel Settings & Features

| Setting | Range / Options | Description |
| :--- | :--- | :--- |
| **Smoothness** | `0.0` to `5.0` | Controls target tracking smoothness. `0.0` = **Instant Lock-On**, `5.0` = **Very Smooth & Natural Tracking** (eliminates screen capture freezing). |
| **FOV Box Size** | `100` to `600` px | Sets the detection box size centered on your crosshair. |
| **In-Game X/Y Sens**| `0.5` to `20.0` | Set this to match your in-game horizontal and vertical mouse sensitivity. |
| **Targeting Sens** | `0.5` to `20.0` | Set this to match your in-game ADS / Scoping sensitivity. |
| **Aim Height Offset**| `1` to `20` | Offset ratio for targeting. Lower values aim closer to the head, higher values aim towards the chest/body. |
| **YOLO Model Selector** | Dropdown (`*.pt`) | Instantly switch between custom AI model files stored in `lib/` (e.g., `lib/best.pt`, `lib/yolov11.pt`). |
| **Confidence Threshold**| `0.10` to `0.95` | AI confidence required before locking on. Default is `0.45` (45%). |
| **Mouse Input Method** | `ddxoft` / `win32` / `makcu` | Select your active mouse driver. |
| **Auto Triggerbot** | Switch (On/Off) | Automatically fires when crosshair locks onto an enemy target. |
| **Always On Top** | Switch (On/Off) | Ensures the live screen capture window remains on top of game windows. |

---

## ⌨️ In-Game Hotkeys

- **`F1`**: Toggle Aimbot On / Off in real-time.
- **`F2`**: Clean Exit & Emergency Stop.

---

## ❓ Troubleshooting & FAQs

### Q1: Screen freeze when aiming / right-clicking
- **Fixed in this version!** Target movements now process in real-time per frame without sleeping the capture thread.

### Q2: `[!] CUDA ACCELERATION IS UNAVAILABLE`
- Ensure you have an NVIDIA GPU and installed PyTorch CUDA build.
- Command: `pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu126`

### Q3: Mouse is not moving in-game
- Run `start.bat` as Administrator.
- Set game display mode to **Windowed Fullscreen** or **Borderless Windowed**.
- If `ddxoft` fails, switch Mouse Method in the GUI dropdown to `win32`.
