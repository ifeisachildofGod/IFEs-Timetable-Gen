import time
import json
import random
from typing import Union
from matplotlib.cbook import flatten

if __name__ == "__main__":
    from objects import *
else:
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
    
    def _nullCheck(self, value, null_replacement):
        if value is None:
            return null_replacement
        return value
    
    def _getSubjects(self, classOptions: dict[str, list[str]], mappings: dict[str, dict[str, list | dict[str, list]]], classTimetableSubjectMappingCoords: dict[int, dict[str, tuple[int, int]]]):
        subjects = {}
        
        for subjectID, (subjectName, subjectInfo) in mappings.items():
            subjects[subjectID] = [subjectName, {}]
            
            for index in range(len(classOptions)):
                teachersMapping = {}
                availableTeachers = []
                for potAvailableTeacherID, potAvailableTeacherData in subjectInfo.items():
                    if not potAvailableTeacherID.startswith("&"):
                        potAvailableTeacherName, indexOfClassLevelsTaught = potAvailableTeacherData
                        if index in indexOfClassLevelsTaught:
                            availableTeachers.append((potAvailableTeacherID, potAvailableTeacherName))
                
                if len(availableTeachers):
                    if random.choice([True, False, False, False, False]):
                        random.shuffle(availableTeachers)
                    
                    options = classOptions[index]
                    classesOptions = subjectInfo.get("&classes")
                    if classesOptions is not None:
                        options = classesOptions.get(str(index))
                    
                    optionIndex = 0
                    for optionID in self._nullCheck(options, classOptions[index]):
                        if optionID in classOptions[index]:
                            teacherData = availableTeachers[optionIndex % len(availableTeachers)]
                            
                            coords = []
                            coordsSubjectsView = classTimetableSubjectMappingCoords.get(index)
                            if coordsSubjectsView is not None:
                                coordsSubjectTeacherView = coordsSubjectsView.get(subjectID)
                                if coordsSubjectTeacherView is not None:
                                    coords = coordsSubjectTeacherView.get(teacherData[0])
                            
                            teachersMapping[optionID] = [teacherData, coords]
                            optionIndex += 1
                    
                    timings = subjectInfo.get("&timings")[str(index)]
                    
                    subjects[subjectID][1][str(index)] = [timings[0], timings[1], teachersMapping]

        return subjects
    
    def findClashes(self, subject: Subject, day: str, period: int, cls: Class):
        clashes = []
        
        for ttCls, timetable in self.schoolDict.items():
            subjPeriod = 1
            for subj in timetable.table[day]:
                if  period <= subjPeriod <= period + subject.total - 1 and subject.teacher == subj.teacher and subject.teacher is not None and subj.teacher is not None and cls.uniqueID != ttCls.uniqueID:
                    clashes.append([subj, ttCls])
                subjPeriod += subj.total
        
        return clashes
    
    def getClashes(self):
        clashes = {}
        
        for cls, timetable in self.schoolDict.items():
            for day, subjects in timetable.table.items():
                for subjectIndex, subject in enumerate(subjects):
                    if subject.teacher is not None:
                        period = sum([subj.total for subj in subjects[:subjectIndex]]) + 1
                        clash = self.findClashes(subject, day, period, cls)
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
        classIDNameMapping = {}
        for _, levelInfo in self.project['levels']:
            for classID, (className, _) in levelInfo.items():
                classIDNameMapping[classID] = className
        
        classOptions = [[_id for _id, _ in classInfo.items()] for _, classInfo in self.project['levels']]
        periods = [{_id: p for _id, (_, (p, _, _)) in classInfo.items()} for _, classInfo in self.project['levels']]
        breakperiods = [{_id: b for _id, (_, (_, b, _))  in classInfo.items()} for _, classInfo in self.project['levels']]
        weekdays = [{_id: w for _id, (_, (_, _, w))  in classInfo.items()} for _, classInfo in self.project['levels']]
        levelNames = [name for name, _ in self.project['levels']]
        
        classTimetableSubjectMappingCoords = {}
        
        subject = self.project.get("subjects")
        if subject is not None:
            for subjectID, (subjectName, subjectInfo) in subject.items():
                for index, (_, _, subjectLevelInfo) in subjectInfo.items():
                    for classID, ((teacherID, _), coords) in subjectLevelInfo.items():
                        if index not in classTimetableSubjectMappingCoords:
                            classTimetableSubjectMappingCoords[index] = {}
                        else:
                            if subjectID not in classTimetableSubjectMappingCoords[index]:
                                classTimetableSubjectMappingCoords[index][subjectID] = {}
                            else:
                                classTimetableSubjectMappingCoords[index][subjectID][teacherID] = coords
        
        subjects = self.project["subjects"] = self._nullCheck(subject, self._getSubjects(classOptions, self.project["subjectTeacherMapping"], classTimetableSubjectMappingCoords))
        
        for subjectID, (subjectName, subjectInfo) in subjects.items():
            for index, (perDay, perWeek, classTeacherMapping) in subjectInfo.items():
                for classID, ((teacherID, teachersName), _) in classTeacherMapping.items():
                    index = int(index)
                    
                    subj = Subject(subjectID, subjectName, perDay, perWeek, None)
                    
                    teacher = self.teachers.get(teacherID)
                    if teacher is not None:
                        subj.teacher = teacher
                    else:
                        self.teachers[teacherID] = teacher = subj.teacher = Teacher(teacherID, teachersName, {subj: None}, self.teachers)
                    
                    new_cls = Class(index, classID, classIDNameMapping[classID], [subj], periods[index][classID], levelNames, self, self.schoolDict, self.teachers, weekdays[index][classID], breakperiods[index][classID])
                    cls = self.classes.get(new_cls.uniqueID)
                    if cls is not None:
                        cls.subjects.append(subj)
                        cls.timetable.subjects.append(subj)
                    else:
                        self.classes[new_cls.uniqueID] = cls = new_cls
                    
                    teacher.subjects[subj] = cls
    
    def setProjectDictFromSchoolInfo(self):
        classLevels = []
        
        class_timetable_subject_teacher_mapping_coords = {}
        for _, cls in sorted(self.classes.items(), key=(lambda c: self.classes[c[0]].index)):
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
                
            class_timetable_subject_teacher_mapping_coords[cls.index] = timetable_subject_mapping_coords
            
            if cls.index != len(classLevels):
                classLevels[cls.index][1][cls.classID] = [cls.className, [cls.periodsPerDay, cls.breakTimePeriods, cls.weekdays]]
            else:
                classLevels.append([cls.namingConvention[cls.index], {cls.classID: [cls.className, [cls.periodsPerDay, cls.breakTimePeriods, cls.weekdays]]}])
        
        subjectTeacherMapping = {}
        for t_id, teacher in self.teachers.items():
            for subject, cls in teacher.subjects.items():
                if subjectTeacherMapping.get(subject.id) is None:
                    subjectTeacherMapping[subject.id] = [subject.name, {"&timings": {}, "&classes": {}}]
                
                if subjectTeacherMapping[subject.id][1].get(t_id) is None:
                    subjectTeacherMapping[subject.id][1][t_id] = [teacher.name, [cls.index]]
                else:
                    subjectTeacherMapping[subject.id][1][t_id][1].append(cls.index)
                
                subjectTeacherMapping[subject.id][1][t_id][1] = list(set(subjectTeacherMapping[subject.id][1][t_id][1]))
                
                if subjectTeacherMapping[subject.id][1]["&classes"].get(str(cls.index)) is None:
                    subjectTeacherMapping[subject.id][1]["&classes"][str(cls.index)] = [cls.classID]
                else:
                    subjectTeacherMapping[subject.id][1]["&classes"][str(cls.index)].append(cls.classID)
                
                subjectTeacherMapping[subject.id][1]["&classes"][str(cls.index)] = list(set(subjectTeacherMapping[subject.id][1]["&classes"][str(cls.index)]))
                
                if subjectTeacherMapping[subject.id][1]["&timings"].get(str(cls.index)) is None:
                    subjectTeacherMapping[subject.id][1]["&timings"][str(cls.index)] = [subject.TOTAL, subject.PERWEEK]
        
        for subjectID, (_, subjectInfo) in subjectTeacherMapping.items():
            for index, validClasses in subjectInfo["&classes"].copy().items():
                if len(validClasses) == len(classLevels[int(index)][1]):
                    subjectInfo["&classes"].pop(index)
            
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
                        subjects[subject.id] = [subject.name, {str(cls.index): subjectLevelInfo}]
                    else:
                        if str(cls.index) not in subjects[subject.id][1]:
                            subjects[subject.id][1][str(cls.index)] = subjectLevelInfo
                        else:
                            subjects[subject.id][1][str(cls.index)][2][cls.classID] = subjectLevelClassInfo
        
        self.project = {
            'levels': classLevels, 
            "subjectTeacherMapping": subjectTeacherMapping,
            "subjects": subjects
        }
    
    def setTimetableFromProjectDict(self):
        for subjectID, (subjectName, subjectInfo) in self.project["subjects"].items():
            for _, (perDay, perWeek, classTeacherCoordsMapping) in subjectInfo.items():
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

def _display_school(school, drawType: int = 1):
    if drawType == 1:
        for cls, timetable in school.items():
            print(f"| {cls.name} |")
            
            for day, todaysSubjects in timetable.table.items():
                subjectsContent = [subjs.get() for subjs in todaysSubjects]
                
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
                        subjectsContent = [subjs.get() for subjs in todaysSubjects]
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
                            subjectsContent += [subjs.name + ", " + (subjs.teacher.name if subjs.teacher is not None else "null") + ", " + timetable.cls.name for _ in range(subjs.total)]
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

    with open("../res/project.json") as file:
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
    # get_clashes(school.school)
    _display_school(school.schoolDict)

    print()
    print(f"School displayed after {time.time() - orig_time} seconds")
    print()

if __name__ == "__main__":
    test()

