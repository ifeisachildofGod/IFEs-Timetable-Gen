from copy import deepcopy
from typing import Any, Callable
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel,
    QScrollArea, QPushButton, QHBoxLayout,
    QFrame, QDialog, QCheckBox,
    QComboBox, QGridLayout
)
from PyQt6.QtCore import Qt, pyqtBoundSignal
from frontend.theme import *
from frontend.theme import (
    _main_bg_color_1, _widgets_bg_color_2, _widget_border_radius_1,
    _general_scrollbar_theme, _widgets_bg_color_5, _widget_text_color_2
)
from frontend.base_widgets import SelectedWidget, UnselectedWidget, CustomLabel, OptionTag, NumberTextEdit


class SelectionList(QDialog):
    def __init__(self, title: str, info: dict, saved_state_changed: pyqtBoundSignal):
        super().__init__()
        
        self.setStyleSheet(THEME[SELECTION_LIST])
        
        self.setWindowTitle(title)
        self.setFixedSize(400, 300)
        
        self.saved_state_changed = saved_state_changed
        
        self.middle_line_thickness = 4
        self.normal_line_thickness = 1
        
        self.selected_widgets = []
        self.unselected_widgets = []
        self.separators = []
        
        self.content = info["content"]
        self.id_mapping = deepcopy(info["id_mapping"])
        
        main_layout = QVBoxLayout(self)
        
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setObjectName("selectionlistscrollarea")
        
        self.container = QWidget()
        self.container_layout = QVBoxLayout()
        self.container_layout.setContentsMargins(0, 0, 0, 0)
        self.container.setLayout(self.container_layout)
        self.container.setStyleSheet("background-color: " + _widgets_bg_color_2 + ";")
        
        self.scroll_area.setWidget(self.container)
        main_layout.addWidget(self.scroll_area)
        
        # Initialize widgets
        split_index = self.content.index(None)
        selected_items = self.content[:split_index]
        unselected_items = self.content[split_index+1:]
        
        # Add selected items
        for index, item in enumerate(selected_items):
            widget = SelectedWidget(item, self, self.id_mapping, self.id_mapping[index], self.saved_state_changed)
            self.add_item(widget)
            self.selected_widgets.append(widget)
            if item != selected_items[-1]:
                self.add_separator(self.normal_line_thickness, isSelected=True)
        
        # Add middle separator if there are unselected items
        if selected_items and unselected_items:
            self.add_separator(self.middle_line_thickness)
        
        # Add unselected items
        for index, item in enumerate(unselected_items):
            widget = UnselectedWidget(item, self, self.id_mapping, self.id_mapping[index + len(selected_items) + 1], self.saved_state_changed)
            self.add_item(widget)
            self.unselected_widgets.append(widget)
            if item != unselected_items[-1]:
                self.add_separator(self.normal_line_thickness, isSelected=False)
    
    def get(self):
        content = []
        
        for widget in self.selected_widgets:
            if isinstance(widget, SelectedWidget):
                content.append(widget.label.text())
        
        content.append(None)
        
        for widget in self.unselected_widgets:
            if isinstance(widget, UnselectedWidget):
                content.append(widget.label.text())
        
        info = {"content": content, "id_mapping": self.id_mapping}
        
        return info
    
    def add_item(self, custom_widget, index: int = None):
        if index is not None:
            self.container_layout.insertWidget(index, custom_widget)
        else:
            self.container_layout.addWidget(custom_widget)
    
    def add_separator(self, thickness=1, index: int = None, isSelected: bool = None):
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        separator.setStyleSheet(f"background-color: {_main_bg_color_1}; height: {thickness}px;")
        separator.setFixedHeight(thickness)
        
        if index is None:
            self.container_layout.addWidget(separator)
        else:
            self.container_layout.insertWidget(index, separator)
        
        self.separators.append(separator)
        if isSelected is not None:
            if isSelected:
                self.selected_widgets.append(separator)
            else:
                self.unselected_widgets.append(separator)

    def clear_separators(self):
        for separator in self.separators:
            self.container_layout.removeWidget(separator)
            separator.deleteLater()
        self.separators.clear()

    def update_separators(self):
        self.clear_separators()
        
        # Get all widgets and their positions
        selected_positions = []
        unselected_positions = []
        
        for i in range(self.container_layout.count()):
            item = self.container_layout.itemAt(i)
            if isinstance(item.widget(), SelectedWidget):
                selected_positions.append(i)
            elif isinstance(item.widget(), UnselectedWidget):
                unselected_positions.append(i)
        
        # Add separators between selected items
        for i in range(len(selected_positions) - 1):
            self.add_separator(
                thickness=self.normal_line_thickness,
                index=selected_positions[i] + 1,
                isSelected=True
            )
            # Update positions after inserting separator
            selected_positions = [p + 1 if p > selected_positions[i] else p 
                               for p in selected_positions]
            unselected_positions = [p + 1 for p in unselected_positions]
        
        # Add middle separator if we have both types
        if selected_positions and unselected_positions:
            self.add_separator(
                thickness=self.middle_line_thickness,
                index=selected_positions[-1] + 1
            )
            unselected_positions = [p + 1 for p in unselected_positions]
        
        # Add separators between unselected items
        for i in range(len(unselected_positions) - 1):
            self.add_separator(
                thickness=self.normal_line_thickness,
                index=unselected_positions[i] + 1,
                isSelected=False
            )
            unselected_positions = [p + 1 if p > unselected_positions[i] else p 
                                  for p in unselected_positions]

