from frontend.imports import *


EXTENSION_NAME = "ttbl"


def gzip_file(input_file_path: str):
    try:
        with gzip.open(input_file_path, "rb") as file:
            json.load(file)
        
        return input_file_path, None
    except Exception as e:
        output_file_path = input_file_path + "." + (f"converted.{EXTENSION_NAME}" if input_file_path.endswith("." + EXTENSION_NAME) else EXTENSION_NAME)
    
    with open(input_file_path, 'rb') as f_in:
        with gzip.open(output_file_path, 'wb') as f_out:
            shutil.copyfileobj(f_in, f_out)
    
    return output_file_path, input_file_path


class Thread(QThread):
    crashed = pyqtSignal(Exception)
    
    def __init__(self, main_window: QMainWindow, func: Callable):
        super().__init__()
        self.setParent(None)
        
        self.func = func is not None and func or (lambda: ())
        main_window.close = self._window_closed()
    
    def _window_closed(self):
        def window_closed_event(self):
            self.exit(0)
            super().close()
        
        return window_closed_event
    
    def run(self):
        try:
            self.func()
        except Exception as e:
            self.crashed.emit(e)
            self.exit(-1)



class FileManager:
    def __init__(self, parent: QWidget, path: Optional[str], file_filter="Text Files (*.txt);;All Files (*)"):
        self.path = path
        self.parent = parent
        self.file_filter = file_filter
        self._from_save = False
        
        # Hooks: user-defined callbacks for file read/write
        self.save_callback: Optional[Callable[[str | None], str]] = None
        self.open_callback: Optional[Callable[[], None] | Callable[[str, Any], None]] = None
        self.load_callback: Optional[Callable[[str], Any]] = None

    def set_callbacks(self, save: Callable[[str | None], None], open_: Callable[[], None] | Callable[[str, Any], None], load: Callable[[str], Any], export: Callable[[str, int], None]):
        self.save_callback = save
        self.open_callback = open_
        self.load_callback = load
        self.export_callback = export
    
    def get_data(self):
        if self.path:
            return self.load_callback(self.path)
    
    def new(self):
        if self.open_callback:
            self.open_callback()
    
    def open(self):
        file_path, _ = QFileDialog.getOpenFileName(self.parent, "Open File", "", self.file_filter)
        if file_path:
            try:
                if self.open_callback:
                    self.open_callback(file_path)
            except Exception as e:
                QMessageBox.critical(self.parent, type(e).__name__, str(e))

    def save(self):
        if self.path:
            # try:
                if self.save_callback:
                    self.save_callback(self.path)
            # except Exception as e:
            #     QMessageBox.critical(self.parent, type(e).__name__, str(e))
        else:
            self._from_save = True
            self.save_as()

    def save_as(self):
        file_path, _ = QFileDialog.getSaveFileName(self.parent, ("Save File" if self._from_save else "Save File As"), "", self.file_filter)
        
        if file_path:
            try:
                if self.save_callback:
                    self.path = file_path
                    self.save_callback(self.path)
            except Exception as e:
                QMessageBox.critical(self.parent, type(e).__name__, str(e))
        
        if self._from_save:
            self._from_save = False

    def export(self, export_mode: int, file_filter: str):
        if export_mode == 0:
            file_path, _ = QFileDialog.getSaveFileName(self.parent, "Export File", "", file_filter)
        elif export_mode == 1:
            file_path = QFileDialog.getExistingDirectory(self.parent, "Batch Export Folder", "")
        else:
            raise Exception("Invalid Export Mode")
        
        if file_path:
            try:
                if self.export_callback:
                    self.export_callback(file_path, export_mode)
            except Exception as e:
                QMessageBox.critical(self.parent, type(e).__name__, str(e))


