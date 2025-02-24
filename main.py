"""
Main program to run the non-compiled app
This file should be kept to a minimum and not handle any logic.

Usage: build.py
"""
import sys
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

if getattr(sys, 'frozen', False):
    import pyi_splash # noqa
    pyi_splash.close()

sys.exit(app.exec())
