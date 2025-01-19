from frontend.sub_widgets import SelectionList, DropDownCheckBoxes, SubjectSelection, ClassOptionSelection
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QLineEdit, QPushButton, QScrollArea,
    # QApplication, QSizePolicy, QComboBox,
    # QLabel
)

from PyQt6.QtCore import Qt
from frontend.theme import *
from frontend.theme import (_widget_fg_color, _widget_border_radius_1, _widget_text_color_2)


main_button_style = """
            QPushButton {
                background-color: """ + _widget_fg_color + """;
                color: """ + _widget_text_color_2 + """;
                border: none;
                padding: 8px 16px;
                border-radius: """ + _widget_border_radius_1 + """;
                font-size: 13px;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: """ + get_hover_color(_widget_fg_color) + """;
            }
            """

class Subjects(QWidget):
    def __init__(self, teachers: list[str | None] | None, classesInfo: dict[str, list[str]]):
        super().__init__()
        self.objectNameChanged.connect(lambda: self.add_button.setText(f"Add {self.objectName().title()}"))
        
        self.info = {}
        self.teacher_assignments = {}  # Track teacher assignments
        
        self.teachers = teachers if teachers is not None else [None]
        self.classesInfo = classesInfo
        
        self.main_layout = QVBoxLayout(self)
        
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        
        self.container = QWidget()
        self.container_layout = QVBoxLayout(self.container)
        self.scroll_area.setWidget(self.container)
        
        self.add_button = QPushButton()
        self.add_button.clicked.connect(self.add)
        # self.add_button.setStyleSheet(main_button_style)
        
        self.main_layout.addWidget(self.scroll_area)
        self.main_layout.addWidget(self.add_button, alignment=Qt.AlignmentFlag.AlignRight)
        
        self.list_selection_values = None
        
        self.setLayout(self.main_layout)
        
        self.setObjectName("subject")
        
        self.setStyleSheet(THEME[SUBJECT_TEACHERS_CLASSES])
    
    def get(self):
        return list(self.info.values())
    
    def add(self):
        widget = QWidget()
        widget.setObjectName("itemContainer")
        widget.setMaximumHeight(150)
        
        layout = QVBoxLayout()
        layout.setSpacing(8)
        layout.setContentsMargins(8, 8, 8, 8)
        widget.setLayout(layout)
        
        header_layout = QHBoxLayout()
        buttons_layout = QHBoxLayout()
        
        header_layout.setSpacing(8)
        
        name_edit = self.make_input(widget)
        
        delete_button = QPushButton("×")
        delete_button.setProperty('class', 'warning')
        delete_button.clicked.connect(self.make_delete_func(widget))
        delete_button.setFixedSize(30, 30)
        delete_button.setStyleSheet("padding: 3px;")
        
        header_layout.addWidget(name_edit)
        
        self.make_action_buttons(widget, buttons_layout)
        buttons_layout.addWidget(delete_button, alignment=Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignTop)
        
        layout.addLayout(buttons_layout)
        layout.addLayout(header_layout)
        
        self.container_layout.addWidget(widget, alignment=Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignVCenter)
        
        self.set_info(widget)
        
        name_edit.returnPressed.connect(lambda: name_edit.clearFocus())
        name_edit.show()
        name_edit.setFocus()
    
    def set_info(self, widget: QWidget):
        self.info[widget] = {"text": "", "classes": {}, "teachers": self.teachers}
    
    def make_delete_func(self, widget: QWidget):
        def del_widget():
            delete_button = self.sender()
            delete_button.setProperty('class', 'warning')
            self.container_layout.removeWidget(widget)
            widget.deleteLater()
            self.info.pop(widget)
        
        return del_widget
    
    def make_input(self, widget: QWidget):
        name_edit = QLineEdit()
        name_edit.setPlaceholderText(f"Enter {self.objectName().title()} Name")
        name_edit.setFixedHeight(80)
        name_edit.setStyleSheet("font-size: 40px;")
        
        def clicked():
            self.info[widget]["text"] = name_edit.text()
        
        name_edit.textChanged.connect(clicked)
        
        return name_edit
    
    def make_action_buttons(self, widget: QWidget, layout: QHBoxLayout):
        classes_button = QPushButton("Classes")
        teachers_button = QPushButton("Teachers")
        
        teachers_button.setFixedWidth(100)
        classes_button.setFixedWidth(100)
        
        classes_button.setProperty('class', 'action')
        teachers_button.setProperty('class', 'action')
        
        classes_button.clicked.connect(self.make_show_popup_1(widget))
        teachers_button.clicked.connect(self.make_show_popup_2(widget))
        
        layout.addWidget(classes_button)
        layout.addWidget(teachers_button, alignment=Qt.AlignmentFlag.AlignLeft)
    
    def make_show_popup_1(self, widget: QWidget):
        def show_popup_1():
            current_classes = self.info[widget]["classes"] if "classes" in self.info[widget] else {}
            classes_list = DropDownCheckBoxes("Classes", self.classesInfo, current_classes)
            classes_list.exec()
            self.info[widget]["classes"] = classes_list.get()
        
        return show_popup_1

    def make_show_popup_2(self, widget: QWidget):
        def show_popup_2():
            current_teachers = self.info[widget]["teachers"]
            teachers_list = SelectionList("Teachers", current_teachers)
            teachers_list.exec()
            
            self.teachers = self.teacher_assignments[self.info[widget]["text"]] = self.info[widget]["teachers"] = teachers_list.get()
        
        return show_popup_2



