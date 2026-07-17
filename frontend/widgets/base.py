from frontend.imports import *
from frontend.extras import *
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
        
        self._saved_changed = True
        self.saved_state_changed.connect(self._change_save_change)
    
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
    
    def popup_closed(self, _id: str, var_name: str, popup: BaseSubWidget, init: bool = False):
        pass
    
    def add_display_data_info(self, _id: str, var_name: str, text: str, desination_id: str):
        def display_data_func(ev):
            popup_class, title, args, kwargs = self.popups_data[_id][var_name]
            
            popup = popup_class(title=title, info=self.info[_id][var_name], saved_state_changed=self.saved_state_changed, *args, **kwargs)
            popup.go_to(desination_id)
            
            show_popup_func = self._make_popup_func(_id, title, popup_class, var_name, *args, **kwargs)
            
            show_popup_func(popup)
        
        if not self.sub_display_data_widgets[_id][var_name]:
            self.display_data_widgets[_id][var_name].layout().addWidget(QLabel(f"<span style='font-weight: 900; font-family: Sans Serif;'>{var_name.title()}</span>"))
        
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
    
    def _change_save_change(self):
        self._saved_changed = True
    
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
            self.popups_data.pop(_id)
            
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
            
            self.popup_closed(_id, var_name, popup)
        
        return show_popup




