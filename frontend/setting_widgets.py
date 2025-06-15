from copy import deepcopy
from typing import Callable
from frontend.sub_widgets import (
    SelectionList, DropDownCheckBoxes, SubjectSelection,
    OptionSelection
)
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QLineEdit, QPushButton, QScrollArea,
    QMainWindow
)
from PyQt6.QtCore import Qt
from frontend.theme import *


class SettingWidget(QWidget):
    def __init__(self, name: str, input_placeholders: list[str], data: dict | None = None):
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
        
        if data is not None:
            self.__dict__.update(data["constants"])
            
            for _id, values in data["variables"].items():
                self.add(self.input_placeholders, _id, values)
    
    def keyPressEvent(self, a0):
        if a0.key() == 16777220:
            self.add(self.input_placeholders)
        return super().keyPressEvent(a0)
    
    def get(self):
        return self.info
    
    def get_constants(self):
        return {}
    
    def add(self, input_placeholders: list[str], _id: str | None = None, data: dict | None = None):
        widget = QWidget()
        widget.setObjectName("itemContainer")
        widget.setMaximumHeight(150)
        
        layout = QVBoxLayout()
        widget.setLayout(layout)
        
        header_layout = QHBoxLayout()
        buttons_layout = QHBoxLayout()
        
        _id = str(widget) if _id is None else _id
        # _id = self.objectName() + ": " + str(len(self.info) + 1) if _id is None else _id
        
        if data is None:
            self.add_id_to_info(_id)
        else:
            self.set_id_data_to_info(_id, data)
        
        text_edits = self._make_inputs(_id, input_placeholders, data)
        
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
    
    def set_id_data_to_info(self, _id: str, data: dict):
        self.info[_id] = data
    
    def add_id_to_info(self, _id: str, info_value: dict):
        pass
    
    def update_data_interaction(self, parent: QMainWindow, prev_index: int, curr_index: int):
        pass
    
    def _make_store_edit_func(self, _id: str, edit: QLineEdit, index: int):
        def store_text_data():
            self.info[_id]["text"][index] = edit.text()
        
        return store_text_data
    
    def _make_inputs(self, _id: str, placeholders: list[str], data: dict | None):
        text_edits: list[QLineEdit] = []
        
        for index, placeholder in enumerate(placeholders):
            text = data["text"][index] if data is not None else ""
            
            edit = QLineEdit(text)
            edit.setPlaceholderText(placeholder)
            edit.setFixedHeight(80)
            edit.setStyleSheet("font-size: 40px;")
            
            self.info[_id]["text"].append(text)
            
            edit.textChanged.connect(self._make_store_edit_func(_id, edit, index))
            
            text_edits.append(edit)
        
        return text_edits
    
    def _make_delete_func(self, _id: str, widget: QWidget):
        def del_widget():
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
    def __init__(self, save_data: dict | None):
        super().__init__("Subjects", ["Enter the subject name"], save_data)
        self.teachers = [None]
    
    def update_data_interaction(self, parent, prev_index, curr_index):
        general_condition = prev_index != 3 and not (curr_index == 3 and prev_index != 0)
        if not general_condition:
            return
        
        teacher_update_condition = (prev_index == 1 and curr_index == 0) or (curr_index == 2 and prev_index == 1)
        class_update_condition = (prev_index == 2 and curr_index == 0) or (curr_index == 1 and prev_index == 2)
        
        subject_info = parent.subjects_widget.get()
        teacher_info = parent.teachers_widget.get()
        class_info = parent.classes_widget.get()
        
        if teacher_update_condition:
            # Update Teachers
            teachers = [None]
            id_mapping = {}
            
            for teacher_index, (teacher_id, teacher_info_entry) in enumerate(teacher_info.items()):
                teacher_name = " ".join(teacher_info_entry["text"])
                
                teachers.append(teacher_name)
                id_mapping[teacher_index + 1] = teacher_id
            
            parent.subjects_widget.teachers = teachers
            parent.subjects_widget.id_mapping = id_mapping
            
            for teacher_index, (teacher_id, teacher_info_entry) in enumerate(teacher_info.items()):
                teacher_subject_index_id_mapping = dict(
                    zip(
                        list(teacher_info_entry["subjects"]["id_mapping"].values()),
                        list(teacher_info_entry["subjects"]["id_mapping"].keys())
                        )
                    )
                
                for index, (subject_id, subject_info_entry) in enumerate(subject_info.items()):
                    subject_teacher_index_id_mapping = dict(zip(list(subject_info_entry["teachers"]["id_mapping"].values()), list(subject_info_entry["teachers"]["id_mapping"].keys())))
                    
                    teacher_index_in_subject = subject_teacher_index_id_mapping.get(teacher_id)
                    subject_index_in_teacher = teacher_subject_index_id_mapping[subject_id]  # The teaacher must always be in the teacher list, if not there is a problem
                    
                    if teacher_index_in_subject is None:
                        teacher_index_in_subject = len(subject_info_entry["teachers"]["content"])
                        teacher_name = " ".join(teacher_info_entry["text"])
                        
                        subject_info_entry["teachers"]["content"].append(teacher_name)
                        subject_info_entry["teachers"]["id_mapping"][teacher_index_in_subject] = teacher_id
                        subject_teacher_index_id_mapping[teacher_id] = teacher_index_in_subject
                    
                    subject_none_index_in_teacher = teacher_info_entry["subjects"]["content"].index(None)
                    teacher_none_index_in_subject = subject_info_entry["teachers"]["content"].index(None)
                    
                    is_teacher_selected_in_subject = teacher_index_in_subject < teacher_none_index_in_subject
                    is_subject_selected_in_teacher = subject_index_in_teacher < subject_none_index_in_teacher
                    
                    if is_teacher_selected_in_subject != is_subject_selected_in_teacher:
                        curr_subject_value = subject_info_entry["teachers"]["content"].pop(teacher_index_in_subject)
                        curr_teacher_id = subject_info_entry["teachers"]["id_mapping"][teacher_index_in_subject]
                        
                        if is_subject_selected_in_teacher and not is_teacher_selected_in_subject:
                            # Make is selected in the subject editor
                            for i in range(teacher_index_in_subject - teacher_none_index_in_subject - 1):
                                j = teacher_index_in_subject - i
                                subject_info_entry["teachers"]["id_mapping"][j] = subject_info_entry["teachers"]["id_mapping"][j - 1]
                            
                            subject_info_entry["teachers"]["id_mapping"][teacher_none_index_in_subject] = curr_teacher_id
                            subject_info_entry["teachers"]["id_mapping"].pop(teacher_none_index_in_subject + 1)
                            
                            subject_info_entry["teachers"]["content"].insert(teacher_none_index_in_subject, curr_subject_value)
                        elif not is_subject_selected_in_teacher and is_teacher_selected_in_subject:
                            # Make is unselected in the subject editor
                            for i in range(len(subject_info_entry["teachers"]["content"]) - teacher_index_in_subject):
                                j = teacher_index_in_subject + i
                                if j + 1 in subject_info_entry["teachers"]["id_mapping"]:
                                    subject_info_entry["teachers"]["id_mapping"][j] = subject_info_entry["teachers"]["id_mapping"][j + 1]
                                else:
                                    subject_info_entry["teachers"]["id_mapping"].pop(j)
                            
                            subject_info_entry["teachers"]["id_mapping"][len(subject_info_entry["teachers"]["content"])] = curr_teacher_id
                            subject_info_entry["teachers"]["content"].append(curr_subject_value)
            
            for i, (subject_id, subject_info_entry) in enumerate(subject_info.items()):
                subject_teacher_index_id_mapping = dict(
                    zip(
                        list(subject_info_entry["teachers"]["id_mapping"].values()),
                        list(subject_info_entry["teachers"]["id_mapping"].keys())
                        )
                    )
                
                for index_id, index in subject_teacher_index_id_mapping.items():
                    if index_id not in teacher_info:
                        for i in range(len(subject_info_entry["teachers"]["id_mapping"]) - index):
                            j = index + i
                            
                            if j + 1 in subject_info_entry["teachers"]["id_mapping"]:
                                subject_info_entry["teachers"]["id_mapping"][j] = subject_info_entry["teachers"]["id_mapping"][j + 1]
                            else:
                                subject_info_entry["teachers"]["id_mapping"].pop(j)
                        
                        for i_id, i in subject_teacher_index_id_mapping.items():
                            if i > index:
                                subject_teacher_index_id_mapping[i_id] -= 1
                        subject_info_entry["teachers"]["content"].pop(index)
                        subject_info_entry["teachers"]["id_mapping"].pop(len(subject_info_entry["teachers"]["id_mapping"]))
                
                for index, index_id in subject_info_entry["teachers"]["id_mapping"].items():
                    teacher_name = " ".join(teacher_info[index_id]["text"])
                    subject_info_entry["teachers"]["content"][index] = teacher_name
        
        if class_update_condition:
            # Update Classes
            for class_id, class_info_entry in deepcopy(class_info).items():
                for subject_id, _ in class_info_entry["subjects"]["content"].items():
                    subject_info[subject_id]["classes"]["id_mapping"]["main"][class_id] = class_info_entry["text"][0]
                    subject_info[subject_id]["classes"]["id_mapping"]["sub"][class_id] = class_info_entry["options"]
                    subject_info[subject_id]["classes"]["content"][class_id] = {option_id : (
                        (
                            subject_info[subject_id]["classes"]["content"][class_id].get(option_id)
                            if subject_info[subject_id]["classes"]["content"][class_id].get(option_id) is None else
                            False
                        ) if subject_info[subject_id]["classes"]["content"].get(class_id) is not None else
                        False
                    ) for option_id, _ in class_info_entry["options"].items()}
        
        parent.subjects_widget.info = subject_info
    
    def add_id_to_info(self, _id):
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
    
    def get_constants(self):
        return {
            "teachers": self.teachers,
            "id_mapping": self.id_mapping
        }
    
    def make_popups(self, _id, layout):
        self._make_popup(_id, "Classes", layout, DropDownCheckBoxes, "classes")
        self._make_popup(_id, "Teachers", layout, SelectionList, "teachers", alignment=Qt.AlignmentFlag.AlignLeft)

