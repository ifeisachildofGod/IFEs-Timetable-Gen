
import math
from dataclasses import dataclass
import random
from periods import *


Timetable = dict[str, list[SubjectPeriod | CombinedSubjectPeriod | BreakPeriod | FreePeriod]]


@dataclass
class GeneratingData:
    randomize: bool
    #                             ClassID    SubjectID    Day           DayWeight  PeriodProclivity
    subject_positioning_weights: dict[str, dict[str, dict[str, tuple[float | None, int | None]]]]
    #                       SubjectID  ClassIDs
    combined_subjects: dict[list[str], list[str]]

@dataclass
class Class:
    id: str
    
    section_name: str
    specifier_name: str
    
    #                Period Amount  Break Period
    dotw_data: dict[str, tuple[int, int]]
    
    #           SubjectID
    subjects: dict[str, SubjectPeriod | CombinedSubjectPeriod]
    
    timetable: Timetable | None = None
    
    def name(self):
        return f"{self.section_name} {self.specifier_name}"

@dataclass
class School:
    subjects: dict[str, SubjectPeriod | CombinedSubjectPeriod]
    teachers: dict[str, Teacher]
    classes: dict[str, Class]
    #         Teacher ID  Classes
    teachers_c: dict[str, list[Class]]
    gen_data: GeneratingData

    def generate_timetable(self, cls_ids: list[str] | None = None):
        cls_ids = cls_ids or list(self.classes)
        
        for cls_id in cls_ids:
            cls = self.classes[cls_id]
            
            if cls.timetable is None:
                cls.timetable = {d: [FreePeriod() if i + 1 != b else BreakPeriod() for i in range(p)] for d, (p, b) in cls.dotw_data.items()}
            
            week_amt_data = {s_id: s.freq_info[1] for s_id, s in cls.subjects.items()} # type: ignore
            
            total_available_periods = sum(amt for amt, _ in cls.dotw_data.values())
            total_subj_amt = sum(list(week_amt_data.values()))
            
            assert total_available_periods > total_subj_amt, "Period slots are not enough for the amount of subjects"
            
            for s_list in cls.timetable.values():
                for s in s_list:
                    if s.id not in (FreePeriod.id, BreakPeriod.id):
                        week_amt_data[s.id] -= 1
            
            completed_ones = []
            
            while True:
                if len(completed_ones) == len(cls.subjects):
                    break
                
                cls_subject_ids = list(cls.subjects)
                
                if self.gen_data.randomize:
                    random.shuffle(cls_subject_ids) # type: ignore
                
                for s_id in cls_subject_ids:
                    if s_id in completed_ones:
                        continue
                    
                    scores = self._plane_period_scores(s_id, cls)
                    
                    selected_period = None
                    
                    max_score = -math.inf
                    for day, score in scores.items():
                        if max(score) > max_score:
                            max_score = max(score)
                            
                            selected_period = day, score.index(max_score)
                    
                    assert selected_period, scores
                    
                    day, index = selected_period
                    
                    assert cls.timetable[day][index].id == FreePeriod.id
                    
                    cls.timetable[day][index] = cls.subjects[s_id]
                    week_amt_data[s_id] -= 1
                    
                    if week_amt_data[s_id] <= 0:
                        completed_ones.append(s_id)

    def detect_clashes(self):
        clashes = {}
        
        for teacher_id, classes in self.teachers_c.items():
            teacher = self.teachers[teacher_id]
            
            day_markers = []
            day_marker_mapping = {}
            
            for cls in classes:
                assert cls.timetable
                
                for day, periods in cls.timetable.items():
                    for p_index, subject_period in enumerate(periods):
                        if subject_period.id not in (FreePeriod.id, BreakPeriod.id):
                            assert subject_period.teacher
                            
                            if teacher.id == subject_period.teacher.id:
                                marker = day, p_index
                                
                                day_markers.append(marker)
                                
                                if marker not in day_marker_mapping:
                                    day_marker_mapping[marker] = []
                                
                                day_marker_mapping[marker].append((cls, subject_period.id))
            
            # u_day_markers = set(day_markers)
            
            # if len(u_day_markers) != len(day_markers):
            #     for marker in u_day_markers:
            #         day_markers.remove(marker)
            
            #     for marker in day_markers:
            #         day, p_index = marker
                    
            #         for cls in day_marker_mapping[marker]:
            #             cls.timetable[day][p_index]
            
            t_clashes = {}
            
            l_dmm = list(day_marker_mapping.values())
            
            for marker, classes in day_marker_mapping.items():
                if len(classes) > 1:
                    for cls, sp_id in classes:
                        combined = next(
                            (
                                True 
                                for s_cls, s_sp_id in
                                l_dmm
                                if next(
                                    (
                                        True
                                        for s_list, c_list in
                                        self.gen_data.combined_subjects.items()
                                        if (sp_id in s_list and s_sp_id in s_list) and (cls.id in c_list and s_cls.id in c_list)
                                        ),
                                    False
                                    )
                                ),
                            False
                            )
                        
                        if not combined:
                            t_clashes[marker] = cls.id
            
            if t_clashes:
                clashes[teacher.id] = t_clashes
        
        return clashes
    
    def _plane_period_scores(self, s_id: str, cls: Class):
        assert cls.timetable
        assert cls.subjects[s_id].teacher
        
        period_scores: dict[str, list[int | float]] = {}
        
        teacher = cls.subjects[s_id].teacher
        freq_info = cls.subjects[s_id].freq_info
        
        assert teacher
        assert freq_info
        
        for day, periods in cls.timetable.items():
            period_scores[day] = [0 for _ in range(len(periods))]
            
            for p_index, period in enumerate(periods):
                
                if (
                    period.id != FreePeriod.id or
                    period.id == BreakPeriod.id or
                    [p.id for p in periods].count(s_id) >= freq_info[0] or
                    abs(p_index - next((p_i for p_i, p in enumerate(periods) if p.id == s_id), p_index + 1)) != 1
                    ):
                    period_scores[day][p_index] = -math.inf
                    continue
                
                for s_cls in self.classes.values():
                    if s_cls.timetable is not None:
                        s_subject = s_cls.timetable[day][p_index]
                        
                        if s_cls.id != cls.id and s_subject.id != FreePeriod.id:
                            s_teacher = s_subject.teacher
                            
                            assert s_teacher
                            
                            combined = next((
                                    True
                                    for s_list, c_list in
                                    self.gen_data.combined_subjects.items()
                                    if (s_id in s_list and s_subject.id in s_list) and (cls.id in c_list and s_cls.id in c_list)
                                    ),
                                False
                                )
                            
                            is_clashing = None
                            
                            if isinstance(s_teacher, Teacher):
                                if isinstance(teacher, Teacher):
                                    is_clashing = teacher.id == s_teacher.id
                                elif isinstance(teacher, CombinedTeacher):
                                    is_clashing = s_teacher.id in [t.id for t in teacher.teachers]
                            elif isinstance(s_teacher, CombinedTeacher):
                                if isinstance(teacher, Teacher):
                                    is_clashing = teacher.id in [t.id for t in s_teacher.teachers]
                                elif isinstance(teacher, CombinedTeacher):
                                    is_clashing = next((True for t in s_teacher.teachers if t.id in [s_t.id for s_t in teacher.teachers]), False)
                            
                            if is_clashing is None:
                                raise Exception()
                            
                            if is_clashing and not combined:
                                period_scores[day][p_index] = -math.inf
                                break
                else:
                    if p_index or p_index != len(periods) - 1:
                        orig = period_scores[day][p_index]
                        mul = freq_info[0] - [p.id for p in periods].count(s_id)
                        
                        if p_index:
                            period_scores[day][p_index] += (periods[p_index - 1].id == s_id) * mul * 10
                        if p_index != len(periods) - 1:
                            period_scores[day][p_index] += (periods[p_index + 1].id == s_id) * mul * 10
                        
                        period_scores[day][p_index] += sum((p_index - s_p_index) - (s_period.freq_info[0] - periods.count(s_period)) for s_p_index, s_period in enumerate(periods) if not s_period.id in (FreePeriod.id, BreakPeriod.id)) # type: ignore
                        if period_scores[day][p_index] == orig:
                            period_scores[day][p_index] -= 20
                    
                    period_amt, break_period = cls.dotw_data[day]
                    
                    if cls.id in self.gen_data.subject_positioning_weights:
                        cls_spw = self.gen_data.subject_positioning_weights[cls.id]
                        if s_id in cls_spw:
                            day_weight, period_proclivity = cls_spw[s_id][day]
                            
                            if day_weight is not None:
                                period_scores[day][p_index] += day_weight * 10
                            
                            if period_proclivity is not None:
                                period_scores[day][p_index] += (1 - (abs(period_proclivity - p_index) / period_amt)) * 10
                    
                    period_scores[day][p_index] += (1 - (p_index / period_amt)) * 10
                    
                    consecs = []
                    max_consec = 0
                    match_indices = [pi for pi, p in enumerate(periods) if p.id == s_id]
                    for j, i in enumerate(match_indices):
                        if j:
                            if i == match_indices[j - 1] - 1:
                                consecs.append(i)
                                continue
                            
                            if len(consecs) <= max_consec:
                                consecs = []
                            else:
                                max_consec = len(consecs)
                        else:
                            consecs.append(i)
                    
                    if consecs:
                        period_scores[day][p_index] += (1 - (abs(consecs[0] - p_index) / period_amt)) * 2
                        period_scores[day][p_index] += (1 - (abs(consecs[-1] - p_index) / period_amt)) * 20
        
        return period_scores


