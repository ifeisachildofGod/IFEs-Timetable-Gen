from copy import deepcopy
from typing import Any
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
        
        self.main_layout = QVBoxLayout(self)
        
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        
        self.container = QWidget()
        self.container_layout = QVBoxLayout(self.container)
        self.container_layout.addStretch()
        self.scroll_area.setWidget(self.container)
        
        self.add_button = QPushButton()
        self.add_button.clicked.connect(lambda: self.add(input_placeholders))
        
        self.main_layout.addWidget(self.scroll_area)
        self.main_layout.addWidget(self.add_button, alignment=Qt.AlignmentFlag.AlignRight)
        
        self.setLayout(self.main_layout)
        self.setObjectName(name)
        self.setStyleSheet(THEME[SUBJECT_TEACHERS_CLASSES])
    
    def keyPressEvent(self, a0):
        if a0.key() == 16777220:
            self.add()
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
        _id = self.objectName() + ": " + str(len(self.info))
        
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
            popup = popup_class(*args, **kwargs, title=title, info=self.info[_id][var_name])
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
    
    def set_info(self, _id: str):
        self.info[_id] = {
            "text": [],
            "options": {},
            "subjects": {
                "content": {},
                "id_mapping": {index : index_id for index, (index_id, _) in enumerate(deepcopy(self.subject_teachers_mapping).items())}
                }
            }
    
    def make_popups(self, _id, layout):
        self._make_popup(_id, "Option Selector", layout, OptionSelection, "options", button_name="Options")
        self._make_popup(_id, "Subjects", layout, SubjectSelection, "subjects", alignment=Qt.AlignmentFlag.AlignLeft, kwargs={"available_subject_teachers": self.subject_teachers_mapping})

# class Subjects(QWidget):
#     def __init__(self):
#         super().__init__()
#         self.objectNameChanged.connect(lambda: self.add_button.setText(f"Add {self.objectName().title()}"))
        
#         self.info = {}
        
#         self.teachers = [None]
#         self.id_mapping = {}
        
#         self.classesInfo = {}
        
#         self.main_layout = QVBoxLayout(self)
        
#         self.scroll_area = QScrollArea()
#         self.scroll_area.setWidgetResizable(True)
        
#         self.container = QWidget()
#         self.container_layout = QVBoxLayout(self.container)
#         self.container_layout.addStretch()
#         self.scroll_area.setWidget(self.container)
        
#         self.add_button = QPushButton()
#         self.add_button.clicked.connect(self.add)
        
#         self.main_layout.addWidget(self.scroll_area)
#         self.main_layout.addWidget(self.add_button, alignment=Qt.AlignmentFlag.AlignRight)
        
#         self.list_selection_values = None
        
#         self.setLayout(self.main_layout)
        
#         self.setObjectName("subject")
#         self.setStyleSheet(THEME[SUBJECT_TEACHERS_CLASSES])
    
#     def keyPressEvent(self, a0):
#         if a0.key() == 16777220:
#             self.add()
#         return super().keyPressEvent(a0)
    
#     def get(self):
#         return self.info
    
#     def add(self):
#         widget = QWidget()
#         widget.setObjectName("itemContainer")
#         widget.setMaximumHeight(150)
        
#         layout = QVBoxLayout()
#         widget.setLayout(layout)
        
#         header_layout = QHBoxLayout()
#         buttons_layout = QHBoxLayout()
        
#         _id = widget.__repr__()
        
#         text_edits = self._make_inputs(_id, [f"Enter {self.objectName().title()} Name"])
        
#         delete_button = QPushButton("×")
#         delete_button.setProperty('class', 'warning')
#         delete_button.clicked.connect(self._make_delete_func(_id, widget))
#         delete_button.setFixedSize(30, 30)
#         delete_button.setStyleSheet("padding: 3px;")
        
#         for edit in text_edits:
#             header_layout.addWidget(edit)
        
#         self.make_action_buttons(_id, buttons_layout)
#         buttons_layout.addWidget(delete_button, alignment=Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignTop)
        
#         layout.addLayout(buttons_layout)
#         layout.addLayout(header_layout)
        
#         self.container_layout.insertWidget(0, widget, alignment=Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignVCenter)
        
