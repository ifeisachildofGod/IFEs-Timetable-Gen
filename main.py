from frontend.main import *


if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    THEME_MANAGER.apply_theme(app, "light-green")
    
    window = Window(app.arguments())
    window.showMaximized()
    
    sys.exit(app.exec())
