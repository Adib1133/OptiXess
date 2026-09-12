"""Release-backed controls and asynchronous per-game deployment workflows."""
import os
import threading
import webbrowser
from pathlib import Path
from core.compatibility import CompatibilityResearch, suggested_controls
from core.detector import GameDetector
from core.game_support import capabilities, describe
from core.install_plan import build_plan, format_plan
from core.game_rules import recipe_for, identity_names
from tkinter import messagebox
import customtkinter as ctk
from core.config_generator import ConfigGenerator
from core.safety import SafetyManager, CrashWatchdog
from gui.dispatch import UIDispatcher


class ConfigTab(ctk.CTkFrame):
    def __init__(self, master, injector, game_library, log_callback, on_profile_updated=None, hw_info=None, **kwargs):
        super().__init__(master, **kwargs)
        self.injector, self.library, self.log = injector, game_library, log_callback
        self.on_profile_updated = on_profile_updated
        self.hw_info = hw_info
        self.current_profile = None
        self.active_watchdog = None
        self.busy = False
        self.dispatcher = UIDispatcher(self)
        self._loading = False
        self._analysis = None
        self.preview_plan = None
        self._build_ui()

    def _build_ui(self):
        scroll = ctk.CTkScrollableFrame(self, fg_color='#0B1220')
        scroll.pack(fill='both', expand=True, padx=12, pady=12)
        self.title_lbl = ctk.CTkLabel(scroll, text='Select a game from the library', font=ctk.CTkFont(size=20, weight='bold'))
        self.title_lbl.pack(anchor='w')
        self.info_lbl = ctk.CTkLabel(scroll, text='', wraplength=850, justify='left')
        self.info_lbl.pack(anchor='w')
        self.status_lbl = ctk.CTkLabel(scroll, text='Configuration preview — runtime activation is checked in the game overlay.', text_color='#00C7FD')
        self.status_lbl.pack(anchor='w', pady=8)
        self.suggestions = ctk.CTkFrame(scroll, fg_color='#10243A', border_color='#0071C5', border_width=1, corner_radius=12)
        self.suggestions.pack(fill='x', pady=12)
        ctk.CTkLabel(self.suggestions, text='01  Suggested Settings', text_color='#00C7FD', font=ctk.CTkFont(size=18, weight='bold')).pack(anchor='w', padx=16, pady=(12, 4))
        self.suggest_text = ctk.CTkTextbox(self.suggestions, height=145, wrap='word', fg_color='#10243A')
        self.suggest_text.pack(fill='x', padx=12, pady=6)
        self.sources_bar = ctk.CTkFrame(self.suggestions, fg_color='transparent')
        self.sources_bar.pack(fill='x', padx=12, pady=(0, 12))
        self.research = None
        self.support = None
        self.research_generation = 0
        self.upscaler_var = ctk.BooleanVar(value=True)
        self.frame_gen_var = ctk.BooleanVar(value=False)
        ctk.CTkLabel(scroll, text='02  Choose components', font=ctk.CTkFont(size=18, weight='bold'), text_color='#00C7FD').pack(anchor='w', pady=(12, 6))
        for label, var in [('Install XeSS upscaling', self.upscaler_var), ('Install XeSS Frame Generation (DX12)', self.frame_gen_var)]:
            ctk.CTkCheckBox(scroll, text=label, variable=var, command=self._on_pipeline_param_changed).pack(anchor='w', pady=8)
        self.plan_lbl = ctk.CTkLabel(scroll, text='Choose at least one component to preview installation.', wraplength=850, justify='left')
        self.plan_lbl.pack(anchor='w', pady=8)
        ctk.CTkLabel(scroll, text='03  Installation settings', font=ctk.CTkFont(size=18, weight='bold'), text_color='#00C7FD').pack(anchor='w', pady=(12, 6))

        def menu(label, variable, values):
            row = ctk.CTkFrame(scroll, fg_color='#121E30', corner_radius=8)
            row.pack(fill='x', pady=4)
            ctk.CTkLabel(row, text=label, width=250, anchor='w').pack(side='left', padx=10)
            widget = ctk.CTkOptionMenu(row, variable=variable, values=values, width=250,
                                       command=self._on_pipeline_param_changed)
            widget.pack(side='left', padx=8, pady=6)
            return widget

        self.mode_var = ctk.StringVar(value='automatic')
        menu('Installation mode (manual = unverified)', self.mode_var, ['automatic', 'manual'])
        self.version_var = ctk.StringVar(value='')
        self.version_dropdown = menu('OptiScaler release', self.version_var, ['No installed releases'])
        self.hook_var = ctk.StringVar(value='dxgi.dll')
        menu('Proxy filename', self.hook_var, self.injector.DEFAULT_HOOKS)
        self.starting_upscaler_var = ctk.StringVar(value='DLSS')
        menu('Game upscaler input', self.starting_upscaler_var, ['DLSS', 'FSR'])
        self.quality_var = ctk.StringVar(value='User Defined')
        menu('Render resolution preset', self.quality_var, ['User Defined', *ConfigGenerator.QUALITY_RATIOS])
        self.model_var = ctk.StringVar(value='auto')
        menu('XeSS network variant (hardware is automatic)', self.model_var, ['auto', '0', '1', '2', '3', '4', '5'])
        self.fg_input_var = ctk.StringVar(value='dlssg')
        menu('Frame-generation input', self.fg_input_var, list(ConfigGenerator.FG_INPUTS))
        ctk.CTkLabel(scroll, text='dlssg: native DLSSG • fsrfg: FSR 3.1 • fsrfg30: FSR 3.0 • upscaler: requires game-specific HUD tuning',
                     wraplength=850, justify='left').pack(anchor='w', pady=4)
        self.invert_depth_var = ctk.StringVar(value='auto')
        menu('Depth inverted override', self.invert_depth_var, ['auto', 'true', 'false'])
        self.jitter_var = ctk.StringVar(value='auto')
        menu('Jittered motion vectors override', self.jitter_var, ['auto', 'true', 'false'])

        self.reflex_var = ctk.BooleanVar(value=False)
        self.spoof_var = ctk.BooleanVar(value=False)
        self.custom_scale_enabled_var = ctk.BooleanVar(value=False)
        for label, variable in [('GPU identity spoofing (separate from required FG dependencies)', self.spoof_var),
                                ('Enable Reflex through FakeNvapi (Intel latency backend chosen by runtime)', self.reflex_var),
                                ('Override preset with custom render scale', self.custom_scale_enabled_var)]:
            ctk.CTkCheckBox(scroll, text=label, variable=variable, command=self._on_pipeline_param_changed).pack(anchor='w', pady=8)
        self.scale_val_lbl = ctk.CTkLabel(scroll, text='Render scale: 0.67x')
        self.scale_val_lbl.pack(anchor='w')
        self.scale_slider = ctk.CTkSlider(scroll, from_=0.25, to=1, command=self._on_scale_slider)
        self.scale_slider.set(0.67)
        self.scale_slider.pack(fill='x')
        self.sharpness_val_lbl = ctk.CTkLabel(scroll, text='Sharpness: 0.30')
        self.sharpness_val_lbl.pack(anchor='w')
        self.sharpness_slider = ctk.CTkSlider(scroll, from_=0, to=1, command=self._on_sharpness_slider)
        self.sharpness_slider.set(0.3)
        self.sharpness_slider.pack(fill='x')
        bar = ctk.CTkFrame(self, fg_color='#121E30', corner_radius=8)
        scroll.pack_forget()
        bar.pack(fill='x', side='bottom', padx=12, pady=(0, 8))
        scroll.pack(fill='both', expand=True, padx=12, pady=12)
        self.apply_btn = ctk.CTkButton(bar, text='Install / Update', command=self.apply_injection)
        self.force_btn = ctk.CTkButton(
            bar, text='⚡ Force Inject',
            command=self.force_injection,
            fg_color='#5C2A00', hover_color='#8A3D00', text_color='#FFB347',
            width=130
        )
        self.launch_btn = ctk.CTkButton(bar, text='Launch & Monitor', command=self.launch_and_protect)
        self.revert_btn = ctk.CTkButton(bar, text='Revert', command=self.revert_changes)
        for button in (self.apply_btn, self.force_btn, self.launch_btn, self.revert_btn):
            button.pack(side='left', padx=8, pady=8)
        self.action_hint_lbl = ctk.CTkLabel(bar, text='', font=ctk.CTkFont(size=12))
        self.action_hint_lbl.pack(side='left', padx=10)
        ctk.CTkButton(bar, text='Open Folder', command=self.open_game_folder).pack(side='right', padx=8)

    def update_version_list(self):
        installed = self.injector.version_manager.get_installed_versions()
        self.version_dropdown.configure(values=installed or ['No installed releases'])
        if not self.version_var.get() and installed:
            self.version_var.set(installed[0])

    @staticmethod
    def _flag(value):
        return 'auto' if value is None else str(value).lower()

    def load_game(self, profile):
        self._loading = True
        self.current_profile = dict(profile)
        self._analysis = None
        self.preview_plan = None
        self.update_version_list()
        self.title_lbl.configure(text=profile.get('name', 'Game'))
        info = f"{profile.get('engine', '')}\n{profile.get('target_dir', '')}"
        if profile.get('anti_cheat'):
            info += f"\n{profile['anti_cheat']} detected. Use only a supported offline game configuration."
        self.info_lbl.configure(text=info)
        values = [(self.mode_var, profile.get('installation_mode', 'automatic')),
                  (self.version_var, profile.get('optiscaler_version', self.version_var.get())),
                  (self.starting_upscaler_var, profile.get('starting_upscaler', 'DLSS')),
                  (self.hook_var, profile.get('hook_method', 'dxgi.dll')),
                  (self.quality_var, profile.get('xess_quality', 'User Defined')),
                  (self.upscaler_var, profile.get('upscaler_enabled', True)),
                  (self.spoof_var, profile.get('gpu_spoofing', False)),
                  (self.frame_gen_var, profile.get('frame_gen_enabled', False)),
                  (self.reflex_var, profile.get('reflex_to_xell_enabled', False)),
                  (self.fg_input_var, profile.get('fg_input', 'dlssg')),
                  (self.model_var, str(profile.get('xess_network_model') if profile.get('xess_network_model') is not None else 'auto')),
                  (self.invert_depth_var, self._flag(profile.get('invert_depth'))),
                  (self.jitter_var, self._flag(profile.get('jitter_cancellation')))]
        for variable, value in values:
            variable.set(value)
        scale = profile.get('custom_scale')
        self.custom_scale_enabled_var.set(scale is not None)
        self.scale_slider.set(scale if scale is not None else 0.67)
        self.sharpness_slider.set(profile.get('sharpness', 0.3))
        self._loading = False
        self._refresh_labels()
        self.support = None
        self.research = None
        self._update_pipeline_view()
        self._research_game(dict(profile))

    def _refresh_labels(self):
        self.scale_val_lbl.configure(text=f'Render scale: {self.scale_slider.get():.2f}x')
        self.sharpness_val_lbl.configure(text=f'Sharpness: {self.sharpness_slider.get():.2f}')

    def _settings(self):
        flag = lambda s: None if s == 'auto' else s == 'true'
        return {'installation_mode': self.mode_var.get(), 'optiscaler_version': self.version_var.get(), 'starting_upscaler': self.starting_upscaler_var.get(),
                'hook_method': self.hook_var.get(), 'xess_quality': self.quality_var.get(),
                'upscaler_enabled': self.upscaler_var.get(), 'gpu_spoofing': self.spoof_var.get(),
                'frame_gen_enabled': self.frame_gen_var.get(), 'fg_input': self.fg_input_var.get(),
                'reflex_to_xell_enabled': self.reflex_var.get(), 'reflex_boost': False,
                'xess_network_model': None if self.model_var.get() == 'auto' else int(self.model_var.get()),
                'custom_scale': self.scale_slider.get() if self.custom_scale_enabled_var.get() and self.quality_var.get() != 'User Defined' else None,
                'sharpness': self.sharpness_slider.get(), 'invert_depth': flag(self.invert_depth_var.get()),
                'jitter_cancellation': flag(self.jitter_var.get()), 'settings_schema': 2}

    def _save_current_settings_to_profile(self):
        if self.current_profile and not self._loading:
            settings = self._settings()
            self.library.update_profile(self.current_profile['id'], settings)
            self.current_profile.update(settings)

    def _on_pipeline_param_changed(self, *args):
        self._update_pipeline_view()
        self._save_current_settings_to_profile()

    def _update_pipeline_view(self):
        analysis = self._analysis
        if analysis is None and self.current_profile:
            analysis = dict(self.current_profile, game_name=self.current_profile['name'])
        if analysis:
            try:
                self.preview_plan = build_plan(analysis, self._settings())
                self.plan_lbl.configure(text=format_plan(self.preview_plan))
                if not self.busy:
                    has_errors = bool(self.preview_plan['errors'])
                    self.apply_btn.configure(state='disabled' if has_errors else 'normal')
                    if has_errors:
                        first_err = self.preview_plan['errors'][0]
                        if 'No reviewed' in first_err:
                            self.action_hint_lbl.configure(
                                text='⚠️ Unlisted game: select "manual" mode or click "Use suggested settings".',
                                text_color='#FFB86C'
                            )
                        elif 'Select XeSS' in first_err:
                            self.action_hint_lbl.configure(
                                text='⚠️ Check "Install XeSS upscaling" above to install.',
                                text_color='#FFB86C'
                            )
                        else:
                            self.action_hint_lbl.configure(text=f'⚠️ {first_err[:65]}', text_color='#FF6B6B')
                    else:
                        self.action_hint_lbl.configure(text='✓ Ready to install', text_color='#50FA7B')
            except Exception as exc:
                self.preview_plan = None
                self.plan_lbl.configure(text='Cannot prepare installation: ' + str(exc))
                self.apply_btn.configure(state='disabled')
                self.action_hint_lbl.configure(text=f'⚠️ {str(exc)[:65]}', text_color='#FF6B6B')
        self.scale_slider.configure(state='normal' if self.quality_var.get() != 'User Defined' and self.custom_scale_enabled_var.get() else 'disabled')

    def _research_game(self, profile):
        self.research_generation += 1
        generation = self.research_generation
        for child in self.sources_bar.winfo_children():
            child.destroy()
        self._show_suggestions('Scanning local runtimes and checking the official OptiScaler compatibility wiki…')
        def worker():
            try:
                analysis = GameDetector.analyze_game(profile['target_exe'])
                if not analysis.get('valid'):
                    raise ValueError(analysis.get('error'))
                if profile.get('base_dir'):
                    analysis['discovered_locations'], analysis['detected_upscalers'] = GameDetector._deep_scan_upscalers(profile['base_dir'], profile['target_dir'])
                analysis['all_target_dirs'] = profile.get('all_target_dirs', [profile['target_dir']])
                support = capabilities(analysis)
                self.dispatcher.post(local_done, support, analysis)
                result = CompatibilityResearch.lookup(identity_names(analysis))
            except Exception as exc:
                support, result = None, {'status': 'error', 'notes': str(exc), 'sources': []}
            self.dispatcher.post(done, support, result)
        def local_done(support, analysis):
            if generation != self.research_generation:
                return
            self.support = support
            self._analysis = analysis
            self._show_suggestions(describe(support) + '\n\nChecking official online compatibility…')
            self._update_pipeline_view()
        def done(support, result):
            if generation != self.research_generation:
                return
            self.support, self.research = support, result
            text = (describe(support) + '\n\n' if support else '')
            if self.preview_plan and self.preview_plan.get('recipe_id'):
                text += 'Reviewed automatic recipe: ' + self.preview_plan['title'] + '\n' + '\n'.join(self.preview_plan['notes']) + '\n\n'
            if self.hw_info:
                gpu = self.hw_info['primary_gpu']
                arc_text = "Intel Arc GPU detected — Dedicated XMX AI matrix acceleration active." if self.hw_info.get('is_arc_detected') else f"{gpu['name']} ({gpu['xess_acceleration']} mode)."
                text += f'Detected Hardware: {arc_text}\n'
            text += 'Online research: ' + result['status'] + ' • ' + result.get('checked_at', '') + '\n' + result['notes']
            text += '\n\nSuggested render preset: User Defined — change quality in game.\nGPU detection errors: leave GPU spoofing off first. If the error persists, Revert and collect the OptiScaler log, game build, API and driver version.'
            self._show_suggestions(text)
            for child in self.sources_bar.winfo_children():
                child.destroy()
            for i, url in enumerate(list(dict.fromkeys((self.preview_plan or {}).get('sources', []) + result.get('sources', [])))[:3]):
                ctk.CTkButton(self.sources_bar, text='Official source ' + str(i + 1), width=130,
                              command=lambda u=url: webbrowser.open(u)).pack(side='left', padx=4)
            ctk.CTkButton(self.sources_bar, text='Use suggested settings', command=self._use_suggestions).pack(side='right', padx=4)
            self._update_pipeline_view()
        threading.Thread(target=worker, daemon=True).start()

    def _use_suggestions(self):
        controls = suggested_controls(self.support, self.research)
        if self.preview_plan and self.preview_plan.get('recipe_id'):
            controls.update(self.preview_plan['settings'])
            self.spoof_var.set(controls['gpu_spoofing'])
        else:
            # For unlisted games, switch to manual mode so the plan is immediately ready to install
            self.mode_var.set('manual')
            if self.hw_info and (self.hw_info.get('is_arc_detected') or self.hw_info.get('primary_gpu', {}).get('vendor') == 'Intel'):
                self.spoof_var.set(False)
        self.upscaler_var.set(True)
        for key, var in [('xess_quality', self.quality_var), ('starting_upscaler', self.starting_upscaler_var),
                         ('fg_input', self.fg_input_var), ('hook_method', self.hook_var)]:
            if key in controls:
                var.set(controls[key])
        self.custom_scale_enabled_var.set(False)
        self._on_pipeline_param_changed()

    def _show_suggestions(self, text):
        self.suggest_text.configure(state='normal')
        self.suggest_text.delete('1.0', 'end')
        self.suggest_text.insert('1.0', text)
        self.suggest_text.configure(state='disabled')

    def _on_scale_slider(self, value):
        self._refresh_labels()
        self._save_current_settings_to_profile()

    def _on_sharpness_slider(self, value):
        self._refresh_labels()
        self._save_current_settings_to_profile()

    def _run(self, operation, done):
        if self.busy:
            return
        self.busy = True
        for button in (self.apply_btn, self.force_btn, self.revert_btn, self.launch_btn):
            button.configure(state='disabled')
        def worker():
            try:
                result = operation()
            except Exception as exc:
                result = {'success': False, 'error': str(exc)}
            self.dispatcher.post(finish, result)
        def finish(result):
            self.busy = False
            for button in (self.apply_btn, self.force_btn, self.revert_btn, self.launch_btn):
                button.configure(state='normal')
            done(result)
            self._update_pipeline_view()
        threading.Thread(target=worker, daemon=True).start()

    def _record_result(self, profile, result):
        updates = {'is_injected': self.injector.is_injected(profile['target_dir']),
                   'has_backup': SafetyManager.has_active_backup(profile['target_dir'])}
        if result.get('success') and result.get('plan'):
            updates['last_installation_plan'] = result['plan']
        self.library.update_profile(profile['id'], updates)
        if self.current_profile and self.current_profile['id'] == profile['id']:
            self.current_profile.update(updates)
            self.status_lbl.configure(text=result.get('message') or result.get('error', ''))
        if self.on_profile_updated:
            self.on_profile_updated()

    def apply_injection(self):
        if not self.current_profile or self.busy:
            return
        self._save_current_settings_to_profile()
        profile = dict(self.current_profile)
        settings = self._settings()
        settings.pop('settings_schema')
        def done(result):
            self._record_result(profile, result)
            if result.get('success'):
                self.log(result['message'], 'success')
            else:
                detail = result.get('error', '')
                if result.get('recovery'):
                    detail += '\nRecovery: ' + str(result['recovery'])
                messagebox.showerror('Installation failed', detail)
        self._run(lambda: self.injector.apply_injection(profile['target_dir'], profile['target_exe'],
                  base_dir=profile.get('base_dir'), **settings), done)

    def force_injection(self):
        """Inject even when errors/conflicts are present.

        Bypasses recipe validation, unmanaged-proxy blocks, and preserves the
        user-chosen proxy filename regardless of the automatic recipe hook.
        OptiScaler.ini is always written; existing user edits are merged in.
        """
        if not self.current_profile or self.busy:
            return
        if not messagebox.askyesno(
            'Force Inject',
            'Force inject will override ALL validation errors, including:\n'
            '  • Unmanaged proxy conflicts\n'
            '  • Recipe hook mismatches\n'
            '  • Automatic mode restrictions\n\n'
            'Existing OptiScaler.ini user edits will be preserved.\n\n'
            'Proceed?',
            icon='warning'
        ):
            return
        self._save_current_settings_to_profile()
        profile = dict(self.current_profile)
        settings = self._settings()
        settings.pop('settings_schema')
        settings['force'] = True
        def done(result):
            self._record_result(profile, result)
            if result.get('success'):
                notes = result.get('plan', {}).get('notes', [])
                force_notes = [n for n in notes if n.startswith('[Force]')]
                if force_notes:
                    self.log('Force inject warnings: ' + ' | '.join(force_notes), 'warning')
                self.log(result['message'], 'success')
            else:
                detail = result.get('error', '')
                if result.get('recovery'):
                    detail += '\nRecovery: ' + str(result['recovery'])
                messagebox.showerror('Force injection failed', detail)
        self._run(lambda: self.injector.apply_injection(profile['target_dir'], profile['target_exe'],
                  base_dir=profile.get('base_dir'), **settings), done)


    def launch_and_protect(self):
        if not self.current_profile or self.busy:
            return
        if self.active_watchdog and self.active_watchdog._monitor_thread and self.active_watchdog._monitor_thread.is_alive():
            messagebox.showinfo('Monitoring active', 'Wait for the current startup observation to finish.')
            return
        profile = dict(self.current_profile)
        if not self.injector.is_injected(profile['target_dir']):
            messagebox.showinfo('Install first', 'Install the selected configuration before launching.')
            return
        if self.injector.is_game_running(profile['target_exe'], profile['target_dir']):
            messagebox.showinfo('Game running', 'This game is already running.')
            return
        def crash(reason, result):
            self._record_result(profile, result)
            self.log(reason, 'error')
            messagebox.showerror('Startup failure', reason + '\n' + result.get('message', result.get('error', '')))
        self.active_watchdog = CrashWatchdog(profile['target_exe'], profile['target_dir'], SafetyManager(),
            additional_dirs=profile.get('recovery_dirs', profile.get('all_target_dirs', [])),
            on_status_update=lambda msg, level: self.dispatcher.post(self.log, msg, level),
            on_crash_detected=lambda reason, result: self.dispatcher.post(crash, reason, result),
            on_launch_success=lambda: self.dispatcher.post(self.log, f"{profile['name']}: startup observation complete; verify the in-game overlay.", 'info'))
        if not self.active_watchdog.launch_and_monitor():
            messagebox.showerror('Launch failed', 'Could not launch the game. See the application log.')

    def revert_changes(self):
        if not self.current_profile or self.busy:
            return
        profile = dict(self.current_profile)
        if not messagebox.askyesno('Revert installation', f"Restore the saved original files for {profile['name']}?"):
            return
        def done(result):
            self._record_result(profile, result)
            self.log(result.get('message', result.get('error', '')), 'success' if result.get('success') else 'error')
            if not result.get('success'):
                messagebox.showerror('Recovery incomplete', result['error'])
        self._run(lambda: self.injector.revert_injection(profile['target_dir'], profile['target_exe'],
                  additional_dirs=profile.get('recovery_dirs', profile.get('all_target_dirs', []))), done)

    def open_game_folder(self):
        if self.current_profile:
            os.startfile(self.current_profile['target_dir'])

    def shutdown(self):
        if self.active_watchdog:
            self.active_watchdog.stop()
        self.dispatcher.close()
