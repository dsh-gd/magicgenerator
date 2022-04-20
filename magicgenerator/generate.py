# magicgenerator/generate.py
# Generation operations.

import json
import logging
import random
import re
import sys
import time
import uuid
from argparse import Namespace
from pathlib import Path
from pprint import pprint
from typing import Dict, List

from magicgenerator import utils


def generate_dict(data_schema: Dict) -> Dict:
    """Generate data based on the data schema.

    Args:
        data_schema (Dict): A data schema.
    Returns:
        Generated data as a dictionary.
    """
    logger = logging.getLogger("magicgenerator.generate.generate_dict")

    d = dict()
    for key, val in data_schema.items():
        if ":" not in val:
            logger.error(f'"{val}" is not a valid value.')
            sys.exit(1)

        # g - what to generate
        dtype, _, g = val.partition(":")

        if dtype not in ("timestamp", "str", "int"):
            logger.error(f'"{dtype}" is not a valid data type.')
            sys.exit(1)

        data_item = None
        if dtype == "timestamp":
            if g == "":
                data_item = time.time()
            else:
                logger.warning('The "timestamp" does not support any values; it will be ignored.')
                continue
        # rand
        elif g == "rand":
            if dtype == "str":
                data_item = str(uuid.uuid4())
            elif dtype == "int":
                data_item = random.randint(0, 10000)
            else:
                logger.error(f'"{val}" is not a valid value.')
                sys.exit(1)
        # list with values []
        elif g.startswith("[") and g.endswith("]"):
            try:
                lst = eval(g)
                t = int if dtype == "int" else str

                if all(type(elem) == t for elem in lst):
                    data_item = random.choice(lst)
                else:
                    raise TypeError(f'Not all elements of {lst} are of type "{dtype}".')
            except TypeError as e:
                logger.error(e)
                sys.exit(1)
            except:  # NOQA: E722 (do not use bare 'except')
                logger.error(f'"{val}" is not a valid value.')
                sys.exit(1)
        # rand(from, to)
        elif g.startswith("rand(") and g.endswith(")"):
            try:
                if dtype == "int":
                    s = re.search(r"\(.*?\)", g).group(0)
                    data_item = random.randint(*eval(s))
                else:
                    raise TypeError(f'"{dtype}" is not a valid type for "{g}".')
            except TypeError as e:
                logger.error(e)
                sys.exit(1)
            except:  # NOQA: E722 (do not use bare 'except')
                logger.error(f'"{val}" is not a valid value.')
                sys.exit(1)
        # Stand alone value
        elif g != "":
            try:
                t = int if dtype == "int" else str
                data_item = t(g)
            except:  # NOQA: E722 (do not use bare 'except')
                logger.error(f'"{val}" is not a valid value.')
                sys.exit(1)
        # Empty value
        elif g == "":
            data_item = None if dtype == "int" else ""
        else:
            logger.error(f'"{val}" is not a valid value.')
            sys.exit(1)

        d[key] = data_item

    return d


def create_prefixes(file_prefix: str, files_count: int) -> List:
    """Create a list of file prefixes.

    Args:
        file_prefix (str): A file prefix.
        files_count (int): A number of files.

    Returns:
        A list of file prefixes.
    """
    if file_prefix == "count":
        ndigits = len(str(files_count))
        return [str(p).zfill(ndigits) for p in range(files_count)]
    elif file_prefix == "uuid":
        prefixes = set()
        while len(prefixes) < files_count:
            prefixes.add(str(uuid.uuid4()))
        return list(prefixes)
    else:
        prefixes = set()
        while len(prefixes) < files_count:
            p = random.randrange(files_count * 10000)
            prefixes.add(p)
        return list(prefixes)


def create_file(filepath: Path, data_schema: Dict, data_lines: int) -> None:
    """Generate data and write it to a file.

    Args:
        filepath (str): A location to save generated data to as a JSON file.
        data_schema (Dict): A data schema.
        data_lines (int): The number of lines in the file.
    """
    with open(filepath, "w") as file:
        for _ in range(data_lines):
            data = generate_dict(data_schema)
            datas = json.dumps(data)
            file.write(datas)
            file.write("\n")


def generate_data(args: Namespace) -> None:
    """The main entry point of the data generator."""
    try:
        data_schema = json.loads(args.data_schema)
    except json.decoder.JSONDecodeError:
        data_schema = utils.load_dict(args.data_schema)

    path = Path(args.path_to_save_files)
    files_count = args.files_count
    file_name = args.file_name
    data_lines = args.data_lines

    if files_count == 0:
        data = generate_dict(data_schema)
        pprint(data)
    elif files_count == 1:
        fname = f"{file_name}.json"
        create_file(path / fname, data_schema, data_lines)
    else:
        prefixes = create_prefixes(args.file_prefix, files_count)
        for prefix in prefixes:
            fname = f"{file_name}_{prefix}.json"
            create_file(path / fname, data_schema, data_lines)
