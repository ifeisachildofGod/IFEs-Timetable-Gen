from frontend.imports import *
from frontend.others import *
from frontend.theme.theme import THEME_MANAGER



BaseWidgetInfoType = Union[
    list[tuple[str, str]],
    dict[str, dict[str, dict[str, dict[str, str | bool]]] | dict[int, str]],
    dict[str, dict[str, str | dict[str, list[str] | dict[int, str]]] | dict[int, str] | dict[str, list[str]]],
    dict[str, str],
    dict[str, list[str] | dict[int, str]]
]
class BaseSubWidget(QDialog):
    def __init__(self, title: str, info: BaseWidgetInfoType, saved_state_changed: pyqtBoundSignal):
        super().__init__()
        self.info = info
        
        self.setWindowTitle(title)
        
        self.saved_state_changed = saved_state_changed
        
        self.container = QWidget()
        self.container_layout = QVBoxLayout()
        self.container.setLayout(self.container_layout)
        
        self.main_layout = QVBoxLayout()
        self.setLayout(self.main_layout)
    
    def get(self):
        return self.info
    
    def find(self, _id: str):
        pass



class BaseSettingWidget(QWidget):
    def __init__(self, main_window: QMainWindow, name: str, input_placeholders: list[tuple[str, int]], saved_state_changed: pyqtBoundSignal, data: dict | None = None):
        super().__init__()
        self.main_window = main_window
        
        self.objectNameChanged.connect(lambda: self.add_button.setText(f"Add {self.objectName().title()}"))
        
        self.display_data_max = 8
        self.font_metrics = QFontMetrics(self.font())
        
        self.info = {}
        self.widgets: dict[str, QWidget] = {}
        self.display_data_widgets: dict[str, dict[str, QWidget]] = {}
        self.sub_display_data_widgets: dict[str, dict[str, list[QWidget]]] = {}
        self._temp_popups: dict = {}
        self.input_placeholders = input_placeholders
        self.saved_state_changed = saved_state_changed
        
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setSpacing(10)
        self.main_layout.setContentsMargins(0, 0, 10, 10)
        
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        
        self.container = QWidget()
        self.container.setContentsMargins(20, 10, 20, 10)
        
        self.container_layout = QVBoxLayout(self.container)
        self.container_layout.setSpacing(20)
        self.scroll_area.setWidget(self.container)
        
        def add_func():
            self.add(self.input_placeholders)
            self.saved_state_changed.emit()
        
        self.add_button = QPushButton()
        self.add_button.clicked.connect(add_func)
        
        self.main_layout.addWidget(self.scroll_area)
        self.main_layout.addWidget(self.add_button, alignment=Qt.AlignmentFlag.AlignRight)
        
        self.setLayout(self.main_layout)
        self.setObjectName(name)
        
        if data is not None:
            self.__dict__.update(data["constants"])
            
            for _id, values in data["variables"].items():
                self.add(self.input_placeholders, _id, values)
        
        self.container_layout.addStretch()
        
        for _id, _temp_popups in self._temp_popups.copy().items():
            for var_name, popup in _temp_popups.items():
                self.popup_closed(_id, popup, var_name, True)
            del self._temp_popups[_id]
        
        self.scroll_area.verticalScrollBar().setValue(0) # type: ignore
    
    def go_to(self, _id):
        for widget_id, widget in self.widgets.items():
            if widget_id == _id:
                self.scroll_area.verticalScrollBar().setValue(widget.y())
                widget.setFocus()
                
                break
    
    def keyPressEvent(self, a0):
        if a0.key() == 16777220: # type: ignore
            focus_widget = self.focusWidget()
            
            if isinstance(focus_widget, (QLineEdit, QScrollArea)):
                self.add(self.input_placeholders)
        
        return super().keyPressEvent(a0)
    
    def get(self):
        return self.info
    
    def get_constants(self):
        return {}
    
    def add(self, input_placeholders: list[tuple[str, int]], _id: str | None = None, data: dict | None = None):
        widget = QWidget()
        layout = QVBoxLayout()
        
        widget.setProperty("class", "SettingOptionEntry")
        widget.setContentsMargins(20, 5, 20, 5)
        widget.setLayout(layout)
        
        buttons_layout = QHBoxLayout()
        header_layout = QHBoxLayout()
        
        _id = hex(id(widget)).lower().replace("0x", "") if _id is None else _id
        
        if data is None:
            self.info[_id] = self.get_new_data()
        else:
            self.info[_id] = data
        
        text_edits = self._make_inputs(_id, input_placeholders, data)
        
        delete_button = QPushButton("×")
        delete_button.setProperty("class", 'Close')
        delete_button.clicked.connect(self._make_delete_func(_id, widget))
        
        self.make_popups(_id, buttons_layout)
        buttons_layout.addWidget(delete_button, alignment=Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignTop)
        
        layout.addLayout(buttons_layout)
        layout.addLayout(header_layout)
        
        for data_widget in self.display_data_widgets[_id].values():
            layout.addWidget(data_widget)
        
        self.container_layout.insertWidget(len(self.info) - 1, widget, alignment=Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignVCenter)
        
        self.scroll_area.update()
        self.scroll_area.verticalScrollBar().setValue(self.scroll_area.verticalScrollBar().maximum()) # type: ignore
        
        for index, (edit, stretch) in enumerate(text_edits):
            header_layout.addWidget(edit, stretch=stretch)
            edit.show()
            
            if not index:
                edit.setFocus()
        
        self.widgets[_id] = widget
    
    def make_popups(self, _id: str, layout: QHBoxLayout):
        pass
    
    def get_new_data(self) -> dict[str, Any] | None:
        pass
    
    def update_data_interaction(self, prev_index: int, curr_index: int):
        pass
    
    def entry_deleted(self, _id):
        pass
    
    def popup_closed(self, _id: str, popup: BaseSubWidget, var_name: str, init: bool = False):
        pass
    
    def add_display_data_info(self, _id: str, text: str, var_name: str):
        if not self.sub_display_data_widgets[_id][var_name] or len(self.sub_display_data_widgets[_id][var_name][-1].findChildren(QLabel)) >= self.display_data_max:
            new_sub_widget = QWidget()
            new_sub_layout = QHBoxLayout()
            new_sub_widget.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Maximum)
            new_sub_widget.setLayout(new_sub_layout)
            
            self.sub_display_data_widgets[_id][var_name].append(new_sub_widget)
            self.display_data_widgets[_id][var_name].layout().addWidget(new_sub_widget)
        
        label = QLabel(self.font_metrics.elidedText(text, Qt.TextElideMode.ElideRight, 90))
        label.setFont(self.font())
        label.setToolTip(text)
        label.setStyleSheet(f"QLabel {{background-color: blue; border-radius: 8px; font-size: 15px}}")
        label.setFixedSize(100, 35)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.mousePressEvent = self._temp_popups
        
        self.sub_display_data_widgets[_id][var_name][-1].layout().addWidget(label)
    
    def clear_display_data_info(self, _id: str, var_name: str):
        for widget in self.sub_display_data_widgets[_id][var_name].copy():
            for label in widget.findChildren(QLabel):
                widget.layout().removeWidget(label)
                label.deleteLater()
            
            self.sub_display_data_widgets[_id][var_name].remove(widget)
            self.display_data_widgets[_id][var_name].layout().removeWidget(widget)
            widget.deleteLater()
    
    def _make_inputs(self, _id: str, placeholders: list[tuple[str, int]], data: dict | None):
        text_edits: list[tuple[QLineEdit, int]] = []
        
        for index, (placeholder, stretch) in enumerate(placeholders):
            text = data["text"][index] if data is not None else ""
            
            edit = QLineEdit()
            edit.setPlaceholderText(placeholder)
            edit.setFixedHeight(80)
            if data is None: self.info[_id]["text"].append(text)
            edit.textChanged.connect(self._make_text_changed_func(_id, index))
            edit.setText(text)
            
            text_edits.append((edit, stretch))
        
        return text_edits
    
    def _make_text_changed_func(self, _id, index):
        def text_changed_func(text: str):
            self.info[_id]["text"][index] = text
            self.saved_state_changed.emit()
        
        return text_changed_func
    
    def _make_delete_func(self, _id: str, widget: QWidget):
        def del_widget():
            self.container_layout.removeWidget(widget)
            widget.deleteLater()
            self.entry_deleted(_id)
            self.info.pop(_id)
            
            self.saved_state_changed.emit()
        
        return del_widget
    
    def _make_popup(self, _id: str, title: str, layout: QHBoxLayout, popup_class: type[BaseSubWidget], var_name: str, button_name: str | None = None, alignment: Qt.AlignmentFlag | None = None, *args, **kwargs):
        if _id not in self.sub_display_data_widgets:
            self.sub_display_data_widgets[_id] = {}
        if _id not in self.display_data_widgets:
            self.display_data_widgets[_id] = {}
        
        self.sub_display_data_widgets[_id][var_name] = []
        
        self.display_data_widgets[_id][var_name] = QWidget()
        self.display_data_widgets[_id][var_name].setLayout(QVBoxLayout())
        self.display_data_widgets[_id][var_name].setStyleSheet("QWidget {background: none}")
        
        button = QPushButton(button_name if button_name is not None else title)
        
        button.setFixedWidth(100)
        button.setProperty("class", 'action')
        button.clicked.connect(self._make_popup_func(_id, title, popup_class, var_name, *args, **kwargs))
        
        if alignment is not None:
            layout.addWidget(button, alignment=alignment)
        else:
            layout.addWidget(button)
    
    def _make_popup_func(self, _id: str, title: str, popup_class: type[BaseSubWidget], var_name: str, *args, **kwargs):
        if _id not in self._temp_popups:
            self._temp_popups[_id] = {}
        self._temp_popups[_id][var_name] = popup_class(title=title, info=self.info[_id].get(var_name, {}), saved_state_changed=self.saved_state_changed, *args, **kwargs)
        
        def show_popup():
            popup = popup_class(title=title, info=self.info[_id].get(var_name, {}), saved_state_changed=self.saved_state_changed, *args, **kwargs)
            
            popup.exec()
            self.info[_id][var_name] = popup.get()
            
            self.popup_closed(_id, popup, var_name)
        
        return show_popup

