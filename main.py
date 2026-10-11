import tkinter as tk
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from threading import Thread
from tkinter import messagebox

from voice_assistant.commands import confirm_pending_action, execute_command
from voice_assistant.speech import SpeechInput, speak_text


class AssistantApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Sora Voice Assistant")
        self.root.geometry("760x620")
        self.root.minsize(620, 520)
        self.root.configure(bg="#101c1a")
        self.speech_input = SpeechInput()
        self.speech_executor = ThreadPoolExecutor(max_workers=1)
        self.speak_responses = tk.BooleanVar(value=True)

        self._build_ui()
        self.root.protocol("WM_DELETE_WINDOW", self.close)

    def _build_ui(self):
        header = tk.Frame(self.root, bg="#101c1a", padx=28, pady=22)
        header.pack(fill="x")

        tk.Label(
            header,
            text="SORA",
            font=("Segoe UI", 11, "bold"),
            fg="#91d6bd",
            bg="#101c1a",
        ).pack(anchor="w")
        tk.Label(
            header,
            text="Voice assistant",
            font=("Segoe UI", 25, "bold"),
            fg="#f2f5ed",
            bg="#101c1a",
        ).pack(anchor="w", pady=(5, 2))
        tk.Label(
            header,
            text="Control common PC actions with your voice or keyboard.",
            font=("Segoe UI", 10),
            fg="#aabbb3",
            bg="#101c1a",
        ).pack(anchor="w")

        body = tk.Frame(self.root, bg="#172623", padx=20, pady=18)
        body.pack(fill="both", expand=True, padx=22, pady=(0, 20))

        toolbar = tk.Frame(body, bg="#172623")
        toolbar.pack(fill="x")
        self.listen_button = tk.Button(
            toolbar,
            text="Start listening",
            command=self.start_listening,
            font=("Segoe UI", 10, "bold"),
            bg="#91d6bd",
            fg="#10221d",
            activebackground="#b0ead4",
            relief="flat",
            padx=15,
            pady=9,
            cursor="hand2",
        )
        self.listen_button.pack(side="left")
        tk.Checkbutton(
            toolbar,
            text="Speak responses",
            variable=self.speak_responses,
            font=("Segoe UI", 9),
            fg="#d7e3dc",
            selectcolor="#172623",
            activebackground="#172623",
            activeforeground="#d7e3dc",
            bg="#172623",
        ).pack(side="right")

        self.status = tk.StringVar(value="Ready")
        tk.Label(
            body,
            textvariable=self.status,
            font=("Segoe UI", 9),
            fg="#91d6bd",
            bg="#172623",
        ).pack(anchor="w", pady=(12, 8))

        self.history = tk.Text(
            body,
            height=14,
            wrap="word",
            state="disabled",
            font=("Segoe UI", 10),
            bg="#0e1816",
            fg="#e3ece6",
            insertbackground="#e3ece6",
            relief="flat",
            padx=14,
            pady=12,
            spacing1=3,
            spacing3=7,
        )
        self.history.pack(fill="both", expand=True)
        self.history.tag_configure("time", foreground="#91d6bd")
        self.history.tag_configure("user", foreground="#f0bd7a")

        input_row = tk.Frame(body, bg="#172623")
        input_row.pack(fill="x", pady=(14, 0))
        self.command_entry = tk.Entry(
            input_row,
            font=("Segoe UI", 11),
            bg="#f2f5ed",
            fg="#15221e",
            relief="flat",
            insertbackground="#15221e",
        )
        self.command_entry.pack(side="left", fill="x", expand=True, ipady=10, padx=(0, 8))
        self.command_entry.bind("<Return>", self.submit_typed_command)
        tk.Button(
            input_row,
            text="Send",
            command=self.submit_typed_command,
            font=("Segoe UI", 10, "bold"),
            bg="#e6a55f",
            fg="#24180d",
            activebackground="#f2bd82",
            relief="flat",
            padx=18,
            pady=8,
            cursor="hand2",
        ).pack(side="right")

        tk.Label(
            body,
            text="Try: click  |  type Hello  |  press Enter  |  switch window  |  take screenshot",
            font=("Segoe UI", 9),
            fg="#aabbb3",
            bg="#172623",
        ).pack(anchor="w", pady=(12, 0))

    def _append_history(self, speaker, text):
        self.history.configure(state="normal")
        timestamp = datetime.now().strftime("%H:%M")
        self.history.insert("end", f"{timestamp}  ", "time")
        self.history.insert("end", f"{speaker}: ", "user" if speaker == "You" else "time")
        self.history.insert("end", f"{text}\n")
        self.history.see("end")
        self.history.configure(state="disabled")

    def start_listening(self):
        self.listen_button.configure(state="disabled", text="Listening...")
        self.status.set("Listening for one command...")
        Thread(target=self._listen_in_background, daemon=True).start()

    def _listen_in_background(self):
        try:
            recognized_text = self.speech_input.listen_once()
            self.root.after(0, self._on_listening_finished, recognized_text, None)
        except Exception as error:
            self.root.after(0, self._on_listening_finished, None, str(error))

    def _on_listening_finished(self, recognized_text, error):
        self.listen_button.configure(state="normal", text="Start listening")
        if error:
            self.status.set("Could not hear a command")
            self._append_history("Assistant", error)
            return
        self.command_entry.delete(0, "end")
        self.command_entry.insert(0, recognized_text)
        self._run_command(recognized_text)

    def submit_typed_command(self, _event=None):
        command = self.command_entry.get().strip()
        self.command_entry.delete(0, "end")
        self._run_command(command)

    def _run_command(self, command):
        if not command:
            return
        self._append_history("You", command)
        try:
            result = execute_command(command)
            if result.confirmation:
                action = result.confirmation
                approved = messagebox.askyesno(
                    "Confirm PC action",
                    f"Are you sure you want to {action} Windows?",
                    parent=self.root,
                )
                result = confirm_pending_action(action, approved)
        except Exception as error:
            self.status.set("Action failed")
            self._append_history("Assistant", f"Action failed: {error}")
            return
        self._append_history("Assistant", result.message)
        self.status.set("Ready")
        if self.speak_responses.get():
            self.speech_executor.submit(speak_text, result.message)
        if result.should_exit:
            self.root.after(600, self.close)

    def close(self):
        self.speech_executor.shutdown(wait=False, cancel_futures=True)
        self.root.destroy()


def main():
    root = tk.Tk()
    try:
        AssistantApp(root)
    except Exception as error:
        messagebox.showerror("Could not start assistant", str(error))
        root.destroy()
        return
    root.mainloop()


if __name__ == "__main__":
    main()