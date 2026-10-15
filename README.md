# 🧠 YOLO AI Aimbot - Lunar LITE

**Lunar LITE** is built on top of the original [Lunar](https://github.com/zeyad-mansour/lunar) project.

It features an updated triggerbot, GUI control panel, smoothness scaling, Raspberry Pi Pico HID mouse support, and YOLO model selection.

---

## 🚀 Key Features

- ✅ **Modern Built-in GUI Control Panel** (`lib/gui.py`)
- ✅ **Raspberry Pi Pico USB HID Mouse Support** (`pico`)
- ✅ **Smoothness Slider** (`0.0` = Fast, `10.0` = Very Slow/Smooth)
- ✅ **FOV Box Size Slider** (`100` to `600` pixels)
- ✅ **In-Game X/Y & Targeting Sensitivity Sliders**
- ✅ **Aim Height Offset Slider** (Lower = Head, Higher = Chest)
- ✅ **Real-Time YOLO Model Selector** (Supports `lib/best.pt`, `lib/yolov11.pt`, custom `.pt` files)
- ✅ **Mouse Driver Selection** (`pico`, `ddxoft` DLL, `win32`, `makcu` UDP)
- ✅ **Always-On-Top Screen Capture Overlay**
- ✅ **Fixed Screen Freeze Bug**: Smooth frame-by-frame interpolation eliminates capture freezes when holding right-click!

---

## 📖 Setup & Tutorial

For full step-by-step setup instructions, Raspberry Pi Pico USB HID flashing, mouse DLL administration, and troubleshooting, please read **[TUTORIAL.md](TUTORIAL.md)**.

### Quick Start:

1. Install Python 3.10 or 3.11 (Check "Add Python to PATH").
2. Run `install_requirements.bat` or `pip install -r requirements.txt`.
3. Run `start.bat` (or `python lunar.py`).
