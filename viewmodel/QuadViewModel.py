"""
The ViewModel logic for the application following the MVVM pattern.

The ViewModel is allowed to import the Model and View.
The ViewModel creates the signals and emits them. ViewModel also handles preparing the data for presentation.
For example, adding two arrays is handled by the Model, ViewModel arranges the array are in a specific shape and
emits back the result to the View.

Usage: main.py, QuadView.py
"""
import pathlib
from PySide6.QtCore import QObject, Signal, QRegularExpression, QTimer

# Internal imports
from viewmodel.helpers.tree_menu_search_filter import CustomFilterProxyModel

class QuadViewModel(QObject):
    # Signals are initialize here - Signal(args) need to match with the emit and the function it connects to
    signal_new_data_loaded = Signal()   # Signal to notify the View that a new data file is loaded

    def __init__(self, model):
        super().__init__()
        self._model = model
        self.mat = pathlib.Path("")
        self.dat = pathlib.Path("")
        self.loaded_data = {}
        self.selected_signals_data = {}
        self.accepted_file_types = [".mat", ".dat"]
        self._proxy_model = CustomFilterProxyModel()

        # Init search filter timer
        self.search_timer = QTimer()
        self.search_timer.setSingleShot(True)
        self.search_timer.timeout.connect(self.apply_filter)
        self.latest_search_text = ""

    def set_mat(self, path: pathlib.Path):
        """ Stores the path of the selected file. """
        if path.suffix == ".mat":
            self.mat = path

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

    def loadmat(self):
        self.loaded_data = self._model.loadmat(self.mat)

    def deselect_all_signals(self):
        self.selected_signals_data = {}

    def update_data_file(self):
        self.loadmat()
        self.signal_new_data_loaded.emit()

    def update_video_file(self):
        pass

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

        # Update
        if current_mat.is_file():
            self.mat = current_mat
            self.update_data_file()

        if current_dat.is_file():
            self.dat = current_dat
            self.update_video_file()

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
