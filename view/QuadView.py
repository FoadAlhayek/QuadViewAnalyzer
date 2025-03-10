"""
The View logic for the application following the MVVM pattern.

The View is allowed to import ViewModel but not the Model!
The View connects signals from the ViewModel and a function with equal amounts of emit

Usage: main.py, QuadViewModel.py
"""
import sys
import pathlib
import numpy as np
import pyqtgraph as pg
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QSplitter, QAbstractItemView, QMainWindow, QTextEdit,
                               QLineEdit)
from PySide6.QtGui import QIcon, QDragEnterEvent, QColor, QStandardItemModel, QStandardItem, QFont
from PySide6.QtCore import Qt, QSortFilterProxyModel, QAbstractItemModel, QModelIndex

# Internal imports
import assets.widgets as c_widgets
from assets.palettes.Palette import LightTheme, DarkTheme  # noqa
from assets.palettes.Colormap import Colormap

class QuadView(QMainWindow):
    def __init__(self, view_model):
        super().__init__()

        # Init the ViewModel and connect the signals with a method
        self._view_model = view_model
        self._view_model.signal_new_data_loaded.connect(self.on_data_file_load)
        self._view_model.signal_silent_add_plot.connect(self.add_signal)
        self._view_model.signal_chosen_item_data_updated.connect(self.update_all_plots)
        self._view_model.signal_update_ts_bar_placeholder.connect(self.update_ts_bar_placeholder_text)
        self._view_model.signal_data_addition.connect(self.on_data_addition)
        self._view_model.signal_update_qva.connect(self.update_qva_on_item_change)

        ##################
        # Init constants #
        ##################
        window_width = int(1200)
        window_height = int(800)
        tree_font_size = "8pt"
        di_font_size = 10
        self.slider_scaling_factor = 100
        self.cm = Colormap("fof20")

        # Get the path to the folder containing the running script (required for exe to work properly)
        if getattr(sys, 'frozen', False):
            app_path = sys._MEIPASS  # noqa
        else:
            app_path = pathlib.Path(__file__).parent.parent

        # Handy predefined paths
        icons_path = pathlib.Path(app_path) / "assets" / "icons"

        ###############
        # Init the UI #
        ###############
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Init the main layout
        main_layout = QVBoxLayout()
        central_widget.setLayout(main_layout)

        self.theme = LightTheme()
        self.setWindowTitle("QuadViewAnalyzer")
        self.setWindowIcon(QIcon(str(icons_path / "gui_logo.ico")))
        self.resize(window_width, window_height)
        self.setStyleSheet(f"background-color: {self.theme.background};")
        self.acceptDrops()

        #########################################
        # Define the widgets and their settings #
        #########################################
        # Init subplots
        glw: pg.GraphicsLayout | pg.GraphicsLayoutWidget = pg.GraphicsLayoutWidget()

        ###################
        #    TOP LEFT     #
        #   Video Frames  #
        ###################
        video_ax = glw.addPlot(row=0, col=0, title="Camera POV")
        video_ax.hideAxis("bottom")
        video_ax.hideAxis("left")

        ###################
        #    TOP RIGHT    #
        #  Analysis Graph #
        ###################
        self.graph_ax = glw.addPlot(row=0, col=1, title="Graph analysis")
        self.graph_plots = {}
        self.vline = pg.InfiniteLine(angle=90, movable=False, pen=pg.mkPen("r", width=1))
        self.graph_ax.addItem(self.vline)
        legend = self.graph_ax.addLegend(offset=(-10, 10), labelTextColor=self.theme.legend_text)
        legend.setScale(0.8)

        ###################
        #   BOTTOM LEFT   #
        #   Data Insight  #
        ###################
        di_ax = glw.addPlot(row=1, col=0, title="Data insight")

        # Remove axis
        di_ax.hideAxis("bottom")
        di_ax.hideAxis("left")

        # Set a fixed view range
        di_ax.setXRange(0, 1)
        di_ax.setYRange(0, 1)

        # Disable mouse and scroll
        di_ax.setMouseEnabled(x=False, y=False)

        # Removes/Disables all right click options except for the Export
        menu = di_ax.getViewBox().menu
        for action in menu.actions():
            menu.removeAction(action)
        di_ax.ctrlMenu = None          # Remove Plot options menu
        di_ax.hideButtons()            # Remove auto-scale [A] button

        # Create the di-text item and make the font monospace for better alignment
        self.di_text_item = pg.TextItem("", anchor=(0, 0), color="w")
        self.di_text_item.setFont(QFont("Courier", di_font_size))

        # Add the text item to the axis
        di_ax.addItem(self.di_text_item)
        self.di_text_item.setPos(0, 1)

        ###################
        #  BOTTOM RIGHT   #
        #  Birdseye View  #
        ###################
        birds_ax = glw.addPlot(row=1, col=1)
        birds_ax.addItem(pg.ScatterPlotItem())

        ###################
        # SLIDER SETTINGS #
        ###################
        self.slider = pg.QtWidgets.QSlider(Qt.Orientation.Horizontal)
        self.slider.setRange(0, 1)
        self.slider.setValue(0)
        self.slider.valueChanged.connect(self.on_slider_change)

        ######################
        # TREE MENU SETTINGS #
        ######################
        self.tree_view = c_widgets.CustomTreeView()
        self.tree_view.setMinimumWidth(200)
        self.tree_view.setHeaderHidden(False)

        # Turn off so we can manually control double-clicking and highlighting
        self.tree_view.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.tree_view.setSelectionMode(QAbstractItemView.SelectionMode.NoSelection)

        ###################
        #  Other widgets  #
        ###################
        button_new_mat_data = c_widgets.ImportFileButton(file_ext_filter="MATLAB MAT-file (*.mat)",
                                                         icon=QIcon(str(icons_path / "add_sign.svg")),
                                                         caption="Choose MAT-file")
        button_new_mat_data.setToolTip("Load in new mat-file")

        button_clear_plots = c_widgets.StandardToolButton(icon=QIcon(str(icons_path / "trash_can.svg")))
        button_clear_plots.setToolTip("Clear all plots")

        button_normalize_plots = c_widgets.StandardToolButton(icon=QIcon(str(icons_path / "normalize.svg")))
        button_normalize_plots.setToolTip("NOT IN USE ATM: Normalize the plots")

        button_add_predefined_signals = c_widgets.ImportFileButton(file_ext_filter="Configuration (*.conf)",
                                                                   icon=QIcon(str(icons_path / "add_chart.svg")),
                                                                   caption="Choose configuration file")
        button_add_predefined_signals.setToolTip("Add predefined signals")

        self.global_ts_ref_bar = c_widgets.FloatInputWidget(icon=QIcon(str(icons_path / "restart.svg")),
                                                            placeholder_text="Reference timestamp")
        self.global_ts_ref_bar.button.setToolTip("Reset ts back to original")

        search_bar = QLineEdit()
        search_bar.setPlaceholderText("Search...")
        search_bar.textChanged.connect(self.on_search_text_changed)
        search_bar.addAction(QIcon(str(icons_path / "search.svg")), QLineEdit.ActionPosition.TrailingPosition)

        self.textbox_selected_signals = QTextEdit()
        self.textbox_selected_signals.setReadOnly(True)

        ##############################
        # Connect with the ViewModel #
        ##############################
        self.tree_view.doubleClicked.connect(self.on_tree_item_double_clicked)
        self.tree_view.rightDoubleClicked.connect(self.on_tree_item_right_double_clicked)

        button_new_mat_data.file_selected.connect(self.set_and_load_new_mat)
        button_clear_plots.clicked.connect(self.reset_ui_workspace)
        #button_normalize_plots.clicked.connect()
        button_add_predefined_signals.file_selected.connect(self.parse_and_load_conf)

        self.global_ts_ref_bar.value_submitted.connect(self.on_global_ts_ref_submit)
        self.global_ts_ref_bar.button_clicked.connect(self.reset_global_ts_ref)

        #####################
        # Style the widgets #
        #####################
        button_new_mat_data.set_size(40,40)
        button_clear_plots.set_size(40, 40)
        button_normalize_plots.set_size(40, 40)
        button_add_predefined_signals.set_size(40, 40)

        self.global_ts_ref_bar.setStyleSheet('''
            FloatInputWidget QLineEdit {
              font-size: ''' + tree_font_size + ''';
              background-color: ''' + self.theme.background + ''';
              color: ''' + self.theme.text + ''';
            }
            QLineEdit:hover {
              background-color: #e8e8e8;
            }
            QLineEdit:focus {
              background-color: #ffffff;
            }
        ''')

        search_bar.setStyleSheet('''
            QLineEdit {
              font-size: ''' + tree_font_size + ''';
              background-color: ''' + self.theme.background + ''';
              color: ''' + self.theme.text + ''';
            }
        ''')

        self.tree_view.setStyleSheet('''
            QTreeView {
              font-size: ''' + tree_font_size + ''';
              background-color: ''' + self.theme.background + ''';
              color: ''' + self.theme.text + ''';
            }
        ''')

        self.textbox_selected_signals.setStyleSheet('''
            QTextEdit {
              font-size: ''' + tree_font_size + ''';
              background-color: ''' + self.theme.background + ''';
              color: ''' + self.theme.text + ''';
            }
        ''')

        #######################################
        # Create the layouts - Order matters! #
        #######################################
        plot_buttons_layout = QHBoxLayout()
        plot_buttons_layout.addWidget(button_new_mat_data)
        plot_buttons_layout.addWidget(button_clear_plots)
        plot_buttons_layout.addWidget(button_normalize_plots)
        plot_buttons_layout.addWidget(button_add_predefined_signals)
        plot_buttons = QWidget()
        plot_buttons.setLayout(plot_buttons_layout)

        tree_splitter = QSplitter(Qt.Orientation.Vertical)
        tree_splitter.addWidget(plot_buttons)
        tree_splitter.addWidget(self.global_ts_ref_bar)
        tree_splitter.addWidget(search_bar)
        tree_splitter.addWidget(self.tree_view)
        tree_splitter.addWidget(self.textbox_selected_signals)

        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.addWidget(glw)
        splitter.addWidget(tree_splitter)

        ##############################
        # Change alignment & spacing #
        ##############################
        tree_splitter.setStretchFactor(0, 1)  # Buttons
        tree_splitter.setStretchFactor(1, 1)  # Timestamp bar
        tree_splitter.setStretchFactor(2, 1)  # Search bar
        tree_splitter.setStretchFactor(3, 6)  # Tree menu
        tree_splitter.setStretchFactor(4, 3)  # Selected signal display

        splitter.setStretchFactor(0, 2)       # 2x2 plots
        splitter.setStretchFactor(1, 1)       # The complete tree menu with display

        ######################
        # Create main layout #
        ######################
        main_layout.addWidget(splitter)
        main_layout.addWidget(self.slider)

    def update_ts_bar_placeholder_text(self):
        self.global_ts_ref_bar.set_placeholder_text(self._view_model.get_current_ts_placeholder_text())
        self.set_slider_range()

    def reset_global_ts_ref(self):
        """ Resets the timestamp to the most optimal value derived from the loaded data. """
        ts_reset = self._view_model.reset_global_ts_ref()
        if ts_reset:
            self.update_ts_bar_placeholder_text()

    def on_global_ts_ref_submit(self, value: float):
        """ Updates the graph based on the new inputted ts (offset) and updates the placeholder text to reflect it. """
        valid_ts = self._view_model.update_global_ts_ref(value)
        if valid_ts:
            self.update_ts_bar_placeholder_text()

    def on_search_text_changed(self, search_query):
        """ Updates the filter of the proxy model based on the search text. """
        self._view_model.set_filter_text(search_query)

    def update_all_plots(self) -> None:
        """ Re-plots all plots that are in memory. Used when ref ts is changed. """
        skip_keys = ("ts", "ts_raw")
        for parent, entries in self._view_model.selected_signals_data.items():
            # Read one instance and check if it is a nested dict (if nested == custom item)
            custom_dict = isinstance(next(iter(entries.values()), None), dict)
            if custom_dict:
                for child, custom_entries in entries.items():
                    ts = custom_entries["ts"]
                    for key, val in custom_entries.items():
                        if key in skip_keys:
                            continue
                        signal_name = f"{parent}/{child}"
                        self.update_graph(ts, val, signal_name)
            elif "ts" in entries:
                ts = entries["ts"]

                for child, item in entries.items():
                    if child in skip_keys:
                        continue
                    signal_name = f"{parent}/{child}"
                    self.update_graph(ts, item, signal_name)

        self.update_qva_on_item_change()

    def update_graph(self, x: list, y: list, signal_name: str) -> None:
        """
        Updates the graph by updating an existing plot or adding a new plot to the graph view.
        See get_signal_data() in view to see how the signal_name is named -> "parent/child".

        :param x: List of x-axis data points.
        :param y: List of y-axis data points.
        :param signal_name: Name of the signal to plot. Here it follows the "parent/child" naming convention.
        """
        if signal_name in self.graph_plots:
            if isinstance(self.graph_plots[signal_name], tuple):
                vline, _ = self.graph_plots[signal_name]
                vline.setPos((x[0], y[0]))
            else:
                self.graph_plots[signal_name].setData(x, y)
        else:
            pen = pg.mkPen(self.cm.get_color(item_id=signal_name), width=2)

            if len(x) == 1:
                # Create a dummy plot so it is shows up as a legend
                vline = pg.InfiniteLine(pos=(x[0], y[0]), angle=90, movable=False, pen=pen, name=signal_name)
                dummy_plot = self.graph_ax.plot([], [], pen=pen, name=signal_name)

                self.graph_ax.addItem(vline)
                self.graph_plots[signal_name] = (vline, dummy_plot)
            else:
                self.graph_plots[signal_name] = self.graph_ax.plot(x, y, pen=pen, name=signal_name)

    def on_slider_change(self, slider_value: int):
        time = slider_value / self.slider_scaling_factor

        # Update the vertical line
        self.vline.setPos(time)

        # Update data insight text
        self.set_time_based_data_insight(time)

    def set_slider_range(self):
        """
        Adjusts the slider's range and resets its value according to the x-values of all plotted data, assuming that
        the x-values are increasing and in ascending order.
        """
        if self.graph_plots == {}:
            self.hard_reset_slider()
            return

        # Compute min
        x_vals = [item.getData()[0][0] for item in self.graph_plots.values() if not isinstance(item, tuple)]
        if not x_vals:
            return     # if only vertical lines
        current_min = int(min(x_vals))

        # Compute max
        x_vals = [item.getData()[0][-1] for item in self.graph_plots.values() if not isinstance(item, tuple)]
        current_max = int(np.ceil(max(x_vals)))

        # Scale
        slider_max = (current_max - current_min) * self.slider_scaling_factor

        # Update the slider's range
        self.slider.setMinimum(0)
        self.slider.setMaximum(slider_max)

        # Reset the slider value and vertical line
        self.soft_reset_slider()

    def set_time_based_data_insight(self, ref_time: float):
        """ Sets data insight text and values based on the reference time provided. """
        di_text = self._view_model.get_time_based_data_insight(self.graph_plots, ref_time)
        self.di_text_item.setPlainText(di_text)

    def set_default_selected_signals_data_insight(self):
        di_text = self._view_model.get_default_data_insight()
        self.di_text_item.setPlainText(di_text)

    def update_selected_signals_display(self):
        """ Updates the text area to show which signals have been selected. """
        selected = self._view_model.selected_signals_data
        display_lines = [
            f"• {parent}: {', '.join(key for key in signals if key != 'ts' and key !='ts_raw')}"
            for parent, signals in selected.items()
        ]
        self.textbox_selected_signals.setPlainText("\n".join(display_lines))

    def index_to_item(self, index: QModelIndex) -> QStandardItem:
        proxy_model: QSortFilterProxyModel | QAbstractItemModel = self.tree_view.model()
        source_index = proxy_model.mapToSource(index)
        tree_model: QStandardItemModel | QAbstractItemModel = proxy_model.sourceModel()
        return tree_model.itemFromIndex(source_index)

    def on_tree_item_right_double_clicked(self, index: QModelIndex):
        """ Handles tree menu right-clicking features. """
        item = self.index_to_item(index)

        # Ignore parent nodes
        if item.hasChildren():
            return None

        item_path = self._view_model.tree_item_to_path(item)

        # Ignore already selected items that are in primary memory
        if self._view_model.is_signal_already_selected(item_path):
            return None

        if self._view_model.is_di_already_selected(item_path):
            item_deleted, signal_name = self._view_model.deselect_item(item_path, backend_memory=self._view_model.selected_di_only_data)

            if item_deleted:
                time = self.slider.value() / self.slider_scaling_factor
                self.set_time_based_data_insight(time)

                # Remove highlight of item in the tree menu
                item.setBackground(QColor(self.theme.background))
                item.setForeground(QColor(self.theme.text))
        else:
            item_added = self._view_model.select_item(item_path, backend_memory=self._view_model.selected_di_only_data)

            if item_added:
                time = self.slider.value() / self.slider_scaling_factor
                self.set_time_based_data_insight(time)

                # Highlight item in the tree menu
                item.setBackground(QColor(self.theme.accent))
                item.setForeground(QColor(self.theme.accent_text))

    def on_tree_item_double_clicked(self, index: QModelIndex):
        """ Handles tree menu clicking features (except for right-clicking). """
        item = self.index_to_item(index)

        # Ignore parent nodes
        if item.hasChildren():
            return None

        # Build dict path to be sent to ViewModel
        item_path = self._view_model.tree_item_to_path(item)
        if self._view_model.is_signal_already_selected(item_path):
            item_deleted, signal_name = self._view_model.deselect_item(item_path)

            if item_deleted:
                # Remove highlight of item in the tree menu
                item.setBackground(QColor(self.theme.background))
                item.setForeground(QColor(self.theme.text))

                # Remove the deselected signal plot/vertical line
                if isinstance(self.graph_plots[signal_name], tuple):
                    vline, dummy_plot = self.graph_plots[signal_name]
                    self.graph_ax.removeItem(vline)
                    self.graph_ax.removeItem(dummy_plot)
                else:
                    self.graph_ax.removeItem(self.graph_plots[signal_name])
                del self.graph_plots[signal_name]

                # Update colormap, display, and slider
                self.cm.release_color(signal_name)
                self.update_qva_on_item_change()
        else:
            item_added = self._view_model.select_item(item_path)

            if item_added:
                self.add_signal(item, item_path, update_qva=True)

    def parse_and_load_conf(self, path: pathlib.Path):
        self._view_model.parse_and_load_conf(path)

    def update_qva_on_item_change(self):
        """ Function to update and refresh the QVA application. """
        self.graph_ax.autoBtnClicked()
        self.update_selected_signals_display()
        self.set_default_selected_signals_data_insight()
        self.set_slider_range()

    def add_signal(self, item: QStandardItem, item_path: list, update_qva: bool):
        """
        Adds an item to the graph view, and updates the display and data insight if enabled.
        :param item: Item to be added
        :param item_path: List of strings representing the path in either the tree or "parent/child" in memory.
        :param update_qva: Updates the QVA, e.g., display and data insight
        :return:
        """
        if self._view_model.is_di_already_selected(item_path):
            self._view_model.deselect_item(item_path, backend_memory=self._view_model.selected_di_only_data)

        # Highlight item in the tree menu
        item.setBackground(QColor(self.theme.highlight))
        item.setForeground(QColor(self.theme.highlight_text))

        # Add plot
        ts, val, signal_name = self._view_model.get_signal_data(item_path)
        self.update_graph(ts, val, signal_name)

        if update_qva:
            self.update_qva_on_item_change()

    def set_and_load_new_mat(self, path: pathlib.Path):
        self._view_model.set_and_load_mat(path)

    def on_data_addition(self, parent_key: str, child_keys: list):
        """
        Visually updates the tree menu by adding a parent item and attaching the specified child items under it.
        However, it does **not** modify the backend memory — only the visual representation in the UI.

        :param parent_key: The name of the parent item to be added (or updated) in the tree menu.
        :param child_keys: A list of child items to be added under the specified parent.
        """
        model = self.tree_view.model()
        if not model:
            return

        # If using a proxy model, get the source model
        if hasattr(model, "sourceModel"):
            model = model.sourceModel()

        # Find the parent tree item (traverse backwards as it is most likely new additions are at the end)
        parent_item = None
        for row in range(model.rowCount()-1, -1, -1):
            item = model.item(row)

            if item.text() == parent_key:
                parent_item = item
                break

        # Create if parent key does not exist
        if parent_item is None:
            parent_item = QStandardItem(parent_key)
            model.appendRow(parent_item)

        # Create a set of existing child texts for faster lookup
        existing_children = set()
        for row in range(parent_item.rowCount()):
            existing_item = parent_item.child(row)
            existing_children.add(existing_item.text())

        # Add the new data
        for child in child_keys:
            if child not in existing_children:
                child_item = QStandardItem(child)
                parent_item.appendRow(child_item)

    def on_data_file_load(self):
        """ Called when a new file is loaded. Clears and refreshes the main window. """
        self.reset_ui_workspace()

        tree_model = self._view_model.update_tree_model()
        self.tree_view.setModel(tree_model)

    def reset_ui_workspace(self):
        """ Function that clears all user UI related actions while keeping imported data intact. """
        if self._view_model.is_mat_loaded():
            self.clear_graph_view_plots()
            self.clear_tree_highlighting()
            self.textbox_selected_signals.setPlainText("")
            self.di_text_item.setPlainText("")
            self._view_model.deselect_all_signals()
            self.cm.reset()
            self.global_ts_ref_bar.set_placeholder_text(self._view_model.get_current_ts_placeholder_text())

    def clear_graph_view_plots(self):
        self.graph_ax.clear()
        self.graph_plots = {}
        self.graph_ax.addItem(self.vline)
        self.hard_reset_slider()

    def hard_reset_slider(self):
        self.slider.setRange(0, 1)
        self.slider.setValue(0)
        self.vline.setPos(0)
        self.vline.setValue(0)

    def soft_reset_slider(self):
        self.slider.setValue(0)
        self.vline.setPos(0)
        self.vline.setValue(0)

    def clear_tree_highlighting(self):
        """ Clears all highlighting from the tree view items. """
        model = self.tree_view.model()
        if not model:
            return

        # If using a proxy model, get the source model
        if hasattr(model, "sourceModel"):
            model = model.sourceModel()

        # Start with the invisible root item
        root = model.invisibleRootItem()
        stack = [root]

        # Reset the item's background and foreground to the default theme
        while stack:
            item = stack.pop()
            item.setBackground(QColor(self.theme.background))
            item.setForeground(QColor(self.theme.text))

            # Push all children of this item onto the stack
            for row in range(item.rowCount()):
                child = item.child(row)
                if child is not None:
                    stack.append(child)

    def dragEnterEvent(self, event: QDragEnterEvent, /):
        """ This event triggers when a file is being dragged into the main window """
        if event.mimeData().hasUrls():
            accept_drop = True

            for url in event.mimeData().urls():
                filepath = pathlib.Path(url.toLocalFile())

                if filepath.suffix.lower() not in self._view_model.accepted_file_types:
                    accept_drop = False
                    break

            if accept_drop:
                event.accept()
            else:
                event.ignore()
        else:
            event.ignore()

    def dropEvent(self, event):
        """ This event triggers when a file is dropped into the main window. Get filepath(s) and send to ViewModel. """
        if event.mimeData().hasUrls():
            accepted_files = []

            for url in event.mimeData().urls():
                filepath = pathlib.Path(url.toLocalFile())
                if filepath.suffix.lower() in self._view_model.accepted_file_types:
                    accepted_files.append(filepath)

            if accepted_files:
                event.accept()  # Confirm that the drop was handled
                self._view_model.handle_dropped_files(accepted_files)
            else:
                event.ignore()
        else:
            event.ignore()

if __name__ == '__main__':
    pass
