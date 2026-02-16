import math
from typing import TypeVar
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
        self.popups_data: dict[str, dict[str, tuple[type[BaseSubWidget], str, list, dict[str, Any]]]] = {}
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
        
        self._update_display_data_info(True)
        
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
        
        for index, (edit, stretch) in enumerate(text_edits):
            header_layout.addWidget(edit, stretch=stretch)
            edit.show()
            
            if not index:
                edit.setFocus()
        
        self.widgets[_id] = widget
        
        QTimer.singleShot(
            200,
            lambda: self.scroll_area.verticalScrollBar().setValue(self.scroll_area.verticalScrollBar().maximum()) # type: ignore
        )
    
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
    
    def add_display_data_info(self, _id: str, var_name: str, text: str, desination_id: str):
        def display_data_func(ev):
            popup_class, title, args, kwargs = self.popups_data[_id][var_name]
            
            popup = popup_class(title=title, info=self.info[_id][var_name], saved_state_changed=self.saved_state_changed, *args, **kwargs)
            popup.go_to(desination_id)
            
            show_popup_func = self._make_popup_func(_id, title, popup_class, var_name, *args, **kwargs)
            
            show_popup_func(popup)
        
        if not self.sub_display_data_widgets[_id][var_name] or len(self.sub_display_data_widgets[_id][var_name][-1].findChildren(QLabel)) >= self.display_data_max:
            new_sub_widget = QWidget()
            new_sub_layout = QHBoxLayout()
            new_sub_widget.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Maximum)
            new_sub_widget.setLayout(new_sub_layout)
            
            self.sub_display_data_widgets[_id][var_name].append(new_sub_widget)
            self.display_data_widgets[_id][var_name].layout().addWidget(new_sub_widget)
        
        label = QLabel(self.font_metrics.elidedText(text, Qt.TextElideMode.ElideRight, 80))
        label.setFont(self.font())
        label.setToolTip(text)
        label.setStyleSheet(f"QLabel {{background-color: {THEME_MANAGER.pallete_get("fg3")}; border-radius: 8px; font-size: 15px}}")
        label.setFixedSize(110, 35)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.mousePressEvent = display_data_func
        
        self.sub_display_data_widgets[_id][var_name][-1].layout().addWidget(label)
    
    def clear_display_data_info(self, _id: str, var_name: str):
        clear_layout(self.display_data_widgets[_id][var_name].layout())
        
        self.sub_display_data_widgets[_id][var_name].clear()
        self.display_data_widgets[_id][var_name].layout().addWidget(QLabel(f"<span style='font-weight: 900; font-family: Sans Serif;'>{var_name.title()}</span>"))
    
    def _update_display_data_info(self, init: bool = False):
        for _id, popup_data in self.popups_data.copy().items():
            for var_name, (popup_class, title, args, kwargs) in popup_data.items():
                popup = popup_class(title=title, info=self.info[_id][var_name], saved_state_changed=self.saved_state_changed, *args, **kwargs)
                
                self.popup_closed(_id, var_name, popup, init)
    
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
        if _id not in self.popups_data:
            self.popups_data[_id] = {}
        self.popups_data[_id][var_name] = popup_class, title, args, kwargs
        
        def show_popup(popup=None):
            popup = popup or popup_class(title=title, info=self.info[_id].get(var_name, {}), saved_state_changed=self.saved_state_changed, *args, **kwargs)
            
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


