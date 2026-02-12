from frontend.imports import *

from frontend.sub_widgets import *
from middle.frameworks import *

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
    def __init__(self, editor: 'TimeTableEditor', progress_bar: _ProgressBar, saved_state_changed: pyqtBoundSignal):
        super().__init__()
        
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
        
        def period_amt_number_changed(number: int):
            global update_break_period
            
            for se_id in self.editor.classes_widget:
                self.editor.cls_levels_data[se_id]["period-func"](number)
            
            self.breakperiod_edit.max_num = number
            if self.breakperiod_edit.max_num < self.breakperiod_edit.number():
                update_break_period = False
                self.breakperiod_edit.setNumber(self.breakperiod_edit.max_num)
                update_break_period = True
            
            for cls in self.school.classes.values():
                for day in cls.dotw_data:
                    cls.dotw_data[day] = number, cls.dotw_data[day][1]
        
        def break_period_number_changed(number: int):
            if update_break_period:
                for se_id in self.editor.classes_widget:
                    self.editor.cls_levels_data[se_id]["break-func"](number)
            
            for cls in self.school.classes.values():
                for day in cls.dotw_data:
                    cls.dotw_data[day] = cls.dotw_data[day][0], number
        
        # self.period_amt_edit = NumberLineEdit(self.info["periodAmount"], 1, 20)
        # self.period_amt_edit.setPlaceholderText("Period amount")
        # self.period_amt_edit.textChanged.connect(period_amt_number_changed)
        
        # self.breakperiod_edit = NumberLineEdit(self.info["breakPeriod"], 1, self.period_amt_edit.number())  # Temporary
        # self.breakperiod_edit.setPlaceholderText("Break period")
        # self.breakperiod_edit.textChanged.connect(break_period_number_changed)
        
        left_sub_option_widget = QWidget()
        
        left_sub_option_layout = QHBoxLayout()
        left_sub_option_widget.setLayout(left_sub_option_layout)
        
        self.clash_viewer = ClashesViewer(self.editor.school)
        
        show_clashes_checkb = QPushButton("Clashes")
        show_clashes_checkb.clicked.connect(self.clash_viewer.exec)
        
        left_sub_option_layout.addWidget(show_clashes_checkb)
        
        # left_option_layout.addWidget(self.period_amt_edit)
        # left_option_layout.addWidget(self.breakperiod_edit)
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
        
        self.editor.school.generate_timetable()
    
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
    def __init__(self, cls: ClassFW, editor: 'TimeTableEditor', remainder_layout: QVBoxLayout, saved_state_changed: pyqtBoundSignal):
        super().__init__()
        
        self.cls = cls
        self.editor = editor
        self.saved_state_changed = saved_state_changed
        
        self.remainder_layout = remainder_layout
        self.remainder_labels: list[DraggableSubjectLabel] = []
        
        self.periodsPerDay = [p for p, _ in self.cls.dotw_data.values()]
        self.breakTimePeriods = [b for _, b in self.cls.dotw_data.values()]
        self.periods = max(self.periodsPerDay)
        
        # Configure table
        self.setRowCount(self.periods)
        self.setColumnCount(len(self.cls.dotw_data))
        self.setHorizontalHeaderLabels([day[0] for day in self.cls.dotw_data])
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
        
        # Variables
        self.current_source = None
    
    def get_max_subject_amount(self):
        periods, break_periods, _ = self.editor.school.project["levels"][self.cls.section_id][1]
        
        max_subject_amt = 0
        
        for index, total_periods in enumerate(periods):
            max_subject_amt += total_periods - (1 if break_periods[index] <= total_periods else 0)
        
        return max_subject_amt
    
    def get_total_subject_amount(self):
        return sum(len(subjects) for subjects in self.cls.timetable.values())
    
    def update_break_time_color(self):
        for row in range(self.rowCount()):
            for col in range(self.columnCount()):
                item = self.item(row, col)
                if item.break_time:
                    item.set_color()
    
    def timetable_exchange(self, source_item: TimeTableItem, target_item: TimeTableItem):
        source_row, source_col = self.row(source_item), self.column(source_item)
        target_row, target_col = self.row(target_item), self.column(target_item)
        
        # Same timetable swap
        self.blockSignals(True)  # Prevent unnecessary updates
        
        # Create new items
        new_target = TimeTableItem(source_item.subject)
        new_source = TimeTableItem(target_item.subject)
        
        # Remove old items
        self.takeItem(source_row, source_col)
        self.takeItem(target_row, target_col)
        
        # Set new items
        self.setItem(target_row, target_col, new_target)
        self.setItem(source_row, source_col, new_source)
        
        # Middle timetable replacement
        self._swap(source_row, source_col, target_row, target_col)
        
        # Force refresh
        self.blockSignals(False)
        self.update()
    
    def exportify(self):
        widget = QWidget()
        layout = QVBoxLayout()
        
        widget.setLayout(layout)
        
        layout.setSpacing(5)
        layout.setContentsMargins(0, 0, 0, 0)
        
        new_ttbl_widget = ClassTimetable(self.cls, self.editor, self.remainder_layout, self.saved_state_changed)
        
        for row in range(new_ttbl_widget.rowCount()):
            for col in range(new_ttbl_widget.columnCount()):
                item = new_ttbl_widget.item(row, col)
                if item.break_time:
                    item.set_color("black")
        
        layout.addWidget(QLabel(self.cls.name()))
        layout.addWidget(new_ttbl_widget)
        
        return widget
    
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
            
            if source is not None and (self.editor.remainder_source_ref is not None or source.subject.id != FREE_PERIOD_ID):
                event.accept()
                if self.editor.remainder_source_ref is None:
                    self.current_source: TimeTableItem = source
    
    def dragMoveEvent(self, event: QDragMoveEvent):
        if event.mimeData().hasText():
            source_cls: ClassTimetable = event.source()
            
            col = self.columnAt(int(event.position().x()))
            row = self.rowAt(int(event.position().y()))
            
            ignore = True
            if self.editor.remainder_source_ref is None:
                ignore = source_cls.cls.id() != self.cls.id() or (
                    self.drag_source_col != col and (
                        row == self.breakTimePeriods[col] - 1 or
                        self.breakTimePeriods[self.drag_source_col] == self.drag_source_row + 1
                        )
                    )
            else:
                ignore = row == self.breakTimePeriods[col] - 1
            
            if ignore:
                event.ignore()
            else:
                event.accept()
    
    def dropEvent(self, event: QDropEvent):
        if event.mimeData().hasText():
            if self.current_source is not None:
                target_row = self.rowAt(int(event.position().y()))
                target_col = self.columnAt(int(event.position().x()))
                target_item = self.item(target_row, target_col)
                
                source_class = self.editor.timetable_widgets[self.cls.id()].cls
                
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
                
                if isinstance(target_item, TimeTableItem) and not target_item.free_period:
                    target_subject = target_item.subject
                    
                    # Create new items
                    new_source = DraggableSubjectLabel(target_subject)
                    new_source.clicked.connect(self.editor.make_ds_func(new_source))
                    
                    # Set new items
                    self.add_remainder(new_source, self.remainder_layout.indexOf(self.editor.remainder_source_ref))
                    
                    self._replace(FreePeriodFW(), row, col)
                
                # Remove remainder widget
                self.remove_remainder(self.editor.remainder_source_ref)
                
                self.remainder_layout.update()
                
                self.blockSignals(False)
                
                self._replace(self.editor.remainder_source_ref.subject, row, col)
                
                self.saved_state_changed.emit()
                
                event.accept()
            
            self.editor.remainder_source_ref = None
            self.current_source = None
    
    def add_remainder(self, remainder: DraggableSubjectLabel, index: int | None = None):
        remainder.subject.lockedPeriod = None
        
        if index is not None:
            self.remainder_layout.insertWidget(index, remainder, alignment=Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop)
            self.remainder_labels.insert(index - 1, remainder)
            self.timetable_remains.insert(index - 1, remainder.subject)
        else:
            self.remainder_layout.insertWidget(self.remainder_layout.count() - 1, remainder, alignment=Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop)
            self.remainder_labels.append(remainder)
            self.timetable_remains.append(remainder.subject)
    
    def remove_remainder(self, remainder: DraggableSubjectLabel):
        self.remainder_labels.remove(remainder)
        self.remainder_layout.removeWidget(remainder)
        self.timetable_remains.remove(remainder.subject)
        
        remainder.deleteLater()
    
    def clear_remainder(self):
        for widg in self.remainder_layout.parentWidget().findChildren(DraggableSubjectLabel):
            self.remainder_layout.removeWidget(widg)
            widg.deleteLater()
        
        for widg in self.remainder_labels.copy():
            self.remainder_labels.remove(widg)
            widg.deleteLater()
        
        self.timetable_remains.clear()
    
    def _replace(self, subject: SubjectPeriodFW, row: int, column: int):
        self.cls.timetable[list(self.cls.dotw_data)[column]][row] = subject
    
    def _swap(self, subject: SubjectPeriodFW, row1: int, column1: int, row2: int, column2: int):
        d1 = list(self.cls.dotw_data)[column1]
        d2 = list(self.cls.dotw_data)[column2]
        
        subject1 = self.cls.timetable[d1][row1]
        subject2 = self.cls.timetable[d2][row2]
        
        self.cls.timetable[d1].pop(row1)
        self.cls.timetable[d1].insert(row1, subject2)
        
        self.cls.timetable[d2].pop(row2)
        self.cls.timetable[d2].insert(row2, subject1)
    
    def populate_timetable(self):
        """Load the timetable data into the grid"""
        for col, (day, _) in enumerate(self.cls.dotw_data.items()):
            subjects = self.cls.timetable[day] + [FreePeriodFW() for _ in range(max(self.periodsPerDay) - len(self.cls.timetable[day]))]
            
            for row, subject in enumerate(subjects):
                item = TimeTableItem(subject)
                self.setItem(row, col, item)
        
        rem_subjects = [subj for subj in self.timetable_remains if subj.id != FREE_PERIOD_ID]
        
        self.clear_remainder()
        
        for subject in rem_subjects:
            subject_label = DraggableSubjectLabel(subject)
            subject_label.clicked.connect(self.editor.make_ds_func(subject_label))
            
            self.add_remainder(subject_label)
    
    def show_context_menu(self, pos):
        item = self.itemAt(pos)
        
        if item and isinstance(item, TimeTableItem) and not item.free_period and not item.break_time:
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
                free_period_subject = FreePeriodFW()
                
                row = self.row(item)
                col = self.column(item)
                
                # Move to remainders if deleted
                subject_label = DraggableSubjectLabel(item.subject)
                subject_label.clicked.connect(self.editor.make_ds_func(subject_label))
                
                self.add_remainder(subject_label)
                
                self.setItem(row, col, TimeTableItem(free_period_subject))
                
                self._replace(free_period_subject, row, col)
                
                self.saved_state_changed.emit()
            elif lock_action is not None and action == lock_action:
                item.subject.lockedPeriod = [self.row(item), 1]  # Lock to current period
                self.saved_state_changed.emit()
                
                QMessageBox.critical("NotFullyImplementedError", "This feature has only been partially implemented")
            elif unlock_action is not None and action == unlock_action:
                item.subject.lockedPeriod = None
                self.saved_state_changed.emit()
                
                QMessageBox.critical("NotFullyImplementedError", "This feature has only been partially implemented")
            elif action == goto_subject_action:
                QMessageBox.critical("NotImplementedError", "This feature has not been implemented")
            elif action == goto_teacher_action:
                QMessageBox.critical("NotImplementedError", "This feature has not been implemented")

