"""
The View logic for the application following the MVVM pattern.

The View is allowed to import ViewModel but not the Model!
The View connects signals from the ViewModel and a function with equal amounts of emit

Usage: main.py, QuadViewModel.py
"""
from os import access

from PySide6.QtWidgets import QWidget, QLabel, QHBoxLayout, QVBoxLayout, QTreeView, QSplitter, QAbstractItemView, QMainWindow
from PySide6.QtGui import QIcon, QDragEnterEvent
from PySide6.QtCore import Qt
import pyqtgraph as pg
import pathlib
import sys
from pyqtgraph import GraphicsLayoutWidget


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
        WINDOW_WIDTH = int(1200)
        WINDOW_HEIGHT = int(800)
        LABEL_FONT_SIZE = "20pt"
        MARGIN_PX = int(30)

        # Get the path to the folder containing the running script (required for exe to work properly)
        if getattr(sys, 'frozen', False):
            app_path = sys._MEIPASS  # noqa
        else:
            app_path = pathlib.Path(__file__).parent.parent

        ###############
        # Init the UI #
        ###############
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Init the main layout
        main_layout = QVBoxLayout()
        central_widget.setLayout(main_layout)

        theme = LightTheme()
        self.setWindowTitle("QuadViewAnalyzer")
        self.setWindowIcon(QIcon(str(pathlib.Path(app_path) / "assets" / "icons" / "gui_logo.ico")))
        self.resize(WINDOW_WIDTH, WINDOW_HEIGHT)
        self.setStyleSheet(f"background-color: {theme.background};")
        self.acceptDrops()

        #########################################
        # Define the widgets and their settings #
        #########################################
        # Init subplots
        self.glw = GraphicsLayoutWidget()

        ###################
        #    TOP LEFT     #
        #   Video Frames  #
        ###################
        self.video_ax = self.glw.addPlot(row=0, col=0, title="Camera POV")
        self.video_ax.hideAxis("bottom")
        self.video_ax.hideAxis("left")

        ###################
        #    TOP RIGHT    #
        #  Analysis Graph #
        ###################
        self.graph_ax = self.glw.addPlot(row=0, col=1, title="Graph analysis")

        ###################
        #   BOTTOM LEFT   #
        #   Data Insight  #
        ###################
        self.di_ax = self.glw.addPlot(row=1, col=0, title="Data insight")
        self.di_ax.hideAxis("bottom")
        self.di_ax.hideAxis("left")

        ###################
        #  BOTTOM RIGHT   #
        #  Birdseye View  #
        ###################
        self.birds_ax = self.glw.addPlot(row=1, col=1)
        self.birds_ax.addItem(pg.ScatterPlotItem())

        ###################
        # SLIDER SETTINGS #
        ###################
        self.slider = pg.QtWidgets.QSlider(Qt.Orientation.Horizontal)
        self.slider.setRange(0, 1000)
        self.slider.setValue(0)

        ######################
        # TREE MENU SETTINGS #
        ######################
        self.tree_view = QTreeView()
        self.tree_view.setMinimumWidth(200)
        self.tree_view.setHeaderHidden(False)
        self.tree_view.setEditTriggers(QAbstractItemView.NoEditTriggers)

        ###################
        #  Other widgets  #
        ###################
        self.label_mat = QLabel("Select mat")
        self.text_box_button_mat = c_widgets.TextBoxWithButton(file_ext_filter="MATLAB file (*.mat)")

        ##############################
        # Connect with the ViewModel #
        ##############################
        self.tree_view.doubleClicked.connect(self.on_tree_item_double_clicked)

        self.text_box_button_mat.button.clicked.connect(self.update_mat_path)

        #####################
        # Style the widgets #
        #####################
        self.tree_view.setStyleSheet('''
            QTreeView {
              font-size: 8pt;
            }
        ''')

        self.text_box_button_mat.set_size(WINDOW_WIDTH // 3 - int(2 * MARGIN_PX), 50)
        self.text_box_button_mat.setStyleSheet('''
            QLabel {
              background-color: ''' + theme.inactive_button + ''';
              color: ''' + theme.button_text + ''';
            }
        ''')

        self.label_mat.setFixedWidth(self.text_box_button_mat.width())
        self.label_mat.setStyleSheet(f"font-size: {LABEL_FONT_SIZE}; color: {theme.label_text}")

        #######################################
        # Create the layouts - Order matters! #
        #######################################
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.addWidget(self.glw)
        splitter.addWidget(self.tree_view)

        # test_layout = QVBoxLayout()
        # test_layout.addWidget(self.label_mat)
        # test_layout.addWidget(self.text_box_button_mat)

        ##############################
        # Change alignment & spacing #
        ##############################
        splitter.setStretchFactor(0, 2)
        splitter.setStretchFactor(1, 1)

        ###################
        # Combine layouts #
        ###################
        #content_layout = QHBoxLayout()
        #content_layout.addLayout(graph_layout)
        #content_layout.addLayout(test_layout)

        ######################
        # Create main layout #
        ######################
        main_layout.addWidget(splitter)
        main_layout.addWidget(self.slider)

    def on_tree_item_double_clicked(self, index):
        """ Handles tree menu clicking features """
        item = self.tree_view.model().itemFromIndex(index)

        # Ignore parent nodes
        if item.hasChildren():
            return

        item_path = []
        while item is not None:
            item_path.insert(0, item.text())
            item = item.parent()

        self._view_model.handle_item_selected(item_path)

    def on_data_file_load(self):
        """ Called when a new file is loaded. Clears and refreshes the main window. """
        self.clear_plots()

        tree_model = self._view_model.generate_tree_model()
        self.tree_view.setModel(tree_model)

    def clear_plots(self):
        pass

    def update_mat_path(self):
        """ Updates the path to the current selected file in the backend """
        self._view_model.set_mat(self.text_box_button_mat.filepath)

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
