"""Isolated fixture window for visual review; never touches the user's library."""
import sys
from pathlib import Path
import tempfile
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from tests.fixtures import package, game, pe_bytes
from gui.main_window import MainWindow

with tempfile.TemporaryDirectory(prefix='arcscaler-preview-') as tmp:
    root=Path(tmp);package(root/'assets')
    with patch('gui.main_window.prepare_assets',return_value=root/'assets'),patch('gui.main_window.data_root',return_value=root),patch('core.version_manager.urllib.request.urlopen',side_effect=OSError('Offline visual review')):
        app=MainWindow();app.title('ArcScaler · UI review')
        exe=game(root/'Townfall');(exe.parent/'nvngx_dlss.dll').write_bytes(pe_bytes())
        profile=app.library.add_game_by_path(str(exe))
        app.library.update_profile(profile['id'],dict(name='Townfall',upscaler_enabled=True,xess_quality='Quality'))
        app.library.add_game_by_path(str(game(root/'Second Game')))
        app.library_tab.refresh_library();app._on_game_selected_from_library(app.library.profiles[profile['id']])
        app.mainloop()