def _display_school(sch: School):
    for cls in sch.classes.values():
        assert cls.timetable
        
        print(cls.name())
        for day, periods in cls.timetable.items():
            print(day, end=": ")
            print(*[(p.name if not isinstance(p, CombinedSubjectPeriod) else "/".join([s.name for s in p.subjects])) for p in periods], sep=", ")
        print()

# Not yet ready
def text_from_school(school: School):
    text = ""
    
    
    # text += "\n".join([s.name for s in school.subjects.values()]) + "\n"
    
    text += "---\n"
    
    text += "\n".join([f"{school.teachers[t_id].name}: {" ".join([str(list(school.classes).index(c.id) + 1) for c in l_cls])}" for t_id, l_cls in school.teachers_c.items()]) + "\n"
    
    text += "---\n"
    
    text += "\n".join([f"{c.name()}: {" ".join([f"{list(school.teachers).index(s.teacher.id) + 1}/{school.teachers_c[s.teacher.id].index(c) + 1}/{s.freq_info[0]}/{s.freq_info[1]}" for s in c.subjects.values()])}" for c in school.classes.values()]) + "\n" # type: ignore
    
    text += "---\n"
    
    text += "\n_\n".join([" ; ".join([" ".join([("0" if s.id == FreePeriod.id else ("-1" if s.id == BreakPeriod.id else str(list(c.subjects).index(s.id) + 1))) for s in l_subj]) for l_subj in c.timetable.values()]) for c in school.classes.values()]) + "\n" # type: ignore
    
    text += "---\n"
    
    text += "\n_\n".join(["\n".join([f"{day}: {d} {w}" for day, (d, w) in c.dotw_data.items()]) for c in school.classes.values()]) + "\n"
    
    return text

