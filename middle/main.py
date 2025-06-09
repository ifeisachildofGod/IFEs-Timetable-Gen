# import json
# import time
import random
from typing import Union
from middle.functions import nullCheck#, display_school#, get_clashes#, get_schools_non_optimalism
from middle.objects import Teacher, Class, Subject, Timetable

PotentialOptionType = Union[
    dict[str,
         tuple[str, dict[str,
                         tuple[str, tuple[list[int], list[int], list[str]]]
                         ]
               ]
         ],
    dict[str,
         tuple[str, dict[str,
                         tuple[str, list[int]]
                         ]
               ]
         ],
    dict[str,
         tuple[str, dict[str,
                         tuple[int, int, dict[str,
                                              tuple[tuple[str, str], list[tuple[tuple[int, int], tuple[int, int]]]]
                                              ]
                               ]
                         ]
               ]
         ]
]

ProjectType = dict[str, PotentialOptionType]

class School:
    def __init__(self, project: ProjectType):
        self.classes: dict[str, Class] = {}
        self.teachers: dict[str, Teacher] = {}
        self.schoolDict: dict[Class, Timetable] = {}
        
        self.project = project
        
        self.setSchoolInfoFromProjectDict()
    
    def _findClashes(self, subject: Subject, day: str, period: int, cls: Class):
        clashes = []
        
        for ttCls, timetable in self.schoolDict.items():
            subjPeriod = 1
            for subj in timetable.table[day]:
                if  period <= subjPeriod <= period + subject.total - 1 and subject.teacher == subj.teacher and subject.teacher is not None and subj.teacher is not None and cls.uniqueID != ttCls.uniqueID:
                    clashes.append([subj, ttCls])
                subjPeriod += subj.total
        
        return clashes
    
    def _getSubjects(self, levels: list[int], classOptions: dict[str, list[str]], mappings: dict[str, dict[str, list | dict[str, list]]], classTimetableSubjectMappingCoords: dict[int, dict[str, tuple[int, int]]]):
        subjects = {}
        
        for subjectID, (subjectName, subjectInfo) in mappings.items():
            subjects[subjectID] = [subjectName, {}]
            
            for level in levels:
                teachersMapping = {}
                availableTeachers = []
                for potAvailableTeacherID, potAvailableTeacherData in subjectInfo.items():
                    if not potAvailableTeacherID.startswith("&"):
                        potAvailableTeacherName, levelsTaught = potAvailableTeacherData
                        if level in levelsTaught:
                            availableTeachers.append((potAvailableTeacherID, potAvailableTeacherName))
                
                if len(availableTeachers):
                    if random.choice([True, False, False, False, False]):
                        random.shuffle(availableTeachers)
                    
                    options = classOptions[str(level)]
                    classesOptions = subjectInfo.get("&classes")
                    if classesOptions is not None:
                        options = classesOptions.get(str(level))
                    
                    optionIndex = 0
                    for optionID in nullCheck(options, classOptions[str(level)]):
                        if optionID in classOptions[str(level)]:
                            teacherData = availableTeachers[optionIndex % len(availableTeachers)]
                            
                            coords = []
                            coordsSubjectsView = classTimetableSubjectMappingCoords.get(level)
                            if coordsSubjectsView is not None:
                                coordsSubjectTeacherView = coordsSubjectsView.get(subjectID)
                                if coordsSubjectTeacherView is not None:
                                    coords = coordsSubjectTeacherView.get(teacherData[0])
                            
                            teachersMapping[optionID] = [teacherData, coords]
                            optionIndex += 1
                    
                    timings = subjectInfo.get("&timings")[str(level)]
                    
                    subjects[subjectID][1][str(level)] = [timings[0], timings[1], teachersMapping]

        return subjects
    
    def get_clashes(self):
        clashes = {}
        
        for cls, timetable in self.schoolDict.items():
            for day, subjects in timetable.table.items():
                for subjectIndex, subject in enumerate(subjects):
                    if subject.teacher is not None:
                        period = sum([subj.total for subj in subjects[:subjectIndex]]) + 1
                        clash = self._findClashes(subject, day, period, cls)
                        if clash:
                            if clashes.get(subject) is None:
                                clashes[subject] = []
                            clashes[subject].append(clash)
                            # print()
                            # print(f"{subject.name} in {cls.name} clashes with")
                            # for clashSubject, clashCls in clash:
                            #     print(f"{clashSubject.name} in {clashCls.name}")
                            # print(f"in period {period} on {day}")
        
        return clashes
    
    def generateTimetable(self, cls: Class):
        cls.timetable.__init__(cls, cls.timetable.subjects, cls.timetable.periodsPerDay, cls.timetable.breakTimePeriods, self.schoolDict)
        cls.timetable.addFreePeriods()
        cls.timetable.generate()
    
    def generateNewSchoolTimetables(self):
        for _, cls in self.classes.items():
            self.generateTimetable(cls)
    
    def setSchoolInfoFromProjectDict(self):
        levels = [int(level) for level in self.project['levels'].keys()]
        
        classIDNameMapping = {}
        for _, (_, levelInfo) in self.project["levels"].items():
            for classID, (className, _) in levelInfo.items():
                classIDNameMapping[classID] = className
        
        classOptions = {level : [_id for _id, _ in classInfo.items()] for level, (_, classInfo) in self.project['levels'].items()}
        periods = {level : {_id: p for _id, (_, (p, _, _)) in classInfo.items()} for level, (_, classInfo) in self.project['levels'].items()}
        breakperiods = {level : {_id: b for _id, (_, (_, b, _))  in classInfo.items()} for level, (_, classInfo) in self.project['levels'].items()}
        weekdays = {level : {_id: w for _id, (_, (_, _, w))  in classInfo.items()} for level, (_, classInfo) in self.project['levels'].items()}
        levelNames = [name for name, _ in self.project['levels'].values()]
        classTimetableSubjectMappingCoords = {}
        
        subject = self.project.get("subjects")
        
        if subject is not None:
            for subjectID, (subjectName, subjectInfo) in subject.items():
                for level, (_, _, subjectLevelInfo) in subjectInfo.items():
                    for classID, ((teacherID, _), coords) in subjectLevelInfo.items():
                        if level not in classTimetableSubjectMappingCoords:
                            classTimetableSubjectMappingCoords[level] = {}
                        else:
                            if subjectID not in classTimetableSubjectMappingCoords[level]:
                                classTimetableSubjectMappingCoords[level][subjectID] = {}
                            else:
                                classTimetableSubjectMappingCoords[level][subjectID][teacherID] = coords
        
        subjects = self.project["subjects"] = nullCheck(subject, self._getSubjects(levels, classOptions, self.project["subjectTeacherMapping"], classTimetableSubjectMappingCoords))
        
        for subjectID, (subjectName, subjectInfo) in subjects.items():
            for level, (perDay, perWeek, classTeacherMapping) in subjectInfo.items():
                for classID, ((teacherID, teachersName), _) in classTeacherMapping.items():
                    uniqueClassID = classID + level
                    
                    subj = Subject(subjectID, subjectName, perDay, perWeek, None)
                    
                    teacher = self.teachers.get(teacherID)
                    if teacher is not None:
                        subj.teacher = teacher
                    else:
                        self.teachers[teacherID] = teacher = subj.teacher = Teacher(teacherID, teachersName, {subj: None}, self.teachers)
                    
                    cls = self.classes.get(uniqueClassID)
                    if cls is not None:
                        cls.subjects.append(subj)
                        cls.timetable.subjects.append(subj)
                    else:
                        self.classes[uniqueClassID] = cls = Class(int(level), classID, classIDNameMapping[classID], [subj], periods[level][classID], levelNames, self, self.schoolDict, self.teachers, self.classes, weekdays[level][classID], breakperiods[level][classID])
                    
                    teacher.subjects[subj] = cls
    
    def setProjectDictFromSchoolInfo(self):
        levels = {}
        
        class_timetable_subject_teacher_mapping_coords = {}
        for _, cls in self.classes.items():
            level = str(cls.level)
            
            timetable_subject_mapping_coords = {}
            for day_index, (_, table) in enumerate(cls.timetable.table.items()):
                period = 1
                for subject in table:
                    if subject.id not in (cls.timetable.breakPeriodID, cls.timetable.freePeriodID):
                        for _ in range(subject.total):
                            if timetable_subject_mapping_coords.get(subject.id) is None:
                                timetable_subject_mapping_coords[subject.id] = {}
                                timetable_subject_mapping_coords[subject.id][subject.teacher.id] = [[(day_index, period), (subject.total, subject.perWeek)]]
                            else:
                                timetable_subject_mapping_coords[subject.id][subject.teacher.id].append([(day_index, period), (subject.total, subject.perWeek)])
                            
                            period += 1
                
            class_timetable_subject_teacher_mapping_coords[cls.level] = timetable_subject_mapping_coords
            
            if levels.get(level) is None:
                levels[level] = [cls.namingConvention[cls.level - 1], {cls.classID: [cls.className, [cls.periodsPerDay, cls.breakTimePeriods, cls.weekdays]]}]
            else:
                levels[level][1][cls.classID] = [cls.className, [cls.periodsPerDay, cls.breakTimePeriods, cls.weekdays]]
        
        subjectTeacherMapping = {}
        for t_id, teacher in self.teachers.items():
            for subject, cls in teacher.subjects.items():
                if subjectTeacherMapping.get(subject.id) is None:
                    subjectTeacherMapping[subject.id] = [subject.name, {"&timings": {}, "&classes": {}}]
                
                if subjectTeacherMapping[subject.id][1].get(t_id) is None:
                    subjectTeacherMapping[subject.id][1][t_id] = [teacher.name, [cls.level]]
                else:
                    subjectTeacherMapping[subject.id][1][t_id][1].append(cls.level)
                
                subjectTeacherMapping[subject.id][1][t_id][1] = list(set(subjectTeacherMapping[subject.id][1][t_id][1]))
                
                if subjectTeacherMapping[subject.id][1]["&classes"].get(str(cls.level)) is None:
                    subjectTeacherMapping[subject.id][1]["&classes"][str(cls.level)] = [cls.classID]
                else:
                    subjectTeacherMapping[subject.id][1]["&classes"][str(cls.level)].append(cls.classID)
                
                subjectTeacherMapping[subject.id][1]["&classes"][str(cls.level)] = list(set(subjectTeacherMapping[subject.id][1]["&classes"][str(cls.level)]))
                
                if subjectTeacherMapping[subject.id][1]["&timings"].get(str(cls.level)) is None:
                    subjectTeacherMapping[subject.id][1]["&timings"][str(cls.level)] = [subject.TOTAL, subject.PERWEEK]
        
        for subjectID, (_, subjectInfo) in subjectTeacherMapping.items():
            for level, validClasses in {k: v for k, v in subjectInfo["&classes"].items()}.items():
                if len(validClasses) == len(levels[level][1]):
                    subjectInfo["&classes"].pop(level)
            
            if not subjectInfo["&classes"]:
                subjectInfo.pop("&classes")
        
        subjects = {}
        for _, cls in self.classes.items():
            for subject in cls.subjects:
                if subject.id not in (cls.timetable.freePeriodID, cls.timetable.breakPeriodID):
                    timetableCoords = []
                    for clsTimetableDayIndex, (_, clsTimetableSubjectsToday) in enumerate(cls.timetable.table.items()):
                        period = 1
                        for clsTimetableSubject in clsTimetableSubjectsToday:
                            if clsTimetableSubject.uniqueID == subject:
                                timetableCoords.append((clsTimetableDayIndex, period))
                            period += clsTimetableSubject.total
                    timetableCoords = []
                    
                    subjectLevelClassInfo = [(subject.teacher.id, subject.teacher.name), timetableCoords]
                    subjectLevelInfo = [subject.TOTAL, subject.PERWEEK, {cls.classID: subjectLevelClassInfo}]
                    
                    if subject.id not in subjects:
                        subjects[subject.id] = [subject.name, {str(cls.level): subjectLevelInfo}]
                    else:
                        if str(cls.level) not in subjects[subject.id][1]:
                            subjects[subject.id][1][str(cls.level)] = subjectLevelInfo
                        else:
                            subjects[subject.id][1][str(cls.level)][2][cls.classID] = subjectLevelClassInfo
        
        self.project = {
            "levels": levels, 
            "subjectTeacherMapping": subjectTeacherMapping,
            "subjects": subjects
        }
    
    def setTimetableFromProjectDict(self):
        for subjectID, (subjectName, subjectInfo) in self.project["subjects"].items():
            for level, (perDay, perWeek, classTeacherCoordsMapping) in subjectInfo.items():
                for classID, ((teacherID, _), coords) in classTeacherCoordsMapping.items():
                    for _, cls in self.classes.items():
                        teacherInClass = {teacher for teacher in cls.teachers if teacher.id == teacherID}
                        teacher = teacherInClass[0] if teacherInClass else None
                        if cls.classID == classID and teacher is not None:
                            for (dayIndex, period), (coordTotal, coordPerWeek) in coords:
                                subjectInsert = Subject(subjectID, subjectName, coordTotal, coordPerWeek, teacher)
                                subjectInsert.TOTAL = perDay
                                subjectInsert.PERWEEK = perWeek
                                
                                daysOfTheWeek = list(cls.timetable.table.keys())
                                dayPeriod = 0
                                
                                subjectInsertIndexReplacementList: list[tuple[int, Subject]] = []
                                
                                for subjectIndex, subject in enumerate(cls.timetable.table[daysOfTheWeek[dayIndex]]):
                                    dayPeriod += subject.total
                                    if period <= dayPeriod:
                                        removalAmountOnLeft = dayPeriod - period + 1
                                        removalAmountOnRight = period - removalAmountOnLeft
                                        
                                        initSubjectRemainder = removalAmountOnLeft - 1 + subjectInsert.total - subject.total
                                        
                                        subjectInsertIndexReplacementList.append((subjectIndex, subjectInsert if initSubjectRemainder >= 0 else (subjectInsert, Subject(subject.name, abs(initSubjectRemainder), subject.perWeek, subject.teacher))))
                                        
                                        subject.total -= removalAmountOnLeft
                                        
                                        for subjectToTheRight in cls.timetable.table[daysOfTheWeek[dayIndex]][subjectIndex + 1:]:
                                            if subjectToTheRight.total > removalAmountOnRight:
                                                subjectToTheRight.total -= removalAmountOnRight
                                                removalAmountOnRight = 0
                                            else:
                                                removalAmountOnRight -= subjectToTheRight.total
                                                subjectToTheRight.total = 0
                                            
                                            if removalAmountOnRight == 0:
                                                break
                                
                                for insertSubjectIndex, insertSubjectorPrevRepRemainder in subjectInsertIndexReplacementList:
                                    if isinstance(insertSubjectorPrevRepRemainder, Subject):
                                        cls.timetable.table[daysOfTheWeek[dayIndex]].insert(insertSubjectIndex + 1, insertSubjectorPrevRepRemainder)
                                    else:
                                        insertSubject, prevRemainderReplacement = insertSubjectorPrevRepRemainder
                                        
                                        cls.timetable.table[daysOfTheWeek[dayIndex]].insert(insertSubjectIndex + 1, insertSubject)
                                        cls.timetable.table[daysOfTheWeek[dayIndex]].insert(insertSubjectIndex + 2, prevRemainderReplacement)
                                
                                referenceTableList = [s for s in cls.timetable.table[daysOfTheWeek[dayIndex]]]
                                for subject in referenceTableList:
                                    if subject.total == 0:
                                        cls.timetable.table[daysOfTheWeek[dayIndex]].remove(subject)
                            
                            break
    
    # The commented functions below are to be reviewed as to whether they will be used at all or not
    
    # def updateSubject(self, className: str, day: str, subjectIndex: int, s_name: str, s_total: int, s_lockedPeriod: list[int, int] | None, s_teacher_name: int):
    #     subject = self.classes[className].timetable.table[day][subjectIndex]
    #     teacher = subject.teacher
        
    #     subject.name = s_name
    #     subject.total = s_total
    #     subject.lockedPeriod = s_lockedPeriod
        
    #     if teacher.name != s_teacher_name:
    #         self.classes[teacher.subjects.pop(subject).name].teachers.pop(teacher)
    #         teacher = self.teachers[s_teacher_name]
    
    # def updateTeacher(self, teacherName: str, t_name: str):
    #     teacher = self.teachers[teacherName]
        
    #     teacher.name = t_name
    
    # def updateClass(self, className: str, c_name: str):
    #     cls = self.classes[className]
        
    #     cls.name = c_name



# orig_time = time.time()

# with open("../res/project.json") as file:
#     project = json.load(file)

# print(f"Project loaded in {time.time() - orig_time} seconds")
# print()
# print("Generating School....")

# orig_time = time.time()

# school = School(project)

# print()
# print(f"School initialised in {time.time() - orig_time} seconds")
# print()

# orig_time = time.time()

# school.generateNewSchoolTimetables()

# print()
# print(f"School generated in {time.time() - orig_time} seconds")
# print()

# print(f"Setting project from school....")
# print()

# orig_time = time.time()

# school.setProjectDictFromSchoolInfo()

# print()
# print(f"Project set from school in {time.time() - orig_time} seconds")
# print()

# orig_time = time.time()

# school.setSchoolInfoFromProjectDict()
# school.generateNewSchoolTimetables()

# print()
# print(f"School generated in {time.time() - orig_time} seconds")
# print()

# # get_clashes(school.school)
# display_school(school.schoolDict)
