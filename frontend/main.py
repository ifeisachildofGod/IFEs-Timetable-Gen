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
        
        self.file_action = menu_bar.addAction(QIcon(), "File")
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
        
        option_buttons = [subjects_btn, teachers_btn, classes_btn, timetable_btn]
        
        self.stack.addWidget(self.subjects_widget)
        self.stack.addWidget(self.teachers_widget)
        self.stack.addWidget(self.classes_widget)
        self.stack.addWidget(self.timetable_widget)
        
        # Connect buttons
        for index, button in enumerate(option_buttons):
            button.clicked.connect(self.make_option_button_func(index, option_buttons))
        
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
            print()
        return super().keyPressEvent(a0)
    
    def make_option_button_func(self, index, option_buttons):
        def func():
            for i, btn in enumerate(option_buttons):
                btn.setChecked(i == index)
            
            if self.display_index != index:
                self.display_index = index
                self.stack.setCurrentIndex(self.display_index)
                self.update_interaction(self.display_index)
        
        return func
    
    def _certify_level_info(self, level: str, option: str):
        if level in self.school.project["levels"]:
            if option in self.school.project["levels"][level][0]:
                return True
        
        return False
    
    # def _update_subjects(self):
    #     # Subject View
    #     subject_classes_data = [[info["text"], {"options": info["options"], "subjects": info["subjects"]}] 
    #                     for info in self.classes_widget.get()]
    #     subject_teachers_data = [[info["text"], info["subjects"]] for info in self.teachers_widget.get()]
        
    #     # Update subjects widget with current teachers
    #     prev_selected_subject_teachers = self.subjects_widget.teachers[:self.subjects_widget.teachers.index(None)]
    #     subject_teacher_names = [name for name, _ in subject_teachers_data]
    #     subject_subjects_names = [[name, subjects[:subjects.index(None)]] for name, subjects in subject_teachers_data]
    #     self.subjects_widget.teachers = [t for t in subject_teacher_names if t in prev_selected_subject_teachers] + [None] + [t for t in subject_teacher_names if t not in prev_selected_subject_teachers]
        
    #     # Refresh subject widget connections
    #     for name, subjects in subject_subjects_names:
    #         for _, info in self.subjects_widget.info.items():
    #             info["teachers"] = [t for t in self.subjects_widget.teachers]
    #             if info['text'] in subjects:
    #                 info["teachers"].remove(name)
    #                 info["teachers"].insert(0, name)
        
    #     # Update class information
    #     class_options = {}
    #     for class_name, data in subject_classes_data:
    #         if data["options"]:
    #             class_options[class_name] = data["options"]
        
    #     self.subjects_widget.classesInfo = class_options if class_options else self.subjects_widget.classesInfo
    
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
    
    def _update_subjects(self):
        subject_info = self.subjects_widget.get()
        teacher_info = self.teachers_widget.get()
        class_info = self.classes_widget.get()
        
        # Update Teachers
        teachers = [None]
        id_mapping = {}
        
        for teacher_index, (teacher_id, teacher_info_entry) in enumerate(teacher_info.items()):
            teachers.append(teacher_info_entry["text"])
            id_mapping[teacher_index + 1] = teacher_id
        
        self.subjects_widget.teachers = teachers
        self.subjects_widget.id_mapping = id_mapping
        
        for teacher_index, (teacher_id, teacher_info_entry) in enumerate(teacher_info.items()):
            teacher_subject_index_id_mapping = dict(zip(list(teacher_info_entry["subjects"]["id_mapping"].values()), list(teacher_info_entry["subjects"]["id_mapping"].keys())))
            
            for subject_id, subject_info_entry in subject_info.items():
                subject_teacher_index_id_mapping = dict(zip(list(subject_info_entry["teachers"]["id_mapping"].values()), list(subject_info_entry["teachers"]["id_mapping"].keys())))
                
                teacher_index_in_subject = subject_teacher_index_id_mapping.get(teacher_id)
                subject_index_in_teacher = teacher_subject_index_id_mapping[subject_id]  # The teaacher must always be in the teacher list, if not there is a problem
                
                if teacher_index_in_subject is None:
                    teacher_index_in_subject = len(subject_info_entry["teachers"]["content"])
                    
                    subject_info_entry["teachers"]["content"].append(teacher_info_entry["text"])
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
        
        for subject_id, subject_info_entry in self._deep_copy(subject_info).items():
            subject_teacher_index_id_mapping = dict(zip(list(subject_info_entry["teachers"]["id_mapping"].values()), list(subject_info_entry["teachers"]["id_mapping"].keys())))
            
            for teacher_index, (teacher_id, teacher_info_entry) in enumerate(teacher_info.items()):
                teacher_index_in_subject = subject_teacher_index_id_mapping[teacher_id]
                subject_info_entry["teachers"]["id_mapping"].pop(teacher_index_in_subject)
            
            for teacher_in_subject_indexes in subject_info_entry["teachers"]["id_mapping"].keys():
                subject_info[subject_id]["teachers"]["content"].pop(teacher_in_subject_indexes)
                subject_info[subject_id]["teachers"]["id_mapping"].pop(teacher_in_subject_indexes)
        
        self.subjects_widget.info = subject_info
    
    # def _update_teachers(self):
    #     teacher_info = self.teachers_widget.get()
    #     subject_info = self.subjects_widget.get()
        
    #     # Update Teachers
    #     subjects = [None]
    #     id_mapping = {}
        
    #     for subject_index, (subject_id, subject_info_entry) in enumerate(subject_info.items()):
    #         subjects.append(subject_info_entry["text"])
    #         id_mapping[subject_index + 1] = subject_id
        
    #     self.teachers_widget.subjects = subjects
    #     self.teachers_widget.id_mapping = id_mapping
        
    #     for subject_index, (subject_id, subject_info_entry) in enumerate(subject_info.items()):
    #         subject_teacher_index_id_mapping = dict(zip(list(subject_info_entry["teachers"]["id_mapping"].values()), list(subject_info_entry["teachers"]["id_mapping"].keys())))
            
    #         for teacher_id, teacher_info_entry in teacher_info.items():
    #             teacher_subject_index_id_mapping = dict(zip(list(teacher_info_entry["subjects"]["id_mapping"].values()), list(teacher_info_entry["subjects"]["id_mapping"].keys())))
                
    #             subject_index_in_teacher = teacher_subject_index_id_mapping.get(subject_id)
    #             teacher_index_in_subject = subject_teacher_index_id_mapping[teacher_id]  # The teaacher must always be in the subject list, if not there is a problem
                
    #             if subject_index_in_teacher is None:
    #                 subject_index_in_teacher = len(teacher_info_entry["subjects"]["content"])
                    
    #                 teacher_info_entry["subjects"]["content"].append(subject_info_entry["text"])
    #                 teacher_info_entry["subjects"]["id_mapping"][subject_index_in_teacher] = subject_id
    #                 teacher_subject_index_id_mapping[subject_id] = subject_index_in_teacher
                
    #             teacher_none_index_in_subject = subject_info_entry["teachers"]["content"].index(None)
    #             subject_none_index_in_teacher = teacher_info_entry["subjects"]["content"].index(None)
                
    #             is_subject_selected_in_teacher = subject_index_in_teacher < subject_none_index_in_teacher
    #             is_teacher_selected_in_subject = teacher_index_in_subject < teacher_none_index_in_subject
                
    #             if is_subject_selected_in_teacher != is_teacher_selected_in_subject:
    #                 curr_teacher_value = teacher_info_entry["subjects"]["content"].pop(subject_index_in_teacher)
    #                 curr_subject_id = teacher_info_entry["subjects"]["id_mapping"].pop(subject_index_in_teacher)
                    
    #                 if is_teacher_selected_in_subject and not is_subject_selected_in_teacher:
    #                     # Make is selected in the teacher editor
    #                     teacher_info_entry["subjects"]["content"].insert(subject_none_index_in_teacher, curr_teacher_value)
    #                     teacher_info_entry["subjects"]["id_mapping"][subject_none_index_in_teacher] = curr_subject_id
    #                 elif not is_teacher_selected_in_subject and is_subject_selected_in_teacher:
    #                     # Make is unselected in the teacher editor
    #                     teacher_info_entry["subjects"]["content"].append(curr_teacher_value)
    #                     teacher_info_entry["subjects"]["id_mapping"][len(teacher_info_entry["subjects"]["content"]) - 1] = curr_subject_id
        
    #     for teacher_id, teacher_info_entry in self._deep_copy(teacher_info).items():
    #         teacher_subject_index_id_mapping = dict(zip(list(teacher_info_entry["subjects"]["id_mapping"].values()), list(teacher_info_entry["subjects"]["id_mapping"].keys())))
            
    #         for subject_index, (subject_id, subject_info_entry) in enumerate(subject_info.items()):
    #             subject_index_in_teacher = teacher_subject_index_id_mapping[subject_id]
    #             teacher_info_entry["subjects"]["id_mapping"].pop(subject_index_in_teacher)
            
    #         for subject_in_teacher_indexes in teacher_info_entry["subjects"]["id_mapping"].keys():
    #             teacher_info[teacher_id]["subjects"]["content"].pop(subject_in_teacher_indexes)
    #             teacher_info[teacher_id]["subjects"]["id_mapping"].pop(subject_in_teacher_indexes)
        
    #     self.teachers_widget.info = teacher_info
    
    def _update_teachers(self):
        teacher_info = self.teachers_widget.get()
        subject_info = self.subjects_widget.get()
        
        subject = [None]
        id_mapping = {}
        
        for subject_index, (subject_id, subject_info_entry) in enumerate(subject_info.items()):
            subject.append(subject_info_entry["text"])
            id_mapping[subject_index + 1] = subject_id
            
            subject_teacher_index_id_mapping = dict(zip(list(subject_info_entry["teachers"]["id_mapping"].values()), list(subject_info_entry["teachers"]["id_mapping"].keys())))
            
            for teacher_id, teacher_info_entry in teacher_info.items():
                teacher_subject_index_id_mapping = dict(zip(list(teacher_info_entry["subjects"]["id_mapping"].values()), list(teacher_info_entry["subjects"]["id_mapping"].keys())))
                
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
                    teacher_info_entry["subjects"]["content"].append(subject_info_entry["text"])
                    teacher_info_entry["subjects"]["id_mapping"][len(teacher_info_entry["subjects"]["content"]) - 1] = subject_id
        
        for teacher_id, teacher_info_entry in self._deep_copy(teacher_info).items():
            teacher_subject_index_id_mapping = dict(zip(list(teacher_info_entry["subjects"]["id_mapping"].values()), list(teacher_info_entry["subjects"]["id_mapping"].keys())))
            
            for subject_index, (subject_id, subject_info_entry) in enumerate(subject_info.items()):
                subject_index_in_teacher = teacher_subject_index_id_mapping[subject_id]
                teacher_info_entry["subjects"]["id_mapping"].pop(subject_index_in_teacher)
            
            for subject_in_teacher_indexes in teacher_info_entry["subjects"]["id_mapping"].keys():
                teacher_info[teacher_id]["subjects"]["content"].pop(subject_in_teacher_indexes)
                teacher_info[teacher_id]["subjects"]["id_mapping"].pop(subject_in_teacher_indexes)
        
        self.teachers_widget.info = teacher_info
        
        self.teachers_widget.subject = subject
        self.teachers_widget.id_mapping = id_mapping
    
    # def _update_teachers(self):
    #     teacher_subjects_data = [[info["text"], {"classes": info["classes"], "teachers": info["teachers"]}]
    #                     for info in self.subjects_widget.get()]
        
    #     # Update available subjects list
    #     prev_selected_teacher_subjects = self.teachers_widget.subjects[:self.teachers_widget.subjects.index(None)]
    #     self.teachers_widget.subjects = [None] + [name for name, _ in teacher_subjects_data]
    #     for info in self.teachers_widget.info.values():
    #         prev_selected_teacher_subjects = info["subjects"][:info["subjects"].index(None)]
    #         info["subjects"] = [name for name, _ in teacher_subjects_data if name in prev_selected_teacher_subjects] + [None] + [name for name, _ in teacher_subjects_data if name not in prev_selected_teacher_subjects]
        
    #     # teacher_names = [name for name, _ in teacher_subjects_data]
    #     prev_teacher_subjects_names = [[name, subjects['teachers'][:subjects['teachers'].index(None)]] for name, subjects in teacher_subjects_data]
        
    #     # Refresh subject widget connections
    #     for name, teachers in prev_teacher_subjects_names:
    #         for _, info in self.teachers_widget.info.items():
    #             if info['text'] in teachers:
    #                 info["subjects"].remove(name)
    #                 info["subjects"].insert(0, name)
        
    #     # Update subject widget according to teacher widget
    #     for _, info in self.subjects_widget.info.items():
    #         teachers_selected_by_subjects = [teacher_info["text"] for teacher_info in self.teachers_widget.get() if info["text"] in teacher_info["subjects"][:teacher_info["subjects"].index(None)]]
    #         info["teachers"] = [i for i in info["teachers"] if i in teachers_selected_by_subjects and i is not None] + [None] + [i for i in info["teachers"] if i not in teachers_selected_by_subjects and i is not None]
    
    # def _update_classes(self):
    #     class_subjects_data = [[info["text"], {"classes": info["classes"], "teachers": info["teachers"]} ]
    #                     for info in self.subjects_widget.get()]
    #     class_teachers_data = [[info["text"], info["subjects"]] for info in self.teachers_widget.get()]
        
    #     # Update available subjects and teachers
    #     teacher_names = [name for name, _ in class_teachers_data]
    #     prev_selected_teachers = self.classes_widget.teachers[:self.classes_widget.teachers.index(None)]
    #     self.classes_widget.subjects = [name for name, _ in class_subjects_data]
    #     self.classes_widget.teachers = [t for t in teacher_names if t in prev_selected_teachers] + [None] + [t for t in teacher_names if t not in prev_selected_teachers]
    #     self.classes_widget.subject_teacher = {info["text"]: [None] + info["teachers"][:info["teachers"].index(None)] for info in self.subjects_widget.get()}
        
    #     for class_info in self.classes_widget.info:
    #         class_subjects = class_info["subjects"]
    #         for index, (subject, _) in enumerate(class_subjects):
    #             if subject not in self.classes_widget.subjects:
    #                 del class_subjects[index]
    #             else:
    #                 # Update available teachers for each subject
    #                 available_teachers = [t_name for t_name, subjects in class_teachers_data
    #                                     if subject in subjects]
    #                 prev_selected_teachers = class_subjects[index][1][2][:class_subjects[index][1][2].index(None)]
    #                 class_subjects[index][1][2] = [teacher for teacher in available_teachers if teacher in prev_selected_teachers] + [None] + [teacher for teacher in available_teachers if teacher not in prev_selected_teachers]
    
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
                
                if class_subject_content is not None:
                    if class_subject_content["teachers"]["id_mapping"] != teacher_info["id_mapping"]:
                        subject_teachers_corrections = {index : index_id for index, index_id in teacher_info["id_mapping"].items() if class_subject_content["teachers"]["id_mapping"].get(index) != index_id}
                        class_subject_content["teachers"]["id_mapping"].update(subject_teachers_corrections)
                        class_subject_content["teachers"]["content"] = [teacher_info["content"][index] for index in class_subject_content["teachers"]["id_mapping"].keys()]
                        class_object["subjects"]["content"][subject_id] = class_subject_content
            
            subject_teacher_mapping[subject_id] = {"name": subject_info_entry["text"], "teachers": teacher_info}
        
        for subject_index, (subject_id, _) in enumerate(self.classes_widget.subject_teachers_mapping.items()):
            if subject_id not in subject_info:
                for _, class_object in class_info.items():
                    class_object["subjects"]["content"].pop(subject_id)
                    class_object["subjects"]["id_mapping"].pop(subject_index)
        
        self.classes_widget.info = class_info
        self.classes_widget.subject_teachers_mapping = subject_teacher_mapping
    
    def _update_timetable_editor(self):
        levels = {}
        for index, class_info in enumerate(self.classes_widget.get()):
            level = str(index + 1)
            level_info = {option: (self.school.project["levels"][level][0][option] if self._certify_level_info(level, option) else self.default_settings) for option in class_info["options"]}
            levels[level] = [level_info, class_info["text"]]
        
        subjectTeacherMapping = {}
        for classes_info in self.classes_widget.get():
            cls = subjectTeacherMapping[classes_info["text"]] = {}
            
            for subject_name, (per_day, per_week, teachers_info) in classes_info["subjects"]:
                subject = cls[subject_name] = {}
                
                for teacher_name in teachers_info[:teachers_info.index(None)]:
                    subject[teacher_name] = []
                
                subject["&timings"] = {}
                subject["&classes"] = {}
                
                subject_info = {}
                for subject_info in self.subjects_widget.get():
                    if subject_info["text"] == subject_name:
                        break
                
                for cls_name, teachables in subject_info["classes"].items():
                    if sum(teachables):
                        for level, (_, level_cls_name) in levels.items():
                            if level_cls_name == cls_name:
                                for teacher_name in teachers_info[:teachers_info.index(None)]:
                                    subject[teacher_name].append(int(level))
                                subject["&timings"][level] = [int(per_day), int(per_week)]
                                if sum(teachables) != len(teachables):
                                    valid_options = [classes_info["options"][class_name_index] for class_name_index, selected in enumerate(teachables) if selected]
                                    subject["&classes"][level] = valid_options
                                
                                break
                
                if not subject["&classes"]:
                    subject.pop("&classes")
        
        subjects = {}
        for index, classes_info in enumerate(self.classes_widget.get()):
            level = str(index + 1)
            
            for subject_name, (per_day, per_week, teachers_info) in classes_info["subjects"]:
                valid_teachers = []
                option_teacher_mapping = {}
                for optionIndex, option in enumerate(classes_info["options"]):
                    for subject_info in self.subjects_widget.get():
                        if subject_name == subject_info["text"] and subject_info["classes"][classes_info["text"]][optionIndex]:
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
    
    def update_interaction(self, index: int):
        match index:
            case 0:  # Subjects view
                self._update_subjects()
            case 1:  # Teachers view
                self._update_teachers()
            case 2:  # Classes view
                self._update_subjects()
                self._update_teachers()
                self._update_classes()
            case 3:  # Timetable view
                self._update_subjects()
                self._update_teachers()
                self._update_classes()
                
                self._update_timetable_editor()
                # self.timetable_widget.settings_widget.generate_new_school_timetable()
    


