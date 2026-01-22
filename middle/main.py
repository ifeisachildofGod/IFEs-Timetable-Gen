# import time, json, random
# from matplotlib.cbook import flatten
# from typing import Union
# from objects import *

import math
# from middle.objects import *
from dataclasses import dataclass
from periods import SubjectPeriod, BreakPeriod, FreePeriod, Teacher

# PotentialOptionType = Union[
#     dict[str,
#          tuple[str, dict[str,
#                          tuple[str, tuple[list[int], list[int], list[str]]]
#                          ]
#                ]
#          ],
#     dict[str,
#          tuple[str, dict[str,
#                          tuple[str, list[int]]
#                          ]
#                ]
#          ],
#     dict[str,
#          tuple[str, dict[str,
#                          tuple[int, int, dict[str,
#                                               tuple[str, str]
#                                               ]
#                                ]
#                          ]
#                ]
#          ]
# ]

# ProjectType = dict[str, PotentialOptionType]

# class School:
#     def __init__(self, project: ProjectType):
#         self.subjects: dict[str, SubjectType] = {}
#         self.classes: dict[str, Class] = {}
#         self.teachers: dict[str, Teacher] = {}
#         self.schoolDict: dict[Class, Timetable] = {}
        
#         self.setProjectData(project)
    
#     def _add_subject_clash(self, clashes: dict[str, dict[str, list[tuple[int, Subject, Subject]]]], s1: Subject, s2: Subject, day: str, period: int):
#         if None not in (s1.teacher, s2.teacher) and s1.teacher.id == s2.teacher.id:
#             period += 1  # Convert period index to actual period
            
#             clashing_subject_ids = (period, s1, s2)
            
#             if s1.teacher.id not in clashes:
#                 clashes[s1.teacher.id] = {}
            
#             clash_point = clashes[s1.teacher.id][day] = clashes[s1.teacher.id].get(day, [])
            
#             if next((
#                 False
#                 for p, s, ps in clash_point
#                 if (
#                     p == period
#                     and
#                     (
#                         (
#                             (ps.id == s2.id and ps.cls.uniqueID == s2.cls.uniqueID) and
#                             (s.id == s1.id and s.cls.uniqueID == s1.cls.uniqueID)
#                             ) or
#                         (
#                             (s.id == s2.id and s.cls.uniqueID == s2.cls.uniqueID) and
#                             (ps.id == s1.id and ps.cls.uniqueID == s1.cls.uniqueID)
#                             )
#                         )
#                     )
#                 ), True):
                
#                 clash_point.append(clashing_subject_ids)
    
#     def setProjectData(self, project: ProjectType):
#         self.project = project
    
#     @staticmethod
#     def placeRandomTeachers(randomTeachers: list[tuple[int, str, tuple[str, str], list[str]]]):
#         placedClassLevels = {}
        
#         for maxClasses, strClassIndex, t_data, available_options in randomTeachers:
#             classAmt = 0
#             placedSubClasses = {}
            
#             if random.choice([True, False]):
#                 random.shuffle(available_options)
            
#             for option in available_options:
#                 if classAmt >= maxClasses:
#                     break
                
#                 placedSubClasses[option] = [t_data, []]
#                 classAmt += 1
            
#             placedClassLevels[strClassIndex] = placedSubClasses
        
#         return placedClassLevels
    
#     def getClashes(self):
#         def create_ttbl_copy(ttbl: Timetable):
#             ttbl_copy = ttbl.copy()
            
#             for i in range(len(ttbl_copy.table)):
#                 ttbl_copy.correct(i)
            
#             return ttbl_copy
        
#         clashes: dict[str, dict[str, list[tuple[int, Subject, Subject]]]] = {}
        
#         school_dict_copy = {s_cls.copy(): create_ttbl_copy(s_ttbl) for s_cls, s_ttbl in self.schoolDict.items()}
        
#         for cls, timetable in school_dict_copy.items():
#             for day, subjects in timetable.table.items():
#                 Timetable.spread(subjects)
#                 for period, subject in enumerate(subjects):
#                     for sub_cls, sub_timetable in school_dict_copy.items():
#                         if sub_cls.uniqueID != cls.uniqueID:
#                             Timetable.spread(sub_timetable.table[day])
#                             possible_clash_subject = sub_timetable.table[day][period]
                            
