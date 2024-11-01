import sys

import urllib.request
import urllib.parse
import urllib.error

from pathlib import Path

from PyQt5.QtWidgets import QMainWindow, QApplication, QFileDialog, QMessageBox
from PyQt5.uic import loadUiType

# Load UI file
UI, _ = loadUiType('Design.UI')


class App(QMainWindow, UI):
    """
    Main Application Class for the URL Download App.

    This class provides a GUI to input a URL and a save location to download a file.
    It includes functions to parse and validate URLs, browse for file save location,
    and track download progress.
    """

    def __init__(self, parent=None):
        """
        Initialize the main application window and connect buttons to their corresponding functions.

        Args:
            parent (QWidget, optional): The parent widget. Defaults to None.
        """

        super(App, self).__init__(parent)
        QMainWindow.__init__(self)
        self.setupUi(self)

        self.setWindowTitle('URL Download App')
        self.setFixedSize(750, 600)

        # Connect buttons to functions
        self.download_button.clicked.connect(self.download)
        self.browse_button.clicked.connect(self.browse)

        self.progress_bar.setValue(0)

    @staticmethod
    def extract_media_url(url: str) -> str:
        """
        Extract the media URL from the given URL if it contains the 'media_url' query parameter.

        Args:
            url (str): The input URL.

        Returns:
            str: The extracted media URL if available, otherwise returns the input URL.
        """

        parsed_url = urllib.parse.urlparse(url)
        params = urllib.parse.parse_qs(parsed_url.query)
        media_url = params.get('mediaurl', [None])[0]

        return media_url if media_url else url

    @staticmethod
    def has_extension(file_path: Path) -> bool:
        """
        Check if the given file path has an extension.

        Args:
            file_path (Path): The file path to check.

        Returns:
            bool: True if the file path has an extension, False otherwise.
        """

        return file_path.suffix != ''

    def download(self) -> None:
        """
        Download the file from the URL entered by the user to the specified location.
        Updates progress bar during the download and handles errors.
        """

        url = self.extract_media_url(self.url_line_edit.text())
        location = Path(self.location_line_edit.text())

        if not self.has_extension(location):
            extension = Path(urllib.parse.urlparse(url).path).suffix
            location = location.with_suffix(extension)

        self.url_line_edit.setText('')
        self.location_line_edit.setText('')

        try:
            urllib.request.urlretrieve(url, location, self.handle_progress)
            QMessageBox.information(self, "Download Completed", "The Download Completed Successfully")
            self.progress_bar.setValue(0)

        except urllib.error.URLError as e:
            QMessageBox.warning(self, "Download Error", f"Failed to download the file. Error: {str(e)}")

        except Exception as e:
            QMessageBox.warning(self, "Download Error", f"An error occurred: {str(e)}")

    def browse(self) -> None:
        """
        Open a file dialog for the user to specify a save location for the download.
        """

        location: str = QFileDialog.getSaveFileName(self, caption='Save as', directory='')[0]
        self.location_line_edit.setText(location)

    def handle_progress(self, block_number: int, block_size: int, total_size: int) -> None:
        """
        Update the progress bar based on the download progress.

        Args:
            block_number (int): The current block number being downloaded.
            block_size (int): The size of each block.
            total_size (int): The total size of the file being downloaded.
        """

        read = block_number * block_size
        if total_size > 0:
            percent = int(read * 100 / total_size)
            if percent > 100:
                percent = 100
            self.progress_bar.setValue(percent)
            QApplication.processEvents()

        if read >= total_size:
            self.progress_bar.setValue(100)
            QApplication.processEvents()


def main() -> None:
    """
    Main entry point of the application.
    Initializes the QApplication and the main window, then starts the event loop.
    """

    app = QApplication(sys.argv)
    window = App()
    window.show()
    app.exec()


if __name__ == '__main__':
    main()
