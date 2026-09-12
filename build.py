"""Build the single-file Windows distribution using pinned dependencies."""
import json
from pathlib import Path
import shutil
import subprocess
import sys


def build():
    root = Path(__file__).resolve().parent
    import customtkinter
    import PyInstaller
    from core.version_manager import VersionManager
    from core.files import sha256
    VersionManager(root / 'assets/versions').resolve_package('v0.9.4')
    command = [sys.executable, '-m', 'PyInstaller', '--noconfirm', '--clean', '--onefile', '--windowed',
               '--name', 'OptiScalerXeSS', '--icon', str(root / 'assets/icon.ico'),
               '--add-data', f'{Path(customtkinter.__file__).parent};customtkinter',
               '--add-data', f'{root / "assets/icon.ico"};assets',
               '--add-data', f'{root / "assets/versions/v0.9.4"};assets/versions/v0.9.4',
               '--collect-all', 'py7zr', '--hidden-import', 'psutil',
               '--hidden-import', 'PIL', '--hidden-import', 'tkinter', str(root / 'main.py')]
    with (root / 'audit/build-log.txt').open('w', encoding='utf-8') as log:
        subprocess.run(command, cwd=root, check=True, stdout=log, stderr=subprocess.STDOUT)
    output = root / 'dist/OptiScalerXeSS.exe'
    old = root / 'OptiScalerXeSS.exe'
    backup = root / 'audit/OptiScalerXeSS.before-fixes.exe'
    if old.exists() and not backup.exists():
        shutil.copy2(old, backup)
    shutil.copy2(output, old)
    metadata = {'python': sys.version, 'pyinstaller': PyInstaller.__version__,
                'executable': str(old), 'sha256': sha256(old), 'size': old.stat().st_size}
    (root / 'audit/build-result.json').write_text(json.dumps(metadata, indent=2), encoding='utf-8')
    print(json.dumps(metadata, indent=2))
    return True


if __name__ == '__main__':
    build()
