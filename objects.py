import random
from typing import Any

from matplotlib.cbook import flatten
from constants import *

class Subject:
    def __init__(self, name: str, total: int, perWeek: int, teacher: Any | None) -> None:
        self.TOTAL = total
        self.PERWEEK = perWeek
        
        self.name = name
        self.total = self.TOTAL
        self.perWeek = self.PERWEEK
        self.teacher = teacher
    
    def copy(self):
        return Subject(self.name, self.total, self.perWeek, self.teacher)
    
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
    def __init__(self, level: int, className: str, subjects: list[Subject], periodsPerDay: list[int], namingConvention: list[str]) -> None:
        self.name = namingConvention[level - 1] + " " + className
        self.subjects = subjects
        self.periodsPerDay = periodsPerDay
        self.teachers = {}
        
        for subjs in self.subjects:
            for _, teacher in TEACHERS.items():
                classesTaught = teacher.subjects.get(subjs)
                
                if classesTaught is not None:
                    if self.name in [cls.name for cls in classesTaught]:
                        self.teachers[teacher] = subjs
        
        self.breakTimePeriods = [BREAKTIMEPERIOD for _ in range(len(WEEKDAYS))]
        
        self.timetable = Timetable(self, self.subjects, self.periodsPerDay, self.breakTimePeriods)
        
        CLASSES[self.name] = self
    

class Teacher:
    def __init__(self, name: str, subjects: dict[Subject, list[Class]]) -> None:
        self.name = name
        self.subjects = subjects
        
        TEACHERS[self.name] = self