def school_from_text(text: str):
    text = "\n".join(["".join(list(line)[:line.find("#")] if "#" in line else list(line)) for line in text.splitlines()])
        
    subjects_string, teachers_string, classes_string, timetable_string, dotw_string = text.split("---")

    subjects_string = subjects_string.strip()
    teachers_string = teachers_string.strip()
    classes_string = classes_string.strip()
    timetable_string = timetable_string.strip()
    dotw_string = dotw_string.strip()

    subjects = []
    for s_string in subjects_string.splitlines():
        s_string = s_string.strip()
        
        if s_string:
            s_id = str(len(subjects))
            
            subjects.append(
                CombinedSubjectPeriod(s_id, [subjects[int(s.strip()) - 1] for s in s_string.strip().split("/")])
                if "/" in s_string else
                SubjectPeriod(s_id, s_string)
            )
    
    teachers = {}
    for t_string in teachers_string.splitlines():
        t_string = t_string.strip()
        
        if t_string:
            name, value =  t_string.split(":")
            
            t_id = str(len(teachers))
            
            teachers[t_id] = (
                    CombinedTeacher(t_id, [list([t for t, _ in teachers.values()])[int(s.strip()) - 1] for s in name.strip().split("/")])
                    if "/" in name else
                    Teacher(t_id, name.strip())
                ), tuple(int(v) - 1 for v in value.strip().split())
    
    dotw_data = []
    for dw_string in dotw_string.split("_"):
        s_dotw_data = {}
        
        for s_dw_string in dw_string.splitlines():
            s_dw_string = s_dw_string.strip()
            
            if s_dw_string:
                day, values = s_dw_string.split(":")
                day, values = day.strip(), values.strip()
                
                p_amt, b_p = values.split()
                
                s_dotw_data[day] = int(p_amt), int(b_p)
        
        dotw_data.append(s_dotw_data)
    
    sc_classes = {}
    sc_teachers_c = {}
    for c_index, c_string in enumerate(classes_string.splitlines()):
        c_string = c_string.strip()
        
        name, value =  c_string.split(":")
        se_name, sp_name = name.strip().split()
        
        subject_mapping = {}
        
        for v in value.strip().split():
            s_list = v.split("/")
            
            if len(s_list) == 3:
                t_index, per_day, per_week = s_list
                s_index = "1"
            elif len(s_list) == 4:
                t_index, s_index, per_day, per_week = s_list
            else:
                raise Exception()
            
            l_teachers = list(teachers.values())
            
            t_index = int(t_index.strip()) - 1
            s_index = int(s_index.strip()) - 1
            per_day = int(per_day)
            per_week = int(per_week)
            
            if not (0 <= t_index <= len(l_teachers) - 1):
                raise IndexError(f"Invalid teacher index: {t_index + 1}")
            
            teacher, subject_indices = l_teachers[t_index]
            
            if not (0 <= s_index <= len(subject_indices) - 1):
                raise IndexError(f"Invalid teacher-subject index: {s_index + 1}")
            
            if not (0 <= subject_indices[s_index] <= len(subjects) - 1):
                raise IndexError(f"Invalid subject index: {subject_indices[s_index] + 1}")
            
            r_subject = subjects[subject_indices[s_index]]
            
            if isinstance(r_subject, SubjectPeriod) and isinstance(teacher, Teacher):
                subject = SubjectPeriod(r_subject.id, r_subject.name, teacher, (per_day, per_week))
            elif isinstance(r_subject, CombinedSubjectPeriod) and isinstance(teacher, CombinedTeacher):
                subject = CombinedSubjectPeriod(r_subject.id, r_subject.subjects, teacher, (per_day, per_week))
            else:
                raise Exception()
            
            subject_mapping[subject.id] = subject
        
        _id = str(len(sc_classes))
        sc_classes[_id] = cls = Class(_id, se_name, sp_name, dotw_data[c_index], subject_mapping)
        
        for subj in subject_mapping.values():
            if subj.teacher.id not in sc_teachers_c:
                sc_teachers_c[subj.teacher.id] = []
            
            if cls in sc_teachers_c[subj.teacher.id]:
                continue
            
            sc_teachers_c[subj.teacher.id].append(cls)
    
    if timetable_string:
        for cls_i, ttbl_string in enumerate(timetable_string.split("_")):
            cls = list(sc_classes.values())[cls_i]
            
            ttbl_string = ttbl_string.strip()
            
            if ttbl_string:
                sc_classes[cls.id].timetable = {}
                
                for s_ttbl_i, s_ttbl_string in enumerate(ttbl_string.strip().split(";")):
                    s_ttbl_string = s_ttbl_string.strip()
                    
                    if s_ttbl_string:
                        sc_classes[cls.id].timetable[list(dotw_data[cls_i])[s_ttbl_i]] = [
                            (
                                FreePeriod()
                                if int(s.strip()) == 0 else
                                (
                                    BreakPeriod()
                                    if int(s.strip()) == -1 else
                                    list(cls.subjects.values())[int(s.strip()) - 1]
                                )
                            )
                            for s in
                            s_ttbl_string.split()
                        ]
            else:
                sc_classes[cls.id].timetable = None
    
    return School({s.id: s for s in subjects}, {k: v for k, (v, _) in teachers.items()}, sc_classes, sc_teachers_c, GeneratingData(False, {}, {}))



if __name__ == "__main__":
    with open("backend/test_proj.txt") as file:
        data = file.read()
    
    sch = school_from_text(data)
    
    print("Started Generating")
    sch.generate_timetable()
    print("Started Clash detection")
    sch.detect_clashes()
    print("Ended")
    print()
    
    _display_school(sch)

