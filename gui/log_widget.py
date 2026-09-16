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
        super().__init__(master, fg_color="#0B1322", border_color="#162A44", border_width=1, corner_radius=12, **kwargs)

        self._build_ui()
        self.dispatcher = UIDispatcher(self)

    def _build_ui(self):
        # Header bar
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=16, pady=(14, 6))

        title = ctk.CTkLabel(
            header,
            text="LIVE DIAGNOSTIC & SAFETY CONSOLE",
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
            text_color="#00C7FD"
        )
        title.pack(side="left")

        btn_frame = ctk.CTkFrame(header, fg_color="transparent")
        btn_frame.pack(side="right")

        clear_btn = ctk.CTkButton(
            btn_frame,
            text="Clear",
            width=60,
            height=26,
            font=ctk.CTkFont(size=11),
            fg_color="#0F1D2E",
            border_color="#1A3452",
            border_width=1,
            text_color="#7A9CBD",
            hover_color="#162D46",
            corner_radius=6,
            command=self.clear_logs
        )
        clear_btn.pack(side="right", padx=2)

        # Text widget for logs
        self.text_area = ctk.CTkTextbox(
            self,
            font=ctk.CTkFont(family="Consolas", size=11),
            fg_color="#080D17",
            text_color="#D8DEE9",
            corner_radius=8,
            wrap="word"
        )
        self.text_area.pack(fill="both", expand=True, padx=16, pady=(4, 16))
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
