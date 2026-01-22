from frontend.imports import *
from frontend.theme.theme import *

EXTENSION_NAME = "ttbl"


class Thread(QThread):
    crashed = pyqtSignal(Exception)
    
    def __init__(self, main_window: QMainWindow, func: Callable):
        super().__init__()
        self.setParent(None)
        
        self.main_window = main_window
        
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
            QMessageBox.critical(None, e.__class__.__name__, str(e))
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
            QMessageBox.critical("NotImplementedError", "This feature has not been implemented")
            # file_path = QFileDialog.getExistingDirectory(self.parent, "Batch Export Folder", "")
        else:
            raise Exception("Invalid Export Mode")
        
        if file_path:
            try:
                if self.export_callback:
                    self.export_callback(file_path, export_mode)
            except Exception as e:
                QMessageBox.critical(self.parent, type(e).__name__, str(e))



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
    
    def display_clashes(self):
        for teacher_id, day_mapping in self.school.getClashes().items():
            _, display_layout = self._make_new_widget(QHBoxLayout, self.main_layout)
            
            display_layout.addWidget(QLabel(self.school.teachers[teacher_id].name))
            _, days_display_layout = self._make_new_widget(QVBoxLayout, display_layout)
            
            for day, day_clash_sub_data in day_mapping.items():
                days_display_layout.addWidget(QLabel(day))
                _, main_clashes_layout = self._make_new_scrollable_widget(QVBoxLayout, days_display_layout)
                
                for period, s1, s2 in day_clash_sub_data:
                    main_clashes_layout.addWidget(QLabel(f"Period {period}"))
                    _, sub_clashes_layout = self._make_new_widget(QHBoxLayout, main_clashes_layout)
                    
                    _, clash_s1_layout = self._make_new_widget(QVBoxLayout, sub_clashes_layout)
                    clash_s1_layout.addWidget(QLabel(s1.cls.name))
                    clash_s1_layout.addWidget(QLabel(s1.name))
                    
                    _, clash_s2_layout = self._make_new_widget(QVBoxLayout, sub_clashes_layout)
                    clash_s2_layout.addWidget(QLabel(s2.cls.name))
                    clash_s2_layout.addWidget(QLabel(s2.name))
    
    def reset(self):
        for _ in range(len(self.main_layout.children())):
            widget = self.main_layout.children()[0]
            
            self.main_layout.removeWidget(widget)
            widget.deleteLater()
        
        self.display_clashes()
    
    def exec(self):
        self.reset()
        return super().exec()



# class ThreshDial(QWidget):
#     def __init__(self, parent=None, minimum:int=None, maximum:int=None, readonly=True, gradient_start_color=None, gradient_middle_color=None, gradient_end_color=None):
#         super().__init__(parent)
#         self.setMinimum(0 if minimum is None else minimum)
#         self.setMaximum(100 if maximum is None else maximum)
#         self.setNotchesVisible(True)
#         self.setWrapping(False)
        
#         if readonly:
#             self.setFocusPolicy(Qt.FocusPolicy.NoFocus)
#             self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        
#         self.setStyleSheet("""
#             QDial {
#                 background-color: """ + THEME_MANAGER.get_current_palette()["highlight"] + """;
#             }
#             QDial::groove {
#                 background: transparent;
#             }
#             QDial::handle {
#                 background-color: #00c896;
#                 border: 2px solid #00ffcc;
#                 width: 16px;
#                 height: 16px;
#                 border-radius: 8px;
#             }
#         """)
        
#         self.thresh_value = 0
        
#         self.gradient_start_color = gradient_start_color
#         self.gradient_middle_color = gradient_middle_color
#         self.gradient_end_color = gradient_end_color
    
#     def set_thresh_value(self, value: float | int):
#         self.thresh_value = value
    
    
#     def paintEvent(self, a0):
#         super().paintEvent(a0)
        
#         painter = QPainter(self)
#         painter.setRenderHint(QPainter.RenderHint.Antialiasing)

