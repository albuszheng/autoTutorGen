# from ..utl.db_trace import check_trace_result
import json


files = [{'name': 'example.py', 'content': 'x = 1\nfor i in range(1, 2):\n    x += i', 'trace': {'code': 'x = 1\nfor i in range(1, 2):\n    x += i', 'trace': [{'line': 1, 'event': 'step_line', 'func_name': '<module>', 'globals': {}, 'ordered_globals': [], 'stack_to_render': [], 'heap': {}, 'stdout': ''}, {'line': 2, 'event': 'step_line', 'func_name': '<module>', 'globals': {'x': 1}, 'ordered_globals': ['x'], 'stack_to_render': [], 'heap': {}, 'stdout': ''}, {'line': 3, 'event': 'step_line', 'func_name': '<module>', 'globals': {'x': 1, 'i': 1}, 'ordered_globals': ['x', 'i'], 'stack_to_render': [], 'heap': {}, 'stdout': ''}, {'line': 2, 'event': 'step_line', 'func_name': '<module>', 'globals': {'x': 2, 'i': 1}, 'ordered_globals': ['x', 'i'], 'stack_to_render': [], 'heap': {}, 'stdout': ''}, {'line': 2, 'event': 'return', 'func_name': '<module>', 'globals': {'x': 2, 'i': 1}, 'ordered_globals': ['x', 'i'], 'stack_to_render': [], 'heap': {}, 'stdout': ''}]}}]


def check_trace_result(trace_step: dict):
    print(trace_step)
    if trace_step['event'] == "exception":
        return True, trace_step['exception_msg']
    elif trace_step['event'] == "uncaught_exception":
        return True, json.dumps(trace_step)
    else:
        return False, trace_step['event']

# get the number of variables in the code snippet
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

# cognitive_model:
#   "changed" -> the name of the variable or information that has changed in this step
#   "value"   -> the value of that changed variable or information
#   "snapshot"-> the snapshot of all the variables and their values after this change
def get_cognitive_model(variables: list, db_trace: dict):
    trace = db_trace['trace']
    cognitive_model = []

    # initialization
    snapshot = {"line": 1, "previous_line": 1}
    for variables in variables:
        snapshot[variables] = 0

    cognitive_model.append({"changed": "line", "value": snapshot['line'], "line": snapshot['line']})
    # print(cognitive_model)
    # running the code and update the snapshot
    for step in trace:
        # print(snapshot)
        has_error, msg = check_trace_result(step)
        if not has_error:
            g_vars = step['globals']
            for var_name in g_vars:
                if g_vars[var_name] != snapshot[var_name]:
                    cognitive_model.append({"changed": var_name, "value": g_vars[var_name], "line": snapshot['line']})
                    # print({"changed": var_name, "value": g_vars[var_name], "line": snapshot['previous_line']})
                    snapshot = update_snapshot(var_name, g_vars[var_name], snapshot)
                    # print(snapshot)

            line = step['line']
            if line != snapshot['line']:
                cognitive_model.append({"changed": "line", "value": line, "line": line})
                # print({"changed": "line", "value": line, "line": line})
                snapshot = update_snapshot('previous_line', snapshot['line'], snapshot)
                snapshot = update_snapshot('line', line, snapshot)
                # print(snapshot)

            if step['stdout'] != '':
                cognitive_model.append({"changed": 'stdout', "value": step['stdout'], "line": line})
                variables.append('stdout')

        else:
            print(msg)
            break

    return cognitive_model, variables


m,v = get_cognitive_model(['x', 'i'], files[0]['trace'])
for temp in m:
    print(temp)
print("===")
m = sorted(m, key=lambda k: k['line'])
for temp in m:
    print(temp)

