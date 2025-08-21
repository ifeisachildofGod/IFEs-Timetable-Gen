import sys
from PyQt6.QtWidgets import QApplication
from frontend.main import Window
from frontend.theme.theme import THEME_MANAGER


if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    THEME_MANAGER.apply_theme(app, "dark-blue")
    
    window = Window(app.arguments())
    window.showMaximized()
    
    sys.exit(app.exec())
