from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QScrollArea, QLayout
from PyQt6.QtCore import Qt


class PanelLayout(QWidget):
    """
    Dual side-by-side panels which are scroll areas.
    """
    def __init__(self, parent=None):
        """Initialize the PanelLayout.

        Args:
            parent (QWidget, optional): The parent widget. Defaults to None.
        """        
        super().__init__(parent)
        self.setObjectName("Panels")
        # L panel
        self.left_panel_widget = QWidget()
        self.left_panel_layout = QVBoxLayout(self.left_panel_widget)
        self.left_panel_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        left_scroll = QScrollArea()
        left_scroll.setWidgetResizable(True)
        left_scroll.setWidget(self.left_panel_widget)
        left_scroll.setObjectName("Panel_L")
        # R panel
        self.right_panel_widget = QWidget()
        self.right_panel_layout = QVBoxLayout(self.right_panel_widget)
        self.right_panel_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        right_scroll = QScrollArea()
        right_scroll.setWidgetResizable(True)
        right_scroll.setWidget(self.right_panel_widget)
        right_scroll.setObjectName("Panel_R")

        # Main layout
        main_layout = QHBoxLayout()
        main_layout.addWidget(left_scroll)
        main_layout.addWidget(right_scroll)

        self.setLayout(main_layout)


    def add_left(self, item):
        """
        Add something to the left panel. Widget or Layout
        """
        if isinstance(item, QLayout):
            container = QWidget()
            container.setLayout(item)
            self.left_panel_layout.addWidget(container)
        else:
            self.left_panel_layout.addWidget(item)


    def add_right(self, item):
        """
        Add something to the right panel. Widget or Layout
        """
        if isinstance(item, QLayout):
            container = QWidget()
            container.setLayout(item)
            self.right_panel_layout.addWidget(container)
        else:
            self.right_panel_layout.addWidget(item)
