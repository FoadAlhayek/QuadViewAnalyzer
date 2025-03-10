"""
@Author: Foad Alhayek
@Description: A custom QTreeView widget that differentiates between left and right double-click events. It emits a
custom signal when a right double-click occurs, allowing external handlers to process the event accordingly.
"""
from PySide6.QtWidgets import QTreeView
from PySide6.QtCore import Qt, Signal, QModelIndex


class CustomTreeView(QTreeView):
    """
    CustomTreeView extends QTreeView to handle right-button double-click events separately.

    Attributes:
        rightDoubleClicked (Signal): Emitted when an item is double-clicked with the right mouse button.
    """
    rightDoubleClicked = Signal(QModelIndex)

    def mouseDoubleClickEvent(self, event):
        """ Adds custom right double click event. """
        index = self.indexAt(event.pos())

        if not index.isValid():
            event.ignore()
            return

        if event.button() == Qt.MouseButton.RightButton:
            self.rightDoubleClicked.emit(index)
        else:
            super().mouseDoubleClickEvent(event)