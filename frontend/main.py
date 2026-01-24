from frontend.imports import *

from frontend.setting_widgets import *
from frontend.editing_widgets import TimeTableEditor

from openpyxl import Workbook

class Window(QMainWindow):
    saved_state_changed = pyqtSignal()
    
    def __init__(self, app: QApplication, arguments: list[str]):
        super().__init__()
        path = len(arguments) > 1 and arguments[1] or None
        
        self.app = app
        self.title = "IFEs Timetable Generator"
        self.export_file_filter = "JSON File (*.json);;Image File (*.png *.jpg *.wpeg *.svg);;Microsoft Document (*.msix);;Excel Document (*.xlsx);;Pickle File (*.pickle);;CSV File (*.csv);;HTML File (*.html);;PDF File (*.pdf)"
        
        self.file = FileManager(self, path, f"Timetable Files (*.{EXTENSION_NAME})")
        self.file.set_callbacks(self.save_callback, self.open_callback, self.load_callback, self.export_callback)
        
        # Default data
        self.default_per_day      =   2   # Being used by the classes editor
        self.default_per_week     =   4   #   "     "   "  "     "       "
        self.default_max_classes  =   3   # Being used by the teachers editor
        self.default_save_data    =   {
            "levels": [],
            "subjectTeacherMapping": {},
            "timetableInfo": {
                "breakPeriod": 7,
                "periodAmount": 10,
                "DOTW": [("ID:monday3231", "Monday"), ("ID:tuesday6456", "Tuesday"), ("ID:wednesday0921", "Wednesday"), ("ID:thursday9182", "Thursday"), ("ID:friday8765", "Friday"), None, ("ID:saturday8728", "Saturday"), ("ID:sunday0091", "Sunday")],
                "levelTimetableData": []
            },
        }
        
        self.children_saved_tracker = {}
        
        # Setting resize geometry
        self.setGeometry(100, 100, 1000, 700)
        
        # Get saved data
        self._init_save_data()
        self.saved_state_changed.connect(self.unsaved_callback)
        
        # Initialize school data
        self.school = School(self.save_data)
        self.school.setSchoolInfoFromProjectDict()
        self.school.setTimetableFromProjectDict()
        
        # Misc
        self.display_index = 0
        self.prev_display_index = 0
        
        self.go_focus_index = 0
        self.view_tracker = [0]
        
        menu_bar = self.create_menu_bar()
        
        # Make settings widgets
        self.subjects_widget = Subjects(self, self.save_data.get("subjectsInfo"), self.saved_state_changed)
        self.classes_widget = Classes(self, self.save_data.get("classesInfo"), self.saved_state_changed)
        self.teachers_widget = Teachers(self, self.save_data.get("teachersInfo"), self.saved_state_changed)
        
        self.timetable_widget = TimeTableEditor(self, self.school, self.save_data.get("timetableInfo"), self.saved_state_changed)
        
        # Create viewing container
        main_container = QWidget()
        main_container_layout = QVBoxLayout()
        main_container_layout.setContentsMargins(0, 0, 5, 5)
        main_container.setLayout(main_container_layout)
        
        self.title_bar = MainTitleBar(self, menu_bar, self.subjects_widget, self.go_back, self.go_forward)
        main_container_layout.addWidget(self.title_bar)
        
        # Create viewing container
        viewing_container = QWidget()
        viewing_container_layout = QHBoxLayout()
        viewing_container_layout.setContentsMargins(0, 10, 5, 5)
        viewing_container.setLayout(viewing_container_layout)
        main_container_layout.addWidget(viewing_container)
        
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
        self.option_buttons = [subjects_btn, teachers_btn, classes_btn, timetable_btn]
        
        self.stack.addWidget(self.subjects_widget)
        self.stack.addWidget(self.teachers_widget)
        self.stack.addWidget(self.classes_widget)
        self.stack.addWidget(self.timetable_widget)
        
        # Connect buttons
        for index, button in enumerate(self.option_buttons):
            button.setCheckable(True)
            button.clicked.connect(self.make_option_button_func(index))
            sub_sidebar_layout.addWidget(button)
        
        sub_sidebar_layout.insertStretch(3)
        
        # Add sub sidebar widgets to main sidebar layout
        main_sidebar_layout.addWidget(self.sub_sidebar_widget)
        # main_sidebar_layout.addWidget(self.toggle_sidebar_button)
        
        # Add widgets to main layout
        viewing_container_layout.addWidget(main_sidebar_widget)
        viewing_container_layout.addWidget(self.stack)
        
        self.setCentralWidget(main_container)
        subjects_btn.click()  # Start with subjects page selected
        
        self.orig_data = deepcopy(self.save_data)
                
        self.go_back_action.setDisabled(True)
        self.title_bar.go_back_button.setDisabled(True)
        
        self.go_forward_action.setDisabled(True)
        self.title_bar.go_forward_button.setDisabled(True)
        
        if path is not None:
            self.saved_callback()
    
    def _init_save_data(self):
        self.saved = True
        self.save_data = deepcopy(self.default_save_data)
        self.orig_data = deepcopy(self.save_data)
        
        if self.file.path is not None:
            self.save_data = self.file.get_data()
            
            self.saved_callback()
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
        
        if self.file.path is not None:
            self.setWindowTitle(f"{self.title} - {Path(self.file.path).absolute().as_posix()} *Unsaved")
        else:
            self.setWindowTitle(self.title)
    
    def saved_callback(self):
        self.saved = True
        self.setWindowTitle(f"{self.title} - {Path(self.file.path).absolute().as_posix()}")
    
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
        self.file.path = path
        
        self.update_interaction(self.display_index, self.prev_display_index)
        
        self.save_data.update(self.get_settings_info())
        
        with gzip.open(self.file.path, "wb") as file:
            file.write(json.dumps(self.save_data, indent=2).encode())
        
        self.orig_data = deepcopy(self.save_data)
        
        self.saved_callback()
    
    def export_callback(self, path: str, export_mode: int):
        saved = self.saved
        
        self.update_interaction(self.prev_display_index, self.display_index)
        self.update_interaction(self.display_index, 3)
        
        if export_mode == 0:
            if path.endswith(("png", "jpg", "wpeg", "svg", "pdf", "html", "msix", "xlsx")):
                title = "Timetable"
                
                widgets = list(self.timetable_widget.timetable_widgets.values())
                
                widget = self.timetable_widget.exportify_widgets(widgets)
                
                widget.resize(QSize(max(w.columnCount() for w in widgets) * 90 + 114, widget.sizeHint().height()))
                
                if path.endswith("pdf"):
                    printer = QPrinter(QPrinter.PrinterMode.HighResolution)
                    printer.setOutputFormat(QPrinter.OutputFormat.PdfFormat)
                    printer.setOutputFileName(path)
                    
                    painter = QPainter(printer)
                    widget.render(painter)
                    painter.end()
                elif path.endswith("html"):
                    style = """
                    body {
                        font-family: Arial, sans-serif;
                        padding: 20px;
                        background: #f9f9f9;
                    }

                    h2 {
                        text-align: left;
                        margin-bottom: 20px;
                    }

                    .timetable {
                        display: grid;
                        grid-template-columns: 100px repeat(5, 1fr);
                        border: 1px solid #ccc;
                        margin-bottom: 100px;
                    }

                    .cell {
                        border: 1px solid #ccc;
                        padding: 15px;
                        text-align: center;
                    }

                    .header {
                        background: black;
                        color: white;
                        font-weight: bold;
                    }
                    
                    .break {
                        background: #1f1f1f;
                        color: #1f1f1f;
                    }
                    """
                    
                    body = ""
                    for cls_ttbl in widgets:
                        ttbl_text = f'<div class="cell"></div>'
                        
                        for col in range(cls_ttbl.columnCount()):
                            ttbl_text += f'<div class="cell header">{cls_ttbl.horizontalHeaderItem(col).text()}</div>'
                        
                        for row in range(cls_ttbl.rowCount()):
                            ttbl_text += f'<div class="cell header">{cls_ttbl.verticalHeaderItem(row).text()}</div>'
                            for col in range(cls_ttbl.columnCount()):
                                item: TimeTableItem = cls_ttbl.item(row, col)
                                
                                ttbl_text += (
                                    f'<div class="cell break"></div>'
                                    if item.break_time else
                                    (
                                        f'<div class="cell"></div>'
                                        if item.free_period else
                                        f'<div class="cell">{item.subject.name}</div>'
                                    )
                                )
                        
                        body += f"""
                        <h2>{cls_ttbl.cls.name}</h2>
                        <div class="timetable">
                            {ttbl_text}
                        </div>
                        """
                    
                    html = f"""
                    <!DOCTYPE html>
                    <html lang="en">
                    <head>
                        <meta charset="UTF-8">
                        <meta name="viewport" content="width=device-width, initial-scale=1.0">
                        <title>{title}</title>
                        <style>
                            {style}
                        </style>
                    </head>
                        <body>
                            {body}
                        </body>
                    </html>
                    """
                    
                    with open(path, "w") as file:
                        file.write(html)
                elif path.endswith("msix"):
                    doc = Document()
                    
                    doc.add_heading(title, level=1)
                    
                    for cls_ttbl in widgets:
                        doc.add_heading(cls_ttbl.cls.name, level=2)
                        
                        # Create a Word table
                        word_table = doc.add_table(cls_ttbl.rowCount() + 1, cls_ttbl.columnCount() + 1)
                        word_table.style = "Table Grid"
                        
                        for row in range(cls_ttbl.rowCount()):
                            word_table.cell(1, row).text = cls_ttbl.verticalHeaderItem(row).text()
                        for col in range(cls_ttbl.columnCount()):
                            word_table.cell(col, 1).text = cls_ttbl.horizontalHeaderItem(col).text()
                        
                        for row in range(1, cls_ttbl.rowCount() + 1):
                            for col in range(1, cls_ttbl.columnCount() + 1):
                                item: TimeTableItem = cls_ttbl.item(row - 1, col - 1)
                                word_table.cell(row, col).text = ("BREAK" if item and item.break_time else "") if not item or item.break_time or item.free_period else item.text()
                    
                    doc.save(path)
                elif path.endswith("xlsx"):
                    wb = Workbook()
                    ws = wb.active
                    ws.title = title
                    
                    for cls_ttbl in widgets:
                        # Add header row
                        ws.append(["" for _ in range(cls_ttbl.columnCount() + 1)])
                        
                        headers = ["", ""] + [cls_ttbl.horizontalHeaderItem(col).text() for col in range(cls_ttbl.columnCount())]
                        ws.append(headers)
                        
                        for row in range(cls_ttbl.rowCount()):
                            row_data = [cls_ttbl.verticalHeaderItem(row).text()]
                            for col in range(cls_ttbl.columnCount()):
                                item = cls_ttbl.item(row, col)
                                
                                row_data.append(("BREAK" if item and item.break_time else "") if not item or item.break_time or item.free_period else item.text())
                            ws.append(row_data)
                    
                    wb.save(path)
                else:
                    pixmap = QPixmap(widget.size())
                    widget.render(pixmap)
                    pixmap.save(path)
            elif path.endswith("json"):
                with open(path, "w") as file:
                    json.dump(self.save_data, file, indent=2)
            elif path.endswith("pickle"):
                with open(path, "wb") as file:
                    pickle.dump(self.save_data, file)
        elif export_mode == 1:
            pass
        
        if saved:
            self.saved_callback()
        else:
            self.unsaved_callback()
    
    def undo(self):
        undo_func = self.focusWidget().__dict__.get("undo")
        if undo_func is not None:
            undo_func()
    
    def redo(self):
        redo_func = self.focusWidget().__dict__.get("redo")
        if redo_func is not None:
            redo_func()
    
    def go_back(self):
        if self.go_focus_index > 0:
            self.go_focus_index -= 1
            
            self.go_forward_action.setDisabled(False)
            self.title_bar.go_forward_button.setDisabled(False)
            
            self.option_button_func(self.view_tracker[self.go_focus_index])
        
        if self.go_focus_index == 0:
            self.go_back_action.setDisabled(True)
            self.title_bar.go_back_button.setDisabled(True)
    
    def go_forward(self):
        if self.go_focus_index < len(self.view_tracker) - 1:
            self.go_focus_index += 1
            
            self.go_back_action.setDisabled(False)
            self.title_bar.go_back_button.setDisabled(False)
            
            self.option_button_func(self.view_tracker[self.go_focus_index])
        
        if self.go_focus_index == len(self.view_tracker) - 1:
            self.go_forward_action.setDisabled(True)
            self.title_bar.go_forward_button.setDisabled(True)
    
    def create_menu_bar(self):
        menubar = QMenuBar()
        
        # File Menu
        file_menu = menubar.addMenu("File")
        edit_menu = menubar.addMenu("Edit")
        go_menu = menubar.addMenu("Go")
        theme_menu = menubar.addMenu("Theme")
        help_menu = menubar.addMenu("Help")
        
        # Export Menu
        export_menu = QMenu("Export", self)
        
        export_menu.addAction("Single", lambda: self.file.export(0, self.export_file_filter))
        export_menu.addAction("Batch", lambda: self.file.export(1, self.export_file_filter))
        
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
        
        self.go_back_action = go_menu.addAction("Back", self.go_back)
        self.go_forward_action = go_menu.addAction("Forward", self.go_forward)
        go_menu.addSeparator()
        go_menu.addAction("Go to ID")
        go_menu.addSeparator()
        go_menu.addAction("Go to Subject")
        go_menu.addAction("Go to Teacher")
        go_menu.addAction("Go to Class")
        
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
        
        return menubar
    
    def _make_set_app_stylsheet(self, style):
        def func():
            THEME_MANAGER.apply_theme(self.app, style)
            self.save_data["theme"] = style
        
        return func
    
    def get_settings_info(self):
        setting_widgets: dict[str, BaseSettingWidget] = {
            "subjectsInfo": self.subjects_widget,
            "teachersInfo": self.teachers_widget,
            "classesInfo": self.classes_widget
        }
        
        data = {
            widget_name: {
                "variables": widget.get(),
                "constants": getattr(widget, "get_constants", lambda: {})()
            }
            for widget_name, widget in
            setting_widgets.items()
        }
        
        data.update({"timetableInfo": self.timetable_widget.get()})
        
        return data
    
    def keyPressEvent(self, a0):
        if a0.key() == 16777220: # type: ignore
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
            if self.display_index != index:
                self.view_tracker[self.go_focus_index + 1:] = []
                self.go_focus_index += 1
                
                self.view_tracker.append(index)
                
                self.go_back_action.setDisabled(False)
                self.title_bar.go_back_button.setDisabled(False)
                
                self.go_forward_action.setDisabled(True)
                self.title_bar.go_forward_button.setDisabled(True)
            
            self.option_button_func(index)
        
        return func
    
    def option_button_func(self, index: int):
        for i, btn in enumerate(self.option_buttons):
            btn.setChecked(i == index)
        
        if self.display_index != index:
            self.stack.setCurrentIndex(index)
            self.update_interaction(self.display_index, index)
            self.prev_display_index = self.display_index
            self.display_index = index
    
    def update_interaction(self, prev_index: int, curr_index: int):
        match curr_index:
            case 0:  # Subjects view
                self.subjects_widget.update_data_interaction(prev_index, curr_index)
                self.teachers_widget.update_data_interaction(prev_index, curr_index)
                self.classes_widget.update_data_interaction(prev_index, curr_index)
                self.timetable_widget.update_data_interaction(prev_index, curr_index)
            case 1:  # Teachers view
                self.teachers_widget.update_data_interaction(prev_index, curr_index)
                self.subjects_widget.update_data_interaction(prev_index, curr_index)
                self.classes_widget.update_data_interaction(prev_index, curr_index)
                self.timetable_widget.update_data_interaction(prev_index, curr_index)
            case 2:  # Classes view
                self.classes_widget.update_data_interaction(prev_index, curr_index)
                self.subjects_widget.update_data_interaction(prev_index, curr_index)
                self.teachers_widget.update_data_interaction(prev_index, curr_index)
                self.timetable_widget.update_data_interaction(prev_index, curr_index)
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
                self.timetable_widget.update_data_interaction(prev_index, curr_index)



