# app/cli.py
# Command line interface (CLI) application.

import argparse
import configparser
import json
import logging
import logging.config
import sys
from argparse import Namespace
from pathlib import Path

from magicgenerator import config, generate, utils

DEFAULTS = "default.ini"
LOGGING = "logging.ini"


def check_arguments(args: Namespace) -> bool:
    """Check that the arguments are valid.

    Args:
        args (Namespace): The input arguments.

    Returns:
        Whether the arguments are valid.
    """
    logger = logging.getLogger("magicgenerator.check_arguments")

    are_valid = True

    path_to_save_files = Path(args.path_to_save_files)
    if not path_to_save_files.exists():
        logger.error(f"path_to_save_files={path_to_save_files} does not exist.")
        are_valid = False
    else:
        if not path_to_save_files.is_dir():
            logger.error(f"path_to_save_files={path_to_save_files} is not a directory.")
            are_valid = False

    files_count = args.files_count
    if files_count < 0:
        logger.error(f"files_count={files_count} is not valid.")
        are_valid = False

    file_name = args.file_name
    if not file_name:
        logger.error(f"file_name={file_name} is not valid.")
        are_valid = False

    file_prefix = args.file_prefix
    if file_prefix not in ("count", "random", "uuid"):
        logger.error(f"file_prefix={file_prefix} is not valid.")
        are_valid = False

    data_schema = args.data_schema
    if data_schema.startswith("{") and data_schema.endswith("}"):
        try:
            json.loads(data_schema)
        except json.decoder.JSONDecodeError:
            logger.error(f"Fail to convert data_schema={data_schema} into the dictionary.")
            are_valid = False
    else:
        try:
            utils.load_dict(data_schema)
        except (json.decoder.JSONDecodeError, FileNotFoundError):
            logger.error(f"Fail to load a dictionary from data_schema={data_schema}.")
            are_valid = False

    data_lines = args.data_lines
    if data_lines < 1:
        logger.error(f"data_lines={data_lines} is not valid.")
        are_valid = False

    return are_valid


def main() -> None:
    """The main entry point of the CLI application."""
    logging.config.fileConfig(config.CONFIG_DIR / LOGGING)
    logger = logging.getLogger("magicgenerator")

    cfg_parser = configparser.ConfigParser()
    cfg_parser.read(config.CONFIG_DIR / DEFAULTS)
    def_cfg = cfg_parser["DEFAULT"]

    # Read default values for the parameters.
    def_path_to_save_files = def_cfg.get("path_to_save_files")
    def_files_count = def_cfg.getint("files_count")
    def_file_name = def_cfg.get("file_name")
    def_file_prefix = def_cfg.get("file_prefix")
    def_data_schema = def_cfg.get("data_schema")
    def_data_lines = def_cfg.getint("data_lines")
    def_clear_path = def_cfg.getboolean("clear_path")

    parser = argparse.ArgumentParser(
        description="Generate test data based on provided data schema.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "path_to_save_files",
        nargs="?",
        type=str,
        default=def_path_to_save_files,
        help="Where all files need to save.",
    )
    parser.add_argument("--files_count", type=int, default=def_files_count, help="How much json files to generate.")
    parser.add_argument("--file_name", type=str, default=def_file_name, help="Base file_name.")
    parser.add_argument(
        "--file_prefix",
        type=str,
        choices=["count", "random", "uuid"],
        default=def_file_prefix,
        help="What prefix for file name to use if more than 1 file needs to be generated.",
    )
    parser.add_argument(
        "--data_schema",
        type=str,
        default=def_data_schema,
        help="A string with json schema or path to json file with schema.",
    )
    parser.add_argument("--data_lines", type=int, default=def_data_lines, help="Count of lines for each file.")
    parser.add_argument(
        "--clear_path",
        action="store_true",
        default=def_clear_path,
        help="If this flag is on, before the script starts creating new data files, all files in path_to_save_files that match file_name will be deleted.",
    )

    args = parser.parse_args()

    if not check_arguments(args):
        sys.exit(1)

    if args.clear_path:
        path = Path(args.path_to_save_files)
        file_name = args.file_name
        for p in path.glob(f"{file_name}*.json"):
            p.unlink()

    logger.info("Start data generation.")

    generate.generate_data(args)

    logger.info("✅ Data generated!")