class Teachers(Subjects):
    def __init__(self, subjects: list[str | None] | None):
        super().__init__(None, [])
        self.setObjectName("teacher")
        self.subjects = subjects if subjects is not None else [None]
    
    def make_action_buttons(self, widget: QWidget, layout: QHBoxLayout):
        subjects_button = QPushButton("Subjects")
        
        subjects_button.setProperty('class', 'action')
        
        subjects_button.clicked.connect(self.make_show_popup_1(widget))
        
        subjects_button.setFixedWidth(200)
        
        layout.addWidget(subjects_button, alignment=Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
    
    def make_show_popup_1(self, widget: QWidget):
        def show_popup_1():
            subjects_list = SelectionList("Subjects", self.info[widget]["subjects"])
            subjects_list.exec()
            
            self.subjects = self.info[widget]["subjects"] = subjects_list.get()
        
        return show_popup_1
    
    def set_info(self, widget: QWidget):
        self.info[widget] = {"text": "", "subjects": self.subjects}


class Classes(QWidget):
    def __init__(self, teachers: list[str | None] | None, subjects: list[str]):
        super().__init__()
        
        self.teachers = teachers if teachers is None else [None]
        self.subjects = subjects
        
        self.main_layout = QVBoxLayout(self)
        
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        
        self.container = QWidget()
        self.container_layout = QVBoxLayout(self.container)
        self.scroll_area.setWidget(self.container)
        
        self.add_button = QPushButton("Add Class")
        self.add_button.clicked.connect(self.add)
        
        self.main_layout.addWidget(self.scroll_area)
        self.main_layout.addWidget(self.add_button, alignment=Qt.AlignmentFlag.AlignRight)
        
        self.info = []
        
        self.setLayout(self.main_layout)
        
        self.setStyleSheet(THEME[SUBJECT_TEACHERS_CLASSES])
        # self.add_button.setStyleSheet(main_button_style)
    
    def get(self):
        info = [{k: v for k, v in val.items()} for val in self.info]
        
        for value in info:
            value["text"] = value["widget"].findChild(QLineEdit).text()
            value.pop("widget")
        
        return info
    
    def make_delete_func(self, widget: QWidget):
        def del_widget():
            delete_button = self.sender()
            delete_button.setProperty('class', 'warning')
            self.container_layout.removeWidget(widget)
            widget.deleteLater()
            if widget in self.info:
                self.info.remove(widget)
        
        return del_widget
    
    def add(self):
        widget = QWidget()
        widget.setObjectName("itemContainer")
        widget.setMaximumHeight(150)
        
        layout = QVBoxLayout()
        layout.setSpacing(8)
        layout.setContentsMargins(8, 8, 8, 8)
        widget.setLayout(layout)
        
        header_layout = QVBoxLayout()
        header_layout.setSpacing(8)
        
        name_edit = QLineEdit()
        name_edit.setPlaceholderText("Enter Class Name")
        name_edit.setFixedHeight(80)
        name_edit.setStyleSheet("font-size: 40px;")
        
        def make_clicked_func(index):
            def clicked():
                self.info[index]["text"] = name_edit.text()
            
            return clicked
        
        name_edit.textChanged.connect(make_clicked_func(len(self.info)))
        
        delete_button = QPushButton("×")
        delete_button.setProperty('class', 'warning')
        delete_button.clicked.connect(self.make_delete_func(widget))
        delete_button.setFixedSize(30, 30)
        delete_button.setStyleSheet("padding: 3px;")
        
        # header_layout.addWidget(delete_button, alignment=Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignTop)
        header_layout.addWidget(name_edit)
        
        buttons_layout = QHBoxLayout()
        
        main_buttons_layout = QHBoxLayout()
        
        subjects_button = QPushButton("Subjects")
        options_button = QPushButton("Options")
        subjects_button.setFixedWidth(100)
        options_button.setFixedWidth(100)
        
        subjects_button.setProperty('class', 'action')
        options_button.setProperty('class', 'action')
        
        subjects_button.clicked.connect(self.make_show_subjects_popup_func(widget))
        options_button.clicked.connect(self.make_show_options_popup_func(widget))
        
        main_buttons_layout.addWidget(options_button)
        main_buttons_layout.addWidget(subjects_button, alignment=Qt.AlignmentFlag.AlignLeft)
        
        buttons_layout.addLayout(main_buttons_layout)
        buttons_layout.addWidget(delete_button, alignment=Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignTop)
        
        layout.addLayout(buttons_layout)
        layout.addLayout(header_layout)
        
        self.container_layout.addWidget(widget, alignment=Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignVCenter)
        # self.container_layout.setContentsMargins(0, 0, 0, 0)
        
        self.info.append({"widget": widget, "options": {}, "subjects": {}})
        
        name_edit.show()
        name_edit.setFocus()
    
    def make_show_subjects_popup_func(self, widget: QWidget):
        def show_subjects_popup():
            info_entry = next((item for item in self.info if item["widget"] == widget), None)
            if info_entry:
                subjects = SubjectSelection("Subjects", self.subjects, self.teachers, info_entry["subjects"])
                subjects.exec()
                info_entry["subjects"] = subjects.get()
        
        return show_subjects_popup

    def make_show_options_popup_func(self, widget: QWidget):
        def show_options_popup():
            info_entry = next((item for item in self.info if item["widget"] == widget), None)
            if info_entry:
                option_selector = ClassOptionSelection("Options Selection", info_entry["options"])
                option_selector.exec()
                info_entry["options"] = option_selector.get()
        
        return show_options_popup


