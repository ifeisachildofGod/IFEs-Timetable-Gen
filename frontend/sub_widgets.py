from frontend.imports import *

from frontend.base_widgets import *

class SelectionList(QDialog):
    def __init__(self, title: str, info: list, saved_state_changed: pyqtBoundSignal):
        super().__init__()
        self.setWindowTitle(title)
        self.setFixedSize(400, 300)
        
        self.saved_state_changed = saved_state_changed
        
        main_layout = QVBoxLayout(self)
        
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        
        self.container = QWidget()
        self.container_layout = QVBoxLayout()
        
        self.container.setLayout(self.container_layout)
        self.container.setProperty("class", "SelectionList")
        
        self.container_layout.setContentsMargins(10, 20, 20, 5)
        self.container_layout.setSpacing(30)
        
        self.scroll_area.setWidget(self.container)
        main_layout.addWidget(self.scroll_area)
        
        # Initialize widgets
        split_index = info.index(None)
        selected_items = info[:split_index]
        unselected_items = info[split_index+1:]
        
        # Add selected items
        for item_id, item_name in selected_items:
            widget = SelectedWidget(item_id, item_name, self.container_layout, self.saved_state_changed)
            self.container_layout.addWidget(widget)
        
        # Add unselected items
        for item_id, item_name in unselected_items:
            widget = UnselectedWidget(item_id, item_name, self.container_layout, self.saved_state_changed)
            self.container_layout.addWidget(widget)
        
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
    
    @staticmethod
    def fix_none_selection_content_problem(problem_content_list: list):
        fixed_content_list = problem_content_list.copy()
        fixed_content_list.insert(fixed_content_list.index(None), (None, None))
        fixed_content_list.remove(None)
        
        return fixed_content_list

class SubjectDropdownCheckBoxes(QDialog):
    def __init__(self, title: str, info: dict[str, dict[str, dict[str, dict[str, str | bool]]] | dict[int, str]], saved_state_changed: pyqtBoundSignal, general_data: dict):
        super().__init__()
        
        self.info = info
        self.general_data = general_data
        
        self.setWindowTitle(title)
        self.setFixedSize(400, 300)
        
        self.saved_state_changed = saved_state_changed
        
        self.main_guy_is_clicked = False
        self.mini_guy_is_clicked = False
        
        main_layout = QVBoxLayout(self)
        
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        
        container = QWidget()
        self.container_layout = QVBoxLayout(container)
        self.container_layout.setContentsMargins(0, 0, 0, 0)
        
        main_layout.addWidget(scroll_area)
        scroll_area.setWidget(container)
        
        self.setLayout(main_layout)
        
        self.class_check_box_tracker = {"main_cb": {}, "sub_cbs": {}, "icon": {}, "widget": {}}
        
        for widget in self._create_checkbox_widgets(self.info, self.general_data, self.class_check_box_tracker):
            self.container_layout.addWidget(widget, alignment=Qt.AlignmentFlag.AlignTop)
        
        self.container_layout.addStretch()
    
    def _create_checkbox_widgets(self, data: dict[str, dict[str, str | bool]], general_data, class_check_box_tracker: dict[str, dict[str, QCheckBox | QWidget | dict[str, QCheckBox]]]):
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
                def odp_func(event):
                    if event.button() == Qt.MouseButton.LeftButton:
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
            widget_wrapper_layout.addWidget(class_check_box_tracker["widget"][class_id])
            
            all_clicked_checkboxes.extend(to_be_clicked)
            
            widgets.append(main_widget)
        
        for cb in all_clicked_checkboxes:
            cb.click()
        
        return widgets
    
    def get(self):
        return self.info
    
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
            # print(optionState, all_clicked, dp_checkbox.isChecked())
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