class SubjectDropDownCheckBoxes(QDialog):
    def __init__(self, title: str, info: dict[str, dict[str, dict[str, dict[str, str | bool]]] | dict[int, str]], saved_state_changed: pyqtBoundSignal, general_data: dict):
        super().__init__()
        
        self.info = info
        self.general_data = general_data
        
        self.setStyleSheet(THEME[DROPDOWN_CHECK_BOXES_THEME])
        
        self.setWindowTitle(title)
        self.setFixedSize(400, 300)
        
        self.saved_state_changed = saved_state_changed
        
        self.main_guy_is_clicked = False
        self.mini_guy_is_clicked = False
        
        main_layout = QVBoxLayout(self)
        
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        
        container = QWidget()
        container.setStyleSheet(f"background-color: {_main_bg_color_1};")
        self.container_layout = QVBoxLayout(container)
        self.container_layout.setContentsMargins(0, 0, 0, 0)
        
        main_layout.addWidget(scroll_area)
        scroll_area.setWidget(container)
        
        self.setLayout(main_layout)
        
        self.init()
        
        self.container_layout.addStretch()
    
    def init(self):
        self.class_check_box_tracker = {"main_cb": {}, "sub_cbs": {}, "icon": {}, "widget": {}}
        
        for widget in self._create_checkbox_widgets(self.info, self.general_data, self.class_check_box_tracker):
            self.container_layout.addWidget(widget, alignment=Qt.AlignmentFlag.AlignTop)
    
    def _create_checkbox_widgets(self, data: dict[str, dict[str, str | bool]], general_data, class_check_box_tracker: dict[str, dict[str, QCheckBox | QWidget | dict[str, QCheckBox]]]):
        updated_data = deepcopy(general_data)
        for class_id, options_info in data.items():
            updated_data["content"][class_id].update(options_info)
        
        id_mapping = updated_data["id_mapping"]
        
        widgets: list[QWidget] = []
        all_clicked_checkboxes: list[QCheckBox] = []
        
        for class_id, class_options in updated_data["content"].items():
            main_widget = QWidget()
            
            widget_wrapper_layout = QVBoxLayout()
            widget_wrapper_layout.setSpacing(0)
            main_widget.setLayout(widget_wrapper_layout)
            
            open_dp_func = self.make_open_dp_func(class_id, widget_wrapper_layout, class_check_box_tracker)
            
            def make_open_dp_func(odp_param_func):
                def odp_func(event):
                    if event.button() == Qt.MouseButton.LeftButton:
                        odp_param_func()
                
                return odp_func
            
            header = QWidget()
            header.setObjectName("dropdownHeader")
            header.setFixedHeight(50)
            header.mousePressEvent = make_open_dp_func(open_dp_func)
            
            widget_wrapper_layout.addWidget(header)
            
            header_layout = QHBoxLayout(header)
            header_layout.setContentsMargins(12, 0, 12, 0)
            
            dp_icon = CustomLabel("▼", 270)
            dp_icon.setObjectName("arrow")
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
            
            all_clicked_checkboxes.extend(to_be_clicked)
            
            widgets.append(main_widget)
        
        for cb in all_clicked_checkboxes:
            cb.click()
        
        return widgets
    
    def get(self):
        return self.info
    
    def make_open_dp_func(self, class_id: str, parent_layout: QVBoxLayout, class_check_box_tracker: dict[str, Any]):
        def open_dp():
            widget = class_check_box_tracker["widget"][class_id]
            
            class_check_box_tracker["icon"][class_id].setAngle(0 if class_check_box_tracker["icon"][class_id].angle != 0 else 270)
            
            if parent_layout.itemAt(1) is None:
                parent_layout.addWidget(widget)
            else:
                parent_layout.removeWidget(widget)
        
        return open_dp
    
    def make_dp_widget(self, class_id: str, options: dict[str, bool], all_clicked: bool, info, updated_data, class_check_box_tracker: dict[str, Any]):
        dp_widget = QWidget()
        dp_widget.setObjectName("dropdownContent")
        
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
        
        return dp_widget, clicked_cbs
    
    def make_main_checkbox_func(self, class_id: str, class_check_box_tracker: dict[str, Any]):
        def checkbox_func(is_on):
            if not self.mini_guy_is_clicked:
                self.main_guy_is_clicked = True
                
                if is_on:
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

