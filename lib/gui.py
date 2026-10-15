import os
import json
import glob
import threading
import customtkinter as ctk

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

CONFIG_PATH = "lib/config/config.json"

def load_config():
    default_config = {
        "xy_sens": 5.0,
        "targeting_sens": 5.0,
        "xy_scale": 2.0,
        "targeting_scale": 20.0,
        "fov": 350,
        "smoothness": 0.0,
        "confidence": 0.45,
        "aim_height": 10,
        "use_trigger_bot": True,
        "mouse_method": "ddxoft",
        "always_on_top": True,
        "selected_model": "lib/best.pt"
    }
    if os.path.exists(CONFIG_PATH):
        try:
            with open(CONFIG_PATH, "r") as f:
                data = json.load(f)
                default_config.update(data)
        except Exception:
            pass
    return default_config

def save_config(cfg):
    os.makedirs(os.path.dirname(CONFIG_PATH), exist_ok=True)
    try:
        with open(CONFIG_PATH, "w") as f:
            json.dump(cfg, f, indent=4)
    except Exception as e:
        print(f"[!] Error saving config: {e}")

class LunarGUI(ctk.CTk):
    def __init__(self, aimbot_instance=None):
        super().__init__()

        self.aimbot = aimbot_instance
        self.config_data = load_config()

        self.title("🌙 Lunar LITE AI - Control Panel")
        self.geometry("860x700")
        self.resizable(False, False)

        # Configure dark theme palette
        self.configure(fg_color="#121214")

        self.aimbot_thread = None
        self.is_running = False

        self.scan_models()
        self.build_ui()
        self.apply_config_to_aimbot()

    def scan_models(self):
        models = glob.glob("lib/*.pt") + glob.glob("*.pt")
        models = sorted(list(set([m.replace("\\", "/") for m in models])))
        if not models:
            models = ["lib/best.pt"]
        self.available_models = models

    def build_ui(self):
        # Header Frame
        header_frame = ctk.CTkFrame(self, fg_color="#1e1e24", corner_radius=12)
        header_frame.pack(fill="x", padx=20, pady=(20, 10))

        title_label = ctk.CTkLabel(
            header_frame,
            text="🌙 LUNAR LITE AI",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color="#a78bfa"
        )
        title_label.pack(side="left", padx=20, pady=15)

        subtitle_label = ctk.CTkLabel(
            header_frame,
            text="v2.0 LITE • YOLO Detection Suite",
            font=ctk.CTkFont(size=12),
            text_color="#9ca3af"
        )
        subtitle_label.pack(side="left", padx=5, pady=15)

        self.status_badge = ctk.CTkLabel(
            header_frame,
            text="● STOPPED",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color="#ef4444",
            fg_color="#27272a",
            corner_radius=8,
            padx=12,
            pady=6
        )
        self.status_badge.pack(side="right", padx=20, pady=15)

        # Content Grid
        content_frame = ctk.CTkFrame(self, fg_color="transparent")
        content_frame.pack(fill="both", expand=True, padx=20, pady=10)

        left_column = ctk.CTkFrame(content_frame, fg_color="#1e1e24", corner_radius=12)
        left_column.pack(side="left", fill="both", expand=True, padx=(0, 10))

        right_column = ctk.CTkFrame(content_frame, fg_color="#1e1e24", corner_radius=12)
        right_column.pack(side="right", fill="both", expand=True, padx=(10, 0))

        # --- LEFT COLUMN: Motion & Sensitivity Controls ---
        left_title = ctk.CTkLabel(
            left_column, text="🎯 Aim & Motion Settings", font=ctk.CTkFont(size=16, weight="bold"), text_color="#e5e7eb"
        )
        left_title.pack(anchor="w", padx=20, pady=(15, 10))

        # Smoothness Slider
        self.smoothness_var = ctk.DoubleVar(value=float(self.config_data.get("smoothness", 0.0)))
        self.create_slider(
            left_column,
            label="Smoothness (0 = Lock-On, 5 = Very Smooth):",
            variable=self.smoothness_var,
            from_=0.0,
            to=5.0,
            steps=50,
            command=self.on_smoothness_change
        )

        # FOV Slider
        self.fov_var = ctk.IntVar(value=int(self.config_data.get("fov", 350)))
        self.create_slider(
            left_column,
            label="FOV Box Size (Pixels):",
            variable=self.fov_var,
            from_=100,
            to=600,
            steps=50,
            command=self.on_fov_change
        )

        # X/Y Sensitivity Slider
        self.xy_sens_var = ctk.DoubleVar(value=float(self.config_data.get("xy_sens", 5.0)))
        self.create_slider(
            left_column,
            label="In-Game X/Y Sensitivity:",
            variable=self.xy_sens_var,
            from_=0.5,
            to=20.0,
            steps=39,
            command=self.on_sens_change
        )

        # Targeting Sensitivity Slider
        self.targeting_sens_var = ctk.DoubleVar(value=float(self.config_data.get("targeting_sens", 5.0)))
        self.create_slider(
            left_column,
            label="Targeting/Scoping Sensitivity:",
            variable=self.targeting_sens_var,
            from_=0.5,
            to=20.0,
            steps=39,
            command=self.on_sens_change
        )

        # Aim Height Ratio Slider
        self.aim_height_var = ctk.IntVar(value=int(self.config_data.get("aim_height", 10)))
        self.create_slider(
            left_column,
            label="Aim Height Offset (Lower = Head, Higher = Chest):",
            variable=self.aim_height_var,
            from_=1,
            to=20,
            steps=19,
            command=self.on_aim_height_change
        )

        # --- RIGHT COLUMN: AI Model & Mouse Configuration ---
        right_title = ctk.CTkLabel(
            right_column, text="🤖 AI Model & Input Drivers", font=ctk.CTkFont(size=16, weight="bold"), text_color="#e5e7eb"
        )
        right_title.pack(anchor="w", padx=20, pady=(15, 10))

        # Model Selector
        model_label = ctk.CTkLabel(right_column, text="Select YOLO Model:", font=ctk.CTkFont(size=13), text_color="#9ca3af")
        model_label.pack(anchor="w", padx=20, pady=(5, 2))

        selected_m = self.config_data.get("selected_model", self.available_models[0])
        if selected_m not in self.available_models:
            selected_m = self.available_models[0]

        self.model_dropdown = ctk.CTkOptionMenu(
            right_column,
            values=self.available_models,
            command=self.on_model_select,
            fg_color="#27272a",
            button_color="#3f3f46",
            button_hover_color="#52525b"
        )
        self.model_dropdown.set(selected_m)
        self.model_dropdown.pack(fill="x", padx=20, pady=(0, 15))

        # Confidence Slider
        self.conf_var = ctk.DoubleVar(value=float(self.config_data.get("confidence", 0.45)))
        self.create_slider(
            right_column,
            label="Detection Confidence Threshold:",
            variable=self.conf_var,
            from_=0.10,
            to=0.95,
            steps=85,
            command=self.on_conf_change
        )

        # Mouse Method Dropdown
        mouse_label = ctk.CTkLabel(right_column, text="Mouse Input Method:", font=ctk.CTkFont(size=13), text_color="#9ca3af")
        mouse_label.pack(anchor="w", padx=20, pady=(5, 2))

        self.mouse_dropdown = ctk.CTkOptionMenu(
            right_column,
            values=["ddxoft", "win32", "makcu"],
            command=self.on_mouse_method_change,
            fg_color="#27272a",
            button_color="#3f3f46",
            button_hover_color="#52525b"
        )
        self.mouse_dropdown.set(self.config_data.get("mouse_method", "ddxoft"))
        self.mouse_dropdown.pack(fill="x", padx=20, pady=(0, 15))

        # Switches Frame
        switches_frame = ctk.CTkFrame(right_column, fg_color="transparent")
        switches_frame.pack(fill="x", padx=20, pady=10)

        self.triggerbot_switch = ctk.CTkSwitch(
            switches_frame,
            text="Enable Auto Triggerbot",
            command=self.on_triggerbot_toggle,
            progress_color="#a78bfa"
        )
        if self.config_data.get("use_trigger_bot", True):
            self.triggerbot_switch.select()
        else:
            self.triggerbot_switch.deselect()
        self.triggerbot_switch.pack(anchor="w", pady=5)

        self.always_top_switch = ctk.CTkSwitch(
            switches_frame,
            text="Detection Screen Always On Top",
            command=self.on_always_top_toggle,
            progress_color="#a78bfa"
        )
        if self.config_data.get("always_on_top", True):
            self.always_top_switch.select()
        else:
            self.always_top_switch.deselect()
        self.always_top_switch.pack(anchor="w", pady=5)

        # --- FOOTER CONTROLS ---
        footer_frame = ctk.CTkFrame(self, fg_color="#1e1e24", corner_radius=12)
        footer_frame.pack(fill="x", padx=20, pady=(10, 20))

        info_label = ctk.CTkLabel(
            footer_frame,
            text="⌨ Hotkeys: [F1] Toggle Aimbot On/Off   •   [F2] Emergency Stop",
            font=ctk.CTkFont(size=12),
            text_color="#9ca3af"
        )
        info_label.pack(side="left", padx=20, pady=15)

        self.start_btn = ctk.CTkButton(
            footer_frame,
            text="▶ START AIMBOT",
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color="#10b981",
            hover_color="#059669",
            width=160,
            height=40,
            command=self.toggle_aimbot_running
        )
        self.start_btn.pack(side="right", padx=20, pady=15)

    def create_slider(self, parent, label, variable, from_, to, steps, command):
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.pack(fill="x", padx=20, pady=6)

        header = ctk.CTkFrame(frame, fg_color="transparent")
        header.pack(fill="x")

        lbl = ctk.CTkLabel(header, text=label, font=ctk.CTkFont(size=12), text_color="#9ca3af")
        lbl.pack(side="left")

        val_lbl = ctk.CTkLabel(header, text=f"{variable.get():.2f}" if isinstance(variable.get(), float) else f"{variable.get()}", font=ctk.CTkFont(size=12, weight="bold"), text_color="#a78bfa")
        val_lbl.pack(side="right")

        def _on_slider(val):
            if isinstance(variable, ctk.IntVar):
                val_lbl.configure(text=f"{int(val)}")
            else:
                val_lbl.configure(text=f"{val:.2f}")
            command(val)

        slider = ctk.CTkSlider(
            frame,
            from_=from_,
            to=to,
            number_of_steps=steps,
            variable=variable,
            command=_on_slider,
            button_color="#a78bfa",
            button_hover_color="#8b5cf6",
            progress_color="#6366f1"
        )
        slider.pack(fill="x", pady=(2, 0))

    def apply_config_to_aimbot(self):
        if not self.aimbot:
            return

        self.aimbot.smoothness = float(self.smoothness_var.get())
        self.aimbot.box_constant = int(self.fov_var.get())
        self.aimbot.conf = float(self.conf_var.get())
        self.aimbot.aim_height = int(self.aim_height_var.get())
        self.aimbot.use_trigger_bot = bool(self.triggerbot_switch.get())
        self.aimbot.always_on_top = bool(self.always_top_switch.get())

        m_method = self.mouse_dropdown.get()
        if self.aimbot.mouse_method != m_method:
            self.aimbot.mouse_method = m_method
            self.aimbot.init_mouse_driver()

        model_p = self.model_dropdown.get()
        if os.path.exists(model_p):
            self.aimbot.change_model(model_p)

        xy_sens = float(self.xy_sens_var.get())
        targeting_sens = float(self.targeting_sens_var.get())
        self.aimbot.sens_config = {
            "xy_sens": xy_sens,
            "targeting_sens": targeting_sens,
            "xy_scale": 10 / xy_sens if xy_sens > 0 else 2.0,
            "targeting_scale": 1000 / (targeting_sens * xy_sens) if (targeting_sens * xy_sens) > 0 else 20.0
        }

    def save_current_config(self):
        xy_sens = float(self.xy_sens_var.get())
        targeting_sens = float(self.targeting_sens_var.get())
        cfg = {
            "xy_sens": xy_sens,
            "targeting_sens": targeting_sens,
            "xy_scale": 10 / xy_sens if xy_sens > 0 else 2.0,
            "targeting_scale": 1000 / (targeting_sens * xy_sens) if (targeting_sens * xy_sens) > 0 else 20.0,
            "fov": int(self.fov_var.get()),
            "smoothness": round(float(self.smoothness_var.get()), 2),
            "confidence": round(float(self.conf_var.get()), 2),
            "aim_height": int(self.aim_height_var.get()),
            "use_trigger_bot": bool(self.triggerbot_switch.get()),
            "mouse_method": self.mouse_dropdown.get(),
            "always_on_top": bool(self.always_top_switch.get()),
            "selected_model": self.model_dropdown.get()
        }
        save_config(cfg)
        self.apply_config_to_aimbot()

    def on_smoothness_change(self, val):
        if self.aimbot:
            self.aimbot.smoothness = float(val)
        self.save_current_config()

    def on_fov_change(self, val):
        if self.aimbot:
            self.aimbot.box_constant = int(val)
        self.save_current_config()

    def on_sens_change(self, val):
        self.save_current_config()

    def on_aim_height_change(self, val):
        if self.aimbot:
            self.aimbot.aim_height = int(val)
        self.save_current_config()

    def on_conf_change(self, val):
        if self.aimbot:
            self.aimbot.conf = float(val)
        self.save_current_config()

    def on_model_select(self, val):
        if self.aimbot:
            self.aimbot.change_model(val)
        self.save_current_config()

    def on_mouse_method_change(self, val):
        if self.aimbot:
            self.aimbot.mouse_method = val
            self.aimbot.init_mouse_driver()
        self.save_current_config()

    def on_triggerbot_toggle(self):
        if self.aimbot:
            self.aimbot.use_trigger_bot = bool(self.triggerbot_switch.get())
        self.save_current_config()

    def on_always_top_toggle(self):
        if self.aimbot:
            self.aimbot.always_on_top = bool(self.always_top_switch.get())
            self.aimbot.set_always_on_top()
        self.save_current_config()

    def toggle_aimbot_running(self):
        if self.is_running:
            self.stop_aimbot()
        else:
            self.start_aimbot()

    def start_aimbot(self):
        if not self.aimbot:
            from lib.aimbot import Aimbot
            self.aimbot = Aimbot(
                box_constant=int(self.fov_var.get()),
                collect_data=False
            )
            self.apply_config_to_aimbot()

        self.is_running = True
        self.aimbot.is_running = True

        self.aimbot_thread = threading.Thread(target=self.aimbot.start, daemon=True)
        self.aimbot_thread.start()

        self.start_btn.configure(text="⏹ STOP AIMBOT", fg_color="#ef4444", hover_color="#dc2626")
        self.status_badge.configure(text="● RUNNING", text_color="#10b981")

    def stop_aimbot(self):
        if self.aimbot:
            self.aimbot.is_running = False

        self.is_running = False
        self.start_btn.configure(text="▶ START AIMBOT", fg_color="#10b981", hover_color="#059669")
        self.status_badge.configure(text="● STOPPED", text_color="#ef4444")

if __name__ == "__main__":
    app = LunarGUI()
    app.mainloop()
