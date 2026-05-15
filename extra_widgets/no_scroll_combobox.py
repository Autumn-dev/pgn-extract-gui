from PyQt6.QtWidgets import QComboBox
from PyQt6.QtGui import QWheelEvent

class NoScrollComboBox(QComboBox):
    """A QComboBox that ignores scroll events.

    Args:
        QComboBox (QComboBox): The base QComboBox class.
    """
    def wheelEvent(self, event: QWheelEvent):
        """Ignore wheel events.

        Args:
            event (QWheelEvent): The wheel event to ignore.
        """        
        event.ignore() 