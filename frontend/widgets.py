from matplotlib.cbook import flatten
from frontend.sub_widgets import (
    SelectionList, DropDownCheckBoxes, SubjectSelection,
    ClassOptionSelection, DraggableSubjectLabel, TimeTableItem
    )
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QLineEdit, QPushButton, QScrollArea,
    QTableWidget, QLabel,QFrame,
    QAbstractItemView, QHeaderView, QMenu, QSizePolicy
)

from PyQt6.QtGui import QDrag, QDragEnterEvent, QDragMoveEvent, QDropEvent
from PyQt6.QtCore import Qt, QMimeData
from frontend.theme import *
from frontend.theme import (_widget_fg_color, _widget_border_radius_1, _widget_text_color_2)

from middle.constants import BREAKTIMEPERIOD
from middle.main import School
from middle.objects import Class, Subject

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


class TimeTableEditor(QWidget):
    def __init__(self, school: School):
        super().__init__()
        self.school = school
        
        self.setStyleSheet(THEME[TIMETABLE_EDITOR])
        
        self.main_layout = QHBoxLayout(self)
        
        # Create scroll area for timetables
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        # Container for all timetables
        self.timetables_container = QWidget()
        self.timetables_layout = QVBoxLayout(self.timetables_container)
        self.scroll_area.setWidget(self.timetables_container)
        
        # Create right sidebar for remaining subjects
        self.sidebar = QWidget()
        self.sidebar.setFixedWidth(200)
        self.sidebar_layout = QVBoxLayout(self.sidebar)
        self.sidebar_layout.setSpacing(4)
        
        # Create scrollable container for remainders
        self.remainder_scroll = QScrollArea()
        self.remainder_scroll.setWidgetResizable(True)
        self.remainder_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        self.remainder_container = QWidget()
        self.remainder_layout = QVBoxLayout(self.remainder_container)
        self.remainder_layout.setSpacing(4)
        self.remainder_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        # Add title for remainders
        remainder_title = QLabel("Remaining Subjects")
        remainder_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.remainder_layout.addWidget(remainder_title)
        
        self.remainder_scroll.setWidget(self.remainder_container)
        self.sidebar_layout.addWidget(self.remainder_scroll)
        
        # Variables
        self.remainder_labels = []
        
        # Create timetable for each class
        self.timetable_widgets = {}
        for class_name, cls in self.school.classes.items():
            # Create class header with separator
            separator = QFrame()
            separator.setFrameShape(QFrame.Shape.HLine)
            separator.setStyleSheet("background-color: #3d3d3d;")
            self.timetables_layout.addWidget(separator)
            
            class_header = QLabel(f"Class: {class_name}")
            class_header.setStyleSheet("font-weight: bold; padding: 10px;")
            self.timetables_layout.addWidget(class_header)
            
            # Create timetable
            table = _ClassTimetable(cls, self, class_name, self.remainder_labels, self.remainder_layout)
            self.timetable_widgets[class_name] = table
            self.timetables_layout.addWidget(table)
            
            # Add remainders to sidebar
            self.update_remainders(cls)
        
        self.main_layout.addWidget(self.scroll_area, stretch=4)
        self.main_layout.addWidget(self.sidebar, stretch=1)
    
    def update_remainders(self, cls: Class):
        # Add remaining subjects to sidebar with class label
        class_label = QLabel(f"{cls.name} Remainders:")
        class_label.setStyleSheet("font-weight: bold; padding: 4px;")
        self.remainder_layout.addWidget(class_label)
        
        subjects = flatten([[subj for _ in range(subj.total)] for subj in cls.timetable.remainderContent])
        for subject in subjects:
            subject_label = DraggableSubjectLabel(subject, cls)
            self.remainder_labels.append(subject_label)
            self.remainder_layout.addWidget(subject_label)


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
        self.setFixedHeight(self.rowCount() * 40 + 60)  # Adjust row height + header
        
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
        self.remainder_source = None
    
    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasText():
            row = self.rowAt(int(event.position().y()))
            col = self.columnAt(int(event.position().x()))
            
            source = self.item(row, col)
            
            if source is not None:
                if source.subject.name.lower() != 'break':
                    event.accept()
                    
                    self.remainder_source = [label.external_source_ref for label in self.remainder_labels]
                    if self.remainder_source.count(None) == len(self.remainder_source):
                        self.current_source = self.item(self.rowAt(int(event.position().y())), self.columnAt(int(event.position().x())))
                    else:
                        self.remainder_source = [label for label in self.remainder_source if label is not None][0]
    
    def dragMoveEvent(self, event: QDragMoveEvent):
        if event.mimeData().hasText():
            row = self.rowAt(int(event.position().y()))
            
            if row != BREAKTIMEPERIOD - 1:
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
            elif self.remainder_source is not None:
                row = self.rowAt(int(event.position().y()))
                col = self.columnAt(int(event.position().x()))
                target_item = self.item(row, col)
                
                self.blockSignals(True)  # Prevent unnecessary updates
                new_target = TimeTableItem(self.remainder_source.subject)
                
                self.takeItem(row, col)
                self.setItem(row, col, new_target)
                
                if target_item and isinstance(target_item, TimeTableItem) and target_item.subject:
                    target_subject = target_item.subject
                    
                    # Create new items
                    new_source = DraggableSubjectLabel(target_subject, self.cls)
                    
                    # Set new items
                    self.remainder_layout.insertWidget(self.remainder_layout.indexOf(self.remainder_source), new_source)
                    
                    self.timetable.remainderContent.append(Subject(new_source.subject.name, 1, new_source.subject.perWeek, new_source.subject.teacher, new_source.subject.schoolSubjectsList))
                
                # Remove remainder widget
                self.remainder_labels.remove(self.remainder_source)
                self.remainder_layout.removeWidget(self.remainder_source)
                
                # Add Replacement
                self.blockSignals(False)
                
                # Force refresh
                self.save_timetable()
                event.accept()
                
            self.current_source = None
            self.remainder_source = None
    
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
                item = TimeTableItem(subject)
                self.setItem(row, col, item)
    
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
                new_remainder_subject = Subject(item.subject.name, 1, item.subject.perWeek, item.subject.teacher, item.subject.schoolSubjectsList)
                self.timetable.remainderContent.append(new_remainder_subject)
                
                label_index = 0
                pot_label = None
                for label_index, pot_label in enumerate(self.remainder_layout.children()):
                    if isinstance(pot_label, QLabel):
                        if self.name in pot_label.text():
                            break
                
                self.remainder_layout.insertWidget(label_index + 2, DraggableSubjectLabel(new_remainder_subject, self.cls))
                self.remainder_layout.update()
                
                self.setItem(self.row(item), self.column(item), None)
                self.save_timetable()
            elif action and action.text() == "Lock to Period":
                item.subject.lockedPeriod = [self.row(item), 1]  # Lock to current period
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


