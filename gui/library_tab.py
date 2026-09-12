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

    def __init__(self, master, game_library, on_select_game: Callable[[dict], None], log_callback: Callable[[str, str], None], **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)

        self.library = game_library
        self.on_select_game = on_select_game
        self.log = log_callback
        self.search_term = ""
        self.dispatcher = UIDispatcher(self)
        self.scanning = False

        self._build_ui()
        self.refresh_library()

    def _build_ui(self):
        # Top toolbar
        toolbar = ctk.CTkFrame(self, fg_color=("#121622", "#0D111A"), corner_radius=12, border_width=1, border_color="#1E2738")
        toolbar.pack(fill="x", padx=14, pady=(10, 8))

        # Search bar
        self.search_var = ctk.StringVar()
        self.search_var.trace_add("write", self._on_search_changed)
        search_entry = ctk.CTkEntry(
            toolbar,
            textvariable=self.search_var,
            placeholder_text="🔍 Search library (by title, engine, or upscaler)...",
            width=280,
            height=34,
            fg_color="#0A0D14",
            border_color="#1E2738"
        )
        search_entry.pack(side="left", padx=14, pady=10)

        # Action Buttons
        add_btn = ctk.CTkButton(
            toolbar,
            text="+ Add Game (.exe / .lnk)",
            width=170,
            height=34,
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color="#0071C5",
            hover_color="#005A9E",
            command=self._add_game_file
        )
        add_btn.pack(side="right", padx=(4, 14), pady=10)

        add_folder_btn = ctk.CTkButton(
            toolbar,
            text="+ Add Folder",
            width=110,
            height=34,
            font=ctk.CTkFont(size=12),
            fg_color="#1E2738",
            hover_color="#2A374E",
            command=self._add_game_folder
        )
        add_folder_btn.pack(side="right", padx=4, pady=10)

        scan_btn = ctk.CTkButton(
            toolbar,
            text="⚡ Auto-Scan (Steam/Epic)",
            width=170,
            height=34,
            font=ctk.CTkFont(size=12),
            fg_color="#1E2738",
            hover_color="#2A374E",
            command=self._auto_scan
        )
        scan_btn.pack(side="right", padx=4, pady=10)

        # Main scrollable frame for cards
        self.cards_scroll = ctk.CTkScrollableFrame(
            self,
            fg_color="transparent",
            corner_radius=0
        )
        self.cards_scroll.pack(fill="both", expand=True, padx=10, pady=(0, 10))

    def _on_search_changed(self, *args):
        self.search_term = self.search_var.get().lower().strip()
        self.refresh_library()

    def refresh_library(self):
        """Re-populates game cards."""
        for child in self.cards_scroll.winfo_children():
            child.destroy()

        profiles = self.library.get_all_profiles()

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
        card = ctk.CTkFrame(parent, fg_color=("#121622", "#0D111A"), corner_radius=12, border_width=1, border_color="#1E2738")
        card.pack(fill="x", pady=6, padx=4)

        # Left info section
        info_frame = ctk.CTkFrame(card, fg_color="transparent")
        info_frame.pack(side="left", fill="both", expand=True, padx=16, pady=12)

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

        config_btn = ctk.CTkButton(
            act_frame,
            text="Configure & Inject ➔",
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color="#0071C5",
            hover_color="#005A9E",
            height=34,
            width=150,
            command=lambda p=profile: self.on_select_game(p)
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
