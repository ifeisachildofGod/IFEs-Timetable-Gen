from typing import Callable
from matplotlib.cbook import flatten
from frontend.sub_widgets import (
    CustomLabel, OptionSelection, DraggableSubjectLabel,
    TimeTableItem, NumberTextEdit, WarningDialog
    )
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QLineEdit, QPushButton, QScrollArea,
    QTableWidget, QLabel, QFrame,
    QAbstractItemView, QHeaderView, QMenu, QSizePolicy,
    QProgressBar, QCheckBox
)

from PyQt6.QtGui import QDrag, QDragEnterEvent, QDragMoveEvent, QDropEvent
from PyQt6.QtCore import Qt, QMimeData, QThread, QTimer
from frontend.theme import *
from frontend.theme import _widgets_bg_color_6

from middle.main import School, Class


class _GenerateNewSchoolThread(QThread):
    def __init__(self, run_func: Callable, threads_list: list['_GenerateNewSchoolThread']):
        super().__init__()
        self.run_func = run_func
        threads_list.append(self)
        self.finished.connect(lambda: threads_list.remove(self))
    
    def run(self):
        self.run_func()

class _ProgressBar(QProgressBar):
    def __init__(self, master: QWidget):
        super().__init__()
        
        self.update_var = None
        self.update_max = None
        
        self.progress = 0
        self.progress_timer = QTimer()
        self.progress_timer.timeout.connect(self.update_progress_bar)
        
        self.master = master
        
        if self.master:
            self.master.setVisible(False)
        else:
            self.setVisible(False)
    
    def start(self, mst: int):
        self.progress_timer.start(mst)
        if self.master:
            self.master.setVisible(True)
        else:
            self.setVisible(True)
    
    def set_var_func(self, update_var: Callable[[], int]):
        self.update_var = update_var
    
    def set_max(self, update_max: Callable[[], int]):
        self.update_max = update_max
    
    def update_progress_bar(self):
        self.progress = int((self.update_var() / self.update_max()) * 100)
        
        if self.progress >= 100:
            self.progress_timer.stop()
            if self.master:
                self.master.setVisible(False)
            else:
                self.setVisible(False)
        else:
            self.setValue(self.progress)

