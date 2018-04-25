from yattag import Doc, indent
import os


# TODO: decided whether give user the option of downloading html files


def create_brd_file(brd_content: str, problem_name: str):
    path = "temp_file/HTML/"
    if not os.path.exists(path):
        os.makedirs(path)
    file_name = problem_name + "_%Y_%m_%d.html"
    with open(path + file_name, "w+") as text_file:
        text_file.write(brd_content)

    return path + file_name