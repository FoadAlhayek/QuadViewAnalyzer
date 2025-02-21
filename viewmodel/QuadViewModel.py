"""
The ViewModel logic for the application following the MVVM pattern.

The ViewModel is allowed to import the Model and View.
The ViewModel creates the signals and emits them. ViewModel also handles preparing the data for presentation.
For example, adding two arrays is handled by the Model, ViewModel arranges the array are in a specific shape and
emits back the result to the View.

Usage: main.py, QuadView.py
"""
import pathlib
from PySide6.QtCore import QObject, QUrl, Qt, Signal
from PySide6.QtGui import QStandardItem, QStandardItemModel

class QuadViewModel(QObject):
    # Signals are initialize here - Signal(args) need to match with the emit and the function it connects to
    signal_new_data_loaded = Signal()

    def __init__(self, model):
        super().__init__()
        self._model = model
        self.mat = pathlib.Path("")
        self.loaded_data = {}
        self.selected_signals = {}
        self.selected_signals_data = {}
        self.accepted_file_types = [".mat", ".dat"]

    def set_mat(self, path: pathlib.Path):
        """ Stores the path of the selected file. """
        if path.suffix == ".mat":
            self.mat = path

    def loadmat(self):
        self.loaded_data = self._model.loadmat(self.mat)

    def start_qva(self):
        print("Hello", self._model.ready_to_run(self.mat), self.mat)
        if not self._model.ready_to_run(self.mat):
            print("Test")
            return None

    def handle_dropped_files(self, filepaths: list[pathlib.Path]):
        # To prevent loading in multiple files at the same time
        current_mat = pathlib.Path("")
        current_dat = pathlib.Path("")

        for filepath in filepaths:
            file_ext = filepath.suffix

            if file_ext == ".mat":
                current_mat = filepath
            elif file_ext == ".dat":
                current_dat = filepath
            else:
                continue

        if current_mat.is_file():
            print(current_mat)

        if current_dat.is_file():
            print(current_dat)

    def handle_item_selected(self, signal_path: list):
        """
        Stores user-picked signals in a dict with their corresponding timestamp.
        Dict format: {parent1: {ts, child1, child2}, parent2: {ts, child1}}

        NOTE: The function does not consider if the same parent-child exists in a different grandparent, e.g.,
        grandparent1-parent1-child1 and grandparent2-parent1-child1, the grandparent2's parent-child will override the
        original values. If that is an issue, expand the function to handle that scenario. For now, too much overhead.

        :param signal_path: An array where each element is a key in a dict
        """
        temp_data = self.loaded_data
        parent = None

        # Traverse up to the second-last key
        for key in signal_path[:-1]:
            temp_data = temp_data.get(key, {})

        if "TimestampLogfile" in temp_data:
            parent = signal_path[-2]

            # No need to store the same ts
            if parent not in self.selected_signals_data:
                self.selected_signals_data[parent] = {"ts": temp_data.get("TimestampLogfile", [])}

        signal_key = signal_path[-1]
        if parent:
            self.selected_signals_data[parent][signal_key] = temp_data.get(signal_key, [])
        else:
            print(f"Timestamp for {signal_key} was not found! Skipping signal.")

    def generate_tree_model(self) -> QStandardItemModel:
        """ Transform a nested dictionary's keys into a QT tree menu. """
        model = QStandardItemModel()
        model.setHorizontalHeaderLabels(["Signals"])

        # TODO, DELETE THIS LATER WHEN LOADING WORKS
        self.set_mat(pathlib.Path(r"C:\Users\foadal\Documents\Tools\AnalysTool_JN\data\coll_fcw_aeb.mat"))
        self.loadmat()

        if self.loaded_data == {}:
            return model

        root_item = model.invisibleRootItem()
        stack = [(root_item, self.loaded_data)]

        while stack:
            current_dict, current_data = stack.pop()

            if isinstance(current_data, dict):
                for key, value in current_data.items():
                    key_item = QStandardItem(str(key))
                    current_dict.appendRow(key_item)

                    if isinstance(value, dict):
                        stack.append((key_item, value))
        return model

if __name__ == '__main__':
    pass
