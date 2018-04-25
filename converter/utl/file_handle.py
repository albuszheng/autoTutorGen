import os
import sys
from .db_trace import get_code_trace
from ..brd.trace_analysis import var_analysis


def handle_uploaded_files(files):
    # print(files)
    print("start handling files")
    files = files.getlist('python_files')
    files_content = []
    for f in files:
        print(f)
        f.open(mode='rb')
        lines = f.readlines()
        f.close()
        content_str = b''.join(lines).decode("utf-8")
        # print(type(lines), b''.join(lines).decode("utf-8"))
        trace = get_code_trace(content_str, is_file=False)
        # print(trace)
        variable_list = var_analysis(trace)
        files_content.append(
            {'name': f.name, 'content': content_str, 'trace': trace, 'variable_list': variable_list})
        # file_name = path + f.name
        # destination = open(file_name + f.name, 'wb+')
        # for chunk in f.chunks():
        #     destination.write(chunk)
        # destination.close()
    return files_content
    # try:
    #     # print(files)
    #     # path = "temp_file/python/"
    #     # if not os.path.exists(path):
    #     #     os.makedirs(path)
    #     #     # print(path)
    #     for f in files:
    #         print(f)
    #         f.open(mode='rb')
    #         lines = f.readlines()
    #         f.close()
    #         content_str = b''.join(lines).decode("utf-8")
    #         # print(type(lines), b''.join(lines).decode("utf-8"))
    #         trace = get_code_trace(content_str, is_file=False)
    #         # print(trace)
    #         # variable_list = var_analysis(trace)
    #         files_content.append({'name': f.name, 'content': content_str, 'trace': trace, 'variable_list': var_analysis(trace)})
    #         # file_name = path + f.name
    #         # destination = open(file_name + f.name, 'wb+')
    #         # for chunk in f.chunks():
    #         #     destination.write(chunk)
    #         # destination.close()
    #     return files_content
    # except:
    #     # e = sys.exc_info()[0]
    #     print("fail to save the file")
    #     print(sys.exc_info())
    #     # return files_content


