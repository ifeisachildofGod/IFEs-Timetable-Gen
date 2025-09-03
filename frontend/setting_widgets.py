from frontend.imports import *
from frontend.sub_widgets import *

class SettingWidget(QWidget):
    def __init__(self, main_window: QMainWindow, name: str, input_placeholders: list[str], saved_state_changed: pyqtBoundSignal, data: dict | None = None):
        super().__init__()
        self.main_window = main_window
        
        self.objectNameChanged.connect(lambda: self.add_button.setText(f"Add {self.objectName().title()}"))
        
        self.info = {}
        self.id_mapping = {}
        self.input_placeholders = input_placeholders
        self.saved_state_changed = saved_state_changed
        
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setSpacing(10)
        self.main_layout.setContentsMargins(0, 0, 10, 10)
        
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        
        self.container = QWidget()
        self.container.setContentsMargins(20, 10, 20, 10)
        
        self.container_layout = QVBoxLayout(self.container)
        self.container_layout.setSpacing(20)
        self.scroll_area.setWidget(self.container)
        
        def add_func():
            self.add(self.input_placeholders)
            self.saved_state_changed.emit()
        
        self.add_button = QPushButton()
        self.add_button.clicked.connect(add_func)
        
        self.main_layout.addWidget(self.scroll_area)
        self.main_layout.addWidget(self.add_button, alignment=Qt.AlignmentFlag.AlignRight)
        
        self.setLayout(self.main_layout)
        self.setObjectName(name)
        
        if data is not None:
            self.__dict__.update(data["constants"])
            
            for _id, values in data["variables"].items():
                self.add(self.input_placeholders, _id, values)
        
        self.container_layout.addStretch()
        
        self.scroll_area.verticalScrollBar().setValue(0)
    
    def keyPressEvent(self, a0):
        if a0.key() == 16777220:
            focus_widget = self.focusWidget()
            
            if isinstance(focus_widget, (QLineEdit, QScrollArea)):
                self.add(self.input_placeholders)
        
        return super().keyPressEvent(a0)
    
    def get(self):
        return self.info
    
    def get_constants(self):
        return {}
    
    def add(self, input_placeholders: list[tuple[str, int]], _id: str | None = None, data: dict | None = None):
        widget = QWidget()
        layout = QVBoxLayout()
        
        widget.setProperty("class", "SettingOptionEntry")
        widget.setContentsMargins(20, 5, 20, 5)
        widget.setLayout(layout)
        
        buttons_layout = QHBoxLayout()
        header_layout = QHBoxLayout()
        
        _id = (self.objectName().lower() + ":" + hex(id(widget)).upper().replace("0X", "")) if _id is None else _id
        
        if data is None:
            self.info[_id] = self.get_new_data()
        else:
            self.info[_id] = data
        
        text_edits = self._make_inputs(_id, input_placeholders, data)
        
        delete_button = QPushButton("×")
        delete_button.setProperty("class", 'Close')
        delete_button.clicked.connect(self._make_delete_func(_id, widget))
        
        self.make_popups(_id, buttons_layout)
        buttons_layout.addWidget(delete_button, alignment=Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignTop)
        
        layout.addLayout(buttons_layout)
        layout.addLayout(header_layout)
        
        self.container_layout.insertWidget(len(self.info) - 1, widget, alignment=Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignVCenter)
        
        self.scroll_area.update()
        self.scroll_area.verticalScrollBar().setValue(self.scroll_area.verticalScrollBar().maximum())
        
        for index, (edit, stretch) in enumerate(text_edits):
            header_layout.addWidget(edit, stretch=stretch)
            edit.show()
            
            if not index:
                edit.setFocus()
    
    def make_popups(self, _id: str, layout: QHBoxLayout):
        pass
    
    def get_new_data(self):
        pass
    
    def update_data_interaction(self, prev_index: int, curr_index: int):
        pass
    
    def entry_deleted(self, _id):
        pass
    
    def _make_inputs(self, _id: str, placeholders: list[str, int], data: dict | None):
        text_edits: list[tuple[QLineEdit, int]] = []
        
        for index, (placeholder, stretch) in enumerate(placeholders):
            text = data["text"][index] if data is not None else ""
            
            edit = QLineEdit()
            edit.setPlaceholderText(placeholder)
            edit.setFixedHeight(80)
            if data is None: self.info[_id]["text"].append(text)
            edit.textChanged.connect(self._make_text_changed_func(_id, index))
            edit.setText(text)
            
            text_edits.append((edit, stretch))
        
        return text_edits
    
    def _make_text_changed_func(self, _id, index):
        def text_changed_func(text: str):
            self.info[_id]["text"][index] = text
            self.saved_state_changed.emit()
        
        return text_changed_func
    
    def _make_delete_func(self, _id: str, widget: QWidget):
        def del_widget():
            self.container_layout.removeWidget(widget)
            widget.deleteLater()
            self.entry_deleted(_id)
            self.info.pop(_id)
        
        return del_widget
    
    def _make_popup(self, _id: str, title: str, layout: QHBoxLayout, popup_class: type[SelectionList] | type[SubjectSelection] | type[OptionsMaker] | type[SubjectDropdownCheckBoxes], var_name: str, button_name: str | None = None, closed_func: Callable[[str], None] | None = None, alignment: Qt.AlignmentFlag = None, *args, **kwargs):
        button = QPushButton(button_name if button_name is not None else title)
        
        button.setFixedWidth(100)
        button.setProperty("class", 'action')
        button.clicked.connect(self._make_popup_func(_id, title, popup_class, var_name, closed_func, *args, **kwargs))
        
        if alignment is not None:
            layout.addWidget(button, alignment=alignment)
        else:
            layout.addWidget(button)
    
    def _make_popup_func(self, _id: str, title: str, popup_class: type[SelectionList] | type[SubjectSelection] | type[OptionsMaker] | type[SubjectDropdownCheckBoxes], var_name: str, closed_func: Callable[[str], None] | None, *args, **kwargs):
        def show_popup():
            popup = popup_class(title=title, info=self.info[_id].get(var_name, {}), saved_state_changed=self.saved_state_changed, *args, **kwargs)
            
            popup.exec()
            self.info[_id][var_name] = popup.get()
            
            if closed_func is not None:
                closed_func(_id)
        
        return show_popup


