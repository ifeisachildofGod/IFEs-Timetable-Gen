import unittest
from helpers import findClashes
from objects import SCHOOL, Subject, Class, Teacher, Timetable, TimetableSeed

class TestSubject(unittest.TestCase):
    def setUp(self):
        self.subject = Subject("Math", 10, 5, "Mr. Smith")

    def test_initialization(self):
        self.assertEqual(self.subject.name, "Math")
        self.assertEqual(self.subject.total, 10)
        self.assertEqual(self.subject.perWeek, 5)
        self.assertEqual(self.subject.teacher, "Mr. Smith")

    def test_copy(self):
        subject_copy = self.subject.copy()
        self.assertEqual(subject_copy.name, self.subject.name)
        self.assertEqual(subject_copy.total, self.subject.total)
        self.assertEqual(subject_copy.perWeek, self.subject.perWeek)
        self.assertEqual(subject_copy.teacher, self.subject.teacher)

    def test_fullReset(self):
        self.subject.total = 5
        self.subject.perWeek = 2
        self.subject.fullReset()
        self.assertEqual(self.subject.total, 10)
        self.assertEqual(self.subject.perWeek, 5)

    def test_resetTotal(self):
        self.subject.total = 5
        self.subject.resetTotal()
        self.assertEqual(self.subject.total, 10)

    def test_get(self):
        self.assertEqual(self.subject.get(), ["Math"] * 10)

    def test_remove(self):
        self.subject.remove(3)
        self.assertEqual(self.subject.total, 7)
        self.assertEqual(self.subject.perWeek, 2)

class TestClass(unittest.TestCase):
    def setUp(self):
        self.subject = Subject("Math", 10, 5, "Mr. Smith")
        self.cls = Class(1, "A", [self.subject], [6, 6, 6, 6, 6], ["Grade"])

    def test_initialization(self):
        self.assertEqual(self.cls.name, "Grade A")
        self.assertEqual(self.cls.subjects, [self.subject])
        self.assertEqual(self.cls.periodsPerDay, [6, 6, 6, 6, 6])

class TestTeacher(unittest.TestCase):
    def setUp(self):
        self.subject = Subject("Math", 10, 5, "Mr. Smith")
        self.cls = Class(1, "A", [self.subject], [6, 6, 6, 6, 6], ["Grade"])
        self.teacher = Teacher("Mr. Smith", {self.subject: self.cls})

    def test_initialization(self):
        self.assertEqual(self.teacher.name, "Mr. Smith")
        self.assertEqual(self.teacher.subjects, {self.subject: self.cls})

class TestTimetable(unittest.TestCase):
    def setUp(self):
        self.subject1 = Subject("Math", 2, 5, "Mr. Smith")
        self.subject2 = Subject("Eng", 2, 5, "Mr. Smith")
        self.subject3 = Subject("Chem", 2, 4, "Mr. Smith")
        self.subject4 = Subject("Phys", 2, 4, "Mr. Smith")
        self.subject5 = Subject("Bio", 2, 4, "Mr. Smith")
        self.subject6 = Subject("F/Maths", 2, 4, "Mr. Smith")
        self.subject7 = Subject("Cisco", 2, 4, "Mr. Smith")
        self.subject8 = Subject("BE", 2, 4, "Mr. Smith")
        self.subject9 = Subject("EI", 2, 4, "Mr. Smith")
        self.subject10 = Subject("Geo", 2, 4, "Mr. Smith")
        self.subject11 = Subject("TD", 2, 4, "Mr. Smith")
        self.subject12 = Subject("Civic", 2, 3, "Mr. Smith")
        
        self.cls = Class(1, "A", [self.subject1, self.subject2, self.subject3, self.subject4, self.subject5, self.subject6, self.subject7, self.subject8, self.subject9, self.subject10, self.subject11, self.subject12], [10, 10, 10, 10, 10], ["Grade", "Grade", "Grade", "Grade", "Grade"])
        self.cls.timetable.generate()

    def test_clashing(self):
        for cls, timetable in SCHOOL.items():
            for day, subjects in timetable.table.items():
                for subjectIndex, subject in enumerate(subjects):
                    if subject.teacher is not None:
                        period = sum([subj.total for subj in subjects[:subjectIndex]]) + 1
                        clash = findClashes(SCHOOL, subject, day, period, cls)
                        
                        self.assertEqual(clash, [], f"{subject.name} in {cls.name} clashes with {"".join([f"{clashSubject.name} in {clashCls.name}" for clashSubject, clashCls in clash])}")
        

