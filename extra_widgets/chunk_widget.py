from PyQt6.QtWidgets import QWidget, QSpinBox, QLabel, QHBoxLayout, QCheckBox
from PyQt6.QtCore import pyqtSignal

class ChunkWidget(QWidget):

    state_changed = pyqtSignal()

    def __init__(self, parent=None):
        """Initialize the ChunkWidget.

        Args:
            parent (QWidget, optional): The parent widget. Defaults to None.
        """        
        super().__init__(parent)

        self.is_enabled = False

        self.chunk_size_entry = QSpinBox()
        self.chunk_size_entry.setObjectName("SplitByChunksize-entry")
        self.chunk_size_entry.setFixedSize(125, 25)
        self.chunk_size_entry.setMinimum(1)
        self.chunk_size_entry.setMaximum(9999999)
        self.chunk_size_entry.setEnabled(False)
        self.chunk_size_entry.setSuffix(" Games/file")
        self.chunk_size_entry.valueChanged.connect(self.state_changed.emit)

        self.enable_checkbox = QCheckBox("Output 'N' games per new file")
        self.enable_checkbox.stateChanged.connect(self.update_widgets)
        self.enable_checkbox.setToolTip("Output a certain number of games per file, starting at a certain number (as filename)")

        self.name_entry = QSpinBox()
        self.name_entry.setObjectName("SplitByChunkincrement-entry")
        self.name_entry.setFixedSize(125, 25)
        self.name_entry.setMaximum(9999999)
        self.name_entry.setEnabled(False)
        self.name_entry.valueChanged.connect(self.state_changed.emit)
        self.name_entry.setPrefix("Starting name: ")

        layout = QHBoxLayout()
        layout.setContentsMargins(0, 3, 0, 3)
        layout.addWidget(self.enable_checkbox)
        layout.addWidget(self.chunk_size_entry)
        layout.addWidget(self.name_entry)
        self.setLayout(layout)


    def update_widgets(self):
        """Update the state of the widgets based on the current selection.
        """        
        self.is_enabled = self.enable_checkbox.isChecked()

        self.chunk_size_entry.setEnabled(self.is_enabled)
        self.name_entry.setEnabled(self.is_enabled)
        self.state_changed.emit()

    
    def get_values(self):
        """Get the current values from the chunk size and name spin boxes.

        Returns:
            tuple: A tuple containing the chunk size and starting name values.
        """        
        return self.chunk_size_entry.value(), self.name_entry.value()