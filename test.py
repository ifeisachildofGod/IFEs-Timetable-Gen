
import random

from matplotlib.cbook import flatten

subjectsCopy = ["aasda", "ca", "esdd", "ddssasdas", "bsd", "fdds"]
subjectsCopy2 = subjectsCopy.copy()

# mapp1 = {
#     "a": [0, 2, 1, 3],
#     "b": [1, 4, 5],
#     "c": [3, 2],
#     "d": [1, 2, 3, 4],
#     "e": [0, 5, 3, 1, 2, 4],
#     "f": [1, 2],
# }

period = 1
mapp = {}
for subject in subjectsCopy:
    for nonClashingPeriod in range(10):
        if random.choice([True, False]):
            tmpSubjPeriod = 1
            nonClash = []
            for subjIndex, subj in enumerate(subjectsCopy):
                if tmpSubjPeriod >= nonClashingPeriod:
                    nonClash.append(subjIndex)
                tmpSubjPeriod += len(subj)
            mapp[subject] = nonClash
    
    period += len(subject)


for subject, nonClash in sorted(mapp.items(), key=lambda nCInfo: len(nCInfo[1]), reverse=True):
    if nonClash:
        allNonClashes = list(mapp.values())
        otherNonClashes = list(flatten(allNonClashes[:allNonClashes.index(nonClash)] + allNonClashes[allNonClashes.index(nonClash) + 1:]))
        nonClashesCopy = nonClash.copy()
        for index in nonClashesCopy:
            if index in otherNonClashes:
                mapp[subject].remove(index)
    else:
        print(f"{subject} will always clash with another letter here")


takenIndexes = []
for subject, nonClash in sorted(mapp.items(), key=lambda nCInfo: len(nCInfo[1]), reverse=True):
    index = random.choice(nonClash) if nonClash else random.choice([i for i in range(len(subjectsCopy2)) if i not in takenIndexes])
    subjectsCopy2[index] = subject
    takenIndexes.append(index)

print(subjectsCopy2)