import subprocess, gzip, json, shutil

from copy import deepcopy
from typing import Callable
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout,
    QVBoxLayout, QPushButton, QStackedWidget,
    QMessageBox, QFileDialog   
)
from PyQt6.QtGui import QAction
from PyQt6.QtCore import QThread, Qt
from matplotlib.cbook import flatten
from frontend.setting_widgets import SettingWidget, Subjects, Teachers, Classes
from frontend.editing_widgets import TimeTableEditor
from frontend.theme import *
from middle.main import School

EXTENSION_NAME = "ttbl"

class Thread(QThread):
    def __init__(self, func: Callable):
        super().__init__()
        self.func = func
    
    def run(self):
        try:
            self.func()
        except Exception as e:
            print(e)
            self.terminate()

def gzip_file(input_file_path: str):
    try:
        with gzip.open(input_file_path, "rb") as file:
            json.load(file)
        
        return input_file_path, None
    except:
        output_file_path = input_file_path + "." + (f"converted.{EXTENSION_NAME}" if input_file_path.endswith("." + EXTENSION_NAME) else EXTENSION_NAME)
    
    with open(input_file_path, 'rb') as f_in:
        with gzip.open(output_file_path, 'wb') as f_out:
            shutil.copyfileobj(f_in, f_out)
    
    return output_file_path, input_file_path