class MenuFrame(QFrame):
    def __init__(self):
        super().__init__()
        self.setProperty("class", "Menu")
        self.setStyleSheet("QFrame.Menu { border: 1px solid "+ THEME_MANAGER.parse_stylesheet("{border2}") +"; }")
        self.setWindowFlags(Qt.WindowType.Popup)
        self.setFrameShape(QFrame.Shape.Box)
        
        self.main_layout = QVBoxLayout()
        self.setLayout(self.main_layout)
        
        self._pos = self.pos()
    
    def set_pos(self, pos: QPoint):
        self._pos = pos
    
    def toogle(self):
        if self.isVisible():
            self.hide()
        else:
            self.move(self._pos)
            self.show()


class SearchWidget(QWidget):
    def __init__(self, prime_widget: BaseSubWidget | BaseSettingWidget):
        super().__init__()
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        self.container = QWidget()
        self.main_layout = QVBoxLayout()
        self.container.setLayout(self.main_layout)
        self.container.setFixedHeight(30)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        
        layout.addWidget(self.container)
        layout.setContentsMargins(0, 0, 0, 0)
        
        self.prime_widget = prime_widget
        
        # Center widget
        self.set_search_visible_button = QPushButton("Search")
        self.set_search_visible_button.setFixedHeight(30)
        self.set_search_visible_button.clicked.connect(self._toggle_search)
        self.set_search_visible_button.setStyleSheet("min-width: 600px; min-height: 30px; border-radius: 10px; padding: 0px;")
        
        self.main_search_widget = MenuFrame()
        self.main_search_widget.setFixedWidth(600)
        self.main_search_widget.setFixedWidth(300)
        self.main_search_layout = self.main_search_widget.layout()
        self.main_search_layout.setContentsMargins(0, 0, 0, 0)
        
        self.search_widget = QWidget()
        self.search_layout = QVBoxLayout()
        self.search_widget.setLayout(self.search_layout)
        
        self.search_edit = QLineEdit()
        self.search_edit.setVisible(False)
        self.search_edit.setFixedHeight(30)
        self.search_edit.textChanged.connect(self.search)
        self.search_edit.setPlaceholderText("Search file by name")
        self.search_edit.setStyleSheet("min-width: 600px; min-height: 30px; border-radius: 10px; padding: 0px;")
        
        self.main_search_layout.addWidget(self.search_edit)
        self.main_search_layout.addWidget(self.search_widget)
        
        self.main_layout.addWidget(self.set_search_visible_button)
    
    def get_intellisense(search_text: str, target_text: str):
        intellisense = []
        
        index = -1
        for c in search_text:
            if (index := target_text[index + 1:].find(c)) != -1:
                intellisense.append(index)
                continue
            
            break
        
        return intellisense
    
    def _toggle_search(self):
        # self.set_search_visible_button.setVisible(not self.set_search_visible_button.isVisible())
        self.main_search_widget.set_pos(QPoint(0, 0))
        self.main_search_widget.toogle()
    
    def search(self, text: str):
        for widget in self.search_widget.children():
            self.search_layout.removeWidget(widget)
            widget.deleteLater()
        
        if isinstance(self.prime_widget, BaseSettingWidget):
            sorted_data = sorted(list(self.prime_widget.get().items()), key=lambda _, data: " ".join(data["text"]))
            for _id, data in sorted_data:
                data_text = " ".join(data["text"])
                intellisense = self.get_intellisense(text, data_text)
                
                if intellisense:
                    label = QLabel("".join([(f"<span style='color: {'red' if i in intellisense else 'white'}'>{c}</span>") for i, c in enumerate(data_text)]))
                    label.mousePressEvent = lambda _: self.prime_widget.go_to(_id)
                    
                    self.search_layout.addWidget(label)



