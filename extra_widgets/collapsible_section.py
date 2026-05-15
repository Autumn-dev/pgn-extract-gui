from PyQt6.QtWidgets import QWidget, QPushButton, QVBoxLayout, QSizePolicy
from PyQt6.QtCore import Qt


class CollapsibleSection(QWidget):
    """
    Button that toggles visibility of the content area below it.
    Functionally a 'segment' header object
    """
    def __init__(self, title, parent=None, start_collapsed=False):
        """Initialize the CollapsibleSection.

        Args:
            title (str): The title of the section.
            parent (QWidget, optional): The parent widget. Defaults to None.
            start_collapsed (bool, optional): Whether the section should start collapsed. Defaults to False.
        """        
        super().__init__(parent)
        self.setObjectName("CollapsibleSection")

        self.toggle_button = QPushButton(title)
        self.toggle_button.setObjectName("ToggleButton")
        self.toggle_button.setCheckable(True)
        self.toggle_button.setChecked(not start_collapsed)
        self.toggle_button.clicked.connect(self.toggle_content)
        self.toggle_button.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        self.content_area = QWidget()
        self.content_layout = QVBoxLayout()
        self.content_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.content_area.setLayout(self.content_layout)
        self.content_area.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        layout = QVBoxLayout()
        layout.addWidget(self.toggle_button)
        layout.addWidget(self.content_area)
        self.setLayout(layout)
        self.content_area.setVisible(not start_collapsed)

    def toggle_content(self):
        """Toggle the visibility of the content area.
        """        
        visible = self.toggle_button.isChecked()
        self.content_area.setVisible(visible)

    def add_widget(self, widget):
        """Add a widget to the content area.

        Args:
            widget (QWidget): The widget to add.
        """        
        self.content_layout.addWidget(widget)

    def add_layout(self, layout):
        """Add a layout to the content area.

        Args:
            layout (QLayout): The layout to add.
        """        
        self.content_layout.addLayout(layout)