#                             if isinstance(subject, Subject) and isinstance(possible_clash_subject, Subject):
#                                 self._add_subject_clash(clashes, subject, possible_clash_subject, day, period)
#                             elif isinstance(subject, Subject) and isinstance(possible_clash_subject, CompoundSubject):
#                                 for sub_p_subject in possible_clash_subject.subjects:
#                                     self._add_subject_clash(clashes, subject, sub_p_subject, day, period)
#                             elif isinstance(subject, CompoundSubject) and isinstance(possible_clash_subject, Subject):
#                                 for sub_subject in subject.subjects:
#                                     self._add_subject_clash(clashes, possible_clash_subject, sub_subject, day, period)
#                             elif isinstance(subject, CompoundSubject) and isinstance(possible_clash_subject, CompoundSubject):
#                                 for sub_subject in subject.subjects:
#                                     for sub_p_subject in possible_clash_subject.subjects:
#                                         self._add_subject_clash(clashes, sub_subject, sub_p_subject, day, period)
        
#         return clashes
    
#     def generateTimetable(self, cls: Class):
#         cls.timetable.reset()
#         cls.timetable.generate()
    
#     def generateNewSchoolTimetables(self):
#         for cls in self.classes.values():
#             self.generateTimetable(cls)
    
#     def createSubjectsFromSubjectTeacherMapping(self, classOptions: dict[str, list[str]], mappings: dict[str, dict[str, list | dict[str, list]]]):
#         subjects = {}
        
#         for subjectID, (subjectName, subjectInfo) in mappings.items():
#             subjectTimingMappings = subjectInfo.pop("&timings")
#             subjectClassesMappings = subjectInfo.pop("&classes", {})
            
#             subjects[subjectID] = [subjectName, {}]
            
#             selectedLevelIDs = {}
#             randomTeachers = []
#             for teacherID, (teacherName, levelIndexesMapping) in subjectInfo.items():
#                 for strClassIndex, (maxRandomClassesAmt, options) in levelIndexesMapping.items():
#                     teachersMapping = {}
#                     selectedLevelIDs[strClassIndex] = []
                    
#                     timings = subjectTimingMappings[strClassIndex]
#                     if options:
#                         for optionID in options:
#                             teachersMapping[optionID] = [[teacherID, teacherName], []]
#                             selectedLevelIDs[strClassIndex].append(optionID)
                        
#                         subjects[subjectID][1][strClassIndex] = [timings[0], timings[1], teachersMapping]
#                     else:
#                         randomTeachers.append([maxRandomClassesAmt, strClassIndex, [teacherID, teacherName], []])
                        
#                         if strClassIndex not in subjects[subjectID][1]:
#                             subjects[subjectID][1][strClassIndex] = [timings[0], timings[1], {}]
            
#             for _, strClassIndex, _, availableTeachers in randomTeachers:
#                 availableTeachers.clear()
#                 availableTeachers.extend([opt_id for opt_id in subjectClassesMappings.get(strClassIndex, classOptions[int(strClassIndex)]) if opt_id not in selectedLevelIDs[strClassIndex]])
            
#             for strClassIndex, randomSubClassTeacherData in School.placeRandomTeachers(randomTeachers).items():
#                 subjects[subjectID][1][strClassIndex][2].update(randomSubClassTeacherData)
        
#         return subjects
    
#     def setSchoolInfoFromProjectDict(self):
#         self.subjects = {}
#         self.classes = {}
#         self.teachers = {}
#         self.schoolDict = {}
        
#         classIDNameMapping = {}
#         for _, _, levelInfo in self.project['levels']:
#             for classID, className in levelInfo.items():
#                 classIDNameMapping[classID] = className
        
#         levelNames = [name for name, _, _ in self.project['levels']]
#         classOptions = [list(classInfo.keys()) for _, _, classInfo in self.project['levels']]
        
#         subjects = self.project.get("subjects")
        
#         if subjects is None:
#             subjects = self.project["subjects"] = self.createSubjectsFromSubjectTeacherMapping(classOptions, self.project["subjectTeacherMapping"])
        