class Timetable:
    def __init__(self, cls: Class, subjects: list[Subject], periodsPerDay: list[int], breakTimePeriod: list[int]) -> None:
        self._subjects = subjects
        
        self._perfectTimetableCounter = 0
        self._maxPerfectTimetableTries = 30
        self._foundPerfectTimeTable = False
        
        self.cls = cls
        
        self.reset()
        
        self.periodsPerDay = periodsPerDay
        self.breakTimePeriod = breakTimePeriod
        
        self.weekInfo = [[day, self.periodsPerDay[dayIndex], self.breakTimePeriod[dayIndex]] for dayIndex, day in enumerate(WEEKDAYS)]
        
        self.freePeriodAmt = max(sum(self.periodsPerDay) - (sum([subject.perWeek for subject in self._subjects]) + len(self.weekInfo)), 0)
        if self.freePeriodAmt:
            self._subjects.append(Subject("Free", int(sum([subject.total for subject in self._subjects]) / len(self._subjects)), self.freePeriodAmt, None))
        
        random.shuffle(self._subjects)
    
    def reset(self):
        for subject in self._subjects:
            subject.fullReset()
        self.subjects = [subject.copy() for subject in self._subjects]
        
        self.table: dict[str, Subject] = {}
        self.remainderContent = []
    
    def findClashes(self, subject: Subject, day: str, period: int, cls: Class):
        clashes = []
        
        for ttCls, timetable in TIMETABLES.items():
            subjPeriod = 1
            for subj in timetable.table[day]:
                if  period <= subjPeriod <= period + subject.total - 1 and subject.teacher == subj.teacher and subject.teacher is not None and subj.teacher is not None and cls.name != ttCls.name:
                    clashes.append([subj, ttCls])
                subjPeriod += subj.total
        
        return clashes
    
    def switchExtras(self, day: str, subjects: list[Subject]):
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
                               and not self.findClashes(subject, timetableDay, replacementPeriod, self.cls)\
                               and not self.findClashes(s, day, subjectPeriod, self.cls):
                                tableReplace = subject.copy()
                                tableReplace.TOTAL = s.total
                                tableReplace.total = tableReplace.TOTAL
                                
                                subjectReplace = s.copy()
                                
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
        subjectsCopy = [subject.copy() for subject in subjects]
        
        period = 1
        nonClashingPeriodsMapping = {}
        for subject in subjectsCopy:
            nonClash = []
            for nonClashingPeriod in range(self.periodsPerDay[WEEKDAYS.index(subjectDay)]):
                if not self.findClashes(subject, subjectDay, nonClashingPeriod + 1, self.cls):
                    tmpSubjPeriod = 1
                    for subjIndex, subj in enumerate(subjectsCopy):
                        if nonClashingPeriod + 1 <= tmpSubjPeriod <= nonClashingPeriod + subject.total:
                            nonClash.append(subjIndex)
                        tmpSubjPeriod += subj.total
            nonClashingPeriodsMapping[subject] = list(set(nonClash))
            
            period += subject.total
            
            if not nonClashingPeriodsMapping[subject]:
                nonClashingPeriodsMapping[subject] = []
                
                if subject.teacher is not None:# and self.cls.name == "SS2 H":
                    print()
                    clashes = flatten([[f"{"\n" if not nonClashingPeriod else ""}{subj.name} in {cls.name} by period {nonClashingPeriod + 1}" for subj, cls in self.findClashes(subject, subjectDay, nonClashingPeriod, self.cls)] for nonClashingPeriod in range(self.periodsPerDay[WEEKDAYS.index(subjectDay)])])
                    print(f"{subject.name} in {self.cls.name} will always clash with {",\n".join(clashes) if clashes else "nothing"}")
                    print()
        
        for subject, nonClash in sorted(nonClashingPeriodsMapping.items(), key=lambda nCInfo: len(nCInfo[1]), reverse=True):
            if nonClash:
                allNonClashes = list(nonClashingPeriodsMapping.values())
                otherNonClashes = list(flatten(allNonClashes[:allNonClashes.index(nonClash)] + allNonClashes[allNonClashes.index(nonClash) + 1:]))
                nonClashesCopy = nonClash.copy()
                for index in nonClashesCopy:
                    if index in otherNonClashes:
                        nonClashingPeriodsMapping[subject].remove(index)
            else:
                pass
                # if subject.teacher is not None:
                #     print(f"{subject.name} will always clash with another subject in {self.cls.name}")
        
        for subject, nonClash in nonClashingPeriodsMapping.items():
            if nonClash:
                nonClashingPeriodsMapping[subject] = random.choice(nonClash)
            else:
                nonClashingPeriodsMapping[subject] = None
        
        takenIndexes = [nonClash for _, nonClash in nonClashingPeriodsMapping.items() if nonClash is not None]
        
        for subject, nonClashingIndex in nonClashingPeriodsMapping.items():
            if nonClashingIndex is not None:
                subjects[nonClashingIndex] = subject
            else:
                index = [i for i in range(len(subjects)) if i not in takenIndexes][0]
                subjects[index] = subject
                takenIndexes.append(index)
    
    def generate(self):
        self._subjects = [subject.copy() for subject in self.subjects]
        
        for dayIndex, (day, periods, breakPeriod) in enumerate(self.weekInfo):
            period = 0
            
            subjects = []
            empties = []
            
            random.shuffle(self.subjects)
            
            for subject in self.subjects:
                subject.resetTotal()
            
            self.classSort(self.subjects, day)
            
            if dayIndex == len(self.weekInfo) - 1:
                self.switchExtras(WEEKDAYS[dayIndex], self.subjects)
            
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
                    subjects.append(Subject(subject.name, subjectAmount, subject.perWeek, subject.teacher))
                else:
                    period += 1
                    subjects.append(Subject('Break', 1, 1, None))
                    
                    self.subjects.append(subject)
                    empties.append(subjectIndex)
            
            self.table[day] = subjects
            
            tempSubjects = []
            for subjectIndex, subject in enumerate(self.subjects):
                if subjectIndex not in set(empties) and subject.perWeek > 0:
                    tempSubjects.append(subject)
            
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
                TIMETABLES[self.cls] = self
                print()
                print(f"Found the perfect time table for {self.cls.name} after {self._perfectTimetableCounter + 1} {'tries' if self._perfectTimetableCounter else 'try'}")
                print()
            else:
                self._perfectTimetableCounter += 1
                self.reset()
                self.generate()
        else:
            TIMETABLES[self.cls] = self
            print(f"Couldn't get the perfect timetable combination for {self.cls.name} after all {self._perfectTimetableCounter + 1} tries")

CLASSES: dict[str, Class] = {}
TIMETABLES: dict[Class, Timetable] = {}
TEACHERS: dict[str, Teacher] = {}