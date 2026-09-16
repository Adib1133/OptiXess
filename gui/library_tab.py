"""
Game Profile Library View (Intel Arc Signature Styling).
Provides game discovery, search, filtering, shortcut (.lnk) support,
deep recursive upscaler folder indicators, status badges, and selection.
"""

import os
from typing import Callable, List, Optional
import customtkinter as ctk
from tkinter import filedialog, messagebox
from gui.dispatch import UIDispatcher

class LibraryTab(ctk.CTkFrame):
    """Intel Arc Styled View presenting the user's game library and quick injection status."""

    def __init__(self, master, game_library, on_select_game: Callable[[dict], None], log_callback: Callable[[str, str], None],
                 hw_info=None, on_show_system_info=None, on_force_inject=None, on_install=None, on_launch=None, on_revert=None, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)

        self.library = game_library
        self.on_select_game = on_select_game
        self.log = log_callback
        self.hw_info = hw_info or {"badge_text": "Arc GPU • XMX", "is_arc_detected": True}
        self.on_show_system_info = on_show_system_info
        self.on_force_inject = on_force_inject
        self.on_install = on_install
        self.on_launch = on_launch
        self.on_revert = on_revert
        self.active_profile = None
        self.search_term = ""
        self.dispatcher = UIDispatcher(self)
        self.scanning = False

        self._build_ui()
        self.refresh_library()

    def _build_ui(self):
        # ── 1. Hero Card Matching UI Sample 1 ──────────────────────────────────
        hero = ctk.CTkFrame(self, fg_color="#0B1322", corner_radius=12, border_width=1, border_color="#162A44")
        hero.pack(fill="x", padx=14, pady=(10, 8))

        # Field builder helper
        def make_field(label_text, default_value):
            field = ctk.CTkFrame(hero, fg_color="#101C2E", corner_radius=8, border_width=1, border_color="#182C46", height=38)
            field.pack(fill="x", padx=16, pady=4)
            field.pack_propagate(False)
            ctk.CTkLabel(
                field, text=label_text, width=80, anchor="w",
                font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
                text_color="#7A9ABD"
            ).pack(side="left", padx=14)
            val_lbl = ctk.CTkLabel(
                field, text=default_value, anchor="e",
                font=ctk.CTkFont(family="Consolas", size=13, weight="bold"),
                text_color="#E2EDF8"
            )
            val_lbl.pack(side="right", padx=14)
            return val_lbl

        self.hero_game_lbl = make_field("Game", "Marvel's Spider-Man 2")
        self.hero_proxy_lbl = make_field("Proxy", "dxgi.dll")
        self.hero_upscaler_lbl = make_field("Upscaler", "XeSS SR • Quality")

        # Badges row: [ XeSS SR ]  [ XeFG ]  [ Snapshot OK ]
        badges_row = ctk.CTkFrame(hero, fg_color="transparent")
        badges_row.pack(fill="x", padx=16, pady=(8, 4))

        self.badge_xess = ctk.CTkLabel(
            badges_row, text="XeSS SR",
            font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
            fg_color="#0D2235", border_color="#00A2E8", border_width=1,
            text_color="#38C8F8", corner_radius=6, padx=12, pady=4
        )
        self.badge_xess.pack(side="left", padx=(0, 8))

        self.badge_xefg = ctk.CTkLabel(
            badges_row, text="XeFG",
            font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
            fg_color="#10243C", border_color="#1B5E94", border_width=1,
            text_color="#5CA4E8", corner_radius=6, padx=12, pady=4
        )
        self.badge_xefg.pack(side="left", padx=(0, 8))

        self.badge_snapshot = ctk.CTkLabel(
            badges_row, text="Snapshot OK",
            font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
            fg_color="#0D2618", border_color="#246E45", border_width=1,
            text_color="#3ED598", corner_radius=6, padx=12, pady=4
        )
        self.badge_snapshot.pack(side="left")

        # Glowing Neon Cyan Progress bar
        self.hero_progress = ctk.CTkProgressBar(
            hero, fg_color="#101E30", progress_color="#00C7FD",
            height=6, corner_radius=3
        )
        self.hero_progress.set(0.65)
        self.hero_progress.pack(fill="x", padx=16, pady=(10, 8))

        # Bottom Action Row: [ Force Inject ] [ Arc A770 • XMX ] ... [ Install / Update ] [ Launch ] [ Revert ]
        action_row = ctk.CTkFrame(hero, fg_color="transparent")
        action_row.pack(fill="x", padx=16, pady=(0, 12))

        # Left action pills
        self.btn_force = ctk.CTkButton(
            action_row, text="Force Inject",
            font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
            fg_color="#261608", hover_color="#38200C",
            border_color="#A06020", border_width=1,
            text_color="#F59E0B", corner_radius=6, height=32, width=110,
            command=self._on_hero_force
        )
        self.btn_force.pack(side="left", padx=(0, 8))

        hw_text = self.hw_info.get('badge_text', 'Arc A770 • XMX')
        self.btn_hw = ctk.CTkButton(
            action_row, text=hw_text,
            font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
            fg_color="#0C2419", hover_color="#143625",
            border_color="#1E6040", border_width=1,
            text_color="#34D399", corner_radius=6, height=32, width=120,
            command=self._on_hero_hw
        )
        self.btn_hw.pack(side="left")

        # Right control buttons
        self.btn_install = ctk.CTkButton(
            action_row, text="Install / Update",
            font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
            fg_color="#0071C5", hover_color="#005A9E",
            text_color="#FFFFFF", corner_radius=6, height=32, width=125,
            command=self._on_hero_install
        )
        self.btn_install.pack(side="right", padx=(6, 0))

        self.btn_launch = ctk.CTkButton(
            action_row, text="Launch",
            font=ctk.CTkFont(family="Segoe UI", size=11),
            fg_color="#121D2C", hover_color="#1B2B40",
            border_color="#1D3652", border_width=1,
            text_color="#8AB4D8", corner_radius=6, height=32, width=80,
            command=self._on_hero_launch
        )
        self.btn_launch.pack(side="right", padx=6)

        self.btn_revert = ctk.CTkButton(
            action_row, text="Revert",
            font=ctk.CTkFont(family="Segoe UI", size=11),
            fg_color="#181014", hover_color="#29151B",
            border_color="#44222A", border_width=1,
            text_color="#F87171", corner_radius=6, height=32, width=75,
            command=self._on_hero_revert
        )
        self.btn_revert.pack(side="right")

        # ── 2. Library Search & Toolbar ────────────────────────────────────────
        toolbar = ctk.CTkFrame(self, fg_color="#0E1624", corner_radius=10, border_width=1, border_color="#16273C")
        toolbar.pack(fill="x", padx=14, pady=(4, 6))

        # Search bar
        self.search_var = ctk.StringVar()
        self.search_var.trace_add("write", self._on_search_changed)
        search_entry = ctk.CTkEntry(
            toolbar,
            textvariable=self.search_var,
            placeholder_text="🔍 Search library (title, engine, or upscaler)...",
            width=280,
            height=32,
            fg_color="#0A0E17",
            border_color="#182A40"
        )
        search_entry.pack(side="left", padx=12, pady=8)

        # Action Buttons
        add_btn = ctk.CTkButton(
            toolbar,
            text="+ Add Game (.exe / .lnk)",
            width=165,
            height=32,
            font=ctk.CTkFont(size=11, weight="bold"),
            fg_color="#0071C5",
            hover_color="#005A9E",
            command=self._add_game_file
        )
        add_btn.pack(side="right", padx=(4, 12), pady=8)

        add_folder_btn = ctk.CTkButton(
            toolbar,
            text="+ Add Folder",
            width=100,
            height=32,
            font=ctk.CTkFont(size=11),
            fg_color="#162232",
            hover_color="#22344C",
            command=self._add_game_folder
        )
        add_folder_btn.pack(side="right", padx=4, pady=8)

        scan_btn = ctk.CTkButton(
            toolbar,
            text="⚡ Auto-Scan (Steam/Epic)",
            width=160,
            height=32,
            font=ctk.CTkFont(size=11),
            fg_color="#162232",
            hover_color="#22344C",
            command=self._auto_scan
        )
        scan_btn.pack(side="right", padx=4, pady=8)

        # ── 3. Scrollable Library Cards ────────────────────────────────────────
        self.cards_scroll = ctk.CTkScrollableFrame(
            self,
            fg_color="transparent",
            corner_radius=0
        )
        self.cards_scroll.pack(fill="both", expand=True, padx=10, pady=(0, 6))

    def set_active_game(self, profile: dict):
        """Updates the top hero card with the selected profile's details."""
        self.active_profile = profile
        name = profile.get("name", "Unknown Game")
        self.hero_game_lbl.configure(text=name)
        hook = profile.get("effective_settings", {}).get("hook_method") or profile.get("hook_method", "dxgi.dll")
        self.hero_proxy_lbl.configure(text=hook)
        quality = profile.get("effective_settings", {}).get("xess_quality", "Quality")
        self.hero_upscaler_lbl.configure(text=f"XeSS SR • {quality}")

        is_injected = profile.get("is_injected", False)
        if is_injected:
            self.badge_snapshot.configure(text="Snapshot OK", text_color="#3ED598", fg_color="#0D2618", border_color="#246E45")
            self.hero_progress.set(1.0)
        else:
            self.badge_snapshot.configure(text="Vanilla (Stock)", text_color="#7A9ABD", fg_color="#101A28", border_color="#1A3048")
            self.hero_progress.set(0.0)

    def _on_hero_force(self):
        if self.on_force_inject:
            self.on_force_inject()
        elif self.active_profile:
            self.on_select_game(self.active_profile)

    def _on_hero_hw(self):
        if self.on_show_system_info:
            self.on_show_system_info()

    def _on_hero_install(self):
        if self.on_install:
            self.on_install()
        elif self.active_profile:
            self.on_select_game(self.active_profile)

    def _on_hero_launch(self):
        if self.on_launch:
            self.on_launch()

    def _on_hero_revert(self):
        if self.on_revert:
            self.on_revert()

    def _on_search_changed(self, *args):
        self.search_term = self.search_var.get().lower().strip()
        self.refresh_library()

    def refresh_library(self):
        """Re-populates game cards."""
        for child in self.cards_scroll.winfo_children():
            child.destroy()

        profiles = self.library.get_all_profiles()

        if profiles and (self.active_profile is None or not any(p.get("id") == self.active_profile.get("id") for p in profiles)):
            self.set_active_game(profiles[0])
        elif self.active_profile:
            # Refresh active profile data if updated
            for p in profiles:
                if p.get("id") == self.active_profile.get("id"):
                    self.set_active_game(p)
                    break

        if self.search_term:
            profiles = [
                p for p in profiles
                if self.search_term in p.get("name", "").lower()
                or self.search_term in p.get("engine", "").lower()
                or any(self.search_term in str(v).lower() for v in p.get("detected_upscalers", {}).values())
            ]

        if not profiles:
            empty_lbl = ctk.CTkLabel(
                self.cards_scroll,
                text="No games found in library.\nClick '+ Add Game (.exe / .lnk)' or 'Auto-Scan' to populate your library.",
                font=ctk.CTkFont(size=14),
                text_color="#6C727F",
                justify="center"
            )
            empty_lbl.pack(pady=60)
            return

        for p in profiles:
            self._create_game_card(self.cards_scroll, p)

    def _create_game_card(self, parent, profile: dict):
        is_active = bool(self.active_profile and self.active_profile.get("id") == profile.get("id"))
        card = ctk.CTkFrame(
            parent,
            fg_color="#0F1B2C" if is_active else "#0E1624",
            corner_radius=10,
            border_width=1,
            border_color="#0071C5" if is_active else "#182A40"
        )
        card.pack(fill="x", pady=4, padx=4)

        # Left info section
        info_frame = ctk.CTkFrame(card, fg_color="transparent")
        info_frame.pack(side="left", fill="both", expand=True, padx=16, pady=10)

        title_row = ctk.CTkFrame(info_frame, fg_color="transparent")
        title_row.pack(fill="x", anchor="w")

        title_lbl = ctk.CTkLabel(
            title_row,
            text=profile.get("name", "Unknown Game"),
            font=ctk.CTkFont(family="Segoe UI", size=15, weight="bold"),
            text_color="#FFFFFF"
        )
        title_lbl.pack(side="left")

        # Engine badge
        engine_txt = profile.get("engine", "DirectX")
        engine_badge = ctk.CTkLabel(
            title_row,
            text=f" {engine_txt} ",
            font=ctk.CTkFont(size=10, weight="bold"),
            fg_color="#1E2738",
            corner_radius=4,
            text_color="#00C7FD"
        )
        engine_badge.pack(side="left", padx=8)

        # Anti-Cheat badge if present
        if profile.get("anti_cheat"):
            ac_badge = ctk.CTkLabel(
                title_row,
                text=" ⚠️ ANTI-CHEAT ",
                font=ctk.CTkFont(size=9, weight="bold"),
                fg_color="#2E1D0E",
                corner_radius=4,
                text_color="#F59E0B"
            )
            ac_badge.pack(side="left", padx=4)

        # Status badge
        is_injected = profile.get("is_injected", False)
        if is_injected:
            status_text = " INSTALLED • verify in-game "
            status_color = "#123322"
            text_color = "#3ED598"
        else:
            status_text = " VANILLA (STOCK) "
            status_color = "#1E2738"
            text_color = "#8E9297"

        status_badge = ctk.CTkLabel(
            title_row,
            text=status_text,
            font=ctk.CTkFont(size=10, weight="bold"),
            fg_color=status_color,
            corner_radius=4,
            text_color=text_color
        )
        status_badge.pack(side="left", padx=4)

        # Path and details
        details_txt = f"Binary: {os.path.basename(profile.get('target_exe', ''))}  |  Folder: {profile.get('target_dir', '')}"
        path_lbl = ctk.CTkLabel(
            info_frame,
            text=details_txt,
            font=ctk.CTkFont(size=10),
            text_color="#7B808C",
            anchor="w"
        )
        path_lbl.pack(fill="x", pady=(4, 2))

        # Deep scan targets count
        targets_count = len(profile.get("all_target_dirs", [profile.get("target_dir")]))
        target_info = f"Installation target: {targets_count} folder(s) identified across directory tree"

        # Detected native upscalers
        detected = profile.get("detected_upscalers", {})
        det_parts = []
        if detected.get("DLSS"):
            det_parts.append(f"DLSS ({', '.join(detected['DLSS'])})")
        if detected.get("FSR"):
            det_parts.append(f"FSR ({', '.join(detected['FSR'])})")
        if detected.get("XeSS"):
            det_parts.append(f"XeSS ({', '.join(detected['XeSS'])})")

        det_str = f"Found: {' | '.join(det_parts)}  •  {target_info}" if det_parts else target_info
        det_lbl = ctk.CTkLabel(
            info_frame,
            text=det_str,
            font=ctk.CTkFont(size=10),
            text_color="#5865F2",
            anchor="w"
        )
        det_lbl.pack(fill="x")

        # Right actions section
        act_frame = ctk.CTkFrame(card, fg_color="transparent")
        act_frame.pack(side="right", padx=14, pady=12)

        def select_this(p=profile):
            self.set_active_game(p)
            self.on_select_game(p)

        config_btn = ctk.CTkButton(
            act_frame,
            text="Configure & Inject ➔",
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color="#0071C5",
            hover_color="#005A9E",
            height=32,
            width=150,
            command=select_this
        )
        config_btn.pack(side="top", pady=2)

        del_btn = ctk.CTkButton(
            act_frame,
            text="Remove Profile",
            font=ctk.CTkFont(size=10),
            fg_color="transparent",
            text_color="#8E9297",
            hover_color="#1E2738",
            height=22,
            width=100,
            command=lambda gid=profile["id"]: self._remove_game(gid)
        )
        del_btn.pack(side="top", pady=2)

    def _add_game_file(self):
        """Allows user to select a game .exe or desktop .lnk shortcut."""
        filename = filedialog.askopenfilename(
            title="Select Game Executable or Desktop Shortcut",
            filetypes=[
                ("Game Executables and Shortcuts", "*.exe;*.lnk"),
                ("Executable Files", "*.exe"),
                ("Windows Shortcuts", "*.lnk"),
                ("All Files", "*.*")
            ]
        )
        if filename:
            profile = self.library.add_game_by_path(filename)
            if profile:
                self.log(f"Added game: {profile['name']} ({profile['engine']})", "success")
                self.refresh_library()
                self.on_select_game(profile)
            else:
                messagebox.showerror("Error", "Could not resolve the selected file into a valid game executable.")

    def _add_game_folder(self):
        """Allows user to select a game root directory."""
        folder = filedialog.askdirectory(title="Select Game Installation Folder")
        if folder:
            profile = self.library.add_game_by_path(folder)
            if profile:
                self.log(f"Added game from directory: {profile['name']} ({profile['engine']})", "success")
                self.refresh_library()
                self.on_select_game(profile)
            else:
                messagebox.showerror("Error", "Could not find a valid game binary within the selected directory.")

    def _auto_scan(self):
        """Auto scans installed Steam/Epic games in a background thread."""
        if self.scanning:
            return
        self.scanning = True
        self.log("Scanning system for Steam and Epic Games installations...", "info")
        
        import threading
        def worker():
            try:
                discovered = self.library.auto_scan_installed_games()
                error = None
            except Exception as exc:
                discovered, error = [], str(exc)
            def update_ui():
                self.scanning = False
                if error:
                    self.log(error, 'error')
                    return
                self.refresh_library()
                self.log(f"Auto-scan complete. Discovered {len(discovered)} games.", "success")
                if not discovered:
                    messagebox.showinfo(
                        "Auto-Scan",
                        "Scan completed. No new Steam or Epic games were found in default library locations.\n"
                        "You can add custom games manually using '+ Add Game (.exe / .lnk)'."
                    )
            self.dispatcher.post(update_ui)

        threading.Thread(target=worker, daemon=True).start()

    def _remove_game(self, game_id: str):
        if messagebox.askyesno("Remove Profile", "Remove this game profile from the library? (Game files will not be deleted)"):
            self.library.remove_game(game_id)
            self.refresh_library()
