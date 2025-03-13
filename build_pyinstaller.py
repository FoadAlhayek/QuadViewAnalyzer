"""
Builds the main.py into an app (.exe), either in development or production mode.

Usage: -
"""
import os
import sys
import subprocess

dev_mode = True

# Init paths
icons_path = os.path.join("assets", "icons")
img_path = os.path.join("assets", "images")
exe_icon = os.path.join("assets", "icons", "gui_logo.ico")
splash_screen = os.path.join("assets", "images", "splash_screen.png")

console_call = str(
    f'{sys.executable} -m PyInstaller main.py --onefile --clean '  # General settings
    f'--add-data={icons_path}{os.pathsep}{icons_path} '    # Icons
    f'--add-data={img_path}{os.pathsep}{img_path} '        # Images
    f'--icon={exe_icon} '                                  # Add exe icon
    f'--splash={splash_screen}'                            # Splash screen
)


if dev_mode:
    console_call += ' --name QuadViewAnalyzer_dev'
else:
    console_call += ' --name QuadViewAnalyzer --noconsole --optimize 2'

# Print info and make a cmd call to build
print(console_call)
subprocess.call(console_call)
print(f"Compiled for {'development' if dev_mode else 'production'}!")
