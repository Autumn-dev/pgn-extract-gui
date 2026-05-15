from PyQt6.QtWidgets import QWidget, QLabel, QHBoxLayout
from utils import constants
from .no_scroll_combobox import NoScrollComboBox


class EnumCombobox(QWidget):
    """
    Label and combobox widget builder for build_enum_combobox
    """
    def __init__(self, flag_enum_group, label_text="", tooltip_text="",  item_names=[], parent=None):
        """Initialize the EnumCombobox.

        Args:
            flag_enum_group (Enum): The enumeration group for the combobox.
            label_text (str, optional): The label text for the combobox. Defaults to "".
            tooltip_text (str, optional): The tooltip text for the combobox. Defaults to "".
            item_names (list, optional): The display names for the combobox items. Defaults to [].
            parent (QWidget, optional): The parent widget. Defaults to None.
        """        
        super().__init__(parent)
        
        self.combobox = NoScrollComboBox()
        self.combobox.setObjectName(f"{flag_enum_group.__name__}-combobox")
        self.combobox.setMinimumWidth(constants.min_combobox_width)
        
        # add items (use enum names if no item_names arg)
        for i, item in enumerate(flag_enum_group):
            item_name = str(item_names[i] if item_names else item.name)
            if item_name == "Disabled": item_name = "..."
            self.combobox.addItem(item_name, item)

        self.combobox.currentIndexChanged.connect(self._update_attributes)
        self.current_index = self.combobox.currentIndex
        self.current_data = self.combobox.currentData

        self.label = QLabel(label_text)
        summary = (f"{tooltip_text}\n" if tooltip_text else "") + "\n".join(
            e.value if e.value else e.name for e in flag_enum_group if e.name != "Disabled")
        self.label.setToolTip(summary)

        layout = QHBoxLayout()
        layout.setContentsMargins(0, 3, 0, 3)
        layout.setSpacing(1)
        layout.addWidget(self.label)
        layout.addWidget(self.combobox)
        self.setLayout(layout)


    def _update_attributes(self):
        """Update the current index and data attributes based on the combobox selection.
        """        
        self.current_index = self.combobox.currentIndex()
        self.current_data = self.combobox.currentData()