import threading
import time
from typing import Callable
from matplotlib.cbook import flatten
from frontend.sub_widgets import (
    SelectionList, DropDownCheckBoxes, SubjectSelection,
    ClassOptionSelection, DraggableSubjectLabel, TimeTableItem,
    NumberTextEdit
    )
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QLineEdit, QPushButton, QScrollArea,
    QTableWidget, QLabel, QFrame,
    QAbstractItemView, QHeaderView, QMenu, QSizePolicy,
    QProgressBar
)

from PyQt6.QtGui import QDrag, QDragEnterEvent, QDragMoveEvent, QDropEvent
from PyQt6.QtCore import Qt, QMimeData, QThread, QTimer
from frontend.theme import *

from middle.main import School
from middle.objects import Class

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
        
        self.container_layout.insertWidget(self.container_layout.count() - 1, widget, alignment=Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignVCenter)
        
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
        self.container_layout.addStretch()
        self.scroll_area.setWidget(self.container)
        
        self.add_button = QPushButton("Add Class")
        self.add_button.clicked.connect(self.add)
        
        self.main_layout.addWidget(self.scroll_area)
        self.main_layout.addWidget(self.add_button, alignment=Qt.AlignmentFlag.AlignRight)
        
        self.info = []
        
        self.setLayout(self.main_layout)
        
        self.setStyleSheet(THEME[SUBJECT_TEACHERS_CLASSES])
    
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
        
        self.container_layout.insertWidget(self.container_layout.count() - 1, widget, alignment=Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignVCenter)
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

class GenerateNewSchoolThread(QThread):
    def __init__(self, editor: 'TimeTableEditor'):
        super().__init__()
        self.editor = editor
    
    def run(self):
        self.editor.school.generateNewSchoolTimetables()
    
