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
    def ready_to_run(mat_path: pathlib.Path):
        return mat_path.is_file() and mat_path.suffix == ".mat"

    @staticmethod
    def loadmat(filepath):
        return loadmat(filepath)


if __name__ == '__main__':
    pass
