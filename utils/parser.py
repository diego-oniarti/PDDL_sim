import os
import re

# Read the contents of a file and convert them in a one line string
# Each group of adjacent whitespaces is replaced by one space to make parsing easier
# Rises an exception if the provided filepath doesn't point to any file
def file_to_string(filepath: str) -> str:
    if not os.path.isfile(filepath):
        raise Exception("File not found {fp}".format(fp=filepath))

    file = open(filepath, "r")
    contents = file.read()
    file.close()

    contents_one_line = re.sub(r"\s+", " ", contents)
    return contents_one_line.strip(" ")