class Subjects(SettingWidget):
    def __init__(self, main_window: QMainWindow, save_data: dict | None, saved_state_changed):
        self.teachers = [None]
        self.classes_data = {"content": {}, "id_mapping": {"main": {}, "sub": {}}}
        
        super().__init__(main_window, "Subjects", [("Enter the subject name", 10)], saved_state_changed, save_data)
    
    def update_data_interaction(self, prev_index, curr_index):
        general_condition = prev_index != 3 and not (curr_index == 3 and prev_index != 0)
        if not general_condition:
            return
        
        teacher_update_condition = (prev_index == 1 and curr_index == 0) or (curr_index == 2 and prev_index == 1)
        class_update_condition = (prev_index == 2 and curr_index == 0) or (curr_index == 1 and prev_index == 2)
        
        teacher_info = self.main_window.teachers_widget.get()
        
        if teacher_update_condition:
            # Update Teachers
            teachers = [None]
            
            for teacher_id, teacher_info_entry in teacher_info.items():
                teacher_name = " ".join(teacher_info_entry["text"])
                teachers.append((teacher_id, teacher_name))
            
            self.main_window.subjects_widget.teachers = teachers
            
            for teacher_id, teacher_info_entry in teacher_info.items():
                teacher_subject_index_id_mapping = {k: i for i, (k, _) in enumerate(SelectionList.fix_none_selection_content_problem(teacher_info_entry["subjects"]))}
                
                for subject_id, subject_info_entry in self.info.items():
                    teacher_index_in_subject = None
                    
                    for s_t_index, s_t_data in enumerate(SelectionList.fix_none_selection_content_problem(subject_info_entry["teachers"])):
                        if s_t_data is not None and s_t_data[0] == teacher_id:
                            teacher_index_in_subject = s_t_index
                            break
                    
                    subject_index_in_teacher = teacher_subject_index_id_mapping[subject_id]  # The teaacher must always be in the teacher list, if not there is a problem
                    
                    if teacher_index_in_subject is None:
                        teacher_index_in_subject = len(subject_info_entry["teachers"])
                        teacher_name = " ".join(teacher_info_entry["text"])
                        
                        subject_info_entry["teachers"].append((teacher_id, teacher_name))
                    
                    subject_none_index_in_teacher = teacher_info_entry["subjects"].index(None)
                    teacher_none_index_in_subject = subject_info_entry["teachers"].index(None)
                    
                    is_teacher_selected_in_subject = teacher_index_in_subject < teacher_none_index_in_subject
                    is_subject_selected_in_teacher = subject_index_in_teacher < subject_none_index_in_teacher
                    
                    if is_teacher_selected_in_subject != is_subject_selected_in_teacher:
                        curr_subject_value = subject_info_entry["teachers"].pop(teacher_index_in_subject)
                        
                        if is_subject_selected_in_teacher and not is_teacher_selected_in_subject:
                            # Make is selected in the subject editor
                            subject_info_entry["teachers"].insert(teacher_none_index_in_subject, curr_subject_value)
                        elif not is_subject_selected_in_teacher and is_teacher_selected_in_subject:
                            # Make is unselected in the subject editor
                            subject_info_entry["teachers"].append(curr_subject_value)
            
            for subject_id, subject_info_entry in self.info.items():
                for s_t_index, (s_t_id, _) in enumerate(SelectionList.fix_none_selection_content_problem(subject_info_entry["teachers"])):
                    if s_t_id is not None:
                        if s_t_id not in teacher_info:
                            subject_info_entry["teachers"].pop(s_t_index)
                        else:
                            teacher_name = " ".join(teacher_info[s_t_id]["text"])
                            subject_info_entry["teachers"][s_t_index] = (s_t_id, teacher_name)
        
        if class_update_condition:
            self.update_classes()
    
    def get_new_data(self):
        return {
            "text": [],
            "classes": {},
            "teachers": deepcopy(self.teachers)
        }
    
    def get_constants(self):
        return {
            "teachers": self.teachers,
            "classes_data": self.classes_data
        }
    
    def make_popups(self, _id, layout):
        self._make_popup(_id, "Classes", layout, SubjectDropdownCheckBoxes, "classes", general_data=self.classes_data)
        self._make_popup(_id, "Teachers", layout, SelectionList, "teachers", alignment=Qt.AlignmentFlag.AlignLeft)
    
    def update_classes(self):
        class_info = self.main_window.classes_widget.get()
        
        self.classes_data["content"] = {}
        
        self.classes_data["id_mapping"]["main"] = {}
        self.classes_data["id_mapping"]["sub"] = {}
        
        for class_id, class_info_entry in class_info.items():
            self.classes_data["content"][class_id] = dict.fromkeys(class_info_entry["options"], False)
            
            self.classes_data["id_mapping"]["main"][class_id] = class_info_entry["text"][0]
            self.classes_data["id_mapping"]["sub"][class_id] = class_info_entry["options"].copy()
        
        for subject_data_entry in self.info.values():
            for class_id, options_data in subject_data_entry["classes"].copy().items():
                if class_id not in class_info:
                    subject_data_entry["classes"].pop(class_id)
                    continue
                
                for option_id in options_data.copy():
                    if option_id not in class_info[class_id]["options"]:
                        options_data.pop(option_id)

