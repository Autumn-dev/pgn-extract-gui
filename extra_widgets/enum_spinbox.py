from PyQt6.QtWidgets import QSpinBox, QCheckBox, QHBoxLayout, QWidget

class EnumSpinbox(QWidget):
    """
    Create a spinbox for a flag, enabling the flag when checked and passing the spinbox value as the argument.
    """
    def __init__(self, flag_enum, label_text="", min_value=0, max_value=9999999, step=1, width=100, tooltip_text="", parent=None):
        """Initialize the EnumSpinbox.

        Args:
            flag_enum (Enum): The enumeration value associated with the spinbox.
            label_text (str, optional): The label text for the spinbox. Defaults to "".
            min_value (int, optional): The minimum value for the spinbox. Defaults to 0.
            max_value (int, optional): The maximum value for the spinbox. Defaults to 9999999.
            step (int, optional): The step size for the spinbox. Defaults to 1.
            width (int, optional): The width of the spinbox. Defaults to 100.
            tooltip_text (str, optional): The tooltip text for the spinbox. Defaults to "".
            parent (QWidget, optional): The parent widget. Defaults to None.
        """        
        super().__init__(parent)
        self.checkbox = QCheckBox(label_text)
        self.checkbox.setObjectName(f"{flag_enum.name}-spinboxcheckbox")
        self.checkbox.setToolTip(f"{flag_enum.value} {tooltip_text}")

        self.spinbox = QSpinBox()
        self.spinbox.setObjectName(f"{flag_enum.name}-spinboxvalue")
        self.spinbox.setMinimum(min_value)
        self.spinbox.setMaximum(max_value)
        self.spinbox.setSingleStep(step)
        self.spinbox.setFixedSize(width, 25)

        layout = QHBoxLayout()
        layout.setContentsMargins(0, 3, 0, 3)
        layout.setSpacing(1)
        layout.addWidget(self.checkbox)
        layout.addWidget(self.spinbox)
        self.setLayout(layout)


    def is_checked(self):
        """Check if the spinbox is enabled.

        Returns:
            bool: True if the spinbox is enabled, False otherwise.
        """        
        return self.checkbox.isChecked()
    
    @property
    def value(self):
        """Get the current value of the spinbox.

        Returns:
            int: The current value of the spinbox.
        """        
        return self.spinbox.value