class TimeTableEditor(QWidget):
    def __init__(self, school: School):
        super().__init__()
        self.school = school
        
        self.can_generate_new = True
        self.thread_generate_new = GenerateNewSchoolThread(self)
        
        self.setStyleSheet(THEME[TIMETABLE_EDITOR])
        
        self.main_layout = QVBoxLayout(self)
        
        self.external_source_ref = None
        
        # Create settings for timetables
        self.settings_widget = QWidget()
        self.settings_widget_layout = QHBoxLayout()
        
        self.settings_widget.setLayout(self.settings_widget_layout)
        
        generate_new_timetable = QPushButton("Generate New")
        generate_new_timetable.clicked.connect(self.generate_new_school_timetable)
        
        self.progress = 0
        self.progress_timer = QTimer()
        self.progress_timer.timeout.connect(self.update_progress_bar)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        
        self.settings_widget_layout.addWidget(self.progress_bar, alignment=Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignLeft)
        self.settings_widget_layout.addWidget(generate_new_timetable, alignment=Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignRight)
        
        # Create scroll area for timetables
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        # Container for all timetables
        self.timetables_container = QWidget()
        self.timetables_layout = QVBoxLayout(self.timetables_container)
        self.scroll_area.setWidget(self.timetables_container)
        
        # Create timetable for each class
        self.timetable_widgets: dict[str, _ClassTimetable] = {}
        for index, (class_name, cls) in enumerate(self.school.classes.items()):
            remainder_labels = []
            
            # Create class header with separator
            if index != 0:
                separator = QFrame()
                separator.setFrameShape(QFrame.Shape.HLine)
                separator.setStyleSheet("background-color: #3d3d3d;")
                self.timetables_layout.addWidget(separator)
            
            class_header = QLabel(f"Class: {class_name}")
            class_header.setStyleSheet("font-weight: bold; padding: 10px;")
            self.timetables_layout.addWidget(class_header)
            
            # Create timetable
            class_widget = QWidget()
            class_widget_layout = QHBoxLayout(class_widget)
            
            sidebar_widget = QWidget()
            sidebar_widget.setStyleSheet("background-color: #1b1a1a;")
            sidebar_widget_layout = QVBoxLayout(sidebar_widget)
            
            remainder_widget = QScrollArea()
            remainder_widget.setStyleSheet("background-color: #3f3f3f")
            remainder_widget.setFixedWidth(150)
            remainder_widget_layout = QVBoxLayout(remainder_widget)
            
            settings_widget = QScrollArea()
            settings_widget.setStyleSheet("background-color: #3f3f3f")
            settings_widget.setFixedSize(150, 100)
            settings_widget_layout = QVBoxLayout(settings_widget)
            self.get_timetable_settings(settings_widget_layout)
            
            sidebar_widget_layout.addWidget(remainder_widget, alignment=Qt.AlignmentFlag.AlignHCenter)
            sidebar_widget_layout.addWidget(settings_widget, alignment=Qt.AlignmentFlag.AlignHCenter)
            
            remainder_title = QLabel("Remaining Subjects")
            remainder_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
            remainder_widget_layout.addWidget(remainder_title, alignment=Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop)
            
            remainder_widget_layout.addStretch()
            
            table = _ClassTimetable(cls, self, class_name, remainder_labels, remainder_widget_layout)
            self.timetable_widgets[class_name] = table
            
            class_widget_layout.addWidget(table)
            class_widget_layout.addWidget(sidebar_widget)
            
            self.timetables_layout.addWidget(class_widget)
        
        self.main_layout.addWidget(self.settings_widget)
        self.main_layout.addWidget(self.scroll_area)
        
        self.total_subjects = sum([len(names) * (sum(periods) - (len(periods))) for _, (names, periods, _) in self.school.project["levels"].items()])
    
    def update_progress_bar(self):
        added_subjects = sum([sum([sum([s.total for s in subjects]) - 1 for _, subjects in timetable.table.items()]) for _, timetable in self.school.school.items()])
        
        self.progress = int((added_subjects / self.total_subjects) * 100)
        if self.progress < 100:
            self.progress_bar.setValue(self.progress)
        elif self.progress < 110:
            self.progress_timer.stop()
            self.progress_bar.setVisible(False)
    
    def _set_school_timetable(self):
        self.can_generate_new = True
        for class_name, _ in self.school.classes.items():
            self.timetable_widgets[class_name].populate_timetable()
    
    def generate_new_school_timetable(self):
        if self.can_generate_new:
            self.can_generate_new = False
            
            self.progress_timer.start(100)
            self.progress_bar.setVisible(True)
            
            self.thread_generate_new = GenerateNewSchoolThread(self)
            self.thread_generate_new.finished.connect(self._set_school_timetable)
            self.thread_generate_new.start()
    
    def make_ds_func(self, label: DraggableSubjectLabel):
        def func(event):
            self.external_source_ref = label
            
            drag = QDrag(label)
            mime_data = QMimeData()
            mime_data.setText(label.subject.name)
            drag.setMimeData(mime_data)
            
            # Create drag feedback
            pixmap = label.grab()
            drag.setPixmap(pixmap)
            drag.setHotSpot(event.pos())
            
            drag.exec()
        
        return func

    def get_timetable_settings(self, layout: QVBoxLayout):
        periods_edit = NumberTextEdit()
        periods_edit.edit.setFixedWidth(60)
        periods_edit.edit.setPlaceholderText("Periods Amt")
        
        break_period_edit = NumberTextEdit()
        break_period_edit.edit.setFixedWidth(60)
        break_period_edit.edit.setPlaceholderText("Break period")
        
        generate_new_button = QPushButton("Generate New")
        reset_button = QPushButton("Reset")
        
        buttons_layout = QHBoxLayout()
        buttons_widget = QWidget()
        buttons_widget.setLayout(buttons_layout)
        
        edits_layout = QHBoxLayout()
        edits_widget = QWidget()
        edits_widget.setLayout(edits_layout)
        
        buttons_layout.addWidget(generate_new_button)
        buttons_layout.addWidget(reset_button)
        
        edits_layout.addWidget(periods_edit)
        edits_layout.addWidget(break_period_edit)
        
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(buttons_widget)
        layout.addWidget(edits_widget)

