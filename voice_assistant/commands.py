import ctypes
import os
import platform
import subprocess
import webbrowser
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from urllib.parse import quote_plus

import pyautogui


@dataclass(frozen=True)
class CommandResult:
    message: str
    should_exit: bool = False
    confirmation: str | None = None


APP_COMMANDS = {
    "notepad": "notepad.exe",
    "calculator": "calc.exe",
    "file explorer": "explorer.exe",
    "explorer": "explorer.exe",
    "paint": "mspaint.exe",
    "task manager": "taskmgr.exe",
}

KEY_ALIASES = {
    "return": "enter",
    "escape": "esc",
    "spacebar": "space",
    "control": "ctrl",
    "windows": "win",
    "windows key": "win",
}

ALLOWED_KEYS = set("abcdefghijklmnopqrstuvwxyz0123456789") | {
    "enter", "tab", "esc", "space", "backspace", "delete", "home", "end",
    "pageup", "pagedown", "up", "down", "left", "right", "f1", "f2", "f3",
    "f4", "f5", "f6", "f7", "f8", "f9", "f10", "f11", "f12", "ctrl",
    "alt", "shift", "win",
}


def _press_volume_key(virtual_key):
    user32 = ctypes.windll.user32
    key_up = 0x0002
    user32.keybd_event(virtual_key, 0, 0, 0)
    user32.keybd_event(virtual_key, 0, key_up, 0)


def _normalize_key(key):
    key = key.strip().lower()
    return KEY_ALIASES.get(key, key)


def _save_screenshot():
    screenshot_dir = Path.home() / "Pictures" / "SoraScreenshots"
    screenshot_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S-%f")
    screenshot_path = screenshot_dir / f"sora-{timestamp}.png"
    pyautogui.screenshot().save(screenshot_path)
    return screenshot_path


def _search_windows_for_app(app_name):
    pyautogui.hotkey("win", "s")
    pyautogui.sleep(0.6)
    pyautogui.write(app_name, interval=0.04)
    pyautogui.sleep(0.8)
    pyautogui.press("enter")


