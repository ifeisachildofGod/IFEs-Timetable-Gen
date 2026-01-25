
from dataclasses import dataclass

@dataclass
class GeneratingData:
    randomize: bool
    #                             ClassID    SubjectID    Day    DayWeight  PeriodProclivity
    subject_positioning_weights: dict[str, dict[str, dict[str, tuple[float, int]]]]
    
    #                          ClassID    SubjectID    Day  Weight
    subject_clumping_weights: dict[str, dict[str, dict[str, float]]]
    
    #                       SubjectID  ClassIDs
    combined_subjects: dict[list[str], list[str]]
