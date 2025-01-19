from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout,
    QVBoxLayout, QPushButton, QStackedWidget,
    QMenuBar, QLineEdit
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QIcon
from matplotlib.cbook import flatten
from frontend.widgets import Subjects, Teachers, Classes
from frontend.theme import *


class Window(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # Set application style
        self.setStyleSheet(THEME[WINDOW])
        
        menu_bar = QMenuBar(self)
        self.setMenuBar(menu_bar)
        
        self.file_action = menu_bar.addAction(QIcon(), "File")
        self.edit_action = menu_bar.addAction(QIcon(), "Edit")
        self.window_action = menu_bar.addAction(QIcon(), "Window")
        
        menu_bar.setStyleSheet(menu_bar.styleSheet() + THEME[WINDOW_MENUBAR_ADDITION])
        
        self.class_options = {
            "JS1": ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J"],
            "JS2": ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J"],
            "JS3": ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J"],
            "SS1": ["A", "B", "C", "D", "E", "F", "G", "H", "I"],
            "SS2": ["A", "B", "C", "D", "E", "F", "G", "H"],
            "SS3": ["A", "B", "C", "D", "E", "F", "G", "H"]
            }
        self.teacher_subject_options = {"Subject 1": ["Teacher 1", "Teacher 2", "Teacher 3", "Teacher 4"], "Subject 2": ["Teacher 5", "Teacher 6", "Teacher 7", "Teacher 8"], "Subject 3": ["Teacher 9", "Teacher 10", "Teacher 11", "Teacher 12"], "Subject 4": ["Teacher 13", "Teacher 14", "Teacher 15", "Teacher 16"]}
        
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
        
        subjects_btn.setCheckable(True)
        teachers_btn.setCheckable(True)
        classes_btn.setCheckable(True)
        
        # Add widgets to stack
        self.subjects_widget = Subjects(None, {})
        self.teachers_widget = Teachers(None)
        self.classes_widget = Classes([], [])
        
        self.stack.addWidget(self.subjects_widget)
        self.stack.addWidget(self.teachers_widget)
        self.stack.addWidget(self.classes_widget)
        
        # Connect buttons
        subjects_btn.clicked.connect(lambda: self.switch_page(0, [subjects_btn, teachers_btn, classes_btn]))
        teachers_btn.clicked.connect(lambda: self.switch_page(1, [subjects_btn, teachers_btn, classes_btn]))
        classes_btn.clicked.connect(lambda: self.switch_page(2, [subjects_btn, teachers_btn, classes_btn]))
        
        # Add buttons to sidebar
        sidebar_layout.addWidget(subjects_btn)
        sidebar_layout.addWidget(teachers_btn)
        sidebar_layout.addWidget(classes_btn)
        sidebar_layout.addStretch()
        sidebar.setLayout(sidebar_layout)
        
        # Add widgets to main layout
        main_layout.addWidget(sidebar)
        main_layout.addWidget(self.stack)
        
        self.setCentralWidget(container)
        subjects_btn.click()  # Start with subjects page selected
        
    def switch_page(self, index, buttons):
        self.update_interaction(index)
        self.stack.setCurrentIndex(index)
        for i, btn in enumerate(buttons):
            btn.setChecked(i == index)

    def update_interaction(self, index: int):
        if index == 0:  # Subjects view
            # Get current states
            classes_data = [[info["text"], {"options": info["options"], "subjects": info["subjects"]}] 
                           for info in self.classes_widget.get()]
            teachers_data = [[info["text"], info["subjects"]] for info in self.teachers_widget.get()]
            
            # Update subjects widget with current teachers
            prev_selected_teachers = self.subjects_widget.teachers[:self.subjects_widget.teachers.index(None)]
            teacher_names = [name for name, _ in teachers_data]
            self.subjects_widget.teachers = [t for t in teacher_names if t in prev_selected_teachers] + [None] + [t for t in teacher_names if t not in prev_selected_teachers]
            
            # Update class information
            class_options = {}
            for class_name, data in classes_data:
                if data["options"]:
                    class_options[class_name] = data["options"]
            
            self.subjects_widget.classesInfo = class_options if class_options else self.subjects_widget.classesInfo
            
            # Refresh subject widget connections
            for widget, info in self.subjects_widget.info.items():
                widget_name = info["text"]
                
                # Update teacher assignments based on teacher data
                for _, subjects in teachers_data:
                    if widget_name in subjects:
                        prev_selected = info["teachers"][:info["teachers"].index(None)]
                        
                        selected_teachers = []
                        unselected_teachers = []
                        for t in range(len(teacher_names)):
                            if widget_name in teachers_data[t][1]:
                                if widget_name in prev_selected:
                                    selected_teachers.append(teachers_data[t][0])
                                    prev_selected.remove(teachers_data[t][0])
                                else:
                                    unselected_teachers.append(teachers_data[t][0])
                        
                        info["teachers"] = selected_teachers + [None] + unselected_teachers
                
                # Reconnect buttons
                buttons = widget.findChildren(QPushButton)[1:]
                buttons[0].clicked.disconnect()
                buttons[1].clicked.disconnect()
                buttons[0].clicked.connect(self.subjects_widget.make_show_popup_1(widget))
                buttons[1].clicked.connect(self.subjects_widget.make_show_popup_2(widget))

        elif index == 1:  # Teachers view
            # Get current states
            subjects_data = [[info["text"], {"classes": info["classes"], "teachers": info["teachers"]}]
                            for info in self.subjects_widget.get()]
            
            # Update available subjects list
            prev_selected_subjects = self.teachers_widget.subjects[:self.teachers_widget.subjects.index(None)]
            self.teachers_widget.subjects = [None] + [name for name, _ in subjects_data]
            for widget, info in self.teachers_widget.info.items():
                prev_selected_subjects = info["subjects"][:info["subjects"].index(None)]
                info["subjects"] = [name for name, _ in subjects_data if name in prev_selected_subjects] + [None] + [name for name, _ in subjects_data if name not in prev_selected_subjects]
                
                button = widget.findChildren(QPushButton)[1]
                button.clicked.disconnect()
                button.clicked.connect(self.teachers_widget.make_show_popup_1(widget))
            
            # Update teacher widget info
            # for widget, info in self.teachers_widget.info.items():
            #     teacher_name = info["text"]
            #     print(subjects_data)
            #     # Update subject assignments
            #     prev_selected = info["subjects"][:info["subjects"].index(None)]
                
            #     selecteds = []
            #     unselecteds = []
            #     for subject, data in subjects_data:
            #         if teacher_name in data["teachers"]:
            #             if subject in prev_selected:
            #                 selecteds.append(subject)
            #                 prev_selected.remove(subject)
            #             else:
            #                 unselecteds.append(subject)
                
            #     info["subjects"] = selecteds + [None] + unselecteds
                
            #     # Reconnect button
            #     button = widget.findChildren(QPushButton)[1]
            #     button.clicked.disconnect()
            #     button.clicked.connect(self.teachers_widget.make_show_popup_1(widget))

        elif index == 2:  # Classes view
            # Get current states
            subjects_data = [[info["text"], {"classes": info["classes"], "teachers": info["teachers"]} ]
                            for info in self.subjects_widget.get()]
            teachers_data = [[info["text"], info["subjects"]] for info in self.teachers_widget.get()]
            
            # Update available subjects and teachers
            teacher_names = [name for name, _ in teachers_data]
            prev_selected_teachers = self.classes_widget.teachers[:self.classes_widget.teachers.index(None)]
            self.classes_widget.subjects = [name for name, _ in subjects_data]
            self.classes_widget.teachers = [t for t in teacher_names if t in prev_selected_teachers] + [None] + [t for t in teacher_names if t not in prev_selected_teachers]
            
            # Update class subject availability based on teacher assignments
            for class_info in self.classes_widget.info:
                class_subjects = class_info["subjects"]
                for index, (subject, _) in enumerate(class_subjects):
                    if subject not in self.classes_widget.subjects:
                        del class_subjects[index]
                    else:
                        # Update available teachers for each subject
                        available_teachers = [t_name for t_name, subjects in teachers_data
                                           if subject in subjects]
                        prev_selected_teachers = class_subjects[index][1][2][:class_subjects[index][1][2].index(None)]
                        class_subjects[index][1][2] = [teacher for teacher in available_teachers if teacher in prev_selected_teachers] + [None] + [teacher for teacher in available_teachers if teacher not in prev_selected_teachers]


