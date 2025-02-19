"""
The ViewModel logic for the application following the MVVM pattern.

The ViewModel is allowed to import the Model and View.
The ViewModel creates the signals and emits them. It should not handle any complicated logic, that is handled by the
Model. For example, adding two numbers is handled by the Model while emitting back the result to the View is handled by
the ViewModel.

Usage: main.py, QuadView.py
"""
import pathlib
from PySide6.QtCore import QObject, Signal

class QuadViewModel(QObject):
    def __init__(self, model):
        super().__init__()
        self._model = model
        self.mat = pathlib.Path("")

    def set_mat(self, path):
        """ Stores the path of the selected file """
        self.mat = path

    def loadmat(self):
        self._model.loadmat(self.mat)

    def start_qva(self):
        print("Hello", self._model.ready_to_run(self.mat), self.mat)
        if not self._model.ready_to_run(self.mat):
            print("Test")
            return None



if __name__ == '__main__':
    pass
