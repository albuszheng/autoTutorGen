from .db_trace import get_code_trace
from ..brd.trace_analysis import var_analysis

# read the content of the file and get the debugging trace of the code
def handle_uploaded_files(files):
    print("start handling files")
    files = files.getlist('python_files')
    files_content = []
    for f in files:
        print(f)
        f.open(mode='rb')
        lines = f.readlines()
        f.close()
        content_str = b''.join(lines).decode("utf-8")
        trace = get_code_trace(content_str, is_file=False)
        variable_list = var_analysis(trace)
        files_content.append(
            {'name': f.name, 'content': content_str, 'trace': trace, 'variable_list': variable_list})

    return files_content


