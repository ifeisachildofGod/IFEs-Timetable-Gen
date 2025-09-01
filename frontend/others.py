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
        file_path, _ = QFileDialog.getSaveFileName(self.parent, ("Save File" if self._from_save else "Save File As"), "", file_filter)
        
        if file_path:
            try:
                if self.export_callback:
                    self.export_callback(file_path, export_mode)
            except Exception as e:
                QMessageBox.critical(self.parent, type(e).__name__, str(e))


class CustomTitleBar(QWidget):
    def __init__(self, parent: QWidget):
        super().__init__(parent)
        self.master = parent
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        self.container = QWidget()
        self.mian_layout = QHBoxLayout()
        self.container.setFixedHeight(30)
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
        self.center_layout.setContentsMargins(60, 0, 60, 0)
        
        right_widget = QWidget()
        self.right_layout = QHBoxLayout()
        right_widget.setProperty("class", "TitleBar")
        right_widget.setLayout(self.right_layout)
        self.right_layout.setContentsMargins(60, 0, 0, 0)
        self.right_layout.setSpacing(0)

        # Center widget
        self.search_edit = QLineEdit("Search")
        self.search_edit.setFixedHeight(30)
        self.search_edit.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.center_layout.addWidget(self.search_edit)
        
        # Right widget
        # Minimize Button
        btn_min = QPushButton("—")
        btn_min.setProperty("class", "FileMinumum")
        btn_min.clicked.connect(self.master.showMinimized)
        self.right_layout.addWidget(btn_min)
        
        # Maximize/Restore Button
        btn_max = QPushButton("□")
        btn_max.setProperty("class", "FileMaximum")
        btn_max.clicked.connect(self.toggle_max_restore)
        self.right_layout.addWidget(btn_max)
        
        # Close Button
        btn_close = QPushButton("✕")
        btn_close.setProperty("class", "FileClose")
        btn_close.clicked.connect(self.master.close)
        self.right_layout.addWidget(btn_close)
        
        self._maximized = True
        
        self.mian_layout.addWidget(left_widget, alignment=Qt.AlignmentFlag.AlignLeft)
        self.mian_layout.addWidget(center_widget)
        self.mian_layout.addWidget(right_widget, alignment=Qt.AlignmentFlag.AlignRight)
        
        self._drag_pos = QPoint()
    
    def toggle_max_restore(self):
        if self._maximized:
            self.master.showNormal()
        else:
            self.master.showMaximized()
        self._maximized = not self._maximized

    # Enable window dragging
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_pos = event.globalPosition().toPoint()
    
    def mouseDoubleClickEvent(self, _):
        self.toggle_max_restore()
    
    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.MouseButton.LeftButton:
            delta = event.globalPosition().toPoint() - self._drag_pos
            
            if delta and self._maximized:
                self.toggle_max_restore()
                
                mouse_point = event.globalPosition().toPoint()
                
                mouse_x_index = mouse_point.x() / self.window().width()
                mouse_y_index = mouse_point.y() / self.window().height()
                
                point_offset = QPoint(int(self.master.width() * mouse_x_index), int(self.master.height() * mouse_y_index))
                
                self.master.move(point_offset - QPoint(int(self.window().minimumWidth() * mouse_x_index), int(self.window().minimumHeight() * mouse_y_index)))
            
            if not self._maximized:
                self.master.move(self.master.pos() + delta)
                self._drag_pos = event.globalPosition().toPoint()


class MainTitleBar(CustomTitleBar):
    def __init__(self, parent, menu_bar: QMenuBar, go_back_func: Callable, go_forward_func: Callable):
        super().__init__(parent)
        
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





