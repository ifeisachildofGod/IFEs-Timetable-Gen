from copy import deepcopy
import random
from typing import Callable
from frontend.sub_widgets import (
    SelectionList, SubjectDropDownCheckBoxes, SubjectSelection,
    OptionSelection, TeacherDropDownCheckBoxes
)
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QLineEdit, QPushButton, QScrollArea,
    QMainWindow
)
from PyQt6.QtCore import Qt, pyqtSignal, pyqtBoundSignal

class SettingWidget(QWidget):
    def __init__(self, main_window: QMainWindow, name: str, input_placeholders: list[str], saved_state_changed: pyqtBoundSignal, data: dict | None = None):
        super().__init__()
        self.main_window = main_window
        
        self.setProperty("class", "SettingOptionEntry")
        self.objectNameChanged.connect(lambda: self.add_button.setText(f"Add {self.objectName().title()}"))
        
        self.info = {}
        self.id_mapping = {}
        self.input_placeholders = input_placeholders
        self.saved_state_changed = saved_state_changed
        
        self.main_layout = QVBoxLayout(self)
        
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        
        self.container = QWidget()
        self.container_layout = QVBoxLayout(self.container)
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
        
        self.scroll_area.verticalScrollBar().setValue(0)
    
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
        
        _id = str(hex(id(widget)).upper()) if _id is None else _id
        
        if data is None:
            self.add_id_to_info(_id)
        else:
            self.info[_id] = data
        
        text_edits = self._make_inputs(_id, input_placeholders, data)
        
        delete_button = QPushButton("×")
        delete_button.setProperty('class', 'Close')
        delete_button.clicked.connect(self._make_delete_func(_id, widget))
        delete_button.setFixedSize(30, 30)
        
        for edit in text_edits:
            header_layout.addWidget(edit)
        
        self.make_popups(_id, buttons_layout)
        buttons_layout.addWidget(delete_button, alignment=Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignTop)
        
        layout.addLayout(buttons_layout)
        layout.addLayout(header_layout)
        
        self.container_layout.insertWidget(len(self.info) - 1, widget, alignment=Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignVCenter)
        
        for edit in text_edits:
            edit.show()
        text_edits[0].setFocus()
        
        self.scroll_area.update()
        self.scroll_area.verticalScrollBar().setValue(self.scroll_area.verticalScrollBar().maximum())
        
    def make_popups(self, _id: str, layout: QHBoxLayout):
        pass
    
    def add_id_to_info(self, _id: str, info_value: dict):
        pass
    
    def update_data_interaction(self, prev_index: int, curr_index: int):
        pass
    
    def _make_inputs(self, _id: str, placeholders: list[str], data: dict | None):
        text_edits: list[QLineEdit] = []
        
        for index, placeholder in enumerate(placeholders):
            text = data["text"][index] if data is not None else ""
            
            edit = QLineEdit(text)
            edit.setPlaceholderText(placeholder)
            edit.setFixedHeight(80)
            
            if data is None:
                self.info[_id]["text"].append(text)
            
            edit.textChanged.connect(self._make_text_changed_func(_id, index))
            
            text_edits.append(edit)
        
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
            self.info.pop(_id)
        
        return del_widget
    
    def _make_popup(self, _id: str, title: str, layout: QHBoxLayout, popup_class: type[SelectionList] | type[SubjectSelection] | type[OptionSelection] | type[SubjectDropDownCheckBoxes], var_name: str, button_name: str | None = None, closed_func: Callable[[str], None] | None = None, alignment: Qt.AlignmentFlag = None, *args, **kwargs):
        button = QPushButton(button_name if button_name is not None else title)
        
        button.setFixedWidth(100)
        button.setProperty('class', 'action')
        button.clicked.connect(self._make_popup_func(_id, title, popup_class, var_name, closed_func, *args, **kwargs))
        
        if alignment is not None:
            layout.addWidget(button, alignment=alignment)
        else:
            layout.addWidget(button)
    
    def _make_popup_func(self, _id: str, title: str, popup_class: type[SelectionList] | type[SubjectSelection] | type[OptionSelection] | type[SubjectDropDownCheckBoxes], var_name: str, closed_func: Callable[[str], None] | None, *args, **kwargs):
        def show_popup():
            popup = popup_class(title=title, info=self.info[_id].get(var_name, {}), saved_state_changed=self.saved_state_changed, *args, **kwargs)
            
            popup.exec()
            self.info[_id][var_name] = popup.get()
            
            if closed_func is not None:
                closed_func(_id)
        
        return show_popup


