from frontend.imports import *
from frontend.base_widgets import *

class SelectionList(BaseSubWidget):
    def __init__(self, title: str, info: list, saved_state_changed: pyqtBoundSignal, constant_indexing: bool = False):
        super().__init__(title, info, saved_state_changed)
        self.setFixedSize(400, 300)
        self.container.setProperty("class", "SelectionList")
        
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        
        self.container_layout.setContentsMargins(10, 20, 20, 5)
        self.container_layout.setSpacing(30)
        
        self.scroll_area.setWidget(self.container)
        self.main_layout.addWidget(self.scroll_area)
        
        # Initialize widgets
        split_index = info.index(None)
        selected_items = info[:split_index]
        unselected_items = info[split_index+1:]
        
        self.index_tracker = {}
        
        # Add selected items
        for item_index, (item_id, item_name) in enumerate(selected_items):
            widget = SelectedWidget(item_id, item_name, self.container_layout, self.saved_state_changed, self.index_tracker if constant_indexing else None)
            self.container_layout.addWidget(widget)
            
            self.index_tracker[item_id] = item_index
        
        # Add unselected items
        for item_index, (item_id, item_name) in enumerate(unselected_items):
            widget = UnselectedWidget(item_id, item_name, self.container_layout, self.saved_state_changed, self.index_tracker if constant_indexing else None)
            self.container_layout.addWidget(widget)
            
            self.index_tracker[item_id] = len(selected_items) + item_index
        
        self.container_layout.addStretch()
    
    def get(self):
        content = []
        
        for widget in self.container.children():
            if isinstance(widget, SelectedWidget):
                content.append((widget.id, widget.text))
        
        content.append(None)
        
        for widget in self.container.children():
            if isinstance(widget, UnselectedWidget):
                content.append((widget.id, widget.text))
        
        return content
    
    def get_selected(self):
        data = self.get()
        
        return [name for _, name in data[:data.index(None)]]
    
    def go_to(self, _id):
        for widget in self.container.children():
            if isinstance(widget, (SelectedWidget, UnselectedWidget)) and widget.id == _id:
                def func():
                    self.scroll_area.verticalScrollBar().setValue(widget.y())
                    widget.setFocus()
                
                QTimer.singleShot(200, func)
                
                break
    
    @staticmethod
    def fix_none_selection_content_problem(problem_content_list: list):
        fixed_content_list = problem_content_list.copy()
        fixed_content_list.insert(fixed_content_list.index(None), (None, None))
        fixed_content_list.remove(None)
        
        return fixed_content_list

