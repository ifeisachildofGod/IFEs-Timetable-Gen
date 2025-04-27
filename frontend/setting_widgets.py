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


class Subjects(QWidget):
    def __init__(self):
        super().__init__()
        self.objectNameChanged.connect(lambda: self.add_button.setText(f"Add {self.objectName().title()}"))
        
        self.widget_id_mapping = {}
        
        self.info = {}
        
        self.teachers = [None]
        self.id_mapping = {}
        
        self.classesInfo = {}
        
        self.main_layout = QVBoxLayout(self)
        
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        
        self.container = QWidget()
        self.container_layout = QVBoxLayout(self.container)
        self.container_layout.addStretch()
        self.scroll_area.setWidget(self.container)
        
        self.add_button = QPushButton()
        self.add_button.clicked.connect(self.add)
        
        self.main_layout.addWidget(self.scroll_area)
        self.main_layout.addWidget(self.add_button, alignment=Qt.AlignmentFlag.AlignRight)
        
        self.list_selection_values = None
        
        self.setLayout(self.main_layout)
        
        self.setObjectName("subject")
        self.setStyleSheet(THEME[SUBJECT_TEACHERS_CLASSES])
    
    def get(self):
        return self.info
    
    def add(self):
        widget = QWidget()
        widget.setObjectName("itemContainer")
        widget.setMaximumHeight(150)
        
        layout = QVBoxLayout()
        widget.setLayout(layout)
        
        header_layout = QHBoxLayout()
        buttons_layout = QHBoxLayout()
        
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
        
        self.container_layout.insertWidget(self.container_layout.count() - 1, widget, alignment=Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignVCenter)
        
        self.set_info(widget)
        
        name_edit.returnPressed.connect(lambda: name_edit.clearFocus())
        name_edit.show()
        name_edit.setFocus()
    
    def set_info(self, widget: QWidget):
        self.widget_id_mapping[widget] = "--" + str(len(self.info) * 1000) + "--"
        self.info[self.widget_id_mapping[widget]] = {"text": "", "classes": {"content": {}, "id_mapping": {}}, "teachers": {"content": self.teachers.copy(), "id_mapping": self.id_mapping.copy()}}
    
    def make_delete_func(self, widget: QWidget):
        def del_widget():
            delete_button = self.sender()
            delete_button.setProperty('class', 'warning')
            self.container_layout.removeWidget(widget)
            widget.deleteLater()
            self.info.pop(self.widget_id_mapping[widget])
        
        return del_widget
    
    def make_input(self, widget: QWidget):
        name_edit = QLineEdit()
        name_edit.setPlaceholderText(f"Enter {self.objectName().title()} Name")
        name_edit.setFixedHeight(80)
        name_edit.setStyleSheet("font-size: 40px;")
        
        def clicked():
            self.info[self.widget_id_mapping[widget]]["text"] = name_edit.text()
        
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
            classes_list = DropDownCheckBoxes("Classes", self.classesInfo, self.info[self.widget_id_mapping[widget]]["classes"])
            classes_list.exec()
            self.info[self.widget_id_mapping[widget]]["classes"] = classes_list.get()
        
        return show_popup_1
    
    def make_show_popup_2(self, widget: QWidget):
        def show_popup_2():
            teachers_list = SelectionList("Teachers", self.info[self.widget_id_mapping[widget]]["teachers"])
            teachers_list.exec()
            
            self.info[self.widget_id_mapping[widget]]["teachers"] = teachers_list.get()
        
        return show_popup_2


