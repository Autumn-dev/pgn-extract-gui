from PyQt6.QtWidgets import QPlainTextEdit, QSizePolicy

class OutputViewer(QPlainTextEdit):
    """
    Class for viewing output of pgn-extract as a text viewer.
    """

    def __init__(self, parent=None):
        """Initialize the OutputViewer.

        Args:
            parent (QWidget, optional): The parent widget. Defaults to None.
        """        
        super().__init__(parent)

        self.setObjectName("OutputViewer")
        self.setReadOnly(True)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.setPlaceholderText("Output from pgn-extract will appear here..")