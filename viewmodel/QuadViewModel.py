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
    signal_new_data_loaded = Signal()                     # Notifies the View that a new data file is loaded
    signal_add_plot = Signal(QStandardItem, list)  # Notifies the View to plot a newly added item
    signal_chosen_item_data_updated = Signal()            # Notifies the View that the chosen item data is updated
    signal_update_ts_bar_placeholder = Signal()           # Notifies the View to update the placeholder text in ts bar
    signal_data_addition = Signal(str, list)

    def __init__(self, model):
        super().__init__()
        self._model = model
        self.mat = pathlib.Path("")
        self.dat = pathlib.Path("")
        self.loaded_data = {}
        self.selected_signals_data = {}
        self.accepted_file_types = [".mat", ".dat", ".conf", ".py"]
        self._proxy_model = CustomFilterProxyModel()
        self.global_ts_ref = None
        self.loaded_ts_ref = None

        # Init search filter timer
        self.search_timer = QTimer()
        self.search_timer.setSingleShot(True)
        self.search_timer.timeout.connect(self.apply_filter)
        self.latest_search_text = ""

    def get_current_ts_placeholder_text(self):
        """ Helper function to return concise f-string for the placeholder text. """
        return f"Reference ts: {self.global_ts_ref}"

    def reset_global_ts_ref(self) -> bool:
        """ Resets the timestamp to the most optimal value derived from the loaded data. """
        return self.update_global_ts_ref(self.loaded_ts_ref)

    def is_mat_loaded(self) -> bool:
        return self.mat.suffix == ".mat" and self.loaded_data != {}

    def set_and_load_mat(self, path: pathlib.Path):
        """ Only function that handles loading in the .mat data into the backend-memory. """
        if path.suffix == ".mat":
            self.mat = path
            self.loaded_data = self._model.load_mat(self.mat)
            self.loaded_ts_ref = self._model.min_dict_value(self.loaded_data, ["TimestampLogfile"])
            self.global_ts_ref = self.loaded_ts_ref
            self.signal_new_data_loaded.emit()

    def add_custom_data_points(self, path: pathlib.Path, parent_key: str = "CustomItems") -> None:
        custom_data_points = self._model.import_custom_data_points(path, self.loaded_data)

        if custom_data_points == {}:
            return

        if parent_key not in self.loaded_data:
            self.loaded_data[parent_key] = {}

        self.loaded_data[parent_key] = custom_data_points
        self.signal_data_addition.emit(parent_key, list(custom_data_points.keys()))

    def update_tree_model(self):
        """ Regenerate the tree model from the loaded data and update the proxy model. """
        tree_model = self._model.generate_tree_model(self.loaded_data)
        self._proxy_model.setSourceModel(tree_model)
        return self._proxy_model

    def update_global_ts_ref(self, ts: float) -> bool:
        try:
            ts = float(ts)
        except (ValueError, TypeError):
            return False

        # TODO: Allow ts == 0 now until the ts_raw can be plotted, so one can seamlessly switch between ts and ts_raw
        if self.global_ts_ref == ts:
            return False

        if not self.is_mat_loaded():
            return False

        # Update and recompute ts in memory
        self.global_ts_ref = ts

        if self.selected_signals_data == {}:
            self.signal_update_ts_bar_placeholder.emit()
            return False

        for item in self.selected_signals_data.values():
            item["ts"] = item["ts_raw"] - self.global_ts_ref

        # Notify the View the memory has been updated
        self.signal_chosen_item_data_updated.emit()
        return True

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
        # To prevent loading in multiple mat files at the same time
        current_mat = pathlib.Path("")
        current_dat = pathlib.Path("")
        config_files = []
        pyfiles = []

        # Loop over all dropped files and only consider the latest of each file type
        for filepath in filepaths:
            file_ext = filepath.suffix

            if file_ext == ".mat":
                current_mat = filepath
            elif file_ext == ".dat":
                current_dat = filepath
            elif file_ext == ".conf":
                config_files.append(filepath)
            elif file_ext == ".py":
                pyfiles.append(filepath)

        # Update - important, always parse the .mat file first
        if current_mat.is_file():
            self.set_and_load_mat(current_mat)

        if current_dat.is_file():
            self.dat = current_dat
            self.update_video_file()

        if pyfiles:
            for pyfile in pyfiles:
                try:
                    self.add_custom_data_points(pyfile)
                except Exception as e:
                    print(f"\033[91mCould not parse {pyfile} due to {type(e).__name__}: {e}\033[0m")
                    continue

        if config_files:
            for conf in config_files:
                self.parse_and_load_conf(conf)

    def get_data_insight(self) -> str:
        di_dict = {}
        for parent, item in self.selected_signals_data.items():
            for child, val in item.items():
                if child == "ts" or child == "ts_raw":
                    continue

                if isinstance(val, dict):   # Handle custom items
                    for c, v in val.items():
                        if c == "ts" or c == "ts_raw":
                            continue
                        di_dict[child] = v[0]
                else:
                    di_dict[child] = val[0]

        return self._model.format_data_insight(di_dict)

    def get_signal_data(self, item_path) -> tuple[list, list, str]:
        """
        Retrieves the timestamp, values, and signal name from the backend-memory.
        :param item_path: List of strings representing the path in either the tree or "parent/child" in memory.
        :return: A tuple containing the timestamps, values, and signal name.
        """
        ts = []
        val = []
        signal_name = ""

        if self._model.invalid_signal(item_path):
            return ts, val, signal_name

        parent = item_path[-2]
        child = item_path[-1]

        if parent in self.selected_signals_data:
            if child in self.selected_signals_data[parent]:
                if isinstance(self.selected_signals_data[parent][child], dict): # handles the custom added items
                    ts = self.selected_signals_data[parent][child]["ts"]
                    val = self.selected_signals_data[parent][child]["val"]
                    signal_name = f"{parent}/{child}"
                else:
                    ts = self.selected_signals_data[parent]["ts"]
                    val = self.selected_signals_data[parent][child]
                    signal_name = f"{parent}/{child}"

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

        This is the only function that handles deleting chosen item data from the backend-memory.

        :param signal_path: An array where each element is a key in a dict
        :return: Bool if the signal was removed and the signal name that was deleted
        """
        signal_name = ""
        if self._model.invalid_signal(signal_path):
            return False, signal_name

        parent = signal_path[-2]
        child = signal_path[-1]

        try:
            # Delete the entire parent dict if only the ts, ts_raw and child key exists, otherwise delete the child only
            if len(self.selected_signals_data[parent]) <= 3:
                del self.selected_signals_data[parent]
            else:
                del self.selected_signals_data[parent][child]
            signal_name = f"{parent}/{child}"
        except KeyError:
            return False, signal_name

        return True, signal_name

    def select_item(self, signal_path: list) -> bool:
        """
        Stores user-picked signals in a dict with their corresponding timestamp.
        Dict format: {parent1: {ts, child1, child2}, parent2: {ts, child1}}

        This is the only function that handles adding chosen item data to the backend-memory.

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
        child = signal_path[-1]

        # Traverse up to the second-last key
        for key in signal_path[:-1]:
            temp_data = temp_data.get(key, {})

        if temp_data == {}:
            return False

        if "TimestampLogfile" in temp_data:
            parent = signal_path[-2]

            # No need to store the same ts
            if parent not in self.selected_signals_data:
                ts = temp_data.get("TimestampLogfile").copy()

                # Adjust the timestamp based on global ts reference
                if self.global_ts_ref is not None and self.global_ts_ref != 0:
                    ts -= self.global_ts_ref

                # Add modified ts and original
                self.selected_signals_data[parent] = {"ts": ts}
                self.selected_signals_data[parent]["ts_raw"] = temp_data.get("TimestampLogfile")
        elif isinstance(temp_data[child], dict): # handle custom items
            child_data = temp_data.get(child, [])
            ts = child_data.get("x").copy()

            # Adjust the timestamp based on global ts reference
            if self.global_ts_ref is not None and self.global_ts_ref != 0:
                ts -= self.global_ts_ref

            parent = signal_path[-2]
            if parent not in self.selected_signals_data:
                self.selected_signals_data[parent] = {}

            self.selected_signals_data[parent][child] = {"ts": ts}
            self.selected_signals_data[parent][child]["ts_raw"] = child_data.get("x")
            self.selected_signals_data[parent][child]["val"] = child_data.get("y")
            return True

        if not parent:
            print(f"Timestamp for {child} was not found! Skipping signal.")
            return False

        self.selected_signals_data[parent][child] = temp_data.get(child, [])
        return True

if __name__ == '__main__':
    pass
