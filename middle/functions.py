import json

def findClashes(school, subject, day: str, period: int, cls):
    clashes = []
    
    for ttCls, timetable in school.items():
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


def display_school(school, drawType: int = 0):
    if drawType == 0:
        for cls, timetable in school.items():
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
    
    elif drawType == 2:
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


def get_clashes(school):
    clashes = {}
    
    for cls, timetable in school.items():
        for day, subjects in timetable.table.items():
            for subjectIndex, subject in enumerate(subjects):
                if subject.teacher is not None:
                    period = sum([subj.total for subj in subjects[:subjectIndex]]) + 1
                    clash = findClashes(school, subject, day, period, cls)
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


def get_schools_non_optimalism(school):
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


