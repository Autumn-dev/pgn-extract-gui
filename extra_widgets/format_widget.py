from PyQt6.QtWidgets import QWidget, QHBoxLayout, QLabel, QLineEdit, QVBoxLayout
from .no_scroll_combobox import NoScrollComboBox
from utils import constants
from PyQt6.QtCore import pyqtSignal, Qt

class FormatWidget(QWidget):

    state_changed = pyqtSignal()

    def __init__(self, parent=None):
        """Initialize the FormatWidget.

        Args:
            parent (_type_, optional): _description_. Defaults to None.
        """        
        super().__init__(parent)

        self.output_format_selector = NoScrollComboBox()
        self.output_format_selector.setObjectName("outputformat-combobox")
        self.output_format_selector.setMinimumWidth(constants.min_combobox_width)
        self.output_format_selector.currentIndexChanged.connect(self.update_widgets)
        
        self.san_entry = QLineEdit()
        self.san_entry.setPlaceholderText("Must be 6 characters long e.g., PNBRQK")
        self.san_entry.setFixedSize(250, 25)
        self.san_entry.setVisible(False)
        self.san_entry.setMaxLength(constants.san_arg_length)
        self.san_entry.textChanged.connect(self.state_changed.emit)

        self.output_format_selector.addItem("...", "")
        for item in constants.OUTPUT_FORMATS.keys():
            item_name = constants.OUTPUT_FORMATS[item]
            self.output_format_selector.addItem(item_name, item)

        self.label = QLabel("Output format:")
        self.label.setToolTip("-W Select output format")

        sub_layout = QHBoxLayout()
        sub_layout.addWidget(self.label)
        sub_layout.addWidget(self.output_format_selector)

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 3, 0, 3)
        layout.addLayout(sub_layout)
        layout.addWidget(self.san_entry, alignment=Qt.AlignmentFlag.AlignRight)

        self.setLayout(layout)

    
    def current_index(self):
        """Get the current index of the output format selector.

        Returns:
            int: The current index of the output format selector.
        """        
        return self.output_format_selector.currentIndex()
    

    def current_data(self):
        """Get the current data of the output format selector.

        Returns:
            str: The current data of the output format selector.
        """        
        print(self.output_format_selector.currentData())
        return self.output_format_selector.currentData()
    
    
    def update_widgets(self):
        """Update the visibility of widgets based on the current data.
        """        
        self.san_entry.setVisible(self.current_data() == "san")
        self.state_changed.emit()


    def get_san_suffix(self):
        """Get the SAN suffix from the entry field.

        Returns:
            str: The SAN suffix if valid, empty string otherwise.
        """
        if len(self.san_entry.text()) == constants.san_arg_length:
            return self.san_entry.text()
        else:
            return ""