T = TypeVar("T")
class SearchEdit(QFrame):
    DEBOUNCE_MS = 120
    MAX_RESULTS = math.inf

    def __init__(
        self,
        get_search_scope_callback: Callable[
            [], list[tuple[T, str, tuple[Optional[str], Optional[str], Optional[str]], list[Optional[str]]]]
        ],
        goto_search_callback: Optional[Callable[[T], None]] = None
    ):
        super().__init__(None)

        self.get_search_scope_callback = get_search_scope_callback
        self.goto_search_callback = goto_search_callback

        self.setWindowFlags(Qt.WindowType.Popup)
        self.setFrameShape(QFrame.Shape.Box)
        self.setProperty("class", "option-menu")
        self.setFixedWidth(500)

        self._updating = False

        # ---------- Layout ----------
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(2, 2, 2, 2)
        
        self.search_le = QLineEdit()
        self.search_le.setPlaceholderText("Search")
        self.search_le.setFixedWidth(496)
        self.search_le.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Preferred)
        
        self.main_layout.addWidget(self.search_le, alignment=Qt.AlignmentFlag.AlignTop)

        self.options_container, self.options_layout = create_scrollable_widget(None, QVBoxLayout)
        self.options_container.setFixedWidth(496)
        self.options_container.setFixedHeight(220)
        self.options_container.setVisible(False)

        self.main_layout.addWidget(self.options_container, alignment=Qt.AlignmentFlag.AlignTop)

        # ---------- Debounce ----------
        self._search_timer = QTimer(self)
        self._search_timer.setSingleShot(True)
        self._search_timer.timeout.connect(self._run_search)

        self.search_le.textEdited.connect(self._on_text_edited)

    # ---------------------------------------------------------
    # Event Flow
    # ---------------------------------------------------------

    def _on_text_edited(self, text: str):
        self._search_timer.start(self.DEBOUNCE_MS)

    def show(self):
        self.search_le.blockSignals(True)
        self.search_le.clear()
        self.search_le.blockSignals(False)

        self._run_search()
        super().show()
        self.search_le.setFocus()

    # ---------------------------------------------------------
    # Search Logic
    # ---------------------------------------------------------

    def _run_search(self):
        if self._updating:
            return

        self._updating = True
        text = self.search_le.text().strip()

        clear_layout(self.options_layout)
        
        self.options_layout.addStretch()
        
        if not text:
            self.options_container.setVisible(False)
            self._updating = False
            return

        score_data = sorted(
            [
                (
                    data_point,
                    (name, right, bottom, end),
                    self._get_find_score(text, name, (right, bottom, end), bg)
                )
                for data_point, name, (right, bottom, end), bg
                in self.get_search_scope_callback()
            ],
            key=lambda x: x[2][0],
            reverse=True
        )

        added = 0
        for index, (data_point, (name, right, bottom, end), (score, indices)) in enumerate(score_data):
            if score == -1 or added >= self.MAX_RESULTS:
                continue

            label = QLabel(
                self._stylize_text_indices(
                    name,
                    f"color: {THEME_MANAGER.pallete_get("fg1")}; font-weight: bold;",
                    right,
                    bottom,
                    end,
                    indices
                )
            )
            label.setProperty("class", "QPushButton")
            label.mousePressEvent = self._make_option_clicked_func(data_point)
            
            self.options_layout.insertWidget(index, label, alignment=Qt.AlignmentFlag.AlignTop)
            added += 1
        
        self.options_container.setVisible(added > 0)
        
        self._updating = False

    # ---------------------------------------------------------
    # Helpers
    # ---------------------------------------------------------

    def _make_option_clicked_func(self, data_point: T):
        def handler(_):
            self.hide()
            self.search_le.blockSignals(True)
            self.search_le.clear()
            self.search_le.blockSignals(False)

            if self.goto_search_callback:
                self.goto_search_callback(data_point)

        return handler
    
    def _get_find_score(
        self,
        text: str,
        potential_match: str,
        extra_text_data: Optional[tuple[Optional[str], Optional[str], Optional[str]]] = None,
        backgrounds_texts: Optional[list[Optional[str]]] = None
    ):
        l_text = text.lower()
        l_target = potential_match.lower()
        
        space_amt = 0
        additions = 0
        
        text_len = len(l_text)
        target_len = len(l_target)
        
        index = 0
        
        bg_data = []
        
        score_indices = []
        right_indices = []
        bottom_indices = []
        end_indices = []
        
        right_score = -1
        bottom_score = -1
        end_score = -1
        
        if extra_text_data:
            right_text, bottom_text, end_text = extra_text_data
            
            if right_text:
                right_score, right_indices = self._get_find_score(text, right_text)
                right_indices = right_indices[0]
            if bottom_text:
                bottom_score, bottom_indices = self._get_find_score(text, bottom_text)
                bottom_indices = bottom_indices[0]
            if end_text:
                end_score, end_indices = self._get_find_score(text, end_text)
                end_indices = end_indices[0]
        
        if backgrounds_texts:
            bg_data = [self._get_find_score(text, bg_text)[0] for bg_text in backgrounds_texts if bg_text is not None]
        
        for i, c in enumerate(l_text):
            f_index = l_target[index:].find(c)
            
            if f_index != -1 and text_len <= target_len:
                space_amt += f_index
                index += f_index + 1
                
                additions += text[i] == potential_match[index - 1]
                additions += f_index == 0
                
                score_indices.append(index - 1)
                
                continue
            break
        else:
            return (text_len / (target_len + space_amt)) + additions, (score_indices, [], [], [])
        
        if bottom_score == -1 and right_score != -1:
            return right_score / 20, ([], right_indices, [], [])
        elif right_score == -1 and bottom_score != -1:
            return bottom_score / 20, ([], [], bottom_indices, [])
        elif right_score != -1 and bottom_score != -1:
            return (right_score + bottom_score) / 20, ([], right_indices, bottom_indices, [])
        elif end_score != -1:
            return end_score / 20, ([], [], [], end_indices)
        elif bg_data:
            for bg_score in bg_data:
                if bg_score != -1:
                    return bg_score / 20, ([], [], [], [])
        
        return -1, ([], [], [], [])
    
    def _stylize_text_indices(self, main_text: str, style: str, right_text: Optional[str], bottom_text: Optional[str], end_text: Optional[str], indices: tuple[list[int], list[int], list[int]]):
        main_indices, right_indices, bottom_indices, end_indices = indices
        
        text = f"""
        <table width="100%">
        <tr>
            <td align="left">
            {"".join([f"<span style='font-size: 23px; {f"{style}" if i in main_indices else ""}'>{c}</span>" for i, c in enumerate(main_text)])}
            <span>    </span>
            {"".join([f"<span style='color: grey; font-size: 18px; font-weight: 300; {f"{style}" if i in right_indices else ""}'>{c}</span>" for i, c in enumerate(right_text)]) if right_text else ""}
            <br>
            {"".join([f"<span style='color: grey; font-size: 15px; font-weight: 500; {f"{style}" if i in bottom_indices else ""}'>{c}</span>" for i, c in enumerate(bottom_text)]) if bottom_text else ""}
            </td>
            <td align="right">
            {"".join([f"<span style='color: lightgrey; font-size: 10px; font-weight: 300; {f"{style}" if i in end_indices else ""}'>{c}</span>" for i, c in enumerate(end_text)]) if end_text else ""}
            </td>
            <br>
        </tr>
        </table>
        """
        return text



