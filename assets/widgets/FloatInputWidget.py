"""
@Author: Foad Alhayek
@Description: A custom widget that accepts numeric input (with dot as decimal separator) and emits the value when Enter
is pressed or the send button is clicked.
"""
from PySide6.QtWidgets import QApplication, QWidget, QHBoxLayout, QLineEdit, QToolButton
from PySide6.QtGui import QIcon, QDoubleValidator
from PySide6.QtCore import QSize, QLocale, Signal

class DotOnlyDoubleValidator(QDoubleValidator):
    """ Inherits from QDoubleValidator and serves as a stricter version by not allowing commas as visual separators. """
    def validate(self, input_str: str, pos: int):
        if "," in input_str:
            return QDoubleValidator.State.Invalid, input_str, pos
        return super().validate(input_str, pos)

class FloatInputWidget(QWidget):
    """
    Custom widget consisting of a line edit box (input) and an interactive button [INPUT][B].
    Accepts only numeric input with dot as a decimal separator, and emits back the value on Enter or button click.

    Attributes:
        value_submitted (Signal): Emits the inputted float when user submits a valid input.
    """
    value_submitted = Signal(float)

    def __init__(self, icon: QIcon, parent=None):
        """
        :param icon: Icon displayed on the button.
        :param parent: Parent widget of the button.
        """
        super().__init__(parent)

        # Init widgets
        self.line_edit = QLineEdit(self)
        self.button = QToolButton()

        # Validator settings
        self.validator = DotOnlyDoubleValidator()
        self.validator.setNotation(DotOnlyDoubleValidator.Notation.StandardNotation)
        self.validator.setLocale(QLocale(QLocale.Language.C))
        self.validator.setDecimals(9)

        # Widget settings
        self.line_edit.setPlaceholderText("Reference time")
        self.line_edit.setValidator(self.validator)

        # Connect on pressing Enter and clicking the button
        self.line_edit.returnPressed.connect(self._submit)
        self.button.clicked.connect(self._submit)

        # Style
        self.line_edit.setStyleSheet('''
            QLineEdit {
              border-width: 1px;
              border-style: solid;
              border-top-left-radius: 6px;
              border-bottom-left-radius: 6px;
            }
        ''')

        self.button.setIcon(icon)
        self.button.setStyleSheet('''
            QToolButton {
              padding: 0px;
              border-width: 1px 1px 1px 0px;
              border-style: solid;
              border-color: black;
              border-top-right-radius: 6px;
              border-bottom-right-radius: 6px;
              background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #f6f7fa, stop: 1 #d3d3d3);
            }
            QToolButton:pressed {
              background: #e1e1e1;
            }
        ''')

        # Define and set layout
        layout = QHBoxLayout()
        layout.addWidget(self.line_edit)
        layout.addWidget(self.button)

        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

    def set_size(self, width, height):
        """ Updates the size of the widget by making sure the combined widgets are aligned and animation works """
        self.line_edit.setFixedSize(width - height, height)
        self.button.setFixedSize(height, height)
        self.button.setIconSize(QSize(height//2, height//2))

        # Animates the button on press
        self.button.setStyleSheet('''
            QToolButton {
                  padding: 0px;
                  border-width: 1px 1px 1px 0px;
                  border-style: solid;
                  border-color: black;
                  border-top-right-radius: 6px;
                  border-bottom-right-radius: 6px;
                  background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #f6f7fa, stop: 1 #d3d3d3);
                }
                QToolButton:pressed {
                  background: #e1e1e1;
                  padding:''' + str(height//4) + '''px;
                }
        ''')

    def _submit(self):
        """ Called when the user submits the input. """
        text = self.line_edit.text().strip()
        text = self.validator.fixup(text)

        try:
            value = float(text)
        except ValueError:
            self.line_edit.clear()
            return

        self.value_submitted.emit(value)
        self.line_edit.clear()


if __name__ == "__main__":
    # Showcasing the usage of the widget.
    app = QApplication([])
    widget = FloatInputWidget(QIcon.fromTheme("folder"))
    widget.set_size(200, 20)
    widget.show()
    app.exec()
