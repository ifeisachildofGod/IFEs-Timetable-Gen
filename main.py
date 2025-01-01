"""
{
    levels: {
        level1: [*classes, *periods],
        level2: [*classes, *periods],
        level3: [*classes, *periods],
        ...
    }
    
    subjectTeacherMapping: {
        subjectName: {
            teachersName: *levels,
            ...,
            "&timings": {
                level1: [maxPerDay, maxPerWeek],
                level2: [maxPerDay, maxPerWeek],
                level3: [maxPerDay, maxPerWeek],
                ...
            }
            ,
            &class?: {
                level1: *classes,
                level2: *classes,
                level3: *classes,
                ...
            }
        },
        ...
    }
    
    subjects?: [
        {
            name: {
                level: [
                    perDay,
                    perWeek,
                    {
                        className1: teacherName,
                        className2: teacherName,
                        className3: teacherName,
                        ...
                    }
                ],
                ...
            },
            ...
        },
        ...
    ],
}
"""


import json
from helpers import nullCheck, displayAndDebugTimetable, getSubjects, test_clashes, test_nonoptimaltimetable
from objects import Teacher, Class, Subject, TEACHERS, CLASSES, SCHOOL, Timetable, TimetableSeed

namingConvention = ["JS1", "JS2", "JS3", "SS1", "SS2", "SS3"]

with open("project.json") as file:
    project = json.loads(file.read())

def loadTimetableInfo(project: dict[str, dict[str, list[list[str], list[int]] | dict[str, list[int] | dict[str, list[int, int] | list[int]]]] | list[dict[str, dict[str, list[int, int, dict[str, str]]]]]], namingConvention: list[str]):
    levels = [int(level) for level in project['levels'].keys()]
    
    assert len(namingConvention) == len(levels), f"Naming convention is too {"short" if len(levels) > len(namingConvention) else "long"} for the level amount"
    
    classOptions = sorted([levelInfo[0] for levelInfo in project['levels'].values()], key = lambda options: len(options), reverse = True)[0]
    
    classes = {level : levelInfo[0] for level, levelInfo in project['levels'].items()}
    periods = {level : levelInfo[1] for level, levelInfo in project['levels'].items()}

    subjects = project["subjects"] = nullCheck(project.get('subjects'), getSubjects(levels, classOptions, classes, project["subjectTeacherMapping"]))
    
    for subjectName, subjectInfo in subjects.items():
        for level, levelInfo in subjectInfo.items():
            perDay, perWeek, classTeacherMapping = levelInfo
            
            for className, teachersName in classTeacherMapping.items():
                fullClassName = namingConvention[int(level) - 1] + " " + className
                
                subj = Subject(subjectName, perDay, perWeek, None)
                
                teacher = TEACHERS.get(teachersName)
                if teacher is not None:
                    subj.teacher = teacher
                else:
                    TEACHERS[teachersName] = teacher = subj.teacher = Teacher(teachersName, {subj: None})
                
                cls = CLASSES.get(fullClassName)
                if cls is not None:
                    cls.subjects.append(subj)
                    cls.timetable.subjects.append(subj)
                else:
                    CLASSES[fullClassName] = cls = Class(int(level), className, [subj], periods[level], namingConvention)
                
                teacher.subjects[subj] = cls


def generateNewTimeTable():
    for _, cls in CLASSES.items():
        cls.timetable.__init__(cls, cls.timetable.subjects, cls.timetable.periodsPerDay, cls.timetable.breakTimePeriod)
        cls.timetable.addFreePeriods()
        cls.timetable.generate()


def updateSubject(className: str, day: str, subjectIndex: int, s_name: str, s_total: int, s_lockedPeriod: list[int, int] | None, s_teacher_name: int):
    subject = CLASSES[className].timetable.table[day][subjectIndex]
    teacher = subject.teacher
    
    subject.name = s_name
    subject.total = s_total
    subject.lockedPeriod = s_lockedPeriod
    
    if teacher.name != s_teacher_name:
        CLASSES[teacher.subjects.pop(subject).name].teachers.pop(teacher)
        teacher = TEACHERS[s_teacher_name]

def updateTeacher(teacherName: str, t_name: str):
    teacher = TEACHERS[teacherName]
    
    teacher.name = t_name

def updateClass(className: str, c_name: str):
    cls = CLASSES[className]
    
    cls.name = c_name


loadTimetableInfo(project, namingConvention)

generateNewTimeTable()

displayAndDebugTimetable(SCHOOL, 0)

# test_clashes(SCHOOL)
# test_nonoptimaltimetable(SCHOOL)