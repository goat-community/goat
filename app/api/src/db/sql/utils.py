import functools
import os
from collections import defaultdict, namedtuple
from pathlib import Path

import rich
from sqlalchemy import text

from src.core.config import settings
from src.db.session import legacy_engine


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


def list_functions():
    query = """
    SELECT
    routine_name
    FROM
        information_schema.routines
    WHERE
        routine_type = 'FUNCTION'
    AND
        routine_schema = :functions_schema;
    """
    query = text(query)
    with legacy_engine.connect() as session:
        functions = session.execute(
            query, {"functions_schema": settings.POSTGRES_FUNCTIONS_SCHEMA}
        )
        return [f["routine_name"] for f in functions]


def report():
    function_paths = Path(str(Path().resolve()) + "/src/db/sql/functions").rglob("*.sql")
    triger_paths = Path(str(Path().resolve()) + "/src/db/sql/triggers").glob("*.sql")
    files = list(function_paths) + list(triger_paths)

    functions = list_functions()
    classified_functions = defaultdict(list)
    not_in_db = []
    for fn in files:
        if not fn:
            continue

        file_name = fn.parts[-1]
        directory_name = fn.parts[-2]
        if get_name_from_path(fn) in functions:
            functions.remove(get_name_from_path(fn))
        else:
            not_in_db.append((directory_name, file_name))
        classified_functions[directory_name].append(file_name)

    for key in classified_functions.keys():
        rich.print(f"[bold blue]## {key}/[/bold blue]")
        for fn in classified_functions[key]:
            print("- ", fn)
    print()
    if functools:
        rich.print("[bold red]# in db but not in files:[/bold red]")
        for fn in functions:
            rich.print(f"[orange1]- {fn}[/orange1]")
    else:
        rich.print("[bold green]All database function names found in files.[/bold green]")

    print()
    if not_in_db:
        rich.print("[bold red]## in files but not in db:[/bold red]")
        for fn in not_in_db:
            rich.print(f"- {fn[0]}/[orange1]{fn[1]}[/orange1]")
    else:
        rich.print("[bold green]All function file names found in database.[/bold green]")
