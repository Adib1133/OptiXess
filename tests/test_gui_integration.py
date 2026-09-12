"""Withdrawn real Tk workflows with isolated storage and no network."""
import os
from pathlib import Path
import tempfile
import time
import unittest
from unittest.mock import patch
from tests.fixtures import package, game
from gui.main_window import MainWindow


class GUIIntegrationTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        package(self.root / 'assets')
        package(self.root / 'assets', 'v0.9.3')
        patches = [patch('gui.main_window.prepare_assets', return_value=self.root / 'assets'),
                   patch('gui.main_window.data_root', return_value=self.root),
                   patch('core.version_manager.urllib.request.urlopen', side_effect=OSError('offline')),
                   patch('tkinter.messagebox.showerror'), patch('tkinter.messagebox.showinfo')]
        for p in patches:
            p.start()
            self.addCleanup(p.stop)
        self.app = MainWindow()
        self.app.withdraw()
        self.addCleanup(self.close)
        self.tab = self.app.config_tab
        self.profile = self.app.library.add_game_by_path(str(game(self.root / 'game')))
        self.app._on_game_selected_from_library(self.profile)

    def close(self):
        self.pump()
        self.app.config_tab.shutdown()
        self.app.version_tab.shutdown()
        self.app.library_tab.dispatcher.close()
        self.app.log_console.dispatcher.close()
        self.app.cancel_timers()
        self.app.destroy()

    def pump(self):
        deadline = time.monotonic() + 30
        while time.monotonic() < deadline:
            self.app.update()
            if not self.tab.busy and not self.app.version_tab.busy:
                # Let queued callbacks and initial release timer execute.
                for _ in range(5):
                    time.sleep(0.02)
                    self.app.update()
                if not self.tab.busy and not self.app.version_tab.busy:
                    return
            time.sleep(0.01)
        import faulthandler
        faulthandler.dump_traceback()
        self.fail('GUI operation did not finish within 30 seconds')

    def test_install_update_revert_workflow(self):
        self.tab.mode_var.set('manual')
        self.tab.upscaler_var.set(True)
        self.tab.starting_upscaler_var.set('FSR')
        self.tab.apply_injection()
        self.pump()
        folder = Path(self.profile['target_dir'])
        self.assertTrue((folder / 'OptiScaler.ini').exists())
        self.assertTrue((folder / 'libxess_dx11.dll').exists())
        self.tab.hook_var.set('winmm.dll')
        self.tab.apply_injection()
        self.pump()
        self.assertTrue((folder / 'winmm.dll').exists())
        self.assertFalse((folder / 'dxgi.dll').exists())
        with patch('tkinter.messagebox.askyesno', return_value=True):
            self.tab.revert_changes()
            self.pump()
        self.assertFalse((folder / 'OptiScaler.ini').exists())
        self.assertFalse((folder / 'fakenvapi.ini').exists())

    def test_components_start_unselected_and_user_defined_ignores_custom_scale(self):
        self.assertFalse(self.tab.upscaler_var.get())
        self.assertFalse(self.tab.frame_gen_var.get())
        self.assertFalse(self.tab.spoof_var.get())
        self.assertEqual(self.tab.quality_var.get(), 'User Defined')
        self.tab.custom_scale_enabled_var.set(True)
        self.assertIsNone(self.tab._settings()['custom_scale'])

    def test_every_saved_control_restored_on_profile_switch(self):
        self.tab.version_var.set('v0.9.3')
        self.tab.invert_depth_var.set('true')
        self.tab.jitter_var.set('false')
        self.tab.fg_input_var.set('fsrfg30')
        self.tab.quality_var.set('Quality')
        self.tab.custom_scale_enabled_var.set(True)
        self.tab.scale_slider.set(0.7)
        self.tab._on_pipeline_param_changed()
        other = self.app.library.add_game_by_path(str(game(self.root / 'other')))
        self.tab.load_game(other)
        restored = self.app.library.profiles[self.profile['id']]
        self.tab.load_game(restored)
        self.assertEqual(self.tab.version_var.get(), 'v0.9.3')
        self.assertEqual(self.tab.invert_depth_var.get(), 'true')
        self.assertEqual(self.tab.jitter_var.get(), 'false')
        self.assertEqual(self.tab.fg_input_var.get(), 'fsrfg30')
        self.assertAlmostEqual(self.tab.scale_slider.get(), 0.7)

    def test_crash_callback_captures_game_and_respects_failed_recovery(self):
        with patch('gui.config_tab.CrashWatchdog') as cls, patch.object(self.tab.injector, 'is_injected', return_value=True), patch.object(self.tab.injector, 'is_game_running', return_value=False):
            self.tab.launch_and_protect()
            callback = cls.call_args.kwargs['on_crash_detected']
        other = self.app.library.add_game_by_path(str(game(self.root / 'other')))
        self.tab.load_game(other)
        with patch.object(self.app.library, 'update_profile', wraps=self.app.library.update_profile) as update:
            callback('crash in A', {'success': False, 'error': 'Still running; backups retained'})
            self.pump()
            self.assertEqual(update.call_args.args[0], self.profile['id'])
        self.assertEqual(self.tab.current_profile['id'], other['id'])

    def test_dispatcher_worker_queues_without_touching_tk(self):
        import threading
        seen = []
        thread = threading.Thread(target=lambda: self.tab.dispatcher.post(lambda: seen.append(threading.get_ident())))
        thread.start()
        thread.join()
        self.pump()
        self.assertEqual(seen, [threading.get_ident()])
