# 📖 Lunar LITE AI Aimbot - Complete Setup & Tutorial Guide

Welcome to the official setup and configuration tutorial for **Lunar LITE AI Aimbot**. This guide covers system requirements, installation, mouse driver DLL / Raspberry Pi Pico HID setup, GUI controls, sensitivity calibration, and troubleshooting.

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

## 🔌 Raspberry Pi Pico HID Mouse Input Setup

Lunar LITE supports using a **Raspberry Pi Pico** as a true hardware USB HID mouse controller.

### 1. Flashing CircuitPython to Raspberry Pi Pico
1. Download CircuitPython UF2 for Raspberry Pi Pico from [circuitpython.org](https://circuitpython.org/board/raspberry_pi_pico/).
2. Hold down the **BOOTSEL** button on your Pi Pico and connect it to your PC via USB.
3. Drag and drop the `.uf2` file onto the mounted **RPI-RP2** drive. The board will reboot into **CIRCUITPY**.

### 2. Copying Firmware & Libraries
1. Download the [Adafruit CircuitPython HID bundle](https://github.com/adafruit/Adafruit_CircuitPython_HID/releases) and place the `adafruit_hid` folder into `lib/` on the `CIRCUITPY` drive.
2. Copy `pico_firmware/code.py` from this project onto the root of your `CIRCUITPY` drive as `code.py`.

### 3. Connecting in Lunar LITE GUI
1. Open Windows Device Manager and check Ports (COM & LPT) to find your Pico's port (e.g. `COM3`).
2. Open the Lunar GUI (`python lunar.py`), select **Mouse Input Method: pico**, and type your COM port into **Pico COM Port** (e.g. `COM3`).

---

## 🖱️ Other Mouse Input Drivers (`ddxoft` / `win32` / `makcu`)

### 1. `ddxoft` (Hardware Simulation DLL)
- Included DLL: `lib/mouse/dd40605x64.dll`
- Right-click `start.bat` and select **"Run as administrator"**.

### 2. `win32` (Standard Windows Input API)
- Works out of the box on any Windows system without driver requirements.

### 3. `makcu` (Dual PC UDP Input)
- Sends relative movements over UDP to a secondary host running `lib/makcu_second_pc/listener.py`.

---

## ⚙️ GUI Control Panel Settings & Features

| Setting | Range / Options | Description |
| :--- | :--- | :--- |
| **Smoothness** | `0.0` to `10.0` | Controls target tracking smoothness (`0.0` = Fast, `10.0` = Very Smooth/Slow). |
| **FOV Box Size** | `100` to `600` px | Sets the detection box size centered on your crosshair. |
| **In-Game X/Y Sens**| `0.5` to `20.0` | Match your in-game horizontal and vertical mouse sensitivity. |
| **Targeting Sens** | `0.5` to `20.0` | Match your in-game ADS / Scoping sensitivity. |
| **Aim Height Offset**| `1` to `20` | Lower values aim closer to the head, higher values aim towards the chest/body. |
| **YOLO Model Selector** | Dropdown (`*.pt`) | Instantly switch between AI model files in `lib/`. |
| **Confidence Threshold**| `0.10` to `0.95` | AI confidence required before locking on. Default is `0.45` (45%). |
| **Mouse Input Method** | `pico` / `ddxoft` / `win32` / `makcu` | Select your active mouse driver. |
| **Pico COM Port** | e.g. `COM3` | Serial port for Raspberry Pi Pico HID. |
| **Auto Triggerbot** | Switch (On/Off) | Automatically fires when crosshair locks onto an enemy target. |
| **Always On Top** | Switch (On/Off) | Keeps the live screen capture preview on top. |

---

## ⌨️ In-Game Hotkeys

- **`F1`**: Toggle Aimbot On / Off in real-time.
- **`F2`**: Clean Exit & Emergency Stop.