class CustomTitleBar(QWidget):
    def __init__(self, parent: QWidget, get_search_data: Callable[[], dict | list | set | tuple | str | int]):
        super().__init__(parent)
        self.master = parent
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        self.get_search_data = get_search_data
        
        self.container = QWidget()
        self.mian_layout = QHBoxLayout()
        self.container.setFixedHeight(40)
        self.container.setProperty("class", "TitleBar")
        self.container.setLayout(self.mian_layout)
        self.mian_layout.setContentsMargins(0, 0, 0, 0)
        self.mian_layout.setSpacing(0)
        
        layout.addWidget(self.container)
        
        left_widget = QWidget()
        self.left_layout = QHBoxLayout()
        left_widget.setProperty("class", "TitleBar")
        left_widget.setLayout(self.left_layout)
        self.left_layout.setContentsMargins(0, 0, 60, 0)
        self.left_layout.setSpacing(0)
        
        center_widget = QWidget()
        self.center_layout = QHBoxLayout()
        center_widget.setProperty("class", "TitleBar")
        center_widget.setLayout(self.center_layout)
        self.center_layout.setContentsMargins(60, 5, 60, 5)
        
        right_widget = QWidget()
        self.right_layout = QHBoxLayout()
        right_widget.setProperty("class", "TitleBar")
        right_widget.setLayout(self.right_layout)
        self.right_layout.setContentsMargins(60, 0, 0, 0)
        self.right_layout.setSpacing(0)
        
        # Center widget
        self.set_search_visible_button = QPushButton("Search")
        self.set_search_visible_button.setFixedHeight(30)
        self.set_search_visible_button.setStyleSheet("min-width: 600px; min-height: 30px; border-radius: 10px; padding: 0px;")
        self.set_search_visible_button.clicked.connect(self._toggle_search)
        
        self.search_edit = QLineEdit("Search file by name")
        self.search_edit.setFixedHeight(30)
        self.search_edit.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.search_edit.textChanged.connect(self._search)
        self.search_edit.setVisible(False)
        
        self.center_layout.addWidget(self.set_search_visible_button)
        self.center_layout.addWidget(self.search_edit)
        
        # # Right widget
        # # Minimize Button
        # btn_min = QPushButton("—")
        # btn_min.setProperty("class", "FileMinumum")
        # btn_min.clicked.connect(self.master.showMinimized)
        # self.right_layout.addWidget(btn_min)
        
        # # Maximize/Restore Button
        # btn_max = QPushButton("□")
        # btn_max.setProperty("class", "FileMaximum")
        # btn_max.clicked.connect(self.toggle_max_restore)
        # self.right_layout.addWidget(btn_max)
        
        # # Close Button
        # btn_close = QPushButton("✕")
        # btn_close.setProperty("class", "FileClose")
        # btn_close.clicked.connect(self.master.close)
        # self.right_layout.addWidget(btn_close)
        
        # self._maximized = True
        
        # self._drag_pos = QPoint()
        
        self.mian_layout.addWidget(left_widget, alignment=Qt.AlignmentFlag.AlignLeft)
        self.mian_layout.addWidget(center_widget)
        self.mian_layout.addWidget(right_widget, alignment=Qt.AlignmentFlag.AlignRight)
    
    # def toggle_max_restore(self):
    #     if self._maximized:
    #         self.master.showNormal()
    #     else:
    #         self.master.showMaximized()
    #     self._maximized = not self._maximized
    
    def _toggle_search(self):
        self.set_search_visible_button.setVisible(not self.set_search_visible_button.isVisible())
        self.search_edit.setVisible(not self.search_edit.isVisible())
        
        if self.search_edit.isVisible():
            self.search_edit.setFocus()
        else:
            self.setFocus()
    
    def _search_compare(self, text: str, search_text: str):
        compared_indices = []
        
        search_text_index = -1
        index = 0
        
        for c in text:
            index = search_text[index + 1:].find(c)
            
            if index == -1:
                return
            
            search_text_index += index + 1
            
            compared_indices.append(search_text_index)
        
        return compared_indices
    
    def _search(self, text: str, search_scope: dict | list | set | tuple | str | int | None = None):
        search_scope = search_scope if search_scope is not None else self.get_search_data()
        
        data = None
        
        if isinstance(search_scope, dict):
            data = {}
            
            for key, value in search_scope.items():
                s_key = self._search(text, key)
                s_value = self._search(text, value)
                
                if (s_key, s_value).count(None) < 2:
                    data[s_key] = s_value
            
            if not data:
                data = None
        elif isinstance(search_scope, (list, tuple, set)):
            data = []
            
            for value in search_scope:
                s_value = self._search(text, value)
                
                if s_value is not None:
                    data.append(s_value)
            
            if not data:
                data = None
        elif isinstance(search_scope, str):
            data = search_scope, self._search_compare(text, search_scope)
        elif isinstance(search_scope, int):
            data = str(search_scope), self._search_compare(text, str(search_scope))
        
        return data
    
    # # Enable window dragging
    # def mousePressEvent(self, event):
    #     if event.button() == Qt.MouseButton.LeftButton:
    #         self._drag_pos = event.globalPosition().toPoint()
    
    # def mouseDoubleClickEvent(self, _):
    #     self.toggle_max_restore()
    
    # def mouseMoveEvent(self, event):
    #     if event.buttons() == Qt.MouseButton.LeftButton:
    #         delta = event.globalPosition().toPoint() - self._drag_pos
            
    #         if delta and self._maximized:
    #             self.toggle_max_restore()
                
    #             mouse_point = event.globalPosition().toPoint()
                
    #             mouse_x_index = mouse_point.x() / self.window().width()
    #             mouse_y_index = mouse_point.y() / self.window().height()
                
    #             point_offset = QPoint(int(self.master.width() * mouse_x_index), int(self.master.height() * mouse_y_index))
                
    #             self.master.move(point_offset - QPoint(int(self.window().width() * 0.5), int(40 * 0.5)))
            
    #         if not self._maximized:
    #             self.master.move(self.master.pos() + delta)
    #             self._drag_pos = event.globalPosition().toPoint()


