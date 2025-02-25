"""
The View logic for the application following the MVVM pattern.

The View is allowed to import ViewModel but not the Model!
The View connects signals from the ViewModel and a function with equal amounts of emit

Usage: main.py, QuadViewModel.py
"""
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTreeView, QSplitter, QAbstractItemView, QMainWindow,
                               QTextEdit, QLineEdit, QToolButton)
from PySide6.QtGui import QIcon, QDragEnterEvent, QColor, QStandardItemModel
from PySide6.QtCore import Qt, QSortFilterProxyModel, QAbstractItemModel
import pyqtgraph as pg
import pathlib
import sys
import numpy as np

# Internal imports
import assets.widgets as c_widgets
from assets.palettes.Palette import LightTheme, DarkTheme  # noqa

class QuadView(QMainWindow):
    def __init__(self, view_model):
        super().__init__()

        # Init the ViewModel and connect the signals with a method
        self._view_model = view_model
        self._view_model.signal_new_data_loaded.connect(self.on_data_file_load)

        ##################
        # Init constants #
        ##################
        window_width = int(1200)
        window_height = int(800)
        tree_font_size = "8pt"

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
        legend = self.graph_ax.addLegend(offset=(-10, 10), labelTextColor=self.theme.legend_text)
        legend.setScale(0.8)

        ###################
        #   BOTTOM LEFT   #
        #   Data Insight  #
        ###################
        di_ax = glw.addPlot(row=1, col=0, title="Data insight")
        di_ax.hideAxis("bottom")
        di_ax.hideAxis("left")

        ###################
        #  BOTTOM RIGHT   #
        #  Birdseye View  #
        ###################
        birds_ax = glw.addPlot(row=1, col=1)
        birds_ax.addItem(pg.ScatterPlotItem())

        ###################
        # SLIDER SETTINGS #
        ###################
        slider = pg.QtWidgets.QSlider(Qt.Orientation.Horizontal)
        slider.setRange(0, 1000)
        slider.setValue(0)

        ######################
        # TREE MENU SETTINGS #
        ######################
        self.tree_view = QTreeView()
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
        button_normalize_plots.setToolTip("Normalize the plots")

        button_add_custom_signal = c_widgets.StandardToolButton(icon=QIcon(str(icons_path / "add_chart.svg")))
        button_add_custom_signal.setToolTip("Add custom xy-signal")

        search_bar = QLineEdit()
        search_bar.setPlaceholderText("Search...")
        search_bar.textChanged.connect(self.on_search_text_changed)

        self.textbox_selected_signals = QTextEdit()
        self.textbox_selected_signals.setReadOnly(True)

        ##############################
        # Connect with the ViewModel #
        ##############################
        self.tree_view.doubleClicked.connect(self.on_tree_item_double_clicked)
        button_new_mat_data.file_selected.connect(self.set_and_load_new_mat)
        button_clear_plots.clicked.connect(self.reset_ui_workspace)
        #button_normalize_plots.clicked.connect()
        #button_add_custom_signal.clicked.connect()

        #####################
        # Style the widgets #
        #####################
        button_new_mat_data.set_size(40,40)
        button_clear_plots.set_size(40, 40)
        button_normalize_plots.set_size(40, 40)
        button_add_custom_signal.set_size(40, 40)

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
        plot_buttons_layout.addWidget(button_add_custom_signal)
        plot_buttons = QWidget()
        plot_buttons.setLayout(plot_buttons_layout)

        tree_splitter = QSplitter(Qt.Orientation.Vertical)
        tree_splitter.addWidget(plot_buttons)
        tree_splitter.addWidget(search_bar)
        tree_splitter.addWidget(self.tree_view)
        tree_splitter.addWidget(self.textbox_selected_signals)

        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.addWidget(glw)
        splitter.addWidget(tree_splitter)

        ##############################
        # Change alignment & spacing #
        ##############################
        tree_splitter.setStretchFactor(0, 1)  # Search bar
        tree_splitter.setStretchFactor(1, 6)  # Tree menu
        tree_splitter.setStretchFactor(2, 2)  # Selected signal display

        splitter.setStretchFactor(0, 2)       # 2x2 plots
        splitter.setStretchFactor(1, 1)       # The complete tree menu with display

        ######################
        # Create main layout #
        ######################
        main_layout.addWidget(splitter)
        main_layout.addWidget(slider)

    def on_search_text_changed(self, search_query):
        """ Updates the filter of the proxy model based on the search text. """
        self._view_model.set_filter_text(search_query)

    def update_graph(self, x: list, y: list, signal_name: str):
        if signal_name in self.graph_plots:
            self.graph_plots[signal_name].setData(x, y)
        else:
            rgb_colors =  np.random.randint(0, 256, 3)
            if not np.any(rgb_colors >= 220):
                rgb_colors[np.random.randint(0, 3)] = np.random.randint(220, 256)
            r, g, b = rgb_colors.tolist() # To resolve linting issue
            pen = pg.mkPen(QColor(r, g, b), width=2)

            self.graph_plots[signal_name] = self.graph_ax.plot(x, y, pen=pen, name=signal_name)

    def update_selected_signals_display(self):
        """ Updates the text area to show which signals have been selected. """
        selected = self._view_model.selected_signals_data
        display_lines = [
            f"• {parent}: {', '.join(key for key in signals if key != 'ts')}" for parent, signals in selected.items()
        ]
        self.textbox_selected_signals.setPlainText("\n".join(display_lines))

    def on_tree_item_double_clicked(self, index):
        """ Handles tree menu clicking features """
        proxy_model: QSortFilterProxyModel|QAbstractItemModel = self.tree_view.model()
        source_index = proxy_model.mapToSource(index)
        tree_model: QStandardItemModel|QAbstractItemModel = proxy_model.sourceModel()
        item = tree_model.itemFromIndex(source_index)

        # Ignore parent nodes
        if item.hasChildren():
            return

        # Build dict path to be sent to ViewModel
        item_path = []
        temp_item = item
        while temp_item is not None:
            item_path.insert(0, temp_item.text())
            temp_item = temp_item.parent()

        if self._view_model.is_signal_already_selected(item_path):
            signal_deleted, signal_name = self._view_model.deselect_item(item_path)

            if signal_deleted:
                # Remove highlight of item in the tree menu
                item.setBackground(QColor(self.theme.background))
                item.setForeground(QColor(self.theme.text))

                # Remove the deselected signal plot
                self.graph_ax.removeItem(self.graph_plots[signal_name])
                del self.graph_plots[signal_name]
        else:
            signal_added = self._view_model.select_item(item_path)

            if signal_added:
                # Highlight item in the tree menu
                item.setBackground(QColor(self.theme.highlight))
                item.setForeground(QColor(self.theme.highlight_text))

                # Add plot
                ts, val, signal_name = self._view_model.get_signal_data(item_path)
                self.update_graph(ts, val, signal_name)

        self.update_selected_signals_display()

    def set_and_load_new_mat(self, path: pathlib.Path):
        self._view_model.set_and_load_mat(path)

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
            self._view_model.deselect_all_signals()

    def clear_graph_view_plots(self):
        self.graph_ax.clear()
        self.graph_plots = {}

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