class _ClassTimetable(QTableWidget):
    def __init__(self, cls: Class, editor: TimeTableEditor, name: str, remainder_labels: list[DraggableSubjectLabel], remainder_layout: QVBoxLayout):
        super().__init__()
        self.name = name
        self.cls = cls
        self.timetable = cls.timetable
        self.editor = editor
        
        self.remainder_labels = remainder_labels
        self.remainder_layout = remainder_layout
        
        # Configure table
        self.setRowCount(max(self.timetable.periodsPerDay))
        self.setColumnCount(len(self.timetable.weekInfo))
        self.setHorizontalHeaderLabels([day[0] for day in self.timetable.weekInfo])
        self.setVerticalHeaderLabels([f"Period {i+1}" for i in range(self.rowCount())])
        
        # Set size policies
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.setFixedHeight(self.rowCount() * 30 + 40)  # Adjust row height + header
        
        # Enable drag & drop
        self.setDragEnabled(True)
        self.setAcceptDrops(True)
        self.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.setDragDropMode(QAbstractItemView.DragDropMode.DragDrop)
        
        # Configure headers
        self.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.verticalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Fixed)
        
        # Connect context menu
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_context_menu)
        
        # Load initial data
        self.populate_timetable()
        
        # Variables
        self.current_source = None
    
    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasText():
            row = self.rowAt(int(event.position().y()))
            col = self.columnAt(int(event.position().x()))
            
            source = self.item(row, col)
            
            if source is not None:
                event.accept()
                if self.editor.external_source_ref is None:
                    self.current_source = self.item(self.rowAt(int(event.position().y())), self.columnAt(int(event.position().x())))
    
    def dragMoveEvent(self, event: QDragMoveEvent):
        if event.mimeData().hasText():
            col = self.columnAt(int(event.position().x()))
            row = self.rowAt(int(event.position().y()))
            
            if row != self.cls.breakTimePeriods[col] - 1:
                event.accept()
            else:
                event.ignore()

    def dropEvent(self, event: QDropEvent):
        if event.mimeData().hasText():
            if self.current_source is not None:
                row = self.rowAt(int(event.position().y()))
                col = self.columnAt(int(event.position().x()))
                target_item = self.item(row, col)
                
                source_subject = self.current_source.subject
                source_class = self.editor.timetable_widgets[self.name].cls
                source_widget = self.current_source.tableWidget()
                source_row = source_widget.row(self.current_source)
                source_col = source_widget.column(self.current_source)
                
                # Handle swapping
                if target_item and isinstance(target_item, TimeTableItem) and target_item.subject:
                    target_subject = target_item.subject
                    
                    if source_class == self.cls:
                        # Same timetable swap
                        self.blockSignals(True)  # Prevent unnecessary updates
                        
                        # Create new items
                        new_target = TimeTableItem(source_subject)
                        new_source = TimeTableItem(target_subject)
                        
                        # Remove old items
                        source_widget.takeItem(source_row, source_col)
                        self.takeItem(row, col)
                        
                        # Set new items
                        self.setItem(row, col, new_target)
                        source_widget.setItem(source_row, source_col, new_source)
                        
                        self.blockSignals(False)
                        
                        # Force refresh
                        self.update()
                        source_widget.update()
                        
                        self.save_timetable()
                        event.accept()
                        
                        del target_item
            elif self.editor.external_source_ref is not None:
                row = self.rowAt(int(event.position().y()))
                col = self.columnAt(int(event.position().x()))
                target_item = self.item(row, col)
                
                self.blockSignals(True)  # Prevent unnecessary updates
                
                new_target = TimeTableItem(self.editor.external_source_ref.subject)
                
                self.takeItem(row, col)
                self.setItem(row, col, new_target)
                
                if target_item and isinstance(target_item, TimeTableItem) and target_item.subject:
                    target_subject = target_item.subject
                    
                    # Create new items
                    new_source = DraggableSubjectLabel(target_subject, self.cls)
                    new_source.clicked.connect(self.editor.make_ds_func(new_source))
                    
                    # Set new items
                    self.add_remainder(new_source, self.remainder_layout.indexOf(self.editor.external_source_ref))
                
                # Remove remainder widget
                self.remainder_labels.remove(self.editor.external_source_ref)
                self.remainder_layout.removeWidget(self.editor.external_source_ref)
                # self.timetable.remainderContent.remove(self.editor.external_source_ref.subject)
                self.editor.external_source_ref.deleteLater()
                
                self.remainder_layout.update()
                
                self.blockSignals(False)
                
                # Force refresh
                self.save_timetable()
                event.accept()
            
            self.editor.external_source_ref = None
            self.current_source = None
    
    def add_remainder(self, remainder: DraggableSubjectLabel, index: int | None = None):
        if index is not None:
            self.remainder_layout.insertWidget(index, remainder, alignment=Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop)
        else:
            self.remainder_layout.insertWidget(self.remainder_layout.count() - 1, remainder, alignment=Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop)
        self.remainder_labels.append(remainder)
        self.timetable.remainderContent.append(remainder.subject)
    
    def save_timetable(self):
        """Save current grid state back to timetable"""
        for col, (day, _, _) in enumerate(self.timetable.weekInfo):
            subjects = []
            for row in range(self.rowCount()):
                item = self.item(row, col)
                if isinstance(item, TimeTableItem) and item.subject:
                    subjects.append(item.subject)
            self.timetable.table[day] = subjects
    
    def populate_timetable(self):
        """Load the timetable data into the grid"""
        for col, (day, _, _) in enumerate(self.timetable.weekInfo):
            subjects = list(flatten([[subj for _ in range(subj.total)] for subj in self.timetable.table[day]])) + [None for _ in range(max(self.timetable.periodsPerDay) - len(self.timetable.table[day]))]
            
            for row, subject in enumerate(subjects):
                item = TimeTableItem(subject, row + 1 == self.cls.breakTimePeriods[col])
                self.setItem(row, col, item)
        
        for label in self.remainder_layout.findChildren(DraggableSubjectLabel):
            self.remainder_layout.removeWidget(label)
        self.remainder_labels = []
        
        subjects = flatten([[subj for _ in range(subj.total)] for subj in self.cls.timetable.remainderContent])
        for subject in subjects:
            subject_label = DraggableSubjectLabel(subject, self.cls)
            subject_label.clicked.connect(self.editor.make_ds_func(subject_label))
            
            self.remainder_labels.append(subject_label)
            self.remainder_layout.insertWidget(self.remainder_layout.count() - 1, subject_label, alignment=Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop)
    
    def show_context_menu(self, pos):
        item = self.itemAt(pos)
        if item and isinstance(item, TimeTableItem):
            menu = QMenu(self)
            delete_action = menu.addAction("Delete")
            if item.subject.lockedPeriod:
                menu.addAction("Unlock Period")
            else:
                menu.addAction("Lock to Period")
            
            action = menu.exec(self.viewport().mapToGlobal(pos))
            
            if action == delete_action:
                # Move to remainders if deleted
                subject_label = DraggableSubjectLabel(item.subject, self.cls)
                subject_label.clicked.connect(self.editor.make_ds_func(subject_label))
                
                self.add_remainder(subject_label)
                
                self.setItem(self.row(item), self.column(item), TimeTableItem())
                self.save_timetable()
            elif action and action.text() == "Lock to Period":
                item.subject.lockedPeriod = [self.row(item), 1]  # Lock to current period
                item.locked = True
            elif action and action.text() == "Unlock Period":
                item.subject.lockedPeriod = None
    
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            item = self.itemAt(event.pos())
            if item and isinstance(item, TimeTableItem) and item.subject:
                # Store original position
                self.drag_source_row = self.row(item)
                self.drag_source_col = self.column(item)
                
                drag = QDrag(self)
                mime_data = QMimeData()
                mime_data.setText(item.subject.name)
                drag.setMimeData(mime_data)
                
                # Create drag feedback by grabbing the cell widget
                cell_rect = self.visualItemRect(item)
                pixmap = self.viewport().grab(cell_rect)
                drag.setPixmap(pixmap)
                drag.setHotSpot(event.pos() - cell_rect.topLeft())
                
                drag.exec()
        
        super().mousePressEvent(event)


