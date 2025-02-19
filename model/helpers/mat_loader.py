"""
@Author: Foad Alhayek
@Description: Function to convert .mat to python (nested) dictionaries.
"""
import re
import scipy.io as sio

def loadmat(filepath):
    """
    Converts a mat file's structs to Python dictionaries.
    Tested on mat-file version 5 - see in the __header__ for version info.

    :param filepath: Path to the mat file.
    :return: Content in dict form.
    """
    data = sio.loadmat(filepath, struct_as_record=False, squeeze_me=True)

    if "__header__" in data:
        decoded_string = data["__header__"].decode('utf-8')
        match = re.search(r'\d+\.\d+', decoded_string)

        if match is not None:
            if float(match.group()) >= 7.3:
                print(
                    f"Warning, you are using a different mat file version (7.3 or above) which has not been tested.\n"
                    f"The function might not work and the results are not guaranteed.")

    # Remove unnecessary metadata
    data.pop("__header__", None)
    data.pop("__version__", None)
    data.pop("__globals__", None)

    return _check_keys(data)


def _check_keys(data):
    """
    Sorts and checks if the keys are structs. If yes
    todict is called to convert to nested dictionaries.
    """
    for key in sorted(data.keys(), key=lambda s: s.lower()):
        if isinstance(data[key], sio.matlab.mat_struct):
            data[key] = _todict_iterative(data[key])
    return data


def _todict_iterative(matobj):
    """ Iteratively converts MATLAB structs to nested dictionaries. """
    result = {}
    stack = [(result, matobj)]

    while stack:
        current_dict, current_obj = stack.pop()
        fieldnames = sorted(current_obj._fieldnames, key=lambda s: s.lower())

        for fieldname in fieldnames:
            elem = getattr(current_obj, fieldname)

            if isinstance(elem, sio.matlab.mat_struct):
                new_dict = {}
                current_dict[fieldname] = new_dict
                stack.append((new_dict, elem))
            else:
                current_dict[fieldname] = elem
    return result