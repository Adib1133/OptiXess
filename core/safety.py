"""Durable original-file snapshots and conservative startup monitoring."""
import copy
from contextlib import ExitStack
import hashlib
import json
import os
from pathlib import Path
import subprocess
import threading
import time
import psutil
from core.files import atomic_write, canonical, inside, operation_lock, safe_path, sha256, write_json


class SafetyManager:
    BACKUP_DIR_NAME = '.optiscaler_backup'
    MANAGED_NAMES = {'dxgi.dll', 'version.dll', 'winmm.dll', 'nvngx.dll', 'd3d12.dll',
                     'dbghelp.dll', 'wininet.dll', 'winhttp.dll', 'optiscaler.dll',
                     'optiscaler.ini', 'nvngx.ini', 'libxess.dll', 'libxess_dx11.dll',
                     'libxess_fg.dll', 'libxessfg.dll', 'libxell.dll', 'fakenvapi.dll', 'fakenvapi.ini'}

    @staticmethod
    def get_file_hash(filepath):
        return sha256(filepath) if os.path.isfile(filepath) else ''

    @staticmethod
    def has_active_backup(target_dir):
        return (Path(target_dir) / SafetyManager.BACKUP_DIR_NAME / 'manifest.json').is_file()

    @staticmethod
    def load_manifest(target_dir, additional_dirs=None):
        primary = Path(target_dir).resolve()
        backup = safe_path(primary, SafetyManager.BACKUP_DIR_NAME)
        with safe_path(backup, 'manifest.json').open(encoding='utf-8') as stream:
            manifest = json.load(stream)
        if canonical(manifest.get('primary_dir', primary)) != canonical(primary):
            raise ValueError('Backup belongs to a different game directory.')
        folders = manifest.get('folders')
        if not isinstance(folders, dict) or not folders:
            raise ValueError('Invalid backup manifest; recovery data retained.')
        allowed = {canonical(primary), *(canonical(d) for d in (additional_dirs or []))}
        for folder, record in folders.items():
            if canonical(folder) not in allowed:
                raise ValueError(f'Backup includes an unselected directory: {folder}')
            if not Path(folder).is_dir():
                raise ValueError(f'Recovery directory is missing: {folder}')
            names = list(record.get('created_files', []))
            for item in record.get('overwritten_files', []):
                names.append(item['filename'])
                dest = Path(item['backup_path'])
                permitted = backup if manifest.get('schema') == 2 else Path(folder) / SafetyManager.BACKUP_DIR_NAME
                if not inside(dest, permitted) or dest.is_symlink():
                    raise ValueError('Invalid backup file location.')
                safe_path(permitted, dest.relative_to(permitted).as_posix())
                expected = item.get('original_hash', '')
                if len(expected) != 64 or not dest.is_file() or sha256(dest) != expected:
                    raise ValueError(f'Original backup missing or corrupt: {item["filename"]}')
            if len(names) != len(set(names)):
                raise ValueError('Duplicate manifest entries.')
            for name in names:
                if name.lower() not in SafetyManager.MANAGED_NAMES:
                    raise ValueError(f'Unexpected file in recovery manifest: {name}')
                safe_path(folder, name)
        return manifest

    @staticmethod
    def create_multi_dir_snapshot(target_dirs_files, metadata, primary_dir):
        primary = Path(primary_dir).resolve()
        backup = safe_path(primary, SafetyManager.BACKUP_DIR_NAME)
        if SafetyManager.has_active_backup(primary):
            manifest = copy.deepcopy(SafetyManager.load_manifest(primary, target_dirs_files))
            if manifest.get('schema') != 2:
                raise ValueError('Revert the legacy installation before applying a new configuration.')
        else:
            manifest = {'schema': 2, 'timestamp': time.time(), 'primary_dir': str(primary), 'folders': {}}
        manifest['metadata'] = metadata
        backup.mkdir(exist_ok=True)
        for folder, names in target_dirs_files.items():
            folder = str(Path(folder).resolve())
            record = manifest['folders'].setdefault(folder, {'created_files': [], 'overwritten_files': []})
            tracked = set(record['created_files']) | {x['filename'] for x in record['overwritten_files']}
            for name in dict.fromkeys(names):
                if name.lower() not in SafetyManager.MANAGED_NAMES:
                    raise ValueError(f'Unsupported deployment filename: {name}')
                target = safe_path(folder, name)
                if name in tracked:
                    continue
                if target.exists():
                    if not target.is_file():
                        raise ValueError(f'Target is not a regular file: {target}')
                    original_hash = sha256(target)
                    token = hashlib.sha256((canonical(target) + original_hash).encode()).hexdigest()
                    dest = safe_path(backup, token + '.orig')
                    atomic_write(dest, source=target)
                    if sha256(dest) != original_hash or sha256(target) != original_hash:
                        raise OSError('Original changed during backup.')
                    record['overwritten_files'].append({'filename': name, 'backup_path': str(dest), 'original_hash': original_hash})
                else:
                    record['created_files'].append(name)
        write_json(backup / 'manifest.json', manifest)
        return manifest

    @staticmethod
    def create_pre_injection_snapshot(target_dir, planned_files, metadata):
        return SafetyManager.create_multi_dir_snapshot({target_dir: planned_files}, metadata, target_dir)

    @staticmethod
    def restore_files(manifest, selection=None):
        removed, restored = [], []
        for folder, record in manifest['folders'].items():
            for name in record['created_files']:
                if selection is not None and (folder, name) not in selection:
                    continue
                target = safe_path(folder, name)
                SafetyManager._safe_remove(target)
                removed.append(str(target))
            for item in record['overwritten_files']:
                name = item['filename']
                if selection is not None and (folder, name) not in selection:
                    continue
                target = safe_path(folder, name)
                SafetyManager._safe_copy(item['backup_path'], target)
                if sha256(target) != item['original_hash']:
                    raise OSError(f'Restored file verification failed: {target}')
                restored.append(str(target))
        return removed, restored

    @staticmethod
    def rollback(target_dir, additional_dirs=None, _locked=False):
        try:
            if not _locked:
                with ExitStack() as stack:
                    directories = sorted({canonical(d): d for d in [target_dir, *(additional_dirs or [])]}.values(), key=canonical)
                    for folder in directories:
                        stack.enter_context(operation_lock(folder))
                    from core.injector import Injector
                    if any(Injector.process_in_directory('', d) for d in directories):
                        raise RuntimeError('Game processes are active. Close the game before recovery.')
                    return SafetyManager.rollback(target_dir, additional_dirs, _locked=True)
            if not SafetyManager.has_active_backup(target_dir):
                return {'success': False, 'error': 'No recovery manifest found. No game files were removed.'}
            manifest = SafetyManager.load_manifest(target_dir, additional_dirs)
            removed, restored = SafetyManager.restore_files(manifest)
            backup = Path(target_dir) / SafetyManager.BACKUP_DIR_NAME
            retired = backup / 'completed.json'
            os.replace(backup / 'manifest.json', retired)
            warning = ''
            try:
                for record in manifest['folders'].values():
                    for item in record['overwritten_files']:
                        Path(item['backup_path']).unlink(missing_ok=True)
                retired.unlink()
                for folder in manifest['folders']:
                    try:
                        (Path(folder) / SafetyManager.BACKUP_DIR_NAME).rmdir()
                    except OSError:
                        pass
            except OSError as exc:
                warning = f' Recovery cleanup pending: {exc}'
            return {'success': True, 'removed': removed, 'restored': restored,
                    'message': f'Restored {len(restored)} original files; removed {len(removed)} managed files.' + warning}
        except Exception as exc:
            return {'success': False, 'error': f'Recovery incomplete; backups retained. {exc}'}

    @staticmethod
    def _safe_remove(filepath, retries=4, delay=0.1):
        for attempt in range(retries):
            try:
                Path(filepath).unlink(missing_ok=True)
                return
            except PermissionError:
                if attempt == retries - 1:
                    raise
                time.sleep(delay * 2 ** attempt)

    @staticmethod
    def _safe_copy(src, dst, retries=4, delay=0.1):
        for attempt in range(retries):
            try:
                atomic_write(dst, source=src)
                return
            except PermissionError:
                if attempt == retries - 1:
                    raise
                time.sleep(delay * 2 ** attempt)


