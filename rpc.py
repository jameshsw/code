"""
# Imagine you have an RPC server that is producing log entries or we're analyzing such a log (either 
# fresh or an old log from a hard drive). There are two entries for each call, one when the RPC starts 
# and one when the RPC finishes processing. We'd like to know as soon as possible if there's an RPC  
# that took too much time / timed out.

# Log is already sorted by timestamp

# Example:
# With timeout 3
# Schema: <RpcId, Timestamp, Start or End>

# Example log:
# ID 1,   0,  Start
# ID 2,   1,  Start
# ID 1,   2,  End
# ID 3,   6,  Start
# ID 2,   7,  End
# ID 3,   8,  End

# Graphical representation of the log
# ID: 3                               (-------)
# ID: 2           (-----------------------)
# ID: 1       (-------)
# Time:       0   1   2   3   4   5   6   7   8
"""

"""
def fine_earliest_to(log, to):
    start_time = {}
    
    for id, ts, type in log:
        if type == "Start":
        start_time[id] = ts
        for id, st in start_time.items():
        if ts - st > to:
            return True
        if type == "End":
        del start_time[id]
    return False
"""

def fine_earliest_to2(log, to):
    dic = {}
    arr = []
    for id, ts, type in log:
        if type == "Start":
            dic[id] = len(arr) - 1
            arr.append([id, ts])
        if ts - arr[0][1] > to:
            return True
        if type == "End":
            idx = dic[id]
            if idx is not None:
                last_id, last_ts = arr[-1]
                arr[idx] = arr[-1]
                dic[last_id] = idx
                arr.pop()
    return False

print(fine_earliest_to2(
[
    [1, 0, "Start"],
    [2, 1, "Start"],
    [1, 2, "End"],
    [3, 6, "Start"],
    [2, 7, "End"],
    [3, 8, "End"],
], 3))

print(fine_earliest_to2(
[
    [1, 0, "Start"],
    [2, 1, "Start"],
    [1, 2, "End"],
    [3, 6, "Start"],
    [2, 7, "End"],
    [3, 8, "End"],
], 9))