class Window(QMainWindow):
    def __init__(self, args):
        super().__init__()
        
        # Default data
        self.default_period_amt = 10  # Being used by the timetable editor
        self.default_breakperiod = 7  #   "     "   "  "      "       "
        self.default_per_day = 2      # Being used by the settings editors
        self.default_per_week = 4     #   "     "   "  "     "        "
        self.default_save_data = {"levels": [], "subjectTeacherMapping": {}, 'subjects': {}}
        self.default_weekdays = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
        
        # Get saved data
        self.path = None
        self.uncompressed_path = None
        self.save_data = deepcopy(self.default_save_data)
        self.orig_data = deepcopy(self.save_data)
        
        self.setWindowTitle(f"IFEs Timetable Generator")
        
        if len(args) > 1:
            self.path = args[1]
            
            self.path, self.uncompressed_path = gzip_file(self.path)
            
            with gzip.open(self.path, "rb") as file:
                self.save_data = json.load(file)
            
            self._fix_data()
            
            self.setWindowTitle(self.windowTitle() + " - " + self.path)
        
        # Initialize school data
        self.school = School(self.save_data)
        
        # Set application style
        self.setStyleSheet(THEME[WINDOW])
        
        # Misc
        self.display_index = 0
        self.prev_display_index = 0
        
        self.setGeometry(100, 100, 1000, 700)
        
        self.create_menu_bar()
        
        # Create main container
        container = QWidget()
        main_layout = QHBoxLayout()
        container.setLayout(main_layout)
        
        # Create sidebar with modern styling
        sidebar = QWidget()
        sidebar.setFixedWidth(200)
        sidebar.setStyleSheet(THEME[WINDOW_SIDEBAR])
        
        # Create sidebar layout
        sidebar_layout = QVBoxLayout()
        sidebar_layout.setSpacing(0)
        sidebar_layout.setContentsMargins(0, 0, 0, 0)
        
        # Create stacked widget for content
        self.stack = QStackedWidget()
        
        # Create navigation buttons
        subjects_btn = QPushButton("Subjects")
        teachers_btn = QPushButton("Teachers")
        classes_btn = QPushButton("Classes")
        timetable_btn = QPushButton("Timetable")
        
        subjects_btn.setCheckable(True)
        teachers_btn.setCheckable(True)
        classes_btn.setCheckable(True)
        timetable_btn.setCheckable(True)
        
        # Add widgets to stack
        self.subjects_widget = Subjects(self, self.save_data.get("subjectsInfo"))
        self.teachers_widget = Teachers(self, self.save_data.get("teachersInfo"))
        self.classes_widget = Classes(self, self.save_data.get("classesInfo"))
        
        self.timetable_widget = TimeTableEditor(self, self.school)
        
        self.option_buttons = [subjects_btn, teachers_btn, classes_btn, timetable_btn]
        
        self.stack.addWidget(self.subjects_widget)
        self.stack.addWidget(self.teachers_widget)
        self.stack.addWidget(self.classes_widget)
        self.stack.addWidget(self.timetable_widget)
        
        # Connect buttons
        for index, button in enumerate(self.option_buttons):
            button.clicked.connect(self.make_option_button_func(index))
        
        # Add buttons to sidebar
        sidebar_layout.addWidget(subjects_btn)
        sidebar_layout.addWidget(teachers_btn)
        sidebar_layout.addWidget(classes_btn)
        sidebar_layout.addStretch()
        sidebar_layout.addWidget(timetable_btn)
        sidebar.setLayout(sidebar_layout)
        
        # Add widgets to main layout
        main_layout.addWidget(sidebar)
        main_layout.addWidget(self.stack)
        
        self.setCentralWidget(container)
        subjects_btn.click()  # Start with subjects page selected
        
        self.orig_data = deepcopy(self.save_data)
    
    def _fix_data(self):
        subjects_data = self.save_data.get("subjectsInfo")
        teachers_data = self.save_data.get("teachersInfo")
        classes_data = self.save_data.get("classesInfo")
        
        if subjects_data is not None:
            for subject_info in subjects_data["variables"].values():
                for k in subject_info["teachers"]["id_mapping"].copy().keys():
                    subject_info["teachers"]["id_mapping"][int(k)] = subject_info["teachers"]["id_mapping"].pop(k)
        
        if teachers_data is not None:
            for teacher_info in self.save_data["teachersInfo"]["variables"].values():
                for k in teacher_info["subjects"]["id_mapping"].copy().keys():
                    teacher_info["subjects"]["id_mapping"][int(k)] = teacher_info["subjects"]["id_mapping"].pop(k)
        
        if classes_data is not None:
            for class_info in self.save_data["classesInfo"]["variables"].values():
                for k in class_info["subjects"]["id_mapping"].copy().keys():
                    class_info["subjects"]["id_mapping"][int(k)] = class_info["subjects"]["id_mapping"].pop(k)
                
                for subject_in_class_info in class_info["subjects"]["content"].values():
                    for k in subject_in_class_info["teachers"]["id_mapping"].copy().keys():
                        subject_in_class_info["teachers"]["id_mapping"][int(k)] = subject_in_class_info["teachers"]["id_mapping"].pop(k)
    
    def _file_dialog(self, func: Callable[[tuple[str, str]], str], file_mode: str):
        open_file_dialog = QFileDialog()
        match file_mode:
            case "save":
                func(open_file_dialog.getSaveFileName(caption="Save As"))
            case "open":
                func(open_file_dialog.getOpenFileName(caption="Open File", options=QFileDialog.Option.ReadOnly))
            case "new":
                func(open_file_dialog.getSaveFileName(caption="New File"))
            case "folder":
                func(open_file_dialog.getExistingDirectory(caption="Folder"))
    
    def _make_new_file(self, path: tuple[str, str]):
        with open(path[0], "w") as file:
            json.dump(deepcopy(self.default_save_data), file, indent=2)
        
        create_new_file_thread = Thread(lambda : subprocess.run(["py", "main.py", path[0]]))
        create_new_file_thread.start()
    
    def _set_path(self, path: tuple[str, str]):
        self.path = path[0]
    
    def _save_file_as(self, path: tuple[str, str], uncompressed_path: str | None = None):
        self.update_interaction(self.prev_display_index, self.display_index)
        
        data = self.save_data.copy()
        data.update(self.get_settings_info())
        
        with gzip.open(path[0], "wb") as file:
            file.write(json.dumps(data, indent=2).encode())
        
        if uncompressed_path is not None:
            with open(uncompressed_path, "w") as u_file:
                json.dump(data, u_file, indent=2)
    
    def new(self):
        self._file_dialog(self._make_new_file, "new")
    
    def open(self):
        def func(path):
            create_new_file_thread = Thread(lambda : subprocess.run(["py", "main.py", path]))
            create_new_file_thread.start()
        
        self._file_dialog(func, "open")
    
    def save(self):
        self.save_data.update(self.get_settings_info())
        
        if self.path is None:
            self._file_dialog(self._set_path, "save")
        
        self._save_file_as(self.path, self.uncompressed_path)
        self.orig_data = deepcopy(self.save_data)
    
    def save_as(self):
        self._file_dialog(self._save_file_as, "save")
    
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
        
        # Add File Actions
        new_action = QAction("New", self)
        open_action = QAction("Open", self)
        save_action = QAction("Save", self)
        save_as_action = QAction("Save_as", self)
        exit_action = QAction("Exit", self)
        
        new_action.setShortcut("Ctrl+N")
        open_action.setShortcut("Ctrl+O")
        save_action.setShortcut("Ctrl+S")
        save_as_action.setShortcut("Ctrl+Shift+S")
        
        new_action.triggered.connect(self.new)
        open_action.triggered.connect(self.open)
        save_action.triggered.connect(self.save)
        save_as_action.triggered.connect(self.save_as)
        exit_action.triggered.connect(self.close)
        
        file_menu.addActions([new_action, open_action, save_action, save_as_action, exit_action])
        
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
    
    def xl_equal(self, value1, value2):
        if isinstance(value1, dict):
            if isinstance(value2, dict):
                if self.xl_equal(sorted(list(value1.keys())), sorted(list(value2.keys()))):
                    if self.xl_equal(list(value1.values()), list(value2.values())):
                        return True
            return False
        elif isinstance(value1, (list, tuple, set)):
            if isinstance(value2, (list, tuple, set)):
                for i, v in enumerate(value1):
                    if i < len(value2):
                        if not self.xl_equal(v, value2[i]):
                            break
                        continue
                    break
                else:
                    return True
            
            return False
        else:
            if not value1 == value2:
                if (
                    (isinstance(value1, (int, float)) and isinstance(value2, str)) or
                    (isinstance(value2, (int, float)) and isinstance(value1, str))
                    ) and (value1.isnumeric() or value2.isnumeric()):
                    return float(value1) == float(value1)
            
            return value1 == value2
    
    def closeEvent(self, event):
        for thread in self.timetable_widget.THREADS:
            thread.quit()
        
        if not self.xl_equal(self.orig_data, self.save_data):
            reply = QMessageBox.question(self, "Save", "Save before quitting?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No | QMessageBox.StandardButton.Cancel)
            
            if reply == QMessageBox.StandardButton.Yes:
                self.save()
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
        match curr_index:
            case 0:  # Subjects view
                self.subjects_widget.update_data_interaction(prev_index, curr_index)
                self.teachers_widget.update_data_interaction(prev_index, curr_index)
                self.classes_widget.update_data_interaction(prev_index, curr_index)
            case 1:  # Teachers view
                self.teachers_widget.update_data_interaction(prev_index, curr_index)
                self.subjects_widget.update_data_interaction(prev_index, curr_index)
                self.classes_widget.update_data_interaction(prev_index, curr_index)
            case 2: # Classes view
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