class _TimetableSettings(QWidget):
    def __init__(self, editor: 'TimeTableEditor', progress_bar: _ProgressBar, threads_list: list[_GenerateNewSchoolThread]):
        super().__init__()
        self.editor = editor
        self.threads_list = threads_list
        
        self.thread_generate_new = _GenerateNewSchoolThread(self._generate, self.threads_list)
        
        self._can_generate_new = True
        self.continue_refresh = True
        self.warning_dont_ask_again = True
        
        self.refresh_warning = WarningDialog("INFORMATION WILL BE LOST", "By doing this, all information in all timetables will be overwritten, no exceptions are made\nDo you want to proceed with this action?")
        self.refresh_warning.button_clicked.connect(self._dailog_clicked_func)
        self.refresh_warning.checkbox_on.connect(self._dailog_dont_ask_again)
        
        self.main_layout = QVBoxLayout()
        self.setLayout(self.main_layout)
        
        self.main_settings_widget = QWidget()
        
        self.main_settings_layout = QVBoxLayout()
        self.main_settings_widget.setLayout(self.main_settings_layout)
        
        options_widget = QWidget()
        
        options_layout = QHBoxLayout()
        options_widget.setLayout(options_layout)
        
        self.toogle_button = CustomLabel("▼", 0)
        self.toogle_button.setStyleSheet("QLabel{background-color: " + _widgets_bg_color_6 + "; padding: 10px; border-top-right-radius: 10px; border-bottom-right-radius: 10px;} QLabel:hover{background-color: " + get_hover_color(_widgets_bg_color_6) +";}")
        self.toogle_button.mouseclicked.connect(self._toogle)
        
        self.options_info = CustomLabel("Expand Options")
        self.options_info.setStyleSheet("QLabel{background-color: " + _widgets_bg_color_6 + "; padding: 10px; border-top-left-radius: 10px; border-bottom-left-radius: 10px;} QLabel:hover{background-color: " + get_hover_color(_widgets_bg_color_6) +";}")
        self.options_info.mouseclicked.connect(self._toogle)
        
        options_layout.addStretch()
        options_layout.addWidget(self.options_info, alignment=Qt.AlignmentFlag.AlignRight)
        options_layout.addWidget(self.toogle_button, alignment=Qt.AlignmentFlag.AlignRight)
        
        self.main_layout.addWidget(options_widget)
        self.main_layout.addWidget(self.main_settings_widget)
        
        timetable_settings_widget = QWidget()
        timetable_settings_layout = QHBoxLayout()
        timetable_settings_widget.setLayout(timetable_settings_layout)
        
        general_settings_widget = QWidget()
        general_settings_layout = QHBoxLayout()
        general_settings_widget.setLayout(general_settings_layout)
        general_settings_widget.setStyleSheet(THEME[TIMETABLE_SETTINGS])
        
        self.progress_bar = progress_bar
        
        left_option_widget = QWidget()
        left_option_layout = QVBoxLayout()
        left_option_widget.setLayout(left_option_layout)
        
        self.breakperiod_edit = NumberTextEdit(1, min([widg.periods for widg in  self.editor.timetable_widgets.values()]))
        self.breakperiod_edit.edit.setPlaceholderText("Break period")
        self.period_amt_edit = NumberTextEdit(1, 100)
        self.period_amt_edit.edit.setPlaceholderText("Period amount")
        
        left_sub_option_widget = QWidget()
        
        left_sub_option_layout = QHBoxLayout()
        left_sub_option_widget.setLayout(left_sub_option_layout)
        
        self.set_days_of_the_week = list(self.editor.school.classes.values())[0].weekdays
        self.days_of_the_week_selector = OptionSelection("Days of the week", self.set_days_of_the_week)
        
        dotw_button = QPushButton("Days of the Week")
        dotw_button.clicked.connect(self.show_dotw_editor)
        show_clashes_checkb = QCheckBox("Show clashes")
        
        left_sub_option_layout.addWidget(dotw_button)
        left_sub_option_layout.addWidget(show_clashes_checkb)
        
        left_option_layout.addWidget(self.breakperiod_edit)
        left_option_layout.addWidget(self.period_amt_edit)
        left_option_layout.addWidget(left_sub_option_widget)
        
        right_option_widget = QWidget()
        right_option_layout = QVBoxLayout()
        right_option_widget.setLayout(right_option_layout)
        
        generate_button = QPushButton("Generate New")
        generate_button.setProperty("class", "safety")
        generate_button.clicked.connect(self.generate_new_school_timetable)
        
        refresh_button = QPushButton("Refresh")
        refresh_button.clicked.connect(self.refresh)
        
        right_option_layout.addWidget(generate_button)
        right_option_layout.addWidget(refresh_button)
        
        general_settings_layout.addWidget(left_option_widget)
        general_settings_layout.addStretch()
        general_settings_layout.addWidget(right_option_widget)
        
        self.main_settings_layout.addWidget(general_settings_widget)
        self.main_settings_layout.addWidget(timetable_settings_widget)
        
        self.main_settings_widget.setVisible(False)
    
    def _dailog_dont_ask_again(self):
        self.warning_dont_ask_again = False
    
    def _dailog_clicked_func(self, ok_clicked: bool):
        self.continue_refresh = ok_clicked
    
    def _generating_finished(self):
        self._can_generate_new = True
        self.editor._set_school_timetable()
    
    def _refresh(self):
        for _, timetable in self.editor.timetable_widgets.items():
            period_amt = int(self.period_amt_edit.edit.text()) if self.period_amt_edit.edit.text().isnumeric() else None
            breaktime_period = int(self.breakperiod_edit.edit.text()) if self.breakperiod_edit.edit.text().isnumeric() else None
            
            self.timetable_refresh(period_amt, breaktime_period, self.set_days_of_the_week, timetable)
        
        self.editor.refresh()
        
        for _, timetable in self.editor.timetable_widgets.items():
            self.timetable_update(timetable)
    
    def _toogle(self):
        self.toogle_button.setAngle(180 * (not self.main_settings_widget.isVisible()))
        self.options_info.setText("Callapse Options" if not self.main_settings_widget.isVisible() else "Expand Options")
        self.main_settings_widget.setVisible(not self.main_settings_widget.isVisible())
        self.main_settings_widget.update()
    
    def _generate(self):
        self._refresh()
        self.editor.school.generateNewSchoolTimetables()
    
    def timetable_refresh(self, period_amt: int | None, break_period: int | None, days_of_the_week: list[str], timetable: '_ClassTimetable'):
        if break_period is not None and break_period != int(sum(timetable.cls.timetable.breakTimePeriods) / len(timetable.cls.timetable.breakTimePeriods)):
            for x in range(timetable.columnCount()):
                break_period_item = timetable.takeItem(timetable.cls.timetable.breakTimePeriods[x] - 1, x)  # TimeTableItem(Subject("Break", 1, 1, None), break_time=True)
                replacement_item = timetable.takeItem(break_period - 1, x)
                
                timetable.setItem(timetable.cls.timetable.breakTimePeriods[x] - 1, x, replacement_item)
                timetable.setItem(break_period - 1, x, break_period_item)
            
            for index, (_, subjects) in enumerate(timetable.cls.timetable.table.items()):
                current_break_period = timetable.cls.timetable.breakTimePeriods[index]
                
                if current_break_period != break_period:
                    timetable.cls.breakTimePeriods = [period for period in timetable.cls.breakTimePeriods.copy()]
                    timetable.cls.breakTimePeriods[index] = break_period
                    timetable.cls.timetable.breakTimePeriods = [period for period in timetable.cls.timetable.breakTimePeriods.copy()]
                    timetable.cls.timetable.breakTimePeriods[index] = break_period
                    
                    for index, subject in enumerate(subjects):
                        if index == current_break_period:
                            break_subj = subjects[index].copy()
                            if break_period in subjects:
                                subjects[index] = subjects[break_period]
                                subjects[break_period] = break_subj
                            else:
                                subjects.pop(index)
                            
                            break
        
        if period_amt is not None and period_amt != int(sum(timetable.cls.timetable.periodsPerDay) / len(timetable.cls.timetable.periodsPerDay)):
            timetable.setRowCount(period_amt)
            timetable.setVerticalHeaderLabels([f"Period {i + 1}" for i in range(timetable.rowCount())])
            timetable.setFixedHeight(timetable.rowCount() * 30 + 40)
            
            for y in range(timetable.rowCount()):
                for x in range(timetable.columnCount()):
                    item = timetable.takeItem(y, x)
                    timetable.setItem(y, x, TimeTableItem() if item is None else item)
            
            for index, (day, subjects) in enumerate(timetable.cls.timetable.table.items()):
                timetable.cls.periodsPerDay = [period_amt for _ in timetable.cls.periodsPerDay.copy()]
                timetable.cls.periodsPerDay[index] = period_amt
                timetable.cls.timetable.periodsPerDay = [period_amt for _ in timetable.cls.timetable.periodsPerDay.copy()]
                timetable.cls.timetable.periodsPerDay[index] = period_amt
                
                period = 0
                for index, subject in enumerate(subjects):
                    period += subject.total
                    if period > period_amt:
                        new_total = period - period_amt
                        subject.total = new_total
                        subjects[index + 1:] = []
                        
                        break
        
        if days_of_the_week and days_of_the_week != timetable.cls.weekdays:
            timetable.cls.weekdays = [day for day in days_of_the_week.copy()]
            
            timetable.setColumnCount(len(days_of_the_week))
            timetable.setHorizontalHeaderLabels(days_of_the_week)
            
            timetable.cls.timetable.weekInfo = [[day, timetable.cls.timetable.periodsPerDay[dayIndex], timetable.cls.breakTimePeriods[dayIndex]] for dayIndex, day in enumerate(days_of_the_week)]
            
            for dayIndex, day in enumerate(days_of_the_week):
                previous_days = list(timetable.cls.timetable.table.keys())
                if dayIndex < len(previous_days):
                    current_day = previous_days[dayIndex]
                    timetable.cls.timetable.table[day] = timetable.cls.timetable.table[current_day]
                    if current_day not in days_of_the_week:
                        timetable.cls.timetable.table.pop(current_day)
                else:
                    timetable.cls.timetable.table[day] = []
                    timetable.cls.timetable.addFreePeriod(day, timetable.periods, timetable.periods)
                    timetable.cls.timetable.breakTimePeriods.append(int(sum(timetable.cls.timetable.breakTimePeriods) / len(timetable.cls.timetable.breakTimePeriods)))
                    timetable.cls.timetable.periodsPerDay.append(timetable.periods)
                    
                    for y in range(timetable.cls.timetable.periodsPerDay[-1]):
                        timetable.setItem(y, dayIndex, TimeTableItem(break_time = True if y == timetable.cls.timetable.breakTimePeriods[-1] - 1 else None))

    def timetable_update(self, timetable: '_ClassTimetable'):
        timetable.timetable.reset()
        
        timetable.cls = self.editor.school.classes[timetable.cls.name]
        timetable.timetable = self.editor.school.classes[timetable.cls.name].timetable
        
        timetable.save_timetable()
    
    def refresh(self):
        if self.warning_dont_ask_again:
            self.refresh_warning.exec()
            
            if not self.continue_refresh:
                return

        self._refresh()
    
    def show_dotw_editor(self):
        self.days_of_the_week_selector.exec()
        self.set_days_of_the_week = self.days_of_the_week_selector.get()
    
    def generate_new_school_timetable(self):
        if self._can_generate_new:
            self._can_generate_new = False
            
            if self.warning_dont_ask_again:
                self.refresh_warning.exec()
                
                if not self.continue_refresh:
                    return
            
            self.progress_bar.set_max(lambda: sum([sum([sum(periods) - len(periods) for _, (periods, _, _) in timing_info.items()]) for _, (timing_info, _) in self.editor.school.project["levels"].items()]))
            self.progress_bar.set_var_func(lambda: sum([sum([sum([s.total for s in subjects]) - 1 for _, subjects in timetable.table.items()]) for _, timetable in self.editor.school.school.items()]))
            self.progress_bar.start(100)
            
            self.thread_generate_new = _GenerateNewSchoolThread(self._generate, self.threads_list)
            self.thread_generate_new.finished.connect(self._generating_finished)
            self.thread_generate_new.start()

