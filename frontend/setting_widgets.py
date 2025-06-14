from copy import deepcopy
from typing import Any, Callable
from frontend.sub_widgets import (
    SelectionList, DropDownCheckBoxes, SubjectSelection,
    OptionSelection
)
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QLineEdit, QPushButton, QScrollArea
)
from PyQt6.QtCore import Qt
from frontend.theme import *


class SettingWidget(QWidget):
    def __init__(self, name: str, input_placeholders: list[str]):
        super().__init__()
        self.objectNameChanged.connect(lambda: self.add_button.setText(f"Add {self.objectName().title()}"))
        
        self.info = {}
        self.id_mapping = {}
        self.info_framework = {}
        self.input_placeholders = input_placeholders
        
        self.main_layout = QVBoxLayout(self)
        
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        
        self.container = QWidget()
        self.container_layout = QVBoxLayout(self.container)
        self.container_layout.addStretch()
        self.scroll_area.setWidget(self.container)
        
        self.add_button = QPushButton()
        self.add_button.clicked.connect(lambda: self.add(self.input_placeholders))
        
        self.main_layout.addWidget(self.scroll_area)
        self.main_layout.addWidget(self.add_button, alignment=Qt.AlignmentFlag.AlignRight)
        
        self.setLayout(self.main_layout)
        self.setObjectName(name)
        self.setStyleSheet(THEME[SUBJECT_TEACHERS_CLASSES])
    
    def _wrapper_function_dec(func: Callable):
        def wrapper(*args, **kwargs):
            def sub_wrapper():
                return func(*args, **kwargs)
            return sub_wrapper
        
        return wrapper
    
    def keyPressEvent(self, a0):
        if a0.key() == 16777220:
            self.add(self.input_placeholders)
        return super().keyPressEvent(a0)
    
    def get(self):
        return self.info
    
    def add(self, input_placeholders: list[str]):
        widget = QWidget()
        widget.setObjectName("itemContainer")
        widget.setMaximumHeight(150)
        
        layout = QVBoxLayout()
        widget.setLayout(layout)
        
        header_layout = QHBoxLayout()
        buttons_layout = QHBoxLayout()
        
        # _id = widget.__repr__()
        _id = self.objectName() + ": " + str(len(self.info) + 1)
        
        self.set_info(_id)
        
        text_edits = self._make_inputs(_id, input_placeholders)
        
        delete_button = QPushButton("×")
        delete_button.setProperty('class', 'warning')
        delete_button.clicked.connect(self._make_delete_func(_id, widget))
        delete_button.setFixedSize(30, 30)
        delete_button.setStyleSheet("padding: 3px;")
        
        for edit in text_edits:
            header_layout.addWidget(edit)
        
        self.make_popups(_id, buttons_layout)
        buttons_layout.addWidget(delete_button, alignment=Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignTop)
        
        layout.addLayout(buttons_layout)
        layout.addLayout(header_layout)
        
        self.container_layout.insertWidget(0, widget, alignment=Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignVCenter)
        
        # name_edit.returnPressed.connect(lambda: name_edit.clearFocus())
        for edit in text_edits:
            edit.show()
        text_edits[0].setFocus()
        
    def make_popups(self, _id: str, layout: QHBoxLayout):
        pass
    
    def set_info(self, _id: str):
        pass
    
    def _make_store_edit_func(self, _id: str, edit: QLineEdit, index: int):
        def store_text_data():
            self.info[_id]["text"][index] = edit.text()
        
        return store_text_data
    
    def _make_inputs(self, _id: str, placeholders: list[str]):
        text_edits: list[QLineEdit] = []
        
        for index, placeholder in enumerate(placeholders):
            edit = QLineEdit()
            edit.setPlaceholderText(placeholder)
            edit.setFixedHeight(80)
            edit.setStyleSheet("font-size: 40px;")
            
            self.info[_id]["text"].append("")
            
            edit.textChanged.connect(self._make_store_edit_func(_id, edit, index))
            
            text_edits.append(edit)
        
        return text_edits
    
    def _make_delete_func(self, _id: str, widget: QWidget):
        def del_widget():
            delete_button = self.sender()
            delete_button.setProperty('class', 'warning')
            self.container_layout.removeWidget(widget)
            widget.deleteLater()
            self.info.pop(_id)
        
        return del_widget
    
    def _make_popup(self, _id: str, title: str, layout: QHBoxLayout, popup_class: type[SelectionList] | type[SubjectSelection] | type[OptionSelection] | type[DropDownCheckBoxes], var_name: str, button_name: str | None = None, alignment: Qt.AlignmentFlag = None, *args, **kwargs):
        button = QPushButton(button_name if button_name is not None else title)
        
        button.setFixedWidth(100)
        button.setProperty('class', 'action')
        button.clicked.connect(self._make_popup_func(_id, title, popup_class, var_name, *args, **kwargs))
        
        if alignment is not None:
            layout.addWidget(button, alignment=alignment)
        else:
            layout.addWidget(button)
    
    def _make_popup_func(self, _id: str, title: str, popup_class: type[SelectionList] | type[SubjectSelection] | type[OptionSelection] | type[DropDownCheckBoxes], var_name: str, *args, **kwargs):
        def show_popup():
            popup = popup_class(title=title, info=self.info[_id][var_name], *args, **kwargs)
            popup.exec()
            self.info[_id][var_name] = popup.get()
        
        return show_popup



class Subjects(SettingWidget):
    def __init__(self):
        super().__init__("Subject", ["Enter the subject name"])
        self.teachers = [None]
    
    def set_info(self, _id):
        self.info[_id] = {
            "text": [],
            "classes": {
                "content": {},
                "id_mapping": {
                    "main": {},
                    "sub": {}
                }
            },
            "teachers": {
                "content": deepcopy(self.teachers),
                "id_mapping": deepcopy(self.id_mapping)
            }
        }
    
    def make_popups(self, _id, layout):
        self._make_popup(_id, "Classes", layout, DropDownCheckBoxes, "classes")
        self._make_popup(_id, "Teachers", layout, SelectionList, "teachers", alignment=Qt.AlignmentFlag.AlignLeft)

class Teachers(SettingWidget):
    def __init__(self):
        super().__init__("Teacher", ["Full name"])
        self.subjects = [None]
    
    def set_info(self, _id: str):
        self.info[_id] = {
            "text": [],
            "subjects": {
                "content": deepcopy(self.subjects),
                "id_mapping": deepcopy(self.id_mapping)
            }
        }
    
    def make_popups(self, _id, layout):
        self._make_popup(_id, "Subjects", layout, SelectionList, "subjects", alignment=Qt.AlignmentFlag.AlignLeft)

class Classes(SettingWidget):
    def __init__(self):
        super().__init__("Class", ["Enter the class section name"])
        
        self.subject_teachers_mapping = {}
        
        self.default_per_day = 2
        self.default_per_week = 4
    
    def set_info(self, _id: str):
        self.info[_id] = {
            "text": [],
            "options": {},
            "subjects": {
                "content": {},
                "id_mapping": {index : index_id for index, (index_id, _) in enumerate(deepcopy(self.subject_teachers_mapping).items())},
                "available_subject_teachers": self.subject_teachers_mapping
            }
        }
    
    def make_popups(self, _id, layout):
        self._make_popup(_id, "Option Selector", layout, OptionSelection, "options", button_name="Options")
        self._make_popup(_id, "Subjects", layout, SubjectSelection, "subjects", alignment=Qt.AlignmentFlag.AlignLeft, default_per_day=self.default_per_day, default_per_week=self.default_per_week)


