from frontend.imports import *
from frontend.sub_widgets import *

class Subjects(BaseSettingWidget):
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
        
        teacher_info = self.main_window.teachers_widget.get() # type: ignore
        
        if teacher_update_condition:
            # Update Teachers
            teachers: list[tuple[str, str] | None] = [None]
            
            for teacher_id, teacher_info_entry in teacher_info.items():
                teacher_name = " ".join(teacher_info_entry["text"])
                teachers.append((teacher_id, teacher_name))
            
            self.main_window.subjects_widget.teachers = teachers # type: ignore
            
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
                removals = []
                
                for s_t_index, (s_t_id, _) in enumerate(SelectionList.fix_none_selection_content_problem(subject_info_entry["teachers"])):
                    if s_t_id is not None:
                        if s_t_id not in teacher_info:
                            removals.append(s_t_index)
                        else:
                            subject_info_entry["teachers"][s_t_index] = s_t_id, " ".join(teacher_info[s_t_id]["text"])
                
                for index in sorted(removals, reverse=True):
                    subject_info_entry["teachers"].pop(index)
        
        if class_update_condition:
            self.update_classes()
        
        if class_update_condition or teacher_update_condition:
            self._update_display_data_info()
    
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
        class_info = self.main_window.classes_widget.get() # type: ignore
        
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
    
    def popup_closed(self, _id, var_name, popup, init = False):
        super().popup_closed(_id, var_name, popup, init)
        
        if isinstance(popup, SelectionList):
            self.clear_display_data_info(_id, var_name)
            
            popup_data = popup.get()
            
            for t_id, text in popup_data[:popup_data.index(None)]:
                self.add_display_data_info(_id, var_name, text, t_id)
        elif isinstance(popup, SubjectDropdownCheckBoxes):
            self.clear_display_data_info(_id, var_name)
            
            popup_data = popup.get()
            
            for lvl_id, lvl_data in popup_data.items():
                for cls_id, cls_state in lvl_data.items():
                    if cls_state:
                        self.add_display_data_info(
                            _id,
                            var_name,
                            f"{popup.general_data["id_mapping"]["main"][lvl_id]} {popup.general_data["id_mapping"]["sub"][lvl_id][cls_id]}",
                            f"{lvl_id}--{cls_id}"
                        )