class _ClassTimetable(QTableWidget):
    def __init__(self, cls: Class, editor: 'TimeTableEditor', name: str, remainder_layout: QVBoxLayout):
        super().__init__()
        self.name = name
        self.cls = cls
        self.timetable = cls.timetable
        self.editor = editor
        
        self.remainder_layout = remainder_layout
        
        self.periods = max(self.timetable.periodsPerDay)
        
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
                if target_item and isinstance(target_item, TimeTableItem) and target_item.break_time is None:
                    
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
        
        subjects = flatten([[subj for _ in range(subj.total)] for subj in self.cls.timetable.remainderContent])
        for subject in subjects:
            subject_label = DraggableSubjectLabel(subject, self.cls)
            subject_label.clicked.connect(self.editor.make_ds_func(subject_label))
            
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

class TimeTableEditor(QWidget):
    THREADS: list[_GenerateNewSchoolThread] = []
    
    def __init__(self, school: School):
        super().__init__()
        self.school = school
        
        progress_bar_widget = QWidget()
        
        progress_bar_layout = QHBoxLayout()
        progress_bar_widget.setLayout(progress_bar_layout)
        
        self.progress_bar = _ProgressBar(progress_bar_widget)
        
        progress_label = QLabel("Generating...")
        progress_label.setStyleSheet("font-weight: bold;")
        
        progress_bar_layout.addWidget(progress_label)
        progress_bar_layout.addWidget(self.progress_bar)
        progress_bar_layout.addStretch()
        
        self._can_generate_new_timetable = True
        self.timetable_warning_dont_ask_again = True
        
        self.timetable_refresh_warning = WarningDialog("Warning", "By doing this, all information in this timetable will be overwritten.\nDo you want to proceed with this action?")
        self.timetable_refresh_warning.button_clicked.connect(self._timetable_dailog_clicked_func)
        self.timetable_refresh_warning.checkbox_on.connect(self._timetable_dailog_dont_ask_again)
        
        self.thread_generate_new = _GenerateNewSchoolThread(lambda: print, self.THREADS)
        self.continue_timetable_refresh = True
        
        self.setStyleSheet(THEME[TIMETABLE_EDITOR])
        
        self.main_layout = QVBoxLayout(self)
        
        self.external_source_ref = None
        
        self.option_selectors: dict[str, list[OptionSelection, list[str]]] = {}
        
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
            self.set_timetable_for_each_class(index, class_name, cls)
        
        # Create settings for timetables
        self.settings_widget = _TimetableSettings(self, self.progress_bar, self.THREADS)
        
        self.main_layout.addWidget(self.settings_widget)
        self.main_layout.addWidget(progress_bar_widget)
        self.main_layout.addWidget(self.scroll_area)
    
    def _set_school_timetable(self):
        for class_name, _ in self.school.classes.items():
            self.timetable_widgets[class_name].populate_timetable()
    
    def _timetable_generating_finished(self, name: str):
        self._can_generate_new_timetable = True
        self.timetable_widgets[name].populate_timetable()
    
    def _timetable_dailog_dont_ask_again(self):
        self.timetable_warning_dont_ask_again = False
    
    def _timetable_dailog_clicked_func(self, ok_clicked: bool):
        self.continue_timetable_refresh = ok_clicked
    
    def refresh(self):
        self.school.setProjectDictFromSchoolInfo()
        self.school = School(self.school.project)
    
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

    def get_settings_func(self, timetable: _ClassTimetable, period_amt_edit: QLineEdit, breakperiod_edit: QLineEdit):
        def _refresh_func():
            period_amt = int(period_amt_edit.text()) if period_amt_edit.text().isnumeric() else None
            breaktime_period = int(breakperiod_edit.text()) if breakperiod_edit.text().isnumeric() else None
            days_of_the_week = self.option_selectors[timetable.cls.name][1]
            
            self.settings_widget.timetable_refresh(period_amt, breaktime_period, days_of_the_week, timetable)
            self.refresh()
            self.settings_widget.timetable_update(timetable)
        
        def new_func():
            if self._can_generate_new_timetable:
                self._can_generate_new_timetable = False
                
                if self.timetable_warning_dont_ask_again:
                    self.timetable_refresh_warning.exec()
                    
                    if not self.continue_timetable_refresh:
                        return
                
                self.progress_bar.set_max(lambda: sum(timetable.cls.timetable.periodsPerDay) - len(timetable.cls.timetable.periodsPerDay))
                self.progress_bar.set_var_func(lambda: sum([sum([s.total for s in subjects]) - 1 for _, subjects in timetable.cls.timetable.table.items()]))
                self.progress_bar.start(100)
                
                _refresh_func()
                
                self.thread_generate_new = _GenerateNewSchoolThread(lambda: self.school.generateTimetable(timetable.cls), self.THREADS)
                self.thread_generate_new.finished.connect(lambda: self._timetable_generating_finished(timetable.cls.name))
                self.thread_generate_new.start()
        
        def weekdays_func():
            self.option_selectors[timetable.cls.name][0].exec()
            self.option_selectors[timetable.cls.name][1] = self.option_selectors[timetable.cls.name][0].get()
        
        def refresh_func():
            if self.timetable_warning_dont_ask_again:
                self.timetable_refresh_warning.exec()
                
                if not self.continue_timetable_refresh:
                    return
            
            _refresh_func()
        
        return {
            "new": new_func,
            "weekdays": weekdays_func,
            "refresh": refresh_func,
        }
    
    def set_timetable_settings(self, timetable: _ClassTimetable, layout: QVBoxLayout):
        period_amt_edit = NumberTextEdit()
        period_amt_edit.edit.setPlaceholderText("Periods Amt")
        
        breakperiod_edit = NumberTextEdit()
        breakperiod_edit.edit.setPlaceholderText("Break period")
        
        func_info = self.get_settings_func(timetable, period_amt_edit.edit, breakperiod_edit.edit)
        
        dotw_button = QPushButton("Weekdays")
        dotw_button.setFixedWidth(95)
        dotw_button.clicked.connect(func_info["weekdays"])
        
        generate_new_button = QPushButton("New")
        generate_new_button.setProperty("class", "safety")
        generate_new_button.setFixedWidth(95)
        generate_new_button.clicked.connect(func_info["new"])
        
        refresh_button = QPushButton("Refresh")
        refresh_button.setFixedWidth(95)
        refresh_button.clicked.connect(func_info["refresh"])
        
        layout.addWidget(period_amt_edit)
        layout.addWidget(breakperiod_edit)
        layout.addSpacing(5)
        layout.addWidget(dotw_button, alignment=Qt.AlignmentFlag.AlignHCenter)
        layout.addSpacing(20)
        layout.addWidget(generate_new_button, alignment=Qt.AlignmentFlag.AlignHCenter)
        layout.addWidget(refresh_button, alignment=Qt.AlignmentFlag.AlignHCenter)

    def set_timetable_for_each_class(self, index, class_name, cls):
        settings_width = 200
        
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
        sidebar_widget.setStyleSheet(THEME[GENERAL_SCROLLBARS])
        sidebar_widget_layout = QVBoxLayout(sidebar_widget)
        
        remainder_scroll_area = QScrollArea()
        remainder_scroll_area.setWidgetResizable(True)
        remainder_scroll_area.setFixedWidth(settings_width)
        remainder_scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        remainder_widget = QWidget()
        remainder_widget.setFixedWidth(settings_width)
        remainder_scroll_area.setWidget(remainder_widget)
        
        remainder_widget_layout = QVBoxLayout(remainder_widget)
        
        settings_scroll_area = QScrollArea()
        settings_scroll_area.setWidgetResizable(True)
        settings_scroll_area.setFixedSize(settings_width, 100)
        settings_scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        settings_widget = QWidget()
        settings_widget.setFixedWidth(settings_width)
        settings_scroll_area.setWidget(settings_widget)
        
        settings_widget.setStyleSheet(THEME[GENERAL_BUTTON] + THEME[GENERAL_CHECKBOXES] + THEME[GENERAL_DIALOGS])
        
        settings_widget_layout = QVBoxLayout(settings_widget)
        
        timetable = _ClassTimetable(cls, self, class_name, remainder_widget_layout)
        self.timetable_widgets[class_name] = timetable
        set_days_of_the_week = timetable.cls.weekdays
        self.option_selectors[class_name] = [OptionSelection("Days of the week", set_days_of_the_week), set_days_of_the_week]
        
        self.set_timetable_settings(timetable, settings_widget_layout)
        
        remainder_title = QLabel("Remaining Subjects")
        remainder_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        remainder_widget_layout.addWidget(remainder_title, alignment=Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop)
        
        remainder_widget_layout.addStretch()
        
        class_widget_layout.addWidget(timetable)
        class_widget_layout.addWidget(sidebar_widget)
        
        self.timetables_layout.addWidget(class_widget)
        
        sidebar_widget_layout.addWidget(remainder_scroll_area, alignment=Qt.AlignmentFlag.AlignHCenter)
        sidebar_widget_layout.addWidget(settings_scroll_area, alignment=Qt.AlignmentFlag.AlignHCenter)

