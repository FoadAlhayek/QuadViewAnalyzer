"""
@Author: Foad Alhayek
@Description: A custom widget that accepts numeric input (with dot as decimal separator) and emits the value when Enter
is pressed and has a customizable trigger button used to trigger other code logic outside this widget.
"""
from PySide6.QtWidgets import QApplication, QWidget, QLineEdit, QToolButton, QSizePolicy
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
    Accepts only numeric input with dot as a decimal separator, and emits back the value on Enter press.
    Button click, will emit a different signal free of use.

    Attributes:
        value_submitted (Signal): Emits the inputted float when user submits a valid input.
        button_clicked (Signal): Emits nothing, used to trigger other code logic outside this widget
    """
    value_submitted = Signal(float)
    button_clicked = Signal()

    def __init__(self, icon: QIcon, placeholder_text: str="", parent=None):
        """
        :param icon: Icon displayed on the button.
        :param placeholder_text: The text that should be used as a placeholder
        :param parent: Parent widget of the button.
        """
        super().__init__(parent)
        # Class settings
        self.min_width = 148
        self.min_height = 20
        self.setMinimumSize(self.min_width, self.min_height)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        # Init widgets and set this class as their parent so they are part of the widgets hierarchy
        self.lineEdit = QLineEdit(self)
        self.button = QToolButton(self)

        # Validator settings
        self.validator = DotOnlyDoubleValidator()
        self.validator.setNotation(DotOnlyDoubleValidator.Notation.StandardNotation)
        self.validator.setLocale(QLocale(QLocale.Language.C))
        self.validator.setDecimals(9)

        # Widget settings
        self.lineEdit.setPlaceholderText(placeholder_text)
        self.lineEdit.setValidator(self.validator)

        # Connect on pressing Enter and clicking the button
        self.lineEdit.returnPressed.connect(self._submit)
        self.button.clicked.connect(self.button_clicked.emit)

        # Style - This will make it not possible to style the defined things from outside, consider in the future
        # to make it more dynamic. Maybe put it in a function where the "default styling" is this but can be replaced.
        self.lineEdit.setStyleSheet('''
            QLineEdit {
              padding: 2px;
              margin-left: 1px;
              border-width: 1px 0px 1px 1px;
              border-style: solid;
              border-color: #dcdcdc;
              border-bottom-color: #808080;
              border-top-left-radius: 5px;
              border-bottom-left-radius: 5px;
            }
            QLineEdit:focus {
              border-bottom-color: #0067c0;
            }
        ''')

        self.button.setIcon(icon)
        self.button.setStyleSheet('''
            QToolButton {
              padding: 0px;
              border-width: 1px 1px 1px 0px;
              border-style: solid;
              border-color: #dcdcdc;
              border-bottom-color: #808080;
              border-top-right-radius: 5px;
              border-bottom-right-radius: 5px;
              background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #f6f7fa, stop: 1 #d3d3d3);
            }
            QToolButton:pressed {
              background: #e1e1e1;
            }
        ''')

    def set_placeholder_text(self, text):
        self.lineEdit.setPlaceholderText(text)

    def set_size(self, width, height):
        if width - height < self.min_width - self.min_height:
            height = width - self.min_width

        if height < self.min_height:
            height = self.min_height

        line_width = width - height

        # Order the widgets
        self.lineEdit.setGeometry(0, 0, line_width, height)
        self.button.setGeometry(line_width, 0, height, height)
        self.button.setIconSize(QSize(height // 2, height // 2))

        # Animates the button on press
        self.button.setStyleSheet('''
            QToolButton {
              padding: 0px;
              border-width: 1px 1px 1px 0px;
              border-style: solid;
              border-color: #dcdcdc;
              border-bottom-color: #808080;
              border-top-right-radius: 5px;
              border-bottom-right-radius: 5px;
              background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #f6f7fa, stop: 1 #d3d3d3);
            }
            QToolButton:pressed {
              background: #e1e1e1;
              padding:''' + str(height // 4) + '''px;
            }
        ''')

    def sizeHint(self, /):
        return QSize(self.min_width, self.min_height)

    def minimumSizeHint(self, /):
        return QSize(self.min_width, self.min_height)

    def setMinimumHeight(self, minh, /):
        self.min_height = minh
        self.set_size(self.width(), minh)
        super().setMinimumHeight(minh)

    def resizeEvent(self, event, /):
        """ Override to maintain the correct internal proportions and animation. """
        self.set_size(self.width(), self.height())
        super().resizeEvent(event)

    def _submit(self):
        """ Called when the user submits the input. """
        text = self.lineEdit.text().strip()
        text = self.validator.fixup(text)

        try:
            value = float(text)
        except ValueError:
            self.lineEdit.clear()
            return

        self.value_submitted.emit(value)
        self.lineEdit.clear()


if __name__ == "__main__":
    # Showcasing the usage of the widget.
    app = QApplication([])
    widget = FloatInputWidget(QIcon.fromTheme("folder"))
    widget.show()
    app.exec()
