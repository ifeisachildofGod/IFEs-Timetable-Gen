# import random
# from matplotlib.cbook import flatten

from imports import *

class Subject:
    def __init__(self, _id: str, name: str, total: int, perWeek: int, teacher: 'Teacher', cls: 'Class') -> None:
        self.TOTAL = total
        self.PERWEEK = perWeek
        
        self._teacher = teacher
        
        self.id = _id
        self.name = name
        self.total = self.TOTAL
        self.perWeek = self.PERWEEK
        self.teacher = teacher
        self.cls = cls
        
        self.lockedPeriod = None
    
    @property
    def teacher(self):
        return self._teacher
    
    @teacher.setter
    def teacher(self, teacher: 'Teacher'):
        self._teacher = teacher
        self.uniqueID = (self.id + (self._teacher.id if self._teacher is not None else "")).lower()
        self.uniqueID = self.uniqueID.lower().replace("0x", "").upper()
    
    def copy(self):
        subject = Subject(self.id, self.name, self.total, self.perWeek, self.teacher, self.cls)
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
    def __init__(self, index: int, classID: str, className: str, subjects: list[Subject], periodsPerDay: list[int], namingConvention: list[str], school, schoolDict: dict, schoolSubjects: dict[str, "Teacher"], weekdays: list[str], breakTimePeriods: list[int]) -> None:
        self.school = school
        self.schoolDict = schoolDict
        self.schoolSubjects = schoolSubjects
        
        self.weekdays = weekdays
        
        self.index = index
        self.classID = classID
        self.uniqueID = Class.getUniqueID(self.index, self.classID)
        self.className = className
        self.namingConvention = namingConvention
        
        self.name = self.namingConvention[self.index] + " " + self.className
        self.subjects = subjects
        self.periodsPerDay = periodsPerDay
        self.teachers: dict[Teacher, Subject] = {}
        
        self.breakTimePeriods = breakTimePeriods
        
        self.timetable = Timetable(self, [subject.copy() for subject in self.subjects], self.schoolSubjects, self.periodsPerDay, self.breakTimePeriods, self.schoolDict)
    
    @staticmethod
    def getUniqueID(index, classID):
        return classID + str(index + 1)

class Teacher:
    def __init__(self, _id: str, name: str, subjectIDs: list[str]) -> None:
        self.id = _id
        self.name = name
        self.subjectIDs = subjectIDs

