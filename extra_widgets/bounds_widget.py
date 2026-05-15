from PyQt6.QtWidgets import QWidget, QComboBox, QSpinBox, QHBoxLayout, QLabel
from PyQt6.QtCore import pyqtSignal


class BoundsWidget(QWidget):
    """
    For min/max ply/moves
    """
    state_changed = pyqtSignal()

    def __init__(self, parent=None):
        """Initialize the BoundsWidget.

        Args:
            parent (QWidget, optional): The parent widget. Defaults to None.
        """        
        super().__init__(parent)
        self.flag_enabled = False

        self.mode_combobox = QComboBox()
        self.mode_combobox.setObjectName("bounds-combobox")
        self.max_spinbox = QSpinBox()
        self.max_spinbox.setObjectName("boundsmax-spinbox")
        self.min_spinbox = QSpinBox()
        self.min_spinbox.setObjectName("boundsmix-spinbox")

        self.mode_combobox.addItems(["...", "Moves", "Plies"])
        self.mode_combobox.currentIndexChanged.connect(self.update_widgets)

        self.max_spinbox.setPrefix("≤ ")
        self.max_spinbox.valueChanged.connect(self.update_widgets)
        self.max_spinbox.setRange(0, 1000)
        self.max_spinbox.setFixedSize(75, 25)
        self.max_spinbox.setEnabled(False)

        self.min_spinbox.setPrefix("≥ ")
        self.min_spinbox.valueChanged.connect(self.update_widgets)
        self.max_spinbox.setRange(0, 1000)
        self.min_spinbox.setFixedSize(75, 25)
        self.min_spinbox.setEnabled(False)

        left_layout = QHBoxLayout()
        left_layout.addWidget(QLabel("Set boundaries:"))

        right_layout = QHBoxLayout()
        right_layout.addWidget(QLabel("Move/Ply"))
        right_layout.addWidget(self.mode_combobox)
        right_layout.addWidget(QLabel("Min:"))
        right_layout.addWidget(self.min_spinbox)
        right_layout.addWidget(QLabel("Max:"))
        right_layout.addWidget(self.max_spinbox)

        layout = QHBoxLayout()
        layout.setContentsMargins(0, 8, 0, 8)
        layout.setSpacing(8)
        layout.addLayout(left_layout)
        layout.addLayout(right_layout)

        self.setLayout(layout)


    def update_widgets(self):
        """Update the state of the widgets based on the current selection.
        """        
        self.flag_enabled = self.mode_combobox.currentIndex() != 0

        self.min_spinbox.setEnabled(self.flag_enabled)
        self.max_spinbox.setEnabled(self.flag_enabled)
        
        # Min cannot exceed Max, Max cannot subceed Min
        self.min_spinbox.setRange(0, self.max_spinbox.value())
        self.max_spinbox.setRange(self.min_spinbox.value(), 1000)

        self.state_changed.emit()