class SubjectDropdownCheckBoxes(BaseSubWidget):
    def __init__(self, title: str, info: dict[str, dict[str, dict[str, dict[str, str | bool]]] | dict[int, str]], saved_state_changed: pyqtBoundSignal, general_data: dict):
        super().__init__(title, info, saved_state_changed)
        self.general_data = general_data
        
        self.setFixedSize(400, 300)
        
        self.saved_state_changed = saved_state_changed
        
        self.main_guy_is_clicked = False
        self.mini_guy_is_clicked = False
        
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        
        self.container_layout.setContentsMargins(0, 0, 0, 0)
        
        self.scroll_area.setWidget(self.container)
        self.main_layout.addWidget(self.scroll_area)
        
        self.class_check_box_tracker = {"main_cb": {}, "sub_cbs": {}, "icon": {}, "widget": {}}
        
        for widget in self._create_checkbox_widgets(self.info, self.general_data, self.class_check_box_tracker):
            self.container_layout.addWidget(widget, alignment=Qt.AlignmentFlag.AlignTop)
        
        self.container_layout.addStretch()
    
    def go_to(self, _id):
        for lvl_id, lvl_data in self.get().items():
            if lvl_id == _id:
                if not self.class_check_box_tracker["widget"][lvl_id].isVisible():
                    self.class_check_box_tracker["icon"][lvl_id].mouseclicked.emit()
                
                def func():
                    self.scroll_area.verticalScrollBar().setValue(self.class_check_box_tracker["widget"][lvl_id].y())
                    
                    self.class_check_box_tracker["widget"][lvl_id].setFocus()
                
                QTimer.singleShot(200, func)
                
                break
            
            for cls_id, cls_state in lvl_data.items():
                if not cls_state:
                    continue
                
                if "-" in _id or cls_id == _id:
                    if cls_id != _id:
                        f_lvl_id, f_cls_id = _id.split("-")
                        if lvl_id != f_lvl_id or cls_id != f_cls_id:
                            continue
                    
                    if not self.class_check_box_tracker["widget"][lvl_id].isVisible():
                        self.class_check_box_tracker["icon"][lvl_id].mouseclicked.emit()
                    
                    self.scroll_area.verticalScrollBar().setValue(self.class_check_box_tracker["sub_cbs"][lvl_id][cls_id].y())
                    
                    self.class_check_box_tracker["sub_cbs"][lvl_id][cls_id].setFocus()
                    
                    break
            else:
                continue
            
            break
    
    def _create_checkbox_widgets(self, data, general_data, class_check_box_tracker: dict[str, dict[str, QCheckBox | QWidget | dict[str, QCheckBox]]]):
        updated_data = deepcopy(general_data)
        for class_id, options_info in data.items():
            updated_data["content"][class_id].update(options_info)
        
        id_mapping = updated_data["id_mapping"]
        
        widgets: list[QWidget] = []
        all_clicked_checkboxes: list[QCheckBox] = []
        
        for class_id, class_options in updated_data["content"].items():
            main_widget = QWidget()
            main_widget.setProperty("class", "Bordered")
            main_widget.setProperty("class", "DropdownCheckboxes")
            
            widget_wrapper_layout = QVBoxLayout()
            widget_wrapper_layout.setSpacing(0)
            main_widget.setLayout(widget_wrapper_layout)
            
            open_dp_func = self.make_open_dp_func(class_id, class_check_box_tracker)
            
            def make_open_dp_func(odp_param_func):
                def odp_func(a0: QMouseEvent | None):
                    if a0.button() == Qt.MouseButton.LeftButton: # type: ignore
                        odp_param_func()
                
                return odp_func
            
            header = QWidget()
            header.setProperty("class", "DPC_Header")
            header.setFixedHeight(50)
            header.mousePressEvent = make_open_dp_func(open_dp_func)
            
            
            header_layout = QHBoxLayout(header)
            header_layout.setContentsMargins(12, 0, 12, 0)
            
            dp_icon = CustomLabel("▼", 270)
            dp_icon.setProperty("class", "Arrow")
            dp_icon.mouseclicked.connect(open_dp_func)
            dp_icon.setContentsMargins(0, 0, 10, 0)
            
            title = QLabel(id_mapping["main"][class_id])
            
            check_box = QCheckBox()
            check_box.clicked.connect(self.make_main_checkbox_func(class_id, class_check_box_tracker))
            all_clicked = False not in list(class_options.values()) and class_options
            
            header_layout.addWidget(dp_icon)
            header_layout.addWidget(title)
            header_layout.addStretch()
            header_layout.addWidget(check_box)
            
            class_check_box_tracker["icon"][class_id] = dp_icon
            class_check_box_tracker["sub_cbs"][class_id] = {}
            class_check_box_tracker["main_cb"][class_id] = check_box
            class_check_box_tracker["widget"][class_id], to_be_clicked = self.make_dp_widget(class_id, class_options, all_clicked, data, updated_data, class_check_box_tracker)
            
            widget_wrapper_layout.addWidget(header)
            widget_wrapper_layout.addWidget(class_check_box_tracker["widget"][class_id]) # type: ignore
            
            all_clicked_checkboxes.extend(to_be_clicked)
            
            widgets.append(main_widget)
        
        for cb in all_clicked_checkboxes:
            cb.click()
        
        return widgets
    
    def make_open_dp_func(self, class_id: str, class_check_box_tracker: dict[str, Any]):
        def open_dp():
            widget: QWidget = class_check_box_tracker["widget"][class_id]
            
            class_check_box_tracker["icon"][class_id].setAngle(0 if class_check_box_tracker["icon"][class_id].angle != 0 else 270)
            
            if widget.isVisible():
                widget.setVisible(False)
            else:
                widget.setVisible(True)
        
        return open_dp
    
    def make_dp_widget(self, class_id: str, options: dict[str, bool], all_clicked: bool, info, updated_data, class_check_box_tracker: dict[str, Any]):
        dp_widget = QWidget()
        dp_widget.setProperty("class", "DPC_Body")
        
        dp_layout = QVBoxLayout()
        dp_layout.setSpacing(2)
        dp_widget.setLayout(dp_layout)
        
        clicked_cbs: list[QCheckBox] = []
        
        for optionID, optionState in options.items():
            option_layout = QHBoxLayout()            
            
            dp_title = QLabel(updated_data["id_mapping"]["sub"][class_id][optionID])
            dp_checkbox = QCheckBox()
            
            class_check_box_tracker["sub_cbs"][class_id][optionID] = dp_checkbox
            
            dp_checkbox.clicked.connect(self.make_sub_checkbox_func(class_id, info, updated_data, options, class_check_box_tracker))
            
            if optionState and not dp_checkbox.isChecked():
                clicked_cbs.append(dp_checkbox)
            
            option_layout.addSpacing(50)
            option_layout.addWidget(dp_title)
            option_layout.addStretch()
            option_layout.addWidget(dp_checkbox)
            
            dp_layout.addLayout(option_layout)
        
        dp_widget.setVisible(False)
        
        return dp_widget, clicked_cbs
    
    def make_main_checkbox_func(self, class_id: str, class_check_box_tracker: dict[str, Any]):
        def checkbox_func(is_on):
            if not self.mini_guy_is_clicked:
                self.main_guy_is_clicked = True
                
                if is_on:
                    if not class_check_box_tracker["sub_cbs"][class_id]:
                        QMessageBox.critical(self, "Setting SDCB Error", "No class level option has been made for this class level")
                        self.main_guy_is_clicked = False
                        class_check_box_tracker["main_cb"][class_id].click()
                    else:
                        for c_box in class_check_box_tracker["sub_cbs"][class_id].values():
                            if not c_box.isChecked():
                                c_box.click()
                else:
                    for c_box in class_check_box_tracker["sub_cbs"][class_id].values():
                        if c_box.isChecked():
                            c_box.click()
                
                self.main_guy_is_clicked = False
        
        return checkbox_func
    
    def make_sub_checkbox_func(self, class_id: str, content, updated_data, options: dict[str, bool], class_check_box_tracker: dict[str, Any]):
        def checkbox_func(on):
            if class_id not in content:
                content[class_id] = {}
            
            for checkBoxID, checkBox in class_check_box_tracker["sub_cbs"][class_id].items():
                if not checkBox.isChecked() and class_id in content and checkBoxID in content[class_id]:
                    content[class_id].pop(checkBoxID)
                elif checkBox.isChecked():
                    if class_id not in content:
                        content[class_id] = {}
                    content[class_id][checkBoxID] = True
            
            # new_options = dict.fromkeys(options, False)
            # new_options.update(content[class_id])
            
            # options.update(new_options)
            
            if not sum(list(content[class_id].values())):
                content.pop(class_id)
            
            if not self.main_guy_is_clicked:
                self.mini_guy_is_clicked = True
                
                if on:
                    if len(content[class_id]) == len(updated_data["content"][class_id]) and not class_check_box_tracker["main_cb"][class_id].isChecked():
                        class_check_box_tracker["main_cb"][class_id].click()
                else:
                    if class_check_box_tracker["main_cb"][class_id].isChecked():
                        class_check_box_tracker["main_cb"][class_id].click()
                
                self.mini_guy_is_clicked = False
            
            self.saved_state_changed.emit()
        
        return checkbox_func

