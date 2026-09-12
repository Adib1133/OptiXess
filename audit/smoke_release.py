"""Launch the rebuilt EXE alone, with fresh isolated user data and no network."""
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import time
ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / '.audit-deps')]
from core.files import sha256


with tempfile.TemporaryDirectory(prefix='OptiScaler standalone ') as tmp:
    folder = Path(tmp)
    exe = folder / 'OptiScalerXeSS.exe'
    shutil.copy2(ROOT / 'OptiScalerXeSS.exe', exe)
    user_data = folder / 'user-data'
    cache = user_data / 'assets/versions/releases_cache.json'
    cache.parent.mkdir(parents=True)
    cache.write_text('[{"tag_name":"v0.9.4","name":"v0.9.4","assets":[]}]', encoding='utf-8')
    env = dict(os.environ, OPTISCALER_GUI_DATA_DIR=str(user_data))
    startup = subprocess.STARTUPINFO()
    startup.dwFlags |= subprocess.STARTF_USESHOWWINDOW
    startup.wShowWindow = subprocess.SW_HIDE
    start = time.monotonic()
    result = subprocess.run([str(exe), '--smoke-test'], cwd=folder, env=env,
                            startupinfo=startup, capture_output=True, timeout=90)
    logs = (user_data / 'application.log').read_text(encoding='utf-8') if (user_data / 'application.log').exists() else ''
    report = {'exit_code': result.returncode, 'elapsed_seconds': round(time.monotonic() - start, 2),
              'standalone_no_sibling_assets': not (folder / 'assets').exists(),
              'bundled_package_seeded': (user_data / 'assets/versions/v0.9.4/libxess_dx11.dll').is_file(),
              'application_log': logs, 'stderr': result.stderr.decode('utf-8', errors='replace')}
    if report['bundled_package_seeded']:
        report['seed_hash_matches'] = sha256(user_data / 'assets/versions/v0.9.4/OptiScaler.dll') == sha256(ROOT / 'assets/versions/v0.9.4/OptiScaler.dll')
    (ROOT / 'audit/standalone-smoke-result.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
    print(json.dumps(report, indent=2))
    assert result.returncode == 0 and report.get('seed_hash_matches') and 'Unhandled error' not in logs, report