#         self.set_info(_id)
        
#         # name_edit.returnPressed.connect(lambda: name_edit.clearFocus())
#         text_edits[0].show()
#         text_edits[0].setFocus()
    
#     def set_info(self, _id: str):
#         self.info[_id] = {"text": [], "classes": {"content": {}, "id_mapping": {"main": {}, "sub": {}}}, "teachers": {"content": self.teachers.copy(), "id_mapping": self.id_mapping.copy()}}
    
#     def _make_delete_func(self, _id: str, widget: QWidget):
#         def del_widget():
#             delete_button = self.sender()
#             delete_button.setProperty('class', 'warning')
#             self.container_layout.removeWidget(widget)
#             widget.deleteLater()
#             self.info.pop(_id)
        
#         return del_widget
    
#     def make_store_edit_func(self, _id: str, edit: QLineEdit, index: int):
#         def store_text_data():
#             self.info[_id]["text"][index] = edit.text()
        
#         return store_text_data
    
#     def _make_inputs(self, _id: str, placeholders: list[str]):
#         text_edits: list[QLineEdit] = []
        
#         for index, placeholder in enumerate(placeholders):
#             edit = QLineEdit()
#             edit.setPlaceholderText(placeholder)
#             edit.setFixedHeight(80)
#             edit.setStyleSheet("font-size: 40px;")
            
#             self.info[_id]["text"].append("")
            
#             edit.textChanged.connect(self.make_store_edit_func(_id, edit, index))
            
#             text_edits.append(edit)
        
#         return text_edits
    
#     def make_action_buttons(self, _id: str, layout: QHBoxLayout):
#         classes_button = QPushButton("Classes")
#         teachers_button = QPushButton("Teachers")
        
#         teachers_button.setFixedWidth(100)
#         classes_button.setFixedWidth(100)
        
#         classes_button.setProperty('class', 'action')
#         teachers_button.setProperty('class', 'action')
        
#         classes_button.clicked.connect(self.make_show_popup_1(_id))
#         teachers_button.clicked.connect(self.make_show_popup_2(_id))
        
#         layout.addWidget(classes_button)
#         layout.addWidget(teachers_button, alignment=Qt.AlignmentFlag.AlignLeft)
    
#     def make_show_popup_1(self, _id: str):
#         def show_popup_1():
#             classes_list = DropDownCheckBoxes("Classes", self.info[_id]["classes"])
#             classes_list.exec()
#             self.info[_id]["classes"] = classes_list.get()
        
#         return show_popup_1
    
#     def make_show_popup_2(self, _id: str):
#         def show_popup_2():
#             teachers_list = SelectionList("Teachers", self.info[_id]["teachers"])
#             teachers_list.exec()
            
#             self.info[_id]["teachers"] = teachers_list.get()
        
#         return show_popup_2


# class Teachers(Subjects):
#     def __init__(self):
#         super().__init__()
        
#         self.subject = [None]
#         self.setObjectName("teacher")
    
#     def make_action_buttons(self, widget: QWidget, layout: QHBoxLayout):
#         subjects_button = QPushButton("Subjects")
        
#         subjects_button.setProperty('class', 'action')
        
#         subjects_button.clicked.connect(self.make_show_popup_1(widget))
        
#         subjects_button.setFixedWidth(200)
        
#         layout.addWidget(subjects_button, alignment=Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
    
#     def make_show_popup_1(self, _id: str):
#         def show_popup_1():
#             subjects_list = SelectionList("Subjects", self.info[_id]["subjects"])
#             subjects_list.exec()
            
#             self.info[_id]["subjects"] = subjects_list.get()
        
#         return show_popup_1
    
#     def set_info(self, _id: str):
#         self.info[_id] = {"text": "", "subjects": {"content": self.subject.copy(), "id_mapping": self.id_mapping.copy()}}


# class Classes(QWidget):
#     def __init__(self):
#         super().__init__()
        
#         self.subject_teachers_mapping = {}
        
#         self.main_layout = QVBoxLayout(self)
        
#         self.scroll_area = QScrollArea()
#         self.scroll_area.setWidgetResizable(True)
        
#         self.container = QWidget()
#         self.container_layout = QVBoxLayout(self.container)
#         self.container_layout.addStretch()
#         self.scroll_area.setWidget(self.container)
        