class CustomTitleBar(QWidget):
    def __init__(self, parent: QWidget, focus_widget: BaseSettingWidget, get_search_data: Callable[[], dict | list | set | tuple | str | int]):
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
        self.center_layout.addWidget(SearchWidget(focus_widget))
        
        # Right widget
        # Nothing here
        
        self.mian_layout.addWidget(left_widget, alignment=Qt.AlignmentFlag.AlignLeft)
        self.mian_layout.addWidget(center_widget)
        self.mian_layout.addWidget(right_widget, alignment=Qt.AlignmentFlag.AlignRight)
    
class MainTitleBar(CustomTitleBar):
    def __init__(self, parent, menu_bar: QMenuBar, focus_widget: BaseSettingWidget, go_back_func: Callable, go_forward_func: Callable):
        super().__init__(parent, focus_widget , lambda: {})
        
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


class TimeTableItem(QTableWidgetItem):
    def __init__(self, subject: SubjectType, break_time: bool, free_period: bool):
        super().__init__()
        self.subject = subject
        self.break_time = break_time
        self.free_period = free_period
        
        self.setFlags(self.flags() & Qt.ItemFlag.ItemIsEnabled)
        
        if self.break_time:
            self.set_color()
        elif self.free_period:
            self.setFlags(self.flags() & ~Qt.ItemFlag.ItemIsDragEnabled & ~Qt.ItemFlag.ItemIsEnabled & ~Qt.ItemFlag.ItemIsSelectable)
        
        # I check if subject is None seperately bcos of when the break time is checked
        
        if self.break_time:
            self.setFlags(self.flags() & ~Qt.ItemFlag.ItemIsDragEnabled & ~Qt.ItemFlag.ItemIsDropEnabled & ~Qt.ItemFlag.ItemIsEnabled & ~Qt.ItemFlag.ItemIsSelectable)
        elif not self.free_period and not self.break_time:
            locked = self.subject.lockedPeriod is not None
            
            if locked:
                color = QColor(THEME_MANAGER.parse_stylesheet("{fg4}"))
                self.setBackground(color)
            
            self.setText(self.subject.name)
            self.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            
            if isinstance(self.subject, Subject):
                self.setToolTip(f"Name: {self.subject.name}\nID: {self.subject.uniqueID}\nTeacher: {self.subject.teacher.name}{"\nSubject Locked" if locked else ""}")
            else:
                name = "/".join([s.name for s in self.subject.subjects]) if self.subject.name is None else self.subject.name
                sub_subject_names = "\n".join([f"\tName: {s.name}\n\tID: {s.uniqueID}\n" for s in self.subject.subjects])
                
                self.setToolTip(f"Name: {name}\nID: {self.subject.uniqueID}\nSubjects: {sub_subject_names}{"\nSubject Locked" if locked else ""}")

    def set_color(self, color: str | None = None):
        color = QColor(THEME_MANAGER.parse_stylesheet("{fg1}") if color is None else color)
        self.setBackground(color)

