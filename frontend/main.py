import json
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout,
    QVBoxLayout, QPushButton, QStackedWidget,
    QMenuBar
)
from PyQt6.QtGui import QIcon
from matplotlib.cbook import flatten
from frontend.setting_widgets import Subjects, Teachers, Classes
from frontend.editting_widgets import TimeTableEditor
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
        elif a0.text() == "2":
            self._update_timetable_editor()
        return super().keyPressEvent(a0)
    
    def make_option_button_func(self, index, option_buttons):
        def func():
            self.switch_page(index, option_buttons)
        
        return func
    
    def switch_page(self, index: int, buttons: list[QPushButton]):
        self.stack.setCurrentIndex(index)
        
        for i, btn in enumerate(buttons):
            btn.setChecked(i == index)
        
        self.update_interaction(index)
    
    def _certify_level_info(self, level: str, option: str):
        if level in self.school.project["levels"]:
            if option in self.school.project["levels"][level][0]:
                return True
        
        return False
    
    def _update_subjects(self):
        # Subject View
        subject_classes_data = [[info["text"], {"options": info["options"], "subjects": info["subjects"]}] 
                        for info in self.classes_widget.get()]
        subject_teachers_data = [[info["text"], info["subjects"]] for info in self.teachers_widget.get()]
        
        # Update subjects widget with current teachers
        prev_selected_subject_teachers = self.subjects_widget.teachers[:self.subjects_widget.teachers.index(None)]
        subject_teacher_names = [name for name, _ in subject_teachers_data]
        subject_subjects_names = [[name, subjects[:subjects.index(None)]] for name, subjects in subject_teachers_data]
        self.subjects_widget.teachers = [t for t in subject_teacher_names if t in prev_selected_subject_teachers] + [None] + [t for t in subject_teacher_names if t not in prev_selected_subject_teachers]
        
        # Refresh subject widget connections
        for name, subjects in subject_subjects_names:
            for _, info in self.subjects_widget.info.items():
                info["teachers"] = [t for t in self.subjects_widget.teachers]
                if info['text'] in subjects:
                    info["teachers"].remove(name)
                    info["teachers"].insert(0, name)
        
        # Update class information
        class_options = {}
        for class_name, data in subject_classes_data:
            if data["options"]:
                class_options[class_name] = data["options"]
        
        self.subjects_widget.classesInfo = class_options if class_options else self.subjects_widget.classesInfo
    
    def _update_teachers(self):
        teacher_subjects_data = [[info["text"], {"classes": info["classes"], "teachers": info["teachers"]}]
                        for info in self.subjects_widget.get()]
        
        # Update available subjects list
        prev_selected_teacher_subjects = self.teachers_widget.subjects[:self.teachers_widget.subjects.index(None)]
        self.teachers_widget.subjects = [None] + [name for name, _ in teacher_subjects_data]
        for info in self.teachers_widget.info.values():
            prev_selected_teacher_subjects = info["subjects"][:info["subjects"].index(None)]
            info["subjects"] = [name for name, _ in teacher_subjects_data if name in prev_selected_teacher_subjects] + [None] + [name for name, _ in teacher_subjects_data if name not in prev_selected_teacher_subjects]
        
        # teacher_names = [name for name, _ in teacher_subjects_data]
        prev_teacher_subjects_names = [[name, subjects['teachers'][:subjects['teachers'].index(None)]] for name, subjects in teacher_subjects_data]
        
        # Refresh subject widget connections
        for name, teachers in prev_teacher_subjects_names:
            for _, info in self.teachers_widget.info.items():
                if info['text'] in teachers:
                    info["subjects"].remove(name)
                    info["subjects"].insert(0, name)
        
        # Update subject widget according to teacher widget
        for _, info in self.subjects_widget.info.items():
            teachers_selected_by_subjects = [teacher_info["text"] for teacher_info in self.teachers_widget.get() if info["text"] in teacher_info["subjects"][:teacher_info["subjects"].index(None)]]
            info["teachers"] = [i for i in info["teachers"] if i in teachers_selected_by_subjects and i is not None] + [None] + [i for i in info["teachers"] if i not in teachers_selected_by_subjects and i is not None]
    
    def _update_classes(self):
        class_subjects_data = [[info["text"], {"classes": info["classes"], "teachers": info["teachers"]} ]
                        for info in self.subjects_widget.get()]
        class_teachers_data = [[info["text"], info["subjects"]] for info in self.teachers_widget.get()]
        
        # Update available subjects and teachers
        teacher_names = [name for name, _ in class_teachers_data]
        prev_selected_teachers = self.classes_widget.teachers[:self.classes_widget.teachers.index(None)]
        self.classes_widget.subjects = [name for name, _ in class_subjects_data]
        self.classes_widget.teachers = [t for t in teacher_names if t in prev_selected_teachers] + [None] + [t for t in teacher_names if t not in prev_selected_teachers]
        self.classes_widget.subject_teacher = {info["text"]: [None] + info["teachers"][:info["teachers"].index(None)] for info in self.subjects_widget.get()}
        
        for class_info in self.classes_widget.info:
            class_subjects = class_info["subjects"]
            for index, (subject, _) in enumerate(class_subjects):
                if subject not in self.classes_widget.subjects:
                    del class_subjects[index]
                else:
                    # Update available teachers for each subject
                    available_teachers = [t_name for t_name, subjects in class_teachers_data
                                        if subject in subjects]
                    prev_selected_teachers = class_subjects[index][1][2][:class_subjects[index][1][2].index(None)]
                    class_subjects[index][1][2] = [teacher for teacher in available_teachers if teacher in prev_selected_teachers] + [None] + [teacher for teacher in available_teachers if teacher not in prev_selected_teachers]
    
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
        
        # subjects = {}
        # for index, classes_info in enumerate(self.classes_widget.get()):
        #     level = str(index + 1)
            
        #     for subject_name, (per_day, per_week, teachers_info) in classes_info["subjects"]:
        #         valid_teachers = []
        #         option_teacher_mapping = {}
        #         for optionIndex, option in enumerate(classes_info["options"]):
        #             for subject_info in self.subjects_widget.get():
        #                 if subject_name == subject_info["text"] and subject_info["classes"][classes_info["text"]][optionIndex]:
        #                     if not valid_teachers:
        #                         valid_teachers = [t for t in teachers_info[:teachers_info.index(None)]]
        #                     option_teacher_mapping[option] = valid_teachers.pop()
        #                     break
                
        #         subjects[subject_name] = {}
        #         subjects[subject_name][level] = [int(per_day), int(per_week), option_teacher_mapping]
        
        project = {
            "levels": levels,
            "subjectTeacherMapping": subjectTeacherMapping,
            # "subjects": subjects
        }
        
        self.school.setProject(project)
    
    def update_interaction(self, index: int):
        self._update_subjects()
        self._update_teachers()
        self._update_classes()
        self._update_subjects()
        self._update_teachers()
        self._update_classes()
        
        if index == 0:  # Subjects view
            
            for widget, info in self.subjects_widget.info.items():
                # Reconnect buttons
                buttons = widget.findChildren(QPushButton)
                buttons[0].clicked.disconnect()
                buttons[1].clicked.disconnect()
                buttons[0].clicked.connect(self.subjects_widget.make_show_popup_1(widget))
                buttons[1].clicked.connect(self.subjects_widget.make_show_popup_2(widget))
        elif index == 1:  # Teachers view
            for widget in self.teachers_widget.info.keys():
                button = widget.findChildren(QPushButton)[1]
                button.clicked.disconnect()
                button.clicked.connect(self.teachers_widget.make_show_popup_1(widget))
        elif index == 3:  # Timetable view
            self._update_timetable_editor()
            self.timetable_widget.settings_widget.generate_new_school_timetable()
    


