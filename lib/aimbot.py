import ctypes
import cv2
import json
import math
import mss
import os
import sys
import time
import torch
import numpy as np
from termcolor import colored
from ultralytics import YOLO
import socket

try:
    import serial
except ImportError:
    serial = None

# Safely import win32api
try:
    import win32api
except ImportError:
    win32api = None

if hasattr(ctypes, 'windll') and hasattr(ctypes.windll, 'user32'):
    screensize = {'X': ctypes.windll.user32.GetSystemMetrics(0), 'Y': ctypes.windll.user32.GetSystemMetrics(1)}
else:
    screensize = {'X': 1920, 'Y': 1080}

screen_res_x = screensize['X']
screen_res_y = screensize['Y']

screen_x = int(screen_res_x / 2)
screen_y = int(screen_res_y / 2)

aim_height = 10
fov = 350
confidence = 0.45
use_trigger_bot = True
smoothness = 2.0
always_on_top = True

mouse_methods = ['win32', 'ddxoft', 'makcu', 'pico']
mouse_method = mouse_methods[1]
pico_port = 'COM3'

second_pc_ip = '192.67.67.67'

PUL = ctypes.POINTER(ctypes.c_ulong)
class KeyBdInput(ctypes.Structure):
    _fields_ = [("wVk", ctypes.c_ushort),
                ("wScan", ctypes.c_ushort),
                ("dwFlags", ctypes.c_ulong),
                ("time", ctypes.c_ulong),
                ("dwExtraInfo", PUL)]

class HardwareInput(ctypes.Structure):
    _fields_ = [("uMsg", ctypes.c_ulong),
                ("wParamL", ctypes.c_short),
                ("wParamH", ctypes.c_ushort)]

class MouseInput(ctypes.Structure):
    _fields_ = [("dx", ctypes.c_long),
                ("dy", ctypes.c_long),
                ("mouseData", ctypes.c_ulong),
                ("dwFlags", ctypes.c_ulong),
                ("time", ctypes.c_ulong),
                ("dwExtraInfo", PUL)]

class Input_I(ctypes.Union):
    _fields_ = [("ki", KeyBdInput),
                ("mi", MouseInput),
                ("hi", HardwareInput)]

class Input(ctypes.Structure):
    _fields_ = [("type", ctypes.c_ulong),
                ("ii", Input_I)]

class POINT(ctypes.Structure):
    _fields_ = [("x", ctypes.c_long), ("y", ctypes.c_long)]

class PicoSerial:
    def __init__(self, port="COM3"):
        self.port = port
        self.serial = None

    def connect(self, port=None):
        if port:
            self.port = port
        if not serial:
            print(colored("[!] pyserial is not installed. Install with 'pip install pyserial'", "red"))
            return False
        try:
            if not self.serial or not self.serial.is_open or self.serial.port != self.port:
                if self.serial:
                    try:
                        self.serial.close()
                    except Exception:
                        pass
                self.serial = serial.Serial(self.port, baudrate=115200, timeout=0.3)

            time.sleep(0.1)
            try:
                self.serial.reset_input_buffer()
                self.serial.reset_output_buffer()
            except Exception:
                pass

            for attempt in range(5):
                self.serial.write(b"\nPING\n")
                time.sleep(0.1)
                reply = self.serial.readline().decode(errors="ignore").strip()
                if "PONG" in reply or "Pico" in reply:
                    print(colored(f"[INFO] Raspberry Pi Pico handshake OK on {self.port}", "green"))
                    return True

            print(colored(f"[INFO] Connected to Raspberry Pi Pico on {self.port} (handshake fallback)", "green"))
            return True
        except Exception as e:
            print(colored(f"[!] Failed to connect to Raspberry Pi Pico on {self.port}: {e}", "yellow"))
            self.serial = None
            return False

    def move(self, dx, dy):
        if self.serial and self.serial.is_open:
            try:
                self.serial.write(f"M,{int(dx)},{int(dy)}\n".encode())
            except Exception:
                pass

    def click(self):
        if self.serial and self.serial.is_open:
            try:
                self.serial.write(b"CLICK\n")
            except Exception:
                pass

class MAKCU_UDP:
    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def send(self, msg):
        try:
            self.sock.sendto(msg.encode("utf-8"), (second_pc_ip, 5005))
        except Exception:
            pass

    def move(self, x, y):
        msg = f"MOVE:{int(x)},{int(y)}"
        self.send(msg)

    def click(self):
        self.send("CLICK:LEFT")