#         for classIndex, classIDs in enumerate(classOptions):
#             for classID in classIDs:
#                 cls = Class(classIndex, classID, classIDNameMapping[classID], [], self.project['levels'][classIndex][1][0], levelNames, self, self.schoolDict, self.subjects, self.project['levels'][classIndex][1][2], self.project['levels'][classIndex][1][1])
#                 self.classes[cls.uniqueID] = cls
        
#         for subjectID, (subjectName, subjectInfo) in subjects.items():
#             for classIndex, (perDay, perWeek, classTeacherMapping) in subjectInfo.items():
#                 for classID, (teacherID, teachersName) in classTeacherMapping.items():
#                     teacher = self.teachers[teacherID] = self.teachers.get(teacherID, Teacher(teacherID, teachersName, []))
#                     subj = Subject(subjectID, subjectName, perDay, perWeek, teacher, cls)
#                     cls = self.classes[Class.getUniqueID(int(classIndex), classID)]
                    
#                     cls.teachers[teacher] = subj
#                     teacher.subjectIDs.append(subj.uniqueID)
#                     teacher.subjectIDs = list(set(teacher.subjectIDs))
                    
#                     cls.subjects.append(subj)
#                     cls.timetable.subjects.append(subj)
#                     cls.timetable._subjects.append(subj.copy())
                    
#                     self.subjects[subj.uniqueID] = subj
    
#     def setProjectDictFromSchoolInfo(self):
#         classLevels = []
#         for _, cls in sorted(self.classes.items(), key=(lambda c: self.classes[c[0]].index)):
#             if cls.index != len(classLevels):
#                 classLevels[cls.index][2][cls.classID] = cls.className
#             else:
#                 classLevels.append([cls.namingConvention[cls.index], [cls.periodsPerDay, cls.breakTimePeriods, cls.weekdays], {cls.classID: cls.className}])
        
#         subjectTeacherMapping = {}
#         for t_id, teacher in self.teachers.items():
#             for subjectID in teacher.subjectIDs:
#                 subject = self.subjects[subjectID]
                
#                 if subjectTeacherMapping.get(subject.id) is None:
#                     subjectTeacherMapping[subject.id] = [subject.name, {"&timings": {}, "&classes": {}}]
                
#                 maxRandomAmt = self.project["subjectTeacherMapping"][subject.id][1][t_id][1][str(subject.cls.index)][0]
                
#                 if subjectTeacherMapping[subject.id][1].get(t_id) is None:
#                     subjectTeacherMapping[subject.id][1][t_id] = [teacher.name, {str(subject.cls.index): [maxRandomAmt, [subject.cls.classID]]}]
#                 else:
#                     if subjectTeacherMapping[subject.id][1][t_id][1].get(str(subject.cls.index)) is None:
#                         subjectTeacherMapping[subject.id][1][t_id][1][str(subject.cls.index)] = [maxRandomAmt, [subject.cls.classID]]
#                     else:
#                         subjectTeacherMapping[subject.id][1][t_id][1][str(subject.cls.index)][1].append(subject.cls.classID)
                
#                 subjectTeacherMapping[subject.id][1][t_id][1][str(subject.cls.index)][1] = list(set(subjectTeacherMapping[subject.id][1][t_id][1][str(subject.cls.index)][1]))
                
#                 if subjectTeacherMapping[subject.id][1]["&classes"].get(str(subject.cls.index)) is None:
#                     subjectTeacherMapping[subject.id][1]["&classes"][str(subject.cls.index)] = [subject.cls.classID]
#                 else:
#                     subjectTeacherMapping[subject.id][1]["&classes"][str(subject.cls.index)].append(subject.cls.classID)
                
#                 subjectTeacherMapping[subject.id][1]["&classes"][str(subject.cls.index)] = list(set(subjectTeacherMapping[subject.id][1]["&classes"][str(subject.cls.index)]))
                
#                 if subjectTeacherMapping[subject.id][1]["&timings"].get(str(subject.cls.index)) is None:
#                     subjectTeacherMapping[subject.id][1]["&timings"][str(subject.cls.index)] = [subject.TOTAL, subject.PERWEEK]
        
#         for _, (_, subjectInfo) in subjectTeacherMapping.items():
#             for index, validClasses in subjectInfo["&classes"].copy().items():
#                 if len(validClasses) == len(classLevels[int(index)][1]):
#                     subjectInfo["&classes"].pop(index)
            
