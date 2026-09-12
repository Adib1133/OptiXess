import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from tests.test_gui_integration import GUIIntegrationTests
from tests.fixtures import game
from PIL import ImageGrab
case = GUIIntegrationTests()
case.setUp()
try:
    profile = case.app.library.add_game_by_path(str(game(case.root / 'Spider-Man 2', 'Spider-Man2.exe')))
    case.app._on_game_selected_from_library(profile)
    case.tab.frame_gen_var.set(True)
    case.tab._on_pipeline_param_changed()
    case.app.deiconify()
    case.app.geometry('1200x860+40+40')
    case.pump()
    assert case.tab.preview_plan['recipe_id'] == 'spider-man-2'
    assert not case.tab.preview_plan['errors'], case.tab.preview_plan
    app = case.app
    ImageGrab.grab(bbox=(app.winfo_rootx(), app.winfo_rooty(), app.winfo_rootx()+app.winfo_width(), app.winfo_rooty()+app.winfo_height())).save('audit/spider-settings-preview.png')
finally:
    case.doCleanups()
