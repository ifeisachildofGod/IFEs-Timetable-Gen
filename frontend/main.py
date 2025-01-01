from PyQt6.QtWidgets import QMainWindow, QMenuBar, QStatusBar, QToolBar  #, QVBoxLayout, QWidget
from PyQt6.QtGui import QIcon

class Window(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("IFEs Timetable Genererator")
        self.setGeometry(100, 100, 800, 600)
        
        # Menu bar
        menu_bar = QMenuBar(self)
        self.setMenuBar(menu_bar)

        # Status bar
        status_bar = QStatusBar(self)
        self.setStatusBar(status_bar)

        # Tool bar
        tool_bar = QToolBar(self)
        self.addToolBar(tool_bar)

        # Adding some dummy actions to the tool bar
        self.file_action = menu_bar.addAction(QIcon(), "File")
        self.edit_action = menu_bar.addAction(QIcon(), "Edit")
        self.window_action = menu_bar.addAction(QIcon(), "Window")
        
        # Adding some dummy actions to the menu bar
        self.subject_action = tool_bar.addAction(QIcon(), "Subjects")
        self.teacher_action = tool_bar.addAction(QIcon(), "Teachers")
        self.class_action = tool_bar.addAction(QIcon(), "Classes")
        self.timetable_action = tool_bar.addAction(QIcon(), "Timetable")
        self.school_action = tool_bar.addAction(QIcon(), "School")
