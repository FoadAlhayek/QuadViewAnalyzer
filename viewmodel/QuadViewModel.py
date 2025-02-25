"""
The ViewModel logic for the application following the MVVM pattern.

The ViewModel is allowed to import the Model and View.
The ViewModel creates the signals and emits them. ViewModel also handles preparing the data for presentation.
For example, adding two arrays is handled by the Model, ViewModel arranges the array are in a specific shape and
emits back the result to the View.

Usage: main.py, QuadView.py
"""
import pathlib
from PySide6.QtCore import QObject, Signal, QRegularExpression, QTimer, QAbstractItemModel
from PySide6.QtGui import QStandardItem, QStandardItemModel

# Internal imports
from viewmodel.helpers.tree_menu_search_filter import CustomFilterProxyModel

class QuadViewModel(QObject):
    # Signals are initialize here - Signal(args) need to match with the emit and the function it connects to
    signal_new_data_loaded = Signal()   # Signal to notify the View that a new data file is loaded
    signal_add_plot = Signal(QStandardItem, list)

    def __init__(self, model):
        super().__init__()
        self._model = model
        self.mat = pathlib.Path("")
        self.dat = pathlib.Path("")
        self.loaded_data = {}
        self.selected_signals_data = {}
        self.accepted_file_types = [".mat", ".dat", ".conf"]
        self._proxy_model = CustomFilterProxyModel()

        # Init search filter timer
        self.search_timer = QTimer()
        self.search_timer.setSingleShot(True)
        self.search_timer.timeout.connect(self.apply_filter)
        self.latest_search_text = ""

    def is_mat_loaded(self) -> bool:
        return self.mat.suffix == ".mat" and self.loaded_data != {}

    def set_and_load_mat(self, path: pathlib.Path):
        """ Stores the path of the selected file. """
        if path.suffix == ".mat":
            self.mat = path
            self.loaded_data = self._model.load_mat(self.mat)
            self.signal_new_data_loaded.emit()

    def reload_mat(self):
        self.loaded_data = self._model.load_mat(self.mat)

    def update_tree_model(self):
        """ Regenerate the tree model from the loaded data and update the proxy model. """
        tree_model = self._model.generate_tree_model(self.loaded_data)
        self._proxy_model.setSourceModel(tree_model)
        return self._proxy_model

    def set_filter_text(self, text: str):
        """
        The filter text is set here. The filtering process is initiated in apply_filter() after a brief delay,
        allowing time for any additional key presses before processing.

        :param text: Search query text
        """
        self.search_timer.stop()          # Stops the timer
        self.search_timer.start(200)      # Restart the timer
        self.latest_search_text = text    # Sets the latest text

    def apply_filter(self):
        """ Converts a wildcard search into a regex pattern and sets the filter when the search_timer hits 0. """
        pattern = self.latest_search_text.replace("*", ".*")
        regex = QRegularExpression(pattern)
        regex.setPatternOptions(QRegularExpression.PatternOption.CaseInsensitiveOption)
        self._proxy_model.setFilterRegularExpression(regex)

    def deselect_all_signals(self):
        self.selected_signals_data = {}

    def update_video_file(self):
        pass

    def find_tree_item_by_path(self, item_path: list) -> QStandardItem | None:
        """
        Traverses the tree model and returns the QStandardItem corresponding to the given hierarchical path.

        :param item_path: List of strings representing the path in the tree, e.g., ["A", "B", "C"]
        :return: QStandardItem corresponding to the path or None if not found.
        """
        tree_model: QStandardItemModel | QAbstractItemModel = self._proxy_model.sourceModel()
        current_item = tree_model.invisibleRootItem()

        for key in item_path:
            found = None

            for row in range(current_item.rowCount()):
                child = current_item.child(row)

                if child.text() == key:
                    found = child
                    break

            if found is None:
                return None

            current_item = found
        return current_item

    def parse_and_load_conf(self, path: pathlib.Path):
        """
        Parses the configuration file, extracts the signals, and updates the view if they exist by emitting the item and
        item path with the Signal "signal_add_plot".

        :param path: Path to the configuration file.
        """
        parsed_conf_data = self._model.parse_conf(path, sep=";")

        for item_path in parsed_conf_data:
            if self.is_signal_already_selected(item_path):
                continue

            item_added = self.select_item(item_path)
            if item_added:
                item = self.find_tree_item_by_path(item_path)

                # Mismatch between data and tree menu (should not be possible due to item_added)
                if item is None:
                    self.deselect_item(item_path)
                    return

                self.signal_add_plot.emit(item, item_path)

    def handle_dropped_files(self, filepaths: list[pathlib.Path]):
        # To prevent loading in multiple files at the same time
        current_mat = pathlib.Path("")
        current_dat = pathlib.Path("")
        current_conf = pathlib.Path("")

        # Loop over all dropped files and only consider the latest of each file type
        for filepath in filepaths:
            file_ext = filepath.suffix

            if file_ext == ".mat":
                current_mat = filepath
            elif file_ext == ".dat":
                current_dat = filepath
            elif file_ext == ".conf":
                current_conf = filepath

        # Update - important, always parse the .mat file first
        if current_mat.is_file():
            self.set_and_load_mat(current_mat)

        if current_dat.is_file():
            self.dat = current_dat
            self.update_video_file()

        if current_conf.is_file():
            self.parse_and_load_conf(current_conf)

    def get_signal_data(self, signal_path) -> tuple[list, list, str]:
        ts = []
        val = []
        signal_name = ""

        if self._model.invalid_signal(signal_path):
            return ts, val, signal_name

        parent = signal_path[-2]
        child = signal_path[-1]

        if parent in self.selected_signals_data:
            if child in self.selected_signals_data[parent]:
                ts = self.selected_signals_data[parent]["ts"]
                val = self.selected_signals_data[parent][child]
                signal_name = parent + "/" + child

        return ts, val, signal_name

    def is_signal_already_selected(self, signal_path: list) -> bool:
        """
        Helper function for the View, to know if the signal is selected and exists already in the backend (ViewModel).
        :param signal_path: An array where each element is a key in a dict
        :return: Bool if the signal exists in ViewModel.
        """
        if self._model.invalid_signal(signal_path):
            return False

        parent = signal_path[-2]
        child = signal_path[-1]

        if parent in self.selected_signals_data:
            if child in self.selected_signals_data[parent]:
                return True

        return False

    def deselect_item(self, signal_path: list) -> tuple[bool, str]:
        """
        Deselects the signal, see select_item() for more information.
        :param signal_path: An array where each element is a key in a dict
        :return: Bool if the signal was removed and the signal name that was deleted
        """
        signal_name = ""
        if self._model.invalid_signal(signal_path):
            return False, signal_name

        parent = signal_path[-2]
        child = signal_path[-1]

        try:
            # Delete the entire parent dict if only the ts and child key exists, otherwise delete the child only
            if len(self.selected_signals_data[parent]) <= 2:
                del self.selected_signals_data[parent]
            else:
                del self.selected_signals_data[parent][child]
            signal_name = parent + "/" + child
        except KeyError:
            return False, signal_name

        return True, signal_name

    def select_item(self, signal_path: list) -> bool:
        """
        Stores user-picked signals in a dict with their corresponding timestamp.
        Dict format: {parent1: {ts, child1, child2}, parent2: {ts, child1}}

        NOTE: The function does not consider if the same parent-child exists in a different grandparent, e.g.,
        grandparent1-parent1-child1 and grandparent2-parent1-child1, the grandparent2's parent-child will override the
        original values. If that is an issue, expand the function to handle that scenario. For now, too much overhead.

        :param signal_path: An array where each element is a key in a dict
        :return: Bool if the signal was added
        """
        if self._model.invalid_signal(signal_path):
            return False

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
        if not parent:
            print(f"Timestamp for {signal_key} was not found! Skipping signal.")
            return False

        self.selected_signals_data[parent][signal_key] = temp_data.get(signal_key, [])
        return True

if __name__ == '__main__':
    pass
