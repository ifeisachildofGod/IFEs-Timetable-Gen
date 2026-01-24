
from dataclasses import dataclass


class CompStr(str):
    def __init__(self, c_strings: list[str] | str) -> None:
        super().__init__()
        
        self.is_c_string = isinstance(c_strings, list)
        self.c_strings = c_strings if isinstance(c_strings, list) else list(c_strings)
        
        if not self.is_c_string:
            self = c_strings
    
    # --- Equality Overloading ---
    def __eq__(self, value: object) -> bool:
        if self.is_c_string:
            if isinstance(value, CompStr):
                return next((True for s in self.c_strings if s in value.c_strings), False)
            elif isinstance(value, str):
                return next((True for s in self.c_strings if s == value), False)
            
            raise NotImplementedError()
        else:
            return super().__eq__(value)
    def __ne__(self, value: object) -> bool:
        if self.is_c_string:
            if isinstance(value, CompStr):
                return next((True for s in self.c_strings if s not in value.c_strings), False)
            elif isinstance(value, str):
                return next((True for s in self.c_strings if s != value), False)
            
            raise NotImplementedError()
        else:
            return super().__ne__(value)
    
    # --- Iterator Overloading ---
    def __getitem__(self, key):
        return self.c_strings[key] if self.is_c_string else super().__getitem__(key)
    def __len__(self):
        return len(self.c_strings)
    def __iter__(self):
        return iter(self.c_strings) if self.is_c_string else super().__iter__()
    
    # --- Arithmetic Overloading ---
    def __add__(self, value):
        return CompStr(self.c_strings + [value]) if self.is_c_string else super().__add__(value)
    def __radd__(self, other):
        return self.__add__(other)
    
    def __mul__(self, value):
        return NotImplemented if self.is_c_string else super().__mul__(value)
    def __rmul__(self, other):
        return self.__mul__(other)

@dataclass
class Teacher:
    id: str
    
    name: str

@dataclass
class CombinedTeacher:
    id: str
    
    teachers: list[Teacher]

@dataclass
class SubjectPeriod:
    id: str
    
    name: str
    
    teacher: Teacher | None = None
    #                Day  Week
    freq_info: tuple[int, int] | None = None

@dataclass
class CombinedSubjectPeriod:
    id: str
    
    subjects: list[SubjectPeriod]
    
    teacher: CombinedTeacher | None = None
    
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

