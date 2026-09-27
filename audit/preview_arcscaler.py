"""Deterministic visual smoke run using isolated fixtures; no real games touched."""
from pathlib import Path
import sys,os,tempfile,time,json
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT),str(ROOT/'.audit-deps')]
from unittest.mock import patch
from tests.fixtures import game,package
from PIL import ImageGrab
from gui.main_window import MainWindow

def run():
    with tempfile.TemporaryDirectory() as td:
        root=Path(td);package(root/'assets')
        os.environ['ARCSCALER_DATA_DIR']=str(root)
        with patch('gui.main_window.prepare_assets',return_value=root/'assets'),patch('core.version_manager.urllib.request.urlopen',side_effect=OSError('Offline visual fixture')):
            app=MainWindow();errors=[]
            app.report_callback_exception=lambda *args:errors.append(str(args[1]))
            for name in ["Marvel's Spider-Man 2",'Cyberpunk 2077','Alan Wake 2','Hogwarts Legacy','Ghost of Tsushima']:
                profile=app.library.add_game_by_path(str(game(root/name,name+'.exe')))
                app.library.update_profile(profile['id'],{'name':name})
            selected=list(app.library.profiles.values())[1]
            app._on_game_selected_from_library(selected)
            app.config_tab.upscaler_var.set(True);app.config_tab.quality_var.set('Quality');app.config_tab._toggle_mode('upscaler_enabled')
            app.geometry('1100x720+60+60')
            def pump(seconds):
                end=time.monotonic()+seconds
                while time.monotonic()<end:app.update();time.sleep(.02)
            pump(3)
            for screen in ['Library','Downloads','Hardware','Log','App settings']:
                app.select_tab(screen);pump(.3)
                x,y=app.winfo_rootx(),app.winfo_rooty()
                ImageGrab.grab(bbox=(x,y,x+app.winfo_width(),y+app.winfo_height())).save(ROOT/'audit'/('arcscaler-'+screen.lower().replace(' ','-')+'.png'))
            app.select_tab('Library');app.config_tab._game_menu();pump(.2)
            x,y=app.winfo_rootx(),app.winfo_rooty()
            ImageGrab.grab(bbox=(x,y,x+app.winfo_width(),y+app.winfo_height())).save(ROOT/'audit/arcscaler-game-menu.png')
            app.config_tab.game_menu.destroy()
            app.config_tab.frame_gen_var.set(True);app.config_tab._toggle_mode('frame_gen_enabled');pump(.2)
            x,y=app.winfo_rootx(),app.winfo_rooty()
            ImageGrab.grab(bbox=(x,y,x+app.winfo_width(),y+app.winfo_height())).save(ROOT/'audit/arcscaler-fg.png')
            app.library.profiles.clear();app.library_tab.refresh_library()
            app.config_tab.show_empty(app.library_tab);pump(.2)
            ImageGrab.grab(bbox=(x,y,x+app.winfo_width(),y+app.winfo_height())).save(ROOT/'audit/arcscaler-empty.png')
            print(json.dumps({'title':app.title(),'screens':list(app.views),'callback_errors':errors}))
            app._on_close()
            if errors:raise RuntimeError(errors)
if __name__=='__main__':run()
