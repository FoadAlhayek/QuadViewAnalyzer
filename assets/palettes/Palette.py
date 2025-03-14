"""
The themes used for the application

Feel free to create new palettes.
Remember to add new variables in the default class Theme and then override with the specific color you want to use in a
new palette. This is to ensure the new variable exists and is inherited in all palette themes.

Note: LightTheme is and should be the default Theme.

Usage: QuadView.py
"""


class Theme:
    background = "#f0f0f0"
    foreground = "#f0f0f0"
    text = "#0B1215"
    header_text = "#0B1215"
    label_text = "#0B1215"
    button = "#d3d3d3"
    pressed_button = "e1e1e1"
    inactive_button = "#f0f0f0"
    button_text = "#0B1215"
    highlight = "#87CEFA"
    highlight_text = "#051650"
    accent = "#f2bf15"
    accent_text = "#231d07"
    placeholder_text = "#7f7f7f"
    empty_widget = "#FAF9F6"
    legend_text = "#f5ece9"


class LightTheme(Theme):
    pass


class DarkTheme(Theme):
    background = "#1e1a16"
    foreground = "#f5ece9"
    text = "#f5ece9"
    header_text = "#f5ece9"
    label_text = "#f5ece9"
    button_text = "#141414"
    highlight_text = "#141414"
    highlight = "#d77f48"


class EasterEggTheme(Theme):
    background = "#f90b0b"
    text = "#63250e"
    button = "#1b5300"
    inactive_button = "#3f8f29"
    header_text = "#8cd4ff"
    label_text = "#8cd4ff"
    button_text = "#63250e"
    highlight_text = "#ffd97d"
    highlight = "#ffd97d"
    empty_widget = "#3f8f29"
    placeholder_text = "#d3d3d3"


if __name__ == "__main__":
    pass
