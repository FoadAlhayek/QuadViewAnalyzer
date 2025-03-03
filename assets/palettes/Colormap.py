"""
@Author: Foad Alhayek
@Description: Colormap with distinguishable colors. Inspired from matplotlib e.g., Set3 and tab10 colormaps.
"""
from PySide6.QtGui import QColor
from collections import deque

class Colormap:
    """
    Manages multiple colormaps with lazy initialization, dynamic color reuse, and independent instances.

    Attributes:
        COLORMAPS (dict): A dictionary of predefined colormaps, shared across all instances
                          to avoid redundant memory allocation.
    """
    # Define colormaps at the class level to avoid re-creating it for every instance
    COLORMAPS = {
        "tab10": [
            "#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd",
            "#8c564b", "#e377c2", "#7f7f7f", "#bcbd22", "#17becf"
        ],
        "set3": [
            "#8dd3c7", "#ffffb3", "#bebada", "#fb8072", "#80b1d3", "#fdb462",
            "#b3de69", "#fccde5", "#d9d9d9", "#bc80bd", "#ccebc5", "#ffed6f"
        ],
        "tab20": [
            "#1f77b4", "#aec7e8", "#ff7f0e", "#ffbb78", "#2ca02c", "#98df8a", "#d62728", "#ff9896", "#9467bd", "#c5b0d5",
            "#8c564b", "#c49c94", "#e377c2", "#f7b6d2", "#7f7f7f", "#c7c7c7", "#bcbd22", "#dbdb8d", "#17becf", "#9edae5"
        ],
        "fof20": [ # Similar to tab20, but all dark colors first then lighter version in the second half
            "#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd", "#8c564b", "#e377c2", "#7f7f7f", "#bcbd22", "#17becf",
            "#aec7e8", "#ffbb78", "#98df8a", "#ff9896", "#c5b0d5", "#c49c94", "#f7b6d2", "#c7c7c7", "#dbdb8d", "#9edae5"
        ]
    }

    def __init__(self, colormap_name: str = "tab10"):
        """ Initialize a colormap cycle for a specific colormap: Available: tab10, set3, tab20, fof20 """
        if colormap_name not in self.COLORMAPS:
            raise ValueError(f"Colormap '{colormap_name}' is not available. Choose from {list(self.COLORMAPS.keys())}")

        self.colormap_name = colormap_name
        self.all_colors = tuple(self.COLORMAPS[colormap_name])
        self.available_colors = deque(self.all_colors)
        self.colors_in_use_by_item = dict()

    def get_color(self, item_id) -> QColor:
        """ Returns the next available color from the selected colormap as a QColor object. """
        if item_id in self.colors_in_use_by_item:
            return QColor(self.colors_in_use_by_item[item_id])

        # Either pick from available colors or cycle if no new colors exists
        if self.available_colors:
            color = self.available_colors.popleft()
        else:
            idx = len(self.colors_in_use_by_item) % len(self.all_colors)
            color = self.all_colors[idx]

        # Track and return color
        self.colors_in_use_by_item[item_id] = color
        return QColor(color)

    def release_color(self, item_id):
        """ Releases the color and returns it to the pool of available colors. """
        if item_id in self.colors_in_use_by_item:
            color = self.colors_in_use_by_item.pop(item_id)
            self.available_colors.appendleft(color)

    def reset(self):
        """ Resets the colormap cycle to the beginning. """
        self.available_colors = deque(self.all_colors)
        self.colors_in_use_by_item = dict()

    def set_colormap(self, colormap_name: str):
        """ Changes the colormap dynamically and resets the cycle. """
        if colormap_name not in self.COLORMAPS:
            raise ValueError(f"Colormap '{colormap_name}' is not available. Choose from {list(self.COLORMAPS.keys())}")

        self.colormap_name = colormap_name
        self.all_colors = tuple(self.COLORMAPS[colormap_name])
        self.reset()

    def available_cm(self):
        """ Returns available colormap names in a list. """
        return list(self.COLORMAPS.keys())

if __name__ == "__main__":
    pass