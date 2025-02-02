import sys
from PyQt6.QtWidgets import QApplication

from frontend.main import Window


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Window()
    window.showMaximized()
    sys.exit(app.exec())
