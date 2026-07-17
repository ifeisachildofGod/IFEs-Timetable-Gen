import os, sys, time, gzip, json, random, shutil

from copy import deepcopy
from matplotlib.cbook import flatten

from typing import Any, Callable, Union, Optional


DOTW_DATA = {
    "content": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", None, "Saturday", "Sunday"],
    "id_mapping": {0: "ID:monday3231", 1: "ID:tuesday6456", 2: "ID:wednesday0921", 3: "ID:thursday9182", 4: "ID:friday8765", 6: "ID:saturday8728", 7: "ID:sunday0091"}
}
