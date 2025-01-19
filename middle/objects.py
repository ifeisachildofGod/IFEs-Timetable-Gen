import random
from typing import Any

from matplotlib.cbook import flatten
from middle.constants import *
from middle.helpers import findClashes

class Subject:
    def __init__(self, name: str, total: int, perWeek: int, teacher: Any | None, schoolSubjectsList: list) -> None:
        global global_subjectID
        
        self.schoolSubjectsList = schoolSubjectsList
        
        self.schoolSubjectsList.append(self)
        
        self.id = global_subjectID
        global_subjectID += 1
        
        self.TOTAL = total
        self.PERWEEK = perWeek
        
        self.name = name
        self.total = self.TOTAL
        self.perWeek = self.PERWEEK
        self.teacher = teacher
        self.lockedPeriod = None
    
    def copy(self):
        subject = Subject(self.name, self.total, self.perWeek, self.teacher, self.schoolSubjectsList)
        subject.lockedPeriod = self.lockedPeriod
        return subject
    
    def fullReset(self):
        self.total = self.TOTAL
        self.perWeek = self.PERWEEK
    
    def resetTotal(self):
        self.total = self.TOTAL
    
    def get(self):
        return [self.name for _ in range(self.total)]
    
    def remove(self, amount):
        assert amount <= self.total, f"Invalid removal amount: {amount}, for day total: {self.total}"
        assert amount <= self.perWeek, f"Invalid removal amount: {amount}, for week total: {self.perWeek}"
        
        self.total -= amount
        self.perWeek -= amount

class Class:
    def __init__(self, level: int, className: str, subjects: list[Subject], periodsPerDay: list[int], namingConvention: list[str], school: dict, schoolTeachers: dict[str, Any], schoolClasses: dict[str, Any], schoolSubjectsList: list[Subject], schoolClassesList: list) -> None:
        self.school = school
        self.schoolSubjectsList = schoolSubjectsList
        self.schoolClassesList = schoolClassesList
        
        self.schoolClassesList.append(self)
        
        self.level = level
        self.className = className
        self.namingConvention = namingConvention
        
        self.name = self.namingConvention[self.level - 1] + " " + self.className
        self.subjects = subjects
        self.periodsPerDay = periodsPerDay
        self.teachers = {}
        
        for subjs in self.subjects:
            for _, teacher in schoolTeachers.items():
                classTaught = teacher.subjects.get(subjs)
                
                if classTaught is not None:
                    if self.name in classTaught.name:
                        self.teachers[teacher] = subjs
        
        self.breakTimePeriods = [BREAKTIMEPERIOD for _ in range(len(WEEKDAYS))]
        
        self.timetable = Timetable(self, self.subjects, self.periodsPerDay, self.breakTimePeriods, self.school, self.schoolSubjectsList)
        
        schoolClasses[self.name] = self

class Teacher:
    def __init__(self, name: str, subjects: dict[Subject, Class], schoolTeachers: dict[str, Any]) -> None:
        self.name = name
        self.subjects = subjects
        
        schoolTeachers[self.name] = self

