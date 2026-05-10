# import random
# from matplotlib.cbook import flatten

from imports import *
from middle.frameworks import FreePeriodFW, BreakPeriodFW

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
        self.uniqueID = (str(self.id) + str(self._teacher.id if self._teacher is not None else "")).lower()
        self.uniqueID = self.uniqueID.lower().replace("0x", "").upper()
    
    def copy(self):
        subject = Subject(self.id, self.name, self.total, self.perWeek, self.teacher, self.cls)
        
        subject.TOTAL = self.TOTAL
        subject.PERWEEK = self.PERWEEK
        
        subject.lockedPeriod = self.lockedPeriod
        
        return subject
    
    def fullReset(self):
        self.resetTotal()
        self.perWeek = self.PERWEEK
    
    def resetTotal(self):
        self.total = self.TOTAL
    
    def remove(self, amount):
        assert amount <= self.total, f"Invalid removal amount: {amount}, for day total: {self.total}"
        assert amount <= self.perWeek, f"Invalid removal amount: {amount}, for week total: {self.perWeek}"
        
        self.total -= amount
        self.perWeek -= amount

class CompoundSubject:
    def __init__(self, _id: str, name: str, total: int, perWeek: int, subjects: list['SubjectType'], cls: 'Class'):
        self.TOTAL = total
        self.PERWEEK = perWeek
        
        self.id = _id
        self.name = name
        self.total = self.TOTAL
        self.perWeek = self.PERWEEK
        self.subjects = subjects
        self.cls = cls
        self.uniqueID = self.id + self.cls.uniqueID
        
        self.lockedPeriod = None
    
    def copy(self):
        compSubject = CompoundSubject(self.id, self.name, self.total, self.perWeek, self.subjects, self.cls)
        
        compSubject.TOTAL = self.TOTAL
        compSubject.PERWEEK = self.PERWEEK
        
        compSubject.lockedPeriod = self.lockedPeriod
        
        return compSubject
    
    def fullReset(self):
        self.resetTotal()
        self.perWeek = self.PERWEEK
    
    def resetTotal(self):
        self.total = self.TOTAL
    
    def remove(self, amount):
        assert amount <= self.total, f"Invalid removal amount: {amount}, for day total: {self.total}"
        assert amount <= self.perWeek, f"Invalid removal amount: {amount}, for week total: {self.perWeek}"
        
        self.total -= amount
        self.perWeek -= amount

class Class:
    def __init__(self, index: int, classID: str, className: str, subjects: list['SubjectType'], periodsPerDay: list[int], namingConvention: list[str], school, schoolDict: dict, schoolSubjects: dict[str, "Teacher"], weekdays: list[str], breakTimePeriods: list[int]) -> None:
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
        self.breakTimePeriods = breakTimePeriods
        self.teachers: dict[Teacher, SubjectType] = {}
        
        self.timetable = Timetable(self, [subject.copy() for subject in self.subjects], self.schoolSubjects, self.periodsPerDay, self.breakTimePeriods, self.schoolDict)
    
    def copy(self):
        return Class(self.index, self.classID, self.className, [s.copy() for s in self.subjects], self.periodsPerDay, self.namingConvention, self.school, self.schoolDict, self.schoolSubjects, self.weekdays, self.breakTimePeriods)
    
    @staticmethod
    def getUniqueID(index: int, classID: str):
        return classID + str(index + 1)

class Teacher:
    def __init__(self, _id: str, name: str, subjectIDs: list[str]) -> None:
        self.id = _id
        self.name = name
        self.subjectIDs = subjectIDs

