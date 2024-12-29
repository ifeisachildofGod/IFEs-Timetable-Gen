import json
from constants import WEEKDAYS
import random

def getSubjects(levels: list[int], classOptions: list[str], classes: list[str, list[str]], mappings: dict[str, dict[str, list | dict[str, list]]]):
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


def findClashes(timetables, subject, day: str, period: int, cls):
    clashes = []
    
    for ttCls, timetable in timetables.items():
        subjPeriod = 1
        for subj in timetable.table[day]:
            if  period <= subjPeriod <= period + subject.total - 1 and subject.teacher == subj.teacher and subject.teacher is not None and subj.teacher is not None and cls.name != ttCls.name:
                clashes.append([subj, ttCls])
            subjPeriod += subj.total
    
    return clashes


def nullCheck(value, null_replacement):
    if value is None:
        return null_replacement
    return value


def displayAndDebugTimetable(timetables, drawType: int = 0):
    if drawType == 0:
        for cls, timetable in timetables.items():
            print(f"| {cls.name} |")
            
            for day, todaysSubjects in timetable.table.items():
                subjectsContent = [subjs.get() for subjs in todaysSubjects]
                print(day, ":", f'{subjectsContent}'.replace('[', '').replace(']', '').replace("'", ''))
            
            for subject in timetable.remainderContent:
                index = timetable.remainderContent.index(subject)
                if index == 0:
                    print()
                    print("Extras:", end=' ')
                print(subject.name, subject.perWeek, end=', ' if index < len(timetable.remainderContent) - 1 else '')
            
            print("\n")
    
    elif drawType == 1:
        for day in WEEKDAYS:
            print()
            print(f"| {day} |")
            print()
            for cls, timetable in timetables.items():
                for timetableDay, todaysSubjects in timetable.table.items():
                    if day == timetableDay:
                        subjectsContent = [subjs.get() for subjs in todaysSubjects]
                        print(f"{cls.name}: {str(subjectsContent).replace('[', '').replace(']', '').replace("'", '')}")
                        break
    
    elif drawType == 2:
        clashesDict = {}
        for day in WEEKDAYS:
            clashesDict[day] = {}
            for _, timetable in timetables.items():
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


def test_clashes(timetables):
    clashes = {}
    for cls, timetable in timetables.items():
        for day, subjects in timetable.table.items():
            for subjectIndex, subject in enumerate(subjects):
                if subject.teacher is not None:
                    period = sum([subj.total for subj in subjects[:subjectIndex]]) + 1
                    clash = findClashes(timetables, subject, day, period, cls)
                    if clash:
                        if clashes.get(subject) is None:
                            clashes[subject] = []
                        clashes[subject].append(clash)
                        
                        print()
                        print(f"{subject.name} in {cls.name} clashes with")
                        for clashSubject, clashCls in clash:
                            print(f"{clashSubject.name} in {clashCls.name}")
                        print(f"in period {period} on {day}")
    
    return clashes


def test_nonoptimaltimetable(timetables):
    nonoptimaltimetable = {}
    
    for cls, timetable in timetables.items():
        totalSubjectsAmt = sum(timetable.periodsPerDay)
        timeTableSubjectsAmt = sum([subject.perWeek for subject in timetable._subjects]) + len(timetable.weekInfo)
        totalRemainingSubjectsAmt = len(timetable.remainderContent)
        
        if max(timeTableSubjectsAmt - totalSubjectsAmt, 0) != totalRemainingSubjectsAmt:
            nonoptimaltimetable[cls] = timetable.remainderContent
            print(f"Couldn't get the perfect timetable combination for {timetable.cls.name} after all {timetable._perfectTimetableCounter + 1} tries")
        else:
            print(f"Found the perfect time table for {timetable.cls.name} after {timetable._perfectTimetableCounter + 1} {'tries' if timetable._perfectTimetableCounter else 'try'}")
    
    return nonoptimaltimetable