def execute_command(command):
    """Run a supported desktop action; potentially destructive power actions need approval."""
    raw_command = command.strip()
    normalized = " ".join(raw_command.lower().split())
    if not normalized:
        return CommandResult("Please say or type a command.")

    if normalized in {"exit", "quit", "close assistant", "stop assistant"}:
        return CommandResult("Goodbye.", should_exit=True)

    for prefix in ("search for ", "search ", "google "):
        if normalized.startswith(prefix):
            query = normalized[len(prefix):].strip()
            if not query:
                return CommandResult("Tell me what you want to search for.")
            webbrowser.open(f"https://www.google.com/search?q={quote_plus(query)}")
            return CommandResult(f"Searching the web for {query}.")

    if normalized in {"open browser", "open the browser", "open web browser"}:
        webbrowser.open("about:blank")
        return CommandResult("Opening your default browser.")

    if normalized.startswith("go to "):
        address = raw_command[6:].strip()
        if not address:
            return CommandResult("Tell me which website to open.")
        if "://" not in address:
            address = f"https://{address}"
        if not address.lower().startswith(("https://", "http://")):
            return CommandResult("I can only open HTTP or HTTPS websites.")
        webbrowser.open(address)
        return CommandResult(f"Opening {address}.")

    for prefix in ("open ", "launch ", "start "):
        if normalized.startswith(prefix):
            app_name = normalized[len(prefix):].strip()
            for article in ("the ", "a ", "an "):
                if app_name.startswith(article):
                    app_name = app_name[len(article):]
                    break
            if not app_name:
                return CommandResult("Say the name of the app you want to open.")
            if app_name in APP_COMMANDS:
                subprocess.Popen([APP_COMMANDS[app_name]])
                return CommandResult(f"Opening {app_name}.")
            if app_name == "settings":
                if platform.system() != "Windows":
                    return CommandResult("Opening Settings is available on Windows only.")
                os.startfile("ms-settings:")
                return CommandResult("Opening Windows Settings.")
            if app_name in {"browser", "web browser"}:
                webbrowser.open("about:blank")
                return CommandResult("Opening your default browser.")
            if platform.system() == "Windows":
                _search_windows_for_app(app_name)
                return CommandResult(f"Searching Windows for {app_name}.")
            return CommandResult("Opening apps by name from the Start menu is available on Windows only.")

    if normalized in {"click", "left click", "click here"}:
        pyautogui.click()
        return CommandResult("Clicking at the current pointer position.")
    if normalized in {"double click", "double-click"}:
        pyautogui.doubleClick()
        return CommandResult("Double-clicking at the current pointer position.")
    if normalized in {"right click", "right-click"}:
        pyautogui.rightClick()
        return CommandResult("Right-clicking at the current pointer position.")

    mouse_moves = {
        "move mouse left": (-120, 0),
        "move mouse right": (120, 0),
        "move mouse up": (0, -120),
        "move mouse down": (0, 120),
    }
    if normalized in mouse_moves:
        x_offset, y_offset = mouse_moves[normalized]
        pyautogui.moveRel(x_offset, y_offset, duration=0.2)
        return CommandResult("Moving the mouse pointer.")

    if normalized.startswith("type "):
        text = raw_command[5:]
        if not text:
            return CommandResult("Tell me what text to type.")
        pyautogui.write(text, interval=0.02)
        return CommandResult("Typing your text into the focused app.")

    if normalized.startswith("press "):
        key = _normalize_key(normalized[6:])
        if key not in ALLOWED_KEYS:
            return CommandResult("That key is not supported. Try Enter, Tab, Escape, an arrow, or a letter.")
        pyautogui.press(key)
        return CommandResult(f"Pressing {key}.")

    if normalized.startswith("hotkey "):
        keys = [_normalize_key(key) for key in normalized[7:].replace("+", " ").split()]
        if len(keys) < 2 or any(key not in ALLOWED_KEYS for key in keys):
            return CommandResult("Try a supported shortcut such as hotkey control c.")
        pyautogui.hotkey(*keys)
        return CommandResult("Sending the keyboard shortcut.")

    shortcuts = {
        "copy": ("ctrl", "c"),
        "paste": ("ctrl", "v"),
        "cut": ("ctrl", "x"),
        "select all": ("ctrl", "a"),
        "undo": ("ctrl", "z"),
        "redo": ("ctrl", "y"),
        "save": ("ctrl", "s"),
        "new tab": ("ctrl", "t"),
        "close tab": ("ctrl", "w"),
        "next tab": ("ctrl", "tab"),
        "previous tab": ("ctrl", "shift", "tab"),
        "switch window": ("alt", "tab"),
        "show desktop": ("win", "d"),
        "maximize window": ("win", "up"),
        "minimize window": ("win", "down"),
    }
    if normalized in shortcuts:
        pyautogui.hotkey(*shortcuts[normalized])
        return CommandResult(f"{normalized.capitalize()}.")

    if normalized in {"scroll up", "page up"}:
        if normalized == "scroll up":
            pyautogui.scroll(5)
        else:
            pyautogui.press("pageup")
        return CommandResult("Scrolling up.")
    if normalized in {"scroll down", "page down"}:
        if normalized == "scroll down":
            pyautogui.scroll(-5)
        else:
            pyautogui.press("pagedown")
        return CommandResult("Scrolling down.")

    navigation = {
        "go back": ("left", "Going back."),
        "back": ("left", "Going back."),
        "go forward": ("right", "Going forward."),
        "forward": ("right", "Going forward."),
    }
    if normalized in navigation:
        key, response = navigation[normalized]
        pyautogui.hotkey("alt", key)
        return CommandResult(response)
    if normalized in {"go home", "home"}:
        pyautogui.hotkey("alt", "home")
        return CommandResult("Going to the browser home page.")

    if normalized in {"take screenshot", "screenshot", "capture screen"}:
        screenshot_path = _save_screenshot()
        return CommandResult(f"Screenshot saved to {screenshot_path}.")

    if normalized in {"lock pc", "lock computer", "lock screen"}:
        if platform.system() != "Windows":
            return CommandResult("Locking the computer is currently supported on Windows only.")
        ctypes.windll.user32.LockWorkStation()
        return CommandResult("Locking your computer.")

    if normalized in {"shut down pc", "shutdown pc", "shut down computer", "turn off pc"}:
        return CommandResult("Confirm Windows shutdown in the dialog.", confirmation="shutdown")
    if normalized in {"restart pc", "restart computer"}:
        return CommandResult("Confirm Windows restart in the dialog.", confirmation="restart")

    if normalized in {"volume up", "increase volume", "turn volume up"}:
        if platform.system() != "Windows":
            return CommandResult("Volume controls are currently supported on Windows only.")
        _press_volume_key(0xAF)
        return CommandResult("Increasing volume.")
    if normalized in {"volume down", "decrease volume", "turn volume down"}:
        if platform.system() != "Windows":
            return CommandResult("Volume controls are currently supported on Windows only.")
        _press_volume_key(0xAE)
        return CommandResult("Decreasing volume.")
    if normalized in {"mute", "mute volume", "toggle mute"}:
        if platform.system() != "Windows":
            return CommandResult("Volume controls are currently supported on Windows only.")
        _press_volume_key(0xAD)
        return CommandResult("Toggling mute.")

    return CommandResult(
        "I did not recognize that. Try open app, search, go to website, click, type text, press a key, switch window, screenshot, scroll, or volume."
    )


def confirm_pending_action(action, approved):
    if not approved:
        return CommandResult(f"Cancelled {action}.")
    if platform.system() != "Windows":
        return CommandResult("Power actions are currently supported on Windows only.")

    power_commands = {
        "shutdown": ["shutdown.exe", "/s", "/t", "10"],
        "restart": ["shutdown.exe", "/r", "/t", "10"],
    }
    if action not in power_commands:
        return CommandResult("That confirmation action is not supported.")
    subprocess.Popen(power_commands[action])
    return CommandResult(f"Windows will {action} in 10 seconds. Run shutdown /a in a terminal to cancel.")