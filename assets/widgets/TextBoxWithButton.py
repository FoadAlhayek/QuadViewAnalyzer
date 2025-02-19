"""
@Author: Foad Alhayek
@Description: A custom button widget that includes a display showcasing the name of the file that has been chosen.
"""
import sys
import pathlib
from PySide6.QtWidgets import QApplication, QWidget, QHBoxLayout, QLabel, QPushButton, QSizePolicy, QFileDialog
from PySide6.QtGui import QIcon
from PySide6.QtCore import QSize


class TextBoxWithButton(QWidget):
    def __init__(self, file_ext_filter: str):
        """ Custom widget consisting of a text box (label) and an interactive button [LABEL][B] """
        super().__init__()

        # Init class settings
        self.file_ext_filter = file_ext_filter
        self.filepath = pathlib.Path("")
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)

        # Required or else the exe does not display the icon
        if getattr(sys, 'frozen', False):
            app_path = sys._MEIPASS  # noqa
        else:
            app_path = r"C:\Users\foadal\Documents\GitHub\QuadViewAnalyzer"

        # Init widgets
        self.label = QLabel("")
        self.button = QPushButton()

        # Connect button to file explorer
        self.button.clicked.connect(self.open_file_dialog)

        # Style
        self.label.setStyleSheet('''
            QLabel {
              border-width: 1px;
              border-style: solid;
              border-top-left-radius: 6px;
              border-bottom-left-radius: 6px;
            }
        ''')

        self.button.setIcon(QIcon(str(pathlib.Path(app_path) / "assets" / "icons" / "three_dots.svg")))
        self.button.setStyleSheet('''
            QPushButton {
              padding: 0px;
              border-width: 1px 1px 1px 0px;
              border-style: solid;
              border-color: black;
              border-top-right-radius: 6px;
              border-bottom-right-radius: 6px;
              background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #f6f7fa, stop: 1 #d3d3d3);
            }
            QPushButton:pressed {
              background: #e1e1e1;
            }
        ''')

        # Layout
        self.dialog_box_layout = QHBoxLayout()
        self.dialog_box_layout.addWidget(self.label)
        self.dialog_box_layout.addWidget(self.button)

        self.dialog_box_layout.setSpacing(0)
        self.dialog_box_layout.setContentsMargins(0, 0, 0, 0)

        # Display widget
        self.setLayout(self.dialog_box_layout)

    def set_size(self, width, height):
        """ Updates the size of the widget by making sure the combined widgets are aligned and animation works """
        self.label.setFixedSize(width - height, height)
        self.button.setFixedSize(height, height)
        self.button.setIconSize(QSize(height//2, height//2))

        # Animates the button on press
        self.button.setStyleSheet(self.button.styleSheet() + "QPushButton:pressed {padding:" + str(height//2) + "px;}")

        # Update the changes
        self.adjustSize()

    def open_file_dialog(self):
        """ Function to open file explorer when button is clicked """
        filepath, _ = QFileDialog.getOpenFileName(self, caption="Open File", dir="", filter=self.file_ext_filter)

        # If Cancel or X is clicked, don't do anything
        if filepath != "":
            self.filepath = pathlib.Path(filepath)
            filename = self.filepath.name
            self.label.setText(filename)


if __name__ == "__main__":
    app = QApplication([])
    widget = TextBoxWithButton("*.py")
    widget.label.setText("Wow")
    widget.set_size(200, 50)
    widget.show()
    app.exec()