class MainTitleBar(CustomTitleBar):
    def __init__(self, parent, menu_bar: QMenuBar, go_back_func: Callable, go_forward_func: Callable):
        super().__init__(parent, lambda: {})
        
        menu_bar.setFixedHeight(40)
        menu_bar.setStyleSheet("QMenuBar {background-color: transparent; border: none;}")
        self.left_layout.addWidget(menu_bar)
        
        self.go_back_button = QPushButton("<")
        self.go_forward_button = QPushButton(">")
        
        self.go_back_button.setProperty("class", "GoButton")
        self.go_forward_button.setProperty("class", "GoButton")
        
        self.go_back_button.clicked.connect(go_back_func)
        self.go_forward_button.clicked.connect(go_forward_func)
        
        self.center_layout.insertWidget(0, self.go_back_button)
        self.center_layout.insertWidget(1, self.go_forward_button)


class ClashesViewer(QDialog):
    def __init__(self, school: School):
        super().__init__()
        self.setWindowTitle("Clash Viewer")
        
        layout = QVBoxLayout(self)
        
        self.container, self.main_layout = self._make_new_scrollable_widget(QVBoxLayout, layout)
        
        self.container.setProperty("class", "ClashesViewer")
        
        self.main_layout.setContentsMargins(10, 20, 20, 5)
        self.main_layout.setSpacing(30)
        
        self.school = school
        self.clashes: dict[str, list[tuple[tuple[Subject, Class], tuple[Subject, Class]]]] = {}
    
    def _make_new_widget(self, layout_type: type[QHBoxLayout] | type[QVBoxLayout], parent_layout: QHBoxLayout | QVBoxLayout | None = None):
        widget = QWidget()
        layout = layout_type()
        widget.setLayout(layout)
        
        if parent_layout is not None:
            parent_layout.addWidget(widget)
        
        return widget, layout
    
    def _make_new_scrollable_widget(self, layout_type: type[QHBoxLayout] | type[QVBoxLayout], parent_layout: QHBoxLayout | QVBoxLayout | None = None):
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        
        widget = QWidget()
        layout = layout_type()
        
        widget.setLayout(layout)
        
        scroll_area.setWidget(widget)
        
        if parent_layout is not None:
            parent_layout.addWidget(scroll_area)
        
        return widget, layout
    
    def update_clashes(self):
        for cls in self.school.schoolDict:
            for subject in cls.subjects:
                clashes = self.school.findClashes(subject)
                
                for clash_subject, clash_cls in clashes:
                    if clash_subject.teacher.id not in self.clashes:
                        self.clashes[clash_subject.teacher.id] = []
                    
                    self.clashes[clash_subject.teacher.id].append(((subject, cls), (clash_subject, clash_cls)))
    
    def display_clashes(self):
        for teacher_id, clash_data in self.clashes.items():
            _, display_layout = self._make_new_widget(QHBoxLayout, self.main_layout)
            
            display_layout.addWidget(QLabel(self.school.teachers[teacher_id].name))
            _, clash_display_layout = self._make_new_scrollable_widget(QHBoxLayout, display_layout)
            
            for (subject, cls), (clash_subject, clash_cls) in clash_data:
                _, main_clash_layout = self._make_new_widget(QHBoxLayout, clash_display_layout)
                
                _, subject_layout = self._make_new_widget(QVBoxLayout, main_clash_layout)
                _, subject_clash_layout = self._make_new_widget(QVBoxLayout, main_clash_layout)
                
                subject_layout.addWidget(QLabel(f"<span style: 'font-weight: 100;'>{cls.name}</span>"))
                subject_layout.addWidget(QLabel(f"<b>{subject.name}</b>"))
                
                subject_clash_layout.addWidget(QLabel(f"<span style: 'font-weight: 100;'>{clash_cls.name}</span>"))
                subject_clash_layout.addWidget(QLabel(f"<b>{clash_subject.name}</b>"))
    
    def reset(self):
        self.clashes = {}
        
        for _ in range(len(self.main_layout.children())):
            widget = self.main_layout.children()[0]
            
            self.main_layout.removeWidget(widget)
            widget.deleteLater()
        
        self.update_clashes()
        self.display_clashes()
    
    def exec(self):
        self.reset()
        return super().exec()


