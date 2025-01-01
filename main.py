import sys
from PyQt6.QtWidgets import QApplication

from frontend.main import Window
from middle.main import School


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Window()
    window.show()
    sys.exit(app.exec())
