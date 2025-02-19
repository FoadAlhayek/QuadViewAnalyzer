"""
The View logic for the application following the MVVM pattern.

The View is allowed to import ViewModel but not the Model!
The View connects signals from the ViewModel and a function with equal amounts of emit

Usage: main.py, QuadViewModel.py
"""
from PySide6.QtWidgets import QWidget, QToolButton, QLabel, QHBoxLayout, QVBoxLayout, QComboBox, QGridLayout
from PySide6.QtGui import QIcon, QFontDatabase, QPixmap
from PySide6.QtCore import Qt
import pathlib
import sys

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
        WINDOW_WIDTH = int(900)
        WINDOW_HEIGHT = int(600)
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
        self.theme = LightTheme()
        self.setWindowTitle("QuadViewAnalyzer")
        self.setWindowIcon(QIcon(str(pathlib.Path(app_path) / "assets" / "icons" / "gui_logo.ico")))
        self.resize(WINDOW_WIDTH, WINDOW_HEIGHT)
        self.setStyleSheet(f"background-color: {self.theme.background};")

        #########################################
        # Define the widgets and their settings #
        #########################################
        self.button_start_QVA = QToolButton()

        self.label_mat = QLabel("Select mat")

        self.text_box_button_mat = c_widgets.TextBoxWithButton(file_ext_filter="MATLAB file (*.mat)")

        ###########################################
        # Connect interactions with the ViewModel #
        ###########################################
        self.button_start_QVA.clicked.connect(self._view_model.start_qva)
        self.text_box_button_mat.button.clicked.connect(self.update_mat_path)

        #####################
        # Style the widgets #
        #####################
        self.button_start_QVA.setIcon(QIcon(str(pathlib.Path(app_path) / "assets" / "icons" / "power_button.svg")))
        self.button_start_QVA.setFixedSize(125, 125)
        self.button_start_QVA.setIconSize(self.button_start_QVA.size())
        self.button_start_QVA.setStyleSheet('''
            QToolButton {
              border-radius: ''' + str(self.button_start_QVA.height() // 2) + ''';
              border-width: 2px;
              border-style: solid;
              border-color: black;
              background-color: ''' + self.theme.button + ''';
              text-align: center;
            }
            QToolButton:hover {
              background-color: ''' + self.theme.highlight + ''';
            }
        ''')

        self.text_box_button_mat.set_size(WINDOW_WIDTH // 3 - int(2 * MARGIN_PX), 50)
        self.text_box_button_mat.setStyleSheet('''
            QLabel {
              background-color: ''' + self.theme.inactive_button + ''';
              color: ''' + self.theme.button_text + ''';
            }
        ''')

        self.label_mat.setFixedWidth(self.text_box_button_mat.width())
        self.label_mat.setStyleSheet(f"font-size: {LABEL_FONT_SIZE}; color: {self.theme.label_text}")

        #######################################
        # Create the layouts - Order matters! #
        #######################################
        self.header_layout = QVBoxLayout()
        self.header_layout.addStretch()
        self.header_layout.addWidget(self.button_start_QVA)
        self.header_layout.addStretch()

        self.config_label_layout = QHBoxLayout()
        self.config_label_layout.addWidget(self.label_mat)

        self.config_box_layout = QHBoxLayout()
        self.config_box_layout.addWidget(self.text_box_button_mat)

        ##############################
        # Change alignment & spacing #
        ##############################
        self.header_layout.setAlignment(self.button_start_QVA, Qt.AlignmentFlag.AlignHCenter)

        self.config_label_layout.setSpacing(MARGIN_PX)
        self.config_box_layout.setSpacing(MARGIN_PX)

        ###################
        # Combine layouts #
        ###################
        self.config_layout = QVBoxLayout()
        self.config_layout.addLayout(self.config_label_layout)
        self.config_layout.addLayout(self.config_box_layout)
        self.config_layout.setContentsMargins(MARGIN_PX, 0, MARGIN_PX, MARGIN_PX)

        ######################
        # Create main layout #
        ######################
        self.main_layout = QVBoxLayout()
        self.main_layout.addLayout(self.header_layout)
        self.main_layout.addLayout(self.config_layout)
        self.main_layout.setContentsMargins(0, 0, 0, 0)

        # Set the main layout
        self.setLayout(self.main_layout)

    def update_mat_path(self):
        """ Updates the path to the current selected file in the backend """
        self._view_model.set_mat(self.text_box_button_mat.filepath)

if __name__ == '__main__':
    pass
