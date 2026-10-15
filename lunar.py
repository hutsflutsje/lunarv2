import json
import os
import sys
from termcolor import colored

try:
    from pynput import keyboard
    has_pynput = True
except Exception:
    has_pynput = False

def on_release(key):
    try:
        if key == keyboard.Key.f1:
            Aimbot.update_status_aimbot()
        if key == keyboard.Key.f2:
            Aimbot.clean_up()
    except NameError:
        pass

def launch_gui(aimbot_instance=None):
    from lib.gui import LunarGUI
    app = LunarGUI(aimbot_instance=aimbot_instance)
    app.mainloop()

def main():
    global lunar
    lunar = Aimbot(collect_data = "collect_data" in sys.argv)
    if "cli" in sys.argv or "no_gui" in sys.argv:
        lunar.start()
    else:
        launch_gui(aimbot_instance=lunar)

def setup():
    path = "lib/config"
    if not os.path.exists(path):
        os.makedirs(path)

    print("[INFO] In-game X and Y axis sensitivity should be the same")
    def prompt(str):
        valid_input = False
        while not valid_input:
            try:
                number = float(input(str))
                valid_input = True
            except ValueError:
                print("[!] Invalid Input. Make sure to enter only the number (e.g. 6.9)")
        return number

    xy_sens = prompt("X-Axis and Y-Axis Sensitivity (from in-game settings): ")
    targeting_sens = prompt("Targeting Sensitivity (from in-game settings): ")

    print("[INFO] Your in-game targeting sensitivity must be the same as your scoping sensitivity")
    sensitivity_settings = {"xy_sens": xy_sens, "targeting_sens": targeting_sens, "xy_scale": 10/xy_sens, "targeting_scale": 1000/(targeting_sens * xy_sens)}

    with open('lib/config/config.json', 'w') as outfile:
        json.dump(sensitivity_settings, outfile)
    print("[INFO] Sensitivity configuration complete")

if __name__ == "__main__":
    os.system('cls' if os.name == 'nt' else 'clear')
    os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'

    print(colored(r'''

  _    _   _ _   _    _    ____     _     ___ _____ _____
 | |  | | | | \ | |  / \  |  _ \   | |   |_ _|_   _| ____|
 | |  | | | |  \| | / _ \ | |_) |  | |    | |  | | |  _|
 | |__| |_| | |\  |/ ___ \|  _ <   | |___ | |  | | | |___
 |_____\___/|_| \_/_/   \_\_| \_\  |_____|___| |_| |_____|

(Neural Network Aimbot)''', "green"))

    print(colored('To get full version of Lunar V2, visit https://gannonr.com/lunar OR join the discord: discord.gg/aiaimbot', "red"))

    path_exists = os.path.exists("lib/config/config.json")
    if not path_exists or ("setup" in sys.argv):
        if not path_exists:
            print("[!] Sensitivity configuration is not set. Launching initial setup...")
        setup()
    path_exists = os.path.exists("lib/data")
    if "collect_data" in sys.argv and not path_exists:
        os.makedirs("lib/data")
    from lib.aimbot import Aimbot
    if has_pynput:
        try:
            listener = keyboard.Listener(on_release=on_release)
            listener.start()
        except Exception as e:
            print(f"[!] Warning starting keyboard listener: {e}")
    main()