class DraggableSubjectLabel(QLabel):
    clicked = pyqtSignal(QMouseEvent)
    
    def __init__(self, subject: SubjectType):
        super().__init__(subject.name)
        self.subject = subject
        
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setProperty("class", 'RemSubjectItem')
        if isinstance(self.subject, Subject):
            self.setToolTip(f"Name: {self.subject.name}\nID: {self.subject.uniqueID}\nTeacher: {self.subject.teacher.name}")
        else:
            name = "/".join([s.name for s in self.subject.subjects]) if self.subject.name is None else self.subject.name
            sub_subject_names = "\n".join([f"\tName: {s.name}\n\tID: {s.uniqueID}\n" for s in self.subject.subjects])
            
            self.setToolTip(f"Name: {name}\nID: {self.subject.uniqueID}\nSubjects: {sub_subject_names}")
        
        self.setFixedSize(150, 40)
    
    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit(event)

class NumberLineEdit(QWidget):
    textChanged = pyqtSignal(int)
    
    def __init__(self, number: int, min_validatorAmt: int = 0, max_validatorAmt: int = 10):
        super().__init__()
        
        self.min_num = min_validatorAmt
        self.max_num = max_validatorAmt
        
        self.edit = QLineEdit()
        self.edit.textChanged.connect(self._updateNumber)
        self.edit.setValidator(QIntValidator())
        self.setNumber(number)
        
        layout = QHBoxLayout()
        self.setLayout(layout)
        
        buttons_widget = QWidget()
        buttons_layout = QVBoxLayout()
        
        buttons_widget.setStyleSheet("background: none;")
        buttons_widget.setLayout(buttons_layout)
        
        layout.addWidget(self.edit, alignment=Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignRight)
        layout.addWidget(buttons_widget, alignment=Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignLeft)
        
        buttons_layout.setContentsMargins(0, 0, 0, 0)
        
        increment_button = CustomLabel("▼", 180)
        increment_button.setContentsMargins(0, 0, 0, 0)
        increment_button.mouseclicked.connect(lambda: self._incDecNumber(1))
        
        decrement_button = CustomLabel("▼", 0)
        increment_button.setContentsMargins(0, 0, 0, 0)
        decrement_button.mouseclicked.connect(lambda: self._incDecNumber(-1))
        
        buttons_layout.addWidget(increment_button, alignment=Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignLeft)
        buttons_layout.addWidget(decrement_button, alignment=Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignLeft)
        
        self.setFixedHeight(50)
        self.edit.setFixedHeight(30)
    
    def number(self):
        return int(self._number)
    
    def setNumber(self, number: int):
        self._number = str(number)
        self.edit.setText(self._number)
    
    def setPlaceholderText(self, text: str):
        self.edit.setPlaceholderText(text)
    
    def _updateNumber(self, text: str):
        if not text.isnumeric() or self.max_num < int(text) < self.min_num:
            self.edit.setText(self._number)
        else:
            self._number = text
            self.textChanged.emit(int(self._number))
    
    def _incDecNumber(self, direction: int):
        number = self.number() + direction
        
        if self.min_num <= number <= self.max_num:
            self.setNumber(number)