class Teachers(Subjects):
    def __init__(self):
        super().__init__()
        
        self.subject = [None]
        self.setObjectName("teacher")
    
    def make_action_buttons(self, widget: QWidget, layout: QHBoxLayout):
        subjects_button = QPushButton("Subjects")
        
        subjects_button.setProperty('class', 'action')
        
        subjects_button.clicked.connect(self.make_show_popup_1(widget))
        
        subjects_button.setFixedWidth(200)
        
        layout.addWidget(subjects_button, alignment=Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
    
    def make_show_popup_1(self, widget: QWidget):
        def show_popup_1():
            subjects_list = SelectionList("Subjects", self.info[self.widget_id_mapping[widget]]["subjects"])
            subjects_list.exec()
            
            self.info[self.widget_id_mapping[widget]]["subjects"] = subjects_list.get()
        
        return show_popup_1
    
    def set_info(self, widget: QWidget):
        self.widget_id_mapping[widget] = ".." + str(len(self.info) * 1000) + ".."
        self.info[self.widget_id_mapping[widget]] = {"text": "", "subjects": {"content": self.subject.copy(), "id_mapping": self.id_mapping.copy()}}


class Classes(QWidget):
    def __init__(self):
        super().__init__()
        self.widget_id_mapping = {}
        
        self.subject_teachers_mapping = {}
        
        self.main_layout = QVBoxLayout(self)
        
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        
        self.container = QWidget()
        self.container_layout = QVBoxLayout(self.container)
        self.container_layout.addStretch()
        self.scroll_area.setWidget(self.container)
        
        self.add_button = QPushButton("Add Class")
        self.add_button.clicked.connect(self.add)
        
        self.main_layout.addWidget(self.scroll_area)
        self.main_layout.addWidget(self.add_button, alignment=Qt.AlignmentFlag.AlignRight)
        
        self.info = {}
        
        self.setLayout(self.main_layout)
        
        self.setStyleSheet(THEME[SUBJECT_TEACHERS_CLASSES])
    
    def get(self):
        return dict(self.info)
    
    def make_delete_func(self, widget: QWidget):
        def del_widget():
            delete_button = self.sender()
            delete_button.setProperty('class', 'warning')
            self.container_layout.removeWidget(widget)
            widget.deleteLater()
            self.info.pop(self.widget_id_mapping[widget])
        
        return del_widget
    
    def make_clicked_func(self, widget: QWidget, name_edit: QLineEdit):
        def clicked():
            info_entry = self.info[self.widget_id_mapping[widget]]
            info_entry["text"] = name_edit.text()
        
        return clicked
    
    def add(self):
        widget = QWidget()
        widget.setObjectName("itemContainer")
        widget.setMaximumHeight(150)
        
        layout = QVBoxLayout()
        widget.setLayout(layout)
        
        header_layout = QVBoxLayout()
        
        name_edit = QLineEdit()
        name_edit.setPlaceholderText("Enter Class Name")
        name_edit.setFixedHeight(80)
        name_edit.setStyleSheet("font-size: 40px;")
        
        name_edit.textChanged.connect(self.make_clicked_func(widget, name_edit))
        
        delete_button = QPushButton("×")
        delete_button.setProperty('class', 'warning')
        delete_button.clicked.connect(self.make_delete_func(widget))
        delete_button.setFixedSize(30, 30)
        delete_button.setStyleSheet("padding: 3px;")
        
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
        
        self.container_layout.insertWidget(self.container_layout.count() - 1, widget, alignment=Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignVCenter)
        
        self.set_info(widget)
        
        name_edit.show()
        name_edit.setFocus()
    
    def set_info(self, widget: QWidget):
        self.widget_id_mapping[widget] = "<<" + str(len(self.info) * 1000) + "<<"
        self.info[self.widget_id_mapping[widget]] = {"text": "", "options": {}, "subjects": {"content": {}, "id_mapping": {index : index_id for index, (index_id, _) in enumerate(self.subject_teachers_mapping.items())}}}
    
    def make_show_subjects_popup_func(self, widget: QWidget):
        def show_subjects_popup():
            info_entry = self.info[self.widget_id_mapping[widget]]
            
            subjects = SubjectSelection("Subjects", self.subject_teachers_mapping, info_entry["subjects"])
            subjects.exec()
            info_entry["subjects"] = subjects.get()
        
        return show_subjects_popup
    
    def make_show_options_popup_func(self, widget: QWidget):
        def show_options_popup():
            info_entry = self.info[self.widget_id_mapping[widget]]
            
            option_selector = OptionSelection("Options Selection", info_entry["options"])
            option_selector.exec()
            info_entry["options"] = option_selector.get()
        
        return show_options_popup


