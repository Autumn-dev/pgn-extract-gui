from PyQt6.QtWidgets import QWidget, QCheckBox, QHBoxLayout

class EnumCheckbox(QWidget):
    def __init__(self, flag_enum, label_text="", default_state=False, tooltip_text="", parent=None):
        """Initialize the EnumCheckbox.

        Args:
            flag_enum (Enum): The enumeration value associated with the checkbox.
            label_text (str, optional): The label text for the checkbox. Defaults to "".
            default_state (bool, optional): The default checked state of the checkbox. Defaults to False.
            tooltip_text (str, optional): The tooltip text for the checkbox. Defaults to "".
            parent (QWidget, optional): The parent widget. Defaults to None.
        """        
        super().__init__(parent)

        self.checkbox = QCheckBox(label_text)
        self.checkbox.setObjectName(f"{flag_enum.name}-checkbox") 
        self.checkbox.setChecked(default_state)
        self.checkbox.setToolTip(f"{flag_enum.value} {tooltip_text}")

        self.stateChanged = self.checkbox.stateChanged
        self.isChecked = self.checkbox.isChecked

        layout = QHBoxLayout()
        layout.setContentsMargins(0, 1, 0, 1)
        layout.setSpacing(1)
        layout.addWidget(self.checkbox)
        self.setLayout(layout)