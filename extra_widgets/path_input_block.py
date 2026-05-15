from PyQt6.QtWidgets import QWidget, QLineEdit, QHBoxLayout, QFileDialog
from PyQt6.QtCore import pyqtSignal

from utils import constants
from .build_button import build_button

class PathInputBlock(QWidget):
    """
    Input, browse, and clear path widget. MODES: 'output' and 'select'
    """
    path_changed = pyqtSignal()

    def __init__(self, parent=None, browse_text="Browse", placeholder_text="Path or filename...", mode="output", obj_name=""):
        """Initialize the PathInputBlock.

        Args:
            parent (QWidget, optional): The parent widget. Defaults to None.
            browse_text (str, optional): The text for the browse button. Defaults to "Browse".
            placeholder_text (str, optional): The placeholder text for the input field. Defaults to "Path or filename...".
            mode (str, optional): The mode of the input block. Defaults to "output".
            obj_name (str, optional): The object name for the input field. Defaults to "".
        """        
        super().__init__(parent)

        self.mode = mode
        self.text_area = QLineEdit()
        self.text_area.setObjectName(obj_name)
        self.text_area.setFixedHeight(25)
        self.text_area.setPlaceholderText(placeholder_text)
        self.text_area.textChanged.connect(self.path_changed.emit)

        self.browse_btn = build_button(
            text=browse_text,
            width=95,
            height=30,
            callback=lambda: self.choose_output_path(self.text_area)
        )

        self.clear_btn = build_button(
            img_name="x_icon.png",
            width=constants.remove_btn_size,
            height=constants.remove_btn_size,
            callback=lambda: self.text_area.setText("")
        )

        layout = QHBoxLayout()
        layout.addWidget(self.browse_btn)
        layout.addWidget(self.text_area)
        layout.addWidget(self.clear_btn)
        self.setLayout(layout)


    @property
    def text(self):
        """Get the text from the input field.

        Returns:
            str: The text from the input field.
        """        
        return self.text_area.text()

    @text.setter
    def text(self, value):
        """Set the text for the input field.

        Args:
            value (str): The text to set for the input field.
        """        
        self.text_area.setText(value)
    

    def choose_output_path(self, label):
        """Choose an output path (new or existing file) via File explorer.

        Args:
            label (QLineEdit): The label to update with the chosen path.
        """        
        if self.mode == "output":
            file_path, selected_ext = QFileDialog.getSaveFileName(
                self,
                "Choose output path",
                "",
                "All Files (*);;PGN Files (*.pgn);;Text Files (*.txt)"
            )

            if file_path:
                if selected_ext == "PGN Files (*.pgn)" and not file_path.endswith(".pgn"):
                    file_path += ".pgn"
                elif selected_ext == "Text Files (*.txt)" and not file_path.endswith(".txt"):
                    file_path += ".txt"
                label.setText(file_path)

        elif self.mode == "select":
            file_path, _ = QFileDialog.getOpenFileName(
                self,
                "Select input file",
                "",
                "All Files (*);;PGN Files (*.pgn);;Text Files (*.txt)"
            )
            if file_path:
                label.setText(file_path)