class CrashWatchdog:
    """Observe startup. Recover only confirmed failures after game processes exit.

    Callbacks run on the worker; GUI consumers must use their UI dispatcher.
    """
    def __init__(self, target_exe, target_dir, safety_manager, additional_dirs=None,
                 on_status_update=None, on_crash_detected=None, on_launch_success=None,
                 surveillance_duration=25):
        self.target_exe, self.target_dir = target_exe, target_dir
        self.safety_manager = safety_manager
        self.additional_dirs = additional_dirs or []
        self.on_status_update = on_status_update or (lambda *args: None)
        self.on_crash_detected = on_crash_detected or (lambda *args: None)
        self.on_launch_success = on_launch_success or (lambda: None)
        self.surveillance_duration = surveillance_duration
        self._stop_event = threading.Event()
        self._monitor_thread = None

    def launch_and_monitor(self):
        if self._monitor_thread and self._monitor_thread.is_alive():
            return False
        self._stop_event.clear()
        try:
            cmd = self.target_exe if isinstance(self.target_exe, list) else [self.target_exe]
            proc = subprocess.Popen(cmd, cwd=self.target_dir,
                                    creationflags=getattr(subprocess, 'CREATE_NEW_PROCESS_GROUP', 0))
            self.on_status_update(f'Startup monitoring: PID {proc.pid}.', 'info')
            self._monitor_thread = threading.Thread(target=self._surveillance_loop, args=(proc, proc.pid), daemon=True)
            self._monitor_thread.start()
            return True
        except Exception as exc:
            self.on_status_update(f'Launch failed: {exc}', 'error')
            return False

    @staticmethod
    def reporter_targets(args, pids):
        args = [str(a).lower() for a in args]
        for i, arg in enumerate(args):
            if arg in ('-p', '-pid', '--pid') and i + 1 < len(args) and args[i + 1] in {str(p) for p in pids}:
                return True
        return False

    def _surveillance_loop(self, proc, initial_pid):
        start = time.monotonic()
        tracked = {}
        live = []
        reason = None
        clean_since = None
        try:
            while time.monotonic() - start < self.surveillance_duration:
                if self._stop_event.is_set():
                    return
                if proc.poll() is None:
                    try:
                        for child in psutil.Process(initial_pid).children(recursive=True):
                            tracked[(child.pid, child.create_time())] = child
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        pass
                live = []
                for key, child in list(tracked.items()):
                    try:
                        if child.is_running():
                            live.append(child.pid)
                            for descendant in child.children(recursive=True):
                                tracked[(descendant.pid, descendant.create_time())] = descendant
                        else:
                            exit_code = child.wait(timeout=0)
                            if exit_code not in (None, 0):
                                reason = f'Child process exited with code {exit_code}.'
                    except psutil.NoSuchProcess:
                        pass
                    except (psutil.AccessDenied, psutil.TimeoutExpired):
                        live.append(child.pid)
                exit_code = proc.poll()
                if exit_code not in (None, 0):
                    reason = f'Process exited with code {exit_code} (0x{exit_code & 0xffffffff:08X}).'
                for reporter in psutil.process_iter(['name']):
                    try:
                        reporter_pids = ([initial_pid] if exit_code is None else []) + live
                        if (reporter.info.get('name') or '').lower() == 'werfault.exe' and self.reporter_targets(reporter.cmdline(), reporter_pids):
                            reason = 'Windows reported a failure for the monitored process.'
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        pass
                if reason:
                    break
                if exit_code == 0 and not live:
                    clean_since = clean_since or time.monotonic()
                    if time.monotonic() - clean_since >= 1:
                        self.on_status_update('Process exited normally. No rollback performed.', 'info')
                        return
                if self._stop_event.wait(0.25):
                    return
            if self._stop_event.is_set():
                return
            if reason:
                from core.injector import Injector
                if proc.poll() is None or live or any(Injector.process_in_directory('', d) for d in [self.target_dir, *self.additional_dirs]):
                    result = {'success': False, 'error': 'Game processes are still active. Close the game, then use Revert; backups retained.'}
                else:
                    result = self.safety_manager.rollback(self.target_dir, self.additional_dirs)
                self.on_status_update(reason, 'error')
                self.on_crash_detected(reason, result)
            else:
                self.on_status_update('Startup observation ended without a detected failure. Rendering/backend activation is not verified.', 'info')
                self.on_launch_success()
        except Exception as exc:
            self.on_status_update(f'Monitoring stopped: {exc}. No automatic recovery attempted.', 'error')

    def stop(self):
        self._stop_event.set()
