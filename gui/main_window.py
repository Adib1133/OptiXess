"""
Main Application Window for OptiScaler Per-Game Injector (Intel XeSS Edition).
Coordinates Game Library, Pipeline Configurator, Version Manager, and Log Console.
Handles graceful cleanup upon application shutdown.
"""

import os
import sys
import customtkinter as ctk

from core.injector import Injector
from core.library import GameLibrary
from core.hardware import HardwareDetector
from gui.library_tab import LibraryTab
from gui.config_tab import ConfigTab
from gui.version_tab import VersionTab
from gui.log_widget import LogConsole
from core.paths import prepare_assets, data_root, resource_root

class MainWindow(ctk.CTk):
    """Primary application GUI."""

    def __init__(self):
        super().__init__()

        # Appearance configuration
        ctk.set_appearance_mode("Dark")
        ctk.set_default_color_theme("blue")

        self.title("OptiScaler XeSS Suite — Game Configurator")
        self.geometry("1200x860")
        self.minsize(1020, 720)

        # Handle window close gracefully
        self.protocol("WM_DELETE_WINDOW", self._on_close)

        # Determine base directory (executable location when bundled)
        base_dir = str(resource_root())

        # Set application icon
        icon_path = os.path.join(base_dir, "assets", "icon.ico")
        if os.path.exists(icon_path):
            try:
                self.iconbitmap(icon_path)
            except Exception:
                pass

        # Core subsystems with persistent assets directory
        assets_dir = str(prepare_assets())
        self.injector = Injector(assets_dir=assets_dir)
        self.library = GameLibrary(str(data_root() / 'profiles.json'))
        self.hw_info = HardwareDetector.get_system_info()

        self._build_ui()

        # Initial logging
        self.log_console.log("OptiScaler Game Configurator initialized (Intel Arc Edition).", "info")
        self.log_console.log("Official Upstream: https://github.com/optiscaler/OptiScaler (v0.9.4+).", "info")
        gpu_name = self.hw_info['primary_gpu']['name']
        driver = self.hw_info['primary_gpu']['driver_version']
        self.log_console.log(f"Detected Hardware: {gpu_name} (Driver: {driver})", "info")
        if self.hw_info['is_arc_detected']:
            self.log_console.log("Intel Arc GPU recognized: XMX AI matrix acceleration active.", "success")
        else:
            self.log_console.log(f"Display adapter: {gpu_name} ({self.hw_info['primary_gpu']['xess_acceleration']}).", "info")
        self.log_console.log('Install files, then verify backend activation in the game overlay.', 'info')

    def _build_ui(self):
        # 1. Top Branding Header
        top_bar = ctk.CTkFrame(self, height=60, fg_color=("#1A1D24", "#11141A"), corner_radius=0)
        top_bar.pack(fill="x", side="top")

        # Logo / Title
        brand_frame = ctk.CTkFrame(top_bar, fg_color="transparent")
        brand_frame.pack(side="left", padx=20, pady=10)

        title_lbl = ctk.CTkLabel(
            brand_frame,
            text="OptiScaler  /  XeSS Studio",
            font=ctk.CTkFont(family="Segoe UI", size=16, weight="bold"),
            text_color="#00C7FD"
        )
        title_lbl.pack(anchor="w")

        sub_lbl = ctk.CTkLabel(
            brand_frame,
            text="Per-game proxy installation • Intel XeSS • Original-file recovery",
            font=ctk.CTkFont(family="Segoe UI", size=11),
            text_color="#8E9297"
        )
        sub_lbl.pack(anchor="w")

        # Status badge on right
        status_frame = ctk.CTkFrame(top_bar, fg_color="transparent")
        status_frame.pack(side="right", padx=20, pady=10)

        shield_lbl = ctk.CTkLabel(
            status_frame,
            text="Original-file recovery",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color="#3ED598",
            fg_color="#1E2B25",
            corner_radius=6,
            padx=10,
            pady=4
        )
        shield_lbl.pack(side="right")

        # Hardware diagnostics badge & click-to-view button
        hw_btn = ctk.CTkButton(
            status_frame,
            text=self.hw_info['badge_text'],
            font=ctk.CTkFont(size=11, weight="bold"),
            fg_color="#003B6F" if self.hw_info['is_arc_detected'] else "#1A2230",
            hover_color="#005A9E" if self.hw_info['is_arc_detected'] else "#273448",
            text_color="#00C7FD" if self.hw_info['is_arc_detected'] else "#B0B8C0",
            corner_radius=6,
            height=28,
            command=self._show_system_info
        )
        hw_btn.pack(side="right", padx=(0, 10))

        # 2. Bottom Live Diagnostic & Safety Console
        self.log_console = LogConsole(self, height=100)
        self.log_console.pack(fill="x", side="bottom", padx=12, pady=(0, 12))

        # 3. Middle Segmented Tabview
        self.tabview = ctk.CTkTabview(
            self,
            fg_color=("#12141A", "#0E1015"),
            segmented_button_selected_color="#0071C5",
            segmented_button_selected_hover_color="#005A9E",
            corner_radius=10
        )
        self.tabview.pack(fill="both", expand=True, padx=12, pady=(6, 8))

        tab_lib = self.tabview.add("Game Library")
        tab_config = self.tabview.add("Game Settings")
        tab_versions = self.tabview.add("Downloads")

        # Tab 1: Game Profile Library
        self.library_tab = LibraryTab(
            tab_lib,
            game_library=self.library,
            on_select_game=self._on_game_selected_from_library,
            log_callback=self.log_console.log
        )
        self.library_tab.pack(fill="both", expand=True)

        # Tab 2: Configurator & Injector
        self.config_tab = ConfigTab(
            tab_config,
            injector=self.injector,
            game_library=self.library,
            log_callback=self.log_console.log,
            on_profile_updated=self._on_profile_updated,
            hw_info=self.hw_info
        )
        self.config_tab.pack(fill="both", expand=True)

        # Tab 3: Version Manager & Downloader
        self.version_tab = VersionTab(
            tab_versions,
            version_manager=self.injector.version_manager,
            log_callback=self.log_console.log,
            on_versions_updated=self.config_tab.update_version_list
        )
        self.version_tab.pack(fill="both", expand=True)

    def _on_game_selected_from_library(self, profile: dict):
        """Called when user clicks 'Configure & Inject' on a game card."""
        self.config_tab.load_game(profile)
        self.tabview.set("Game Settings")
        self.log_console.log(f"Loaded profile: {profile['name']} ({profile['engine']})", "info")

    def _on_profile_updated(self):
        """Refreshes library card view after injection or configuration changes."""
        self.library_tab.refresh_library()

    def _on_close(self):
        """Cleanly stops running background threads upon exit."""
        if self.config_tab.busy or self.version_tab.busy or self.library_tab.scanning:
            from tkinter import messagebox
            messagebox.showinfo('Operation in progress', 'Wait for the current file operation to finish before closing.')
            return
        watchdog = self.config_tab.active_watchdog
        if watchdog:
            watchdog.stop()
            if watchdog._monitor_thread and watchdog._monitor_thread.is_alive():
                # Allow an in-flight recovery to finish instead of exiting its daemon thread.
                self.after(100, self._on_close)
                return
        self.config_tab.shutdown()
        self.version_tab.shutdown()
        self.library_tab.dispatcher.close()
        self.log_console.dispatcher.close()
        self.cancel_timers()
        self.destroy()

    def cancel_timers(self):
        # Includes CustomTkinter's recurring DPI/appearance callbacks.
        for timer in self.tk.splitlist(self.tk.call('after', 'info')):
            # Cancel scheduling only. Each owning widget destroys its own Tcl command.
            self.tk.call('after', 'cancel', timer)

    def _show_system_info(self):
        """Displays a dedicated System & Hardware Information modal dialog."""
        win = ctk.CTkToplevel(self)
        win.title("System & Hardware Diagnostics")
        win.geometry("560x510")
        win.resizable(False, False)
        win.transient(self)
        win.grab_set()

        # Center on parent window
        x = self.winfo_x() + max(0, (self.winfo_width() - 560) // 2)
        y = self.winfo_y() + max(0, (self.winfo_height() - 510) // 2)
        win.geometry(f"+{x}+{y}")

        frame = ctk.CTkFrame(win, fg_color="#0E1219", corner_radius=12)
        frame.pack(fill="both", expand=True, padx=16, pady=16)

        ctk.CTkLabel(
            frame,
            text="System & GPU Hardware Diagnostics",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="#00C7FD"
        ).pack(anchor="w", padx=16, pady=(14, 4))

        gpu = self.hw_info['primary_gpu']
        is_arc = self.hw_info['is_arc_detected']

        # Status badge banner
        banner_color = "#0A2540" if is_arc else "#131C28"
        banner = ctk.CTkFrame(frame, fg_color=banner_color, corner_radius=8, border_width=1, border_color="#0071C5" if is_arc else "#2D3A50")
        banner.pack(fill="x", padx=16, pady=8)

        status_header = "⚡ Intel Arc GPU Active" if is_arc else f"🖥️ {gpu['vendor']} GPU Detected"
        ctk.CTkLabel(banner, text=status_header, font=ctk.CTkFont(size=14, weight="bold"), text_color="#00C7FD" if is_arc else "#E0E0E0").pack(anchor="w", padx=12, pady=(10, 2))
        sub_desc = "Dedicated Intel XMX AI Matrix Engines enabled for XeSS neural upscaling." if is_arc else f"XeSS running in {gpu['xess_acceleration']} mode."
        ctk.CTkLabel(banner, text=sub_desc, font=ctk.CTkFont(size=11), text_color="#A0AAB5", wraplength=480, justify="left").pack(anchor="w", padx=12, pady=(0, 10))

        # Hardware Grid
        grid = ctk.CTkFrame(frame, fg_color="#121620", corner_radius=8)
        grid.pack(fill="x", padx=16, pady=4)

        rows = [
            ("Primary GPU:", gpu['name']),
            ("Driver Version:", gpu['driver_version']),
            ("Architecture:", gpu['architecture']),
            ("XeSS Acceleration:", gpu['xess_acceleration']),
            ("Processor (CPU):", self.hw_info['cpu']),
            ("System Memory:", f"{self.hw_info['ram_gb']} GB"),
            ("Operating System:", self.hw_info['os']),
        ]
        for label, val in rows:
            r = ctk.CTkFrame(grid, fg_color="transparent")
            r.pack(fill="x", padx=10, pady=3)
            ctk.CTkLabel(r, text=label, width=150, anchor="w", font=ctk.CTkFont(size=11, weight="bold"), text_color="#8E9297").pack(side="left")
            ctk.CTkLabel(r, text=val, anchor="w", font=ctk.CTkFont(size=11), text_color="#FFFFFF").pack(side="left", fill="x", expand=True)

        # OptiScaler Guidance Box
        rec_frame = ctk.CTkFrame(frame, fg_color="#141E28", corner_radius=8)
        rec_frame.pack(fill="x", padx=16, pady=8)
        ctk.CTkLabel(rec_frame, text="Tailored OptiScaler Configuration:", font=ctk.CTkFont(size=11, weight="bold"), text_color="#00C7FD").pack(anchor="w", padx=12, pady=(8, 2))
        notes = "• GPU Spoofing: Disabled (Protects Intel Arc against ray-tracing crashes)\n• XeSS Network: Auto (Optimal hardware selection)\n• XeLL Latency: Enabled (Reflex markers routed to Intel XeLL)"
        ctk.CTkLabel(rec_frame, text=notes, font=ctk.CTkFont(size=10), text_color="#8E9297", justify="left").pack(anchor="w", padx=12, pady=(0, 8))

        ctk.CTkButton(frame, text="Close", width=120, fg_color="#0071C5", hover_color="#005A9E", command=win.destroy).pack(side="bottom", pady=10)