class Teachers(SettingWidget):
    def __init__(self, main_window: QMainWindow, save_data: dict | None, saved_state_changed):
        self.subjects = [None]
        self.all_subject_classes_info = {}
        
        super().__init__(main_window, "Teachers", [("Full name", 10)], saved_state_changed, save_data)
    
    def update_data_interaction(self, prev_index, curr_index):
        class_update_condition = prev_index in (0, 2)
        if not ((prev_index == 0 and curr_index in (1, 2)) or (curr_index == 3 and prev_index != 1) or (class_update_condition and curr_index == 1)) or prev_index == 3:
            return
        
        subject_info = self.main_window.subjects_widget.get()
        
        subjects = [None]
        
        for subject_id, subject_info_entry in subject_info.items():
            subject_name = " ".join(subject_info_entry["text"])
            subjects.append((subject_id, subject_name))
        
        self.main_window.teachers_widget.subjects = subjects
        
        for subject_id, subject_info_entry in subject_info.items():
            subject_teacher_index_id_mapping = {k: i for i, (k, _) in enumerate(SelectionList.fix_none_selection_content_problem(subject_info_entry["teachers"]))}
            
            for teacher_id, teacher_info_entry in self.info.items():
                subject_index_in_teacher = None
                
                for t_s_index, t_s_data in enumerate(SelectionList.fix_none_selection_content_problem(teacher_info_entry["subjects"])):
                    if t_s_data is not None and t_s_data[0] == subject_id:
                        subject_index_in_teacher = t_s_index
                        break
                
                teacher_index_in_subject = subject_teacher_index_id_mapping[teacher_id]  # The teacher must always be in the subject list, if not there is a problem
                
                if subject_index_in_teacher is None:
                    subject_index_in_teacher = len(teacher_info_entry["subjects"])
                    subject_name = " ".join(subject_info_entry["text"])
                    
                    teacher_info_entry["subjects"].append((subject_id, subject_name))
                
                teacher_none_index_in_subject = subject_info_entry["teachers"].index(None)
                subject_none_index_in_teacher = teacher_info_entry["subjects"].index(None)
                
                is_subject_selected_in_teacher = subject_index_in_teacher < subject_none_index_in_teacher
                is_teacher_selected_in_subject = teacher_index_in_subject < teacher_none_index_in_subject
                
                if is_subject_selected_in_teacher != is_teacher_selected_in_subject:
                    curr_teacher_value = teacher_info_entry["subjects"].pop(subject_index_in_teacher)
                    
                    if not is_subject_selected_in_teacher:
                        # Make is selected in the teacher editor
                        teacher_info_entry["subjects"].insert(subject_none_index_in_teacher, curr_teacher_value)
                    elif not is_teacher_selected_in_subject:
                        # Make is unselected in the teacher editor
                        teacher_info_entry["subjects"].append(curr_teacher_value)
        
        for teacher_id, teacher_info_entry in self.info.items():
            for t_s_index, (t_s_id, _) in enumerate(SelectionList.fix_none_selection_content_problem(teacher_info_entry["subjects"])):
                if t_s_id is not None:
                    if t_s_id not in subject_info:
                        teacher_info_entry["subjects"].pop(t_s_index)
                    else:
                        subject_name = " ".join(subject_info[t_s_id]["text"])
                        teacher_info_entry["subjects"][t_s_index] = (t_s_id, subject_name)
                
            if class_update_condition:
                self._update_classes(teacher_id)
    
    def get_new_data(self):
        return {
            "text": [],
            "classes": {"content": {}, "id_mapping": {}},
            "subjects": deepcopy(self.subjects)
        }
    
    def get_constants(self):
        return {
            "subjects": self.subjects,
            "all_subject_classes_info": self.all_subject_classes_info
        }
    
    def entry_deleted(self, _id):
        self._update_classes_deactivated_general(_id)
    
    def make_popups(self, _id, layout):
        self._make_popup(_id, "Classes", layout, TeacherDropdownCheckBoxes, "classes", teacher_id=_id, general_data=self.all_subject_classes_info, default_max_classes=self.main_window.default_max_classes)
        self._make_popup(_id, "Subjects", layout, SelectionList, "subjects", closed_func=self._update_classes, alignment=Qt.AlignmentFlag.AlignLeft)
    
    def _update_classes_deactivated_general(self, _id):
        selected_subjects_data = {t_s_id: t_s_index for t_s_index, (t_s_id, _) in enumerate(SelectionList.fix_none_selection_content_problem(self.info[_id]["subjects"])) if t_s_index < self.info[_id]["subjects"].index(None)}
        subjects_data = [t_s_id for t_s_id, _ in SelectionList.fix_none_selection_content_problem(self.info[_id]["subjects"]) if t_s_id is not None]
        
        for subject_id, subject_data_info in self.all_subject_classes_info.copy().items():
            if subject_id not in subjects_data:
                self.all_subject_classes_info.pop(subject_id)
            else:
                for _, options_info in subject_data_info["content"].values():
                    option_values = list(options_info.values())
                    
                    if option_values.count(False) == len(option_values):
                        continue
                    
                    for opt_id, opt_state in options_info.copy().items():
                        if isinstance(opt_state, str) and opt_state not in self.info:
                            options_info[opt_id] = False
        
        return selected_subjects_data
    
    def _update_classes(self, _id):
        class_info = self.main_window.classes_widget.get()
        subject_info = self.main_window.subjects_widget.get()
        
        subject_general_data = self.main_window.subjects_widget.classes_data
        
        teacher_subject_class_content_info = self.info[_id]["classes"]["content"]
        teacher_subject_class_id_mapping_info = self.info[_id]["classes"]["id_mapping"]
        
        # Updating generals
        selected_subjects_data = self._update_classes_deactivated_general(_id)
        
        for subject_id in selected_subjects_data:
            if subject_id not in teacher_subject_class_content_info:
                teacher_subject_class_content_info[subject_id] = {}
                teacher_subject_class_id_mapping_info[subject_id] = subject_info[subject_id]["text"][0]
            
            if subject_id not in self.all_subject_classes_info:
                self.all_subject_classes_info[subject_id] = {"content": {}, "id_mapping": {"main": {}, "sub": {}}}
            
            # Setting the content data
            for class_id, options_info in subject_info[subject_id]["classes"].items():
                if class_id not in self.all_subject_classes_info[subject_id]["content"]:
                    self.all_subject_classes_info[subject_id]["content"][class_id] = [None, dict.fromkeys(options_info, False)]
                else:
                    for opt_id in self.all_subject_classes_info[subject_id]["content"][class_id][1].copy():
                        if opt_id not in options_info:
                            self.all_subject_classes_info[subject_id]["content"][class_id][1].pop(opt_id)
                            
                            self.all_subject_classes_info[subject_id]["id_mapping"]["sub"][class_id].pop(opt_id)
                
                # Setting the ID mapping
                self.all_subject_classes_info[subject_id]["id_mapping"]["main"][class_id] = subject_general_data["id_mapping"]["main"][class_id]
                
                self.all_subject_classes_info[subject_id]["id_mapping"]["sub"][class_id] = {}
                for option_id in self.all_subject_classes_info[subject_id]["content"][class_id][1]:
                    self.all_subject_classes_info[subject_id]["id_mapping"]["sub"][class_id][option_id] =\
                        subject_general_data["id_mapping"]["sub"][class_id][option_id]
            
            # Removing the unremoved in the general data
            for class_id, (_, options_info) in self.all_subject_classes_info[subject_id]["content"].copy().items():
                if class_id not in class_info or class_id not in subject_info[subject_id]["classes"]:
                    if class_id in teacher_subject_class_content_info:
                        teacher_subject_class_content_info.pop(class_id)
                        teacher_subject_class_id_mapping_info["main"].pop(class_id)
                        teacher_subject_class_id_mapping_info["sub"].pop(class_id)
                    
                    self.all_subject_classes_info[subject_id]["content"].pop(class_id)
                    
                    self.all_subject_classes_info[subject_id]["id_mapping"]["main"].pop(class_id)
                    self.all_subject_classes_info[subject_id]["id_mapping"]["sub"].pop(class_id)
                else:
                    for option_id in options_info.copy():
                        if option_id not in class_info[class_id]["options"] or option_id not in subject_info[subject_id]["classes"][class_id]:
                            if class_id in teacher_subject_class_content_info:
                                if option_id in teacher_subject_class_content_info[class_id][1]:
                                    teacher_subject_class_content_info[class_id][1].pop(option_id)
                                    teacher_subject_class_id_mapping_info["sub"][class_id].pop(option_id)
                            
                                if not teacher_subject_class_id_mapping_info[class_id][1]:
                                    teacher_subject_class_id_mapping_info.pop(class_id)
                            
                            self.all_subject_classes_info[subject_id]["content"][class_id][1].pop(option_id)
                            self.all_subject_classes_info[subject_id]["id_mapping"]["sub"][class_id].pop(option_id)
        
        # Removals
        for subject_id, subject_class_data in teacher_subject_class_content_info.copy().items():
            if subject_id not in selected_subjects_data:
                teacher_subject_class_content_info.pop(subject_id)
                teacher_subject_class_id_mapping_info.pop(subject_id)
                continue
            
            for class_id in subject_class_data.copy():
                if class_id not in class_info or class_id not in subject_info[subject_id]["classes"]:
                    subject_class_data.pop(class_id)
                    continue
                
                for option_id in subject_class_data[class_id][1].copy():
                    if option_id not in class_info[class_id]["options"] or option_id not in subject_info[subject_id]["classes"][class_id]:
                        subject_class_data[class_id][1].pop(option_id)

