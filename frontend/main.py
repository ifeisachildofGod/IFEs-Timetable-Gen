import sys

from copy import deepcopy
import json
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout,
    QVBoxLayout, QPushButton, QStackedWidget,
    QMenuBar
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
        self.default_settings = [
                    [10, 10, 10, 10, 10],
                    [7, 7, 7, 7, 7],
                    ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
                ]
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
    
    def closeEvent(self, a0):
        for thread in self.timetable_widget.THREADS:
            thread.quit()
        
        return super().closeEvent(a0)
    
    def keyPressEvent(self, a0):
        if a0.text() == "1":
            print(self.subjects_widget.get())
            print()
            print(self.teachers_widget.get())
            print()
            print(self.classes_widget.get())
            print()
            print()
        return super().keyPressEvent(a0)
    
    def make_option_button_func(self, index: int):
        def func():
            for i, btn in enumerate(self.option_buttons):
                btn.setChecked(i == index)
            
            if self.display_index != index:
                self.stack.setCurrentIndex(index)
                self.update_interaction(self.display_index, index)
                self.display_index = index
        
        return func
    
    def _certify_level_info(self, level: str, option: str):
        if level in self.school.project["levels"]:
            if option in self.school.project["levels"][level][0]:
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
        
        a = teacher_info["Subject: 0"]["subjects"]["id_mapping"]
        
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
                teacher_subject_index_id_mapping = dict(zip(list(teacher_info_entry["subjects"]["id_mapping"].values()), list(teacher_info_entry["subjects"]["id_mapping"].keys())))
                
                for subject_id, subject_info_entry in subject_info.items():
                    subject_teacher_index_id_mapping = dict(zip(list(subject_info_entry["teachers"]["id_mapping"].values()), list(subject_info_entry["teachers"]["id_mapping"].keys())))
                    
                    teacher_index_in_subject = subject_teacher_index_id_mapping.get(teacher_id)
                    if subject_id not in teacher_subject_index_id_mapping:
                        print(subject_info_entry["teachers"]["id_mapping"])
                        print(a)
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
                        curr_teacher_id = subject_info_entry["teachers"]["id_mapping"].pop(teacher_index_in_subject)
                        
                        if is_subject_selected_in_teacher and not is_teacher_selected_in_subject:
                            # Make is selected in the subject editor
                            subject_info_entry["teachers"]["content"].insert(teacher_none_index_in_subject, curr_subject_value)
                            subject_info_entry["teachers"]["id_mapping"][teacher_none_index_in_subject] = curr_teacher_id
                        elif not is_subject_selected_in_teacher and is_teacher_selected_in_subject:
                            # Make is unselected in the subject editor
                            subject_info_entry["teachers"]["content"].append(curr_subject_value)
                            subject_info_entry["teachers"]["id_mapping"][len(subject_info_entry["teachers"]["content"]) - 1] = curr_teacher_id
            
            for i, (subject_id, subject_info_entry) in enumerate(self._deep_copy(subject_info).items()):
                subject_teacher_index_id_mapping = dict(zip(list(subject_info_entry["teachers"]["id_mapping"].values()), list(subject_info_entry["teachers"]["id_mapping"].keys())))
                
                # for teacher_id in teacher_info:
                #     if teacher_id in subject_teacher_index_id_mapping:
                #         teacher_index_in_subject = subject_teacher_index_id_mapping[teacher_id]
                #         subject_info_entry["teachers"]["id_mapping"].pop(teacher_index_in_subject)
                
                # for teacher_in_subject_indexes in deepcopy(subject_info_entry["teachers"]["id_mapping"]).keys():
                #     subject_info_entry["teachers"]["id_mapping"].pop(teacher_in_subject_indexes)
                
                for index, index_id in subject_info_entry["teachers"]["id_mapping"].items():
                    teacher_name = " ".join(teacher_info[index_id]["text"])
                    
                    subject_info_entry["teachers"]["content"][index] = teacher_name
        
        if comming_from_class:
            # Update Classes
            for class_id, class_info_entry in self._deep_copy(class_info).items():
                for subject_id, _ in class_info_entry["subjects"]["content"].items():
                    subject_info[subject_id]["classes"]["id_mapping"]["main"][class_id] = class_info_entry["text"][0]
                    subject_info[subject_id]["classes"]["id_mapping"]["sub"][class_id] = class_info_entry["options"]
                    subject_info[subject_id]["classes"]["content"][class_id] = {state_id : (
                        (
                            subject_info[subject_id]["classes"]["content"][class_id][state_id]
                            if subject_info[subject_id]["classes"]["content"][class_id].get(state_id) is None else
                            False
                        ) if subject_info[subject_id]["classes"]["content"].get(class_id) is not None else
                        False
                    ) for state_id, _ in class_info_entry["options"].items()}
        
        self.subjects_widget.info = subject_info
    
    def _update_teachers(self):
        teacher_info = self.teachers_widget.get()
        subject_info = self.subjects_widget.get()
        
        subjects = [None]
        id_mapping = {}
        
        for subject_index, (subject_id, subject_info_entry) in enumerate(deepcopy(subject_info).items()):
            subjects.append(subject_info_entry["text"][0])
            id_mapping[subject_index + 1] = subject_id
        
        self.teachers_widget.subjects = subjects
        self.teachers_widget.id_mapping = id_mapping
        
        for subject_index, (subject_id, subject_info_entry) in enumerate(deepcopy(subject_info).items()):
            subject_teacher_index_id_mapping = dict(zip(list(subject_info_entry["teachers"]["id_mapping"].values()), list(subject_info_entry["teachers"]["id_mapping"].keys())))
            
            for teacher_id, teacher_info_entry in teacher_info.items():
                teacher_subject_index_id_mapping = dict(
                    zip(
                        deepcopy(list(teacher_info_entry["subjects"]["id_mapping"].values())),
                        deepcopy(list(teacher_info_entry["subjects"]["id_mapping"].keys()))
                        )
                    )
                
                subject_index_in_teacher = teacher_subject_index_id_mapping.get(subject_id)
                teacher_index_in_subject = subject_teacher_index_id_mapping[teacher_id]  # The teaacher must always be in the subject list, if not there is a problem
                
                if subject_index_in_teacher is not None:
                    subject_teacher_none_index = subject_info_entry["teachers"]["content"].index(None)
                    teacher_subject_none_index = teacher_info_entry["subjects"]["content"].index(None)
                    
                    is_subject_selected_in_teacher = subject_index_in_teacher < teacher_subject_none_index
                    is_teacher_selected_in_subject = teacher_index_in_subject < subject_teacher_none_index
                    
                    if is_subject_selected_in_teacher != is_teacher_selected_in_subject:
                        curr_teacher_value = teacher_info_entry["subjects"]["content"].pop(subject_index_in_teacher)
                        curr_subject_id = teacher_info_entry["subjects"]["id_mapping"].pop(subject_index_in_teacher)
                        
                        if is_teacher_selected_in_subject and not is_subject_selected_in_teacher:
                            # Make is selected in the teacher editor
                            teacher_info_entry["subjects"]["content"].insert(teacher_subject_none_index, curr_teacher_value)
                            teacher_info_entry["subjects"]["id_mapping"][teacher_subject_none_index] = curr_subject_id
                        elif not is_teacher_selected_in_subject and is_subject_selected_in_teacher:
                            # Make is unselected in the teacher editor
                            teacher_info_entry["subjects"]["content"].append(curr_teacher_value)
                            teacher_info_entry["subjects"]["id_mapping"][len(teacher_info_entry["subjects"]["content"]) - 1] = curr_subject_id
                else:
                    teacher_info_entry["subjects"]["content"].append(subject_info_entry["text"][0])
                    teacher_info_entry["subjects"]["id_mapping"][len(teacher_info_entry["subjects"]["content"]) - 1] = subject_id
        
        for teacher_id, teacher_info_entry in self._deep_copy(teacher_info).items():
            teacher_subject_index_id_mapping = dict(zip(list(teacher_info_entry["subjects"]["id_mapping"].values()), list(teacher_info_entry["subjects"]["id_mapping"].keys())))
            
            # for subject_index, (subject_id, subject_info_entry) in enumerate(subject_info.items()):
            #     if subject_id in teacher_subject_index_id_mapping:
            #         subject_index_in_teacher = teacher_subject_index_id_mapping[subject_id]
            #         teacher_info_entry["subjects"]["id_mapping"].pop(subject_index_in_teacher)
            
            # for subject_in_teacher_indexes in deepcopy(teacher_info_entry["subjects"]["id_mapping"]).keys():
            #     teacher_info_entry["subjects"]["id_mapping"].pop(subject_in_teacher_indexes)
            
            for index, index_id in deepcopy(teacher_info_entry["subjects"]["id_mapping"]).items():
                if index_id in subject_info:
                    teacher_info_entry["subjects"]["content"][index] = subject_info[index_id]["text"][0]
                else:
                    teacher_info_entry["subjects"]["content"].pop(index)
                    teacher_info_entry["subjects"]["id_mapping"].pop(index)
        
        self.teachers_widget.info = teacher_info
    
    def _update_classes(self):
        subject_info = self.subjects_widget.get()
        class_info = self.classes_widget.get()
        
        subject_teacher_mapping = {}
        for subject_index, (subject_id, subject_info_entry) in enumerate(subject_info.items()):
            teacher_none_index_in_subjects = subject_info_entry["teachers"]["content"].index(None)
            
            teacher_info = self._deep_copy(subject_info_entry["teachers"])
            teacher_info["content"] = [None] + teacher_info["content"][:teacher_none_index_in_subjects]
            teacher_info["id_mapping"] = {index + 1 : index_id for index, index_id in teacher_info["id_mapping"].items() if index < teacher_none_index_in_subjects}
            
            for _, class_object in class_info.items():
                class_subject_content = class_object["subjects"]["content"].get(subject_id)
                
                if class_subject_content is not None and class_subject_content["teachers"]["id_mapping"] != teacher_info["id_mapping"]:
                    subject_teachers_corrections = {index : index_id for index, index_id in teacher_info["id_mapping"].items() if class_subject_content["teachers"]["id_mapping"].get(index) != index_id}
                    
                    class_subject_content["teachers"]["id_mapping"].update(subject_teachers_corrections)
                    class_subject_content["teachers"]["content"] = [teacher_info["content"][index] for index in class_subject_content["teachers"]["id_mapping"].keys()]
                    
                    if None in class_subject_content["teachers"]["content"]:
                        class_subject_content["teachers"]["content"].remove(None)
                    
                    sorted_teacher_indexes = sorted(list(class_subject_content["teachers"]["id_mapping"].keys()))
                    for i, index in enumerate(sorted_teacher_indexes):
                        if i != index:
                            class_subject_content["teachers"]["content"].insert(i, None)
                            break
                    
                    class_object["subjects"]["content"][subject_id] = class_subject_content
            
            subject_teacher_mapping[subject_id] = {"name": subject_info_entry["text"][0], "teachers": teacher_info}
        
        for subject_index, (subject_id, _) in enumerate(self.classes_widget.subject_teachers_mapping.items()):
            if subject_id not in subject_info:
                for _, class_object in class_info.items():
                    class_object["subjects"]["content"].pop(subject_id)
                    class_object["subjects"]["id_mapping"].pop(subject_index)
        
        self.classes_widget.info = class_info
        self.classes_widget.subject_teachers_mapping = subject_teacher_mapping
    
    def _update_timetable_editor(self):
        subjects_info = self.subjects_widget.get()
        classes_info = self.classes_widget.get()
        
        levels = {}
        for class_index, (_, class_info) in enumerate(classes_info.items()):
            level = str(class_index + 1)
            level_info = {option: (self.school.project["levels"][level][0][option] if self._certify_level_info(level, option) else self.default_settings) for option in class_info["options"]}
            levels[level] = [level_info, class_info["text"][0]]
        
        subjectTeacherMapping = {}
        for _, class_info in classes_info.items():
            cls = subjectTeacherMapping[class_info["text"][0]] = {}
            
            for subj_id, subj_info in class_info["subjects"]["content"].items():
                per_day = int(subj_info["per_day"])
                per_week = int(subj_info["per_week"])
                teachers_info = subj_info["teachers"]["content"]
                
                subject_name = subjects_info[subj_id]["text"][0]
                
                subject = cls[subject_name] = {}
                
                for teacher_name in teachers_info[:teachers_info.index(None)]:
                    subject[teacher_name] = []
                
                subject["&timings"] = {}
                subject["&classes"] = {}
                
                subject_info = {}
                for _, subject_info in subjects_info.items():
                    if subject_info["text"][0] == subject_name:
                        break
                
                for cls_id, cls_options in subject_info["classes"]["content"].items():
                    cls_name = classes_info[cls_id]["text"][0][0]
                    teachables = list(cls_options.values())
                    
                    if sum(teachables):
                        for level, (_, level_cls_name) in levels.items():
                            if level_cls_name == cls_name:
                                for teacher_name in teachers_info[:teachers_info.index(None)]:
                                    subject[teacher_name].append(int(level))
                                subject["&timings"][level] = [per_day, per_week]
                                if sum(teachables) != len(teachables):
                                    valid_options = [class_info["options"][class_name_index] for class_name_index, selected in enumerate(teachables) if selected]
                                    subject["&classes"][level] = valid_options
                                
                                break
                
                if not subject["&classes"]:
                    subject.pop("&classes")
        
        subjects = {}
        for index, (cls_id, class_info) in enumerate(classes_info.items()):
            level = str(index + 1)
            
            for subj_id, subj_info in class_info["subjects"]["content"].items():
                per_day = subj_info["per_day"]
                per_week = subj_info["per_week"]
                teachers_info = subj_info["teachers"]["content"]
                
                subject_name = subjects_info[subj_id]["text"][0]
                
                valid_teachers = []
                option_teacher_mapping = {}
                for optionIndex, (option_id, option) in enumerate(class_info["options"].items()):
                    for _, subject_info in subjects_info.items():
                        if subject_name == subject_info["text"][0] and subject_info["classes"]["content"][cls_id][option_id]:
                            if not valid_teachers:
                                valid_teachers = [t for t in teachers_info[:teachers_info.index(None)]]
                            option_teacher_mapping[option] = valid_teachers.pop()
                            break
                
                subjects[subject_name] = {}
                subjects[subject_name][level] = [int(per_day), int(per_week), option_teacher_mapping]
        
        self.project = {
            "levels": levels,
            "subjectTeacherMapping": subjectTeacherMapping,
            "subjects": subjects
        }
        
        self.school = School(self.project)
        self.timetable_widget.set_editor_from_school(self.school)
    
    def update_interaction(self, prev_index: int, curr_index: int):
        match curr_index:
            case 0:  # Subjects view
                self._update_subjects(prev_index == 1, prev_index == 2)
            case 1:  # Teachers view
                if prev_index == 0:
                    self._update_teachers()
                elif prev_index == 2:
                    self._update_subjects(False, True)
            case 2: # Classes view
                if prev_index == 0:
                    self._update_teachers()
                elif prev_index == 1:
                    self._update_subjects(True, True)
                self._update_classes()
            case 3:  # Timetable view
                if prev_index == 0:
                    self._update_teachers()
                if prev_index == 1:
                    self._update_subjects(True, False)
                if prev_index == 2:
                    self._update_subjects(False, True)
                
                self._update_timetable_editor()
                # self.timetable_widget.settings_widget.generate_new_school_timetable()
    


