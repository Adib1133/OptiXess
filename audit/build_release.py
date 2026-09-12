"""Build with workspace dependencies and a workspace-local build cache."""
import os
from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / '.audit-deps')]
os.environ['PYTHONPATH'] = str(ROOT / '.audit-deps') + os.pathsep + str(ROOT)
os.environ['PYINSTALLER_CONFIG_DIR'] = str(ROOT / 'build/pyinstaller-cache')
from build import build
build()