class TeacherDropdownCheckBoxes(BaseSubWidget):
    def __init__(self, title, info, saved_state_changed, teacher_id, general_data, default_max_classes, main_window):
        super().__init__(title, info, saved_state_changed)
        
        self.teacher_id = teacher_id
        self.general_data = general_data
        self.default_max_classes = default_max_classes
        self.saved_state_changed = saved_state_changed
        self.main_window = main_window
        
        self.setFixedSize(400, 300)
        
        self.main_guy_is_clicked = False
        self.mini_guy_is_clicked = False
        
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        
        self.container_layout.setContentsMargins(0, 0, 0, 0)
        
        self.main_layout.addWidget(self.scroll_area)
        self.scroll_area.setWidget(self.container)
        
        self.subject_check_box_tracker = {}
        self.class_check_box_tracker = {}
        
        for subject_id, info in self.info["content"].items():
            self.subject_check_box_tracker[subject_id] = {}
            self.class_check_box_tracker[subject_id] = {"main_cb": {}, "sub_cbs": {}, "icon": {}, "max_random": {}, "widget": {}}
            
            main_widget = QWidget()
            sub_main_layout = QVBoxLayout()
            
            main_widget.setProperty("class", "Bordered")
            main_widget.setProperty("class", "DropdownCheckboxes")
            main_widget.setLayout(sub_main_layout)
            
            open_dp_func = self.make_open_subject_func(self.subject_check_box_tracker[subject_id])
            
            def make_open_subject(odp_param_func):
                def odp_func(a0: QMouseEvent | None):
                    if a0.button() == Qt.MouseButton.LeftButton: # type: ignore
                        odp_param_func()
                
                return odp_func
            
            header = QWidget()
            header.setProperty("class", "DPC_Header")
            header.setFixedHeight(50)
            header.mousePressEvent = make_open_subject(open_dp_func)
            
            header_layout = QHBoxLayout(header)
            header_layout.setContentsMargins(12, 0, 12, 0)
            
            dp_icon = CustomLabel("▼", 270)
            dp_icon.setProperty("class", "Arrow")
            dp_icon.mouseclicked.connect(open_dp_func)
            dp_icon.setContentsMargins(0, 0, 10, 0)
            
            title = QLabel(self.info["id_mapping"][subject_id])

            header_layout.addWidget(dp_icon)
            header_layout.addWidget(title)
            header_layout.addStretch()
            
            self.subject_check_box_tracker[subject_id]["icon"] = dp_icon
            self.subject_check_box_tracker[subject_id]["widget"] = self.make_subject_widget(info, self.general_data[subject_id], self.class_check_box_tracker[subject_id])
            
            sub_main_layout.addWidget(header)
            sub_main_layout.addWidget(self.subject_check_box_tracker[subject_id]["widget"])
            
            self.container_layout.addWidget(main_widget, alignment=Qt.AlignmentFlag.AlignTop)
        
        self.container_layout.addStretch()
    
    def go_to(self, _id):
        for subj_id, subj_data in self.get()["content"].items():
            if subj_id == _id:
                def func1():
                    if not self.subject_check_box_tracker[subj_id]["widget"].isVisible():
                        self.subject_check_box_tracker[subj_id]["icon"].mouseclicked.emit()
                    
                    def in_func():
                        self.scroll_area.verticalScrollBar().setValue(self.subject_check_box_tracker[subj_id]["widget"].y())
                        
                        self.subject_check_box_tracker[subj_id]["widget"].setFocus()
                
                    QTimer.singleShot(200, in_func)
                
                QTimer.singleShot(200, func1)
                
                break
            
            for lvl_id, (randomly_selected, lvl_data) in subj_data.items():
                if randomly_selected is None:
                    continue
                
                if _id.count("-") == 1 or lvl_id == _id:
                    if lvl_id != _id:
                        f_subj_id, f_lvl_id = _id.split("-")
                        if subj_id != f_subj_id or lvl_id != f_lvl_id:
                            continue
                    def func2():
                        if not self.subject_check_box_tracker[subj_id]["widget"].isVisible():
                            self.subject_check_box_tracker[subj_id]["icon"].mouseclicked.emit()
                        
                        def in_func():
                            if not self.class_check_box_tracker[subj_id]["widget"][lvl_id].isVisible():
                                self.class_check_box_tracker[subj_id]["icon"][lvl_id].mouseclicked.emit()
                            
                            def inner_func():
                                self.scroll_area.verticalScrollBar().setValue(self.class_check_box_tracker[subj_id]["widget"][lvl_id].y())
                                
                                self.class_check_box_tracker[subj_id]["widget"][lvl_id].setFocus()
                        
                            QTimer.singleShot(200, inner_func)
                        
                        QTimer.singleShot(200, in_func)
                    
                    QTimer.singleShot(250, func2)
                    
                    break
                
                for cls_id, cls_state in lvl_data.items():
                    if not cls_state:
                        continue
                    
                    if _id.count("-") == 2 or cls_id == _id:
                        if cls_id != _id:
                            f_subj_id, f_lvl_id, f_cls_id = _id.split("-")
                            if subj_id != f_subj_id or lvl_id != f_lvl_id or cls_id != f_cls_id:
                                continue
                        
                        def func3():
                            if not self.subject_check_box_tracker[subj_id]["widget"].isVisible():
                                self.subject_check_box_tracker[subj_id]["icon"].mouseclicked.emit()
                            
                            def in_func():
                                if not self.class_check_box_tracker[subj_id]["widget"][lvl_id].isVisible():
                                    self.class_check_box_tracker[subj_id]["icon"][lvl_id].mouseclicked.emit()
                                
                                def inner_func():
                                    self.scroll_area.verticalScrollBar().setValue(self.class_check_box_tracker[subj_id]["sub_cbs"][lvl_id][cls_id].y())
                                    
                                    self.class_check_box_tracker[subj_id]["sub_cbs"][lvl_id][cls_id].setFocus()
                        
                                QTimer.singleShot(200, inner_func)
                            
                            QTimer.singleShot(200, in_func)
                            
                        QTimer.singleShot(300, func3)
                        
                        break
                else:
                    continue
                
                break
    
    def _create_checkbox_widgets(self, data: dict[str, dict[str, dict[str, str | bool]]] | dict[int, str], general_data, class_check_box_tracker: dict[str, dict[str, QCheckBox | QWidget | dict[str, QCheckBox]]]):
        updated_data = deepcopy(general_data)
        
        for class_id, (random_on, options_info) in data.items():
            updated_data["content"][class_id][0] = random_on
            for opt_id, opt_state in options_info.items(): # type: ignore
                if not isinstance(updated_data["content"][class_id][1][opt_id], str) or opt_state:
                    updated_data["content"][class_id][1][opt_id] = options_info[opt_id]
        
        id_mapping = updated_data["id_mapping"]
        
        widgets: list[QWidget] = []
        random_on_checkboxes: list[QCheckBox] = []
        
        for class_id, (random_on, class_options) in updated_data["content"].items():
            main_widget = QWidget()
            
            main_widget.setProperty("class", "Bordered")
            main_widget.setProperty("class", "DropdownCheckboxes")
            
            widget_wrapper_layout = QVBoxLayout()
            widget_wrapper_layout.setSpacing(0)
            main_widget.setLayout(widget_wrapper_layout)
            
            open_dp_func = self.make_odp_func(data, class_id, class_check_box_tracker)
            
            def make_open_dp_func(odp_param_func):
                def odp_func(a0: QMouseEvent | None):
                    if a0.button() == Qt.MouseButton.LeftButton: # type: ignore
                        odp_param_func()
                
                return odp_func
            
            header = QWidget()
            header.setProperty("class", "DPC_Header")
            header.setFixedHeight(50)
            header.mousePressEvent = make_open_dp_func(open_dp_func)
            
            header_layout = QHBoxLayout(header)
            header_layout.setContentsMargins(12, 0, 12, 0)
            
            dp_icon = CustomLabel("▼", 270)
            dp_icon.setProperty("class", "Arrow")
            dp_icon.mouseclicked.connect(open_dp_func)
            dp_icon.setContentsMargins(0, 0, 10, 0)
            
            title = QLabel(id_mapping["main"][class_id])
            
            max_random_text_input = NumberLineEdit(random_on if random_on is not None else self.main_window.default_max_classes, len(class_options))
            max_random_text_input.edit.setToolTip("Max Classes")
            max_random_text_input.setVisible(False)
            max_random_text_input.textChanged.connect(self.make_random_text_changed_func(class_id, data))
            
            check_box = QCheckBox("Random")
            check_box.clicked.connect(self.make_main_checkbox_func(class_id, data, class_check_box_tracker))
            
            if random_on:
                random_on_checkboxes.append(check_box)
            
            header_layout.addWidget(dp_icon)
            header_layout.addWidget(title)
            header_layout.addStretch()
            header_layout.addWidget(max_random_text_input)
            header_layout.addWidget(check_box)
            
            class_check_box_tracker["icon"][class_id] = dp_icon
            class_check_box_tracker["sub_cbs"][class_id] = {}
            class_check_box_tracker["main_cb"][class_id] = check_box
            class_check_box_tracker["max_random"][class_id] = max_random_text_input
            class_check_box_tracker["widget"][class_id], to_be_clicked = self.make_dp_widget(class_id, class_options, random_on, data, general_data, updated_data, class_check_box_tracker)
            
            widget_wrapper_layout.addWidget(header)
            widget_wrapper_layout.addWidget(class_check_box_tracker["widget"][class_id]) # type: ignore
            
            random_on_checkboxes.extend(to_be_clicked)
            
            widgets.append(main_widget)
        
        for cb in random_on_checkboxes:
            cb.click()
        
        return widgets
    
    def make_open_dp_func(self, class_id: str, class_check_box_tracker: dict[str, Any]):
        def open_dp():
            widget: QWidget = class_check_box_tracker["widget"][class_id]
            
            class_check_box_tracker["icon"][class_id].setAngle(0 if class_check_box_tracker["icon"][class_id].angle != 0 else 270)
            
            if widget.isVisible():
                widget.setVisible(False)
            else:
                widget.setVisible(True)
        
        return open_dp
    
    def make_random_text_changed_func(self, class_id, data):
        def func(number: int):
            data[class_id][0] = number if number != -1 else None
        
        return func
    
    def make_subject_widget(self, info, general_data, class_check_box_tracker):
        container_widget = QWidget()
        
        container_layout = QVBoxLayout()
        container_widget.setLayout(container_layout)
        
        for widget in self._create_checkbox_widgets(info, general_data, class_check_box_tracker):
            container_layout.addWidget(widget, alignment=Qt.AlignmentFlag.AlignTop)
        
        container_widget.setVisible(False)
        
        return container_widget
    
    def make_dp_widget(self, class_id: str, options: dict[str, bool], random_clicked: int | None, content, general_data, updated_data, class_check_box_tracker):
        dp_widget = QWidget()
        dp_widget.setProperty("class", "DPC_Body")
        
        dp_layout = QVBoxLayout()
        dp_layout.setSpacing(2)
        dp_widget.setLayout(dp_layout)
        
        clicked_cbs: list[QCheckBox] = []
        
        for optionID, optionState in options.items():
            option_widget = QWidget()
            option_layout = QHBoxLayout()
            
            option_widget.setLayout(option_layout)
            option_widget.setDisabled(isinstance(optionState, str))
            
            dp_title = QLabel(updated_data["id_mapping"]["sub"][class_id][optionID])
            
            dp_checkbox = QCheckBox()
            
            class_check_box_tracker["sub_cbs"][class_id][optionID] = dp_checkbox
            
            dp_checkbox.clicked.connect(self.make_sub_checkbox_func(class_id, content, general_data, optionID))
            
            if optionState and random_clicked is None:
                clicked_cbs.append(dp_checkbox)
            
            option_layout.addSpacing(50)
            option_layout.addWidget(dp_title)
            option_layout.addStretch()
            option_layout.addWidget(dp_checkbox)
            
            dp_layout.addWidget(option_widget)
        
        dp_widget.setVisible(False)
        
        return dp_widget, clicked_cbs
    
    def make_main_checkbox_func(self, class_id: str, content, class_check_box_tracker):
        def checkbox_func(is_on):
            if class_id not in content:
                content[class_id] = [None, {}]
            
            if is_on:
                for c_box in class_check_box_tracker["sub_cbs"][class_id].values():
                    if c_box.isChecked():
                        c_box.click()
                
                if class_check_box_tracker["icon"][class_id].angle != 270:
                    class_check_box_tracker["icon"][class_id].mouseclicked.emit()
                
                if class_check_box_tracker["max_random"][class_id].number() == -1:
                    class_check_box_tracker["max_random"][class_id].setNumber(self.default_max_classes)
            
            class_check_box_tracker["icon"][class_id].setDisabled(is_on)
            class_check_box_tracker["max_random"][class_id].setVisible(is_on)
            
            content[class_id][0] = class_check_box_tracker["max_random"][class_id].number() if is_on else None
        
        return checkbox_func
    
    def make_sub_checkbox_func(self, class_id: str, content, general_data, option_id: str):
        def checkbox_func(is_on):
            if is_on:
                if class_id not in content:
                    content[class_id] = [None, {}]
                
                content[class_id][1][option_id] = True
                general_data["content"][class_id][1][option_id] = self.teacher_id
            else:
                content[class_id][1].pop(option_id)
                general_data["content"][class_id][1][option_id] = False
            
            self.saved_state_changed.emit()
        
        return checkbox_func
    
    def make_open_subject_func(self, subject_dp_tracker: dict[str, Any]):
        def open_subject():
            widget: QWidget = subject_dp_tracker["widget"]
            
            subject_dp_tracker["icon"].setAngle(0 if subject_dp_tracker["icon"].angle != 0 else 270)
            
            if widget.isVisible():
                widget.setVisible(False)
            else:
                widget.setVisible(True)
        
        return open_subject
    
    def make_odp_func(self, content, class_id: str, class_check_box_tracker):
        open_dp_func = self.make_open_dp_func(class_id, class_check_box_tracker)
        
        def func():
            if class_id in content and content[class_id][0]:
                return
            
            open_dp_func()
        
        return func

