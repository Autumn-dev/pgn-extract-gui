from PyQt6.QtWidgets import QWidget, QCheckBox, QLineEdit, QHBoxLayout


class EnumEntryField(QWidget):
    def __init__(self, flag_enum, label_text="", placeholder_text="", tooltip_text="", parent=None):
        """Initialize the EnumEntryField.

        Args:
            flag_enum (Enum): The enumeration value associated with the entry field.
            label_text (str, optional): The label text for the entry field. Defaults to "".
            placeholder_text (str, optional): The placeholder text for the entry field. Defaults to "".
            tooltip_text (str, optional): The tooltip text for the entry field. Defaults to "".
            parent (QWidget, optional): The parent widget. Defaults to None.
        """        
        super().__init__(parent)

        self.checkbox = QCheckBox(label_text)
        self.checkbox.setObjectName(f"{flag_enum.name}-entrycheckbox") 
        self.checkbox.setToolTip(f"{flag_enum.value} {tooltip_text}")

        self.entry_field = QLineEdit()
        self.entry_field.setObjectName(f"{flag_enum.name}-entrytext")
        self.entry_field.setPlaceholderText(placeholder_text)
        self.entry_field.setFixedSize(200, 25)

        layout = QHBoxLayout()
        layout.setContentsMargins(0, 3, 0, 3)
        layout.setSpacing(1)
        layout.addWidget(self.checkbox)
        layout.addWidget(self.entry_field)
        self.setLayout(layout)