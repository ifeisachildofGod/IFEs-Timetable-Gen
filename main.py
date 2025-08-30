from frontend.main import *


if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    window = Window(app, app.arguments())
    window.showMaximized()
    
    sys.exit(app.exec())
