import subprocess
import json
import os


def get_code_trace(target: str, is_file=True, need_py_3=True):
    working_path = os.path.dirname(os.path.abspath(__file__))
    # print(working_path)
    python_cmd = "python3" if need_py_3 else "python"
    if is_file:
        op_bytes = subprocess.call([python_cmd, working_path + '/generate_json_trace.py', target])
        return json.loads(op_bytes.decode('utf-8'))
    else:
        # command = ['echo', 'hello']
        # result = subprocess.run([python_cmd, working_path + '/generate_json_trace.py', '--code', target], stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
        # op_bytes = result.stdout
        # print(result.returncode, result.stdout, result.stderr)
        print("start subprocess")
        # result = subprocess.call([python_cmd, working_path + '/generate_json_trace.py', '--code', target])
        p = subprocess.Popen([python_cmd, working_path + '/generate_json_trace.py', '--code', target], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        p.wait()
        print("subprocess end")
        stdout, error = p.communicate()
        # result.com
        print(stdout, error)
        return json.loads(stdout.decode('utf-8'))


def check_trace_result(trace_step: dict):
    if trace_step['event'] == "exception":
        return True, trace_step['exception_msg']
    elif trace_step['event'] == "uncaught_exception":
        return True, trace_step['exception']
    else:
        return False, trace_step['event']

