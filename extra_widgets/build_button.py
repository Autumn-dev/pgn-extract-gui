from PyQt6.QtWidgets import QPushButton
from PyQt6.QtGui import QIcon

def build_button(width, height, callback, text=None, name=None, img_name=None, tooltip=None) -> QPushButton:
    """Build a QPushButton with the specified properties.

    Args:
        width (int): The width of the button.
        height (int): The height of the button.
        callback (function): The function to call when the button is clicked.
        text (str, optional): The text to display on the button. Defaults to None.
        name (str, optional): The object name of the button. Defaults to None.
        img_name (str, optional): The image file name to use as the button icon. Defaults to None.
        tooltip (str, optional): The tooltip text for the button. Defaults to None.

    Returns:
        QPushButton: The constructed QPushButton.
    """    

    button = QPushButton()
    button.setFixedSize(width, height)
    button.clicked.connect(callback)
    if text: 
        button.setText(text)
    if name: 
        button.setObjectName(name)
    if img_name: 
        button.setIcon(QIcon(f"imgs/{img_name}"))
    if tooltip: 
        button.setToolTip(tooltip)
    return button