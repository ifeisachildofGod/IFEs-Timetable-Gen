import gzip, json

from copy import deepcopy
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout,
    QVBoxLayout, QPushButton, QStackedWidget,
    QMessageBox
)
from PyQt6.QtGui import QAction
from PyQt6.QtCore import pyqtSignal
from matplotlib.cbook import flatten
from frontend.setting_widgets import SettingWidget, Subjects, Teachers, Classes
from frontend.editing_widgets import TimeTableEditor
from frontend.others import *

from middle.main import School


class Window(QMainWindow):
    saved_state_changed = pyqtSignal()
    
    def __init__(self, path: str | None):
        super().__init__()
        self.title = "IFEs Timetable Generator"
        
        self.file = FileManager(self, path, f"Timetable Files (*.{EXTENSION_NAME});;JSON Files (*.json)")
        self.file.set_callbacks(self.save_callback, self.open_callback, self.load_callback)
        
        # Default data
        self.default_period_amt = 10  # Being used by the timetable editor and settings editor
        self.default_breakperiod = 7  #   "     "   "  "      "       "     "     "       "
        self.default_per_day = 2      # Being used by the settings editors
        self.default_per_week = 4     #   "     "   "  "     "        "
        self.default_save_data = {"levels": [], "subjectTeacherMapping": {}, 'subjects': {}}
        self.default_weekdays = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
        
        self.children_saved_tracker = {}
        
        # Get saved data
        self._init_data()
        self.saved_state_changed.connect(self.unsaved_callback)
        
        # Initialize school data
        self.school = School(self.save_data)
        
        # Misc
        self.display_index = 0
        self.prev_display_index = 0
        
        self.setGeometry(100, 100, 1000, 700)
        
        self.create_menu_bar()
        
        # Create main container
        container = QWidget()
        main_layout = QHBoxLayout()
        container.setLayout(main_layout)
        
        # Create sidebar
        sidebar = QWidget()
        sidebar_layout = QVBoxLayout()
        
        sidebar.setFixedWidth(200)
        sidebar.setLayout(sidebar_layout)
        sidebar.setProperty("class", "Sidebar")
        
        sidebar_layout.setSpacing(0)
        sidebar_layout.setContentsMargins(0, 0, 0, 0)
        
        # Create stacked widget for content
        self.stack = QStackedWidget()
        
        # Create navigation buttons
        subjects_btn = QPushButton("Subjects")
        teachers_btn = QPushButton("Teachers")
        classes_btn = QPushButton("Classes")
        timetable_btn = QPushButton("Timetable")
        
        # Add widgets to stack
        self.subjects_widget = Subjects(self, self.save_data.get("subjectsInfo"), self.saved_state_changed)
        self.teachers_widget = Teachers(self, self.save_data.get("teachersInfo"), self.saved_state_changed)
        self.classes_widget = Classes(self, self.save_data.get("classesInfo"), self.saved_state_changed)
        
        self.timetable_widget = TimeTableEditor(self, self.school)
        
        self.option_buttons = [subjects_btn, teachers_btn, classes_btn, timetable_btn]
        
        self.stack.addWidget(self.subjects_widget)
        self.stack.addWidget(self.teachers_widget)
        self.stack.addWidget(self.classes_widget)
        self.stack.addWidget(self.timetable_widget)
        
        # Connect buttons
        for index, button in enumerate(self.option_buttons):
            button.setCheckable(True)
            button.clicked.connect(self.make_option_button_func(index))
        
        # Add buttons to sidebar
        sidebar_layout.addWidget(subjects_btn)
        sidebar_layout.addWidget(teachers_btn)
        sidebar_layout.addWidget(classes_btn)
        sidebar_layout.addStretch()
        sidebar_layout.addWidget(timetable_btn)
        
        # Add widgets to main layout
        main_layout.addWidget(sidebar)
        main_layout.addWidget(self.stack)
        
        self.setCentralWidget(container)
        subjects_btn.click()  # Start with subjects page selected
        
        self.orig_data = deepcopy(self.save_data)
    
    def _init_data(self):
        self.saved = False
        self.uncompressed_path = None
        self.save_data = deepcopy(self.default_save_data)
        self.orig_data = deepcopy(self.save_data)
        
        if self.file.path is not None:
            self.file.path, self.uncompressed_path = gzip_file(self.file.path)
            
            self.save_data = self.file.get_data()
            
            self._fix_data()
            
            self.setWindowTitle(f"{self.title} - {self.file.path}")
            
            self.saved = True
        else:
            self.setWindowTitle(self.title)
    
    def unsaved_callback(self):
        self.saved = False
        self.setWindowTitle(f"{self.title} - {self.file.path} *Unsaved")
    
    def _fix_data(self):
        subjects_data = self.save_data.get("subjectsInfo")
        teachers_data = self.save_data.get("teachersInfo")
        
        if subjects_data is not None:
            for subject_info in subjects_data["variables"].values():
                for k in subject_info["teachers"]["id_mapping"].copy().keys():
                    subject_info["teachers"]["id_mapping"][int(k)] = subject_info["teachers"]["id_mapping"].pop(k)
        
        if teachers_data is not None:
            for teacher_info in self.save_data["teachersInfo"]["variables"].values():
                for k in teacher_info["subjects"]["id_mapping"].copy().keys():
                    teacher_info["subjects"]["id_mapping"][int(k)] = teacher_info["subjects"]["id_mapping"].pop(k)
    
    def load_callback(self, path: str):
        with gzip.open(path, "rb") as file:
            content = json.load(file)
        
        return content
    
    def open_callback(self, path: str):
        # def func(path):
        win = Window([path])
        win.showMaximized()
        
        if not hasattr(self, '_windows'):
            self._windows = []
        self._windows.append(win)
        # self._file_dialog(func, "open")
    
    def save_callback(self, path: str):
        self.saved = True
        
        self.file.path = path
        
        self.update_interaction(self.display_index, self.prev_display_index)
        
        self.save_data.update(self.get_settings_info())
        
        with gzip.open(self.file.path, "wb") as file:
            file.write(json.dumps(self.save_data, indent=2).encode())
        
        if self.uncompressed_path is not None:
            with open(self.uncompressed_path, "w") as u_file:
                json.dump(self.save_data, u_file, indent=2)
        
        self.orig_data = deepcopy(self.save_data)
        
        self.setWindowTitle(f"{self.title} - {self.file.path}")
    
    def undo(self):
        undo_func = self.focusWidget().__dict__.get("undo")
        if undo_func is not None:
            undo_func()
    
    def redo(self):
        redo_func = self.focusWidget().__dict__.get("redo")
        if redo_func is not None:
            redo_func()
    
    def create_menu_bar(self):
        menubar = self.menuBar()
        
        # File Menu
        file_menu = menubar.addMenu("File")
        edit_menu = menubar.addMenu("Edit")
        help_menu = menubar.addMenu("Help")
        
        # Add all actions
        file_menu.addAction("New", "Ctrl+N", self.file.new)
        file_menu.addAction("Open", "Ctrl+O", self.file.open)
        file_menu.addAction("Save", "Ctrl+S", self.file.save)
        file_menu.addAction("Save As", "Ctrl+Shift+S", self.file.save_as)
        file_menu.addAction("Close", self.close)
        
        # Add Edit Actions
        undo_action = QAction("Undo", self)
        redo_action = QAction("Redo", self)
        
        undo_action.setShortcut("Ctrl+Z")
        redo_action.setShortcut("Ctrl+Y")
        
        undo_action.triggered.connect(self.undo)
        redo_action.triggered.connect(self.redo)
        
        edit_menu.addActions([undo_action, redo_action])
    
    def get_settings_info(self):
        setting_widgets: dict[str, SettingWidget] = {
            "subjectsInfo": self.subjects_widget,
            "teachersInfo": self.teachers_widget,
            "classesInfo": self.classes_widget
        }
        
        return {
            widget_name: {
                "variables": widget.get(),
                "constants": widget.get_constants()
            }
            for widget_name, widget in
            setting_widgets.items()
        }
    
    def closeEvent(self, event):
        if not self.saved:
            reply = QMessageBox.question(self, "Save", "Save before quitting?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No | QMessageBox.StandardButton.Cancel)
            
            if reply == QMessageBox.StandardButton.Yes:
                self.file.save()
            elif reply == QMessageBox.StandardButton.Cancel:
                event.ignore()
                return
        
        event.accept()
    
    def make_option_button_func(self, index: int):
        def func():
            for i, btn in enumerate(self.option_buttons):
                btn.setChecked(i == index)
            
            if self.display_index != index:
                self.stack.setCurrentIndex(index)
                self.update_interaction(self.display_index, index)
                self.prev_display_index = self.display_index
                self.display_index = index
        
        return func
    
    def update_interaction(self, prev_index: int, curr_index: int):
        match prev_index:
            case 3:
                for _, (_, info1) in self.school.project["subjects"].items():
                    for _, (_, _, info2) in info1.items():
                        for _, (_, info3) in info2.items():
                            info3.clear()
                
                for _, cls in self.school.classes.items():
                    self.timetable_widget.timetable_widgets[cls.uniqueID].save_timetable()
        
        match curr_index:
            case 0:  # Subjects view
                self.subjects_widget.update_data_interaction(prev_index, curr_index)
                self.teachers_widget.update_data_interaction(prev_index, curr_index)
                self.classes_widget.update_data_interaction(prev_index, curr_index)
            case 1:  # Teachers view
                self.teachers_widget.update_data_interaction(prev_index, curr_index)
                self.subjects_widget.update_data_interaction(prev_index, curr_index)
                self.classes_widget.update_data_interaction(prev_index, curr_index)
            case 2:  # Classes view
                self.classes_widget.update_data_interaction(prev_index, curr_index)
                self.subjects_widget.update_data_interaction(prev_index, curr_index)
                self.teachers_widget.update_data_interaction(prev_index, curr_index)
            case 3:  # Timetable view
                if prev_index == 0:
                    self.teachers_widget.update_data_interaction(prev_index, curr_index)
                    self.classes_widget.update_data_interaction(prev_index, curr_index)
                elif prev_index == 1:
                    self.subjects_widget.update_data_interaction(prev_index, curr_index)
                    self.classes_widget.update_data_interaction(prev_index, curr_index)
                elif prev_index == 2:
                    self.subjects_widget.update_data_interaction(prev_index, curr_index)
                    self.teachers_widget.update_data_interaction(prev_index, curr_index)
                self.timetable_widget.update_data_interaction()



