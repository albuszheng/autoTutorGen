import subprocess
import json
import os


# using Python subprocess module to get the step by step debugging trace from the PythonTutor's code
# target: the relative address of the file containing the code snippet / content of the code snippet
# is_file: True -> target is a file address / False -> target is the content of the code snippet
# need_py_3: True -> using alias "Python3" in the subprocess command / False -> using alias "Python")
def get_code_trace(target: str, is_file=True, need_py_3=True):
    working_path = os.path.dirname(os.path.abspath(__file__))
    python_cmd = "python3" if need_py_3 else "python"
    if is_file:
        p = subprocess.Popen([python_cmd, working_path + '/generate_json_trace.py', target], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        p.wait()
        stdout, error = p.communicate()
        return json.loads(stdout.decode('utf-8'))
    else:
        # start subprocess
        p = subprocess.Popen([python_cmd, working_path + '/generate_json_trace.py', '--code', target], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        p.wait()
        # subprocess end
        stdout, error = p.communicate()
        return json.loads(stdout.decode('utf-8'))


def check_trace_result(trace_step: dict):
    if trace_step['event'] == "exception":
        return True, trace_step['exception_msg']
    elif trace_step['event'] == "uncaught_exception":
        return True, trace_step['exception']
    else:
        return False, trace_step['event']

