"""Asynchronous release browsing, download management, and local file validation."""
import os
import threading
from pathlib import Path
from tkinter import messagebox
import customtkinter as ctk
from gui.dispatch import UIDispatcher


class VersionTab(ctk.CTkFrame):
    def __init__(self, master, version_manager, log_callback, on_versions_updated=None, **kwargs):
        super().__init__(master, **kwargs)
        self.version_manager, self.log = version_manager, log_callback
        self.on_versions_updated = on_versions_updated
        self.dispatcher = UIDispatcher(self)
        self.busy = False
        self.releases = []
        self.buttons = []

        # ── Top action bar ────────────────────────────────────────────────────
        top_bar = ctk.CTkFrame(self, fg_color='transparent')
        top_bar.pack(fill='x', padx=16, pady=(12, 4))

        self.check_btn = ctk.CTkButton(
            top_bar, text='⟳  Refresh official releases',
            command=self.refresh_versions, width=200
        )
        self.check_btn.pack(side='left', padx=(0, 8))

        ctk.CTkButton(
            top_bar, text='📂  Open Download Folder',
            command=self.open_versions_dir, width=200,
            fg_color='#1A2D1A', hover_color='#243D24', text_color='#6DDA8A'
        ).pack(side='left', padx=(0, 8))

        ctk.CTkButton(
            top_bar, text='✔  Validate Local Files',
            command=self._validate_local, width=200,
            fg_color='#1A2530', hover_color='#243545', text_color='#7ABFEF'
        ).pack(side='left')

        # ── Status + progress ─────────────────────────────────────────────────
        self.status = ctk.CTkLabel(self, text='', wraplength=900, justify='left')
        self.status.pack(anchor='w', padx=16, pady=(2, 0))
        self.progress = ctk.CTkProgressBar(self)
        self.progress.set(0)
        self.progress.pack(fill='x', padx=16, pady=(2, 4))

        # ── Instructions panel ────────────────────────────────────────────────
        info = ctk.CTkFrame(self, fg_color='#0F1D2A', corner_radius=8,
                            border_width=1, border_color='#1E3A5F')
        info.pack(fill='x', padx=12, pady=(0, 6))
        ctk.CTkLabel(
            info,
            text=('💡  Manual install: click "Open Download Folder", place extracted OptiScaler '
                  'files inside a new sub-folder named after the version (e.g. v0.9.4/), then '
                  'click "Validate Local Files". You can also replace individual files in an '
                  'installed version folder and click "Validate & Rebuild Hashes" on that card.'),
            font=ctk.CTkFont(size=11),
            text_color='#7ABFEF',
            wraplength=900,
            justify='left',
        ).pack(anchor='w', padx=12, pady=8)

        # ── Scrollable release list ───────────────────────────────────────────
        self.releases_scroll = ctk.CTkScrollableFrame(self)
        self.releases_scroll.pack(fill='both', expand=True, padx=12, pady=(0, 8))

        self.after(50, lambda: self.refresh_versions(False))

    # ── Busy state ─────────────────────────────────────────────────────────────

    def _busy(self, value):
        self.busy = value
        for btn in [self.check_btn, *self.buttons]:
            try:
                btn.configure(state='disabled' if value else 'normal')
            except Exception:
                pass

    # ── Release list ───────────────────────────────────────────────────────────

    def refresh_versions(self, force_refresh=True):
        if self.busy:
            return
        self._busy(True)
        self.status.configure(text='Reading official releases…')

        def worker():
            try:
                releases = self.version_manager.fetch_available_releases(force_refresh)
                error = self.version_manager.last_error
            except Exception as exc:
                releases, error = [], str(exc)
            self.dispatcher.post(done, releases, error)

        def done(releases, error):
            self.releases = releases
            self._busy(False)
            self._populate_cards()
            self.status.configure(text=error or f'{len(releases)} release(s) available')
            if self.on_versions_updated:
                self.on_versions_updated()

        threading.Thread(target=worker, daemon=True).start()

    check_for_updates = refresh_versions

    def _populate_cards(self):
        for child in self.releases_scroll.winfo_children():
            child.destroy()
        self.buttons = []

        for release in self.releases:
            self._make_release_card(release, release.get('tag_name', '?'),
                                    release.get('installed', False))

        # Also show locally installed versions not in the release list
        cached_tags = {r.get('tag_name') for r in self.releases}
        for tag in self.version_manager.get_installed_versions():
            if tag not in cached_tags:
                self._make_release_card(
                    {'tag_name': tag, 'name': tag + ' (local only)',
                     'body': '', 'assets': [], 'installed': True},
                    tag, installed=True, local_only=True
                )

    def _make_release_card(self, release, tag, installed, local_only=False):
        card = ctk.CTkFrame(
            self.releases_scroll,
            fg_color='#0B1A2B' if installed else '#111820',
            corner_radius=10,
            border_width=1,
            border_color='#0A4878' if installed else '#1C2A3A'
        )
        card.pack(fill='x', pady=5)

        # Header row
        header = ctk.CTkFrame(card, fg_color='transparent')
        header.pack(fill='x', padx=12, pady=(10, 0))

        label = release.get('name') or tag
        badge_color = '#2A5C3A' if installed else '#3A2A1A'
        badge_text_color = '#6DDA8A' if installed else '#D4A76A'
        status_badge = '✅ Installed' if installed else '⬇  Not installed'

        ctk.CTkLabel(
            header, text=label,
            font=ctk.CTkFont(size=15, weight='bold'),
            text_color='#D0E8FF' if installed else '#B0C0D0',
            anchor='w'
        ).pack(side='left')

        ctk.CTkLabel(
            header, text=f'  {status_badge}',
            font=ctk.CTkFont(size=12, weight='bold'),
            text_color=badge_text_color, fg_color=badge_color,
            corner_radius=6, padx=8, pady=2
        ).pack(side='left', padx=(10, 0))

        # Release notes
        body = (release.get('body') or '').strip()
        if body:
            ctk.CTkLabel(
                card, text=body[:280] + ('…' if len(body) > 280 else ''),
                wraplength=800, justify='left',
                font=ctk.CTkFont(size=11), text_color='#7A8A9A'
            ).pack(anchor='w', padx=12, pady=(4, 0))

        # Installed file list (compact summary)
        if installed:
            try:
                details = self.version_manager.get_version_details(tag)
                files = [f for f in details.get('files', {}) if not f.startswith('.')]
                size_mb = details.get('total_size_mb', 0)
                preview = ', '.join(sorted(files)[:8])
                if len(files) > 8:
                    preview += f', … +{len(files) - 8} more'
                ctk.CTkLabel(
                    card,
                    text=f'📦 {size_mb:.1f} MB  •  {preview}',
                    font=ctk.CTkFont(size=10), text_color='#4A7A9A',
                    wraplength=800, justify='left'
                ).pack(anchor='w', padx=12, pady=(2, 0))
            except Exception:
                pass

        # Action buttons row
        btn_row = ctk.CTkFrame(card, fg_color='transparent')
        btn_row.pack(anchor='e', padx=12, pady=(8, 10))

        if not local_only and release.get('assets'):
            btn_label = '🔄 Re-download' if installed else '⬇  Download & Install'
            btn = ctk.CTkButton(
                btn_row, text=btn_label,
                fg_color='#1A3A2A' if installed else '#003B6F',
                hover_color='#244D38' if installed else '#005A9E',
                text_color='#C0E8D0' if installed else '#A0C8F0',
                command=lambda r=release: self._download_release(r),
                width=190
            )
            btn.pack(side='left', padx=(0, 8))
            self.buttons.append(btn)

        if installed:
            vbtn = ctk.CTkButton(
                btn_row, text='✔ Validate & Rebuild Hashes',
                fg_color='#1A2530', hover_color='#243545', text_color='#7ABFEF',
                command=lambda t=tag: self._validate_version(t),
                width=210
            )
            vbtn.pack(side='left', padx=(0, 8))
            self.buttons.append(vbtn)

            dbtn = ctk.CTkButton(
                btn_row, text='🗑 Delete',
                fg_color='#3A0A0A', hover_color='#5C1111', text_color='#FF6B6B',
                command=lambda t=tag: self._delete_version(t),
                width=90
            )
            dbtn.pack(side='left')
            self.buttons.append(dbtn)


    # ── Download ────────────────────────────────────────────────────────────────

    def _download_release(self, release):
        if self.busy:
            return
        self._busy(True)
        self.progress.set(0)

        def progress(value, text):
            self.dispatcher.post(
                lambda: (self.progress.set(value), self.status.configure(text=text))
            )

        def worker():
            result = self.version_manager.download_and_install_version(release, progress)
            self.dispatcher.post(done, result)

        def done(result):
            self._busy(False)
            if result.get('success'):
                self.log(f"Installed {result['tag']}; package structure verified.", 'success')
                self.status.configure(text=f"✅ {result['tag']} installed successfully.")
                self.progress.set(1)
                self.refresh_versions(False)
            else:
                err = result.get('error', 'Unknown error')
                self.status.configure(text=f'❌ {err[:120]}')
                self.progress.set(0)
                messagebox.showerror('Download failed', err)

        threading.Thread(target=worker, daemon=True).start()

    # ── Local validation ────────────────────────────────────────────────────────

    def _validate_local(self):
        """Scan every sub-folder in the versions directory and validate / rebuild hashes."""
        if self.busy:
            return
        self._busy(True)
        self.status.configure(text='Scanning local version folders…')

        def worker():
            versions_dir = Path(self.version_manager.versions_dir)
            results = []
            for folder in sorted(versions_dir.iterdir()):
                if not folder.is_dir() or folder.name.startswith('.'):
                    continue
                tag = folder.name
                strict = self.version_manager.validate_local_version(tag, ignore_hashes=False)
                if strict['valid']:
                    results.append((tag, 'already valid', True))
                    continue
                loose = self.version_manager.validate_local_version(tag, ignore_hashes=True)
                if loose['valid']:
                    try:
                        self.version_manager.rebuild_version_meta(tag)
                        results.append((tag, 'validated — hashes rebuilt', True))
                    except Exception as exc:
                        results.append((tag, f'rebuild failed: {exc}', False))
                else:
                    results.append((tag, loose['error'], False))
            self.dispatcher.post(done, results)

        def done(results):
            self._busy(False)
            if not results:
                self.status.configure(text='No version folders found.')
                messagebox.showinfo(
                    'Validate Local Files',
                    f'No version folders were found in:\n{self.version_manager.versions_dir}\n\n'
                    'Extract OptiScaler into a sub-folder (e.g. v0.9.4/) and try again.'
                )
                return
            ok_count = sum(1 for _, _, ok in results if ok)
            lines = [f'{"✅" if ok else "❌"}  {t}: {msg}' for t, msg, ok in results]
            self.status.configure(
                text=f'Validation complete: {ok_count}/{len(results)} OK'
            )
            for t, msg, ok in results:
                self.log(f'Local {t}: {msg}', 'success' if ok else 'error')
            messagebox.showinfo('Validate Local Files', '\n'.join(lines))
            self.refresh_versions(False)

        threading.Thread(target=worker, daemon=True).start()

    def _validate_version(self, tag):
        """Validate and rebuild hashes for a single installed version."""
        if self.busy:
            return
        self._busy(True)
        self.status.configure(text=f'Validating {tag}…')

        def worker():
            loose = self.version_manager.validate_local_version(tag, ignore_hashes=True)
            if not loose['valid']:
                self.dispatcher.post(fail, loose['error'])
                return
            try:
                self.version_manager.rebuild_version_meta(tag)
                self.dispatcher.post(done, loose['files'])
            except Exception as exc:
                self.dispatcher.post(fail, str(exc))

        def done(files):
            self._busy(False)
            self.log(f'{tag}: {len(files)} files validated; hashes updated.', 'success')
            self.status.configure(text=f'✅ {tag} validated successfully.')
            detail = '\n'.join(f'  {f}' for f in files[:25])
            messagebox.showinfo('Validation passed',
                                f'{tag} passed all checks.\n\nFiles:\n{detail}')
            self.refresh_versions(False)

        def fail(error):
            self._busy(False)
            self.log(f'{tag}: validation failed — {error}', 'error')
            self.status.configure(text=f'❌ {tag} validation failed.')
            messagebox.showerror('Validation failed',
                                 f'{tag} did not pass validation.\n\n{error}')

        threading.Thread(target=worker, daemon=True).start()

    # ── Delete version ──────────────────────────────────────────────────────────

    def _delete_version(self, tag):
        """Permanently delete an installed version from the downloads folder."""
        if self.busy:
            return
        if not messagebox.askyesno(
            'Delete version',
            f'Permanently delete {tag} from the downloads folder?\n\nThis cannot be undone.',
            icon='warning'
        ):
            return
        self._busy(True)
        self.status.configure(text=f'Deleting {tag}…')

        def worker():
            try:
                self.version_manager.delete_version(tag)
                self.dispatcher.post(done)
            except Exception as exc:
                self.dispatcher.post(fail, str(exc))

        def done():
            self._busy(False)
            self.log(f'{tag}: deleted from downloads folder.', 'success')
            self.status.configure(text=f'{tag} deleted.')
            self.refresh_versions(False)

        def fail(error):
            self._busy(False)
            self.log(f'{tag}: deletion failed — {error}', 'error')
            self.status.configure(text=f'❌ Deletion failed.')
            messagebox.showerror('Deletion failed', error)

        threading.Thread(target=worker, daemon=True).start()

    # ── Folder open ─────────────────────────────────────────────────────────────

    def open_versions_dir(self):
        path = Path(self.version_manager.versions_dir)
        path.mkdir(parents=True, exist_ok=True)
        os.startfile(str(path))


    def shutdown(self):
        self.dispatcher.close()

