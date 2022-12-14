import os


def get_file_name(filepath):
    separator = get_slash_type()
    # reverse the filepath
    reversed = filepath[::-1]
    # split the filepath and take only the first value
    first = reversed.split(separator)[0]
    # reverse it again
    ordered = first[::-1]
    # return it
    return ordered


def get_slash_type():
    # Check the value of the os.name attribute
    if os.name == "nt":
        # Return the slash type for Windows
        return "\\"
    else:
        # Return the slash type for Linux and MacOS
        return os.sep

