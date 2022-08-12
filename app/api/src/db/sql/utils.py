import os
from collections import namedtuple
from pathlib import Path


def find_unapplied_dependencies(function_content, function_list):
    dependencies = set()
    for function in function_list:
        if "." + function.name in function_content:
            dependencies.add(function.name)
    return dependencies


def get_name_from_path(path) -> str:
    """
    to get name of function from path (file name)
    """
    basename = os.path.basename(path)
    return os.path.splitext(basename)[0]


def get_function_list_from_files(path_list):
    function = namedtuple("function", ["path", "name", "dependencies"])
    function_list = []
    for path in path_list:
        function_name = get_name_from_path(path)
        function_list.append(function(path, function_name, set()))
    return function_list


def sorted_path_by_dependency(path_list):
    """
    The first function is not depended to any others.
    But the last one maybe depended.
    """
    new_path_list = []
    function_list = get_function_list_from_files(path_list)
    while function_list:
        function = function_list.pop(0)
        function_content = Path(function.path).read_text()
        dependencies = find_unapplied_dependencies(function_content, function_list)
        if dependencies:
            # found dependencies, add to the end of functions again.
            # update dependencies
            function.dependencies.clear()
            function.dependencies.update(dependencies)
            function_list.append(function)
        else:
            new_path_list.append(Path(function.path))

    return new_path_list


if __name__ == "__main__":
    path_list = Path(str(Path().resolve()) + "/src/db/sql/functions").rglob("*.sql")
    new_path_list = sorted_path_by_dependency(path_list)
    print(new_path_list)