class Aimbot:
    extra = ctypes.c_ulong(0)
    ii_ = Input_I()
    screen = None

    pixel_increment = 1

    default_sens = {
        "xy_sens": 5.0,
        "targeting_sens": 5.0,
        "xy_scale": 0.1,
        "targeting_scale": 1.0,
        "pico_port": "COM3"
    }
    if os.path.exists("lib/config/config.json"):
        try:
            with open("lib/config/config.json") as f:
                sens_config = json.load(f)
        except Exception:
            sens_config = default_sens
    else:
        sens_config = default_sens

    aimbot_status = colored("ENABLED", 'green')

    mouse_dll = None
    makcu = None
    pico = None
    ddxoft_attempted = False

    def __init__(self, box_constant = fov, collect_data = False, mouse_delay = 0.0009):
        self.box_constant = box_constant
        self.aim_height = aim_height
        self.smoothness = smoothness
        self.always_on_top = always_on_top
        self.use_trigger_bot = use_trigger_bot
        self.is_running = False

        if Aimbot.screen is None:
            try:
                Aimbot.screen = mss.mss()
            except Exception as e:
                print(colored(f"[!] Warning initializing mss screen capture: {e}", "yellow"))

        print("[INFO] Loading the neural network model")
        self.use_cuda = torch.cuda.is_available()
        self.model_path = 'lib/best.pt'
        if not os.path.exists(self.model_path) and os.path.exists('lib/yolov11.pt'):
            self.model_path = 'lib/yolov11.pt'
        self.model = YOLO(self.model_path)
        if self.use_cuda:
            print(colored("CUDA ACCELERATION [ENABLED]", "green"))
        else:
            print(colored("[!] CUDA ACCELERATION IS UNAVAILABLE", "red"))
            print(colored("[!] Check your PyTorch installation, else performance will be poor", "red"))

        self.conf = confidence
        self.iou = 0.45
        self.collect_data = collect_data
        self.mouse_delay = mouse_delay
        self.mouse_method = mouse_method

        self.init_mouse_driver()

        print("\n[INFO] PRESS 'F1' TO TOGGLE AIMBOT\n[INFO] PRESS 'F2' TO QUIT")

    def init_mouse_driver(self):
        if self.mouse_method.lower() == 'pico':
            port = self.sens_config.get("pico_port", "COM3")
            if not Aimbot.pico:
                Aimbot.pico = PicoSerial(port=port)
            Aimbot.pico.connect(port=port)
        elif self.mouse_method.lower() == 'makcu':
            if not Aimbot.makcu:
                Aimbot.makcu = MAKCU_UDP()
        elif self.mouse_method.lower() == 'ddxoft':
            if Aimbot.ddxoft_attempted:
                if not Aimbot.mouse_dll:
                    self.mouse_method = 'win32'
                return
            Aimbot.ddxoft_attempted = True
            dll_path = os.path.abspath("lib/mouse/dd40605x64.dll")
            if not os.path.exists(dll_path) or not hasattr(ctypes, 'WinDLL'):
                print(colored(f"[!] ddxoft DLL not applicable or not found at {dll_path}. Defaulting to Win32", "yellow"))
                self.mouse_method = 'win32'
            else:
                try:
                    Aimbot.mouse_dll = ctypes.WinDLL(dll_path)
                    time.sleep(0.2)
                    Aimbot.mouse_dll.DD_btn.argtypes = [ctypes.c_int]
                    Aimbot.mouse_dll.DD_btn.restype = ctypes.c_int
                    Aimbot.mouse_dll.DD_movR.argtypes = [ctypes.c_int, ctypes.c_int]
                    Aimbot.mouse_dll.DD_movR.restype = ctypes.c_int
                    init = Aimbot.mouse_dll.DD_btn(0)
                    if init != 1:
                        print(colored('Failed to initialize ddxoft mouse driver (DD_btn return != 1). Defaulting to Win32', 'yellow'))
                        Aimbot.mouse_dll = None
                        self.mouse_method = 'win32'
                    else:
                        print(colored('Loaded ddxoft mouse driver successfully!', 'green'))
                except Exception as e:
                    print(colored(f"[!] Error loading ddxoft DLL: {e}. Defaulting to Win32", "yellow"))
                    Aimbot.mouse_dll = None
                    self.mouse_method = 'win32'

    @staticmethod
    def update_status_aimbot():
        if Aimbot.aimbot_status == colored("ENABLED", 'green'):
            Aimbot.aimbot_status = colored("DISABLED", 'red')
        else:
            Aimbot.aimbot_status = colored("ENABLED", 'green')
        try:
            sys.stdout.write("\033[K")
            print(f"[!] AIMBOT IS [{Aimbot.aimbot_status}]", end = "\r")
        except Exception:
            pass

    def left_click(self):
        match self.mouse_method.lower():
            case 'pico':
                if Aimbot.pico:
                    Aimbot.pico.click()
            case 'ddxoft':
                if Aimbot.mouse_dll:
                    Aimbot.mouse_dll.DD_btn(1)
                    Aimbot.sleep(0.001)
                    Aimbot.mouse_dll.DD_btn(2)
            case 'win32':
                if hasattr(ctypes, 'windll') and hasattr(ctypes.windll, 'user32'):
                    ctypes.windll.user32.mouse_event(0x0002)
                    Aimbot.sleep(0.0001)
                    ctypes.windll.user32.mouse_event(0x0004)
            case 'makcu':
                if Aimbot.makcu:
                    Aimbot.makcu.click()

    @staticmethod
    def sleep(duration, get_now = time.perf_counter):
        if duration <= 0: return
        now = get_now()
        end = now + duration
        while now < end:
            now = get_now()

    @staticmethod
    def is_aimbot_enabled():
        return Aimbot.aimbot_status == colored("ENABLED", 'green')

    @staticmethod
    def is_shooting():
        if win32api:
            try:
                return win32api.GetKeyState(0x01) in (-127, -128)
            except Exception:
                return False
        return False

    @staticmethod
    def is_targeted():
        if win32api:
            try:
                return win32api.GetKeyState(0x02) in (-127, -128)
            except Exception:
                return True
        return True

    @staticmethod
    def is_target_locked(x, y):
        threshold = 5
        return screen_x - threshold <= x <= screen_x + threshold and screen_y - threshold <= y <= screen_y + threshold

    def change_model(self, model_path):
        if os.path.exists(model_path) and model_path != self.model_path:
            try:
                self.model = YOLO(model_path)
                self.model_path = model_path
                print(colored(f"[INFO] Loaded model: {model_path}", "green"))
            except Exception as e:
                print(colored(f"[!] Failed to load model {model_path}: {e}", "red"))

    def move_crosshair(self, x, y):
        if not Aimbot.is_targeted():
            return

        scale = self.sens_config.get("targeting_scale", 1.0)

        diff_x = (x - screen_x) * scale
        diff_y = (y - screen_y) * scale

        smooth_val = max(0.0, float(self.smoothness))
        smooth_factor = 1.0 / (1.0 + smooth_val * 2.0)

        move_x = diff_x * smooth_factor
        move_y = diff_y * smooth_factor

        if abs(move_x) < 1.0 and abs(diff_x) >= 0.5:
            rel_x = 1 if diff_x > 0 else -1
        else:
            rel_x = int(round(move_x))

        if abs(move_y) < 1.0 and abs(diff_y) >= 0.5:
            rel_y = 1 if diff_y > 0 else -1
        else:
            rel_y = int(round(move_y))

        if rel_x == 0 and rel_y == 0:
            return

        match self.mouse_method.lower():
            case 'pico':
                if Aimbot.pico:
                    Aimbot.pico.move(rel_x, rel_y)
            case 'ddxoft':
                if Aimbot.mouse_dll:
                    Aimbot.mouse_dll.DD_movR(rel_x, rel_y)
                elif hasattr(ctypes, 'windll') and hasattr(ctypes.windll, 'user32'):
                    Aimbot.ii_.mi = MouseInput(rel_x, rel_y, 0, 0x0001, 0, ctypes.pointer(Aimbot.extra))
                    input_obj = Input(ctypes.c_ulong(0), Aimbot.ii_)
                    ctypes.windll.user32.SendInput(1, ctypes.byref(input_obj), ctypes.sizeof(input_obj))
            case 'win32':
                if hasattr(ctypes, 'windll') and hasattr(ctypes.windll, 'user32'):
                    Aimbot.ii_.mi = MouseInput(rel_x, rel_y, 0, 0x0001, 0, ctypes.pointer(Aimbot.extra))
                    input_obj = Input(ctypes.c_ulong(0), Aimbot.ii_)
                    ctypes.windll.user32.SendInput(1, ctypes.byref(input_obj), ctypes.sizeof(input_obj))
            case 'makcu':
                if Aimbot.makcu:
                    Aimbot.makcu.move(rel_x, rel_y)

    def set_always_on_top(self):
        try:
            cv2.setWindowProperty("Screen Capture", cv2.WND_PROP_TOPMOST, 1 if self.always_on_top else 0)
            if os.name == 'nt' and hasattr(ctypes, 'windll') and hasattr(ctypes.windll, 'user32'):
                hwnd = ctypes.windll.user32.FindWindowW(None, "Screen Capture")
                if hwnd:
                    HWND_TOPMOST = -1
                    HWND_NOTOPMOST = -2
                    SWP_NOMOVE = 0x0002
                    SWP_NOSIZE = 0x0001
                    flag = HWND_TOPMOST if self.always_on_top else HWND_NOTOPMOST
                    ctypes.windll.user32.SetWindowPos(hwnd, flag, 0, 0, 0, 0, SWP_NOMOVE | SWP_NOSIZE)
        except Exception:
            pass

    def start(self):
        print("[INFO] Beginning screen capture")
        self.is_running = True
        Aimbot.aimbot_status = colored("ENABLED", 'green')

        half_screen_width = screen_res_x / 2
        half_screen_height = screen_res_y / 2

        window_created = False

        while self.is_running:
            start_time = time.perf_counter()
            box_size = int(self.box_constant)
            detection_box = {
                'left': int(half_screen_width - box_size // 2),
                'top': int(half_screen_height - box_size // 2),
                'width': box_size,
                'height': box_size
            }

            try:
                initial_frame = Aimbot.screen.grab(detection_box)
            except Exception as e:
                time.sleep(0.01)
                continue

            frame = np.array(initial_frame, dtype=np.uint8)
            if frame is None or frame.size == 0:
                continue
            frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)

            boxes = self.model.predict(source=frame, verbose=False, conf=self.conf, iou=self.iou, half=self.use_cuda)
            result = boxes[0]

            if len(result.boxes.xyxy) != 0:
                least_crosshair_dist = None
                closest_detection = None

                for box in result.boxes.xyxy:
                    x1, y1, x2, y2 = map(int, box)
                    x1y1 = (x1, y1)
                    x2y2 = (x2, y2)
                    height = y2 - y1
                    current_aim_height = max(1, self.aim_height)
                    relative_head_X = int((x1 + x2) / 2)
                    relative_head_Y = int((y1 + y2) / 2 - height / current_aim_height)

                    own_player = x1 < 15 or (x1 < box_size / 5 and y2 > box_size / 1.2)
                    crosshair_dist = math.dist((relative_head_X, relative_head_Y), (box_size / 2, box_size / 2))

                    if least_crosshair_dist is None or crosshair_dist < least_crosshair_dist:
                        if not own_player:
                            least_crosshair_dist = crosshair_dist
                            closest_detection = {
                                "x1y1": x1y1,
                                "x2y2": x2y2,
                                "relative_head_X": relative_head_X,
                                "relative_head_Y": relative_head_Y
                            }

                if closest_detection:
                    cv2.circle(frame, (closest_detection["relative_head_X"], closest_detection["relative_head_Y"]), 5, (115, 244, 113), -1)
                    cv2.line(frame, (closest_detection["relative_head_X"], closest_detection["relative_head_Y"]), (int(box_size // 2), int(box_size // 2)), (244, 242, 113), 2)

                    absolute_head_X = closest_detection["relative_head_X"] + detection_box['left']
                    absolute_head_Y = closest_detection["relative_head_Y"] + detection_box['top']
                    x1, y1 = closest_detection["x1y1"]

                    if Aimbot.is_target_locked(absolute_head_X, absolute_head_Y):
                        if self.use_trigger_bot and not Aimbot.is_shooting():
                            self.left_click()
                        cv2.putText(frame, "LOCKED", (x1 + 40, y1), cv2.FONT_HERSHEY_DUPLEX, 0.5, (115, 244, 113), 2)
                    else:
                        cv2.putText(frame, "TARGETING", (x1 + 40, y1), cv2.FONT_HERSHEY_DUPLEX, 0.5, (115, 113, 244), 2)

                    if Aimbot.is_aimbot_enabled():
                        self.move_crosshair(absolute_head_X, absolute_head_Y)

            elapsed = time.perf_counter() - start_time
            fps = int(1 / elapsed) if elapsed > 0 else 0
            cv2.putText(frame, f"FPS: {fps}", (5, 30), cv2.FONT_HERSHEY_DUPLEX, 1, (113, 116, 244), 2)
            cv2.imshow("Screen Capture", frame)

            if not window_created:
                self.set_always_on_top()
                window_created = True

            if cv2.waitKey(1) & 0xFF == ord('0'):
                break

        cv2.destroyAllWindows()

    @staticmethod
    def clean_up():
        print("\n[INFO] F2 WAS PRESSED. QUITTING...")
        if Aimbot.screen:
            try:
                Aimbot.screen.close()
            except Exception:
                pass
        os._exit(0)

if __name__ == "__main__":
    print("You are in the wrong directory and are running the wrong file; you must run lunar.py")
