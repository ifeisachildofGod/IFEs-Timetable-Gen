# import json
import random
from typing import Union
from middle.functions import nullCheck#, display_school, get_clashes#, get_schools_non_optimalism
from middle.objects import Teacher, Class, Subject, Timetable

PotentialOptionType = Union[dict[str, list[list[str], list[int]] | dict[str, list[int] | dict[str, list[int, int] | list[int]]]], list[dict[str, dict[str, list[int, int, dict[str, str]]]]], list[str], dict[str, list[int]], dict[str, list[list[str], list[str]]]]
ProjectType = dict[str, PotentialOptionType]

class School:
    def __init__(self, project: ProjectType):
        self.school: dict[Class, Timetable] = {}
        self.classes: dict[str, Class] = {}
        self.teachers: dict[str, Teacher] = {}
        
        self.project = project
        
        self.setSchoolInfoFromProjectDict()
    
    def _findClashes(self, subject: Subject, day: str, period: int, cls: Class):
        clashes = []
        
        for ttCls, timetable in self.school.items():
            subjPeriod = 1
            for subj in timetable.table[day]:
                if  period <= subjPeriod <= period + subject.total - 1 and subject.teacher == subj.teacher and subject.teacher is not None and subj.teacher is not None and cls.name != ttCls.name:
                    clashes.append([subj, ttCls])
                subjPeriod += subj.total
        
        return clashes
    
    def _getSubjects(self, levels: list[int], classOptions: dict[str, list[str]], classes: list[str, list[str]], mappings: dict[str, dict[str, list | dict[str, list]]]):
        subjects = {}
        
        for subjectName, info in mappings.items():
            subjects[subjectName] = {}
            
            for level in levels:
                teachersMapping = {}
                availableTeachers = []
                for nameOfTeacher, levelsTaught in info.items():
                    if level in levelsTaught:
                        availableTeachers.append(nameOfTeacher)
                
                if len(availableTeachers):
                    if random.choice([True, False]):
                        random.shuffle(availableTeachers)
                    
                    options = info.get("&classes")
                    
                    if options is not None:
                        options = options.get(str(level))
                    
                    optionIndex = 0
                    for option in nullCheck(options, classOptions[str(level)]):
                        if option in classes[str(level)]:
                            teachersMapping[option] = availableTeachers[optionIndex % len(availableTeachers)]
                            optionIndex += 1
                    
                    timings = info.get("&timings")[str(level)]
                    
                    subjects[subjectName][str(level)] = [timings[0], timings[1], teachersMapping]

        return subjects
    
    def get_clashes(self):
        clashes = {}
        
        for cls, timetable in self.school.items():
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
        cls.timetable.__init__(cls, cls.timetable.subjects, cls.timetable.periodsPerDay, cls.timetable.breakTimePeriods, self.school)
        cls.timetable.addFreePeriods()
        cls.timetable.generate()
    
    def setSchoolInfoFromProjectDict(self):
        levels = [int(level) for level in self.project['levels'].keys()]
        
        classOptions = {level: list(levelInfo[0].keys()) for level, levelInfo in self.project['levels'].items()}
        
        classes = {level : list(levelInfo[0].keys()) for level, levelInfo in self.project['levels'].items()}
        periods = {level : {name: info[0] for name, info in levelInfo[0].items()} for level, levelInfo in self.project['levels'].items()}
        breakperiods = {level : {name: info[1] for name, info in levelInfo[0].items()} for level, levelInfo in self.project['levels'].items()}
        weekdays = {level : {name: info[2] for name, info in levelInfo[0].items()} for level, levelInfo in self.project['levels'].items()}
        levelNames = [levelInfo[1] for levelInfo in self.project['levels'].values()]
        
        subjects = self.project["subjects"] = nullCheck(self.project.get("subjects"), self._getSubjects(levels, classOptions, classes, self.project["subjectTeacherMapping"]))
        
        for subjectName, subjectInfo in subjects.items():
            for level, levelInfo in subjectInfo.items():
                perDay, perWeek, classTeacherMapping = levelInfo
                
                for className, teachersName in classTeacherMapping.items():
                    fullClassName = levelNames[int(level) - 1] + " " + className
                    
                    subj = Subject(subjectName, perDay, perWeek, None)
                    
                    teacher = self.teachers.get(teachersName)
                    if teacher is not None:
                        subj.teacher = teacher
                    else:
                        self.teachers[teachersName] = teacher = subj.teacher = Teacher(teachersName, {subj: None}, self.teachers)
                    
                    cls = self.classes.get(fullClassName)
                    if cls is not None:
                        cls.subjects.append(subj)
                        cls.timetable.subjects.append(subj)
                    else:
                        self.classes[fullClassName] = cls = Class(int(level), className, [subj], periods[level][className], levelNames, self.school, self.teachers, self.classes, weekdays[level][className], breakperiods[level][className])
                    
                    teacher.subjects[subj] = cls
    
    def setProjectDictFromSchoolInfo(self):
        levels = {}
        for _, cls in self.classes.items():
            level = str(cls.level)
            
            if levels.get(level) is None:
                levels[level] = [{cls.className: [cls.periodsPerDay, cls.breakTimePeriods, cls.weekdays]}, cls.namingConvention[cls.level - 1]]
            else:
                levels[level][0][cls.className] = [cls.periodsPerDay, cls.breakTimePeriods, cls.weekdays]
        
        subjectTeacherMapping = {}
        for t_name, teacher in self.teachers.items():
            for subject, cls in teacher.subjects.items():
                if subjectTeacherMapping.get(subject.name) is None:
                    subjectTeacherMapping[subject.name] = {"&timings": {}, "&classes": {}}
                
                if subjectTeacherMapping[subject.name].get(t_name) is None:
                    subjectTeacherMapping[subject.name][t_name] = [cls.level]
                else:
                    subjectTeacherMapping[subject.name][t_name].append(cls.level)
                
                subjectTeacherMapping[subject.name][t_name] = list(set(subjectTeacherMapping[subject.name][t_name]))
                
                if subjectTeacherMapping[subject.name]["&classes"].get(str(cls.level)) is None:
                    subjectTeacherMapping[subject.name]["&classes"][str(cls.level)] = [cls.className]
                else:
                    subjectTeacherMapping[subject.name]["&classes"][str(cls.level)].append(cls.className)
                
                subjectTeacherMapping[subject.name]["&classes"][str(cls.level)] = list(set(subjectTeacherMapping[subject.name]["&classes"][str(cls.level)]))
                
                if subjectTeacherMapping[subject.name]["&timings"].get(str(cls.level)) is None:
                    subjectTeacherMapping[subject.name]["&timings"][str(cls.level)] = [subject.TOTAL, subject.PERWEEK]
        
        for subjectName, subjectInfo in subjectTeacherMapping.items():
            toBePopped = []
            
            for level, validClasses in subjectInfo["&classes"].items():
                if len(validClasses) == len(levels[level][0]):
                    toBePopped.append(level)
            
            for level in toBePopped:
                subjectInfo["&classes"].pop(level)
            
            if not subjectInfo["&classes"]:
                subjectTeacherMapping[subjectName].pop("&classes")
        
        subjectLevels = [int(level) for level in levels.keys()]
        subjectClassOptions = {level: list(level_info.keys()) for level, (level_info, _) in levels.items()}
        subjectClasses = {level : levelInfo[0] for level, levelInfo in levels.items()}
        
        subjects = self._getSubjects(subjectLevels, subjectClassOptions, subjectClasses, subjectTeacherMapping)
        
        self.project = {
            "levels": levels, 
            "subjectTeacherMapping": subjectTeacherMapping,
            "subjects": subjects
        }
    
    def generateNewSchoolTimetables(self):
        for _, cls in self.classes.items():
            self.generateTimetable(cls)
    
    def updateSubject(self, className: str, day: str, subjectIndex: int, s_name: str, s_total: int, s_lockedPeriod: list[int, int] | None, s_teacher_name: int):
        subject = self.classes[className].timetable.table[day][subjectIndex]
        teacher = subject.teacher
        
        subject.name = s_name
        subject.total = s_total
        subject.lockedPeriod = s_lockedPeriod
        
        if teacher.name != s_teacher_name:
            self.classes[teacher.subjects.pop(subject).name].teachers.pop(teacher)
            teacher = self.teachers[s_teacher_name]
    
    def updateTeacher(self, teacherName: str, t_name: str):
        teacher = self.teachers[teacherName]
        
        teacher.name = t_name
    
    def updateClass(self, className: str, c_name: str):
        cls = self.classes[className]
        
        cls.name = c_name

# with open("res/project.json") as file:
#     project = json.load(file)

# school = School(project)

# school.setSchoolInfoFromProjectDict()

# school.generateNewSchoolTimetables()

# school.setProjectDictFromSchoolInfo()

# get_clashes(school.school)
# display_school(school.school)