#         self.add_button = QPushButton("Add Class")
#         self.add_button.clicked.connect(self.add)
        
#         self.main_layout.addWidget(self.scroll_area)
#         self.main_layout.addWidget(self.add_button, alignment=Qt.AlignmentFlag.AlignRight)
        
#         self.info = {}
        
#         self.setLayout(self.main_layout)
        
#         self.setStyleSheet(THEME[SUBJECT_TEACHERS_CLASSES])
    
#     def keyPressEvent(self, a0):
#         if a0.key() == 16777220:
#             self.add()
        
#         return super().keyPressEvent(a0)
    
#     def get(self):
#         return self.info
    
#     def add(self):
#         widget = QWidget()
#         widget.setObjectName("itemContainer")
#         widget.setMaximumHeight(150)
        
#         layout = QVBoxLayout()
#         widget.setLayout(layout)
        
#         header_layout = QVBoxLayout()
        
#         name_edit = QLineEdit()
#         name_edit.setPlaceholderText("Enter Class Name")
#         name_edit.setFixedHeight(80)
#         name_edit.setStyleSheet("font-size: 40px;")
        
#         _id = widget.__repr__()
        
#         name_edit.textChanged.connect(self.make_clicked_func(_id, name_edit))
        
#         delete_button = QPushButton("×")
#         delete_button.setProperty('class', 'warning')
#         delete_button.clicked.connect(self._make_delete_func(_id, widget))
#         delete_button.setFixedSize(30, 30)
#         delete_button.setStyleSheet("padding: 3px;")
        
#         header_layout.addWidget(name_edit)
        
#         buttons_layout = QHBoxLayout()
        
#         main_buttons_layout = QHBoxLayout()
        
#         subjects_button = QPushButton("Subjects")
#         options_button = QPushButton("Options")
#         subjects_button.setFixedWidth(100)
#         options_button.setFixedWidth(100)
        
#         subjects_button.setProperty('class', 'action')
#         options_button.setProperty('class', 'action')
        
#         subjects_button.clicked.connect(self.make_show_subjects_popup_func(_id))
#         options_button.clicked.connect(self.make_show_options_popup_func(_id))
        
#         main_buttons_layout.addWidget(options_button)
#         main_buttons_layout.addWidget(subjects_button, alignment=Qt.AlignmentFlag.AlignLeft)
        
#         buttons_layout.addLayout(main_buttons_layout)
#         buttons_layout.addWidget(delete_button, alignment=Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignTop)
        
#         layout.addLayout(buttons_layout)
#         layout.addLayout(header_layout)
        
#         self.container_layout.insertWidget(0, widget, alignment=Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignVCenter)
        
#         self.set_info(_id)
        
#         name_edit.show()
#         name_edit.setFocus()
    
#     def set_info(self, _id: str):
#         self.info[_id] = {"text": "", "options": {}, "subjects": {"content": {}, "id_mapping": {index : index_id for index, (index_id, _) in enumerate(self.subject_teachers_mapping.items())}}}
    
#     def _make_delete_func(self, _id: str, widget: QWidget):
#         def del_widget():
#             delete_button = self.sender()
#             delete_button.setProperty('class', 'warning')
#             self.container_layout.removeWidget(widget)
#             widget.deleteLater()
#             self.info.pop(_id)
        
#         return del_widget
    
#     def make_clicked_func(self, _id: str, name_edit: QLineEdit):
#         def clicked():
#             info_entry = self.info[_id]
#             info_entry["text"] = name_edit.text()
        
#         return clicked
    
#     def make_show_subjects_popup_func(self, _id: str):
#         def show_subjects_popup():
#             subjects = SubjectSelection("Subjects", self.subject_teachers_mapping, self.info[_id]["subjects"])
#             subjects.exec()
#             self.info[_id]["subjects"] = subjects.get()
        
#         return show_subjects_popup
    
#     def make_show_options_popup_func(self, _id: str):
#         def show_options_popup():
#             option_selector = OptionSelection("Options Selection", self.info[_id]["options"])
#             option_selector.exec()
#             self.info[_id]["options"] = option_selector.get()
        
#         return show_options_popup