class TeacherDropDownCheckBoxes(SubjectDropDownCheckBoxes):
    def __init__(self, title, info: dict[str, dict[str, dict[str, tuple[bool, dict[str, str | bool]]]]] | dict[int, str], saved_state_changed, general_data):
        super().__init__(title, info, saved_state_changed, general_data)
    
    def init(self):
        self.subject_check_box_tracker = {}
        self.class_check_box_tracker = {}
        
        for subject_id, info in self.info["content"].items():
            self.subject_check_box_tracker[subject_id] = {}
            self.class_check_box_tracker[subject_id] = {"main_cb": {}, "sub_cbs": {}, "icon": {}, "widget": {}}
            
            main_widget = QWidget()
            main_layout = QVBoxLayout()
            main_widget.setLayout(main_layout)
            
            open_dp_func = self.make_open_subject_func(main_layout, info, self.general_data[subject_id], self.subject_check_box_tracker[subject_id], self.class_check_box_tracker[subject_id])
            
            def make_open_dp_func(odp_param_func):
                def odp_func(event):
                    if event.button() == Qt.MouseButton.LeftButton:
                        odp_param_func()
                
                return odp_func
            
            header = QWidget()
            header.setObjectName("dropdownHeader")
            header.setFixedHeight(50)
            header.mousePressEvent = make_open_dp_func(open_dp_func)
            
            header_layout = QHBoxLayout(header)
            header_layout.setContentsMargins(12, 0, 12, 0)
            
            dp_icon = CustomLabel("▼", 270)
            dp_icon.setObjectName("arrow")
            dp_icon.mouseclicked.connect(open_dp_func)
            dp_icon.setContentsMargins(0, 0, 10, 0)
            
            title = QLabel(self.info["id_mapping"][subject_id])

            header_layout.addWidget(dp_icon)
            header_layout.addWidget(title)
            header_layout.addStretch()
            
            main_layout.addWidget(header)
            
            self.subject_check_box_tracker[subject_id]["icon"] = dp_icon
            self.subject_check_box_tracker[subject_id]["widget"] = self.make_subject_widget(info, self.general_data[subject_id], self.class_check_box_tracker[subject_id])
            
            self.container_layout.addWidget(main_widget, alignment=Qt.AlignmentFlag.AlignTop)
    
    def make_subject_widget(self, info, general_data, class_check_box_tracker):
        container_widget = QWidget()
        container_layout = QVBoxLayout()
        container_widget.setLayout(container_layout)
        
        for widget in self._create_checkbox_widgets(info, general_data, class_check_box_tracker):
            container_layout.addWidget(widget, alignment=Qt.AlignmentFlag.AlignTop)
        
        return container_widget
    
    def _create_checkbox_widgets(self, data: dict[str, dict[str, dict[str, str | bool]]] | dict[int, str], general_data, class_check_box_tracker: dict[str, dict[str, QCheckBox | QWidget | dict[str, QCheckBox]]]):
        updated_data = deepcopy(general_data)
        for class_id, (random_on, options_info) in data.items():
            updated_data["content"][class_id][0] = random_on
            updated_data["content"][class_id][1].update(options_info)
        
        id_mapping = updated_data["id_mapping"]
        
        widgets: list[QWidget] = []
        random_on_checkboxes: list[QCheckBox] = []
        
        for class_id, (random_on, class_options) in updated_data["content"].items():
            main_widget = QWidget()
            
            widget_wrapper_layout = QVBoxLayout()
            widget_wrapper_layout.setSpacing(0)
            main_widget.setLayout(widget_wrapper_layout)
            
            open_dp_func = self.make_odp_func(data, class_id, widget_wrapper_layout, class_check_box_tracker)
            
            def make_open_dp_func(odp_param_func):
                def odp_func(event):
                    if event.button() == Qt.MouseButton.LeftButton:
                        odp_param_func()
                
                return odp_func
            
            header = QWidget()
            header.setObjectName("dropdownHeader")
            header.setFixedHeight(50)
            header.mousePressEvent = make_open_dp_func(open_dp_func)
            
            widget_wrapper_layout.addWidget(header)
            
            header_layout = QHBoxLayout(header)
            header_layout.setContentsMargins(12, 0, 12, 0)
            
            dp_icon = CustomLabel("▼", 270)
            dp_icon.setObjectName("arrow")
            dp_icon.mouseclicked.connect(open_dp_func)
            dp_icon.setContentsMargins(0, 0, 10, 0)
            
            title = QLabel(id_mapping["main"][class_id])
            
            check_box = QCheckBox("Random")
            check_box.clicked.connect(self.make_main_checkbox_func(class_id, data, class_check_box_tracker))
            
            if random_on:
                random_on_checkboxes.append(check_box)
            
            header_layout.addWidget(dp_icon)
            header_layout.addWidget(title)
            header_layout.addStretch()
            header_layout.addWidget(check_box)
            
            class_check_box_tracker["icon"][class_id] = dp_icon
            class_check_box_tracker["sub_cbs"][class_id] = {}
            class_check_box_tracker["main_cb"][class_id] = check_box
            class_check_box_tracker["widget"][class_id], to_be_clicked = self.make_dp_widget(class_id, class_options, random_on, data, updated_data, class_check_box_tracker)
            
            random_on_checkboxes.extend(to_be_clicked)
            
            widgets.append(main_widget)
        
        for cb in random_on_checkboxes:
            cb.click()
        
        return widgets
    
    def get(self):
        return self.info
    
    def make_dp_widget(self, class_id: str, options: dict[str, bool], random_clicked: bool, content, updated_data, class_check_box_tracker):
        dp_widget = QWidget()
        dp_widget.setObjectName("dropdownContent")
        
        dp_layout = QVBoxLayout()
        dp_layout.setSpacing(2)
        dp_widget.setLayout(dp_layout)
        
        clicked_cbs: list[QCheckBox] = []
        
        for optionID, optionState in options.items():
            option_layout = QHBoxLayout()
            
            dp_title = QLabel(updated_data["id_mapping"]["sub"][class_id][optionID])
            
            dp_checkbox = QCheckBox()
            dp_checkbox.setDisabled(random_clicked)
            
            class_check_box_tracker["sub_cbs"][class_id][optionID] = dp_checkbox
            
            dp_checkbox.clicked.connect(self.make_sub_checkbox_func(class_id, content, optionID))
            
            if optionState and not random_clicked:
                clicked_cbs.append(dp_checkbox)
            
            option_layout.addSpacing(50)
            option_layout.addWidget(dp_title)
            option_layout.addStretch()
            option_layout.addWidget(dp_checkbox)
            
            dp_layout.addLayout(option_layout)
        
        return dp_widget, clicked_cbs
    
    def make_main_checkbox_func(self, class_id: str, content, class_check_box_tracker):
        def checkbox_func(is_on):
            if class_id not in content:
                content[class_id] = [False, {}]
            
            if is_on:
                for c_box in class_check_box_tracker["sub_cbs"][class_id].values():
                    if c_box.isChecked():
                        c_box.click()
                    # c_box.setDisabled(True)
                if class_check_box_tracker["icon"][class_id].angle != 270:
                    class_check_box_tracker["icon"][class_id].mouseclicked.emit()
                class_check_box_tracker["icon"][class_id].setDisabled(True)
            else:
                for c_box in class_check_box_tracker["sub_cbs"][class_id].values():
                    c_box.setDisabled(False)
            
            content[class_id][0] = is_on
        
        return checkbox_func
    
    def make_sub_checkbox_func(self, class_id: str, content, option_id: str):
        def checkbox_func(is_on):
            if is_on:
                if class_id not in content:
                    content[class_id] = [False, {}]
                
                content[class_id][1][option_id] = True
            else:
                content[class_id][1].pop(option_id)
            
            self.saved_state_changed.emit()
        
        return checkbox_func
    
    def make_open_subject_func(self, parent_layout: QVBoxLayout, info, general_data, subject_dp_tracker: dict[str, Any], class_check_box_tracker):
        def open_subject():
            widget = subject_dp_tracker["widget"]
            
            subject_dp_tracker["icon"].setAngle(0 if subject_dp_tracker["icon"].angle != 0 else 270)
            
            if parent_layout.itemAt(1) is None:
                parent_layout.addWidget(widget)
            else:
                parent_layout.removeWidget(widget)
                widget.deleteLater()
                
                subject_dp_tracker["widget"] = self.make_subject_widget(info, general_data, class_check_box_tracker)
        
        return open_subject
    
    
    def make_odp_func(self, content, class_id: str, widget_wrapper_layout, class_check_box_tracker):
        open_dp_func = self.make_open_dp_func(class_id, widget_wrapper_layout, class_check_box_tracker)
        
        def func():
            if class_id in content and content[class_id][0]:
                return
            
            open_dp_func()
        
        return func