class Subjects(SettingWidget):
    def __init__(self, main_window: QMainWindow, save_data: dict | None, saved_state_changed):
        self.teachers = [None]
        self.classes_data = {"content": {}, "id_mapping": {"main": {}, "sub": {}}}
        
        super().__init__(main_window, "Subjects", ["Enter the subject name"], saved_state_changed, save_data)
    
    def update_data_interaction(self, prev_index, curr_index):
        general_condition = prev_index != 3 and not (curr_index == 3 and prev_index != 0)
        if not general_condition:
            return
        
        teacher_update_condition = (prev_index == 1 and curr_index == 0) or (curr_index == 2 and prev_index == 1)
        class_update_condition = (prev_index == 2 and curr_index == 0) or (curr_index == 1 and prev_index == 2)
        
        teacher_info = self.main_window.teachers_widget.get()
        
        if teacher_update_condition:
            # Update Teachers
            teachers = [None]
            id_mapping = {}
            
            for teacher_index, (teacher_id, teacher_info_entry) in enumerate(teacher_info.items()):
                teacher_name = " ".join(teacher_info_entry["text"])
                
                teachers.append(teacher_name)
                id_mapping[teacher_index + 1] = teacher_id
            
            self.main_window.subjects_widget.teachers = teachers
            self.main_window.subjects_widget.id_mapping = id_mapping
            
            for teacher_index, (teacher_id, teacher_info_entry) in enumerate(teacher_info.items()):
                teacher_subject_index_id_mapping = dict(
                    zip(
                        list(teacher_info_entry["subjects"]["id_mapping"].values()),
                        list(teacher_info_entry["subjects"]["id_mapping"].keys())
                        )
                    )
                
                for index, (subject_id, subject_info_entry) in enumerate(self.info.items()):
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
            
            for subject_id, subject_info_entry in self.info.items():
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
            self.update_classes()
    
    def add_id_to_info(self, _id):
        self.info[_id] = {
            "text": [],
            "classes": {},
            "teachers": {
                "content": deepcopy(self.teachers),
                "id_mapping": deepcopy(self.id_mapping)
            }
        }
    
    def get_constants(self):
        return {
            "teachers": self.teachers,
            "id_mapping": self.id_mapping,
            "classes_data": self.classes_data
        }
    
    def make_popups(self, _id, layout):
        self._make_popup(_id, "Classes", layout, SubjectDropDownCheckBoxes, "classes", general_data=self.classes_data)
        self._make_popup(_id, "Teachers", layout, SelectionList, "teachers", alignment=Qt.AlignmentFlag.AlignLeft)
    
    def update_classes(self):
        class_info = self.main_window.classes_widget.get()
        
        self.classes_data["content"] = {}
        
        self.classes_data["id_mapping"]["main"] = {}
        self.classes_data["id_mapping"]["sub"] = {}
        
        for class_id, class_info_entry in class_info.items():
            self.classes_data["content"][class_id] = dict.fromkeys(class_info_entry["options"], False)
            
            self.classes_data["id_mapping"]["main"][class_id] = class_info_entry["text"][0]
            self.classes_data["id_mapping"]["sub"][class_id] = class_info_entry["options"].copy()
        
        for subject_data_entry in self.info.values():
            for class_id, options_data in subject_data_entry["classes"].copy().items():
                if class_id not in class_info:
                    subject_data_entry.pop(class_id)
                    continue
                
                for option_id in options_data.copy():
                    if option_id not in class_info[class_id]["options"]:
                        options_data.pop(option_id)

