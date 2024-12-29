import json
from constants import WEEKDAYS

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