class SubjectSelection(QDialog):
    def __init__(self, title: str, info: dict[str, dict[str, str | dict[str, list[str | None], dict[int, str]]] | dict[int, str] | dict[str, list[str | None]]], saved_state_changed: pyqtBoundSignal, default_per_day: int, default_per_week: int):
        super().__init__()
        
        self.setStyleSheet(THEME[SUBJECT_SELECTION])
        
        self.setWindowTitle(title)
        self.setFixedSize(600, 400)
        
        self.saved_state_changed = saved_state_changed
        
        self.default_per_day = default_per_day
        self.default_per_week = default_per_week
        
        self.content = info["content"]
        self.id_mapping = info["id_mapping"]
        self.available_subject_teachers = info["available_subject_teachers"]
        
        self.subjects = [subject_info["name"] for _, subject_info in self.available_subject_teachers.items()]
        
        self.dp_tracker: dict[str, QComboBox] = {}
        self.del_widg_func_tracker: dict[str, Callable[[str], None]] = {}
        
        self.subject_amount = 0
        
        self.main_layout = QVBoxLayout(self)
        
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        
        self.container = QWidget()
        self.container.setObjectName("subjectscontainer")
        self.container.setStyleSheet("#subjectscontainer{background-color: " + _widgets_bg_color_2 + "}")
        
        self.container_layout = QVBoxLayout(self.container)
        self.scroll_area.setWidget(self.container)
        
        self.container_layout.addStretch()
        
        self.add_button = QPushButton("Add Subject")
        
        self.add_button.clicked.connect(self._add_new_subject)
        
        self.main_layout.addWidget(self.scroll_area)
        self.main_layout.addWidget(self.add_button, alignment=Qt.AlignmentFlag.AlignRight)
        
        if not self.subjects:
            self.add_button.setDisabled(True)
        
        self.info = {}
        
        for subject_id, subject_info in self.content.items():
            self.add_subject(subject_id, subject_info)
    
    def _add_new_subject(self):
        subject_id = next(
            index_id
            for index, (index_id, _) in enumerate(self.available_subject_teachers.items())
            if index not in [dp.currentIndex() for dp in self.dp_tracker.values()]
        )
        
        self.add_subject(subject_id, {"per_day": str(self.default_per_day), "per_week": str(self.default_per_week), "teachers": self.available_subject_teachers[subject_id]["teachers"]})
        
        self.saved_state_changed.emit()
    
    def get(self):
        return {"content": self.info, "id_mapping": self.id_mapping, "available_subject_teachers": self.available_subject_teachers}
    
    def add_subject(self, subject_id: str, info: dict):
        selection_widget = QWidget()
        selection_widget.setObjectName("subjectItem")
        
        layout = QVBoxLayout()
        selection_widget.setLayout(layout)
        
        subjects_dp = QComboBox()
        if self.subjects:
            subjects_dp.addItems(self.subjects)
        else:
            subjects_dp.setDisabled(True)
        
        subjects_dp.setCurrentIndex(next((s_i for s_i, s_id in self.id_mapping.items() if s_id == subject_id)))
        subjects_dp.currentIndexChanged.connect(self.make_dp_clicked_func(subject_id))
        self.dp_tracker[subject_id] = subjects_dp
        
        sub_layout = QHBoxLayout()
        
        layout.addWidget(subjects_dp)
        layout.addLayout(sub_layout)
        
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
        
        teacher_button = QPushButton("Teachers")
        teacher_button.setMaximumWidth(60)
        teacher_button.clicked.connect(self.make_show_teacher_popup_func(subject_id))
        
        sub_layout.addWidget(per_day_edit, alignment=Qt.AlignmentFlag.AlignLeft)
        sub_layout.addWidget(per_week_edit, alignment=Qt.AlignmentFlag.AlignLeft)
        sub_layout.addWidget(teacher_button, alignment=Qt.AlignmentFlag.AlignLeft)
        
        self.del_widg_func_tracker[subject_id] = self.make_dp_destroy_func(subject_id)
        
        widget = SelectedWidget(selection_widget, self.container_layout)
        widget.setFixedHeight(100)
        widget.delete_button.clicked.connect(self.del_widg_func_tracker[subject_id])
        
        self.container_layout.insertWidget(0, widget, alignment=Qt.AlignmentFlag.AlignTop)
        
        self.info[subject_id] = info
        
        if len(self.dp_tracker) == len(self.subjects):
            self.add_button.setDisabled(True)
    
    def make_show_teacher_popup_func(self, subject_id: str):
        def temp_show_teacher_popup():
            info = self.info[subject_id]
            
            teachers = SelectionList("Teachers", info["teachers"])
            teachers.exec()
            info["teachers"] = teachers.get()
        
        return temp_show_teacher_popup
    
    def make_text_changed_func(self, subject_id: str, key: str, input_edit: 'NumberTextEdit'):
        def text_changed_func():
            self.info[subject_id][key] = input_edit.edit.text()
            
            self.saved_state_changed.emit()
        
        return text_changed_func

    def make_dp_clicked_func(self, subject_id: str):
        def dp_clicked_func(index):
            dublicate_dp_id = next((dublicate_dp_id for dublicate_dp_id, odp in self.dp_tracker.copy().items() if dublicate_dp_id != subject_id and odp.currentIndex() == index), None)
            new_subject_id = self.id_mapping[index]
            
            if dublicate_dp_id is not None:
                new_subject_id = dublicate_dp_id
                
                odp = self.dp_tracker[dublicate_dp_id]
                
                widget = odp.parent().parent()
                self.container_layout.removeWidget(widget)
                widget.deleteLater()
                self.add_button.setDisabled(False)
            
            self.info[new_subject_id] = self.info.pop(subject_id)
            self.info[new_subject_id]["teachers"] = self.available_subject_teachers[new_subject_id]["teachers"]
            self.dp_tracker[new_subject_id] = self.dp_tracker.pop(subject_id)
            
            main_widget = self.dp_tracker[new_subject_id].parent().parent()
            sub_widget_layout = self.dp_tracker[new_subject_id].parent().layout().itemAt(1).layout()
            
            per_day_edit = sub_widget_layout.itemAt(0).widget()
            per_day_edit.edit.textChanged.disconnect()
            per_day_edit.edit.textChanged.connect(self.make_text_changed_func(new_subject_id, "per_day", per_day_edit))
            
            per_week_edit = sub_widget_layout.itemAt(1).widget()
            per_week_edit.edit.textChanged.disconnect()
            per_week_edit.edit.textChanged.connect(self.make_text_changed_func(new_subject_id, "per_week", per_week_edit))
            
            teacher_button = sub_widget_layout.itemAt(2).widget()
            teacher_button.clicked.disconnect()
            teacher_button.clicked.connect(self.make_show_teacher_popup_func(new_subject_id))
            
            self.dp_tracker[new_subject_id].currentIndexChanged.disconnect()
            self.dp_tracker[new_subject_id].currentIndexChanged.connect(self.make_dp_clicked_func(new_subject_id))
            
            main_widget.delete_button.clicked.disconnect(self.del_widg_func_tracker.pop(subject_id))
            self.del_widg_func_tracker[new_subject_id] = self.make_dp_destroy_func(new_subject_id)
            main_widget.delete_button.clicked.connect(self.del_widg_func_tracker[new_subject_id])
            
            self.saved_state_changed.emit()
        
        return dp_clicked_func

    def make_dp_destroy_func(self, subject_id: str):
        def dp_destroy_func():
            self.add_button.setDisabled(False)
            self.info.pop(subject_id)
            self.dp_tracker.pop(subject_id)
            
            self.saved_state_changed.emit()
        
        return dp_destroy_func