class Timetable:
    def __init__(self, cls: Class, subjects: list[Subject], periodsPerDay: list[int], breakTimePeriod: list[int], school: dict[Class, Any], schoolSubjectsList: list[Subject]) -> None:
        global global_subjectID
        
        self.school = school
        self.schoolSubjectsList = schoolSubjectsList
        
        self.periodsPerDay = periodsPerDay
        self.breakTimePeriod = breakTimePeriod
        self.weekInfo = [[day, self.periodsPerDay[dayIndex], self.breakTimePeriod[dayIndex]] for dayIndex, day in enumerate(WEEKDAYS)]
        
        self.freePeriodAmt = max(sum(self.periodsPerDay) - (sum([subject.perWeek for subject in subjects]) + len(self.weekInfo)), 0)
        
        self.subjects = subjects
        self._subjects = [subject.copy() for subject in self.subjects]
        
        for subjectIndex, subject in enumerate(self.subjects):
            self._subjects[subjectIndex].id = subject.id
            self.schoolSubjectsList.remove(self._subjects[subjectIndex])
        
        global_subjectID -= len(self.subjects)
        
        self._perfectTimetableCounter = 0
        self._maxPerfectTimetableTries = 30
        self._foundPerfectTimeTable = False
        
        self.cls = cls
        self.table: dict[str, list[Subject]] = {day: [] for day in WEEKDAYS}
        self.remainderContent = []
        
        self.reset()
        
        random.shuffle(self._subjects)
    
    def addFreePeriods(self):
        global global_subjectID
        
        if self.freePeriodAmt:
            self.subjects.append(Subject("Free", int(sum([subject.total for subject in self.subjects]) / len(self.subjects)), self.freePeriodAmt, None, self.schoolSubjectsList))
            self._subjects.append(Subject("Free", int(sum([subject.total for subject in self.subjects]) / len(self.subjects)), self.freePeriodAmt, None, self.schoolSubjectsList))
            
            self._subjects[-1].id = self.subjects[-1].id
            self.schoolSubjectsList.pop()
            
            global_subjectID -= 1
    
    def reset(self):
        global global_subjectID
        
        for subject in self._subjects:
            subject.fullReset()
        
        self.subjects = self._subjects
        self._subjects = [subject.copy() for subject in self.subjects]
        
        for subjectIndex, subject in enumerate(self._subjects):
            subject.id = self.subjects[subjectIndex].id
            self.schoolSubjectsList.remove(subject)
        
        global_subjectID -= len(self._subjects)
        
        for subject in flatten(list(self.table.values()) + self.remainderContent):
            if subject in self.schoolSubjectsList:
                self.schoolSubjectsList.remove(subject)
        
        self.table: dict[str, list[Subject]] = {day: [] for day in WEEKDAYS}
        self.remainderContent = []
    
    def switchExtras(self, day: str, subjects: list[Subject]):
        global global_subjectID
        
        for subjectIndex, subject in enumerate(subjects):
            if subject.perWeek > subject.total:
                for timetableDay, subj in self.table.items():
                    replaced = False
                    
                    if not [True for subjInfo in subj if subjInfo.name == subject.name]:
                        subjectPeriod = sum([subjInfo.total for subjInfo in subjects[:subjectIndex]]) + 1
                        
                        for sIndex, s in enumerate(subj):
                            replacementPeriod = sum([subjInfo.total for subjInfo in subj[:sIndex]])
                            if not [True for subjInfo in subjects if subjInfo.name == s.name]\
                               and s.name != "Break" and subject.perWeek > s.total\
                               and subject.total + s.total == subject.perWeek\
                               and not findClashes(self.school, subject, timetableDay, replacementPeriod, self.cls)\
                               and not findClashes(self.school, s, day, subjectPeriod, self.cls)\
                               and not s.lockedPeriod\
                               and not subject.lockedPeriod:
                                   if subject in self.schoolSubjectsList:
                                        self.schoolSubjectsList.remove(subject)
                                   if s in self.schoolSubjectsList:
                                        self.schoolSubjectsList.remove(s)
                                   
                                   tableReplace = subject.copy()
                                   tableReplace.TOTAL = s.total
                                   tableReplace.total = tableReplace.TOTAL
                                   tableReplace.id = subject.id
                                   
                                   subjectReplace = s.copy()
                                   subjectReplace.id = s.id
                                   
                                   global_subjectID -= 2
                                   
                                   overflowReplace = subject.copy()
                                   overflowReplace.TOTAL = subject.perWeek - s.total
                                   overflowReplace.total = overflowReplace.TOTAL
                                   
                                   self.table[timetableDay][sIndex] = tableReplace
                                   subjects[subjectIndex] = subjectReplace
                                   subjects.append(overflowReplace)
                                   
                                   replaced = True
                                    
                                   if random.choice([True, False]):
                                       break
                        
                    if replaced: break
    
    def classSort(self, subjects: list[Subject], subjectDay: str):
        global global_subjectID
        
        subjectsCopy = [subject.copy() for subject in subjects]
        for subject in subjectsCopy:
            self.schoolSubjectsList.remove(subject)
        global_subjectID -= len(subjectsCopy)
        
        period = 1
        nonClashingPeriodsMapping = {}
        for subject in subjectsCopy:
            nonClash = []
            for nonClashingPeriod in range(self.periodsPerDay[WEEKDAYS.index(subjectDay)]):
                condition = not (subject.lockedPeriod[0] <= nonClashingPeriod + 1 <= subject.lockedPeriod[0] + subject.lockedPeriod[1] - 1) if subject.lockedPeriod is not None else True
                if condition:
                    if not findClashes(self.school, subject, subjectDay, nonClashingPeriod + 1, self.cls):
                        tmpSubjPeriod = 1
                        for subjIndex, subj in enumerate(subjectsCopy):
                            if nonClashingPeriod + 1 <= tmpSubjPeriod <= nonClashingPeriod + subject.total:
                                nonClash.append(subjIndex)
                            tmpSubjPeriod += subj.total
            nonClashingPeriodsMapping[subject] = list(set(nonClash))
            
            period += subject.total
        
        for subject, nonClash in sorted(nonClashingPeriodsMapping.items(), key=lambda nCInfo: len(nCInfo[1]), reverse=True):
            if nonClash:
                allNonClashes = list(nonClashingPeriodsMapping.values())
                otherNonClashes = list(flatten(allNonClashes[:allNonClashes.index(nonClash)] + allNonClashes[allNonClashes.index(nonClash) + 1:]))
                nonClashesCopy = nonClash.copy()
                for index in nonClashesCopy:
                    if index in otherNonClashes:
                        nonClashingPeriodsMapping[subject].remove(index)
        
        for subject, nonClash in nonClashingPeriodsMapping.items():
            if nonClash:
                nonClashingPeriodsMapping[subject] = random.choice(nonClash)
            else:
                nonClashingPeriodsMapping[subject] = None
        
        takenIndexes = [nonClash for _, nonClash in nonClashingPeriodsMapping.items() if nonClash is not None]
        
        for subject, nonClashingIndex in nonClashingPeriodsMapping.items():
            if not subject.lockedPeriod:
                if nonClashingIndex is not None:
                    subjects[nonClashingIndex] = subject
                else:
                    index = [i for i in range(len(subjects)) if i not in takenIndexes][0]
                    subjects[index] = subject
                    takenIndexes.append(index)
            else:
                subjects[subject.lockedPeriod[0]] = subject
    
    def generate(self):
        global global_subjectID
        
        for dayIndex, (day, periods, breakPeriod) in enumerate(self.weekInfo):
            period = 0
            
            subjects = []
            empties = []
            
            random.shuffle(self.subjects)
            
            for subject in self.subjects:
                subject.resetTotal()
            
            if dayIndex == len(self.weekInfo) - 1:
                self.switchExtras(WEEKDAYS[dayIndex], self.subjects)
            self.classSort(self.subjects, day)
            
            for subjectIndex, subject in enumerate(self.subjects):
                breakTime = False
                
                if period == periods:
                    break
                
                assert period < periods, f"Error: current period is {period} while maximum periods is {periods}"
                
                if subject.perWeek == 0:
                    empties.append(subjectIndex)
                    continue
                
                subjectAmount = None
                
                if period + 1 + subject.total > breakPeriod and period + 1 <= breakPeriod:
                    if period + 1 == breakPeriod:
                        breakTime = True
                    else:
                        subjectAmount = breakPeriod - period - 1
                elif subject.total > subject.perWeek:
                    subjectAmount =  subject.perWeek
                elif period + subject.total > periods:
                    subjectAmount =  period + subject.total - periods
                else:
                    subjectAmount = subject.total
                
                if not breakTime:
                    period += subjectAmount
                    subject.remove(subjectAmount)
                    subjects.append(Subject(subject.name, subjectAmount, subject.perWeek, subject.teacher, self.schoolSubjectsList))
                else:
                    period += 1
                    subjects.append(Subject('Break', 1, 1, None, self.schoolSubjectsList))
                    
                    self.subjects.append(subject)
                    empties.append(subjectIndex)
            
            self.table[day] = subjects
            
            tempSubjects = []
            for subjectIndex, subject in enumerate(self.subjects):
                if subjectIndex not in set(empties) and subject.perWeek > 0:
                    tempSubjects.append(subject)
                # else:
                #     self._subjects[([subj.id for subj in self.subjects]).index(subject.id)] = subject
            
            self.subjects = tempSubjects
        
        self.remainderContent = self.subjects
        
        if self._foundPerfectTimeTable:
            return
        
        if self._perfectTimetableCounter < self._maxPerfectTimetableTries:
            totalSubjectsAmt = sum(self.periodsPerDay)
            timeTableSubjectsAmt = sum([subject.perWeek for subject in self._subjects]) + len(self.weekInfo)
            totalRemainingSubjectsAmt = len(self.remainderContent)
            
            if max(timeTableSubjectsAmt - totalSubjectsAmt, 0) == totalRemainingSubjectsAmt:
                self._foundPerfectTimeTable = True
                self.school[self.cls] = self
            else:
                self._perfectTimetableCounter += 1
                self.reset()
                self.generate()
        else:
            self.school[self.cls] = self