class Teachers(BaseSettingWidget):
    def __init__(self, main_window: QMainWindow, save_data: dict | None, saved_state_changed):
        self.subjects = [None]
        self.all_subject_classes_info = {}
        
        super().__init__(main_window, "Teachers", [("Full name", 10)], saved_state_changed, save_data)
    
    def update_data_interaction(self, prev_index, curr_index):
        class_update_condition = prev_index in (0, 2)
        if not ((prev_index == 0 and curr_index in (1, 2)) or (curr_index == 3 and prev_index != 1) or (class_update_condition and curr_index == 1)) or prev_index == 3:
            return
        
        subject_info = self.main_window.subjects_widget.get() # type: ignore
        
        subjects: list[tuple[str, str] | None] = [None]
        
        for subject_id, subject_info_entry in subject_info.items():
            subject_name = " ".join(subject_info_entry["text"])
            subjects.append((subject_id, subject_name))
        
        self.main_window.teachers_widget.subjects = subjects # type: ignore
        
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
            removals = []
            
            for t_s_index, (t_s_id, _) in enumerate(SelectionList.fix_none_selection_content_problem(teacher_info_entry["subjects"])):
                if t_s_id is not None:
                    if t_s_id not in subject_info:
                        removals.append(t_s_index)
                    else:
                        teacher_info_entry["subjects"][t_s_index] = t_s_id, " ".join(subject_info[t_s_id]["text"])
            
            for index in sorted(removals, reverse=True):
                teacher_info_entry["subjects"].pop(index)
            
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
        self._make_popup(_id, "Classes", layout, TeacherDropdownCheckBoxes, "classes", teacher_id=_id, general_data=self.all_subject_classes_info, default_max_classes=self.main_window.default_max_classes) # type: ignore
        self._make_popup(_id, "Subjects", layout, SelectionList, "subjects", alignment=Qt.AlignmentFlag.AlignLeft)
    
    def popup_closed(self, _id, popup, var_name, init = False):
        super().popup_closed(_id, var_name, popup, init)
        
        if isinstance(popup, SelectionList):
            if not init:
                self._update_classes(_id)
            
            self.clear_display_data_info(_id, var_name)
            
            popup_data = popup.get()
            
            for s_id, text in popup_data[:popup_data.index(None)]:
                self.add_display_data_info(_id, var_name, text, s_id)
        elif isinstance(popup, TeacherDropdownCheckBoxes):
            subject_info = self.main_window.subjects_widget.get()
            class_info = self.main_window.classes_widget.get()
            
            self.clear_display_data_info(_id, var_name)
            
            popup_data = popup.get()
            
            for s_id, s_data in popup_data["content"].items():
                for lvl_id, (random, cls_data) in s_data.items():
                    if random is not None:
                        self.add_display_data_info(
                            _id,
                            var_name,
                            f"{random} selected in {''.join(class_info[lvl_id]['text'])}",
                            lvl_id
                        )
                    else:
                        for cls_id, cls_state in cls_data.items():
                            if cls_state:
                                self.add_display_data_info(
                                    _id,
                                    var_name,
                                    f"{' '.join(subject_info[s_id]["text"])} in {' '.join(class_info[lvl_id]['text'])} {class_info[lvl_id]['options'][cls_id]}",
                                    f"{lvl_id}-{cls_id}"
                                )
    
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
        class_info = self.main_window.classes_widget.get() # type: ignore
        subject_info = self.main_window.subjects_widget.get() # type: ignore
        
        teacher_subject_class_content_info = self.info[_id]["classes"]["content"]
        teacher_subject_class_id_mapping_info = self.info[_id]["classes"]["id_mapping"]
        
        # Updating generals
        selected_subjects_data = self._update_classes_deactivated_general(_id)
        
        for subject_id in selected_subjects_data:
            teacher_subject_class_id_mapping_info[subject_id] = subject_info[subject_id]["text"][0]
            
            if subject_id not in teacher_subject_class_content_info:
                teacher_subject_class_content_info[subject_id] = {}
            
            if subject_id not in self.all_subject_classes_info:
                self.all_subject_classes_info[subject_id] = {"content": {}, "id_mapping": {"main": {}, "sub": {}}}
            
            # Removing the unremoved in the general data
            for class_id, (_, options_info) in self.all_subject_classes_info[subject_id]["content"].copy().items():
                if class_id not in class_info or class_id not in subject_info[subject_id]["classes"]:
                    if class_id in teacher_subject_class_content_info:
                        teacher_subject_class_content_info.pop(class_id)
                        # teacher_subject_class_id_mapping_info["main"].pop(class_id)
                        # teacher_subject_class_id_mapping_info["sub"].pop(class_id)
                    
                    self.all_subject_classes_info[subject_id]["content"].pop(class_id)
                    
                    self.all_subject_classes_info[subject_id]["id_mapping"]["main"].pop(class_id)
                    self.all_subject_classes_info[subject_id]["id_mapping"]["sub"].pop(class_id)
                    
                    if class_id in subject_info[subject_id]["classes"]:
                        subject_info[subject_id]["classes"].pop(class_id)
                else:
                    for option_id in options_info.copy():
                        if option_id not in class_info[class_id]["options"] or option_id not in subject_info[subject_id]["classes"][class_id]:
                            if class_id in teacher_subject_class_content_info:
                                if option_id in teacher_subject_class_content_info[class_id][1]:
                                    teacher_subject_class_content_info[class_id][1].pop(option_id)
                                    # teacher_subject_class_id_mapping_info["sub"][class_id].pop(option_id)
                            
                                # if not teacher_subject_class_id_mapping_info[class_id][1]:
                                #     teacher_subject_class_id_mapping_info.pop(class_id)
                            
                            self.all_subject_classes_info[subject_id]["content"][class_id][1].pop(option_id)
                            self.all_subject_classes_info[subject_id]["id_mapping"]["sub"][class_id].pop(option_id)
                            
                            if option_id in subject_info[subject_id]["classes"][class_id]:
                                subject_info[subject_id]["classes"][class_id].pop(option_id)
            
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
                self.all_subject_classes_info[subject_id]["id_mapping"]["main"][class_id] = "".join(class_info[class_id]["text"])
                
                self.all_subject_classes_info[subject_id]["id_mapping"]["sub"][class_id] = {}
                for option_id in self.all_subject_classes_info[subject_id]["content"][class_id][1]:
                    self.all_subject_classes_info[subject_id]["id_mapping"]["sub"][class_id][option_id] = class_info[class_id]["options"][option_id]
        
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

