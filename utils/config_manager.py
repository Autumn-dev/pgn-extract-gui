import os
import json
from PyQt6.QtWidgets import QWidget, QCheckBox, QSpinBox, QComboBox, QLineEdit

class ConfigManager:
    def __init__(self, parent, config_dir="configs"):
        """Manage configuration settings for the application.

        Args:
            parent (_type_): The parent widget containing the configuration settings.
            config_dir (str, optional): The directory to save configuration files. Defaults to "configs".
        """        
        self.parent = parent
        self.config_dir = config_dir
        os.makedirs(config_dir, exist_ok=True)

    def save_config(self, config_name):
        """Save the current configuration settings to a file.

        Args:
            config_name (str): The name of the configuration file (without extension).
        """        

        config_data = {}

        for widget in self.parent.findChildren(QWidget):
            wname = widget.objectName()
            if not wname:
                continue

            if isinstance(widget, QCheckBox):
                config_data[wname] = widget.isChecked()

            elif isinstance(widget, QSpinBox):
                config_data[wname] = widget.value()

            elif isinstance(widget, QComboBox):
                config_data[wname] = widget.currentIndex()

            elif isinstance(widget, QLineEdit):
                config_data[wname] = widget.text()

        file_path = os.path.join(self.config_dir, f"{config_name}.json")

        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(config_data, f, indent=4)

        print(f"Config saved: {file_path}")

    def load_config(self, config_name):
        """Load configuration settings from a file.

        Args:
            config_name (str): The name of the configuration file (without extension).
        """        
        file_path = os.path.join(self.config_dir, f"{config_name}.json")
        
        if not os.path.exists(file_path):
            print(f"Config file '{config_name}' not found.")
            return

        with open(file_path, "r", encoding="utf-8") as f:
            config_data = json.load(f)

        for widget in self.parent.findChildren(QWidget):
            wname = widget.objectName()
            if not wname or wname not in config_data:
                continue

            value = config_data[wname]

            if isinstance(widget, QCheckBox):
                widget.setChecked(bool(value))

            elif isinstance(widget, QSpinBox):
                widget.setValue(int(value))

            elif isinstance(widget, QComboBox):
                widget.setCurrentIndex(int(value))

            elif isinstance(widget, QLineEdit):
                widget.setText(str(value))

        print(f"Config loaded: {file_path}")