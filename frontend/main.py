import random
import sys

import json
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout,
    QVBoxLayout, QPushButton, QStackedWidget,
    QMenuBar, QMessageBox
)
from PyQt6.QtGui import QIcon
from matplotlib.cbook import flatten
from frontend.setting_widgets import Subjects, Teachers, Classes
from frontend.editing_widgets import TimeTableEditor
from frontend.theme import *
from middle.main import School


args = sys.argv

class Window(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # Initialize school data
        self.default_weekdays = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
        
        with open("res/project.json") as file:
            self.project = json.loads(file.read())
        
        self.display_index = 0
        self.school = School(self.project)
        
        # Set application style
        self.setStyleSheet(THEME[WINDOW])
        
        menu_bar = QMenuBar(self)
        self.setMenuBar(menu_bar)
        
        self.file_action = menu_bar.addAction(QIcon(), "File", )
        self.edit_action = menu_bar.addAction(QIcon(), "Edit")
        self.window_action = menu_bar.addAction(QIcon(), "Window")
        
        menu_bar.setStyleSheet(menu_bar.styleSheet() + THEME[WINDOW_MENUBAR_ADDITION])
        
        self.setWindowTitle("IFEs Timetable Generator")
        self.setGeometry(100, 100, 1000, 700)
        
        # Create main container
        container = QWidget()
        main_layout = QHBoxLayout()
        container.setLayout(main_layout)
        
        # Create sidebar with modern styling
        sidebar = QWidget()
        sidebar.setFixedWidth(200)
        sidebar.setStyleSheet(THEME[WINDOW_SIDEBAR])
        
        # Create sidebar layout
        sidebar_layout = QVBoxLayout()
        sidebar_layout.setSpacing(0)
        sidebar_layout.setContentsMargins(0, 0, 0, 0)
        
        # Create stacked widget for content
        self.stack = QStackedWidget()
        
        # Create navigation buttons
        subjects_btn = QPushButton("Subjects")
        teachers_btn = QPushButton("Teachers")
        classes_btn = QPushButton("Classes")
        timetable_btn = QPushButton("Timetable")
        
        subjects_btn.setCheckable(True)
        teachers_btn.setCheckable(True)
        classes_btn.setCheckable(True)
        timetable_btn.setCheckable(True)
        
        # Add widgets to stack
        self.subjects_widget = Subjects()
        self.teachers_widget = Teachers()
        self.classes_widget = Classes()
        self.timetable_widget = TimeTableEditor(self.school)
        
        self.option_buttons = [subjects_btn, teachers_btn, classes_btn, timetable_btn]
        
        self.stack.addWidget(self.subjects_widget)
        self.stack.addWidget(self.teachers_widget)
        self.stack.addWidget(self.classes_widget)
        self.stack.addWidget(self.timetable_widget)
        
        # Connect buttons
        for index, button in enumerate(self.option_buttons):
            button.clicked.connect(self.make_option_button_func(index))
        
        # Add buttons to sidebar
        sidebar_layout.addWidget(subjects_btn)
        sidebar_layout.addWidget(teachers_btn)
        sidebar_layout.addWidget(classes_btn)
        sidebar_layout.addStretch()
        sidebar_layout.addWidget(timetable_btn)
        sidebar.setLayout(sidebar_layout)
        
        # Add widgets to main layout
        main_layout.addWidget(sidebar)
        main_layout.addWidget(self.stack)
        
        self.setCentralWidget(container)
        subjects_btn.click()  # Start with subjects page selected
    
    def closeEvent(self, event):
        reply = QMessageBox.StandardButton.Yes
        # reply = QMessageBox.question(self, "Exit", "Are you sure to quit?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            for thread in self.timetable_widget.THREADS:
                thread.quit()
            
            event.accept()
        else:
            event.ignore()
    
    def make_option_button_func(self, index: int):
        def func():
            for i, btn in enumerate(self.option_buttons):
                btn.setChecked(i == index)
            
            if self.display_index != index:
                self.stack.setCurrentIndex(index)
                self.update_interaction(self.display_index, index)
                self.display_index = index
        
        return func
    
    def _certify_class_level_info(self, class_index: int, option_id: str):
        if class_index < len(self.school.project["levels"]):
            if option_id in self.school.project["levels"][class_index][1]:
                return True
        
        return False
    
    def _deep_copy(self, value):
        if isinstance(value, dict):
            copy = {self._deep_copy(key): self._deep_copy(val) for key, val in value.items()}
        elif isinstance(value, (list, tuple, set)):
            copy = (self._deep_copy(val) for val in value)
            
            if isinstance(value, list):
                copy = list(copy)
            elif isinstance(value, tuple):
                copy = tuple(copy)
            elif isinstance(value, set):
                copy = set(copy)
        elif isinstance(value, str):
            copy = "".join(list(value))
        elif isinstance(value, int):
            copy = (value * 100) // 100
        elif isinstance(value, float):
            copy = value * 1.0
        elif isinstance(value, bool):
            copy = True if value else False
        elif value is None:
            copy = None
        else:
            raise Exception(f"Type: {type(value)} is not accounted for in copy")
        
        return copy
    
    def _update_subjects(self, comming_from_teacher: bool = True, comming_from_class: bool = True):
        subject_info = self.subjects_widget.get()
        teacher_info = self.teachers_widget.get()
        class_info = self.classes_widget.get()
        
        if comming_from_teacher:
            # Update Teachers
            teachers = [None]
            id_mapping = {}
            
            for teacher_index, (teacher_id, teacher_info_entry) in enumerate(teacher_info.items()):
                teacher_name = " ".join(teacher_info_entry["text"])
                
                teachers.append(teacher_name)
                id_mapping[teacher_index + 1] = teacher_id
            
            self.subjects_widget.teachers = teachers
            self.subjects_widget.id_mapping = id_mapping
            
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
        
        if comming_from_class:
            # Update Classes
            for class_id, class_info_entry in self._deep_copy(class_info).items():
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
        
        self.subjects_widget.info = subject_info
    
    def _update_teachers(self):
        teacher_info = self.teachers_widget.get()
        subject_info = self.subjects_widget.get()
        
        subjects = [None]
        id_mapping = {}
        
        for subject_index, (subject_id, subject_info_entry) in enumerate(subject_info.items()):
            subject_name = " ".join(subject_info_entry["text"])
            
            subjects.append(subject_name)
            id_mapping[subject_index + 1] = subject_id
        
        self.teachers_widget.subjects = subjects
        self.teachers_widget.id_mapping = id_mapping
        
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
        
        self.teachers_widget.info = teacher_info
    
    def _update_classes(self):
        subject_info = self.subjects_widget.get()
        class_info = self.classes_widget.get()
        teacher_info = self.teachers_widget.get()
        
        subject_teacher_mapping = {}
        for subject_index, (subject_id, subject_info_entry) in enumerate(subject_info.items()):
            subject_teacher_info = self._deep_copy(subject_info_entry["teachers"])
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
        
        for subject_index, (subject_id, _) in enumerate(self.classes_widget.subject_teachers_mapping.items()):
            if subject_id not in subject_info:
                for _, class_info_entry in class_info.items():
                    class_info_entry["subjects"]["content"].pop(subject_id)
                    class_info_entry["subjects"]["id_mapping"].pop(subject_index)
        
        self.classes_widget.info = class_info
        self.classes_widget.subject_teachers_mapping = subject_teacher_mapping
    
    def _update_timetable_editor(self):
        subjects_info = self.subjects_widget.get()
        teachers_info = self.teachers_widget.get()
        classes_info = self.classes_widget.get()
        
        subjectTeacherMapping = {}
        for subject_id, subject_info in subjects_info.items():
            teacher_subject_info = {}
            
            for class_id, _ in subject_info["classes"]["content"].items():
                class_index = next(index for index, (_id, _) in enumerate(classes_info.items()) if _id == class_id)
                subject_in_class_info = classes_info[class_id]["subjects"]["content"][subject_id]
                
                teacher_none_index = subject_in_class_info["teachers"]["content"].index(None)
                available_teachers = [
                    (index_id, teachers_info[index_id])
                    for index, index_id in
                        subject_in_class_info["teachers"]["id_mapping"].items()
                    if index < teacher_none_index
                ]
                
                for teacher_id, teacher_info in available_teachers:
                    if teacher_id not in teacher_subject_info:
                        teacher_subject_info[teacher_id] = [teacher_info["text"][0], [class_index]]
                    else:
                        teacher_subject_info[teacher_id][1].append(class_index)
                
                if "&timings" not in teacher_subject_info:
                    teacher_subject_info["&timings"] = {str(class_index): [int(subject_in_class_info["per_day"]), int(subject_in_class_info["per_week"])]}
                else:
                    teacher_subject_info["&timings"][str(class_index)] = [int(subject_in_class_info["per_day"]), int(subject_in_class_info["per_week"])]
                
                valid_options = [option_id for option_id, option_state in subject_info["classes"]["content"][class_id].items() if option_state]
                if len(valid_options) != len(subject_info["classes"]["content"][class_id]):
                    if "&classes" not in teacher_subject_info:
                        teacher_subject_info["&classes"] = {str(class_index): valid_options}
                    else:
                        teacher_subject_info["&classes"][str(class_index)] = valid_options
        
            subjectTeacherMapping[subject_id] = (subject_info["text"][0], teacher_subject_info)
        
        total_subject_amt = 0
        for _, subject_info in subjectTeacherMapping.values():
            for class_index, (_, perWeek) in subject_info["&timings"].items():
                total_subject_amt += perWeek * len([info["options"] for info in classes_info.values()][int(class_index)])
        
        class_levels = []
        for class_index, (class_id, class_info) in enumerate(classes_info.items()):
            level_info = {
                option_id:
                [
                    option_text,
                    (
                        self.school.project["levels"][class_index][1][class_id + option_id]
                        if self._certify_class_level_info(class_index, option_id) else
                        [[int(total_subject_amt / (len(self.default_weekdays) * len(classes_info))) for _ in range(len(self.default_weekdays))], [int(total_subject_amt / (len(self.default_weekdays) * len(classes_info) * 2)) for _ in range(len(self.default_weekdays))], self.default_weekdays]
                    )
                ]
                for option_id, option_text in class_info["options"].items()}
            class_levels.append([class_info["text"][0], level_info])
        
        self.project = {
            "levels": class_levels,
            "subjectTeacherMapping": subjectTeacherMapping
        }
        
        school_project_subjects_dict = self.school.project.get("subjects")
                
        if school_project_subjects_dict is not None:
            subjects = {}
            for subject_id, (subject_name, subject_info) in subjectTeacherMapping.items():
                subject_level_info = {}
                classes_taught = {
                    str(class_index): list(class_info["options"].keys())
                    for class_index, (_, class_info)
                    in enumerate(classes_info.items())
                } if subject_info.get("&classes") is None else subject_info["&classes"]
                
                for class_index, class_ids in classes_taught.items():
                    class_teacher_mapping = {}
                    for class_id in class_ids:
                        teacher_info_from_project = None
                        
                        subject_info_from_subjects = school_project_subjects_dict.get(subject_id)
                        if subject_info_from_subjects is not None:
                            teacher_info_from_project = subject_info_from_subjects[1][class_index][2].get(class_id)
                        
                        if teacher_info_from_project is not None:
                            class_teacher_mapping[class_id] = teacher_info_from_project
                        else:
                            all_available_class_teacher_ids = list({_id: name for _id, (name, _) in [(k, v) for k, v in subject_info.items() if not k.startswith("&")]}.items())
                            if random.choice([True, False, False, False, False]):
                                random.shuffle(all_available_class_teacher_ids)
                            
                            teacher_id = all_available_class_teacher_ids[0][0]
                            teacher_name = all_available_class_teacher_ids[0][1]
                            
                            class_teacher_mapping[class_id] = [[teacher_id, teacher_name], []]
                        
                    per_day, per_week = subject_info["&timings"][class_index]
                    subject_level_info[class_index] = (per_day, per_week, class_teacher_mapping)
                
                subjects[subject_id] = [subject_name, subject_level_info]
            
            self.project["subjects"] = subjects
        
        self.school = School(self.project)
        self.timetable_widget.set_editor_from_school(self.school)
    
    def update_interaction(self, prev_index: int, curr_index: int):
        match curr_index:
            case 0:  # Subjects view
                self._update_subjects(prev_index == 1, prev_index == 2)
            case 1:  # Teachers view
                if prev_index == 2:
                    self.update_interaction(2, 0)
                self._update_teachers()
            case 2: # Classes view
                if prev_index == 0:
                    self.update_interaction(0, 1)
                elif prev_index == 1:
                    self.update_interaction(1, 0)
                self._update_classes()
            case 3:  # Timetable view
                if prev_index == 0:
                    self.update_interaction(0, 2)
                if prev_index == 1:
                    self.update_interaction(1, 2)
                if prev_index == 2:
                    self.update_interaction(2, 0)
                
                self._update_timetable_editor()
                # self.timetable_widget.settings_widget.generate_new_school_timetable()
    


