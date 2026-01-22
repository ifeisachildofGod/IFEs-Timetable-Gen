
from dataclasses import dataclass

@dataclass
class Teacher:
    id: str
    
    name: str

@dataclass
class SubjectPeriod:
    id: str
    
    name: str
    
    teacher: Teacher | None = None
    #                Day  Week
    freq_info: tuple[int, int] | None = None

@dataclass
class FreePeriod:
    id: str = "FreePeriodID"
    
    name: str = "Free"
    teacher: Teacher | None = None

@dataclass
class BreakPeriod:
    id: str = "BreakPeriodID"
    
    name: str = "Break"
    teacher: Teacher | None = None

