# import time, json, random
# from matplotlib.cbook import flatten
# from typing import Union
# from objects import *

from middle.objects import *

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
                                              tuple[str, str]
                                              ]
                               ]
                         ]
               ]
         ]
]

ProjectType = dict[str, PotentialOptionType]

class School:
    def __init__(self, project: ProjectType):
        self.subjects: dict[str, SubjectType] = {}
        self.classes: dict[str, Class] = {}
        self.teachers: dict[str, Teacher] = {}
        self.schoolDict: dict[Class, Timetable] = {}
        
        self.setProjectData(project)
    
    def _add_subject_clash(self, clashes: dict[str, dict[str, list[tuple[int, Subject, Subject]]]], s1: Subject, s2: Subject, day: str, period: int):
        if None not in (s1.teacher, s2.teacher) and s1.teacher.id == s2.teacher.id:
            period += 1  # Convert period index to actual period
            
            clashing_subject_ids = (period, s1, s2)
            
            if s1.teacher.id not in clashes:
                clashes[s1.teacher.id] = {}
            
            clash_point = clashes[s1.teacher.id][day] = clashes[s1.teacher.id].get(day, [])
            
            if next((
                False
                for p, s, ps in clash_point
                if (
                    p == period
                    and
                    (
                        (
                            (ps.id == s2.id and ps.cls.uniqueID == s2.cls.uniqueID) and
                            (s.id == s1.id and s.cls.uniqueID == s1.cls.uniqueID)
                            ) or
                        (
                            (s.id == s2.id and s.cls.uniqueID == s2.cls.uniqueID) and
                            (ps.id == s1.id and ps.cls.uniqueID == s1.cls.uniqueID)
                            )
                        )
                    )
                ), True):
                
                clash_point.append(clashing_subject_ids)
    
    def setProjectData(self, project: ProjectType):
        self.project = project
    
    @staticmethod
    def placeRandomTeachers(randomTeachers: list[tuple[int, str, tuple[str, str], list[str]]]):
        placedClassLevels = {}
        
        for maxClasses, strClassIndex, t_data, available_options in randomTeachers:
            classAmt = 0
            placedSubClasses = {}
            
            if random.choice([True, False]):
                random.shuffle(available_options)
            
            for option in available_options:
                if classAmt >= maxClasses:
                    break
                
                placedSubClasses[option] = [t_data, []]
                classAmt += 1
            
            placedClassLevels[strClassIndex] = placedSubClasses
        
        return placedClassLevels
    
    def getClashes(self):
        def create_ttbl_copy(ttbl: Timetable):
            ttbl_copy = ttbl.copy()
            
            for i in range(len(ttbl_copy.table)):
                ttbl_copy.correct(i)
            
            return ttbl_copy
        
        clashes: dict[str, dict[str, list[tuple[int, Subject, Subject]]]] = {}
        
        school_dict_copy = {s_cls.copy(): create_ttbl_copy(s_ttbl) for s_cls, s_ttbl in self.schoolDict.items()}
        
        for cls, timetable in school_dict_copy.items():
            for day, subjects in timetable.table.items():
                Timetable.spread(subjects)
                for period, subject in enumerate(subjects):
                    for sub_cls, sub_timetable in school_dict_copy.items():
                        if sub_cls.uniqueID != cls.uniqueID:
                            Timetable.spread(sub_timetable.table[day])
                            possible_clash_subject = sub_timetable.table[day][period]
                            
                            if isinstance(subject, Subject) and isinstance(possible_clash_subject, Subject):
                                self._add_subject_clash(clashes, subject, possible_clash_subject, day, period)
                            elif isinstance(subject, Subject) and isinstance(possible_clash_subject, CompoundSubject):
                                for sub_p_subject in possible_clash_subject.subjects:
                                    self._add_subject_clash(clashes, subject, sub_p_subject, day, period)
                            elif isinstance(subject, CompoundSubject) and isinstance(possible_clash_subject, Subject):
                                for sub_subject in subject.subjects:
                                    self._add_subject_clash(clashes, possible_clash_subject, sub_subject, day, period)
                            elif isinstance(subject, CompoundSubject) and isinstance(possible_clash_subject, CompoundSubject):
                                for sub_subject in subject.subjects:
                                    for sub_p_subject in possible_clash_subject.subjects:
                                        self._add_subject_clash(clashes, sub_subject, sub_p_subject, day, period)
        
        return clashes
    
    def generateTimetable(self, cls: Class):
        cls.timetable.reset()
        cls.timetable.generate()
    
    def generateNewSchoolTimetables(self):
        for cls in self.classes.values():
            self.generateTimetable(cls)
    
    def createSubjectsFromSubjectTeacherMapping(self, classOptions: dict[str, list[str]], mappings: dict[str, dict[str, list | dict[str, list]]]):
        subjects = {}
        
        for subjectID, (subjectName, subjectInfo) in mappings.items():
            subjectTimingMappings = subjectInfo.pop("&timings")
            subjectClassesMappings = subjectInfo.pop("&classes", {})
            
            subjects[subjectID] = [subjectName, {}]
            
            selectedLevelIDs = {}
            randomTeachers = []
            for teacherID, (teacherName, levelIndexesMapping) in subjectInfo.items():
                for strClassIndex, (maxRandomClassesAmt, options) in levelIndexesMapping.items():
                    teachersMapping = {}
                    selectedLevelIDs[strClassIndex] = []
                    
                    timings = subjectTimingMappings[strClassIndex]
                    if options:
                        for optionID in options:
                            teachersMapping[optionID] = [[teacherID, teacherName], []]
                            selectedLevelIDs[strClassIndex].append(optionID)
                        
                        subjects[subjectID][1][strClassIndex] = [timings[0], timings[1], teachersMapping]
                    else:
                        randomTeachers.append([maxRandomClassesAmt, strClassIndex, [teacherID, teacherName], []])
                        
                        if strClassIndex not in subjects[subjectID][1]:
                            subjects[subjectID][1][strClassIndex] = [timings[0], timings[1], {}]
            
            for _, strClassIndex, _, availableTeachers in randomTeachers:
                availableTeachers.clear()
                availableTeachers.extend([opt_id for opt_id in subjectClassesMappings.get(strClassIndex, classOptions[int(strClassIndex)]) if opt_id not in selectedLevelIDs[strClassIndex]])
            
            for strClassIndex, randomSubClassTeacherData in School.placeRandomTeachers(randomTeachers).items():
                subjects[subjectID][1][strClassIndex][2].update(randomSubClassTeacherData)
        
        return subjects
    
    def setSchoolInfoFromProjectDict(self):
        self.subjects = {}
        self.classes = {}
        self.teachers = {}
        self.schoolDict = {}
        
        classIDNameMapping = {}
        for _, _, levelInfo in self.project['levels']:
            for classID, className in levelInfo.items():
                classIDNameMapping[classID] = className
        
        levelNames = [name for name, _, _ in self.project['levels']]
        classOptions = [list(classInfo.keys()) for _, _, classInfo in self.project['levels']]
        
        subjects = self.project.get("subjects")
        
        if subjects is None:
            subjects = self.project["subjects"] = self.createSubjectsFromSubjectTeacherMapping(classOptions, self.project["subjectTeacherMapping"])
        
        for classIndex, classIDs in enumerate(classOptions):
            for classID in classIDs:
                cls = Class(classIndex, classID, classIDNameMapping[classID], [], self.project['levels'][classIndex][1][0], levelNames, self, self.schoolDict, self.subjects, self.project['levels'][classIndex][1][2], self.project['levels'][classIndex][1][1])
                self.classes[cls.uniqueID] = cls
        
        for subjectID, (subjectName, subjectInfo) in subjects.items():
            for classIndex, (perDay, perWeek, classTeacherMapping) in subjectInfo.items():
                for classID, (teacherID, teachersName) in classTeacherMapping.items():
                    teacher = self.teachers[teacherID] = self.teachers.get(teacherID, Teacher(teacherID, teachersName, []))
                    subj = Subject(subjectID, subjectName, perDay, perWeek, teacher, cls)
                    cls = self.classes[Class.getUniqueID(int(classIndex), classID)]
                    
                    cls.teachers[teacher] = subj
                    teacher.subjectIDs.append(subj.uniqueID)
                    teacher.subjectIDs = list(set(teacher.subjectIDs))
                    
                    cls.subjects.append(subj)
                    cls.timetable.subjects.append(subj)
                    cls.timetable._subjects.append(subj.copy())
                    
                    self.subjects[subj.uniqueID] = subj
    
    def setProjectDictFromSchoolInfo(self):
        classLevels = []
        for _, cls in sorted(self.classes.items(), key=(lambda c: self.classes[c[0]].index)):
            if cls.index != len(classLevels):
                classLevels[cls.index][2][cls.classID] = cls.className
            else:
                classLevels.append([cls.namingConvention[cls.index], [cls.periodsPerDay, cls.breakTimePeriods, cls.weekdays], {cls.classID: cls.className}])
        
        subjectTeacherMapping = {}
        for t_id, teacher in self.teachers.items():
            for subjectID in teacher.subjectIDs:
                subject = self.subjects[subjectID]
                
                if subjectTeacherMapping.get(subject.id) is None:
                    subjectTeacherMapping[subject.id] = [subject.name, {"&timings": {}, "&classes": {}}]
                
                maxRandomAmt = self.project["subjectTeacherMapping"][subject.id][1][t_id][1][str(subject.cls.index)][0]
                
                if subjectTeacherMapping[subject.id][1].get(t_id) is None:
                    subjectTeacherMapping[subject.id][1][t_id] = [teacher.name, {str(subject.cls.index): [maxRandomAmt, [subject.cls.classID]]}]
                else:
                    if subjectTeacherMapping[subject.id][1][t_id][1].get(str(subject.cls.index)) is None:
                        subjectTeacherMapping[subject.id][1][t_id][1][str(subject.cls.index)] = [maxRandomAmt, [subject.cls.classID]]
                    else:
                        subjectTeacherMapping[subject.id][1][t_id][1][str(subject.cls.index)][1].append(subject.cls.classID)
                
                subjectTeacherMapping[subject.id][1][t_id][1][str(subject.cls.index)][1] = list(set(subjectTeacherMapping[subject.id][1][t_id][1][str(subject.cls.index)][1]))
                
                if subjectTeacherMapping[subject.id][1]["&classes"].get(str(subject.cls.index)) is None:
                    subjectTeacherMapping[subject.id][1]["&classes"][str(subject.cls.index)] = [subject.cls.classID]
                else:
                    subjectTeacherMapping[subject.id][1]["&classes"][str(subject.cls.index)].append(subject.cls.classID)
                
                subjectTeacherMapping[subject.id][1]["&classes"][str(subject.cls.index)] = list(set(subjectTeacherMapping[subject.id][1]["&classes"][str(subject.cls.index)]))
                
                if subjectTeacherMapping[subject.id][1]["&timings"].get(str(subject.cls.index)) is None:
                    subjectTeacherMapping[subject.id][1]["&timings"][str(subject.cls.index)] = [subject.TOTAL, subject.PERWEEK]
        
        for _, (_, subjectInfo) in subjectTeacherMapping.items():
            for index, validClasses in subjectInfo["&classes"].copy().items():
                if len(validClasses) == len(classLevels[int(index)][1]):
                    subjectInfo["&classes"].pop(index)
            
            if not subjectInfo["&classes"]:
                subjectInfo.pop("&classes")
        
        timetableInfo = self.project["timetableInfo"]
        
        subjects = {}
        for _, cls in self.classes.items():
            for subject in cls.subjects:
                if subject.id not in (FREE_PERIOD_ID, BREAK_PERIOD_ID):
                    subjectLevelClassInfo = subject.teacher.id, subject.teacher.name
                    subjectLevelInfo = [subject.TOTAL, subject.PERWEEK, {cls.classID: subjectLevelClassInfo}]
                    
                    if subject.id not in subjects:
                        subjects[subject.id] = [subject.name, {str(cls.index): subjectLevelInfo}]
                    else:
                        if str(cls.index) not in subjects[subject.id][1]:
                            subjects[subject.id][1][str(cls.index)] = subjectLevelInfo
                        else:
                            subjects[subject.id][1][str(cls.index)][2][cls.classID] = subjectLevelClassInfo
            
            for ltd in timetableInfo["levelTimetableData"]:
                ltd["timetables"].clear()
            
            if cls.index >= len(timetableInfo["levelTimetableData"]):
                for _ in range(cls.index - len(timetableInfo["levelTimetableData"]) + 1):
                    timetableInfo["levelTimetableData"].append({
                        "breakPeriod": timetableInfo["breakPeriod"],
                        "periodAmount": timetableInfo["periodAmount"],
                        "DOTW": timetableInfo["DOTW"],
                        "timetables": {}
                    })
            
            timetable = timetableInfo["levelTimetableData"][cls.index]["timetables"]
            
            if cls.classID not in timetable:
                timetable[cls.classID] = []
            
            for day in cls.weekdays:
                Timetable.spread(cls.timetable.table[day])
                
                timetable[cls.classID].append([(subject.uniqueID, subject.total, subject.perWeek, subject.lockedPeriod) for subject in cls.timetable.table[day]])
        
        self.project.update({
            "levels": classLevels, 
            "subjectTeacherMapping": subjectTeacherMapping,
            "subjects": subjects,
            "timetableInfo": timetableInfo
        })
    
    def setTimetableFromProjectDict(self):
        for clsLvlIndex, lvlData in enumerate(self.project["timetableInfo"]["levelTimetableData"]):
            for clsID, timetableData in lvlData["timetables"].items():
                cls = self.classes[Class.getUniqueID(clsLvlIndex, clsID)]
                
                for dayIndex, subjects in enumerate(timetableData):
                    cls.timetable.table[cls.weekdays[dayIndex]].clear()
                    
                    for uniqueID, total, perWeek, lockedData in subjects:
                        if uniqueID == FREE_PERIOD_ID.upper():
                            subject = Subject(FREE_PERIOD_ID, "Free", total, perWeek, None, cls)
                            subject.lockedPeriod = lockedData
                        elif uniqueID == BREAK_PERIOD_ID.upper():
                            subject = Subject(BREAK_PERIOD_ID, "Break", total, perWeek, None, cls)
                        else:
                            subject = self.subjects[uniqueID].copy()
                            subject.total = total
                            subject.perWeek = perWeek
                            subject.lockedPeriod = lockedData
                        
                        cls.timetable.table[cls.weekdays[dayIndex]].append(subject)

