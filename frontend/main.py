import random
import sys

import json
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout,
    QVBoxLayout, QPushButton, QStackedWidget,
    QMenuBar, QMessageBox
)
from PyQt6.QtGui import QIcon
from frontend.setting_widgets import SettingWidget, Subjects, Teachers, Classes
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
            self.save_data = json.loads(file.read())
        
        self.display_index = 0
        self.school = School(self.save_data)
        
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
        self.subjects_widget = Subjects(self.save_data.get("subjectsInfo"))
        self.teachers_widget = Teachers(self.save_data.get("teachersInfo"))
        self.classes_widget = Classes(self.save_data.get("classesInfo"))
        
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
    
    def get_settings_info(self):
        setting_widgets: dict[str, SettingWidget] = {
            "subjectsInfo": self.subjects_widget,
            "teachersInfo": self.teachers_widget,
            "classesInfo": self.classes_widget
        }
        
        return {
            widget_name: {
                "variables": widget.get(),
                "constants": widget.get_constants()
            }
            for widget_name, widget in
            setting_widgets.items()
        }
    
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
    
    def update_interaction(self, prev_index: int, curr_index: int):
        match curr_index:
            case 0:  # Subjects view
                self.subjects_widget.update_data_interaction(self, prev_index, curr_index)
                self.teachers_widget.update_data_interaction(self, prev_index, curr_index)
                self.classes_widget.update_data_interaction(self, prev_index, curr_index)
            case 1:  # Teachers view
                self.teachers_widget.update_data_interaction(self, prev_index, curr_index)
                self.subjects_widget.update_data_interaction(self, prev_index, curr_index)
                self.classes_widget.update_data_interaction(self, prev_index, curr_index)
            case 2: # Classes view
                self.classes_widget.update_data_interaction(self, prev_index, curr_index)
                self.subjects_widget.update_data_interaction(self, prev_index, curr_index)
                self.teachers_widget.update_data_interaction(self, prev_index, curr_index)
            case 3:  # Timetable view
                if prev_index == 0:
                    self.teachers_widget.update_data_interaction(self, prev_index, curr_index)
                    self.classes_widget.update_data_interaction(self, prev_index, curr_index)
                elif prev_index == 1:
                    self.subjects_widget.update_data_interaction(self, prev_index, curr_index)
                    self.classes_widget.update_data_interaction(self, prev_index, curr_index)
                elif prev_index == 2:
                    self.subjects_widget.update_data_interaction(self, prev_index, curr_index)
                    self.teachers_widget.update_data_interaction(self, prev_index, curr_index)
                self.timetable_widget.update_data_interaction(self)
