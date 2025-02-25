"""
The Model logic for the application following the MVVM pattern.

Should not import ViewModel nor any PySide
The model shall not keep memory of the View state

Usage: main.py, QuadViewModel.py
"""
import sys
import pathlib
from PySide6.QtGui import QStandardItem, QStandardItemModel

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
    def load_mat(filepath):
        return loadmat(filepath)

    @staticmethod
    def parse_conf(path: pathlib.Path, sep=";"):
        if path.suffix != ".conf":
            return []

        parsed_data = []
        with open(path, "r", encoding="utf-8") as fid:
            for row in fid:
                row = row.strip()

                # Skip empty lines and comments
                if not row or row.startswith('#'):
                    continue

                # Split based on sep and handle edge case of removing empty strings (caused by excess of sep)
                items = [item.strip() for item in row.split(sep)]
                items = [item for item in items if item.strip()]
                parsed_data.append(items)
        return parsed_data

    @staticmethod
    def invalid_signal(path) -> bool:
        """ Function can be expanded in the future """
        return len(path) < 2

    @staticmethod
    def generate_tree_model(data) -> QStandardItemModel:
        """ Transform a nested dictionary's keys into a QT tree menu. """
        model = QStandardItemModel()
        model.setHorizontalHeaderLabels(["Signals"])

        if data == {}:
            return model

        root_item = model.invisibleRootItem()
        stack = [(root_item, data)]

        while stack:
            parent, current_data = stack.pop()

            if isinstance(current_data, dict):
                for key, value in current_data.items():
                    key_item = QStandardItem(str(key))
                    parent.appendRow(key_item)

                    if isinstance(value, dict):
                        stack.append((key_item, value))
        return model

if __name__ == '__main__':
    pass