class TestTimetableSeed(unittest.TestCase):
    def setUp(self):
        self.subject1 = Subject("Math", 2, 5, "Mr. Smith")
        self.subject2 = Subject("Eng", 2, 5, "Mr. Smith")
        self.subject3 = Subject("Chem", 2, 4, "Mr. Smith")
        self.subject4 = Subject("Phys", 2, 4, "Mr. Smith")
        self.subject5 = Subject("Bio", 2, 4, "Mr. Smith")
        self.subject6 = Subject("F/Maths", 2, 4, "Mr. Smith")
        self.subject7 = Subject("Cisco", 2, 4, "Mr. Smith")
        self.subject8 = Subject("BE", 2, 4, "Mr. Smith")
        self.subject9 = Subject("EI", 2, 4, "Mr. Smith")
        self.subject10 = Subject("Geo", 2, 4, "Mr. Smith")
        self.subject11 = Subject("TD", 2, 4, "Mr. Smith")
        self.subject12 = Subject("Civic", 2, 3, "Mr. Smith")
        
        self.cls = Class(1, "A", [self.subject1, self.subject2, self.subject3, self.subject4, self.subject5, self.subject6, self.subject7, self.subject8, self.subject9, self.subject10, self.subject11, self.subject12], [10, 10, 10, 10, 10], ["Grade", "Grade", "Grade", "Grade", "Grade"])
        
        resultant_subjects = [Subject("Invalid1", 3, 4, None), Subject("Invalid2", 3, 4, None), Subject("Invalid3", 3, 4, None), Subject("Invalid4", 3, 4, None)]        
        resultant_class = Class(1, "B", resultant_subjects, [1, 1, 1, 1, 1], ["Invalid"])
        
        resultant_subjects[0].teacher = Teacher("Carl", {resultant_class: resultant_subjects[0]})
        resultant_subjects[1].teacher = Teacher("Obama", {resultant_class: resultant_subjects[1]})
        resultant_subjects[2].teacher = Teacher("Trump", {resultant_class: resultant_subjects[2]})
        resultant_subjects[3].teacher = Teacher("Hillary", {resultant_class: resultant_subjects[3]})
        
        self.seed = TimetableSeed()

    def test_convertNumberToSeedNumber(self):
        self.assertEqual(self.seed._convertNumberToSeedNumber(1), "11")
        self.assertEqual(self.seed._convertNumberToSeedNumber(12), "223")
        self.assertEqual(self.seed._convertNumberToSeedNumber(123), "3351")
        self.assertEqual(self.seed._convertNumberToSeedNumber(1234), "447211")
        self.assertEqual(self.seed._convertNumberToSeedNumber(19), f"29{self.seed._seedNumberSep}0")
        self.assertEqual(self.seed._convertNumberToSeedNumber(189), f"39{self.seed._seedNumberSep}71")
        self.assertEqual(self.seed._convertNumberToSeedNumber(9999), f"49{self.seed._seedNumberSep}8919")

    def test_convertSeedNumberToNumber(self):
        self.assertEqual(self.seed._convertSeedNumberToNumber("11"), 1)
        self.assertEqual(self.seed._convertSeedNumberToNumber("223"), 12)
        self.assertEqual(self.seed._convertSeedNumberToNumber("3351"), 123)
        self.assertEqual(self.seed._convertSeedNumberToNumber("447211"), 1234)
        self.assertEqual(self.seed._convertSeedNumberToNumber(f"29{self.seed._seedNumberSep}0"), 19)
        self.assertEqual(self.seed._convertSeedNumberToNumber(f"39{self.seed._seedNumberSep}71"), 189)
        self.assertEqual(self.seed._convertSeedNumberToNumber(f"49{self.seed._seedNumberSep}8919"), 9999)
    
    def test_seed_accuracy(self):
        for _ in range(1000):
            self.cls.timetable.reset()
            self.cls.timetable.generate()
            
            timetableSeed = self.seed.generateTimetableSeed(self.cls.timetable)
            self.resultant_timetable = self.seed.getTimetableFromSeed(timetableSeed)
            
            clsSeed = self.seed.generateTimetableSeed(self.cls)
            self.resultant_cls = self.seed.getTimetableFromSeed(clsSeed)
            
            schoolSeed = self.seed.generateTimetableSeed(SCHOOL)
            self.resultant_school = self.seed.getTimetableFromSeed(schoolSeed)
            
            self.assertEqual(self.resultant_timetable, self.cls.timetable)
            self.assertEqual(self.resultant_cls, self.cls)
            self.assertEqual(self.resultant_school, SCHOOL)

if __name__ == "__main__":
    unittest.main()