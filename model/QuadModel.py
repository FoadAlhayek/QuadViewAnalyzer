"""
The Model logic for the application following the MVVM pattern.

Should not import ViewModel nor any PySide
The model shall not keep memory of the View state

Usage: main.py, QuadViewModel.py
"""
import pathlib
import sys

# Internal imports
from model.helpers.mat_loader import loadmat

class QuadModel:
    def __init__(self):
        # Get the path to the folder containing the running script (required for exe to work properly)
        if getattr(sys, 'frozen', False):
            self.app_path = sys._MEIPASS  # noqa
        else:
            self.app_path = pathlib.Path(__file__).parent.parent

    @staticmethod
    def loadmat(filepath):
        return loadmat(filepath)

    @staticmethod
    def invalid_signal(path) -> bool:
        """ Function can be expanded in the future """
        return len(path) < 2

if __name__ == '__main__':
    pass