def _display_school(school: dict[Class, Timetable], drawType: int = 1):
    if drawType == 1:
        for cls, timetable in school.items():
            print(f"| {cls.name} |")
            
            for day, todaysSubjects in timetable.table.items():
                subjectsContent = [[subjs.name for _ in range(subjs.total)] for subjs in todaysSubjects]
                
                print(day, ":", ", ".join(list(flatten(subjectsContent))))
            
            for subject in timetable.remainderContent:
                index = timetable.remainderContent.index(subject)
                if index == 0:
                    print()
                    print("Extras:", end=' ')
                print(subject.name, subject.perWeek, end=', ' if index < len(timetable.remainderContent) - 1 else '')
            
            print("\n")
    
    elif drawType == 2:
        for day in school.weekdays:
            print()
            print(f"| {day} |")
            print()
            for cls, timetable in school.items():
                for timetableDay, todaysSubjects in timetable.table.items():
                    if day == timetableDay:
                        subjectsContent = [[subjs.name for _ in range(subjs.total)] for subjs in todaysSubjects]
                        print(f"{cls.name}: {str(subjectsContent).replace('[', '').replace(']', '').replace("'", '')}")
                        break
    
    elif drawType == 3:
        clashesDict = {}
        for day in school.weekdays:
            clashesDict[day] = {}
            for _, timetable in school.items():
                for timetableDay, todaysSubjects in timetable.table.items():
                    if day == timetableDay:
                        subjectsContent = []
                        todaysSubjects
                        
                        for subjs in todaysSubjects:
                            subjectsContent += [subjs.name + ", " + (f"({",".join([s.name for s in subjs.subjects])})" if isinstance(subjs, CompoundSubject) else (subjs.teacher.name if subjs.teacher is not None else "null")) + ", " + timetable.cls.name for _ in range(subjs.total)]
                            # subjectsContent += [(subjs.teacher.name if subjs.teacher is not None else None) for _ in range(subjs.total)]
                            # print(subjs.name)
                        
                        for subjIndex, subj in enumerate(subjectsContent):
                            if clashesDict[day].get(subjIndex) is not None:
                                clashesDict[day][subjIndex].append(subj)
                            else:
                                clashesDict[day][subjIndex] = [subj]
                        break
        for day, periodClashes in clashesDict.items():
            print("_" * 40)
            print(day)
            print("_" * 40)
            for clashIndex, clash in periodClashes.items():
                print()
                print(f"Period {clashIndex + 1}")
                print()
                print(json.dumps(clash, indent=2))

    elif drawType == 4:
        nonoptimaltimetable = {}
        
        for cls, timetable in school.items():
            totalSubjectsAmt = sum(timetable.periodsPerDay)
            timeTableSubjectsAmt = sum([subject.perWeek for subject in timetable._subjects]) + len(timetable.weekInfo)
            totalRemainingSubjectsAmt = len(timetable.remainderContent)
            
            if max(timeTableSubjectsAmt - totalSubjectsAmt, 0) != totalRemainingSubjectsAmt:
                nonoptimaltimetable[cls] = timetable.remainderContent
                print(f"Couldn't get the perfect timetable combination for {timetable.cls.name} after all {timetable._perfectTimetableCounter + 1} tries")
            else:
                print(f"Found the perfect time table for {timetable.cls.name} after {timetable._perfectTimetableCounter + 1} {'tries' if timetable._perfectTimetableCounter else 'try'}")
        
        return nonoptimaltimetable

def test():
    orig_time = time.time()

    with open("middle/test_project.json") as file:
        project = json.load(file)

    print(f"Project loaded after {time.time() - orig_time} seconds")
    print()
    
    
    print("-------------------------------------------")
    print("|------TESTING SCHOOL INITIALIZATION------|")
    print("-------------------------------------------")
    
    print()
    print("Initialising School....")

    orig_time = time.time()

    school = School(project)
    school.setSchoolInfoFromProjectDict()
    school.setTimetableFromProjectDict()
    
    print()
    print(f"School initialised after {time.time() - orig_time} seconds")
    print()
    print()
    
    print("-------------------------------------------")
    print("|--------TESTING SCHOOL GENERATION--------|")
    print("-------------------------------------------")
    
    orig_time = time.time()
    
    print()
    print("Generating School....")
    
    school.generateNewSchoolTimetables()

    print()
    print(f"School generated after {time.time() - orig_time} seconds")
    print()
    print()
    
    print("-------------------------------------------")
    print("|-----TESTING PROJECTS INITIALIZATION-----|")
    print("-------------------------------------------")
    
    print()
    print(f"Setting project from school....")

    orig_time = time.time()

    school.setProjectDictFromSchoolInfo()

    print()
    print(f"Project set from school after {time.time() - orig_time} seconds")
    print()
    print()
    
    print("-------------------------------------------")
    print("|---------TESTING SCHOOLS SETTING---------|")
    print("-------------------------------------------")
    
    print()
    print(f"Setting school from project....")

    orig_time = time.time()

    school.setSchoolInfoFromProjectDict()

    print()
    print(f"School set from project after {time.time() - orig_time} seconds")
    print()
    print()
    
    print("-------------------------------------------")
    print("|--TESTING GENRATING SCHOOL FROM PROJECT--|")
    print("-------------------------------------------")
    
    print()
    print(f"Generating school from project....")
    orig_time = time.time()
    
    school.generateNewSchoolTimetables()

    print()
    print(f"School generated after {time.time() - orig_time} seconds")
    print()
    print()

    print("-------------------------------------------")
    print("|------------DISPLAYING SCHOOL------------|")
    print("-------------------------------------------")
    
    print()
    print("Displaying school....")
    
    orig_time = time.time()
    
    _display_school(school.schoolDict)

    print()
    print(f"School displayed after {time.time() - orig_time} seconds")
    print()

if __name__ == "__main__":
    test()

