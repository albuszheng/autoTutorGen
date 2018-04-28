import json

# check if the execution of code snippet has any errors
# return a tuple (has_error:bool, err_msg:str)
def check_trace_result(trace_step: dict):
    if trace_step['event'] == "exception":
        return True, trace_step['exception_msg']
    elif trace_step['event'] == "uncaught_exception":
        return True, json.dumps(trace_step)
    else:
        return False, trace_step['event']

# get the number of global variables in the code snippet
# return a list of global variables' name in string
def var_analysis(db_trace: dict):
    trace = db_trace['trace']
    variables = set()
    for step in trace:
        has_error, msg = check_trace_result(step)
        # print(step)
        if not has_error:
            for global_var_name in step['ordered_globals']:
                variables.add(global_var_name)
        else:
            print(msg)
            break
    return list(variables)


def update_snapshot(key, value, snapshot: dict):
    new_snapshot = snapshot
    new_snapshot[key] = value
    return new_snapshot

# cognitive_model -> dict:
#   "changed" -> the name of the variable or information that has changed in this step
#   "value"   -> the value of that changed variable or information
#   "snapshot"-> the snapshot of all the variables and their values after this change
# return a tuple (cognitive_model:list of cognitive_model dict, variable_list:list)
def get_cognitive_model(variables: list, db_trace: dict):
    trace = db_trace['trace']
    cognitive_model = []

    # initialization
    snapshot = {"line": 1, "previous_line": 1}
    for variables in variables:
        snapshot[variables] = None

    cognitive_model.append({"changed": "line", "value": snapshot['line'], "line": snapshot['line']})
    # running the code and update the snapshot
    for step in trace:
        has_error, msg = check_trace_result(step)
        if not has_error:
            g_vars = step['globals']
            heaps = step['heap']
            for var_name in g_vars:
                if type(g_vars[var_name]) is list:
                    new_heap = heaps[str(g_vars[var_name][1])]
                    if new_heap != snapshot[var_name]:
                        difference = (heap_difference(snapshot[var_name], new_heap))
                        for d in difference:
                            cognitive_model.append({"changed": var_name, "value": d['changed_value'], "line": snapshot['line']})
                    snapshot = update_snapshot(var_name, new_heap, snapshot)
                elif g_vars[var_name] != snapshot[var_name]:
                    cognitive_model.append({"changed": var_name, "value": g_vars[var_name], "line": snapshot['line']})
                    snapshot = update_snapshot(var_name, g_vars[var_name], snapshot)

            line = step['line']
            if line != snapshot['line']:
                cognitive_model.append({"changed": "line", "value": line, "line": line})
                snapshot = update_snapshot('previous_line', snapshot['line'], snapshot)
                snapshot = update_snapshot('line', line, snapshot)

            if step['stdout'] != '':
                cognitive_model.append({"changed": 'stdout', "value": step['stdout'], "line": line})
                variables.append('stdout')

        else:
            print(msg)
            break

    return cognitive_model, variables

# deal with variables using a reference in the heap -> list, dict and tuple
def heap_difference(old_heap:list, new_heap:list):
    print(new_heap[0])
    heap_type = new_heap[0]
    if heap_type == "LIST":
        return heap_list(old_heap,new_heap)
    elif heap_type == "DICT":
        return heap_dict(old_heap, new_heap)
    elif heap_type == "TUPLE":
        return heap_tuple(old_heap, new_heap)

# check the changes in a specific dict
def heap_dict(old_heap:list, new_heap:list):
    old_len = len(old_heap) if old_heap is not None else 0
    new_len = len(new_heap)
    result = []
    if old_len != new_len:
        for i in range(0, new_len):
            if i < old_len and old_heap[i] != new_heap[i]:
                result.append({"changed_value": "[" + new_heap[i][0] + "]" + ":" + str(new_heap[i+1][1])})
            else:
                result.append({"changed_value": "[" + new_heap[i][0] + "]" + ":" + str(new_heap[i+1][1])})
    else:
        for i in range(0, old_len):
            if old_heap[i] != new_heap[i]:
                result.append({"changed_value": "[" + new_heap[i][0] + "]" + ":" + str(new_heap[i+1][1])})
    return result

# check the changes in a specific list
def heap_list(old_heap:list, new_heap:list):
    old_len = len(old_heap) if old_heap is not None else 0
    new_len = len(new_heap)
    result = []
    if old_len != new_len:
        for i in range(0, new_len):
            if i < old_len and old_heap[i] != new_heap[i]:
                result.append({"changed_value": "[" + str(i-1) + "]" + ":" + str(new_heap[i+1])})
            else:
                result.append({"changed_value": "[" + str(i-1) + "]" + ":" + str(new_heap[i+1])})
    else:
        for i in range(0, old_len):
            if old_heap[i] != new_heap[i]:
                result.append({"changed_value": "[" + str(i-1) + "]" + ":" + str(new_heap[i+1])})
    return result

# check the changes in a specific tuple
def heap_tuple(old_heap:list, new_heap:list):
    result = []
    list_diff =  list(set(old_heap) - set(new_heap))
    for item in list_diff:
        if item in old_heap:
            result.append({"changed_value": "del:" + str(item)})
        elif item in new_heap:
            result.append({"changed_value": "add:" + str(item)})
    return result