class Teachers(SettingWidget):
    def __init__(self, save_data: dict | None):
        super().__init__("Teachers", ["Full name"], save_data)
        self.subjects = [None]
    
    def update_data_interaction(self, parent, prev_index, curr_index):
        if not ((prev_index == 0 and curr_index in (1, 2)) or (curr_index == 3 and prev_index != 1)) or prev_index == 3:
            return
        
        teacher_info = parent.teachers_widget.get()
        subject_info = parent.subjects_widget.get()
        
        subjects = [None]
        id_mapping = {}
        
        for subject_index, (subject_id, subject_info_entry) in enumerate(subject_info.items()):
            subject_name = " ".join(subject_info_entry["text"])
            
            subjects.append(subject_name)
            id_mapping[subject_index + 1] = subject_id
        
        parent.teachers_widget.subjects = subjects
        parent.teachers_widget.id_mapping = id_mapping
        
        for subject_index, (subject_id, subject_info_entry) in enumerate(subject_info.items()):
            subject_teacher_index_id_mapping = dict(
                zip(
                    list(subject_info_entry["teachers"]["id_mapping"].values()),
                    list(subject_info_entry["teachers"]["id_mapping"].keys())
                    )
                )
            
            for index, (teacher_id, teacher_info_entry) in enumerate(teacher_info.items()):
                teacher_subject_index_id_mapping = dict(zip(list(teacher_info_entry["subjects"]["id_mapping"].values()), list(teacher_info_entry["subjects"]["id_mapping"].keys())))
                
                subject_index_in_teacher = teacher_subject_index_id_mapping.get(subject_id)
                teacher_index_in_subject = subject_teacher_index_id_mapping[teacher_id]  # The teaacher must always be in the subject list, if not there is a problem
                
                if subject_index_in_teacher is None:
                    subject_index_in_teacher = len(teacher_info_entry["subjects"]["content"])
                    subject_name = " ".join(subject_info_entry["text"])
                    
                    teacher_info_entry["subjects"]["content"].append(subject_name)
                    teacher_info_entry["subjects"]["id_mapping"][subject_index_in_teacher] = subject_id
                    teacher_subject_index_id_mapping[subject_id] = subject_index_in_teacher
                
                teacher_none_index_in_subject = subject_info_entry["teachers"]["content"].index(None)
                subject_none_index_in_teacher = teacher_info_entry["subjects"]["content"].index(None)
                
                is_subject_selected_in_teacher = subject_index_in_teacher < subject_none_index_in_teacher
                is_teacher_selected_in_subject = teacher_index_in_subject < teacher_none_index_in_subject
                
                if is_subject_selected_in_teacher != is_teacher_selected_in_subject:
                    curr_teacher_value = teacher_info_entry["subjects"]["content"].pop(subject_index_in_teacher)
                    curr_subject_id = teacher_info_entry["subjects"]["id_mapping"][subject_index_in_teacher]
                    
                    if not is_subject_selected_in_teacher:
                        # Make is selected in the teacher editor
                        for i in range(subject_index_in_teacher - subject_none_index_in_teacher - 1):
                            j = subject_index_in_teacher - i
                            teacher_info_entry["subjects"]["id_mapping"][j] = teacher_info_entry["subjects"]["id_mapping"][j - 1]
                        
                        teacher_info_entry["subjects"]["id_mapping"][subject_none_index_in_teacher] = curr_subject_id
                        teacher_info_entry["subjects"]["id_mapping"].pop(subject_none_index_in_teacher + 1)
                        
                        teacher_info_entry["subjects"]["content"].insert(subject_none_index_in_teacher, curr_teacher_value)
                    elif not is_teacher_selected_in_subject:
                        # Make is unselected in the teacher editor
                        for i in range(len(teacher_info_entry["subjects"]["content"]) - subject_index_in_teacher):
                            j = subject_index_in_teacher + i
                            
                            if j + 1 in teacher_info_entry["subjects"]["id_mapping"]:
                                teacher_info_entry["subjects"]["id_mapping"][j] = teacher_info_entry["subjects"]["id_mapping"][j + 1]
                            else:
                                teacher_info_entry["subjects"]["id_mapping"].pop(j)
                        
                        teacher_info_entry["subjects"]["id_mapping"][len(teacher_info_entry["subjects"]["content"])] = curr_subject_id
                        teacher_info_entry["subjects"]["content"].append(curr_teacher_value)
        
        for teacher_id, teacher_info_entry in teacher_info.items():
            teacher_subject_index_id_mapping = dict(
                zip(
                    list(teacher_info_entry["subjects"]["id_mapping"].values()),
                    list(teacher_info_entry["subjects"]["id_mapping"].keys())
                    )
                )
            
            for index_id, index in teacher_subject_index_id_mapping.items():
                if index_id not in subject_info:
                    for i in range(len(teacher_info_entry["subjects"]["id_mapping"]) - index):
                        j = index + i
                        
                        if j + 1 in teacher_info_entry["subjects"]["id_mapping"]:
                            teacher_info_entry["subjects"]["id_mapping"][j] = teacher_info_entry["subjects"]["id_mapping"][j + 1]
                        else:
                            teacher_info_entry["subjects"]["id_mapping"].pop(j)
                    
                    for i_id, i in teacher_subject_index_id_mapping.items():
                        if i > index:
                            teacher_subject_index_id_mapping[i_id] -= 1
                    teacher_info_entry["subjects"]["content"].pop(index)
                    teacher_info_entry["subjects"]["id_mapping"].pop(len(teacher_info_entry["subjects"]["id_mapping"]))
            
            for index, index_id in teacher_info_entry["subjects"]["id_mapping"].items():
                subject_name = " ".join(subject_info[index_id]["text"])
                teacher_info_entry["subjects"]["content"][index] = subject_name
        
        parent.teachers_widget.info = teacher_info
    
    def add_id_to_info(self, _id: str):
        self.info[_id] = {
            "text": [],
            "subjects": {
                "content": deepcopy(self.subjects),
                "id_mapping": deepcopy(self.id_mapping)
            }
        }
    
    def get_constants(self):
        return {
            "subjects": self.subjects,
            "id_mapping": self.id_mapping
        }
    
    def make_popups(self, _id, layout):
        self._make_popup(_id, "Subjects", layout, SelectionList, "subjects", alignment=Qt.AlignmentFlag.AlignLeft)

