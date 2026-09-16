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

        self.title("OptiScaler XeSS GUI — OptiXess")
        self.geometry("1180x820")
        self.minsize(1020, 720)
        self.configure(fg_color="#080D17")

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
        # 1. Top Window Header Matching Sample 1
        top_bar = ctk.CTkFrame(self, height=48, fg_color="#080D17", corner_radius=0)
        top_bar.pack(fill="x", side="top")

        # Left: Three Window Dots + Title
        brand_frame = ctk.CTkFrame(top_bar, fg_color="transparent")
        brand_frame.pack(side="left", padx=16, pady=8)

        dots_frame = ctk.CTkFrame(brand_frame, fg_color="transparent")
        dots_frame.pack(side="left", padx=(0, 14))

        for color in ["#C74C4C", "#D69E3D", "#3EA066"]:
            ctk.CTkLabel(dots_frame, text="●", font=ctk.CTkFont(size=13), text_color=color).pack(side="left", padx=2)

        title_lbl = ctk.CTkLabel(
            brand_frame,
            text="OptiScaler XeSS GUI — OptiXess",
            font=ctk.CTkFont(family="Consolas", size=13, weight="bold"),
            text_color="#85A3C2"
        )
        title_lbl.pack(side="left")

        # Right: Status Badges
        status_frame = ctk.CTkFrame(top_bar, fg_color="transparent")
        status_frame.pack(side="right", padx=16, pady=8)

        shield_lbl = ctk.CTkLabel(
            status_frame,
            text="Snapshot OK",
            font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
            text_color="#3ED598",
            fg_color="#0D2618",
            border_color="#246E45",
            border_width=1,
            corner_radius=6,
            padx=10,
            pady=3
        )
        shield_lbl.pack(side="right")

        # Hardware diagnostics badge
        hw_btn = ctk.CTkButton(
            status_frame,
            text=self.hw_info['badge_text'],
            font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
            fg_color="#0C2419" if self.hw_info['is_arc_detected'] else "#121A26",
            hover_color="#143625" if self.hw_info['is_arc_detected'] else "#1E2A3C",
            border_color="#1E6040" if self.hw_info['is_arc_detected'] else "#27384E",
            border_width=1,
            text_color="#34D399" if self.hw_info['is_arc_detected'] else "#B0B8C0",
            corner_radius=6,
            height=28,
            command=self._show_system_info
        )
        hw_btn.pack(side="right", padx=(0, 8))

        # Thin divider line
        divider = ctk.CTkFrame(self, height=1, fg_color="#142236", corner_radius=0)
        divider.pack(fill="x", side="top")

        # 2. Main Body: Sidebar (Left) + Content Area (Right)
        body_container = ctk.CTkFrame(self, fg_color="#080D17")
        body_container.pack(fill="both", expand=True)

        self.sidebar_frame = ctk.CTkFrame(body_container, width=140, fg_color="#080D17", corner_radius=0)
        self.sidebar_frame.pack(side="left", fill="y", padx=(10, 4), pady=10)
        self.sidebar_frame.pack_propagate(False)

        self.content_area = ctk.CTkFrame(body_container, fg_color="#080D17", corner_radius=0)
        self.content_area.pack(side="left", fill="both", expand=True, padx=(4, 10), pady=6)

        # Tabs creation
        self.tab_names = ["Library", "Downloads", "System Info", "Settings", "Log"]
        self.sidebar_buttons = {}

        for name in self.tab_names:
            btn = ctk.CTkButton(
                self.sidebar_frame,
                text=name,
                anchor="center",
                height=38,
                corner_radius=8,
                font=ctk.CTkFont(family="Segoe UI", size=12),
                command=lambda n=name: self.select_tab(n)
            )
            btn.pack(fill="x", pady=4)
            self.sidebar_buttons[name] = btn

        # Views creation inside content_area
        self.config_tab = ConfigTab(
            self.content_area,
            injector=self.injector,
            game_library=self.library,
            log_callback=lambda msg, lvl="info": self.log_console.log(msg, lvl),
            on_profile_updated=self._on_profile_updated,
            hw_info=self.hw_info
        )

        self.library_tab = LibraryTab(
            self.content_area,
            game_library=self.library,
            on_select_game=self._on_game_selected_from_library,
            log_callback=lambda msg, lvl="info": self.log_console.log(msg, lvl),
            hw_info=self.hw_info,
            on_show_system_info=self._show_system_info,
            on_force_inject=self._hero_force,
            on_install=self._hero_install,
            on_launch=self._hero_launch,
            on_revert=self._hero_revert
        )

        self.log_console = LogConsole(self.content_area, height=450)

        self.version_tab = VersionTab(
            self.content_area,
            version_manager=self.injector.version_manager,
            log_callback=self.log_console.log,
            on_versions_updated=self.config_tab.update_version_list
        )

        self.system_info_tab = self._build_system_info_view(self.content_area)

        # Tabview compatibility shim
        class _TabViewCompat:
            def __init__(self, main_win):
                self.main_win = main_win
            def set(self, name):
                mapping = {
                    "Game Library": "Library", "Library": "Library",
                    "Game Settings": "Settings", "Settings": "Settings",
                    "Downloads": "Downloads", "System Info": "System Info", "Log": "Log"
                }
                self.main_win.select_tab(mapping.get(name, name))
        self.tabview = _TabViewCompat(self)

        self.active_tab_name = None
        self.select_tab("Library")

    def select_tab(self, tab_name: str):
        """Switches the active view and updates sidebar button styles."""
        if tab_name == self.active_tab_name:
            return
        self.active_tab_name = tab_name

        # Update sidebar buttons appearance
        for name, btn in self.sidebar_buttons.items():
            if name == tab_name:
                btn.configure(
                    fg_color="#0E2238",
                    border_color="#00C7FD",
                    border_width=1.5,
                    text_color="#FFFFFF",
                    font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold")
                )
            else:
                btn.configure(
                    fg_color="transparent",
                    border_width=0,
                    text_color="#728DA6",
                    hover_color="#111E2E",
                    font=ctk.CTkFont(family="Segoe UI", size=12)
                )

        # Hide all view panels
        for widget in [self.library_tab, self.version_tab, self.system_info_tab, self.config_tab, self.log_console]:
            widget.pack_forget()

        # Show selected view panel
        tab_map = {
            "Library": self.library_tab,
            "Downloads": self.version_tab,
            "System Info": self.system_info_tab,
            "Settings": self.config_tab,
            "Log": self.log_console
        }
        active_widget = tab_map.get(tab_name, self.library_tab)
        active_widget.pack(fill="both", expand=True)

    def _build_system_info_view(self, parent):
        """Embeds dedicated System & Hardware diagnostics view."""
        frame = ctk.CTkFrame(parent, fg_color="#0B1322", corner_radius=12, border_width=1, border_color="#162A44")

        header = ctk.CTkFrame(frame, fg_color="transparent")
        header.pack(fill="x", padx=20, pady=(16, 8))

        ctk.CTkLabel(
            header,
            text="System & GPU Hardware Diagnostics",
            font=ctk.CTkFont(family="Segoe UI", size=18, weight="bold"),
            text_color="#00C7FD"
        ).pack(side="left")

        gpu = self.hw_info['primary_gpu']
        is_arc = self.hw_info['is_arc_detected']

        banner_color = "#0A2540" if is_arc else "#131C28"
        banner = ctk.CTkFrame(frame, fg_color=banner_color, corner_radius=8, border_width=1, border_color="#0071C5" if is_arc else "#2D3A50")
        banner.pack(fill="x", padx=20, pady=8)

        status_header = "⚡ Intel Arc GPU Active" if is_arc else f"🖥️ {gpu['vendor']} GPU Detected"
        ctk.CTkLabel(banner, text=status_header, font=ctk.CTkFont(size=14, weight="bold"), text_color="#00C7FD" if is_arc else "#E0E0E0").pack(anchor="w", padx=14, pady=(10, 2))
        sub_desc = "Dedicated Intel XMX AI Matrix Engines enabled for XeSS neural upscaling." if is_arc else f"XeSS running in {gpu['xess_acceleration']} mode."
        ctk.CTkLabel(banner, text=sub_desc, font=ctk.CTkFont(size=11), text_color="#A0AAB5", wraplength=600, justify="left").pack(anchor="w", padx=14, pady=(0, 10))

        grid = ctk.CTkFrame(frame, fg_color="#101A2B", corner_radius=8, border_width=1, border_color="#182C46")
        grid.pack(fill="x", padx=20, pady=8)

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
            r.pack(fill="x", padx=14, pady=4)
            ctk.CTkLabel(r, text=label, width=160, anchor="w", font=ctk.CTkFont(size=11, weight="bold"), text_color="#7A9ABD").pack(side="left")
            ctk.CTkLabel(r, text=val, anchor="w", font=ctk.CTkFont(family="Consolas", size=12), text_color="#E2EDF8").pack(side="left", fill="x", expand=True)

        rec_frame = ctk.CTkFrame(frame, fg_color="#0E1A29", corner_radius=8, border_width=1, border_color="#192F4A")
        rec_frame.pack(fill="x", padx=20, pady=12)
        ctk.CTkLabel(rec_frame, text="Tailored OptiScaler Configuration:", font=ctk.CTkFont(size=12, weight="bold"), text_color="#00C7FD").pack(anchor="w", padx=14, pady=(10, 4))
        notes = "• GPU Spoofing: Disabled (Protects Intel Arc against ray-tracing crashes)\n• XeSS Network: Auto (Optimal hardware selection)\n• XeLL Latency: Enabled (Reflex markers routed to Intel XeLL)"
        ctk.CTkLabel(rec_frame, text=notes, font=ctk.CTkFont(size=11), text_color="#8E9297", justify="left").pack(anchor="w", padx=14, pady=(0, 10))

        return frame

    def _hero_install(self):
        if self.library_tab.active_profile:
            self.config_tab.load_game(self.library_tab.active_profile)
            self.config_tab.apply_injection()

    def _hero_force(self):
        if self.library_tab.active_profile:
            self.config_tab.load_game(self.library_tab.active_profile)
            self.config_tab.force_injection()

    def _hero_launch(self):
        if self.library_tab.active_profile:
            self.config_tab.load_game(self.library_tab.active_profile)
            self.config_tab.launch_and_protect()

    def _hero_revert(self):
        if self.library_tab.active_profile:
            self.config_tab.load_game(self.library_tab.active_profile)
            self.config_tab.revert_changes()

    def _on_game_selected_from_library(self, profile: dict):
        """Called when user clicks 'Configure & Inject' on a game card."""
        self.config_tab.load_game(profile)
        self.library_tab.set_active_game(profile)
        self.select_tab("Settings")
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