class CustomTitleBar(QWidget):
    def __init__(self, parent: QWidget, get_search_scope_func: Callable, goto_search_func: Callable):
        super().__init__(parent)
        self.master = parent
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
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
        
        self.center_widget = QWidget()
        self.center_layout = QHBoxLayout()
        self.center_widget.setProperty("class", "TitleBar")
        self.center_widget.setLayout(self.center_layout)
        self.center_layout.setContentsMargins(60, 5, 60, 5)
        
        right_widget = QWidget()
        self.right_layout = QHBoxLayout()
        right_widget.setProperty("class", "TitleBar")
        right_widget.setLayout(self.right_layout)
        self.right_layout.setContentsMargins(60, 0, 0, 0)
        self.right_layout.setSpacing(0)
        
        # Center widget
        self.search_edit = SearchEdit(get_search_scope_func, goto_search_func)
        
        self.search_pb = QPushButton("Search Subjects")
        self.search_pb.setFixedWidth(self.search_edit.width())
        self.search_pb.setStyleSheet(f"background-color: {THEME_MANAGER.pallete_get("bg2")}; border: 1px solid {THEME_MANAGER.pallete_get("border1")};")
        self.search_pb.clicked.connect(self._open_search_edit)
        
        # self.center_layout.addWidget(SearchWidget(focus_widget))
        self.center_layout.addWidget(self.search_pb)
        
        # Right widget
        # Nothing here
        
        self.mian_layout.addWidget(left_widget, alignment=Qt.AlignmentFlag.AlignLeft)
        self.mian_layout.addWidget(self.center_widget)
        self.mian_layout.addWidget(right_widget, alignment=Qt.AlignmentFlag.AlignRight)
    
    def _open_search_edit(self):
        self.search_edit.move(self.center_widget.mapToGlobal(QPoint(self.search_pb.x(), self.search_pb.y())))
        self.search_edit.search_le.setFocus()
        
        self.search_edit.show()

class MainTitleBar(CustomTitleBar):
    def __init__(self, parent, menu_bar: QMenuBar, get_search_scope_func: Callable, goto_search_func: Callable, go_back_func: Callable, go_forward_func: Callable):
        super().__init__(parent, get_search_scope_func, goto_search_func)
        
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
    def __init__(self, subject: SubjectType, break_time: bool = False, free_period: bool = False):
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
        elif not self.free_period:
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
        
        assert self.min_num <= self.max_num, f"Min: {self.min_num}; Max: {self.max_num}"
        
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
        assert self.min_num <= self.max_num, f"Min: {self.min_num}; Max: {self.max_num}"
        
        if not text.isnumeric() or self.max_num < int(text) < self.min_num:
            self.edit.setText(self._number)
        else:
            self._number = text
            self.textChanged.emit(int(self._number))
    
    def _incDecNumber(self, direction: int):
        assert self.min_num <= self.max_num, f"Min: {self.min_num}; Max: {self.max_num}"
        
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



