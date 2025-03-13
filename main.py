"""
Main program to run the non-compiled app
This file should be kept to a minimum and not handle any logic.

Usage: build.py
"""
import sys
import os
from PySide6.QtWidgets import QApplication

from model.QuadModel import QuadModel
from view.QuadView import QuadView
from viewmodel.QuadViewModel import QuadViewModel

app = QApplication(sys.argv)
app.setStyleSheet("* {font-family: Roboto;"
                  "font-size: 12px;}")
model = QuadModel()
view_model = QuadViewModel(model)
view = QuadView(view_model)
view.show()

# Handles Nuitka splash screen
if "NUITKA_ONEFILE_PARENT" in os.environ:
    import tempfile

    splash_filename = os.path.join(
        tempfile.gettempdir(),
        "onefile_%d_splash_feedback.tmp" % int(os.environ["NUITKA_ONEFILE_PARENT"]),
    )

    if os.path.exists(splash_filename):
        os.unlink(splash_filename)

# Handles PyInstaller splash screen
if getattr(sys, "frozen", False):
    import pyi_splash  # noqa
    pyi_splash.close()

sys.exit(app.exec())