class TeacherDropdownCheckBoxes(QDialog):
    def __init__(self, title, info, saved_state_changed, teacher_id, general_data, default_max_classes):
        super().__init__()
        
        self.info = info
        self.teacher_id = teacher_id
        self.general_data = general_data
        self.default_max_classes = default_max_classes
        self.saved_state_changed = saved_state_changed
        
        self.setWindowTitle(title)
        self.setFixedSize(400, 300)
        
        self.main_guy_is_clicked = False
        self.mini_guy_is_clicked = False
        
        main_layout = QVBoxLayout(self)
        
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        
        container = QWidget()
        self.container_layout = QVBoxLayout(container)
        self.container_layout.setContentsMargins(0, 0, 0, 0)
        
        main_layout.addWidget(scroll_area)
        scroll_area.setWidget(container)
        
        self.setLayout(main_layout)
        
        self.subject_check_box_tracker = {}
        self.class_check_box_tracker = {}
        
        for subject_id, info in self.info["content"].items():
            self.subject_check_box_tracker[subject_id] = {}
            self.class_check_box_tracker[subject_id] = {"main_cb": {}, "sub_cbs": {}, "icon": {}, "max_random": {}, "widget": {}}
            
            main_widget = QWidget()
            main_layout = QVBoxLayout()
            
            main_widget.setProperty("class", "Bordered")
            main_widget.setProperty("class", "DropdownCheckboxes")
            main_widget.setLayout(main_layout)
            
            open_dp_func = self.make_open_subject_func(self.subject_check_box_tracker[subject_id])
            
            def make_open_subject(odp_param_func):
                def odp_func(event):
                    if event.button() == Qt.MouseButton.LeftButton:
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
            
            main_layout.addWidget(header)
            main_layout.addWidget(self.subject_check_box_tracker[subject_id]["widget"])
            
            self.container_layout.addWidget(main_widget, alignment=Qt.AlignmentFlag.AlignTop)
        
        self.container_layout.addStretch()
    
    def _create_checkbox_widgets(self, data: dict[str, dict[str, dict[str, str | bool]]] | dict[int, str], general_data, class_check_box_tracker: dict[str, dict[str, QCheckBox | QWidget | dict[str, QCheckBox]]]):
        updated_data = deepcopy(general_data)
        
        for class_id, (random_on, options_info) in data.items():
            updated_data["content"][class_id][0] = random_on
            for opt_id, opt_state in options_info.items():
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
                def odp_func(event):
                    if event.button() == Qt.MouseButton.LeftButton:
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
            
            max_random_text_input = NumberTextEdit(min_validatorAmt=1, max_validatorAmt=len(class_options))
            max_random_text_input.edit.setToolTip("Max Classes")
            max_random_text_input.edit.setText(str(random_on) if random_on is not None else "")
            max_random_text_input.setVisible(False)
            max_random_text_input.edit.textChanged.connect(self.make_random_text_changed_func(class_id, data))
            
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
            widget_wrapper_layout.addWidget(class_check_box_tracker["widget"][class_id])
            
            random_on_checkboxes.extend(to_be_clicked)
            
            widgets.append(main_widget)
        
        for cb in random_on_checkboxes:
            cb.click()
        
        return widgets
    
    def get(self):
        return self.info
    
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
        def func(text):
            data[class_id][0] = int(text) if text else None
        
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
                
                if not class_check_box_tracker["max_random"][class_id].edit.text():
                    class_check_box_tracker["max_random"][class_id].edit.setText(str(self.default_max_classes))
            
            class_check_box_tracker["icon"][class_id].setDisabled(is_on)
            class_check_box_tracker["max_random"][class_id].setVisible(is_on)
            
            content[class_id][0] = int(class_check_box_tracker["max_random"][class_id].edit.text()) if is_on else None
        
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
            widget = subject_dp_tracker["widget"]
            
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

