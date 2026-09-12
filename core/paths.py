"""Separate read-only bundled resources from writable per-user state."""
import os
from pathlib import Path
import shutil
import sys
from core.files import operation_lock


def resource_root():
    return Path(getattr(sys, '_MEIPASS', Path(__file__).resolve().parents[1]))


def data_root():
    override = os.environ.get('OPTISCALER_GUI_DATA_DIR')
    root = Path(override) if override else Path(os.environ.get('LOCALAPPDATA', Path.home())) / 'OptiScalerXeSS'
    root.mkdir(parents=True, exist_ok=True)
    return root


def prepare_assets():
    root = data_root() / 'assets'
    # Preserve profiles from the previous application's roaming-data location.
    old_profiles = Path(os.environ.get('APPDATA', '')) / 'OptiScalerXeSS/profiles.json'
    new_profiles = data_root() / 'profiles.json'
    if not os.environ.get('OPTISCALER_GUI_DATA_DIR') and old_profiles.is_file() and not new_profiles.exists():
        from core.files import atomic_write
        atomic_write(new_profiles, source=old_profiles)
    versions = root / 'versions'
    versions.mkdir(parents=True, exist_ok=True)
    bundled = resource_root() / 'assets/versions'
    with operation_lock(versions):
        if bundled.is_dir() and bundled.resolve() != versions.resolve():
            from core.version_manager import VersionManager
            source_vm = VersionManager(bundled)
            for tag in source_vm.get_installed_versions():
                target = versions / tag
                if not target.exists():
                    stage = versions / ('.seed-' + tag)
                    if stage.exists():
                        # Resume a interrupted seed by validating it; discard only our staging dir.
                        shutil.rmtree(stage)
                    shutil.copytree(bundled / tag, stage)
                    os.replace(stage, target)
    return root
