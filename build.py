"""
Builds the main.py into an app (.exe), either in development or production mode.

Usage: -
"""
import subprocess
import os

# Dev mode?
dev_mode = False

# Init paths
fonts_path = os.path.join("assets", "fonts")
icons_path = os.path.join("assets", "icons")
img_path = os.path.join("assets", "images")
config_path = os.path.join("configuration")
exe_icon = os.path.join("assets", "icons", "gui_logo.ico")
splash_screen = os.path.join("assets", "images", "splash_screen.png")