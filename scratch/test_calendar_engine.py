import os, sys, math, json
from typing import List, Dict, Optional, Tuple, Any
from dataclasses import dataclass, asdict

MONTH_NAMES = ["JAN", "FEB", "MAR", "APR", "MAY", "JUN", "JUL", "AUG", "SEP", "OCT", "NOV", "DEC"]
MONTH_FULL_NAMES = [
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December"
]
DAYS_IN_MONTHS = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
MID_MONTH_DAY_OF_YEAR = [15, 45, 74, 105, 135, 165, 196, 227, 258, 288, 319, 349]

def format_cyclic_window(months: List[int]) -> str:
    if not months:
        return "None"
    if len(months) == 12:
        return "January - December (12 Months)"
    if len(months) == 1:
        return f"{MONTH_FULL_NAMES[months[0]]} (1 Month)"
    
    # Identify connected components on Z12 cycle
    month_set = set(months)
    visited = set()
    runs = []
    
    # To preserve natural calendar order, start searching from months that are "starts" of runs
    # A month is a run start if (m - 1) % 12 is NOT in month_set
    starts = [m for m in months if (m - 1) % 12 not in month_set]
    if not starts:
        # It is a complete cycle or empty
        starts = [sorted(months)[0]]
    
    # Sort starts cyclically or normally
    starts.sort()
    for start in starts:
        if start in visited:
            continue
        curr_run = []
        curr = start
        while curr in month_set and curr not in visited:
            curr_run.append(curr)
            visited.add(curr)
            curr = (curr + 1) % 12
        if curr_run:
            runs.append(curr_run)
            
    # Any leftovers?
    for m in sorted(months):
        if m not in visited:
            runs.append([m])
            visited.add(m)
            
    formatted_parts = []
    for run in runs:
        if len(run) == 1:
            formatted_parts.append(MONTH_FULL_NAMES[run[0]])
        else:
            formatted_parts.append(f"{MONTH_FULL_NAMES[run[0]]} - {MONTH_FULL_NAMES[run[-1]]}")
            
    return f"{' & '.join(formatted_parts)} ({len(months)} Months)"

print("Testing format_cyclic_window:")
print("10,11,0,1,2:", format_cyclic_window([10, 11, 0, 1, 2]))
print("2, 10:", format_cyclic_window([2, 10]))
print("0, 1, 5, 9, 10, 11:", format_cyclic_window([0, 1, 5, 9, 10, 11]))
print("4,5,6,7,8:", format_cyclic_window([4, 5, 6, 7, 8]))