class Timetable:
    def __init__(self, cls: Class, subjects: list['SubjectType'], schoolSubjects: dict[str, 'SubjectType'], periodsPerDay: list[int], breakTimePeriods: list[int], schoolDict: dict[Class, "Timetable"]) -> None:
        self.cls = cls
        self.schoolDict = schoolDict
        self.schoolSubjects = schoolSubjects
        
        self.subjects = subjects
        self._subjects: list[SubjectType] = [subject.copy() for subject in self.subjects]
        
        self.periodsPerDay = periodsPerDay
        self.breakTimePeriods = breakTimePeriods
        self.weekInfo = [[day, self.periodsPerDay[dayIndex], self.breakTimePeriods[dayIndex]] for dayIndex, day in enumerate(self.cls.weekdays)]
        
        self.freePeriodAmt = max(sum(self.periodsPerDay) - (sum([subject.perWeek for subject in self.subjects]) + len(self.weekInfo)), 0)
        
        self._perfectTimetableCounter = 0
        self._maxPerfectTimetableTries = 30
        self._foundPerfectTimeTable = False
        
        self.table: dict[str, list[SubjectType]] = {day: [] for day, _, _ in self.weekInfo}
        self.remainderContent: list[SubjectType] = []
        
        self.reset()
        
        random.shuffle(self.subjects)
    
    def copy(self):
        timetable = Timetable(self.cls, [s.copy() for s in self._subjects], self.schoolSubjects, self.periodsPerDay, self.breakTimePeriods, self.schoolDict)
        
        for day, subjects in self.table.items():
            timetable.table[day] = [s.copy() for s in subjects]
        
        self.remainderContent = [s.copy() for s in timetable.remainderContent]
        
        return timetable
    
    def addFreePeriod(self, day: str, total: int, perWeek: int):
        self.table[day].append(Subject(FREE_PERIOD_ID, "Free", total, perWeek, None, self.cls))
    
    def addFreePeriods(self):
        if self.freePeriodAmt:
            self.subjects.append(Subject(FREE_PERIOD_ID, "Free", int(sum([subject.total for subject in self.subjects]) / len(self.subjects)), self.freePeriodAmt, None, self.cls))
            self._subjects.append(Subject(FREE_PERIOD_ID, "Free", int(sum([subject.total for subject in self.subjects]) / len(self.subjects)), self.freePeriodAmt, None, self.cls))
    
    def reset(self):
        self.subjects = self._subjects
        self._subjects = [subject.copy() for subject in self.subjects if subject.id != FREE_PERIOD_ID]
        
        self.table: dict[str, list[SubjectType]] = {day: [Subject(FREE_PERIOD_ID, "Free", b - 1, 0, None, self.cls), Subject(BREAK_PERIOD_ID, "Break", 1, 0, None, self.cls), Subject(FREE_PERIOD_ID, "Free", p - b, 0, None, self.cls)] for day, p, b in self.weekInfo}
        self.remainderContent = []
        
        for subject in self.subjects:
            self.schoolSubjects[subject.uniqueID] = subject
        
        random.shuffle(self.subjects)
    
    def findClashes(self, subject: 'SubjectType', day: str, period: int):
        clashes: list[tuple[SubjectType, Class]] = []
        
        for ttCls, timetable in self.schoolDict.items():
            if subject.cls.uniqueID != ttCls.uniqueID:
                subjPeriod = 1
                for subj in timetable.table[day]:
                    if period <= subjPeriod <= period + subject.total - 1:
                        if isinstance(subj, Subject):
                            if isinstance(subject, Subject):
                                if subject.teacher is not None and subj.teacher is not None and subject.teacher.id == subj.teacher.id:
                                    clashes.append([subj, ttCls])
                            else:
                                if subj.teacher is not None and next((True for s in subject.subjects if s.teacher is not None and subj.teacher.id == s.teacher.id), False):
                                    clashes.append([subj, ttCls])
                        else:
                            if isinstance(subject, Subject):
                                if subject.teacher is not None and next((True for s in subj.subjects if s.teacher is not None and subject.teacher.id == s.teacher.id), False):
                                    clashes.append([subj, ttCls])
                            else:
                                if next((True for s in subj.subjects if s.teacher.id in [s_s.teacher.id for s_s in subject.subjects if s_s.teacher is not None]), False):
                                    clashes.append([subj, ttCls])
                    
                    subjPeriod += subj.total
        
        return clashes
    
    
    def switchExtras(self, day: str, subjects: list['SubjectType']):
        for subjectIndex, subject in enumerate(subjects):
            if subject.perWeek > subject.total:
                for timetableDay, subj in self.table.items():
                    replaced = False
                    
                    if not [True for subjInfo in subj if subjInfo.id == subject.id]:
                        subjectPeriod = sum([subjInfo.total for subjInfo in subjects[:subjectIndex]]) + 1
                        
                        for sIndex, s in enumerate(subj):
                            replacementPeriod = sum([subjInfo.total for subjInfo in subj[:sIndex]])
                            if not [True for subjInfo in subjects if subjInfo.id == s.id]\
                               and s.id != BREAK_PERIOD_ID and subject.perWeek > s.total\
                               and subject.total + s.total == subject.perWeek\
                               and not self.findClashes(subject, timetableDay, replacementPeriod)\
                               and not self.findClashes(s, day, subjectPeriod)\
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
    
    def classSort(self, subjects: list['SubjectType'], subjectDay: str):
        subjectsCopy = [subject.copy() for subject in subjects]
        
        period = 1
        nonClashingPeriodsMapping = {}
        for subject in subjectsCopy:
            nonClash = []
            for nonClashingPeriod in range(self.periodsPerDay[self.cls.weekdays.index(subjectDay)]):
                condition = not (subject.lockedPeriod[0] <= nonClashingPeriod + 1 <= subject.lockedPeriod[0] + subject.lockedPeriod[1] - 1) if subject.lockedPeriod is not None else True
                if condition:
                    if not self.findClashes(subject, subjectDay, nonClashingPeriod + 1):
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
    
    def idFind(self, id: str, col: int, start: int | None = None, end: int | None = None, strict=False):
        subjects = self.table[self.weekInfo[col][0]][(start if start is not None else 0) : (end if end is not None else len(self.table[self.weekInfo[col][0]]))]
        
        index = next((index for index, subj in enumerate(subjects) if subj.id == id), -1)
        
        if strict and index == -1:
            raise ValueError(f"Subject of ID {id} is not in the range of Column {col + 1}")
        
        return index
    
    def idRemove(self, id: str, col: int):
        subjects = self.table[self.weekInfo[col][0]]
        
        index = self.idFind(id, col, strict=True)
        
        subjects[index].total -= 1
        
        if subjects[index].total <= 0:
            subjects.pop(index)
    
    def find(self, row: int, col: int, start: int | None = None, end: int | None = None, strict=False):
        subjects = self.table[self.weekInfo[col][0]][(start if start is not None else 0) : (end if end is not None else len(self.table[self.weekInfo[col][0]]))]
        
        curr_period = 0
        
        for index, subj in enumerate(subjects):
            if curr_period >= row:
                return index

            curr_period += subj.total
        
        if strict:
            raise ValueError(f"Period {row + 1} is out of the range of Column {col + 1}")
        
        return -1
    
    def remove(self, row: int, col: int):
        subjects = self.table[self.weekInfo[col][0]]
        
        index = self.find(row, col, strict=True)
        
        subjects[index].total -= 1
        
        if subjects[index].total <= 0:
            subjects.pop(index)
    
    def insert(self, subject: 'SubjectType', row: int, col: int):
        day = self.weekInfo[col][0]
        
        self.spread(self.table[day])
        self.table[day].insert(row, subject)
        self.flatten(self.table[day])
    
    def replace(self, subject: 'SubjectType', row: int, col: int):
        assert subject.total == 1, f"Replace only replaces subjects with a total of 1 not {subject.total}"
        
        day = self.weekInfo[col][0]
        
        self.spread(self.table[day])
        self.table[day][row] = subject
        self.flatten(self.table[day])
    
    def swap(self, row1: int, col1: int, row2: int, col2: int):
        src_subjs = self.table[self.weekInfo[col1][0]]
        tar_subjs = self.table[self.weekInfo[col2][0]]
        
        self.spread(src_subjs)
        self.spread(tar_subjs)
        
        # Exchange
        temp_src_subj = src_subjs[row1]
        temp_tar_subj = tar_subjs[row2]
        
        src_subjs[row1] = temp_tar_subj
        tar_subjs[row2] = temp_src_subj
        
        if temp_src_subj.id == BREAK_PERIOD_ID:
            self.weekInfo[col1][2] = self.cls.breakTimePeriods[col1]\
                = self.breakTimePeriods[col1] = row2 + 1
        elif temp_tar_subj.id == BREAK_PERIOD_ID:
            self.weekInfo[col2][2] = self.cls.breakTimePeriods[col2]\
                = self.breakTimePeriods[col2] = row1 + 1
        
        self.flatten(src_subjs)
        self.flatten(tar_subjs)
    
    def correct(self, col: int):
        subjects = self.table[self.weekInfo[col][0]]
        
        self.spread(subjects)
        
        break_period_before = self.idFind(BREAK_PERIOD_ID, col)
        before_break = self.weekInfo[col][2] - break_period_before - 1
        
        if before_break < 0:
            for i in range(-before_break):
                last_subj = subjects.pop(break_period_before - i - 1)
                if last_subj != FREE_PERIOD_ID:
                    raise Exception("Subject amount error")
        else:
            free = Subject(FREE_PERIOD_ID, "Free", 1, 0, None, self.cls)
            for _ in range(before_break):
                subjects.insert(break_period_before, free)
        
        after_break = self.weekInfo[col][1] - len(subjects)
        if after_break < 0:
            for _ in range(-after_break):
                last_subj = subjects.pop()
                if last_subj.id != FREE_PERIOD_ID:
                    raise Exception("Subject amount error")
        else:
            free = Subject(FREE_PERIOD_ID, "Free", 1, 0, None, self.cls)
            for _ in range(after_break):
                subjects.append(free)
        
        self.flatten(subjects)
    
    @staticmethod
    def flatten(subjects: list['SubjectType']):
        new_subjects = []
        
        for subject in subjects:
            if new_subjects and new_subjects[-1].id == subject.id:
                new_subjects[-1].total += subject.total
            else:
                new_subjects.append(subject.copy())
        
        subjects.clear()
        subjects.extend(new_subjects)
    
    @staticmethod
    def spread(subjects: list['SubjectType']):
        new_subjects = []
        
        for subject in subjects:
            for _ in range(subject.total):
                new_subjects.append(subject)
            
            subject.total = 1
        
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
                    s = (
                        CompoundSubject(subject.id, subject.name, subjectAmount, subject.perWeek, subject.subjects, subject.cls)
                        if isinstance(subject, CompoundSubject) else
                        Subject(subject.id, subject.name, subjectAmount, subject.perWeek, subject.teacher, subject.cls)
                    )
                    subjects.append(s)
                else:
                    period += 1
                    subjects.append(Subject(BREAK_PERIOD_ID, 'Break', 1, 1, None, self.cls))
                    
                    self.subjects.append(subject)
                    empties.append(subjectIndex)
            
            rem_periods = periods - sum([s.total for s in subjects])
            subjects.append(Subject(FREE_PERIOD_ID, "Free", rem_periods, rem_periods, None, self.cls))
            
            self.table[day] = subjects
            
            tempSubjects = []
            for subjectIndex, subject in enumerate(self.subjects):
                if subjectIndex not in set(empties) and subject.perWeek > 0:
                    tempSubjects.append(subject)
            
            self.subjects = tempSubjects
        
        for dayIndex, (_, subjects) in enumerate(self.table.items()):
            if BREAK_PERIOD_ID not in [subject.id for subject in subjects]:
                period = 1
                for subjectIndex, subject in enumerate(subjects):
                    period += subject.total
                    if period >= self.breakTimePeriods[dayIndex]:
                        if period == self.breakTimePeriods[dayIndex]:
                            subjects.insert(subjectIndex + 1, Subject(BREAK_PERIOD_ID, 'Break', 1, 1, None, subject.cls))
                        elif period > self.breakTimePeriods[dayIndex]:
                            replacementAmt = period - self.breakTimePeriods[dayIndex]
                            subject.total -= replacementAmt
                            
                            subjects.insert(subjectIndex + 1, Subject(BREAK_PERIOD_ID, 'Break', 1, 1, None, subject.cls))
                            s = (
                                CompoundSubject(subject.id, subject.name, replacementAmt, subject.perWeek, subject.subjects, subject.cls)
                                if isinstance(subject, CompoundSubject) else
                                Subject(subject.id, subject.name, replacementAmt, subject.perWeek, subject.teacher, subject.cls)
                            )
                            subjects.insert(subjectIndex + 2, s)
                        break
        
        self.remainderContent = list(flatten([[subj.copy() for _ in range(subj.perWeek)] for subj in self.subjects]))
        
        if self._foundPerfectTimeTable:
            return
        
        if self._perfectTimetableCounter < self._maxPerfectTimetableTries:
            totalSubjectsAmt = sum(self.periodsPerDay)
            timeTableSubjectsAmt = sum([subject.perWeek for subject in self._subjects]) + len(self.weekInfo)
            totalRemainingSubjectsAmt = len(self.remainderContent)
            
            if max(timeTableSubjectsAmt - totalSubjectsAmt, 0) == totalRemainingSubjectsAmt:
                self._foundPerfectTimeTable = True
                self.schoolDict[self.cls] = self
                
                for col in range(len(self.table)):
                    self.correct(col)
            else:
                self._perfectTimetableCounter += 1
                self.reset()
                self.generate()
        else:
            self.schoolDict[self.cls] = self

SubjectType = Union[Subject, CompoundSubject]

FREE_PERIOD_ID = FreePeriodFW.id
BREAK_PERIOD_ID = BreakPeriodFW.id
