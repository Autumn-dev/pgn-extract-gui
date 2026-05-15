from PyQt6.QtWidgets import QWidget, QCheckBox, QLineEdit, QVBoxLayout, QHBoxLayout, QLabel
from PyQt6.QtCore import pyqtSignal

from .path_input_block import PathInputBlock
from .no_scroll_combobox import NoScrollComboBox
from utils import constants


class MaterialMatchWidget(QWidget):
    """
    Widget for selecting material match method 
    """
    state_changed = pyqtSignal()

    def __init__(self, parent=None):
        """Initialize the MaterialMatchWidget.

        Args:
            parent (QWidget, optional): The parent widget. Defaults to None.
        """        
        super().__init__(parent)
        self.flag_enabled = False

        # Enable, and choose mode (y/z)
        self.mode_combobox = NoScrollComboBox()
        self.mode_combobox.setObjectName("MaterialMatches-combobox")
        self.mode_combobox.setMinimumWidth(constants.min_combobox_width)
        self.mode_combobox.addItems(["...", "One-sided", "Both sides"])
        self.mode_combobox.currentIndexChanged.connect(self.update_widgets)

        label = QLabel("Enable material matching")
        mode_layout = QHBoxLayout()
        mode_layout.addWidget(label)
        mode_layout.addWidget(self.mode_combobox)

        # Choose between in-line (--materialy/z) or File (-y/-z)
        self.use_file_checkbox = QCheckBox("Use file containing material balances")
        self.use_file_checkbox.setObjectName("MaterialMatches-checkbox")
        self.use_file_checkbox.stateChanged.connect(self.update_widgets)
        self.use_file_checkbox.hide()

        # For -y/-z
        self.file_selector = PathInputBlock(placeholder_text="e.g., balances.txt", obj_name="MaterialMatches-pathinput")
        self.file_selector.path_changed.connect(self.update_widgets)
        self.file_selector.hide()

        # For --materialy/z
        self.entry_section = QWidget()
        entry_layout = QHBoxLayout()

        self.entry = QLineEdit()
        self.entry.setObjectName("MaterialMatches-entry")
        self.entry.setMinimumHeight(25)
        self.entry.setPlaceholderText("e.g., RP NB")
        self.entry.textChanged.connect(self.update_widgets)
        self.entry_label = QLabel("Material match string")

        entry_layout.addWidget(self.entry_label)
        entry_layout.addWidget(self.entry)
        self.entry_section.setLayout(entry_layout)
        self.entry_section.hide()
        

        layout = QVBoxLayout()
        layout.addLayout(mode_layout)
        layout.addWidget(self.use_file_checkbox)
        layout.addWidget(self.file_selector)
        layout.addWidget(self.entry_section)

        self.setLayout(layout)


    def update_widgets(self):
        """Update the visibility of widgets based on the current data.
        """        
        self.flag_enabled = self.mode_combobox.currentIndex() != 0
        self.use_file_checkbox.setVisible(self.flag_enabled)

        # Reference variables for flag updates
        self.using_file = self.use_file_checkbox.isChecked()
        self.mode = "y" if self.mode_combobox.currentIndex() == 1 else "z"
        
        self.file_selector.setVisible(self.flag_enabled and self.using_file)
        self.entry_section.setVisible(self.flag_enabled and not self.using_file)

        if self.using_file:
            self.contents = self.file_selector.text
        else:
            self.contents = self.entry.text()

        self.state_changed.emit()

