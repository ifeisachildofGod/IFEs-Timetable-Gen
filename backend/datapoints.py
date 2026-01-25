
from dataclasses import dataclass



# Subject Periods
@dataclass
class SubjectPeriod:
    id: str
    
    name: str
    
    teacher: "Teacher | None" = None
    #                Day  Week
    freq_info: tuple[int, int] | None = None

@dataclass
class CombinedSubjectPeriod:
    id: str
    
    subjects: list[SubjectPeriod]
    
    teacher: "CombinedTeacher | None" = None
    
    #                Day  Week
    freq_info: tuple[int, int] | None = None

@dataclass
class FreePeriod:
    id: str = "FreePeriodID"
    
    name: str = "Free"
    teacher: "Teacher | None" = None

@dataclass
class BreakPeriod:
    id: str = "BreakPeriodID"
    
    name: str = "Break"
    teacher: "Teacher | None" = None


# Objects
Timetable = dict[str, list[SubjectPeriod | CombinedSubjectPeriod | BreakPeriod | FreePeriod]]

@dataclass
class Teacher:
    id: str
    
    name: str

@dataclass
class CombinedTeacher:
    id: str
    
    teachers: list[Teacher]

@dataclass
class Class:
    id: str
    
    section_name: str
    specifier_name: str
    
    #                Period Amount  Break Period
    dotw_data: dict[str, tuple[int, int]]
    
    #           SubjectID
    subjects: dict[str, SubjectPeriod | CombinedSubjectPeriod]
    
    timetable: Timetable | None = None
    
    
    def name(self):
        return f"{self.section_name} {self.specifier_name}"
