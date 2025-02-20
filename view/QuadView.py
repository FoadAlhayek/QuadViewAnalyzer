"""
The View logic for the application following the MVVM pattern.

The View is allowed to import ViewModel but not the Model!
The View connects signals from the ViewModel and a function with equal amounts of emit

Usage: main.py, QuadViewModel.py
"""
from PySide6.QtWidgets import QWidget, QToolButton, QLabel, QHBoxLayout, QVBoxLayout, QComboBox, QGridLayout
from PySide6.QtGui import QIcon, QFontDatabase, QPixmap
from PySide6.QtCore import Qt
import pyqtgraph as pg
import pathlib
import sys
from pyqtgraph import GraphicsLayoutWidget


# Internal imports
import assets.widgets as c_widgets
from assets.palettes.Palette import LightTheme, DarkTheme  # noqa

class QuadView(QWidget):
    def __init__(self, view_model):
        super().__init__()

        # Init the ViewModel and connect the signals with a method
        self._view_model = view_model

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
        theme = LightTheme()
        self.setWindowTitle("QuadViewAnalyzer")
        self.setWindowIcon(QIcon(str(pathlib.Path(app_path) / "assets" / "icons" / "gui_logo.ico")))
        self.resize(WINDOW_WIDTH, WINDOW_HEIGHT)
        self.setStyleSheet(f"background-color: {theme.background};")

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

        ###################
        #  Other widgets  #
        ###################
        self.label_mat = QLabel("Select mat")
        self.text_box_button_mat = c_widgets.TextBoxWithButton(file_ext_filter="MATLAB file (*.mat)")

        ###########################################
        # Connect interactions with the ViewModel #
        ###########################################
        self.text_box_button_mat.button.clicked.connect(self.update_mat_path)

        #####################
        # Style the widgets #
        #####################
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
        graph_layout = QVBoxLayout()
        graph_layout.addWidget(self.glw)

        test_layout = QVBoxLayout()
        test_layout.addWidget(self.label_mat)
        test_layout.addWidget(self.text_box_button_mat)
        ##############################
        # Change alignment & spacing #
        ##############################
        test_layout.setSpacing(MARGIN_PX)

        ###################
        # Combine layouts #
        ###################
        content_layout = QHBoxLayout()
        content_layout.addLayout(graph_layout)
        content_layout.addLayout(test_layout)

        ######################
        # Create main layout #
        ######################
        main_layout = QVBoxLayout()
        main_layout.addLayout(content_layout)
        main_layout.addWidget(self.slider)

        # Set the main layout
        self.setLayout(main_layout)

    def update_mat_path(self):
        """ Updates the path to the current selected file in the backend """
        self._view_model.set_mat(self.text_box_button_mat.filepath)

if __name__ == '__main__':
    pass