#             if not subjectInfo["&classes"]:
#                 subjectInfo.pop("&classes")
        
#         timetableInfo = self.project["timetableInfo"]
        
#         subjects = {}
#         for _, cls in self.classes.items():
#             for subject in cls.subjects:
#                 if subject.id not in (FREE_PERIOD_ID, BREAK_PERIOD_ID):
#                     subjectLevelClassInfo = subject.teacher.id, subject.teacher.name
#                     subjectLevelInfo = [subject.TOTAL, subject.PERWEEK, {cls.classID: subjectLevelClassInfo}]
                    
#                     if subject.id not in subjects:
#                         subjects[subject.id] = [subject.name, {str(cls.index): subjectLevelInfo}]
#                     else:
#                         if str(cls.index) not in subjects[subject.id][1]:
#                             subjects[subject.id][1][str(cls.index)] = subjectLevelInfo
#                         else:
#                             subjects[subject.id][1][str(cls.index)][2][cls.classID] = subjectLevelClassInfo
            
#             for ltd in timetableInfo["levelTimetableData"]:
#                 ltd["timetables"].clear()
            
#             if cls.index >= len(timetableInfo["levelTimetableData"]):
#                 for _ in range(cls.index - len(timetableInfo["levelTimetableData"]) + 1):
#                     timetableInfo["levelTimetableData"].append({
#                         "breakPeriod": timetableInfo["breakPeriod"],
#                         "periodAmount": timetableInfo["periodAmount"],
#                         "DOTW": timetableInfo["DOTW"],
#                         "timetables": {}
#                     })
            
#             timetable = timetableInfo["levelTimetableData"][cls.index]["timetables"]
            
#             if cls.classID not in timetable:
#                 timetable[cls.classID] = []
            
#             for day in cls.weekdays:
#                 Timetable.spread(cls.timetable.table[day])
                
#                 timetable[cls.classID].append([(subject.uniqueID, subject.total, subject.perWeek, subject.lockedPeriod) for subject in cls.timetable.table[day]])
        
#         self.project.update({
#             "levels": classLevels, 
#             "subjectTeacherMapping": subjectTeacherMapping,
#             "subjects": subjects,
#             "timetableInfo": timetableInfo
#         })
    
#     def setTimetableFromProjectDict(self):
#         for clsLvlIndex, lvlData in enumerate(self.project["timetableInfo"]["levelTimetableData"]):
#             for clsID, timetableData in lvlData["timetables"].items():
#                 cls = self.classes[Class.getUniqueID(clsLvlIndex, clsID)]
                
#                 for dayIndex, subjects in enumerate(timetableData):
#                     cls.timetable.table[cls.weekdays[dayIndex]].clear()
                    
#                     for uniqueID, total, perWeek, lockedData in subjects:
#                         if uniqueID == FREE_PERIOD_ID.upper():
#                             subject = Subject(FREE_PERIOD_ID, "Free", total, perWeek, None, cls)
#                             subject.lockedPeriod = lockedData
#                         elif uniqueID == BREAK_PERIOD_ID.upper():
#                             subject = Subject(BREAK_PERIOD_ID, "Break", total, perWeek, None, cls)
#                         else:
#                             subject = self.subjects[uniqueID].copy()
#                             subject.total = total
#                             subject.perWeek = perWeek
#                             subject.lockedPeriod = lockedData
                        
#                         cls.timetable.table[cls.weekdays[dayIndex]].append(subject)


Timetable = dict[str, list[SubjectPeriod | BreakPeriod | FreePeriod]]

@dataclass
class Class:
    id: str
    
    section_name: str
    specifier_name: str
    
    #                Period Amount  Break Period
    dotw_data: dict[str, tuple[int, int]]
    
    #           SubjectID
    subjects: dict[str, SubjectPeriod]
    
    timetable: Timetable | None = None
    
    def name(self):
        return f"{self.section_name} {self.specifier_name}"

