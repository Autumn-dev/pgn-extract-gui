from PyQt6.QtCore import Qt, pyqtSignal, QSettings

from utils import constants

from .build_button import build_button
from .no_scroll_combobox import NoScrollComboBox

from PyQt6.QtWidgets import (
    QWidget, QLineEdit, QVBoxLayout, QHBoxLayout,
    QScrollArea, QFileDialog, QCompleter, QFrame, QLabel
)


class TagWindow(QWidget):
    """
    Tag-critera matching widget.
    """
    tag_file_created = pyqtSignal(str)

    def __init__(self, parent=None):
        """Initialize the TagWindow.

        Args:
            parent (QWidget, optional): The parent widget. Defaults to None.
        """        
        super().__init__(parent)

        self.settings = QSettings("UniversityOfKent", "pgn-extract-gui")
        self.settings_group = "TagWindow"

        self.restoreGeometry(self.settings.value(f"{self.settings_group}/geometry", b""))
        self.setWindowTitle("Tags file builder")

        # Tag data: {Key: TagElement}
        self.tags_data: dict[str, TagElement] = {}

        self.key_input = QLineEdit()
        self.key_input.setPlaceholderText("Tag name... e.g., White")
        # Auto-suggest for key input
        self.completer = QCompleter(constants.COMMON_TAGS)
        self.completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self.completer.setFilterMode(Qt.MatchFlag.MatchContains)
        self.key_input.setCompleter(self.completer)

        self.op_selector = NoScrollComboBox()
        self.op_selector.addItems(constants.TAG_OPERATORS)
        self.op_selector.setCurrentIndex(0)

        self.value_input = QLineEdit()
        self.value_input.setPlaceholderText("Value... e.g., Carlsen")

        self.add_tag_btn = build_button(
            text="← Add tag",
            width=70,
            height=25,
            callback=self.add_tag
        )
        self.add_tag_btn.setEnabled(False)

        self.key_input.textChanged.connect(self.update_add_button_state)
        self.value_input.textChanged.connect(self.update_add_button_state)

        # Scroll area
        self.tag_list_area = QWidget()

        self.tag_view = QScrollArea()
        self.tag_view.setWidgetResizable(True)
        self.tag_view.setFixedHeight(250)

        # Save button
        self.save_btn = build_button(
            text="Save tag file",
            width=110,
            height=30,
            callback=self.export_tags
        )
        
        main_layout = QVBoxLayout()

        self.input_row = QHBoxLayout()
        self.input_row.addWidget(self.key_input)
        self.input_row.addWidget(self.op_selector)
        self.input_row.addWidget(self.value_input)
        self.input_row.addWidget(self.add_tag_btn)

        # Dynamic tag list view area (goes in the scrollable)
        self.tag_view_container = QWidget()
        self.tag_view_layout = QVBoxLayout(self.tag_view_container)
        self.tag_view_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.tag_view.setWidget(self.tag_view_container)

        main_layout.addLayout(self.input_row)
        main_layout.addWidget(self.tag_view)
        main_layout.addWidget(self.save_btn, alignment=Qt.AlignmentFlag.AlignCenter)
        self.setLayout(main_layout)


    def add_tag(self):
        """Add a new tag to the tag list.
        """        
        key = self.key_input.text().strip()
        value = self.value_input.text().strip()
        operator = self.op_selector.currentText()
        
        # If key already exists in list, then just update the value and/or operator
        if key in self.tags_data:
            tag_to_edit = self.tags_data[key]
            tag_to_edit.set_value(value)
            if operator:
                tag_to_edit.set_operator(operator)
            else:
                tag_to_edit.set_operator(None)
        else:
            tag_to_add = TagElement(key, value, operator, parent=self)
            self.tags_data[key] = tag_to_add
            self.tag_view_layout.addWidget(tag_to_add)

        self.key_input.clear()
        self.value_input.clear()
        self.op_selector.setCurrentIndex(0)
        self.update_add_button_state()


    def remove_tag(self, key):
        """Remove a tag from the tag list.

        Args:
            key (str): The key of the tag to remove.
        """        
        tag_to_remove = self.tags_data[key]
        tag_to_remove.setParent(None)
        del self.tags_data[key]
        

    def update_add_button_state(self):
        """Update the state of the add tag button.
        """        
        key = self.key_input.text().strip()
        value = self.value_input.text().strip()
        self.add_tag_btn.setEnabled(bool(key and value))


    def export_tags(self):
        """Export the current tags to a file.
        """        
        lines = []
        for key, tag in self.tags_data.items():
            if tag.operator: 
                line = f"{key} {tag.operator} \"{tag.value}\""
            else:
                line = f"{key} \"{tag.value}\""

            lines.append(line)

        file_contents = "\n".join(lines)
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save tag file",
            "",
            "Text Files (*.txt);;All Files (*)"
        )
        if file_path:
            if not file_path.endswith(".txt"):
                file_path += ".txt"
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(file_contents)

        self.tag_file_created.emit(str(file_path))


    def closeEvent(self, event):
        """Handle the close event for the tag window.

        Args:
            event (QCloseEvent): The close event.
        """        
        self.settings.setValue(f"{self.settings_group}/geometry", self.saveGeometry())
        super().closeEvent(event)


class TagElement(QFrame):
    """
    An individual element in the TagCriteria scroll-list
    """
    def __init__(self, key, value, operator=None, parent=None):
        """Initialize the TagElement.

        Args:
            key (str): The key of the tag.
            value (str): The value of the tag.
            operator (str, optional): The operator for the tag. Defaults to None.
            parent (QWidget, optional): The parent widget. Defaults to None.
        """        
        super().__init__(parent)
        self.key = key
        self.value = value
        self.operator = operator
        self.criteria_parent = parent

        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(5, 1, 5, 1)

        self.key_label = QLabel(key)
        self.key_label.setStyleSheet("font-weight: bold;")
        self.layout.addWidget(self.key_label)

        if self.operator:
            self.op_label = QLabel(self.operator)
            self.layout.addWidget(self.op_label)

        self.value_label = QLabel(f"\"{value}\"")
        self.layout.addWidget(self.value_label)

        remove_btn = build_button(
            img_name="x_icon.png",
            width=constants.remove_btn_size,
            height=constants.remove_btn_size,
            callback=self.delete
        )
        self.layout.addStretch()
        self.layout.addWidget(remove_btn)


    def set_value(self, new_value):
        """Set the value of the tag.

        Args:
            new_value (str): The new value for the tag.
        """        
        self.value = new_value
        self.value_label.setText(f"\"{new_value}\"")


    def set_operator(self, new_operator):
        """Set the operator for the tag.

        Args:
            new_operator (str): The new operator for the tag.
        """        
        if not self.operator:
            self.op_label = QLabel(self.operator)
            self.layout.insertWidget(1, self.op_label)
        self.op_label.setText(new_operator)
        self.operator = new_operator


    def delete(self):
        """Delete the tag element.
        """        
        if self.criteria_parent:
            self.criteria_parent.remove_tag(self.key)