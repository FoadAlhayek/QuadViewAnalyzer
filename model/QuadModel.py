"""
The Model logic for the application following the MVVM pattern.

Should not import ViewModel nor any PySide
The model shall not keep memory of the View state

Usage: main.py, QuadViewModel.py
"""
import sys
import pathlib
import numpy as np
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

    @staticmethod
    def isinstance_sequence(arr):
        """ Helper function to determine if the variable is a sequence/list. """
        return isinstance(arr, (list, tuple, np.ndarray))

    def min_dict_value(self, data: dict, keys: list[str]) -> float | None:
        """
        Finds the minimum value from a nested dictionary for any of the specified keys.
        The values must be either a single numeric value or a 1D array-like sequence.
        This function does not support multidimensional arrays.

        :param data: A (nested) dictionary containing 1D array data.
        :param keys: A list of keys to search for.
        :return: The smallest numeric value found, or None if no valid candidate is found.
        """
        min_val: float | None = None
        keys = set(keys)
        is_seq = self.isinstance_sequence # Cache locally, optimization
        stack = [data]

        while stack:
            current = stack.pop()

            if isinstance(current, dict):
                for key, val in current.items():
                    if key in keys:
                        if is_seq(val) and len(val) > 0:
                            candidate = val[0]
                        else:
                            candidate = val
                        try:
                            candidate = float(candidate)
                        except (TypeError, ValueError):
                            continue
                        if min_val is None or candidate < min_val:
                            min_val = candidate

                    # Add nested dictionaries to the stack
                    if isinstance(val, dict):
                        stack.append(val)
                    elif is_seq(val):
                        # Extend the stack with any dicts found in the list
                        stack.extend([item for item in val if isinstance(item, dict)])
            elif is_seq(current):
                stack.extend([item for item in current if isinstance(item, dict)])

        return min_val


if __name__ == '__main__':
    pass