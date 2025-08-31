from frontend.imports import *

from frontend.setting_widgets import *
from frontend.editing_widgets import TimeTableEditor

class Window(QMainWindow):
    saved_state_changed = pyqtSignal()
    
    def __init__(self, app: QApplication, arguments: list[str]):
        super().__init__()
        path = len(arguments) > 1 and arguments[1] or None
        
        self.app = app
        self.title = "IFEs Timetable Generator"
        
        self.file = FileManager(self, path, f"Timetable Files (*.{EXTENSION_NAME});;JSON Files (*.json)")
        self.file.set_callbacks(self.save_callback, self.open_callback, self.load_callback)
        
        # Default data
        self.default_period_amt   =   10  # Being used by the timetable editor
        self.default_breakperiod  =   7   #   "     "   "  "      "       "
        self.default_per_day      =   2   # Being used by the classes editor
        self.default_per_week     =   4   #   "     "   "  "     "       "
        self.default_max_classes  =   3   # Being used by the teachers editor
        self.default_save_data    = {"levels": [], "subjectTeacherMapping": {}}
        self.default_weekdays     = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
        
        self.children_saved_tracker = {}
        
        # Setting resize geometry
        self.setGeometry(100, 100, 1000, 700)
        
        # Get saved data
        self._init_save_data()
        self.saved_state_changed.connect(self.unsaved_callback)
        
        # Initialize school data
        self.school = School(self.save_data)
        
        # Misc
        self.display_index = 0
        self.prev_display_index = 0
        
        self.create_menu_bar()
        
        # Create main container
        container = QWidget()
        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(0, 10, 5, 5)
        container.setLayout(main_layout)
        
        # Create sidebar
        main_sidebar_widget = QWidget()
        main_sidebar_layout = QHBoxLayout()
        
        main_sidebar_widget.setLayout(main_sidebar_layout)
        main_sidebar_widget.setProperty("class", "Sidebar")
        
        # self.toggle_sidebar_button = CustomLabel("▼", 90)
        # self.toggle_sidebar_button.setProperty("class", "SidebarToggleButton")
        # self.toggle_sidebar_button.mouseclicked.connect(self.toggle_sidebar)
        # self.toggle_sidebar_button.setFixedSize(20, 150)
        
        self.sub_sidebar_widget = QWidget()
        sub_sidebar_layout = QVBoxLayout()
        
        self.sub_sidebar_widget.setFixedWidth(200)
        self.sub_sidebar_widget.setLayout(sub_sidebar_layout)
        self.sub_sidebar_widget.setProperty("class", "SubSidebar")
        
        sub_sidebar_layout.setSpacing(0)
        sub_sidebar_layout.setContentsMargins(0, 0, 0, 0)
        
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
        
        self.timetable_widget = TimeTableEditor(self, self.school, self.save_data.get("timetableInfo"), self.saved_state_changed)
        
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
        sub_sidebar_layout.addWidget(subjects_btn)
        sub_sidebar_layout.addWidget(teachers_btn)
        sub_sidebar_layout.addWidget(classes_btn)
        sub_sidebar_layout.addStretch()
        sub_sidebar_layout.addWidget(timetable_btn)
        
        # Add sub sidebar widgets to main sidebar layout
        main_sidebar_layout.addWidget(self.sub_sidebar_widget)
        # main_sidebar_layout.addWidget(self.toggle_sidebar_button)
        
        # Add widgets to main layout
        main_layout.addWidget(main_sidebar_widget)
        main_layout.addWidget(self.stack)
        
        self.setCentralWidget(container)
        subjects_btn.click()  # Start with subjects page selected
        
        self.orig_data = deepcopy(self.save_data)
    
    def _init_save_data(self):
        self.saved = True
        self.uncompressed_path = None
        self.save_data = deepcopy(self.default_save_data)
        self.orig_data = deepcopy(self.save_data)
        
        if self.file.path is not None:
            self.file.path, self.uncompressed_path = gzip_file(self.file.path)
            
            self.save_data = self.file.get_data()
            
            self._fix_data()
            
            self.setWindowTitle(f"{self.title} - {self.file.path}")
        else:
            self.setWindowTitle(self.title)
        
        self._make_set_app_stylsheet(self.save_data.get("theme", "dark-blue"))()
    
    # def toggle_sidebar(self):
    #     if self.sub_sidebar_widget.isVisible():
    #         self.toggle_sidebar_button.setAngle(270)
    #         self.sub_sidebar_widget.setVisible(False)
            
    #         b1 = 0
    #         b2 = 15
    #     else:
    #         self.toggle_sidebar_button.setAngle(90)
    #         self.sub_sidebar_widget.setVisible(True)
            
    #         b1 = 15
    #         b2 = 0
        
    #     self.toggle_sidebar_button.setStyleSheet(f"""
    #         border-top-left-radius: {b1}px;
    #         border-bottom-left-radius: {b1}px;
    #         border-top-right-radius: {b2}px;
    #         border-bottom-right-radius: {b2}px;
    #     """)
    
    def unsaved_callback(self):
        self.saved = False
        self.setWindowTitle(f"{self.title} - {self.file.path} *Unsaved")
    
    def _fix_data(self):
        subjects_data = self.save_data.get("subjectsInfo")
        teachers_data = self.save_data.get("teachersInfo")
        
        if subjects_data is not None:
            if "id_mapping" in subjects_data["constants"]:
                for k in subjects_data["constants"]["id_mapping"].copy().keys():
                    subjects_data["constants"]["id_mapping"][int(k)] = subjects_data["constants"]["id_mapping"].pop(k)
            
            for subject_info in subjects_data["variables"].values():
                for k in subject_info["teachers"]["id_mapping"].copy().keys():
                    subject_info["teachers"]["id_mapping"][int(k)] = subject_info["teachers"]["id_mapping"].pop(k)
        
        if teachers_data is not None:
            if "id_mapping" in teachers_data["constants"]:
                for k in teachers_data["constants"]["id_mapping"].copy().keys():
                    teachers_data["constants"]["id_mapping"][int(k)] = teachers_data["constants"]["id_mapping"].pop(k)
            
            for teacher_info in self.save_data["teachersInfo"]["variables"].values():
                for k in teacher_info["subjects"]["id_mapping"].copy().keys():
                    teacher_info["subjects"]["id_mapping"][int(k)] = teacher_info["subjects"]["id_mapping"].pop(k)
    
    def load_callback(self, path: str):
        with gzip.open(path, "rb") as file:
            content = json.load(file)
        
        return content
    
    def open_callback(self, path: str| None = None):
        win = Window(self.app, ["main.py", path] if path is not None else [])
        win.showMaximized()
        
        if not hasattr(self, '_windows'):
            self._windows = []
        self._windows.append(win)
    
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
        
        export_menu = QMenu("Export", self)
        
        export_menu.addAction("Single")
        export_menu.addAction("Batch")
        
        # File Menu
        file_menu = menubar.addMenu("File")
        edit_menu = menubar.addMenu("Edit")
        theme_menu = menubar.addMenu("Theme")
        help_menu = menubar.addMenu("Help")
        
        # Add all actions
        file_menu.addAction("New", "Ctrl+N", self.file.new)
        file_menu.addSeparator()
        file_menu.addAction("Open", "Ctrl+O", self.file.open)
        file_menu.addSeparator()
        file_menu.addAction("Save", "Ctrl+S", self.file.save)
        file_menu.addAction("Save As", "Ctrl+Shift+S", self.file.save_as)
        file_menu.addMenu(export_menu)
        file_menu.addSeparator()
        file_menu.addAction("Close", self.close)
        
        # Add Edit Actions
        edit_menu.addAction("Redo", "Ctrl+Y", self.redo)
        edit_menu.addAction("Undo", "Ctrl+Z", self.undo)
        edit_menu.addSeparator()
        edit_menu.addAction("Cut", "Ctrl+X")
        edit_menu.addAction("Copy", "Ctrl+C")
        edit_menu.addAction("Paste", "Ctrl+V")
        edit_menu.addSeparator()
        edit_menu.addAction("Find", "Ctrl+F")
        
        theme_pallete = THEME_MANAGER.get()
        for bg in theme_pallete["theme"]:
            sub_menu = QMenu(bg.title(), self)
            
            for color in theme_pallete["color"]:
                sub_menu.addAction(color.title(), self._make_set_app_stylsheet(f"{bg}-{color}"))
            
            theme_menu.addMenu(sub_menu)
        
        help_menu.addAction("Welcome")
        help_menu.addSeparator()
        help_menu.addAction("Documentation")
        help_menu.addAction("View License")
        help_menu.addSeparator()
        help_menu.addAction("Check Updates")
        help_menu.addSeparator()
        help_menu.addAction("About")
    
    def _make_set_app_stylsheet(self, style):
        def func():
            THEME_MANAGER.apply_theme(self.app, style)
            self.save_data["theme"] = style
        
        return func
    
    def get_settings_info(self):
        setting_widgets: dict[str, SettingWidget] = {
            "subjectsInfo": self.subjects_widget,
            "teachersInfo": self.teachers_widget,
            "classesInfo": self.classes_widget,
            "timetableInfo": self.timetable_widget
        }
        
        return {
            widget_name: {
                "variables": widget.get(),
                "constants": getattr(widget, "get_constants", lambda: {})()
            }
            for widget_name, widget in
            setting_widgets.items()
        }
    
    def keyPressEvent(self, a0):
        focus_widget = self.focusWidget()
        
        if isinstance(focus_widget, QPushButton):
            focus_widget.click()
        
        return super().keyPressEvent(a0)
    
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



