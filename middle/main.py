import json
import random
from middle.functions import nullCheck  #, display_school, get_clashes, get_schools_non_optimalism
from middle.objects import Teacher, Class, Subject, Timetable

class School:
    def __init__(self, projectPath: str):
        self.school: dict[Class, Timetable] = {}
        self.classes: dict[str, Class] = {}
        self.teachers: dict[str, Teacher] = {}
        
        self.classes_list: list[Class] = []
        self.subjects_list: list[Subject] = []
        
        with open(projectPath) as file:
            self.project: dict[str, dict[str, list[list[str], list[int]] | dict[str, list[int] | dict[str, list[int, int] | list[int]]]] | list[dict[str, dict[str, list[int, int, dict[str, str]]]]]] = json.loads(file.read())
    
    def _getSubjects(self, levels: list[int], classOptions: list[str], classes: list[str, list[str]], mappings: dict[str, dict[str, list | dict[str, list]]]):
        totalInfo = {}
        
        for subjectName, info in mappings.items():
            totalInfo[subjectName] = {}
            
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
                    
                    timings = info.get("&timings")
                    
                    optionIndex = 0
                    for option in nullCheck(options, classOptions):
                        if option in classes[str(level)]:
                            teachersMapping[option] = availableTeachers[optionIndex % len(availableTeachers)]
                            optionIndex += 1
                    
                    totalInfo[subjectName][str(level)] = [timings[str(level)][0], timings[str(level)][1], teachersMapping]

        return totalInfo

    def setSchoolInfoFromProjectDict(self):
        levels = [int(level) for level in self.project['levels'].keys()]
        
        classOptions = sorted([levelInfo[0] for levelInfo in self.project['levels'].values()], key = lambda options: len(options), reverse = True)[0]
        
        classes = {level : levelInfo[0] for level, levelInfo in self.project['levels'].items()}
        periods = {level : levelInfo[1] for level, levelInfo in self.project['levels'].items()}
        levelNames = [levelInfo[2] for _, levelInfo in self.project['levels'].items()]
        
        subjects = self.project["subjects"] = nullCheck(self.project.get('subjects'), self._getSubjects(levels, classOptions, classes, self.project["subjectTeacherMapping"]))
        
        for subjectName, subjectInfo in subjects.items():
            for level, levelInfo in subjectInfo.items():
                perDay, perWeek, classTeacherMapping = levelInfo
                
                for className, teachersName in classTeacherMapping.items():
                    fullClassName = levelNames[int(level) - 1] + " " + className
                    
                    subj = Subject(subjectName, perDay, perWeek, None, self.subjects_list)
                    
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
                        self.classes[fullClassName] = cls = Class(int(level), className, [subj], periods[level], levelNames, self.school, self.teachers, self.classes, self.subjects_list, self.classes_list)
                    
                    teacher.subjects[subj] = cls

    def setProjectDictFromSchoolInfo(self):
        levels = {}
        for _, cls in self.classes.items():
            level = str(cls.level)
            
            if levels.get(level) is None:
                levels[level] = [[cls.className], cls.periodsPerDay, cls.namingConvention[cls.level - 1]]
            else:
                levels[level][0].append(cls.className)
        
        
        subjectTeacherMapping = {}
        for t_name, teacher in self.teachers.items():
            for subject, cls in teacher.subjects.items():
                if subjectTeacherMapping.get(subject.name) is None:
                    subjectTeacherMapping[subject.name] = {"&timing": {}, "&classes": {}}
                
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
                
                if subjectTeacherMapping[subject.name]["&timing"].get(str(cls.level)) is None:
                    subjectTeacherMapping[subject.name]["&timing"][str(cls.level)] = [subject.TOTAL, subject.PERWEEK]
        
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
        subjectClassOptions = sorted([levelInfo[0] for levelInfo in levels.values()], key = lambda options: len(options), reverse = True)[0]
        subjectClasses = {level : levelInfo[0] for level, levelInfo in levels.items()}
        
        subjects = self._getSubjects(subjectLevels, subjectClassOptions, subjectClasses, subjectTeacherMapping)
        
        self.project = {"levels": levels, "subjectTeacherMapping": subjectTeacherMapping, "subjects": subjects}

    def generateNewSchoolTimetables(self):
        for _, cls in self.classes.items():
            cls.timetable.__init__(cls, cls.timetable.subjects, cls.timetable.periodsPerDay, cls.timetable.breakTimePeriod, self.school, self.subjects_list)
            cls.timetable.addFreePeriods()
            cls.timetable.generate()

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


# school = School("backend/project.json")

# school.setSchoolInfoFromProjectDict()

# school.generateNewSchoolTimetables()

# display_school(school.school)
# get_clashes(school.school)
