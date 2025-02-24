from PySide6.QtCore import QSortFilterProxyModel, Qt

class CustomFilterProxyModel(QSortFilterProxyModel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFilterCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)

    def filterAcceptsRow(self, source_row, source_parent):
        """
        Default behaviour only sorts and filters flat data structures such as arrays/lists and does not otherwise handle
        hierarchical data such as a tree menu (QTreeView).
        """
        # source_model is the tree_model
        source_model = self.sourceModel()
        index = source_model.index(source_row, 0, source_parent)
        if not index.isValid():
            return False

        # Check if the current index matches the filter
        if self.filterRegularExpression().match(source_model.data(index)).hasMatch():
            return True

        # Use a stack to iteratively check all children
        stack = []
        for i in range(source_model.rowCount(index)):
            child_index = source_model.index(i, 0, index)
            stack.append(child_index)

        while stack:
            current_index = stack.pop()
            if self.filterRegularExpression().match(source_model.data(current_index)).hasMatch():
                return True
            # Push all children of the current index onto the stack
            for i in range(source_model.rowCount(current_index)):
                child_index = source_model.index(i, 0, current_index)
                stack.append(child_index)

        return False