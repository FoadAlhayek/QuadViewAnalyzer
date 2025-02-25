"""
@Author: Foad Alhayek
@Description: An alternative custom QToolButton that lets the user pick a file and emits the path.
"""
import pathlib
from PySide6.QtWidgets import QToolButton, QFileDialog
from PySide6.QtGui import QIcon
from PySide6.QtCore import QSize, Signal


class ImportFileButton(QToolButton):
    """
    A custom tool button that opens a file dialog when clicked.

    Attributes:
        file_selected (Signal): Emitted when a file is selected.
    """
    file_selected = Signal(pathlib.Path)

    def __init__(
            self,
            file_ext_filter: str,
            icon: QIcon,
            caption: str = "Open File",
            initial_dir: str = "",
            parent=None):
        """
        :param file_ext_filter: File extension filter for the file dialog.
        :param icon: Icon displayed on the button.
        :param caption: Caption displayed on the file dialog.
        :param initial_dir: Initial directory of the file dialog.
        :param parent: Parent widget of the button.
        """
        super().__init__(parent)

        # Init class settings
        self.file_ext_filter = file_ext_filter
        self.caption = caption
        self.initial_dir = initial_dir

        # Connect button to file explorer
        self.clicked.connect(self.open_file_dialog)

        # Style
        self.setIcon(icon)
        self.setStyleSheet('''
            QToolButton {
              padding: 0px;
              border-width: 1px;
              border-style: solid;
              border-color: black;
              border-radius: 6px;
              background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #f6f7fa, stop: 1 #d3d3d3);
            }
            QToolButton:pressed {
              background: #e1e1e1;
            }
        ''')

    def set_size(self, width, height):
        """ Updates the size of the widget by making sure the widget and icon are proportional and animation works """
        self.setFixedSize(width, height)
        self.setIconSize(QSize(height//2, height//2))

        stylesheet = '''
        QToolButton {
          padding: 0px;
          border-width: 1px;
          border-style: solid;
          border-color: black;
          border-radius: 6px;
          background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #f6f7fa, stop: 1 #d3d3d3);
        }
        QToolButton:pressed {
          background: #e1e1e1;
          padding:''' + str(height//4) + '''px;
        }
        '''

        self.setStyleSheet(stylesheet)

        # Update the changes
        self.adjustSize()

    def open_file_dialog(self):
        """ Opens the file dialog when the button is clicked and emits with the selected file path. """
        try:
            filepath, _ = QFileDialog.getOpenFileName(self,
                                                      caption=self.caption,
                                                      dir=self.initial_dir,
                                                      filter=self.file_ext_filter)

            # If Cancel or X is clicked, don't do anything
            if filepath != "":
                selected_file = pathlib.Path(filepath)
                self.file_selected.emit(selected_file)
        except Exception as e:
            print(f"An error occurred: {e}")


if __name__ == "__main__":
    """ Showcasing the usage of the widget. """
    from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel
    import sys

    app = QApplication(sys.argv)

    # Create the main window
    main_window = QWidget()
    main_layout = QVBoxLayout()

    # Create an icon (using a standard icon for the example)
    file_icon = QIcon.fromTheme("document-open")

    # Instantiate the ImportFileButton
    import_button = ImportFileButton('All Files (*)', file_icon, caption="Select a File")

    # Optionally set the button size
    import_button.set_size(100, 40)

    # Connect the file_selected signal
    def handle_file_selection(file_path):
        print(f"Selected file: {file_path}")
        selected_file_label.setText(f"Selected File: {file_path}")

    import_button.file_selected.connect(handle_file_selection)

    # Add the button to the layout
    main_layout.addWidget(import_button)

    # Add a label to display the selected file path
    selected_file_label = QLabel("No file selected")
    main_layout.addWidget(selected_file_label)

    main_window.setLayout(main_layout)
    main_window.setWindowTitle("ImportFileButton Demo")
    main_window.show()

    sys.exit(app.exec())