class Teachers(SettingWidget):
    def __init__(self, main_window: QMainWindow, save_data: dict | None, saved_state_changed):
        self.subjects = [None]
        self.all_subject_classes_info = {}
        
        super().__init__(main_window, "Teachers", ["Full name"], saved_state_changed, save_data)
    
    def update_data_interaction(self, prev_index, curr_index):
        if not ((prev_index == 0 and curr_index in (1, 2)) or (curr_index == 3 and prev_index != 1)) or prev_index == 3:
            return
        class_update_condition = prev_index in (0, 2)
        
        subject_info = self.main_window.subjects_widget.get()
        
        subjects = [None]
        id_mapping = {}
        
        for subject_index, (subject_id, subject_info_entry) in enumerate(subject_info.items()):
            subject_name = " ".join(subject_info_entry["text"])
            
            subjects.append(subject_name)
            id_mapping[subject_index + 1] = subject_id
        
        self.main_window.teachers_widget.subjects = subjects
        self.main_window.teachers_widget.id_mapping = id_mapping
        
        for subject_index, (subject_id, subject_info_entry) in enumerate(subject_info.items()):
            subject_teacher_index_id_mapping = dict(
                zip(
                    list(subject_info_entry["teachers"]["id_mapping"].values()),
                    list(subject_info_entry["teachers"]["id_mapping"].keys())
                    )
                )
            
            for index, (teacher_id, teacher_info_entry) in enumerate(self.info.items()):
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
        
        for teacher_id, teacher_info_entry in self.info.items():
            teacher_subject_index_id_mapping = {v: k for k, v in teacher_info_entry["subjects"]["id_mapping"].items()}
            
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
                
            if class_update_condition:
                self._update_classes(teacher_id)
    
    def add_id_to_info(self, _id: str):
        self.info[_id] = {
            "text": [],
            "classes": {"content": {}, "id_mapping": {}},
            "subjects": {
                "content": deepcopy(self.subjects),
                "id_mapping": deepcopy(self.id_mapping)
            }
        }
    
    def get_constants(self):
        return {
            "subjects": self.subjects,
            "id_mapping": self.id_mapping,
            "all_subject_classes_info": self.all_subject_classes_info
        }
    
    def make_popups(self, _id, layout):
        self._make_popup(_id, "Classes", layout, TeacherDropDownCheckBoxes, "classes", general_data=self.all_subject_classes_info)
        self._make_popup(_id, "Subjects", layout, SelectionList, "subjects", closed_func=self._update_classes, alignment=Qt.AlignmentFlag.AlignLeft)
    
    def _update_classes(self, _id):
        subject_info = self.main_window.subjects_widget.get()
        subject_general_data = self.main_window.subjects_widget.classes_data
        
        selected_subjects_data = {index_id: index for index, index_id in self.info[_id]["subjects"]["id_mapping"].items() if index < self.info[_id]["subjects"]["content"].index(None)}
        
        teacher_subject_class_content_info = self.info[_id]["classes"]["content"]
        teacher_subject_class_id_mapping_info = self.info[_id]["classes"]["id_mapping"]
        
        # Updating generals
        for subject_id in selected_subjects_data:
            if subject_id not in teacher_subject_class_content_info:
                teacher_subject_class_content_info[subject_id] = {}
                teacher_subject_class_id_mapping_info[subject_id] = subject_info[subject_id]["text"][0]
            
            self.all_subject_classes_info[subject_id] = {"content": {}, "id_mapping": {"main": {}, "sub": {}}}
            
            for class_id, options_info in subject_info[subject_id]["classes"].items():
                self.all_subject_classes_info[subject_id]["content"][class_id] = [False, dict.fromkeys(options_info, False)]
                self.all_subject_classes_info[subject_id]["id_mapping"]["main"][class_id] = subject_general_data["id_mapping"]["main"][class_id]
                
                self.all_subject_classes_info[subject_id]["id_mapping"]["sub"][class_id] = {}
                for option_id in self.all_subject_classes_info[subject_id]["content"][class_id][1]:
                    self.all_subject_classes_info[subject_id]["id_mapping"]["sub"][class_id][option_id] =\
                        subject_general_data["id_mapping"]["sub"][class_id][option_id]
        
        # Removals
        for subject_id, subject_class_data in teacher_subject_class_content_info.copy().items():
            if subject_id not in selected_subjects_data:
                teacher_subject_class_content_info.pop(subject_id)
                teacher_subject_class_id_mapping_info.pop(subject_id)
                continue
            
            for class_id in subject_class_data.copy():
                if class_id not in subject_info[subject_id]["classes"]:
                    subject_class_data.pop(class_id)
                    continue
                
                for option_id in subject_class_data[class_id][1].copy():
                    if option_id not in subject_info[subject_id]["classes"][class_id]:
                        subject_class_data[class_id].pop(option_id)

class Classes(SettingWidget):
    def __init__(self, main_window: QMainWindow, save_data: dict | None, saved_state_changed):
        super().__init__(main_window, "Classes", ["Enter the class section name"], saved_state_changed, save_data)
    
    def update_data_interaction(self, prev_index, _):
        if prev_index in (2, 3):
            return
        
        subject_info = self.main_window.subjects_widget.get()
        
        for class_id, class_info_entry in self.info.items():
            for subject_id, subject_info_entry in subject_info.items():
                if class_id in subject_info_entry["classes"]:
                    default = [
                        _,
                        {
                            "per_day": str(self.main_window.default_per_day),
                            "per_week": str(self.main_window.default_per_week)
                        }
                    ]
                    
                    class_info_entry["subjects"][subject_id] = class_info_entry["subjects"].get(subject_id, default)
                    class_info_entry["subjects"][subject_id][0] = subject_info_entry["text"][0]
                elif subject_id in class_info_entry["subjects"]:
                    class_info_entry["subjects"].pop(subject_id)
            
            for subject_id in class_info_entry["subjects"].copy():
                if subject_id not in subject_info:
                    class_info_entry["subjects"].pop(subject_id)
    
    def add_id_to_info(self, _id: str):
        self.info[_id] = {
            "text": [],
            "options": {},
            "subjects": {}
        }
    
    def get_constants(self):
        return {}
    
    def make_popups(self, _id, layout):
        self._make_popup(_id, "Option Selector", layout, OptionSelection, "options", button_name="Options", closed_func=lambda _: self.main_window.subjects_widget.update_classes())
        self._make_popup(_id, "Subjects", layout, SubjectSelection, "subjects", alignment=Qt.AlignmentFlag.AlignLeft)


