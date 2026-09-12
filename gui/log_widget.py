"""
Live Diagnostic Logging Console Widget.
Displays real-time logs, injection telemetry, and watchdog crash diagnostics.
"""

import time
import customtkinter as ctk
import tkinter as tk
import logging
from gui.dispatch import UIDispatcher

class LogConsole(ctk.CTkFrame):
    """Real-time scrolling terminal console for injection & safety logs."""

    def __init__(self, master, **kwargs):
        super().__init__(master, fg_color=("#1A1D24", "#15181F"), corner_radius=10, **kwargs)

        self._build_ui()
        self.dispatcher = UIDispatcher(self)

    def _build_ui(self):
        # Header bar
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=12, pady=(10, 4))

        title = ctk.CTkLabel(
            header,
            text="LIVE DIAGNOSTIC & SAFETY CONSOLE",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color="#A0A5B0"
        )
        title.pack(side="left")

        btn_frame = ctk.CTkFrame(header, fg_color="transparent")
        btn_frame.pack(side="right")

        clear_btn = ctk.CTkButton(
            btn_frame,
            text="Clear",
            width=50,
            height=22,
            font=ctk.CTkFont(size=10),
            fg_color="#2A2E38",
            hover_color="#3A3F4C",
            command=self.clear_logs
        )
        clear_btn.pack(side="right", padx=2)

        # Text widget for logs
        self.text_area = ctk.CTkTextbox(
            self,
            font=ctk.CTkFont(family="Consolas", size=11),
            fg_color="#0F1116",
            text_color="#D8DEE9",
            corner_radius=6,
            wrap="word", height=55
        )
        self.text_area.pack(fill="both", expand=True, padx=12, pady=(4, 10))
        self.text_area.configure(state="disabled")

    def log(self, message: str, level: str = "info"):
        """Thread-safe logging method that marshals to Tkinter UI loop."""
        logging.getLogger('optiscaler_gui').log(logging.ERROR if level in ('error', 'crash') else logging.INFO, message)
        self.dispatcher.post(self._append_log, message, level)

    def _append_log(self, message: str, level: str = "info"):
        timestamp = time.strftime("%H:%M:%S")
        prefix = {
            "info": "[INFO]",
            "success": "[SUCCESS]",
            "warning": "[WARN]",
            "error": "[ERROR]",
            "crash": "[CRASH DETECTED]"
        }.get(level.lower(), "[INFO]")

        entry = f"{timestamp} {prefix} {message}\n"
        try:
            self.text_area.configure(state="normal")
            self.text_area.insert("end", entry)
            self.text_area.see("end")
            self.text_area.configure(state="disabled")
        except Exception:
            pass

    def clear_logs(self):
        """Clears the console."""
        try:
            self.text_area.configure(state="normal")
            self.text_area.delete("1.0", "end")
            self.text_area.configure(state="disabled")
        except Exception:
            pass
