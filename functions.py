
import random
from helpers import nullCheck

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