class Classes(SettingWidget):
    def __init__(self, save_data: dict | None):
        super().__init__("Classes", ["Enter the class section name"], save_data)
        
        self.subject_teachers_mapping = {}
        
        self.default_per_day = 2
        self.default_per_week = 4
    
    def update_data_interaction(self, parent, prev_index, curr_index):
        if prev_index in (2, 3):
            return
        
        subject_info = parent.subjects_widget.get()
        class_info = parent.classes_widget.get()
        teacher_info = parent.teachers_widget.get()
        
        subject_teacher_mapping = {}
        for subject_index, (subject_id, subject_info_entry) in enumerate(subject_info.items()):
            subject_teacher_info = deepcopy(subject_info_entry["teachers"])
            teacher_none_index_in_subjects = subject_teacher_info["content"].index(None)
            
            selecteds_teacher_subject_id_mapping = {index + 1 : index_id for index, index_id in subject_teacher_info["id_mapping"].items() if index < teacher_none_index_in_subjects}
            
            subject_teacher_mapping[subject_id] = {"name": subject_info_entry["text"][0], "teachers": {
                "content": [None] + subject_teacher_info["content"][:teacher_none_index_in_subjects],
                "id_mapping": selecteds_teacher_subject_id_mapping,
            }}
            
            for _, class_info_entry in class_info.items():
                class_subject_content = class_info_entry["subjects"]["content"].get(subject_id)
                
                if class_subject_content is not None:
                    selected_teachers_ids = selecteds_teacher_subject_id_mapping.values()
                    
                    if sorted(class_subject_content["teachers"]["id_mapping"].values()) != sorted(selected_teachers_ids):
                        class_subject_teacher_content = class_subject_content["teachers"]["content"]
                        class_subject_teacher_id_mapping = class_subject_content["teachers"]["id_mapping"]
                        
                        class_subject_teacher_id_mapping_inv = {index_id: index for index, index_id in class_subject_teacher_id_mapping.items()}
                        
                        # Remove un-removed teachers
                        for _, teacher_id in {k: v for k, v in class_subject_teacher_id_mapping.items()}.items():
                            if teacher_id not in selected_teachers_ids:
                                teacher_index = class_subject_teacher_id_mapping_inv[teacher_id]
                                
                                class_subject_teacher_content.pop(teacher_index)
                                
                                for i in range(len(class_subject_teacher_content) - teacher_index):
                                    j = teacher_index + i
                                    
                                    if j + 1 in class_subject_teacher_id_mapping:
                                        class_subject_teacher_id_mapping[j] = class_subject_teacher_id_mapping[j + 1]
                                    else:
                                        class_subject_teacher_id_mapping.pop(j)
                                
                                class_subject_teacher_id_mapping.pop(len(class_subject_teacher_content))
                            
                            class_subject_teacher_id_mapping_inv = {index_id: index for index, index_id in class_subject_teacher_id_mapping.items()}
                        
                        # Add un-added teachers
                        for teacher_id in selected_teachers_ids:
                            if teacher_id not in class_subject_teacher_id_mapping_inv:
                                class_subject_teacher_id_mapping[len(class_subject_teacher_content)] = teacher_id
                                class_subject_teacher_content.append(teacher_info[teacher_id]["text"][0])
                else:
                    class_info_entry["subjects"]["id_mapping"][subject_index] = subject_id
        
        for _, class_info_entry in class_info.items():
            class_info_entry["subjects"]["available_subject_teachers"] = subject_teacher_mapping
        
        for subject_index, (subject_id, _) in enumerate(parent.classes_widget.subject_teachers_mapping.items()):
            if subject_id not in subject_info:
                for _, class_info_entry in class_info.items():
                    class_info_entry["subjects"]["content"].pop(subject_id)
                    class_info_entry["subjects"]["id_mapping"].pop(subject_index)
        
        parent.classes_widget.info = class_info
        parent.classes_widget.subject_teachers_mapping = subject_teacher_mapping
    
    def add_id_to_info(self, _id: str):
        self.info[_id] = {
            "text": [],
            "options": {},
            "subjects": {
                "content": {},
                "id_mapping": {index : index_id for index, (index_id, _) in enumerate(deepcopy(self.subject_teachers_mapping).items())},
                "available_subject_teachers": self.subject_teachers_mapping
            }
        }
    
    def get_constants(self):
        return {
            "subject_teachers_mapping": self.subject_teachers_mapping
        }
    
    def make_popups(self, _id, layout):
        self._make_popup(_id, "Option Selector", layout, OptionSelection, "options", button_name="Options")
        self._make_popup(_id, "Subjects", layout, SubjectSelection, "subjects", alignment=Qt.AlignmentFlag.AlignLeft, default_per_day=self.default_per_day, default_per_week=self.default_per_week)


