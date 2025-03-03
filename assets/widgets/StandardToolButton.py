"""
@Author: Foad Alhayek
@Description: A commonly styled QToolButton that handles icon resizing, wrapped into a class for consistency.
"""
from PySide6.QtWidgets import QToolButton
from PySide6.QtGui import QIcon
from PySide6.QtCore import QSize


class StandardToolButton(QToolButton):
    """ A commonly styled QToolButton that handles icon resizing, wrapped into a class for consistency. """
    def __init__(self, icon: QIcon, parent=None):
        """
        :param icon: Icon displayed on the button.
        :param parent: Parent widget of the button.
        """
        super().__init__(parent)

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


if __name__ == "__main__":
    import sys
    from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout
    app = QApplication(sys.argv)

    # Create the main window
    window = QWidget()
    window.setWindowTitle("StandardToolButton Demo")

    # Create an icon for the button
    temp_icon = QIcon.fromTheme("folder")  # Use a standard theme icon

    # Create an instance of StandardToolButton
    button = StandardToolButton(temp_icon)
    button.set_size(100, 50)  # Set the desired button size

    # Create a layout and add the button
    layout = QVBoxLayout()
    layout.addWidget(button)

    # Set the layout to the window
    window.setLayout(layout)
    window.show()

    sys.exit(app.exec())