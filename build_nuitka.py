import os
import sys
import subprocess


def build_project(dev_mode=False):
    """
    Builds the application using Nuitka.

    Bundles the interpreter, dependencies, and assets (icons, images, splash screen) into a standalone executable.
    In development mode, the output filename indicates a development build.
    In production mode, the console window is disabled and link-time optimization is enabled.
    """
    # Initialize asset paths
    icons_path = os.path.join("assets", "icons")
    img_path = os.path.join("assets", "images")
    exe_icon = os.path.join("assets", "icons", "gui_logo.ico")
    splash_screen = os.path.join("assets", "images", "splash_screen.png")

    # Build the base Nuitka command
    base_cmd = (
        f'{sys.executable} -m nuitka --standalone --onefile --enable-plugin=pyside6 '
        f'--include-data-dir={icons_path}=assets/icons '
        f'--include-data-dir={img_path}=assets/images '
        f'--onefile-windows-splash-screen-image={splash_screen} '
        f'--windows-icon-from-ico={exe_icon} '
    )

    # Determine output filename and additional flags based on dev_mode
    if dev_mode:
        out_filename = "QuadViewAnalyzer_dev"
    else:
        out_filename = "QuadViewAnalyzer"
        base_cmd += " --windows-console-mode=attach --lto=yes"

    # Construct full command with entry point
    cmd = f"{base_cmd} --output-filename={out_filename} main.py"

    print("Running command:")
    print(cmd)

    # Execute the command and check for errors
    result = subprocess.run(cmd, shell=True)
    if result.returncode != 0:
        print(f"Build failed with return code: {result.returncode}")
    else:
        print(f"Compiled for {'development' if dev_mode else 'production'}!")


if __name__ == "__main__":
    build_project(dev_mode=False)