class Classes(BaseSettingWidget):
    def __init__(self, main_window: QMainWindow, save_data: dict | None, saved_state_changed):
        super().__init__(main_window, "Classes", [("Enter the class section name", 10)], saved_state_changed, save_data)
    
    def update_data_interaction(self, prev_index, curr_index):
        if prev_index in (2, 3):
            return
        
        subject_info = self.main_window.subjects_widget.get() # type: ignore
        
        for class_id, class_info_entry in self.info.items():
            for subject_id, subject_info_entry in subject_info.items():
                if class_id in subject_info_entry["classes"]:
                    default = [
                        None,
                        {
                            "per_day": self.main_window.default_per_day, # type: ignore
                            "per_week": self.main_window.default_per_week # pyright: ignore[reportAttributeAccessIssue]
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
    
    def make_popups(self, _id, layout):
        index = len(self.get()) - 1
        
        if index >= len(self.main_window.school.project["levels"]):
            self.main_window.school.project["levels"].append([
                "",
                [
                    [self.main_window.default_period_amt for _ in range(len(self.main_window.default_weekdays))],
                    [self.main_window.default_breakperiod for _ in range(len(self.main_window.default_weekdays))],
                    self.main_window.default_weekdays
                    ],
                {}
            ])
        
        self._make_popup(_id, "Option Selector", layout, OptionsMaker, "options", button_name="Options") # type: ignore
        self._make_popup(_id, "Subjects", layout, SubjectSelection, "subjects", alignment=Qt.AlignmentFlag.AlignLeft, week_total=sum(self.main_window.school.project["levels"][index][1][1]))
    
    def popup_closed(self, _id, var_name, popup, init = False):
        super().popup_closed(_id, var_name, popup, init)
        
        if isinstance(popup, OptionsMaker):
            options_data = popup.get()
            
            if not init:
                self.main_window.subjects_widget.update_classes()
            
            removed = False
            
            for subject_id, (_, subjects_display_data) in self.info[_id]["subjects"].copy().items():
                for option_id in self.info[_id]["options"].copy():
                    if option_id not in options_data:
                        self.info[_id]["options"].pop(option_id)
                
                if not self.info[_id]["options"]:
                    removed = True
                    self.info[_id]["subjects"].pop(subject_id)
            
            self.clear_display_data_info(_id, var_name)
            
            for option_id, option_name in options_data.items():
                self.add_display_data_info(_id, var_name, option_name, option_id)
            
            if removed:
                self.clear_display_data_info(_id, "subjects")
                
                for subject_id, (subject_name, _) in self.info[_id]["subjects"].items():
                    self.add_display_data_info(_id, "subjects", subject_name, subject_id)
        elif isinstance(popup, SubjectSelection):
            self.clear_display_data_info(_id, var_name)
            
            for subject_id, (subject_name, _) in popup.get().items():
                self.add_display_data_info(_id, var_name, subject_name, subject_id)