@dataclass
class School:
    teachers: dict[str, Teacher]
    classes: dict[str, Class]
    #         Teacher ID
    teachers_c: dict[str, list[Class]]

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
                
                for s_id in cls.subjects:
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
                                
                                day_marker_mapping[marker].append(cls)
            
            # u_day_markers = set(day_markers)
            
            # if len(u_day_markers) != len(day_markers):
            #     for marker in u_day_markers:
            #         day_markers.remove(marker)
            
            #     for marker in day_markers:
            #         day, p_index = marker
                    
            #         for cls in day_marker_mapping[marker]:
            #             cls.timetable[day][p_index]
            
            t_clashes = {marker: [cls.id for cls in classes] for marker, classes in day_marker_mapping.items() if len(classes) > 1}
            
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
        
        for d_index, (day, periods) in enumerate(cls.timetable.items()):
            period_scores[day] = [0 for _ in range(len(periods))]
            
            for p_index, period in enumerate(periods):
                
                if (
                    period.id != FreePeriod.id or
                    period.id == BreakPeriod.id or
                    [p.id for p in periods].count(s_id) == freq_info[0] or
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
                            
                            if s_teacher.id == teacher.id:
                                period_scores[day][p_index] = -math.inf
                                break
                else:
                    if p_index or p_index != len(periods) - 1:
                        orig = period_scores[day][p_index]
                        
                        if p_index:
                            period_scores[day][p_index] += (periods[p_index - 1].id == s_id) * 10
                        if p_index != len(periods) - 1:
                            period_scores[day][p_index] += (periods[p_index + 1].id == s_id) * 10
                        
                        period_scores[day][p_index] += sum((p_index - s_p_index) - (s_period.freq_info[0] - periods.count(s_period)) for s_p_index, s_period in enumerate(periods) if not s_period.id in (FreePeriod.id, BreakPeriod.id)) # type: ignore
                        if period_scores[day][p_index] == orig:
                            period_scores[day][p_index] -= 20
                    
                    # p_dist_l = [abs(p_index - s_p_index) for s_p_index, s_period in enumerate(periods) if s_period.id != s_id and s_period.id != FreePeriod.id]
                    
                    # period_scores[day][p_index] += len(periods) - sum(p_dist_l) / len(p_dist_l)
                    # period_scores[day][p_index] += 0.5 / ((d_index + 1) ** 2 + (p_index + 1) ** 2)
        
        return period_scores


def _display_school(sch: School):
    for cls in sch.classes.values():
        assert cls.timetable
        
        print(cls.name())
        for day, periods in cls.timetable.items():
            print(day, end=": ")
            print(*[p.name for p in periods], sep=", ")
        print()


def parse_school_data(data: str | School):
    if isinstance(data, School):
        return data
    
    data = _substitute_context(data, "#", "\n", placeholder_func=lambda _: "")
    
    subjects_string, teachers_string, classes_string, timetable_string, dotw_string = data.split("---")

    subjects_string = subjects_string.strip()
    teachers_string = teachers_string.strip()
    classes_string = classes_string.strip()
    timetable_string = timetable_string.strip()
    dotw_string = dotw_string.strip()

    subjects = []
    for s_string in subjects_string.splitlines():
        s_string = s_string.strip()
        
        if s_string:
            subjects.append(SubjectPeriod(str(len(subjects)), s_string))
    
    teachers = {}
    for t_string in teachers_string.splitlines():
        t_string = t_string.strip()
        
        if t_string:
            name, value =  t_string.split(":")
            
            _id = str(len(teachers))
            teachers[_id] = Teacher(_id, name.strip()), tuple(int(v) - 1 for v in value.strip().split())
    
    dotw_data = {}
    for dw_string in dotw_string.splitlines():
        if dw_string:
            day, values = dw_string.split(":")
            day, values = day.strip(), values.strip()
            
            p_amt, b_p = values.split()
            
            dotw_data[day] = int(p_amt), int(b_p)
    
    sc_teachers_c = {}
    sc_classes = {}
    for c_string in classes_string.splitlines():
        c_string = c_string.strip()
        
        if c_string:
            name, value =  c_string.split(":")
            se_name, sp_name = name.strip().split()
            
            subject_mapping = {}
            
            for v in value.strip().split():
                t_index, s_index, per_day, per_week = v.split("/")
                
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
                
                subject = SubjectPeriod(r_subject.id, r_subject.name, teacher, (per_day, per_week))
                
                subject_mapping[subject.id] = subject
            
            _id = str(len(sc_classes))
            sc_classes[_id] = cls = Class(_id, se_name, sp_name, dotw_data, subject_mapping)
            
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
                        sc_classes[cls.id].timetable[list(dotw_data)[s_ttbl_i]] = [
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
    
    return School({k: v for k, (v, _) in teachers.items()}, sc_classes, sc_teachers_c)

def _substitute_context(
        text: str,
        starter: str,
        ender: str,
        info_store: list[str | Any] | None = None,
        placeholder_func: Callable[[int], str] | None = None,
        info_encoding_func: Callable[[str], Any] | None = None,
        
        strict: bool = True
    ):
    if strict:
        assert text.count(starter) == text.count(ender), "Error"
    
    enclosements_indexes = []
    
    if info_store is None:
        info_store = []
    
    placeholder_func = placeholder_func or (lambda i: f"{ {i} }")
    info_encoding_func = info_encoding_func or (lambda s: s)
    
    depth = 0
    
    prev_i = None
    for i in range(len(text)):
        c_start = text[i : i + len(starter)]
        c_end = text[i : i + len(ender)]
        
        if strict:
            if starter != ender:
                depth += (c_start == starter) - (c_end == ender)
            else:
                depth = not depth if c_start == starter else depth
            
            start_contition = c_start == starter and prev_i is None and depth == 1
            end_contition = c_end == ender and prev_i is not None and depth == 0
        else:
            start_contition = c_start == starter and prev_i is None
            end_contition = c_end == ender and prev_i is not None
        
        if start_contition:
            prev_i = i
        elif end_contition:
            enclosements_indexes.append((prev_i, i))
            prev_i = None
        
    for i, (start_index, end_index) in enumerate(reversed(enclosements_indexes)):
        value = info_encoding_func(text[start_index + len(starter) : end_index])
        
        info_store.append(value)
        
        text = _slice_text(text, start_index, end_index + len(ender), placeholder_func(info_store.index(value)))
    
    return text

def _slice_text(text: str, start: int, end: int, value: str):
    l_text = list(text)
    l_text[start : end] = value
    
    return "".join(l_text)


if __name__ == "__main__":
    with open("test_proj.txt") as file:
        data = file.read()
    
    sch = parse_school_data(data)

    print("Started Generating")
    sch.generate_timetable()
    print("Started Clash detection")
    sch.detect_clashes()
    print("Ended")
    print()
    
    _display_school(sch)


# def _display_school(school: dict[Class, Timetable], drawType: int = 1):
#     if drawType == 1:
#         for cls, timetable in school.items():
#             print(f"| {cls.name} |")
            
#             for day, todaysSubjects in timetable.table.items():
#                 subjectsContent = [[subjs.name for _ in range(subjs.total)] for subjs in todaysSubjects]
                
#                 print(day, ":", ", ".join(list(flatten(subjectsContent))))
            
#             for subject in timetable.remainderContent:
#                 index = timetable.remainderContent.index(subject)
#                 if index == 0:
#                     print()
#                     print("Extras:", end=' ')
#                 print(subject.name, subject.perWeek, end=', ' if index < len(timetable.remainderContent) - 1 else '')
            
#             print("\n")
    
#     elif drawType == 2:
#         for day in school.weekdays:
#             print()
#             print(f"| {day} |")
#             print()
#             for cls, timetable in school.items():
#                 for timetableDay, todaysSubjects in timetable.table.items():
#                     if day == timetableDay:
#                         subjectsContent = [[subjs.name for _ in range(subjs.total)] for subjs in todaysSubjects]
#                         print(f"{cls.name}: {str(subjectsContent).replace('[', '').replace(']', '').replace("'", '')}")
#                         break
    
#     elif drawType == 3:
#         clashesDict = {}
#         for day in school.weekdays:
#             clashesDict[day] = {}
#             for _, timetable in school.items():
#                 for timetableDay, todaysSubjects in timetable.table.items():
#                     if day == timetableDay:
#                         subjectsContent = []
#                         todaysSubjects
                        
#                         for subjs in todaysSubjects:
#                             subjectsContent += [subjs.name + ", " + (f"({",".join([s.name for s in subjs.subjects])})" if isinstance(subjs, CompoundSubject) else (subjs.teacher.name if subjs.teacher is not None else "null")) + ", " + timetable.cls.name for _ in range(subjs.total)]
#                             # subjectsContent += [(subjs.teacher.name if subjs.teacher is not None else None) for _ in range(subjs.total)]
#                             # print(subjs.name)
                        
#                         for subjIndex, subj in enumerate(subjectsContent):
#                             if clashesDict[day].get(subjIndex) is not None:
#                                 clashesDict[day][subjIndex].append(subj)
#                             else:
#                                 clashesDict[day][subjIndex] = [subj]
#                         break
#         for day, periodClashes in clashesDict.items():
#             print("_" * 40)
#             print(day)
#             print("_" * 40)
#             for clashIndex, clash in periodClashes.items():
#                 print()
#                 print(f"Period {clashIndex + 1}")
#                 print()
#                 print(json.dumps(clash, indent=2))

#     elif drawType == 4:
#         nonoptimaltimetable = {}
        
#         for cls, timetable in school.items():
#             totalSubjectsAmt = sum(timetable.periodsPerDay)
#             timeTableSubjectsAmt = sum([subject.perWeek for subject in timetable._subjects]) + len(timetable.weekInfo)
#             totalRemainingSubjectsAmt = len(timetable.remainderContent)
            
#             if max(timeTableSubjectsAmt - totalSubjectsAmt, 0) != totalRemainingSubjectsAmt:
#                 nonoptimaltimetable[cls] = timetable.remainderContent
#                 print(f"Couldn't get the perfect timetable combination for {timetable.cls.name} after all {timetable._perfectTimetableCounter + 1} tries")
#             else:
#                 print(f"Found the perfect time table for {timetable.cls.name} after {timetable._perfectTimetableCounter + 1} {'tries' if timetable._perfectTimetableCounter else 'try'}")
        
#         return nonoptimaltimetable

# def test():
#     orig_time = time.time()

#     with open("middle/test_project.json") as file:
#         project = json.load(file)

#     print(f"Project loaded after {time.time() - orig_time} seconds")
#     print()
    
    
#     print("-------------------------------------------")
#     print("|------TESTING SCHOOL INITIALIZATION------|")
#     print("-------------------------------------------")
    
#     print()
#     print("Initialising School....")

#     orig_time = time.time()

#     school = School(project)
#     school.setSchoolInfoFromProjectDict()
#     school.setTimetableFromProjectDict()
    
#     print()
#     print(f"School initialised after {time.time() - orig_time} seconds")
#     print()
#     print()
    
#     print("-------------------------------------------")
#     print("|--------TESTING SCHOOL GENERATION--------|")
#     print("-------------------------------------------")
    
#     orig_time = time.time()
    
#     print()
#     print("Generating School....")
    
#     school.generateNewSchoolTimetables()

#     print()
#     print(f"School generated after {time.time() - orig_time} seconds")
#     print()
#     print()
    
#     print("-------------------------------------------")
#     print("|-----TESTING PROJECTS INITIALIZATION-----|")
#     print("-------------------------------------------")
    
#     print()
#     print(f"Setting project from school....")

#     orig_time = time.time()

#     school.setProjectDictFromSchoolInfo()

#     print()
#     print(f"Project set from school after {time.time() - orig_time} seconds")
#     print()
#     print()
    
#     print("-------------------------------------------")
#     print("|---------TESTING SCHOOLS SETTING---------|")
#     print("-------------------------------------------")
    
#     print()
#     print(f"Setting school from project....")

#     orig_time = time.time()

#     school.setSchoolInfoFromProjectDict()

#     print()
#     print(f"School set from project after {time.time() - orig_time} seconds")
#     print()
#     print()
    
#     print("-------------------------------------------")
#     print("|--TESTING GENRATING SCHOOL FROM PROJECT--|")
#     print("-------------------------------------------")
    
#     print()
#     print(f"Generating school from project....")
#     orig_time = time.time()
    
#     school.generateNewSchoolTimetables()

#     print()
#     print(f"School generated after {time.time() - orig_time} seconds")
#     print()
#     print()

#     print("-------------------------------------------")
#     print("|------------DISPLAYING SCHOOL------------|")
#     print("-------------------------------------------")
    
#     print()
#     print("Displaying school....")
    
#     orig_time = time.time()
    
#     _display_school(school.schoolDict)

#     print()
#     print(f"School displayed after {time.time() - orig_time} seconds")
#     print()

# if __name__ == "__main__":
#     test()