class Timetable:
    def __init__(self, cls: Class, subjects: list[Subject], schoolSubjects: dict[str, Subject], periodsPerDay: list[int], breakTimePeriods: list[int], schoolDict: dict[Class, "Timetable"]) -> None:
        self.cls = cls
        self.schoolDict = schoolDict
        self.schoolSubjects = schoolSubjects
        
        self.subjects = subjects
        self._subjects: list[Subject] = [subject.copy() for subject in self.subjects]
        
        self.periodsPerDay = periodsPerDay
        self.breakTimePeriods = breakTimePeriods
        self.weekInfo = [[day, self.periodsPerDay[dayIndex], self.breakTimePeriods[dayIndex]] for dayIndex, day in enumerate(self.cls.weekdays)]
        
        self.freePeriodAmt = max(sum(self.periodsPerDay) - (sum([subject.perWeek for subject in self.subjects]) + len(self.weekInfo)), 0)
        
        self.freePeriodID = "Subject ID: Free"
        self.breakPeriodID = "Subject ID: Break"
        
        self._perfectTimetableCounter = 0
        self._maxPerfectTimetableTries = 30
        self._foundPerfectTimeTable = False
        
        self.table: dict[str, list[Subject]] = {day: [] for day in self.cls.weekdays}
        self.remainderContent = []
        
        self.reset()
        
        random.shuffle(self.subjects)
    
    def addFreePeriod(self, day: str, total: int, perWeek: int):
        self.table[day].append(Subject(self.freePeriodID, "Free", total, perWeek, None, self.cls))
    
    def addFreePeriods(self):
        if self.freePeriodAmt:
            self.subjects.append(Subject(self.freePeriodID, "Free", int(sum([subject.total for subject in self.subjects]) / len(self.subjects)), self.freePeriodAmt, None, self.cls))
            self._subjects.append(Subject(self.freePeriodID, "Free", int(sum([subject.total for subject in self.subjects]) / len(self.subjects)), self.freePeriodAmt, None, self.cls))
    
    def reset(self):
        self.subjects = self._subjects
        self._subjects = [subject.copy() for subject in self.subjects if subject.id != self.freePeriodID]
        
        self.table: dict[str, list[Subject]] = {day: [] for day in self.cls.weekdays}
        self.remainderContent = []
        
        for subject in self.subjects:
            self.schoolSubjects[subject.uniqueID] = subject
        
        random.shuffle(self.subjects)
    
    def switchExtras(self, day: str, subjects: list[Subject]):
        for subjectIndex, subject in enumerate(subjects):
            if subject.perWeek > subject.total:
                for timetableDay, subj in self.table.items():
                    replaced = False
                    
                    if not [True for subjInfo in subj if subjInfo.id == subject.id]:
                        subjectPeriod = sum([subjInfo.total for subjInfo in subjects[:subjectIndex]]) + 1
                        
                        for sIndex, s in enumerate(subj):
                            replacementPeriod = sum([subjInfo.total for subjInfo in subj[:sIndex]])
                            if not [True for subjInfo in subjects if subjInfo.id == s.id]\
                               and s.id != self.breakPeriodID and subject.perWeek > s.total\
                               and subject.total + s.total == subject.perWeek\
                               and not self.cls.school.findClashes(subject, timetableDay, replacementPeriod, self.cls)\
                               and not self.cls.school.findClashes(s, day, subjectPeriod, self.cls)\
                               and not s.lockedPeriod\
                               and not subject.lockedPeriod:
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
            for nonClashingPeriod in range(self.periodsPerDay[self.cls.weekdays.index(subjectDay)]):
                condition = not (subject.lockedPeriod[0] <= nonClashingPeriod + 1 <= subject.lockedPeriod[0] + subject.lockedPeriod[1] - 1) if subject.lockedPeriod is not None else True
                if condition:
                    if not self.cls.school.findClashes(subject, subjectDay, nonClashingPeriod + 1, self.cls):
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
    
    def insert(self, subject: Subject, row: int, col: int):
        subjects = self.table[self.weekInfo[col][0]]
        
        free_periods = self.weekInfo[col][1] - sum(s.total for s in self.table[self.weekInfo[col][0]])
        if free_periods:
            subjects.append(Subject(self.freePeriodID, "Free", free_periods, free_periods, None, self.cls))
        
        offset = None
        subject_index = None
        
        period = 0
        for index, subj in enumerate(subjects):
            if period >= row:
                offset = period - row
                subject_index = index
                break
            
            period += subj.total
        
        subjects[subject_index].total -= offset
        
        main_offset_subject = subjects[subject_index]
        
        subjects.insert(subject_index, subject)
        
        if offset:
            offset_subject = main_offset_subject.copy()
            offset_subject.total = offset
            
            subjects.insert(subject_index, offset_subject)
        
        self.flatten(self.weekInfo[col][0])
    
    def replace(self, subject: Subject, row: int, col: int):
        subjects = self.table[self.weekInfo[col][0]]
        
        free_periods = self.weekInfo[col][1] - sum(s.total for s in self.table[self.weekInfo[col][0]])
        if free_periods:
            subjects.append(Subject(self.freePeriodID, "Free", free_periods, free_periods, None, self.cls))
        
        subject_index = None
        
        period = 0
        for index, subj in enumerate(subjects):
            if period >= row:
                subject_index = index
                break
            
            period += subj.total
        
        subjects[subject_index].total -= 1
        
        if not subjects[subject_index].total:
            subjects.pop(subject_index)
        
        self.flatten(self.weekInfo[col][0])
        self.insert(subject, row, col)
    
    def flatten(self, day: str):
        subjects = self.table[day]
        
        new_subjects = []
        
        for subject in subjects:
            if new_subjects and new_subjects[-1].id == subject.id:
                new_subjects[-1].total += subject.total
            else:
                new_subjects.append(subject)
        
        subjects.clear()
        subjects.extend(new_subjects)
    
    def generate(self):
        for dayIndex, (day, periods, breakPeriod) in enumerate(self.weekInfo):
            period = 0
            
            subjects = []
            empties = []
            
            random.shuffle(self.subjects)
            
            for subject in self.subjects:
                subject.resetTotal()
            
            if dayIndex == len(self.weekInfo) - 1:
                self.switchExtras(self.cls.weekdays[dayIndex], self.subjects)
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
                    subjectAmount = subject.perWeek
                elif period + subject.total > periods:
                    subjectAmount =  period + subject.total - periods
                else:
                    subjectAmount = subject.total  # You might want to randomize the subject amount one day, make it a random number in the range of 1 and subject.total, but if you did that, then you might also want to make this part a code snippet and recurse on it, if it is not filled
                
                if not breakTime:
                    period += subjectAmount
                    subject.remove(subjectAmount)
                    subjects.append(Subject(subject.id, subject.name, subjectAmount, subject.perWeek, subject.teacher, subject.cls))
                else:
                    period += 1
                    subjects.append(Subject(self.breakPeriodID, 'Break', 1, 1, None, self.cls))
                    
                    self.subjects.append(subject)
                    empties.append(subjectIndex)
            
            rem_periods = periods - sum([s.total for s in subjects])
            subjects.append(Subject(self.freePeriodID, "Free", rem_periods, rem_periods, None, self.cls))
            
            self.table[day] = subjects
            
            tempSubjects = []
            for subjectIndex, subject in enumerate(self.subjects):
                if subjectIndex not in set(empties) and subject.perWeek > 0:
                    tempSubjects.append(subject)
            
            self.subjects = tempSubjects
        
        for dayIndex, (_, subjects) in enumerate(self.table.items()):
            if self.breakPeriodID not in [subject.id for subject in subjects]:
                period = 1
                for subjectIndex, subject in enumerate(subjects):
                    period += subject.total
                    if period >= self.breakTimePeriods[dayIndex]:
                        if period == self.breakTimePeriods[dayIndex]:
                            subjects.insert(subjectIndex + 1, Subject(self.breakPeriodID, 'Break', 1, 1, None, subject.cls))
                        elif period > self.breakTimePeriods[dayIndex]:
                            replacementAmt = period - self.breakTimePeriods[dayIndex]
                            subject.total -= replacementAmt
                            
                            subjects.insert(subjectIndex + 1, Subject(self.breakPeriodID, 'Break', 1, 1, None, subject.cls))
                            subjects.insert(subjectIndex + 2, Subject(subject.id, subject.name, replacementAmt, subject.perWeek, subject.teacher, subject.cls))
                        break
        
        self.remainderContent = [subj.copy() for subj in self.subjects]
        
        if self._foundPerfectTimeTable:
            return
        
        if self._perfectTimetableCounter < self._maxPerfectTimetableTries:
            totalSubjectsAmt = sum(self.periodsPerDay)
            timeTableSubjectsAmt = sum([subject.perWeek for subject in self._subjects]) + len(self.weekInfo)
            totalRemainingSubjectsAmt = len(self.remainderContent)
            
            if max(timeTableSubjectsAmt - totalSubjectsAmt, 0) == totalRemainingSubjectsAmt:
                self._foundPerfectTimeTable = True
                self.schoolDict[self.cls] = self
            else:
                self._perfectTimetableCounter += 1
                self.reset()
                self.generate()
        else:
            self.schoolDict[self.cls] = self