class SubjectSelection(QDialog):
    def __init__(self, title: str, info: dict[str, dict[str, str | dict[str, list[str | None], dict[int, str]]] | dict[int, str] | dict[str, list[str | None]]], saved_state_changed: pyqtBoundSignal):
        super().__init__()
        
        self.setWindowTitle(title)
        self.setFixedSize(600, 400)
        
        self.saved_state_changed = saved_state_changed
        
        self.info = info
        
        self.main_layout = QVBoxLayout(self)
        
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        
        self.container = QWidget()
        
        self.container_layout = QVBoxLayout(self.container)
        self.container_layout.setSpacing(20)
        
        self.scroll_area.setWidget(self.container)
        
        self.main_layout.addWidget(self.scroll_area)
        
        for subject_id, (subject_name, subject_info) in self.info.items():
            self.add_subject(subject_id, subject_name, subject_info)
        
        self.container_layout.addStretch()
    
    def get(self):
        return self.info
    
    def add_subject(self, subject_id: str, subject_name: str, info: dict):
        selection_widget = QWidget()
        selection_widget.setProperty("class", "SubjectClassViewEntry")
        
        layout = QHBoxLayout()
        selection_widget.setLayout(layout)
        
        subjects_label = QLabel(subject_name)
        subjects_label.setProperty("class", "SubjectClassViewEntryName")
        
        sub_widget = QWidget()
        sub_widget.setProperty("class", "SubjectClassViewEntryEdits")
        
        sub_layout = QVBoxLayout()
        sub_widget.setLayout(sub_layout)
        
        layout.addWidget(subjects_label, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(sub_widget, alignment=Qt.AlignmentFlag.AlignCenter)
        
        per_day_edit = NumberTextEdit()
        per_day_edit.edit.setFixedWidth(50)
        per_day_edit.edit.setPlaceholderText("Per day")
        per_day_edit.edit.setText(info["per_day"])
        per_day_edit.edit.textChanged.connect(self.make_text_changed_func(subject_id, "per_day", per_day_edit))
        
        per_week_edit = NumberTextEdit()
        per_week_edit.edit.setFixedWidth(54)
        per_week_edit.edit.setPlaceholderText("Per week")
        per_week_edit.edit.setText(info["per_week"])
        per_week_edit.edit.textChanged.connect(self.make_text_changed_func(subject_id, "per_week", per_week_edit))
        
        sub_layout.addWidget(per_day_edit)
        sub_layout.addWidget(per_week_edit)
        
        self.container_layout.addWidget(selection_widget, alignment=Qt.AlignmentFlag.AlignTop)
    
    def make_text_changed_func(self, subject_id: str, key: str, input_edit: 'NumberTextEdit'):
        def text_changed_func():
            self.info[subject_id][1][key] = input_edit.edit.text()
            
            self.saved_state_changed.emit()
        
        return text_changed_func

class OptionsMaker(QDialog):
    def __init__(self, title: str, info: dict[str, str], saved_state_changed: pyqtBoundSignal):
        super().__init__()
        self.title = title
        self.info = info
        self.saved_state_changed = saved_state_changed
        
        self.setWindowTitle(self.title)
        
        self.options: list[OptionTag] = []
        self.current_row = 0
        self.current_col = 0
        self.max_cols = 4  # Maximum number of columns before wrapping
        
        self.main_layout = QVBoxLayout(self)
        
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        
        self.container = QWidget()
        self.grid_layout = QGridLayout(self.container)  # Use QGridLayout
        self.grid_layout.setSpacing(4)
        self.grid_layout.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
        self.scroll_area.setWidget(self.container)
        
        self.add_button = QPushButton("Add Option")
        self.add_button.clicked.connect(lambda: self.add_option())
        
        self.main_layout.addWidget(self.scroll_area)
        self.main_layout.addWidget(self.add_button, alignment=Qt.AlignmentFlag.AlignRight)
        
        temp_option = OptionTag("IFE")
        self.setFixedSize((temp_option.width() + (temp_option.main_layout.spacing() * 4) + self.grid_layout.spacing()) * self.max_cols, 300)
        
        del temp_option
        
        # Load existing options
        for option_id, option_name in self.info.items():
            self.add_option(option_id, option_name)
    
    def get(self):
        return self.info
    
    def add_option(self, _id: str | None = None, text: str | None = None):
        option = OptionTag(text)
        
        _id = str(hex(id(option)).upper()) if _id is None else _id
        
        def update_option():
            self.info[_id] = option.get_text()
            self.saved_state_changed.emit()
        
        update_option()
        
        option.finished_editing_signal.connect(update_option)
        
        def remove_option():
            self.options.remove(option)
            self.info.pop(_id)
            self.grid_layout.removeWidget(option)
            option.deleteLater()
            self.reflow_items()  # Reflow remaining items
        
        option.deleted.connect(remove_option)
        self.options.append(option)
        
        # Add to grid and wrap to next row if needed
        self.grid_layout.addWidget(option, self.current_row, self.current_col)
        self.current_col += 1
        if self.current_col >= self.max_cols:
            self.current_col = 0
            self.current_row += 1
        
        if text is None:
            option.start_editing()
    
    def closeEvent(self, a0):
        for option in self.options:
            if option.is_editing:
                QMessageBox.critical(self, "Setting OM Error", "Please finish edting the option")
                a0.ignore()
                option.start_editing()
                return
        
        return super().closeEvent(a0)
    
    def reflow_items(self):
        # Remove all widgets from grid
        for option in self.options:
            self.grid_layout.removeWidget(option)
        
        # Re-add widgets in order
        self.current_row = 0
        self.current_col = 0
        for option in self.options:
            self.grid_layout.addWidget(option, self.current_row, self.current_col)
            self.current_col += 1
            if self.current_col >= self.max_cols:
                self.current_col = 0
                self.current_row += 1

class OptionSelector(QDialog):
    closed = pyqtSignal()
    
    def __init__(self, title: str, info: dict[str, list[str | None] | dict[int, str]], saved_state_changed: pyqtBoundSignal):
        super().__init__()
        
        self.setFixedHeight(400)
        
        self.title = title
        self.info = info
        self.saved_state_changed = saved_state_changed
        
        self.setWindowTitle(self.title)
        
        self.content = self.info["content"]
        self.id_mapping = self.info["id_mapping"]
        
        self.main_options_rows_layout_list: list[QHBoxLayout] = []
        self.sub_options_rows_layout_list: list[QHBoxLayout] = []
        
        self.main_options_tracker: list[list[OptionTag]] = []
        self.sub_options_tracker: list[list[QLabel]] = []
        
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        self.container = QWidget()
        self.main_layout = QVBoxLayout()
        self.main_layout.setSpacing(10)
        
        self.container.setContentsMargins(10, 10, 10, 10)
        self.container.setLayout(self.main_layout)
        
        
        self.main_max_cols = 4
        
        main_options_widget = QWidget()
        self.main_options_layout = QVBoxLayout(main_options_widget)
        
        # main_options_scroll_area = QScrollArea()
        # main_options_scroll_area.setProperty("class", "MainOptionSelector")
        # main_options_scroll_area.setWidget(main_options_widget)
        
        main_options_widget.setProperty("class", "MainOptionSelector")
        main_options_widget.setLayout(self.main_options_layout)
        
        for index, option_name in enumerate(self.content[:self.content.index(None)].copy()):
            self._add_new_option(option_name, index)
        
        
        self.sub_max_cols = 6
        
        sub_options_widget = QWidget()
        self.sub_options_layout = QVBoxLayout(sub_options_widget)
        
        # sub_options_scroll_area = QScrollArea()
        # sub_options_scroll_area.setProperty("class", "SubOptionSelector")
        # sub_options_scroll_area.setWidget(sub_options_widget)
        
        sub_options_widget.setProperty("class", "SubOptionSelector")
        sub_options_widget.setLayout(self.sub_options_layout)
        
        for index, option_name in enumerate(self.content[self.content.index(None) + 1:].copy()):
            self._remove_new_option(option_name, index)
        
        self.main_layout.setSpacing(20)
        
        self.main_layout.addWidget(QLabel("Selected"))
        self.main_layout.addWidget(main_options_widget, 8)
        self.main_layout.addWidget(QLabel("Unselected"))
        self.main_layout.addWidget(sub_options_widget, 2)
        # self.main_layout.addWidget(main_options_scroll_area, 7)
        # self.main_layout.addWidget(sub_options_scroll_area, 3)
        
        
        layout.addWidget(self.container)
        
        temp_option = OptionTag("Ife")
        self.setFixedWidth((temp_option.width() + (temp_option.main_layout.spacing() * 4) + self.main_options_layout.spacing()) * self.sub_max_cols)
    
    def _make_add_option_func_in_remove_opt(self, name: str, option: QLabel):
        def add_option(_):
            opt_index = None
            
            for row_index, option_row in enumerate(self.sub_options_tracker):
                if option in option_row:
                    opt_index = option_row.index(option) + self.sub_max_cols*row_index
                    break
            else:
                raise ValueError(f"{option} is not in the sub options tracker")
            
            row = opt_index // self.sub_max_cols
            col = opt_index % self.sub_max_cols
            
            self.sub_options_rows_layout_list[row].removeWidget(self.sub_options_tracker[row][col])
            old_option = self.sub_options_tracker[row].pop(col)
            old_option.deleteLater()
            
            self._add_new_option(name, opt_index)
            
            none_index = self.content.index(None)
            
            content_sub_opt_index = opt_index + none_index + 1
            
            id_mapping_copy = self.id_mapping.copy()
            for i in id_mapping_copy:
                if none_index < i < content_sub_opt_index:
                    self.id_mapping[i + 1] = id_mapping_copy[i]
            
            self.id_mapping[none_index] = self.id_mapping.pop(none_index + 1)
            
            self.content.insert(none_index, self.content.pop(content_sub_opt_index))
        
        return add_option
    
    def _make_remove_option_func_in_add_opt(self, name: str, option: OptionTag):
        def remove_option():
            opt_index = None
            
            for row_index, option_row in enumerate(self.main_options_tracker):
                if option in option_row:
                    opt_index = option_row.index(option) + self.main_max_cols*row_index
                    break
            else:
                raise ValueError(f"{option} is not in the main options tracker")
            
            row = opt_index // self.main_max_cols
            col = opt_index % self.main_max_cols
            
            self.main_options_rows_layout_list[row].removeWidget(self.main_options_tracker[row][col])
            old_option = self.main_options_tracker[row].pop(col)
            old_option.deleteLater()
            
            self._remove_new_option(name, opt_index)
            
            id_mapping_copy = self.id_mapping.copy()
            for i in id_mapping_copy:
                if i > opt_index:
                    self.id_mapping[i - 1] = id_mapping_copy[i]
            
            self.id_mapping[len(self.content) - 1] = self.id_mapping.pop(opt_index)
            
            self.content.append(self.content.pop(opt_index))
        
        return remove_option
    
    def _add_new_option(self, name: str, index: int):
        option = OptionTag(name)
        
        option.deleted.disconnect()
        option.deleted.connect(self._make_remove_option_func_in_add_opt(name, option))
        option.started_editing_signal.disconnect()
        
        row = index // self.main_max_cols
        col = index % self.main_max_cols
        
        if row + 1 >= len(self.main_options_tracker):
            row_widget = QWidget()
            row_layout = QHBoxLayout()
            
            row_widget.setProperty("class", "OptionSelectorRow")
            row_widget.setLayout(row_layout)
            
            self.main_options_layout.addWidget(row_widget)
            
            self.main_options_rows_layout_list.append(row_layout)
            self.main_options_tracker.append([])
        
        if col < len(self.main_options_tracker[row]):
            self.main_options_rows_layout_list[row].insertWidget(col, option)
            self.main_options_tracker[row].insert(col, option)
        else:
            self.main_options_rows_layout_list[row].addWidget(option)
            self.main_options_tracker[row].append(option)
    
    def _remove_new_option(self, name: str, index: int):
        option = QLabel(name)
        
        option.setFixedWidth(150)
        option.setAlignment(Qt.AlignmentFlag.AlignCenter)
        option.setProperty("class", "OptionSelectorNotSelected")
        option.mousePressEvent = self._make_add_option_func_in_remove_opt(name, option)
        
        row = index // self.sub_max_cols
        col = index % self.sub_max_cols
        
        if row + 1 >= len(self.sub_options_rows_layout_list):
            row_widget = QWidget()
            row_layout = QHBoxLayout()
            
            row_widget.setProperty("class", "OptionSelectorRow")
            row_widget.setLayout(row_layout)
            
            self.sub_options_layout.addWidget(row_widget)
            
            self.sub_options_rows_layout_list.append(row_layout)
            self.sub_options_tracker.append([])
        
        if col < len(self.sub_options_tracker[row]):
            self.sub_options_rows_layout_list[row].insertWidget(col, option)
            self.sub_options_tracker[row].insert(col, option)
        else:
            self.sub_options_rows_layout_list[row].addWidget(option)
            self.sub_options_tracker[row].append(option)
    
    def get(self):
        return self.info
    
    def get_selected(self):
        return self.info["content"][:self.info["content"].index(None)]
    
    def close(self):
        self.closed.emit()
        return super().close()