class CustomLabel(QLabel):
    mouseclicked = pyqtSignal()
    
    def __init__(self, text, angle: int = 0, parent=None):
        super().__init__(text, parent)
        self.angle = angle  # Angle in degrees to rotate the text
        self.setProperty("class", "Arrow")
    
    def mousePressEvent(self, ev):
        if ev.button() == Qt.MouseButton.LeftButton:
            self.mouseclicked.emit()
    
    def setAngle(self, angle):
        self.angle = angle
        self.update()  # Trigger a repaint
    
    def paintEvent(self, _):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Save the painter's current state
        painter.save()

        # Translate to the center of the label
        center = self.rect().center()
        painter.translate(center)

        # Rotate the painter
        painter.rotate(self.angle)

        # Translate back and draw the text
        center.setX(center.x() + (2 if self.angle >= 180 else -1))
        painter.translate(-center)
        painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, self.text())

        # Restore the painter's state
        painter.restore()


class OptionTag(QWidget):
    deleted = pyqtSignal()
    started_editing_signal = pyqtSignal()
    finished_editing_signal = pyqtSignal()
    
    def __init__(self, initial_text: str | None = None):
        super().__init__()
        self.setProperty("class", "OptionTag")
        
        self.text = initial_text if initial_text is not None else ""
        self.is_editing = False
        
        self.main_layout = QHBoxLayout(self)
        self.main_layout.setContentsMargins(4, 2, 4, 2)
        self.main_layout.setSpacing(4)
        
        # Input mode widgets
        self.input = QLineEdit()
        self.input.setProperty("class", "OptionEdit")
        self.input.setText(self.text)
        self.input.setPlaceholderText("Enter option")
        self.input.setFixedWidth(80)  # Fix input width
        self.input.returnPressed.connect(self.input.clearFocus)
        self.input.editingFinished.connect(self.finish_editing)
        
        self.close_btn = QPushButton("×")
        self.close_btn.setProperty("class", "Close")
        self.close_btn.clicked.connect(self.remove)
        self.close_btn.setFixedSize(20, 20)
        
        self.deleted.connect(self.deleteLater)
        self.started_editing_signal.connect(self.start_editing)
        self.finished_editing_signal.connect(self._finished_editing)
        
        # Label mode widget
        self.label = QLabel(self.text)
        self.label.setMinimumWidth(80)
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label.mousePressEvent = lambda _: self.started_editing_signal.emit()
        
        # Initialize both widgets but hide input initially
        self.main_layout.addWidget(self.label)
        self.main_layout.addWidget(self.input)
        self.main_layout.addWidget(self.close_btn)
        self.input.hide()
        
        self.setFixedHeight(30)
        self.setFixedWidth(130)
    
    def _finished_editing(self):
        if self.is_editing:
            self.text = self.input.text().strip()
            self.is_editing = False
            self.setup_display_mode()
            self.label.setText(self.text)
            self.label.show()
    
    def setup_display_mode(self):
        self.label.show()
        self.input.hide()
        self.close_btn.show()
    
    def setup_edit_mode(self):
        self.label.hide()
        self.input.show()
        self.close_btn.show()
    
    def start_editing(self):
        if not self.is_editing:
            self.input.setText(self.text)
            self.setup_edit_mode()
            self.input.setFocus()
            
            self.is_editing = True
    
    def finish_editing(self):
        self.finished_editing_signal.emit()
    
    def remove(self):
        self.deleted.emit()
    
    def get_text(self):
        return self.text


