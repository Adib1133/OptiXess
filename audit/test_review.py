"""The review acceptance cases now live in the maintained regression suite.

Original pre-fix reproductions are preserved in historical/test_review_original.py.txt.
"""
from pathlib import Path
import runpy
if __name__ == '__main__':
    runpy.run_path(str(Path(__file__).with_name('run_checks.py')), run_name='__main__')
