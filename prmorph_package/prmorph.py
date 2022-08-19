"""Main module."""
import typing as type
import datetime as dt
import os
from . import args
from . import logging as logs
from . import cli as cli
from .functions import main as funcm

logger = logs.get_logger(__name__)

# do not use vision rn
VISION = False

""" This is the main entry point from cli to functions """
def main(in_dir: str, out_dir: str):
    try:
        # check arguments
        args.arg_checker(in_dir, out_dir)

        logger.info("prmorph running")
        logger.info(f"reading from {in_dir}, writing to {out_dir}")

        logger.info("Computing Regular Length")
        file_name = execute_workflow(in_dir, out_dir, "computed_lengths", funcm.regular_length)
        logger.info(f"DONE: regular length computation, find file at {file_name}")

        if VISION:
            logger.info("Renaming Images")
            file_name = execute_workflow(in_dir, out_dir, "renamed_files", funcm.detect_fish_id)
            logger.info(f"DONE: detecting fish IDs, find file at {file_name}")

    except Exception as e:
        logger.error(str(e))
        raise

def execute_workflow(in_dir: str, out_dir: str, file_desc: str, method: type.Callable):
    """ get the date for the file """
    date = dt.date.today().strftime('%y%m%d')
    file_name = f"{out_dir}/{file_desc}_{date}.csv"
    error_file_name = f"{out_dir}/errors_{file_desc}_{date}.txt"

    """ open file to write to """
    with open(file_name, 'w') as writer:

        """ loop through in_dir """
        for img in os.listdir(in_dir):

            """ ensure that is is a valid image file to read """
            if img.lower().endswith(('.png', '.jpg', '.jpeg')):
                try:
                    """ compute the length """
                    method(f"{in_dir}/{img}", writer, out_dir)
                except Exception as e:
                    logger.warning(f"Error reading {img}.")

                    with open(error_file_name, 'a') as error_writer:
                        error_writer.write(f"ERROR: {img} with error: {str(e)}")

    return file_name