#         # Draw outer gradient ring *around* the dial
#         center = self.rect().center().toPointF()
#         radius = min(self.width(), self.height()) // 2 - 5
#         gradient = QConicalGradient(center, -90)
#         gradient.setColorAt(0.0, QColor("#15ff00") if self.gradient_start_color is None else QColor(self.gradient_start_color))
#         gradient.setColorAt(0.5, QColor("#c8c500") if self.gradient_middle_color is None else QColor(self.gradient_middle_color))
#         gradient.setColorAt(1.0, QColor("#ff0000") if self.gradient_end_color is None else QColor(self.gradient_end_color))
        
#         pen = painter.pen()
#         pen.setWidth(5)
#         pen.setBrush(gradient)
#         painter.setPen(pen)
        
#         painter.setBrush(Qt.BrushStyle.NoBrush)
#         painter.drawArc(
#             int(center.x() - radius),
#             int(center.y() - radius),
#             int(radius * 2),
#             int(radius * 2),
#             0 * 16,
#             360 * 16
#         )
        
#         thresh_indicator_radius = 2
        
#         pen = painter.pen()
#         pen.setWidth(5)
#         pen.setBrush(QColor(THEME_MANAGER.get_current_palette()["prefect"]))
#         painter.setPen(pen)
        
#         angle_offset = 30
#         max_turn = (360 - (angle_offset * 2))
#         angle = -(self.thresh_value - self.minimum()) * max_turn / (self.maximum() - self.minimum())
#         angle += 270 - angle_offset
#         angle = angle % 360
        
#         thresh_radius = radius - thresh_indicator_radius - 5
#         painter.drawLine()    
#         painter.drawEllipse(
#             int(center.x() + thresh_radius * math.cos(math.radians(angle))),
#             int(center.y() - thresh_radius * math.sin(math.radians(angle))),
#             int(thresh_indicator_radius * 2),
#             int(thresh_indicator_radius * 2)
#         )
    
#     # def paintEvent(self, a0):
#     #     super().paintEvent(a0)
        
#     #     painter = QPainter(self)
#     #     painter.setRenderHint(QPainter.RenderHint.Antialiasing)

#     #     # Draw outer gradient ring *around* the dial
#     #     center = self.rect().center().toPointF()
#     #     radius = min(self.width(), self.height()) // 2 - 5
#     #     gradient = QConicalGradient(center, -90)
#     #     gradient.setColorAt(0.0, QColor("#15ff00") if self.gradient_start_color is None else QColor(self.gradient_start_color))
#     #     gradient.setColorAt(0.5, QColor("#c8c500") if self.gradient_middle_color is None else QColor(self.gradient_middle_color))
#     #     gradient.setColorAt(1.0, QColor("#ff0000") if self.gradient_end_color is None else QColor(self.gradient_end_color))
        
#     #     pen = painter.pen()
#     #     pen.setWidth(5)
#     #     pen.setBrush(gradient)
#     #     painter.setPen(pen)
        
#     #     painter.setBrush(Qt.BrushStyle.NoBrush)
#     #     painter.drawArc(
#     #         int(center.x() - radius),
#     #         int(center.y() - radius),
#     #         int(radius * 2),
#     #         int(radius * 2),
#     #         0 * 16,
#     #         360 * 16
#     #     )
        
#     #     thresh_indicator_radius = 2
        
#     #     pen = painter.pen()
#     #     pen.setWidth(5)
#     #     pen.setBrush(QColor(THEME_MANAGER.get_current_palette()["prefect"]))
#     #     painter.setPen(pen)
        
#     #     angle_offset = 30
#     #     max_turn = (360 - (angle_offset * 2))
#     #     angle = -(self.thresh_value - self.minimum()) * max_turn / (self.maximum() - self.minimum())
#     #     angle += 270 - angle_offset
#     #     angle = angle % 360
        
#     #     thresh_radius = radius - thresh_indicator_radius - 5
        
#     #     painter.drawEllipse(
#     #         int(center.x() + thresh_radius * math.cos(math.radians(angle))),
#     #         int(center.y() - thresh_radius * math.sin(math.radians(angle))),
#     #         int(thresh_indicator_radius * 2),
#     #         int(thresh_indicator_radius * 2)
#     #     )