class Classes(SettingWidget):
    def __init__(self, main_window: QMainWindow, save_data: dict | None, saved_state_changed):
        super().__init__(main_window, "Classes", [("Enter the class section name", 10)], saved_state_changed, save_data)
    
    def update_data_interaction(self, prev_index, _):
        if prev_index in (2, 3):
            return
        
        subject_info = self.main_window.subjects_widget.get()
        
        for class_id, class_info_entry in self.info.items():
            for subject_id, subject_info_entry in subject_info.items():
                if class_id in subject_info_entry["classes"]:
                    default = [
                        _,
                        {
                            "per_day": str(self.main_window.default_per_day),
                            "per_week": str(self.main_window.default_per_week)
                        }
                    ]
                    
                    class_info_entry["subjects"][subject_id] = class_info_entry["subjects"].get(subject_id, default)
                    class_info_entry["subjects"][subject_id][0] = subject_info_entry["text"][0]
                elif subject_id in class_info_entry["subjects"]:
                    class_info_entry["subjects"].pop(subject_id)
            
            for subject_id in class_info_entry["subjects"].copy():
                if subject_id not in subject_info:
                    class_info_entry["subjects"].pop(subject_id)
    
    def get_new_data(self):
        return {
            "text": [],
            "options": {},
            "subjects": {}
        }
    
    def get_constants(self):
        return {}
    
    def make_popups(self, _id, layout):
        self._make_popup(_id, "Option Selector", layout, OptionsMaker, "options", button_name="Options", closed_func=lambda _: self.main_window.subjects_widget.update_classes())
        self._make_popup(_id, "Subjects", layout, SubjectSelection, "subjects", alignment=Qt.AlignmentFlag.AlignLeft)


