"""
The Model logic for the application following the MVVM pattern.

Should not import ViewModel nor any PySide
The model shall not keep memory of the View state

Usage: main.py, QuadViewModel.py
"""
import sys
import pathlib
import numpy as np
import copy
import inspect
import importlib.util
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

    @staticmethod
    def import_custom_data_points(filepath: pathlib.Path, data: dict) -> dict:
        """
        Loads a Python module and searches for functions that takes one argument (the data) and returns a tuple (x, y).
        If found, its results are stored in a dictionary with the parent key as func name and children "x" and "y".

        :param filepath: Path to the Python file containing the custom functions.
        :param data: The preloaded data dictionary.
        :return: Dict {<func_name>: {x:, y:}}
        """
        # Load the module from the given file path, the name is arbitrary given
        spec = importlib.util.spec_from_file_location("unique_name_foad_f38aa4b22c", filepath)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        # Find potential candidate functions
        candidates = []
        for func_name in dir(module):
            if not func_name.startswith("__"):                      # Does not start with __
                func_handle = getattr(module, func_name)
                if callable(func_handle):                           # Is callable (to prevent imports like numpy)
                    params = inspect.signature(func_handle)
                    if len(params.parameters) == 1:                 # Has only one parameter, e.g., foo(x)
                        candidates.append((func_name, func_handle))

        if not candidates:
            return {}

        # Init
        custom_items = {}
        for candidate in candidates:
            func_name, func = candidate

            try:
                # Deepcopy because we can't trust that the functions do not accidentally modify the original data
                temp_data = copy.deepcopy(data)
                result = func(temp_data)
            except Exception as e:
                print(f"\033[91mCould not parse {func_name} in file {filepath} due to {type(e).__name__}: {e}\033[0m")
                continue

            # Validate
            if not (isinstance(result, tuple) and len(result) == 2):
                continue

            x, y = result
            if len(x) == 0 or len(y) == []:
                continue

            custom_items[func_name] = {}
            custom_items[func_name]["x"] = x
            custom_items[func_name]["y"] = y

        return custom_items

    @staticmethod
    def format_data_insight(data: dict) -> str:
        """
        Formats a dict into a readable and structured (left-aligned) string, where keys and values are aligned.
        :param data:
        :return:
        """
        if not data:
            return ""

        # Determine the maximum width for keys, values, and units, +1 for adding the colon back
        max_key_length = max(len(key) for key in data.keys()) + 1
        max_value_length = max(len(f"{value:.2f}") for value in data.values())

        # Reformat the string
        formatted_lines = [f"{key + ':':<{max_key_length}} {value:>{max_value_length}.2f}" for
                           key, value in data.items()]

        return "\n".join(formatted_lines)


if __name__ == '__main__':
    pass