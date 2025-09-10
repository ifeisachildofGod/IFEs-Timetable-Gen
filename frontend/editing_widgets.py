from frontend.imports import *

from frontend.sub_widgets import *

DOTW_DATA = {
    "content": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", None, "Saturday", "Sunday"],
    "id_mapping": {0: "ID:monday3231", 1: "ID:tuesday6456", 2: "ID:wednesday0921", 3: "ID:thursday9182", 4: "ID:friday8765", 6: "ID:saturday8728", 7: "ID:sunday0091"}
}

class MenuFrame(QFrame):
    def __init__(self):
        super().__init__()
        self.setProperty("class", "Menu")
        self.setStyleSheet("QFrame.Menu { border: 1px solid "+ THEME_MANAGER.parse_stylesheet("{border2}") +"; }")
        self.setWindowFlags(Qt.WindowType.Popup)
        self.setFrameShape(QFrame.Shape.Box)
        
        self.main_layout = QVBoxLayout()
        self.setLayout(self.main_layout)
        
        self._pos = self.pos()
    
    def set_pos(self, pos: QPoint):
        self._pos = pos
    
    def toogle(self):
        if self.isVisible():
            self.hide()
        else:
            self.move(self._pos)
            self.show()

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
    def __init__(self, editor: 'TimeTableEditor', progress_bar: _ProgressBar, info: dict[str, list | dict[int, str]], saved_state_changed: pyqtBoundSignal):
        super().__init__()
        
        self.info = info
        
        self.editor = editor
        self.saved_state_changed = saved_state_changed
        
        self._can_generate_new = True
        
        self.main_layout = QVBoxLayout()
        self.setLayout(self.main_layout)
        
        options_widget = QWidget()
        
        options_layout = QHBoxLayout()
        options_widget.setLayout(options_layout)
        
        self.settings_menu = MenuFrame()
        
        self.toogle_button = QPushButton("☰")
        self.toogle_button.setProperty("class", "Timetable_DP_OptionText")
        self.toogle_button.clicked.connect(self._toogle)
        
        self.main_layout.addWidget(self.toogle_button, alignment=Qt.AlignmentFlag.AlignRight)
        
        timetable_settings_widget = QWidget()
        timetable_settings_layout = QHBoxLayout()
        timetable_settings_widget.setLayout(timetable_settings_layout)
        
        general_settings_widget = QWidget()
        general_settings_layout = QHBoxLayout()
        general_settings_widget.setLayout(general_settings_layout)
        
        self.progress_bar = progress_bar
        
        left_option_widget = QWidget()
        left_option_layout = QVBoxLayout()
        left_option_widget.setLayout(left_option_layout)
        
        update_break_period = True
        
        def periodamt_number_changed(number: int):
            global update_break_period
            
            for level_index in self.editor.classes_widget:
                self.editor.cls_levels_data[level_index]["period-func"](number)
            
            self.breakperiod_edit.max_num = number
            if self.breakperiod_edit.max_num < self.breakperiod_edit.number():
                update_break_period = False
                self.breakperiod_edit.setNumber(self.breakperiod_edit.max_num)
                update_break_period = True
        
        def breakperiod_number_changed(number: int):
            if update_break_period:
                for level_index in self.editor.classes_widget:
                    self.editor.cls_levels_data[level_index]["break-func"](number)
        
        self.period_amt_edit = NumberLineEdit(10, 1, 20)
        self.period_amt_edit.setPlaceholderText("Period amount")
        self.period_amt_edit.textChanged.connect(periodamt_number_changed)
        
        self.breakperiod_edit = NumberLineEdit(7, 1, self.period_amt_edit.number())  # Temporary
        self.breakperiod_edit.setPlaceholderText("Break period")
        self.breakperiod_edit.textChanged.connect(breakperiod_number_changed)
        
        left_sub_option_widget = QWidget()
        
        left_sub_option_layout = QHBoxLayout()
        left_sub_option_widget.setLayout(left_sub_option_layout)
        
        def closed_func():
            self.info = self.days_of_the_week_selector.get()
        
        self.days_of_the_week_selector = OptionSelector("Days of the week", self.info, self.saved_state_changed)
        self.days_of_the_week_selector.closed.connect(closed_func)
        
        self.clash_viewer = ClashesViewer(self.editor.school)
        
        dotw_button = QPushButton("Days of the Week")
        dotw_button.clicked.connect(self.days_of_the_week_selector.exec)
        
        show_clashes_checkb = QPushButton("Clashes")
        show_clashes_checkb.clicked.connect(self.clash_viewer.exec)
        
        left_sub_option_layout.addWidget(dotw_button)
        left_sub_option_layout.addWidget(show_clashes_checkb)
        
        left_option_layout.addWidget(self.period_amt_edit)
        left_option_layout.addWidget(self.breakperiod_edit)
        left_option_layout.addWidget(left_sub_option_widget)
        
        right_option_widget = QWidget()
        right_option_layout = QVBoxLayout()
        right_option_widget.setLayout(right_option_layout)
        
        generate_button = QPushButton("Generate New")
        generate_button.clicked.connect(self.generate_new_school_timetable)
        
        right_option_layout.addWidget(generate_button)
        
        general_settings_layout.addWidget(left_option_widget)
        general_settings_layout.addWidget(right_option_widget)
        
        # Settings Menu
        settings_menu_layout = self.settings_menu.layout()
        
        settings_menu_layout.addWidget(general_settings_widget)
        settings_menu_layout.addWidget(timetable_settings_widget)
    
    def _number_edit_updates(self, name: str):
        def number_changed(number: int):
            for level_index in self.editor.classes_widget:
                self.editor.cls_levels_data[level_index][name](number)
            
            self.breakperiod_edit.max_num = self.period_amt_edit.number()
        
        return number_changed
    
    def _generating_finished(self):
        self._can_generate_new = True
        self.editor._set_school_timetable()
    
    def _toogle(self):
        self.settings_menu.set_pos(self.toogle_button.mapToGlobal(QPoint(-470, self.toogle_button.height())))
        self.settings_menu.toogle()
    
    def _generate(self):
        self.saved_state_changed.emit()
        
        for ttbl in self.editor.timetable_widgets.values():
            ttbl.clear_remainder()
        
        self.editor.school.generateNewSchoolTimetables()
    
    def _continue_with_irreversable_action(self):
        return QMessageBox.StandardButton.Yes == QMessageBox.warning(self, "Action Irreversible", "This action cannot be reversed\n"
                                                                                                  "All information will be overwritten",
                                                                            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
    
    def generate_new_school_timetable(self):
        if self._can_generate_new:
            self._can_generate_new = False
            
            max_subject_amt = 0
            for timetable_editor in self.editor.timetable_widgets.values():
                max_subject_amt += timetable_editor.get_total_subject_amount()
                        
            if not max_subject_amt:
                QMessageBox.critical(self, "Generator Error", "Variables and connections are not sufficient to generate a timetable")
                
                self._can_generate_new = True
                return
            
            if not self._continue_with_irreversable_action():
                self._can_generate_new = True
                return
            
            def total_subject_func():
                total_subjects = 0
                for timetable_editor in self.editor.timetable_widgets.values():
                    total_subjects += timetable_editor.get_max_subject_amount()
                
                return total_subjects
            
            self.progress_bar.set_max(lambda: max_subject_amt)
            self.progress_bar.set_var_func(total_subject_func)
            self.progress_bar.start(100)
            
            self.generate_new = Thread(self.editor.main_window, self._generate)
            self.generate_new.finished.connect(self._generating_finished)
            self.generate_new.start()
        else:
            QMessageBox.warning(self, "Generating", "Timetable is already being generated")

class ClassTimetable(QTableWidget):
    def __init__(self, cls: Class, editor: 'TimeTableEditor', remainder_layout: QVBoxLayout, saved_state_changed: pyqtBoundSignal):
        super().__init__()
        
        self.cls = cls
        self.editor = editor
        self.timetable = cls.timetable
        self.saved_state_changed = saved_state_changed
        
        self.remainder_layout = remainder_layout
        self.remainder_labels: list[DraggableSubjectLabel] = []
        
        self.periods = max(self.timetable.periodsPerDay)
        
        # Configure table
        self.setRowCount(max(self.timetable.periodsPerDay))
        self.setColumnCount(len(self.timetable.weekInfo))
        self.setHorizontalHeaderLabels([day[0] for day in self.timetable.weekInfo])
        self.setVerticalHeaderLabels([f"Period {i+1}" for i in range(self.rowCount())])
        
        # Set size policies
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.setFixedHeight(self.rowCount() * 30 + 45)  # Adjust row height + header
        
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
        
        for col in range(len(self.timetable.table)):
            self.timetable.correct(col)
        
        # Variables
        self.current_source = None
    
    def get_max_subject_amount(self):
        periods, break_periods, _ = self.editor.school.project["levels"][self.cls.index][1]
        
        max_subject_amt = 0
        
        for index, total_periods in enumerate(periods):
            max_subject_amt += total_periods - (1 if break_periods[index] <= total_periods else 0)
        
        return max_subject_amt
    
    def get_total_subject_amount(self):
        total_subject_amt = 0
        
        for subjects in self.cls.timetable.table.values():
            total_subject_amt += sum(s.total for s in subjects) - 1  # 1 is subtracted to acount for the break period
        
        return total_subject_amt
    
    def timetable_exchange(self, source_item: TimeTableItem, target_item: TimeTableItem):
        source_row, source_col = self.row(source_item), self.column(source_item)
        target_row, target_col = self.row(target_item), self.column(target_item)
        
        # Same timetable swap
        self.blockSignals(True)  # Prevent unnecessary updates
        
        # Create new items
        new_target = TimeTableItem(source_item.subject, source_item.break_time)
        new_source = TimeTableItem(target_item.subject, target_item.break_time)
        
        # Remove old items
        self.takeItem(source_row, source_col)
        self.takeItem(target_row, target_col)
        
        # Set new items
        self.setItem(target_row, target_col, new_target)
        self.setItem(source_row, source_col, new_source)
        
        # Middle timetable replacement
        src_subjs = self.timetable.table[self.timetable.weekInfo[source_col][0]]
        tar_subjs = self.timetable.table[self.timetable.weekInfo[target_col][0]]
        
        Timetable.spread(src_subjs)
        Timetable.spread(tar_subjs)
        
        # Exchange
        temp_tar_subj = tar_subjs[target_row]
        temp_src_subj = src_subjs[source_row]
        
        src_subjs[source_row] = temp_tar_subj
        tar_subjs[target_row] = temp_src_subj
        
        if source_item.break_time:
            self.timetable.weekInfo[source_col][2] = self.cls.breakTimePeriods[source_col]\
                = self.timetable.breakTimePeriods[source_col] = target_row + 1
        elif target_item.break_time:
            self.timetable.weekInfo[target_col][2] = self.cls.breakTimePeriods[target_col]\
                = self.timetable.breakTimePeriods[target_col] = source_row + 1
        
        Timetable.flatten(src_subjs)
        Timetable.flatten(tar_subjs)
        
        # Force refresh
        self.blockSignals(False)
        self.update()
    
    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            item = self.itemAt(event.pos())
            if item and isinstance(item, TimeTableItem) and item.subject:
                self.drag_source_col = self.column(item)
                self.drag_source_row = self.row(item)
                
                # Store original position
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
    
    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasText():
            row = self.rowAt(int(event.position().y()))
            col = self.columnAt(int(event.position().x()))
            
            source: TimeTableItem = self.item(row, col)
            
            if source is not None and source.subject.id != self.timetable.freePeriodID:
                event.accept()
                if self.editor.remainder_source_ref is None:
                    self.current_source: TimeTableItem = self.item(self.rowAt(int(event.position().y())), self.columnAt(int(event.position().x())))
    
    def dragMoveEvent(self, event: QDragMoveEvent):
        if event.mimeData().hasText():
            source_cls: ClassTimetable = event.source()
            
            col = self.columnAt(int(event.position().x()))
            row = self.rowAt(int(event.position().y()))
            
            if source_cls.cls.uniqueID != self.cls.uniqueID or (self.drag_source_col != col and (row == self.cls.breakTimePeriods[col] - 1 or self.cls.breakTimePeriods[self.drag_source_col] == self.drag_source_row + 1)):
                event.ignore()
            else:
                event.accept()
    
    def dropEvent(self, event: QDropEvent):
        if event.mimeData().hasText():
            if self.current_source is not None:
                target_row = self.rowAt(int(event.position().y()))
                target_col = self.columnAt(int(event.position().x()))
                target_item = self.item(target_row, target_col)
                
                source_class = self.editor.timetable_widgets[self.cls.uniqueID].cls
                
                # Handle swapping
                if target_item is not None and isinstance(target_item, TimeTableItem):
                    target_subject = target_item.subject
                    
                    if source_class == self.cls:
                        self.timetable_exchange(self.current_source, target_item)
                        
                        event.accept()
                        self.saved_state_changed.emit()
                        
                        del target_item
            
            elif self.editor.remainder_source_ref is not None:
                row = self.rowAt(int(event.position().y()))
                col = self.columnAt(int(event.position().x()))
                target_item = self.item(row, col)
                
                self.blockSignals(True)  # Prevent unnecessary updates
                
                new_target = TimeTableItem(self.editor.remainder_source_ref.subject)
                
                self.takeItem(row, col)
                self.setItem(row, col, new_target)
                
                if target_item and isinstance(target_item, TimeTableItem) and target_item.subject is not None:
                    target_subject = target_item.subject
                    
                    # Create new items
                    new_source = DraggableSubjectLabel(target_subject)
                    new_source.clicked.connect(self.editor.make_ds_func(new_source))
                    
                    # Set new items
                    self.add_remainder(new_source, self.remainder_layout.indexOf(self.editor.remainder_source_ref))
                    
                    self.timetable.replace(Subject(self.timetable.freePeriodID, "Free", 1, 0, None, self.cls), row, col)
                
                # Remove remainder widget
                self.remove_remainder(self.editor.remainder_source_ref)
                
                self.remainder_layout.update()
                
                self.blockSignals(False)
                
                replacement_subject = self.editor.remainder_source_ref.subject.copy()
                replacement_subject.total = 1
                
                self.timetable.replace(replacement_subject, row, col)
                
                self.saved_state_changed.emit()
                
                event.accept()
            
            self.editor.remainder_source_ref = None
            self.current_source = None
    
    def add_remainder(self, remainder: DraggableSubjectLabel, index: int | None = None):
        remainder.subject.lockedPeriod = None
        
        if index is not None:
            self.remainder_layout.insertWidget(index, remainder, alignment=Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop)
            self.remainder_labels.insert(index - 1, remainder)
            self.timetable.remainderContent.insert(index - 1, remainder.subject)
        else:
            self.remainder_layout.insertWidget(self.remainder_layout.count() - 1, remainder, alignment=Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop)
            self.remainder_labels.append(remainder)
            self.timetable.remainderContent.append(remainder.subject)
    
    def remove_remainder(self, remainder: DraggableSubjectLabel):
        self.remainder_labels.remove(remainder)
        self.remainder_layout.removeWidget(remainder)
        self.timetable.remainderContent.remove(remainder.subject)
        
        remainder.deleteLater()
    
    def clear_remainder(self):
        for widg in self.remainder_layout.parentWidget().findChildren(DraggableSubjectLabel):
            self.remainder_layout.removeWidget(widg)
            widg.deleteLater()
        
        for widg in self.remainder_labels.copy():
            self.remainder_labels.remove(widg)
            widg.deleteLater()
        
        self.timetable.remainderContent.clear()
    
    def save_timetable(self):
        """Save current grid state back to timetable"""
        for col in range(self.columnCount()):
            subjects = []
            for row in range(self.rowCount()):
                item = self.item(row, col)
                if isinstance(item, TimeTableItem) and item.subject:
                    if (subjects and subjects[-1].uniqueID != item.subject.uniqueID) or not subjects:
                        subjects.append(item.subject)
                        
                        if item.subject.id not in (self.timetable.freePeriodID, self.timetable.breakPeriodID):
                            coords = [
                                (col, row),
                                (item.subject.total, item.subject.perWeek),
                                len([1 for label in self.remainder_labels if label.subject.id == item.subject.id])
                            ]
                            
                            self.editor.school.project["subjects"][item.subject.id][1][str(self.cls.index)][2][self.cls.classID][1].append(coords)
    
    def populate_timetable(self):
        """Load the timetable data into the grid"""
        for col, (day, _, _) in enumerate(self.timetable.weekInfo):
            total_s_names = list(flatten([[subj for _ in range(subj.total)] for subj in self.timetable.table[day]]))
            subjects = total_s_names + [Subject(self.timetable.freePeriodID, "Free", 1, 1, None, self.cls) for _ in range(max(self.timetable.periodsPerDay) - len(total_s_names))]
            
            for row, subject in enumerate(subjects):
                item = TimeTableItem(subject, row + 1 == self.cls.breakTimePeriods[col], subject.id == self.cls.timetable.freePeriodID)
                self.setItem(row, col, item)
        
        rem_subjects = [subj for subj in self.timetable.remainderContent if subj.teacher is not None]
        
        self.clear_remainder()
        
        for subject in rem_subjects:
            subject_label = DraggableSubjectLabel(subject)
            subject_label.clicked.connect(self.editor.make_ds_func(subject_label))
            
            self.add_remainder(subject_label)
    
    def show_context_menu(self, pos):
        item = self.itemAt(pos)
        
        if item and isinstance(item, TimeTableItem) and item.subject is not None and item.subject.teacher is not None:
            menu = QMenu(self)
            
            lock_action = None
            unlock_action = None
            
            delete_action = menu.addAction("Delete")
            if item.subject.lockedPeriod:
                unlock_action = menu.addAction("Unlock Period")
            else:
                lock_action = menu.addAction("Lock to Period")
            goto_subject_action = menu.addAction("Go to Subject")
            goto_teacher_action = menu.addAction("Go to Teacher")
            
            action = menu.exec(self.viewport().mapToGlobal(pos))
            
            if action == delete_action:
                free_period_subject = Subject(self.cls.timetable.freePeriodID, "Free", 1, 1, None, self.cls)
                
                row = self.row(item)
                col = self.column(item)
                
                # Move to remainders if deleted
                subject = item.subject.copy()
                subject.perWeek = 1
                
                subject_label = DraggableSubjectLabel(subject)
                subject_label.clicked.connect(self.editor.make_ds_func(subject_label))
                
                self.add_remainder(subject_label)
                
                self.setItem(row, col, TimeTableItem(free_period_subject, False, True))
                
                self.timetable.replace(free_period_subject, row, col)
                
                self.saved_state_changed.emit()
            elif lock_action is not None and action == lock_action:
                item.subject.lockedPeriod = [self.row(item), 1]  # Lock to current period
                self.saved_state_changed.emit()
            elif unlock_action is not None and action == unlock_action:
                item.subject.lockedPeriod = None
                self.saved_state_changed.emit()
            elif action == goto_subject_action:
                pass
            elif action == goto_teacher_action:
                pass

class TimeTableEditor(QWidget):
    def __init__(self, main_window: QMainWindow, school: School, info: dict[str, dict] | None, saved_state_changed: pyqtBoundSignal):
        super().__init__()
        
        self.info = info["variables"] if info is not None else {"DOTW": DOTW_DATA}
        self.saved_state_changed = saved_state_changed
        
        self.school = school
        self.main_window = main_window
        
        progress_bar_widget = QWidget()
        
        progress_bar_layout = QHBoxLayout()
        progress_bar_widget.setLayout(progress_bar_layout)
        
        self.progress_bar = _ProgressBar(progress_bar_widget)
        
        progress_label = QLabel("Generating...")
        progress_label.setStyleSheet("font-weight: bold;")
        
        progress_bar_layout.addWidget(progress_label)
        progress_bar_layout.addWidget(self.progress_bar)
        progress_bar_layout.addStretch()
        
        self._leave_updated = True
        
        self.main_layout = QVBoxLayout(self)
        
        self.remainder_source_ref: TimeTableItem = None
        
        self.cls_levels_data: dict[str, dict[str, bool | OptionSelector]] = {}
        self.class_generator_threads: dict[str, Thread] = {}
        
        # Create scroll area for timetables
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        # Container for all timetables
        self.timetables_container = QWidget()
        self.timetables_layout = QVBoxLayout(self.timetables_container)
        self.timetables_layout.setSpacing(20)
        self.scroll_area.setWidget(self.timetables_container)
        
        # Create timetable for each class
        self.timetable_parent_widget: dict[str, QWidget] = {}
        self.timetable_widgets: dict[str, ClassTimetable] = {}
        self.classes_widget: dict[int, tuple[QWidget, QVBoxLayout, dict[str, QWidget]]] = {}
        
        for cls in self.school.classes.values():
            widget = self._make_timetable_for_each_class(cls)
            self.classes_widget[cls.index][1].addWidget(widget)
        
        # Create settings for timetables
        self.settings_widget = _TimetableSettings(self, self.progress_bar, self.info["DOTW"], self.saved_state_changed)
        
        self.main_layout.addWidget(self.settings_widget)
        self.main_layout.addWidget(progress_bar_widget)
        self.main_layout.addWidget(self.scroll_area)
    
    def get(self):
        return self.info
    
    def set_editor_from_school(self, school: School):
        self.school = school
        
        for level_index, (widget, layout, options_widget_data) in self.classes_widget.copy().items():
            if next((False for _, cls in self.school.classes.items() if cls.index == level_index), True):
                self.classes_widget.pop(level_index)
                
                for cls_id in self.timetable_parent_widget.copy():
                    if level_index == self.timetable_widgets[cls_id].cls.index:
                        self.timetable_widgets.pop(cls_id)
                        self.timetable_parent_widget.pop(cls_id)
            else:
                for option_id, widget in options_widget_data.copy().items():
                    if next((False for _, cls in self.school.classes.items() if cls.classID == option_id), True):
                        class_id = Class.getUniqueID(level_index, option_id)
                        
                        self.timetable_widgets.pop(class_id)
                        self.timetable_parent_widget.pop(class_id)
                        
                        sub_widget = options_widget_data.pop(option_id)
                        
                        layout.removeWidget(sub_widget)
            
            self.timetables_layout.removeWidget(widget)
        
        totals = {}
        classes = {}
        for cls in self.school.classes.values():
            totals[cls.uniqueID] = {}
            
            classes[cls.uniqueID] = (
                self.timetable_parent_widget[cls.uniqueID]
                if cls.uniqueID in self.timetable_parent_widget else
                self._make_timetable_for_each_class(cls)
            )
            
            temp_timetable_table = self.timetable_widgets[cls.uniqueID].timetable.table
            temp_timetable_remainder_content = self.timetable_widgets[cls.uniqueID].timetable.remainderContent
            
            self.timetable_widgets[cls.uniqueID].cls = cls
            
            self.timetable_widgets[cls.uniqueID].timetable = cls.timetable
            self.timetable_widgets[cls.uniqueID].timetable.table = temp_timetable_table
            
            self.timetable_widgets[cls.uniqueID].clear_remainder()
            
            for s in temp_timetable_remainder_content:
                self.timetable_widgets[cls.uniqueID].add_remainder(DraggableSubjectLabel(s))
        
        for class_id, widget in classes.items():
            ttbl = self.timetable_widgets[class_id]
            
            ttbl.cls = self.school.classes[class_id]
            ttbl.timetable = self.school.classes[class_id].timetable
            
            for subj in ttbl.cls.subjects:
                totals[class_id][subj.uniqueID] = 0
            
            for col in range(ttbl.columnCount()):
                for row in range(ttbl.rowCount()):
                    ttbl_item: TimeTableItem = ttbl.item(row, col)
                    
                    is_present = ttbl_item.subject.uniqueID in totals[class_id]
                    
                    is_not_break_or_free = ttbl_item.subject.id not in (ttbl.timetable.freePeriodID, ttbl.timetable.breakPeriodID)
                    is_removed = is_not_break_or_free and next((False for s in ttbl.cls.subjects if s.uniqueID == ttbl_item.subject.uniqueID), True)
                    is_per_week_exceeded = is_not_break_or_free and (not is_present or totals[class_id][ttbl_item.subject.uniqueID] > school.subjects[ttbl_item.subject.uniqueID].PERWEEK)
                    
                    if is_present:
                        totals[class_id][ttbl_item.subject.uniqueID] += 1
                    
                    if is_removed or is_per_week_exceeded:
                        subj = Subject(ttbl.timetable.freePeriodID, "Free", 1, 1, None, ttbl)
                        ttbl.timetable.replace(subj, row, col)
                        
                        totals[class_id].pop(ttbl_item.subject.uniqueID, None)
                    
                    if is_not_break_or_free and not is_per_week_exceeded and totals[class_id][ttbl_item.subject.uniqueID] == school.subjects[ttbl_item.subject.uniqueID].PERWEEK:
                        totals[class_id].pop(ttbl_item.subject.uniqueID)
            
            for d_labels in ttbl.remainder_labels.copy():
                is_present = d_labels.subject.uniqueID in totals[class_id]
                
                if is_present:
                    totals[class_id][d_labels.subject.uniqueID] += 1
                
                is_removed = next((False for s in ttbl.cls.subjects if s.uniqueID == d_labels.subject.uniqueID), True)
                is_per_week_exceeded = not is_present or totals[class_id][d_labels.subject.uniqueID] > school.subjects[d_labels.subject.uniqueID].PERWEEK
                
                if is_removed or is_per_week_exceeded:
                    ttbl.remove_remainder(d_labels)
                    totals[class_id].pop(ttbl_item.subject.uniqueID, None)
            
            for s_id, s_amt in totals[class_id].items():
                for _ in range(school.subjects[s_id].PERWEEK - s_amt):
                    ttbl.add_remainder(DraggableSubjectLabel(self.school.subjects[s_id]))
            
            totals.pop(class_id)
            
            ttbl.populate_timetable()
            self.classes_widget[ttbl.cls.index][1].addWidget(widget)
    
    def make_ds_func(self, label: DraggableSubjectLabel):
        def func(event):
            self.remainder_source_ref = label
            
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
    
    def update_data_interaction(self, prev_index: int, curr_index: int):
        if curr_index == 3:
            subjects_info = self.main_window.subjects_widget.get()
            teachers_info = self.main_window.teachers_widget.get()
            classes_info = self.main_window.classes_widget.get()
            
            subjectTeacherMapping = {}
            for subject_id, subject_info in subjects_info.items():
                teacher_subject_info = {"&timings": {}}
                
                for class_id, _ in subject_info["classes"].items():
                    class_index = next(index for index, _id in enumerate(classes_info.keys()) if _id == class_id)
                    subject_in_class_info = classes_info[class_id]["subjects"][subject_id][1]
                    
                    for teacher_id, teacher_info_entry in teachers_info.items():
                        if subject_id in teacher_info_entry["classes"]["content"] and class_id in teacher_info_entry["classes"]["content"][subject_id]:
                            teacher_name = teacher_info_entry["text"][0]
                            
                            if teacher_info_entry["classes"]["content"][subject_id][class_id][0] is not None:
                                selected_class_options = []
                                stm_subjects_data = self.school.project["subjectTeacherMapping"].get(subject_id)
                                cls_index = next((str(class_index) for class_index, cls_id in enumerate(classes_info) if cls_id == class_id), None)
                                
                                if None not in (stm_subjects_data, cls_index):
                                    selected_class_options = stm_subjects_data[1].get(teacher_id, (_, {}))[1].get(cls_index, (_, []))[1]
                            elif sum(list(teacher_info_entry["classes"]["content"][subject_id][class_id][1].values())):
                                selected_class_options = []
                                
                                for option_id, option_state in teacher_info_entry["classes"]["content"][subject_id][class_id][1].items():
                                    if option_state:
                                        selected_class_options.append(option_id)
                            else:
                                continue
                            
                            max_random_classes_amt = teacher_info_entry["classes"]["content"][subject_id][class_id][0]
                            
                            if teacher_id not in teacher_subject_info:
                                teacher_subject_info[teacher_id] = [teacher_name, {str(class_index): [max_random_classes_amt, selected_class_options]}]
                            else:
                                teacher_subject_info[teacher_id][1][str(class_index)] = [max_random_classes_amt, selected_class_options]
                    
                    teacher_subject_info["&timings"][str(class_index)] = [int(subject_in_class_info["per_day"]), int(subject_in_class_info["per_week"])]
                    
                    valid_options = [option_id for option_id, option_state in subject_info["classes"][class_id].items() if option_state]
                    if len(valid_options) != len(subject_info["classes"][class_id]):
                        if "&classes" not in teacher_subject_info:
                            teacher_subject_info["&classes"] = {str(class_index): valid_options}
                        else:
                            teacher_subject_info["&classes"][str(class_index)] = valid_options
            
                subjectTeacherMapping[subject_id] = [subject_info["text"][0], teacher_subject_info]
            
            class_levels = []
            for class_index, (class_id, class_info) in enumerate(classes_info.items()):
                level_info = {option_id: option_text for option_id, option_text in class_info["options"].items()}
                
                class_levels.append([class_info["text"][0], self.school.project["levels"][class_index][1], level_info])
            
            project_update = {
                "levels": class_levels,
                "subjectTeacherMapping": subjectTeacherMapping
            }
            
            school_project_subjects_dict = self.school.project.get("subjects", {})
            
            subjects = {}
            for subject_id, (subject_name, subject_info) in subjectTeacherMapping.items():
                subject_level_info = {}
                
                t_temp = subject_info.pop("&timings")
                c_temp = subject_info.pop("&classes", None)
                
                classes_taught = {}
                
                for _, cls_option_mapping in subject_info.values():
                    for clslvlIndex, (_, classIDs) in cls_option_mapping.items():
                        if clslvlIndex not in classes_taught:
                            classes_taught[clslvlIndex] = []
                        classes_taught[clslvlIndex].extend(classIDs)
                
                subject_info["&timings"] = t_temp
                if c_temp is not None:
                    subject_info["&classes"] = c_temp
                
                classes_taught.update(subject_info.get("&classes", {}))
                
                random_select_teacher_ids = []
                
                for class_index, class_ids in classes_taught.items():
                    class_teacher_mapping = {}
                    
                    class_level_id = list(classes_info)[int(class_index)]
                    
                    for class_id in class_ids:
                        for teacher_id, teacher_data in teachers_info.items():
                            potential_teacher_info_on_subject = teacher_data["classes"]["content"].get(subject_id, {}).get(class_level_id, [-50, {}])
                            
                            if potential_teacher_info_on_subject[0] == -50:
                                continue
                            
                            data = [[teacher_id, "".join(teacher_data["text"])], school_project_subjects_dict.get(subject_id, [_, {}])[1].get(class_index, [_, _, {}])[2].get(class_id, [_, []])[1]]
                            
                            if potential_teacher_info_on_subject[0] is not None:
                                random_select_teacher_ids.append([potential_teacher_info_on_subject[0], class_index, data, []])
                                continue
                            
                            if potential_teacher_info_on_subject[1].get(class_id):
                                class_teacher_mapping[class_id] = data
                                break
                    
                    per_day, per_week = subject_info["&timings"][class_index]
                    subject_level_info[class_index] = (per_day, per_week, class_teacher_mapping)
                    
                    for _, _, _, available_c_ids in random_select_teacher_ids:
                        available_c_ids.clear()
                        available_c_ids.extend([class_id for c_id, c_id_state in subject_info["classes"][class_level_id].items() if c_id_state and c_id not in class_teacher_mapping])
                
                for str_class_index, random_sub_class_teacher_data in School.placeRandomTeachers(random_select_teacher_ids).items():
                    subject_level_info[str_class_index][2].update(random_sub_class_teacher_data)
                
                subjects[subject_id] = [subject_name, subject_level_info]
            
            project_update["subjects"] = subjects
            
            main_window_school: School = self.main_window.school
            
            self.main_window.save_data = self.school.project
            self.main_window.save_data.update(project_update)
            main_window_school.setProjectData(self.main_window.save_data)
            main_window_school.setSchoolInfoFromProjectDict()
            self.school = main_window_school
            
            self.set_editor_from_school(self.school)
            self._leave_updated = False
        else:
            if not self._leave_updated:
                for ttbl in self.timetable_widgets.values():
                    ttbl.save_timetable()
    
    def _certify_class_level_info(self, class_index: int, class_id: str, option_id: str):
        if class_index < len(self.school.project["levels"]):
            if class_id + option_id in self.school.project["levels"][class_index][1]:
                return True
        
        return False
    
    def _set_school_timetable(self):
        for _, cls in self.school.classes.items():
            self.timetable_widgets[cls.uniqueID].populate_timetable()
    
    def _make_timetable_settings(self, lvl_index: int):
        widget_menu = MenuFrame()
        layout = widget_menu.layout()
        
        break_updateable = True
        
        def _generating_finished():
            for ttbl in self.timetable_widgets.values():
                if ttbl.cls.index == lvl_index:
                    ttbl.populate_timetable()
            
            self.class_generator_threads.pop(lvl_index)
            
        def period_amt_changed(curr_period_amt: int):
            global break_updateable
            
            breakperiod_edit.max_num = curr_period_amt
            if curr_period_amt < breakperiod_edit.number():
                break_updateable = False
                breakperiod_edit.setNumber(curr_period_amt)
                break_updateable = True
            
            for ttbl in self.timetable_widgets.values():
                if ttbl.cls.index == lvl_index:
                    for col, (day, prev_period_amt, _) in enumerate(ttbl.cls.timetable.weekInfo):
                        if curr_period_amt < ttbl.cls.timetable.weekInfo[col][2]:
                            ttbl.timetable_exchange(ttbl.item(ttbl.cls.timetable.weekInfo[col][2] - 1, col), ttbl.item(ttbl.cls.timetable.weekInfo[col][2] - 2, col))
                        
                        Timetable.spread(ttbl.cls.timetable.table[day])
                        if prev_period_amt > curr_period_amt:
                            for s in ttbl.cls.timetable.table[day][curr_period_amt:]:
                                if s.id not in (ttbl.cls.timetable.breakPeriodID, ttbl.cls.timetable.freePeriodID):
                                    ttbl.add_remainder(DraggableSubjectLabel(s))
                            ttbl.cls.timetable.table[day][curr_period_amt:] = []
                        elif prev_period_amt < curr_period_amt:
                            rem_free_period = Subject(ttbl.cls.timetable.freePeriodID, "Free", curr_period_amt - prev_period_amt, 0, None, ttbl.cls)
                            
                            ttbl.cls.timetable.table[day].append(rem_free_period)
                        Timetable.flatten(ttbl.cls.timetable.table[day])
                        
                        ttbl.cls.timetable.weekInfo[col][1] = curr_period_amt
                        ttbl.cls.periodsPerDay[col] = curr_period_amt
                        ttbl.cls.timetable.periodsPerDay[col] = curr_period_amt
                        
                        ttbl.timetable.correct(col)
                    
                    ttbl.setRowCount(curr_period_amt)
                    ttbl.setVerticalHeaderLabels([f"Period {i + 1}" for i in range(ttbl.rowCount())])
                    ttbl.setFixedHeight(ttbl.rowCount() * 30 + 45)
                    
                    for col in range(ttbl.columnCount()):
                        for row in range(ttbl.rowCount()):
                            if ttbl.item(row, col) is None:
                                ttbl.setItem(row, col, TimeTableItem(Subject(ttbl.cls.timetable.freePeriodID, "Free", 1, 0, None, ttbl.cls), False, True))
            
            self.saved_state_changed.emit()
        
        def break_period_changed(curr_break_period: int):
            if break_updateable:
                for ttbl in self.timetable_widgets.values():
                    if ttbl.cls.index == lvl_index:
                        for col, (day, period_amt, prev_break_period) in enumerate(ttbl.cls.timetable.weekInfo):
                            prev_break_index = ttbl.cls.timetable.idFind(ttbl.cls.timetable.breakPeriodID, col)
                            
                            break_before_rem_periods = prev_break_period - sum(s.total for s in ttbl.cls.timetable.table[day][:prev_break_index]) - 1
                            if break_before_rem_periods:
                                ttbl.cls.timetable.table[day].insert(prev_break_index, Subject(ttbl.cls.timetable.freePeriodID, "Free", break_before_rem_periods, 0, None, ttbl.cls))
                            break_after_rem_periods = period_amt - sum(s.total for s in ttbl.cls.timetable.table[day])
                            if break_after_rem_periods:
                                ttbl.cls.timetable.table[day].append(Subject(ttbl.cls.timetable.freePeriodID, "Free", break_after_rem_periods, 0, None, ttbl.cls))
                            
                            prev_break_index = ttbl.cls.timetable.idFind(ttbl.cls.timetable.breakPeriodID, col)
                            
                            break_subject = ttbl.cls.timetable.table[day][prev_break_index]
                            
                            rem_periods = max(curr_break_period - sum(s.total for s in ttbl.cls.timetable.table[day]), 0)
                            if rem_periods:
                                free_subj = Subject(ttbl.cls.timetable.freePeriodID, "Free", rem_periods, 0, None, ttbl.cls)
                                ttbl.cls.timetable.table[day].append(free_subj)
                            
                            Timetable.spread(ttbl.cls.timetable.table[day])
                            ttbl.cls.timetable.table[day].pop(next(index for index, subj in enumerate(ttbl.cls.timetable.table[day]) if subj.id == break_subject.id))
                            ttbl.cls.timetable.table[day].insert(curr_break_period - 1, break_subject)
                            Timetable.flatten(ttbl.cls.timetable.table[day])
                            
                            ttbl.timetable_exchange(ttbl.item(ttbl.cls.timetable.weekInfo[col][2] - 1, col), ttbl.item(curr_break_period - 1, col))
                
                self.saved_state_changed.emit()
        
        def generate_new_func():
            classes = []
            
            for ttbl in self.timetable_widgets.values():
                if ttbl.cls.index == lvl_index:
                    classes.append(ttbl.cls)
            
            def generate_new_level():
                for cls in classes:
                    self.school.generateTimetable(cls)
            
            if lvl_index not in self.class_generator_threads:
                response = QMessageBox.warning(self, "Action Irreversible", "This action cannot be reversed\n"
                                                                            "All information will be overwritten",
                                                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
                
                if response != QMessageBox.StandardButton.Yes:
                    return
                self.progress_bar.set_max(lambda: sum(ttbl.cls.timetable.periodsPerDay) - len(ttbl.cls.timetable.periodsPerDay))
                self.progress_bar.set_var_func(lambda: sum([sum([s.total for s in subjects]) - 1 for _, subjects in ttbl.cls.timetable.table.items()]))
                self.progress_bar.start(100)
                
                self.class_generator_threads[lvl_index] = Thread(self.main_window, generate_new_level)
                self.class_generator_threads[lvl_index].finished.connect(_generating_finished)
                self.class_generator_threads[lvl_index].start()
            
            self.saved_state_changed.emit()
        
        self.cls_levels_data[lvl_index] = {
            "break-func": break_period_changed,
            "period-func": period_amt_changed,
            "dotw": OptionSelector("Day of the week", DOTW_DATA.copy(), self.saved_state_changed)
        }
        
        period_amt_edit = NumberLineEdit(self.school.project["levels"][lvl_index][1][0][0], 1, 20)
        period_amt_edit.setPlaceholderText("Periods Amt")
        period_amt_edit.textChanged.connect(period_amt_changed)
        
        breakperiod_edit = NumberLineEdit(self.school.project["levels"][lvl_index][1][1][0], period_amt_edit.min_num, period_amt_edit.number())
        breakperiod_edit.setPlaceholderText("Break period")
        breakperiod_edit.textChanged.connect(break_period_changed)
        
        dotw_button = QPushButton("Weekdays")
        dotw_button.clicked.connect(self.cls_levels_data[lvl_index]["dotw"].exec)
        
        generate_new_button = QPushButton("Generate New")
        generate_new_button.clicked.connect(generate_new_func)
        
        layout.addWidget(period_amt_edit)
        layout.addWidget(breakperiod_edit)
        layout.addSpacing(5)
        layout.addWidget(dotw_button, alignment=Qt.AlignmentFlag.AlignHCenter)
        layout.addSpacing(20)
        layout.addWidget(generate_new_button, alignment=Qt.AlignmentFlag.AlignHCenter)
        
        return widget_menu
    
    def _make_timetable_for_each_class(self, cls: Class):
        widget = QWidget()
        layout = QVBoxLayout()
        
        widget.setProperty("class", "TimetableWidget")
        widget.setLayout(layout)
        
        settings_width = 200
        
        class_header = QLabel(cls.className)
        class_header.setProperty("class", "Title")
        
        # Create timetable
        class_widget = QWidget()
        class_widget.setProperty("class", "NoBackground")
        class_widget_layout = QHBoxLayout(class_widget)
        
        sidebar_widget = QWidget()
        sidebar_widget.setProperty("class", "NoBackground")
        sidebar_widget_layout = QVBoxLayout(sidebar_widget)
        
        remainder_scroll_area = QScrollArea()
        remainder_scroll_area.setWidgetResizable(True)
        remainder_scroll_area.setFixedWidth(settings_width)
        remainder_scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        generate_new_button = QPushButton("Generate New")
        generate_new_button.clicked.connect(self._make_generate_individual_taimetable_func(cls))
        
        remainder_widget = QWidget()
        remainder_widget.setFixedWidth(settings_width)
        remainder_scroll_area.setWidget(remainder_widget)
        
        remainder_widget_layout = QVBoxLayout(remainder_widget)
        
        timetable = ClassTimetable(cls, self, remainder_widget_layout, self.saved_state_changed)
        self.timetable_widgets[cls.uniqueID] = timetable
        self.timetable_parent_widget[cls.uniqueID] = widget
        
        remainder_title = QLabel("Remaining Subjects")
        remainder_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        remainder_widget_layout.addWidget(remainder_title, alignment=Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop)
        
        remainder_widget_layout.addStretch()
        
        class_widget_layout.addWidget(timetable)
        class_widget_layout.addWidget(sidebar_widget)
        
        sidebar_widget_layout.addWidget(remainder_scroll_area, alignment=Qt.AlignmentFlag.AlignHCenter)
        sidebar_widget_layout.addWidget(generate_new_button)
        
        layout.addWidget(class_header)
        layout.addWidget(class_widget)
        
        if cls.index not in self.classes_widget:
            level_widget = QWidget()
            level_layout = QVBoxLayout()
            
            self.classes_widget[cls.index] = level_widget, level_layout, {}
            
            level_widget.setProperty("class", "TimetableWidget")
            level_widget.setLayout(level_layout)
            
            section_header = QWidget()
            section_layout = QHBoxLayout()
            section_header.setProperty("class", "SectionHeader")
            section_header.setStyleSheet("QWidget.SectionHeader {background: none} QLabel {background: none}")
            section_header.setLayout(section_layout)
            
            toogle_button = QPushButton("☰")
            toogle_button.setProperty("class", "Timetable_DP_OptionText")
            
            settings_menu_widget = self._make_timetable_settings(cls.index)
            
            def toogle_menu():
                settings_menu_widget.set_pos(toogle_button.mapToGlobal(QPoint(-150, toogle_button.pos().y() + toogle_button.height())))
                settings_menu_widget.toogle()
            
            toogle_button.clicked.connect(toogle_menu)
            
            section_layout.addWidget(QLabel(f"<span style='font-size: 60px'>{cls.namingConvention[cls.index]}</span>"))
            section_layout.addWidget(toogle_button, alignment=Qt.AlignmentFlag.AlignRight)
            
            level_layout.addWidget(section_header)
            
            self.timetables_layout.addWidget(level_widget)
        
        self.classes_widget[cls.index][2][cls.classID] = widget
        
        return widget
    
    def _make_generate_individual_taimetable_func(self, cls: Class):
        def generate_individual_taimetable():
            response = QMessageBox.warning(
                self,
                "Action Irreversible",
                    "This action cannot be reversed\n"
                    "All information will be overwritten\n"
                    f"Are you sure you want to generate new timetable for {cls.name}",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
                                
            if response != QMessageBox.StandardButton.Yes:
                return
            
            self.school.generateTimetable(cls)
            self.timetable_widgets[cls.uniqueID].populate_timetable()
            
            self.saved_state_changed.emit()
        
        return generate_individual_taimetable


    
