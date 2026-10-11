# Sora Voice Assistant

A beginner-friendly Windows desktop voice assistant. It can open selected apps, browse and search the web, control the mouse and keyboard in the focused window, manage common windows and tabs, take screenshots, scroll, change volume, and lock the PC. You can also type commands if you do not have a microphone.

## 1. Install the tools

1. Install **Python 3.12, 64-bit** from [python.org](https://www.python.org/downloads/). During installation, enable **Add Python to PATH**.
2. Install [Visual Studio Code](https://code.visualstudio.com/).
3. In VS Code, open the `c:\hackathon` folder and install the Microsoft **Python** extension.
4. Open **Terminal > New Terminal** in VS Code.

Check the Python launcher:

```powershell
py -3.12 --version
```

It should print `Python 3.12.x`. This project uses Python 3.12 because audio dependencies may not yet support newer preview versions.

## 2. Create the virtual environment

Run these commands in the VS Code PowerShell terminal, one at a time:

```powershell
cd c:\hackathon
py -3.12 -m venv .venv
```

Activate it:

```powershell
.\.venv\Scripts\Activate.ps1
```

If PowerShell blocks activation, run this once in that terminal and activate again:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

The terminal prompt should now begin with `(.venv)`.

## 3. Install the libraries

```powershell
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Libraries used:

- `SpeechRecognition` listens to the microphone and turns speech into text.
- `PyAudio` connects Python to the microphone.
- `pyttsx3` reads responses aloud using a local speech engine.
- `PyAutoGUI` sends scrolling and navigation key presses.
- `tkinter`, `subprocess`, `webbrowser`, and `ctypes` are included with Python or the Windows standard library.

If installing `PyAudio` fails, confirm you installed 64-bit Python 3.12, then retry the install command. Do not install packages into the system Python; keep the `.venv` active.

## 4. Run the assistant

```powershell
python main.py
```

Click **Start listening**, speak one command, and wait for the result. You can also type a command in the box and press Enter or click **Send**.

## Commands to try

- `open notepad`
- `open calculator`
- `open file explorer`
- `open paint`
- `open task manager`
- `open settings`
- `open browser` or `open the browser` (default browser)
- `open chrome`, `open the chrome`, or `open Spotify` (searches Windows for the installed app)
- `go to wikipedia.org`
- `search for python tutorials`
- `move mouse left` or `move mouse down`
- `click`, `double click`, or `right click`
- `type Hello there` or `press enter`
- `hotkey control c`, `copy`, `paste`, `undo`, or `save`
- `switch window`, `show desktop`, `maximize window`, or `minimize window`
- `new tab`, `next tab`, `previous tab`, or `close tab`
- `scroll down` or `scroll up`
- `page down` or `page up`
- `go back`, `go forward`, or `go home`
- `volume up`, `volume down`, or `mute`
- `take screenshot` or `lock pc`
- `shut down pc` or `restart pc` (requires clicking Yes in a confirmation dialog)
- `exit` or `close assistant`

Mouse, typing, scrolling, and keyboard commands affect the currently focused window. Speak commands carefully: `click`, `type`, and shortcuts immediately interact with the active app. Apps not listed above are looked up through Windows Search and must be installed/searchable there. Shutdown and restart require an on-screen confirmation and start after a 10-second delay. The assistant does not run arbitrary spoken text as a terminal command.

Screenshots are saved to `Pictures\SoraScreenshots` in your Windows user folder. The `type ...` command types into the focused app; avoid using it while a password or private field is focused.

## Project files

```text
c:\hackathon
|-- main.py                       # Tkinter window and button/input handling
|-- requirements.txt              # Python packages to install
|-- voice_assistant
|   |-- __init__.py
|   |-- commands.py               # Maps recognized phrases to safe PC actions
|   `-- speech.py                 # Microphone recognition and spoken responses
`-- README.md                     # Setup and usage guide
```

## Important notes

- Google speech recognition requires an internet connection and sends recorded speech to Google's recognition service. Typed commands do not need that service.
- Spoken responses use the computer's local speech engine.
- Windows may ask you to allow microphone access. Enable it in **Settings > Privacy & security > Microphone**.
- Some antivirus or managed-PC policies may block automation. Only use this assistant on a computer where you are allowed to control apps and keyboard input.
- To stop, type `exit`, say `close assistant`, or close the window.

## Common fixes

- **`No module named ...`**: activate `.venv` and run `python -m pip install -r requirements.txt` again.
- **Microphone unavailable**: check Windows microphone privacy settings and the selected input device.
- **Speech service unavailable**: check the internet connection, or use the typed command box.
- **Volume action does nothing**: confirm Windows is the active operating system and try the keyboard's volume keys.