class SubjectSelection(BaseSubWidget):
    def __init__(self, title: str, info: dict[str, tuple[str, dict[str, int | dict[str, str]]]], week_total: int, saved_state_changed: pyqtBoundSignal):
        super().__init__(title, info, saved_state_changed)
        
        self.setFixedSize(600, 400)
        
        self.week_total = week_total
        
        self.subject_widgets: dict[str, QWidget] = {}
        self.number_edits: dict[str, tuple[NumberLineEdit, NumberLineEdit]] = {}
        
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        
        self.container_layout.setSpacing(20)
        
        self.scroll_area.setWidget(self.container)
        
        self.main_layout.addWidget(self.scroll_area)
        
        for subject_id, (subject_name, subject_info) in self.info.items():
            self.add_subject(subject_id, subject_name, subject_info) # type: ignore
        
        self.container_layout.addStretch()
    
    def go_to(self, _id):
        for subject_id, widget in self.subject_widgets.items():
            if subject_id == _id:
                def func():
                    self.scroll_area.verticalScrollBar().setValue(widget.y())
                    widget.setFocus()
                
                QTimer.singleShot(200, func)
                
                break
    
    def add_subject(self, subject_id: str, subject_name: str, info: dict):
        selection_widget = QWidget()
        selection_widget.setProperty("class", "SubjectClassViewEntry")
        
        layout = QHBoxLayout()
        selection_widget.setLayout(layout)
        
        metrics = QFontMetrics(self.font())
        subjects_label = QLabel(metrics.elidedText(subject_name, Qt.TextElideMode.ElideRight, 100))
        subjects_label.setFont(self.font())
        subjects_label.setToolTip(subject_name)
        subjects_label.setProperty("class", "SubjectClassViewEntryName")
        
        sub_widget = QWidget()
        sub_widget.setProperty("class", "SubjectClassViewEntryEdits")
        
        sub_layout = QVBoxLayout()
        sub_widget.setLayout(sub_layout)
        
        layout.addWidget(subjects_label, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(sub_widget, alignment=Qt.AlignmentFlag.AlignRight)
        
        per_day_edit = NumberLineEdit(int(info["per_day"]), 1, int(info["per_week"]))
        # per_day_edit.edit.setFixedWidth(50)
        per_day_edit.setPlaceholderText("Per day")
        per_day_edit.textChanged.connect(self.make_per_day_text_changed_func(subject_id, per_day_edit))
        
        per_week_edit = NumberLineEdit(int(info["per_week"]), 1, self.week_total - sum([int(v["per_week"]) for _, v in self.info.values()]))
        # per_week_edit.edit.setFixedWidth(54)
        per_week_edit.setPlaceholderText("Per week")
        per_week_edit.textChanged.connect(self.make_per_week_text_changed_func(subject_id, per_day_edit, per_week_edit))
        
        per_day_widget = QWidget()
        per_day_layout = QHBoxLayout()
        per_day_widget.setProperty("class", "Edit")
        per_day_widget.setStyleSheet("QWidget.Edit{background: none} QLabel{background: none}")
        per_day_widget.setLayout(per_day_layout)
        
        per_day_layout.addWidget(QLabel("<b>Per day</b>"))
        per_day_layout.addWidget(per_day_edit)
        
        per_week_widget = QWidget()
        per_week_layout = QHBoxLayout()
        per_week_widget.setProperty("class", "Edit")
        per_week_widget.setStyleSheet("QWidget.Edit{background: none} QLabel{background: none}")
        per_week_widget.setLayout(per_week_layout)
        
        per_week_layout.addWidget(QLabel("<b>Per week</b>"))
        per_week_layout.addWidget(per_week_edit)
        
        sub_layout.addWidget(per_day_widget)
        sub_layout.addWidget(per_week_widget)
        
        self.container_layout.addWidget(selection_widget, alignment=Qt.AlignmentFlag.AlignTop)
        
        self.number_edits[subject_id] = per_day_edit, per_week_edit
        self.subject_widgets[subject_id] = selection_widget
    
    def make_per_day_text_changed_func(self, subject_id: str, input_edit: 'NumberLineEdit'):
        def text_changed_func():
            self.info[subject_id][1]["per_day"] = input_edit.number() # type: ignore
            
            self.saved_state_changed.emit()
        
        return text_changed_func
    
    def make_per_week_text_changed_func(self, subject_id: str, per_day_edit: 'NumberLineEdit', per_week_edit: 'NumberLineEdit'):
        def text_changed_func():
            self.info[subject_id][1]["per_week"] = per_week_edit.number() # type: ignore
            
            if int(self.info[subject_id][1]["per_week"]) < per_day_edit.max_num and int(self.info[subject_id][1]["per_week"]) < int(self.info[subject_id][1]["per_day"]):
                per_day_edit.setNumber(self.info[subject_id][1]["per_week"])
            
            per_day_edit.max_num = self.info[subject_id][1]["per_week"]
            self._update_max_per_week(per_week_edit.number() - self.info[subject_id][1]["per_week"])
            
            self.saved_state_changed.emit()
        
        return text_changed_func
    
    def _update_max_per_week(self, diff: int):
        total_per_week = sum(info_data["per_week"] for _, info_data in self.info.values()) + diff
        remainder_days = self.week_total - total_per_week
        
        for s_id in self.info:
            self.number_edits[s_id][1].max_num = self.info[s_id][1]["per_week"] + remainder_days
            
            if self.number_edits[s_id][1].max_num < self.info[s_id][1]["per_week"] and self.number_edits[s_id][1].number() > self.number_edits[s_id][1].max_num:
                self.number_edits[s_id][1].setNumber(self.number_edits[s_id][1].max_num)

class OptionsMaker(BaseSubWidget):
    def __init__(self, title: str, info: dict[str, str], saved_state_changed: pyqtBoundSignal):
        super().__init__(title, info, saved_state_changed)
        self.option_widgets: dict[str, OptionTag] = {}
        self.current_row = 0
        self.current_col = 0
        self.max_cols = 4  # Maximum number of columns before wrapping
        
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        
        del self.container, self.container_layout
        
        self.container = QWidget()
        self.container_layout = QGridLayout(self.container)  # Use QGridLayout
        self.container_layout.setSpacing(4)
        self.container_layout.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
        self.scroll_area.setWidget(self.container)
        
        self.add_button = QPushButton("Add Option")
        self.add_button.clicked.connect(lambda: self.add_option())
        
        self.main_layout.addWidget(self.scroll_area)
        self.main_layout.addWidget(self.add_button, alignment=Qt.AlignmentFlag.AlignRight)
        
        temp_option = OptionTag("IFE")
        self.setFixedSize((temp_option.width() + (temp_option.main_layout.spacing() * 4) + self.container_layout.spacing()) * self.max_cols, 300)
        
        del temp_option
        
        # Load existing options
        for option_id, option_name in self.info.items():
            self.add_option(option_id, option_name)
    
    def go_to(self, _id: str):
        for option_id, widget in self.option_widgets.items():
            if option_id == _id:
                def func():
                    self.scroll_area.verticalScrollBar().setValue(widget.y())
                    widget.setFocus()
                
                QTimer.singleShot(200, func)
                
                break
    
    def add_option(self, _id: str | None = None, text: str | None = None):
        option = OptionTag(text)
        
        _id = str(hex(id(option)).lower().replace("0x", "")) if _id is None else _id
        
        def update_option():
            self.info[_id] = option.get_text()
            self.saved_state_changed.emit()
        
        update_option()
        
        option.finished_editing_signal.connect(update_option)
        
        def remove_option():
            self.info.pop(_id)
            self.option_widgets.pop(_id)
            self.container_layout.removeWidget(option)
            option.deleteLater()
            self.reflow_items()  # Reflow remaining items
        
        option.deleted.connect(remove_option)
        self.option_widgets[_id] = option
        
        # Add to grid and wrap to next row if needed
        self.container_layout.addWidget(option, self.current_row, self.current_col)
        self.current_col += 1
        if self.current_col >= self.max_cols:
            self.current_col = 0
            self.current_row += 1
        
        if text is None:
            option.start_editing()
    
    def reflow_items(self):
        # Remove all widgets from grid
        for option in self.option_widgets.values():
            self.container_layout.removeWidget(option)
        
        # Re-add widgets in order
        self.current_row = 0
        self.current_col = 0
        for option in self.option_widgets.values():
            self.container_layout.addWidget(option, self.current_row, self.current_col)
            self.current_col += 1
            if self.current_col >= self.max_cols:
                self.current_col = 0
                self.current_row += 1
    
    def closeEvent(self, a0):
        for option in self.option_widgets.values():
            if option.is_editing:
                QMessageBox.critical(self, "Setting OM Error", "Please finish edting the option")
                a0.ignore() # type: ignore
                option.start_editing()
                return
        
        return super().closeEvent(a0)

