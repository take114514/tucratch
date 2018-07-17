import sys
from cx_Freeze import setup, Executable

includes = []
excludes = ['_gtkagg', '_tkagg', 'bsddb', 'curses', 'pywin.debugger',
             'pywin.debugger.dbgcon', 'pywin.dialogs', 'tcl',
             'Tkconstants', 'Tkinter', 'Flask']

base = None
if sys.platform == "win32":
    base = "Win32GUI"

setup(  name = "tucratch",
        version = "0.3",
        options = {"build_exe": {"includes": includes,"excludes": excludes}},
        executables = [Executable("tucratch.py", base=base, icon="assets/appicon.ico")])
