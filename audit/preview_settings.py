import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from tests.test_gui_integration import GUIIntegrationTests
from PIL import ImageGrab
case = GUIIntegrationTests()
case.setUp()
try:
    case.app.deiconify()
    case.app.geometry('1200x860+40+40')
    case.app.update()
    case.pump()
    app=case.app
    ImageGrab.grab(bbox=(app.winfo_rootx(), app.winfo_rooty(), app.winfo_rootx()+app.winfo_width(), app.winfo_rooty()+app.winfo_height())).save('audit/settings-preview.png')
finally:
    case.doCleanups()