class TimeTableEditor(QWidget):
    def __init__(self, main_window: QMainWindow, school: SchoolFrameWork, saved_state_changed: pyqtBoundSignal):
        super().__init__()
        
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
        
        self.cls_levels_data: dict[str, dict[str, bool | SelectionList]] = {}
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
            self.classes_widget[cls.section_id][1].addWidget(widget)
        
        # Create settings for timetables
        self.settings_widget = _TimetableSettings(self, self.progress_bar, self.saved_state_changed)
        
        self.main_layout.addWidget(self.settings_widget)
        self.main_layout.addWidget(progress_bar_widget)
        self.main_layout.addWidget(self.scroll_area)
    
    def exportify_widgets(self, ttbl_widgets: list[ClassTimetable]):
        style_sheet = """
            QWidget {
                background-color: white;
                color: black;
            }
            
            QLabel {
                font-size: 20px;
                color: black;
                background-color: white;
            }
            
            QTableWidget {
                background-color: white;
                border: 2px solid black;
                gridline-color: black;
                color: black
            }
            QHeaderView::section {
                background-color: black;
                color: white;
                padding: 8px;
                border: none;
            }
        """
        main_widget = QWidget()
        main_layout = QVBoxLayout()
        
        main_widget.setLayout(main_layout)
        main_widget.setStyleSheet(style_sheet)
        
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        for ttbl_widget in ttbl_widgets:
            main_layout.addWidget(ttbl_widget.exportify())
        
        return main_widget
    
    def set_editor_from_school(self, school: SchoolFrameWork):
        self.school = school
        
        for se_id, (widget, layout, options_widget_data) in self.classes_widget.copy().items():
            if next((False for cls in self.school.classes.values() if cls.section_id == se_id), True):
                self.classes_widget.pop(se_id)
                
                for sp_id in self.timetable_parent_widget.copy():
                    if se_id == self.timetable_widgets[sp_id].cls.section_id:
                        self.timetable_widgets.pop(sp_id)
                        self.timetable_parent_widget.pop(sp_id)
            else:
                for option_id, widget in options_widget_data.copy().items():
                    if next((False for cls in self.school.classes.values() if cls.specifier_id == option_id), True):
                        class_id = ClassFW.get_id(se_id, option_id)
                        
                        self.timetable_widgets.pop(class_id)
                        self.timetable_parent_widget.pop(class_id)
                        
                        sub_widget = options_widget_data.pop(option_id)
                        
                        layout.removeWidget(sub_widget)
            
            self.timetables_layout.removeWidget(widget)
        
        classes = {}
        for cls in self.school.classes.values():
            classes[cls.id()] = (
                self.timetable_parent_widget[cls.id()]
                if cls.id() in self.timetable_parent_widget else
                self._make_timetable_for_each_class(cls)
            )
            
            temp_timetable_table = self.timetable_widgets[cls.id()].cls.timetable
            temp_timetable_remainder_content = self.timetable_widgets[cls.id()].cls.timetable_remains
            
            self.timetable_widgets[cls.id()].cls = cls
            self.timetable_widgets[cls.id()].clear_remainder()
            
            for s in temp_timetable_remainder_content:
                self.timetable_widgets[cls.id()].add_remainder(DraggableSubjectLabel(s))
        
        for class_id, widget in classes.items():
            ttbl = self.timetable_widgets[class_id]
            
            for col, (day, subjects) in enumerate(ttbl.cls.timetable.items()):
                for row, subj in enumerate(subjects):
                    ttbl._replace(subj, row, col)
            
            ttbl.clear_remainder()
            
            for subjects in enumerate(ttbl.cls.timetable_remains):
                ttbl.add_remainder(DraggableSubjectLabel(subj))
            
            # for subj in ttbl.cls.subjects:
            #     totals[class_id][subj.id()] = 0
            
            # for col in range(ttbl.columnCount()):
            #     for row in range(ttbl.rowCount()):
            #         ttbl_item: TimeTableItem = ttbl.item(row, col)
                    
            #         is_present = ttbl_item.subject.id() in totals[class_id]
                    
            #         is_not_break_or_free = ttbl_item.subject.id not in (FREE_PERIOD_ID, BREAK_PERIOD_ID)
            #         is_removed = is_not_break_or_free and next((False for s in ttbl.cls.subjects if s.id() == ttbl_item.subject.id()), True)
            #         is_per_week_exceeded = is_not_break_or_free and (not is_present or totals[class_id][ttbl_item.subject.id()] > school.subjects[ttbl_item.subject.id()].PERWEEK)
                    
            #         if is_present:
            #             totals[class_id][ttbl_item.subject.id()] += 1
                    
            #         if is_removed or is_per_week_exceeded:
            #             subj = FreePeriodFW()
            #             ttbl._replace(subj, row, col)
                        
            #             totals[class_id].pop(ttbl_item.subject.id(), None)
                    
            #         if is_not_break_or_free and not is_per_week_exceeded and totals[class_id][ttbl_item.subject.id()] == school.subjects[ttbl_item.subject.id()].PERWEEK:
            #             totals[class_id].pop(ttbl_item.subject.id())
            
            # for d_labels in ttbl.remainder_labels.copy():
            #     is_present = d_labels.subject.id() in totals[class_id]
                
            #     if is_present:
            #         totals[class_id][d_labels.subject.id()] += 1
                
            #     is_removed = next((False for s in ttbl.cls.subjects if s.id() == d_labels.subject.id()), True)
            #     is_per_week_exceeded = not is_present or totals[class_id][d_labels.subject.id()] > school.subjects[d_labels.subject.id()].PERWEEK
                
            #     if is_removed or is_per_week_exceeded:
            #         ttbl.remove_remainder(d_labels)
            #         totals[class_id].pop(ttbl_item.subject.id(), None)
            
            # for s_id, s_amt in totals[class_id].items():
            #     for _ in range(school.subjects[s_id].PERWEEK - s_amt):
            #         ttbl.add_remainder(DraggableSubjectLabel(self.school.subjects[s_id]))
            
            # totals.pop(class_id)
            
            ttbl.populate_timetable()
            self.classes_widget[ttbl.cls.section_id][1].addWidget(widget)
    
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
    
    def update_data_interaction(self, _: int, curr_index: int):
        pass
    
    # def paintEvent(self, a0):
    #     super().paintEvent(a0)
        
    #     painter = QPainter(self)
    #     painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
    #     pen = painter.pen()
    #     pen.setWidth(5)
    #     pen.setBrush(QColor("#12ab93"))
    #     painter.setPen(pen)
        
    #     painter.setBrush(Qt.BrushStyle.NoBrush)
    #     painter.drawLine(0, 0, 700, 500)
    
    def _certify_class_level_info(self, class_index: int, class_id: str, option_id: str):
        if class_index < len(self.school.project["levels"]):
            if class_id + option_id in self.school.project["levels"][class_index][1]:
                return True
        
        return False
    
    def _set_school_timetable(self):
        for _, cls in self.school.classes.items():
            self.timetable_widgets[cls.id()].populate_timetable()
    
    def _make_timetable_settings(self, se_id: str):
        widget_menu = MenuFrame()
        layout = widget_menu.layout()
        
        break_updateable = True
        
        def _generating_finished():
            for ttbl in self.timetable_widgets.values():
                if ttbl.cls.section_id == se_id:
                    ttbl.populate_timetable()
            
            self.class_generator_threads.pop(se_id)
            
        def period_amt_changed(curr_period_amt: int):
            global break_updateable
            
            for ttbl in self.timetable_widgets.values():
                if ttbl.cls.section_id == se_id:
                    for day in self.school.classes[ttbl.cls.id()].dotw_data:
                        self.school.classes[ttbl.cls.id()].dotw_data[day] = curr_period_amt, self.school.classes[ttbl.cls.id()].dotw_data[day][1]
                    
                    for col, (day, (prev_period_amt, _)) in enumerate(ttbl.cls.dotw_data.items()):
                        if ttbl.cls.dotw_data[col][2] > curr_period_amt:
                            ttbl.timetable_exchange(ttbl.item(ttbl.cls.dotw_data[col][2] - 1, col), ttbl.item(curr_period_amt - 1, col))
                        
                        if prev_period_amt > curr_period_amt:
                            for s in ttbl.cls.timetable[day][curr_period_amt:]:
                                if s.id not in (BREAK_PERIOD_ID, FREE_PERIOD_ID):
                                    ttbl.add_remainder(DraggableSubjectLabel(s))
                            
                            ttbl.cls.timetable[day][curr_period_amt:] = []
                        elif prev_period_amt < curr_period_amt:
                            for _ in range(curr_period_amt - prev_period_amt):
                                ttbl.cls.timetable[day].append(FreePeriodFW())
                        
                        ttbl.cls.dotw_data[day] = curr_period_amt, ttbl.cls.dotw_data[day][1]
                        ttbl.periodsPerDay[col] = curr_period_amt
                    
                    ttbl.setRowCount(curr_period_amt)
                    ttbl.setVerticalHeaderLabels([f"Period {i + 1}" for i in range(ttbl.rowCount())])
                    ttbl.setFixedHeight(ttbl.rowCount() * 30 + 45)
                    
                    for col in range(ttbl.columnCount()):
                        for row in range(ttbl.rowCount()):
                            if ttbl.item(row, col) is None:
                                ttbl.setItem(row, col, TimeTableItem(FreePeriodFW()))
            
            breakperiod_edit.max_num = curr_period_amt
            if breakperiod_edit.number() > curr_period_amt:
                break_updateable = False
                breakperiod_edit.setNumber(curr_period_amt)
                break_updateable = True
            
            self.saved_state_changed.emit()
        
        def break_period_changed(curr_break_period: int):
            if break_updateable:
                for ttbl in self.timetable_widgets.values():
                    for day in self.school.classes[ttbl.cls.id()].dotw_data:
                        self.school.classes[ttbl.cls.id()].dotw_data[day] = self.school.classes[ttbl.cls.id()].dotw_data[day][0], curr_break_period
                    
                    if ttbl.cls.section_id == se_id:
                        for col, (_, _, prev_break_period) in enumerate(ttbl.cls.dotw_data):
                            ttbl.timetable_exchange(ttbl.item(prev_break_period - 1, col), ttbl.item(curr_break_period - 1, col))
                
                self.saved_state_changed.emit()
        
        def generate_new_func():
            classes = []
            
            for ttbl in self.timetable_widgets.values():
                if ttbl.cls.section_id == se_id:
                    classes.append(ttbl.cls)
            
            def generate_new_level():
                self.school.generate_timetable(classes)
            
            if se_id not in self.class_generator_threads:
                response = QMessageBox.warning(self, "Action Irreversible", "This action cannot be reversed\n"
                                                                            "All information will be overwritten",
                                                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
                
                if response != QMessageBox.StandardButton.Yes:
                    return
                self.progress_bar.set_max(lambda: sum(ttbl.periodsPerDay) - len(ttbl.periodsPerDay))
                self.progress_bar.set_var_func(lambda: sum(len(subjects) for subjects in ttbl.cls.timetable.values()))
                self.progress_bar.start(100)
                
                self.class_generator_threads[se_id] = Thread(self.main_window, generate_new_level)
                self.class_generator_threads[se_id].finished.connect(_generating_finished)
                self.class_generator_threads[se_id].start()
            
            self.saved_state_changed.emit()
        
        self.cls_levels_data[se_id] = {
            "break-func": break_period_changed,
            "period-func": period_amt_changed
        }
        
        [cls.dotw_data[day] for cls in self.school.classes.values() if cls.section_id == se_id]
        
        period_amt_edit = NumberLineEdit(max(p for p, _ in self.school.general_dotw_data.values()), 1, 20)
        period_amt_edit.setPlaceholderText("Periods Amt")
        period_amt_edit.textChanged.connect(period_amt_changed)
        
        breakperiod_edit = NumberLineEdit(max(b for _, b in self.school.general_dotw_data.values()), period_amt_edit.min_num, period_amt_edit.number())
        breakperiod_edit.setPlaceholderText("Break period")
        breakperiod_edit.textChanged.connect(break_period_changed)
        
        generate_new_button = QPushButton("Generate New")
        generate_new_button.clicked.connect(generate_new_func)
        
        layout.addWidget(period_amt_edit)
        layout.addWidget(breakperiod_edit)
        layout.addSpacing(5)
        
        layout.addSpacing(20)
        layout.addWidget(generate_new_button, alignment=Qt.AlignmentFlag.AlignHCenter)
        
        return widget_menu
    
    def _make_timetable_for_each_class(self, cls: ClassFW):
        widget = QWidget()
        layout = QVBoxLayout()
        
        widget.setProperty("class", "TimetableWidget")
        widget.setLayout(layout)
        
        settings_width = 200
        
        class_header = QLabel(cls.name())
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
        self.timetable_widgets[cls.id()] = timetable
        self.timetable_parent_widget[cls.id()] = widget
        
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
        
        if cls.section_id not in self.classes_widget:
            level_widget = QWidget()
            level_layout = QVBoxLayout()
            
            self.classes_widget[cls.section_id] = level_widget, level_layout, {}
            
            level_widget.setProperty("class", "TimetableWidget")
            level_widget.setLayout(level_layout)
            
            section_header = QWidget()
            section_layout = QHBoxLayout()
            section_header.setProperty("class", "SectionHeader")
            section_header.setStyleSheet("QWidget.SectionHeader {background: none} QLabel {background: none}")
            section_header.setLayout(section_layout)
            
            toogle_button = QPushButton("☰")
            toogle_button.setProperty("class", "Timetable_DP_OptionText")
            
            settings_menu_widget = self._make_timetable_settings(cls.section_id)
            
            def toogle_menu():
                settings_menu_widget.set_pos(toogle_button.mapToGlobal(QPoint(-150, toogle_button.pos().y() + toogle_button.height())))
                settings_menu_widget.toogle()
            
            toogle_button.clicked.connect(toogle_menu)
            
            section_layout.addWidget(QLabel(f"<span style='font-size: 60px'>{cls.section_name}</span>"))
            section_layout.addWidget(toogle_button, alignment=Qt.AlignmentFlag.AlignRight)
            
            level_layout.addWidget(section_header)
            
            self.timetables_layout.addWidget(level_widget)
        
        self.classes_widget[cls.section_id][2][cls.specifier_id] = widget
        
        return widget
    
    def _make_generate_individual_taimetable_func(self, cls: ClassFW):
        def generate_individual_taimetable():
            response = QMessageBox.warning(
                self,
                "Action Irreversible",
                    "This action cannot be reversed\n"
                    "All information will be overwritten\n"
                    f"Are you sure you want to generate new timetable for {cls.name()}",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
                                
            if response != QMessageBox.StandardButton.Yes:
                return
            
            self.school.generate_timetable(cls)
            self.timetable_widgets[cls.id()].populate_timetable()
            
            self.saved_state_changed.emit()
        
        return generate_individual_taimetable


    
