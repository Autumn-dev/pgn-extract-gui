from PyQt6.QtCore import QRunnable, pyqtSignal, QObject
import subprocess

from utils.testing import log_execution_time

class WorkerSignals(QObject):
    finished = pyqtSignal()
    error = pyqtSignal(str)
    output = pyqtSignal(str)
    game_processed = pyqtSignal()

class ExtractWorker(QRunnable):
    """Worker for extracting PGN data.
    """    
    def __init__(self, command, output_path):
        """Initialize the extract worker.

        Args:
            command (str): The command to run.
            output_path (str): The path to the output file.
        """
        super().__init__()
        self.command = command
        self.output_path = output_path
        self.signals = WorkerSignals()
        self.process = None

    @log_execution_time
    def run(self):
        """Run the extraction process.
        """
        try:
            self.process = subprocess.Popen(
                self.command,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                universal_newlines=True
            )

            for line in self.process.stdout:
                self.signals.output.emit(line.rstrip("\n"))
                self.signals.game_processed.emit()

            self.process.wait()
            self.signals.finished.emit()

        except Exception as e:
            self.signals.error.emit(str(e))


    @classmethod
    def get_pgn_extract_version(self):
        """Get the version of pgn-extract.

        Returns:
            str: The version of pgn-extract.
        """        
        result = subprocess.run("pgn-extract --version", capture_output=True, text=True)
        return result.stderr
    

    def terminate(self):
        """Terminate the extraction process.
        """
        if self.process and self.process.poll() is None:
            self.process.terminate()