class SelectedWidget(QWidget):
    def __init__(self, _id: str, text: str, host_container_layout: QVBoxLayout, saved_state_changed_signal: pyqtBoundSignal):
        super().__init__()
        layout = QHBoxLayout()
        layout.setSpacing(8)
        layout.setContentsMargins(10, 0, 0, 0)
        
        self.setLayout(layout)
        
        container = QWidget()
        container_layout = QHBoxLayout()
        
        container.setProperty("class", "SelectedSelectionListEntry")
        container.setLayout(container_layout)
        
        layout.addWidget(container)
        
        self.id = _id
        self.text = text
        self.host_container_layout = host_container_layout
        
        metrics = QFontMetrics(self.font())
        label = QLabel(metrics.elidedText(self.text, Qt.TextElideMode.ElideRight, 200))
        label.setFont(self.font())
        label.setToolTip(self.text)
        
        delete_button = QPushButton("×")
        delete_button.setProperty("class", 'Close')
        delete_button.setFixedSize(24, 24)
        delete_button.clicked.connect(self.delete_self)
        
        container_layout.addWidget(label)
        container_layout.addStretch()
        container_layout.addWidget(delete_button, alignment=Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        
        self.saved_state_changed_signal = saved_state_changed_signal
    
    def delete_self(self):
        self.host_container_layout.removeWidget(self)
        
        widget = UnselectedWidget(self.id, self.text, self.host_container_layout, self.saved_state_changed_signal)
        
        # Find the last unselected widget or append at the end
        insert_index = self.host_container_layout.count() - 1
        for i in range(self.host_container_layout.count() - 1, -1, -1):
            if isinstance(self.host_container_layout.itemAt(i).widget(), UnselectedWidget):
                insert_index = i
                break
        
        self.host_container_layout.insertWidget(insert_index, widget)
        
        self.deleteLater()
        
        self.saved_state_changed_signal.emit()

class UnselectedWidget(QWidget):
    def __init__(self, _id: str, text: str, host_container_layout: QVBoxLayout, saved_state_changed_signal: pyqtBoundSignal):
        super().__init__()
        layout = QHBoxLayout()
        layout.setSpacing(8)
        layout.setContentsMargins(10, 0, 0, 0)
        
        self.setLayout(layout)
        
        container = QWidget()
        container_layout = QHBoxLayout()
        
        container.setProperty("class", "UnselectedSelectionListEntry")
        container.setLayout(container_layout)
        
        layout.addWidget(container)
        
        self.id = _id
        self.text = text
        self.host_container_layout = host_container_layout
        
        metrics = QFontMetrics(self.font())
        label = QLabel(metrics.elidedText(self.text, Qt.TextElideMode.ElideRight, 200))
        label.setFont(self.font())
        label.setToolTip(text)
        
        add_button = QPushButton("×")
        add_button.setProperty("class", 'Close')
        add_button.setFixedSize(24, 24)
        add_button.clicked.connect(self.add_self)
        
        container_layout.addWidget(label)
        container_layout.addStretch()
        container_layout.addWidget(add_button, alignment=Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        
        self.saved_state_changed_signal = saved_state_changed_signal
    
    def add_self(self):
        self.host_container_layout.removeWidget(self)
        
        widget = SelectedWidget(self.id, self.text, self.host_container_layout, self.saved_state_changed_signal)
        
        insert_index = 0
        for i in range(self.host_container_layout.count()):
            if isinstance(self.host_container_layout.itemAt(i).widget(), SelectedWidget):
                insert_index = i + 1
        
        self.host_container_layout.insertWidget(insert_index, widget)
        
        self.deleteLater()
        
        self.saved_state_changed_signal.emit()



