from imports import *

class Subject:
    def __init__(self, _id: str, name: str, total: int, perWeek: int, teacher: 'Teacher') -> None:
        self.TOTAL = total
        self.PERWEEK = perWeek
        
        self._teacher = teacher
        
        self.id = _id
        self.name = name
        self.total = self.TOTAL
        self.perWeek = self.PERWEEK
        self.teacher = teacher
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
        subject = Subject(self.id, self.name, self.total, self.perWeek, self.teacher)
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
    def __init__(self, index: int, classID: str, className: str, subjects: list[Subject], periodsPerDay: list[int], namingConvention: list[str], school, schoolDict: dict, schoolTeachers: dict[str, "Teacher"], weekdays: list[str], breakTimePeriods: list[int]) -> None:
        self.school = school
        self.schoolDict = schoolDict
        self.schoolTeachers = schoolTeachers
        
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
        
        # self.updateTeachers()
        
        self.timetable = Timetable(self, [subject.copy() for subject in self.subjects], self.periodsPerDay, self.breakTimePeriods, self.schoolDict)
    
    @staticmethod
    def getUniqueID(index, classID):
        return classID + str(index + 1)
    
    def updateTeachers(self):
        for subjs in self.subjects:
            for _, teacher in self.schoolTeachers.items():
                classTaught = teacher.subjects.get(subjs)
                
                if classTaught is not None:
                    if self.uniqueID in classTaught.uniqueID:
                        self.teachers[teacher] = subjs

class Teacher:
    def __init__(self, _id: str, name: str, subjects: dict[Subject, Class]) -> None:
        self.id = _id
        self.name = name
        self.subjects = subjects

class Timetable:
    def __init__(self, cls: Class, subjects: list[Subject], periodsPerDay: list[int], breakTimePeriods: list[int], schoolDict: dict[Class, "Timetable"]) -> None:
        self.cls = cls
        self.schoolDict = schoolDict
        
        self.subjects = subjects
        self._subjects = [subject.copy() for subject in self.subjects]
        
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
        self.table[day].append(Subject(self.freePeriodID, "Free", total, perWeek, None))
    
    def addFreePeriods(self):
        if self.freePeriodAmt:
            self.subjects.append(Subject(self.freePeriodID, "Free", int(sum([subject.total for subject in self.subjects]) / len(self.subjects)), self.freePeriodAmt, None))
            self._subjects.append(Subject(self.freePeriodID, "Free", int(sum([subject.total for subject in self.subjects]) / len(self.subjects)), self.freePeriodAmt, None))
    
    def reset(self):
        self.subjects = self._subjects
        self._subjects = [subject.copy() for subject in self.subjects if subject.id != self.freePeriodID]
        
        self.table: dict[str, list[Subject]] = {day: [] for day in self.cls.weekdays}
        self.remainderContent = []
        
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
                    subjects.append(Subject(subject.id, subject.name, subjectAmount, subject.perWeek, subject.teacher))
                else:
                    period += 1
                    subjects.append(Subject(self.breakPeriodID, 'Break', 1, 1, None))
                    
                    self.subjects.append(subject)
                    empties.append(subjectIndex)
            
            rem_periods = periods - sum([s.total for s in subjects])
            subjects.append(Subject(self.freePeriodID, "Free", rem_periods, rem_periods, None))
            
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
                            subjects.insert(subjectIndex + 1, Subject(self.breakPeriodID, 'Break', 1, 1, None))
                        elif period > self.breakTimePeriods[dayIndex]:
                            replacementAmt = period - self.breakTimePeriods[dayIndex]
                            subject.total -= replacementAmt
                            
                            subjects.insert(subjectIndex + 1, Subject(self.breakPeriodID, 'Break', 1, 1, None))
                            subjects.insert(subjectIndex + 2, Subject(subject.id, subject.name, replacementAmt, subject.perWeek, subject.teacher))
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