class SeedSystem:
    def __init__(self, school: dict[Class, Timetable], schoolClasses: dict[str, Class], schoolSubjectsList: list, schoolClassesList: list):
        self.school = school
        self.schoolClasses = schoolClasses
        self.schoolSubjectsList = schoolSubjectsList
        self.schoolClassesList = schoolClassesList
        
        seedNumberOptions = ["(", "@", "*", "#", "/", "\\", ">", "["]
        self._seedNumberSep = random.choice(seedNumberOptions)
        
        self._seedSeperators = [chr(c) for c in range(65, 123) if chr(c).isalpha()] + ["|", "`", "%", "&", "!", ""]
        self._seedPartsSeperators = ["$", ")", "<", "?", ".", "+", "]", "~", "}"]
        
        assert len(self._seedSeperators) == len(set(self._seedSeperators)), f"One or more values in the general seed seperator is repeated: {sorted(self._seedSeperators)}"
        assert len(self._seedPartsSeperators) == len(set(self._seedPartsSeperators)), "One or more values in the seed part seperators is repeated: {sorted(self._seedPartsSeperators)}"
        assert len(self._seedPartsSeperators + self._seedSeperators) == len(set(self._seedPartsSeperators + self._seedSeperators)), f"One or more values in the seed part seperators is also in the general seed seperator: {sorted(self._seedPartsSeperators + self._seedSeperators)}"
        assert len(seedNumberOptions + self._seedSeperators) == len(set(seedNumberOptions + self._seedSeperators)), f"One or more values in the seed number seperators is repeated in the general seed seperator: {sorted(seedNumberOptions + self._seedSeperators)}"
        assert len(seedNumberOptions + self._seedPartsSeperators) == len(set(seedNumberOptions + self._seedPartsSeperators)), f"One or more values in the seed number seperators is repeated in the seed parts seperators: {sorted(seedNumberOptions + self._seedPartsSeperators)}"
    
    def _convertNumberToSeedString(self, number: int):
        num = str(number)
        
        firstChr = str(len(num))
        secondChr = num[-1]
        
        if len(num) == 1:
            return firstChr + secondChr
        
        nextChr = str(int(num[-1]) + int(num[-2]))
        thirdChr = nextChr if int(nextChr) < 10 else self._seedNumberSep + nextChr[-1]
        
        if len(num) == 2:
            return firstChr + secondChr + thirdChr
        
        fourthChr = num[-3]
        
        if len(num) == 3:
            return firstChr + secondChr + thirdChr + fourthChr
        
        fifthChr = self._convertNumberToSeedString(num[-4])
        
        if len(num) == 4:
            return firstChr + secondChr + thirdChr + fourthChr + fifthChr
        else:
            raise ValueError(f"{number} is an inappropriate value")
    
    def _convertSeedStringToNumber(self, seedNumber: str):
        length = int(seedNumber[0])
        
        firstChr = seedNumber[1]
        
        if length == 1:
            return int(firstChr)
        
        secondChr = str(int(seedNumber[2] if seedNumber[2] != self._seedNumberSep else ("1" + seedNumber[3])) - int(firstChr))
        
        if length == 2:
            return int(secondChr + firstChr)
        
        thirdChr = seedNumber[3 + seedNumber.count(self._seedNumberSep)]
        
        if length == 3:
            return int(thirdChr + secondChr + firstChr)
        
        fourthChr = str(self._convertSeedStringToNumber(seedNumber[3 + seedNumber.count(self._seedNumberSep) + 1:]))
        
        if length == 4:
            return int(fourthChr + thirdChr + secondChr + firstChr)
        else:
            raise ValueError(f"{seedNumber} is an inappropriate value")
    
    def _convertStringToSeedString(self, string: str):
        stringList = []
        for s in string:
            stringList.append(self._convertNumberToSeedString(ord(s)))
        
        seed = self._seedPartsSeperators[7].join(stringList)
        
        return seed
    
    def _convertSeedStringToString(self, seed: str):
        string = "".join([chr(self._convertSeedStringToNumber(s)) for s in seed.split(self._seedPartsSeperators[7])])
        
        return string
    
    def _convertListToSeedString(self, lst: list[int | str], sep: str):
        for value in lst:
            assert isinstance(value, (int, str))
        return sep.join([(self._convertStringToSeedString(value) if isinstance(value, str) else self._convertNumberToSeedString(value)) +  + ("i" if isinstance(value, str) else "s") for value in lst]) + self._seedPartsSeperators[8]
    
    def _convertSeedStringToList(self, seed: str, sep: str):
        seed, status = seed.split(self._seedPartsSeperators[8])
        
        return [self._convertSeedStringToString(value) if status == "i" else self._convertSeedStringToNumber(value) for value in seed.split(sep)]
    
    def generateTimetableSeed(self, timetable: Timetable):
        classIndex = self.generateClassSeed(timetable.cls) + self._seedPartsSeperators[0] + random.choice(self._seedSeperators)
        
        timetablesList = []
        for subjects in timetable.table.values():
            timetablesList.append(random.choice(self._seedSeperators) + self._seedPartsSeperators[3].join([random.choice(self._seedSeperators) + self._convertNumberToSeedString([subj.id for subj in self.schoolSubjectsList].index(subject.id)) + random.choice(self._seedSeperators) + self._seedPartsSeperators[4] + random.choice(self._seedSeperators) + str(self.schoolSubjectsList[[subj.id for subj in self.schoolSubjectsList].index(subject.id)].total) + random.choice(self._seedSeperators) + self._seedPartsSeperators[4] + random.choice(self._seedSeperators) + str(self.schoolSubjectsList[[subj.id for subj in self.schoolSubjectsList].index(subject.id)].perWeek) + random.choice(self._seedSeperators) for subject in subjects]) + random.choice(self._seedSeperators))
        
        list_timetable = random.choice(self._seedSeperators) + self._seedPartsSeperators[1].join(timetablesList) + random.choice(self._seedSeperators) + self._seedPartsSeperators[1] + random.choice(self._seedSeperators)
        
        list_remainderContent = []
        for subject in timetable.remainderContent:
            if subject not in self.schoolSubjectsList:
                self.schoolSubjectsList.append(subject)
            
            list_remainderContent.append(random.choice(self._seedSeperators) + self._convertNumberToSeedString(self.schoolSubjectsList.index(subject)) + random.choice(self._seedSeperators) + self._seedPartsSeperators[5] + random.choice(self._seedSeperators) + str(subject.total) + random.choice(self._seedSeperators) + self._seedPartsSeperators[5] + random.choice(self._seedSeperators) + str(subject.perWeek) + random.choice(self._seedSeperators))
        
        list_remainderContent = random.choice(self._seedSeperators) + self._seedPartsSeperators[2].join(list_remainderContent) + random.choice(self._seedSeperators) + self._seedPartsSeperators[2] + random.choice(self._seedSeperators)
        
        seed = classIndex + list_timetable + list_remainderContent
        
        return seed
    
    def generateClassSeed(self, cls: Class):
        return random.choice(self._seedSeperators) + self._convertNumberToSeedString(self.schoolClassesList.index(cls)) + random.choice(self._seedSeperators)
    
    def generateSchoolSeed(self, school: dict[Class, Timetable]):
        return self._seedPartsSeperators[6].join([random.choice(self._seedSeperators) + self.generateTimetableSeed(timetable) + random.choice(self._seedSeperators) for timetable in school.values()])
    
    def getTimetableFromSeed(self, seed: str):
        global global_subjectID
        
        for seperators in self._seedSeperators:
            if seperators:
                seed = ", ".join(seed.split(seperators))
        
        seedInfo: list[list[str], list[str]] = []
        
        sortedSeed = "".join([val for val in seed.split(", ") if val])
        
        for seperator in self._seedPartsSeperators[:2]:
            fullList = sortedSeed.split(seperator)
            sortedSeed = fullList[-1]
            fullList.remove(sortedSeed)
            seedInfo.append(fullList)
        
        classIndex, list_timetable, list_remainderContent = seedInfo
        
        cls = self.schoolClassesList[self._convertSeedStringToNumber("".join(classIndex))]
        timetable = Timetable(cls, cls.subjects, cls.periodsPerDay, cls.breakTimePeriods)
        
        refClass = list(self.schoolClasses.values())[[cls.level for cls in list(self.schoolClasses.values())].index(timetable.cls.level)]
        
        timetable.periodsPerDay = refClass.periodsPerDay.copy()
        timetable.breakTimePeriod = refClass.breakTimePeriods.copy()
        
        timetable.remainderContent = []
        for subjectIndexInfo in list_remainderContent:
            index, perDay, perWeek = subjectIndexInfo.split(self._seedPartsSeperators[5])
            
            subject = self.schoolSubjectsList[self._convertSeedStringToNumber(index)]
            subject.total = perDay
            subject.perWeek = perWeek
            
            timetable.remainderContent.append(subject)
        
        timetable.subjects = []
        timetable._subjects = []
        
        for sIs, subjectIndexesInfo in enumerate(list_timetable):
            timetable.table[WEEKDAYS[sIs]] = []
            
            for subjectInfo in subjectIndexesInfo.split(self._seedPartsSeperators[3]):
                if subjectInfo:
                    index, perDay, perWeek = subjectInfo.split(self._seedPartsSeperators[4])
                    
                    subject = self.schoolSubjectsList[self._convertSeedStringToNumber(index)]
                    
                    subject.total = int(perDay)
                    subject.perWeek = int(perWeek)
                    
                    timetable.table[WEEKDAYS[sIs]].append(subject)
            
            timetable.subjects += timetable.table[WEEKDAYS[sIs]]
        
        for subject in timetable.subjects:
            copy = subject.copy()
            
            copy.id = subject.id
            
            self.schoolSubjectsList.remove(copy)
            timetable._subjects.append(copy)
        
        global_subjectID -= len(timetable._subjects)
        
        return timetable
    
    def getClassFromSeed(self, seed: str):
        for seperators in self._seedSeperators:
            if seperators:
                seed = ", ".join(seed.split(seperators))
        
        return self.schoolClassesList[int("".join([val for val in seed.split(", ") if val]))]
    
    def getSchoolFromSeed(self, seed: str):
        self.school.clear()
        
        for timetableSeed in seed.split(self._seedPartsSeperators[6]):
            cls = self.getClassFromSeed(timetableSeed)
            timetable = self.getTimetableFromSeed(timetableSeed)
            self.school[cls] = timetable


global_subjectID = 1