class OptionSelection(QDialog):
    def __init__(self, title: str, info: dict[str, str], saved_state_changed: pyqtBoundSignal | None = None):
        super().__init__()
        
        self.title = title
        self.info = info
        self.saved_state_changed = saved_state_changed
        
        self.setWindowTitle(self.title)
        
        self.options = []
        self.current_row = 0
        self.current_col = 0
        self.max_cols = 4  # Maximum number of columns before wrapping
        
        self.main_layout = QVBoxLayout(self)
        
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        
        self.container = QWidget()
        self.container.setObjectName("optionselectorcontainer")
        self.grid_layout = QGridLayout(self.container)  # Use QGridLayout
        self.grid_layout.setSpacing(4)
        self.grid_layout.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
        self.scroll_area.setWidget(self.container)
        
        self.add_button = QPushButton("Add Option")
        self.add_button.clicked.connect(lambda: self.add_option())
        
        self.main_layout.addWidget(self.scroll_area)
        self.main_layout.addWidget(self.add_button, alignment=Qt.AlignmentFlag.AlignRight)
        
        temp_option = OptionTag("IFe")
        self.setFixedSize((temp_option.width() + (temp_option.main_layout.spacing() * 4) + self.grid_layout.spacing()) * self.max_cols, 300)
        
        del temp_option
        
        # Load existing options
        for option_id, option_name in self.info.items():
            self.add_option(option_id, option_name)
        
        self.setStyleSheet("""
            QDialog {
                background-color: """ + _widgets_bg_color_2 + """;
            }
            QPushButton {
                background-color: """ + _widgets_bg_color_5 + """;
                color: """ + _widget_text_color_2 + """;
                border: none;
                border-radius: """ + _widget_border_radius_1 + """;
                min-width: 60px;
                padding: 5px;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: """ + get_hover_color(_widgets_bg_color_5) + """;
            }
            QWidget #optionselectorcontainer {
                background-color: """ + _main_bg_color_1 + """
            }
            """ + _general_scrollbar_theme
            )
    
    def get(self):
        return self.info
    
    def add_option(self, _id: str | None = None, text: str = ""):
        option = OptionTag(text)
        
        _id = str(hex(id(option)).upper()) if _id is None else _id
        
        def update_option():
            self.info[_id] = option.get_text()
            
            if self.saved_state_changed is not None:
                self.saved_state_changed.emit()
        
        update_option()
        
        option.done_editing.connect(update_option)
        
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
        
        if not text:
            option.start_editing()
    
    def close(self):
        for option in self.options:
            if option.is_editing:
                option.finish_editing()
        
        return super().close()
    
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



