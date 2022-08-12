"""Main module."""
import datetime as dt
import os
from . import args
from . import logging as logs
from . import cli as cli
from .functions import main as funcm

logger = logs.get_logger(__name__)

""" This is the main entry point from cli to functions """
def main(in_dir: str, out_dir: str):
    try:
        # setup everything
        cli.main()

        # check arguments
        args.arg_checker(in_dir, out_dir)

        logger.info("prmorph running")
        logger.info(f"reading from {in_dir}, writing to {out_dir}")

        """ get the date for the file """
        date = dt.date.today().strftime('%y%m%d')
        file_name = f"{out_dir}/computed_lengths_{date}.csv"

        """ open file to write to """
        with open(file_name, 'w') as writer:
            # """ add header """
            # writer.write("file_name,length (mm)\n")

            """ loop through in_dir """
            for img in os.listdir(in_dir):

                """ ensure that is is a valid image file to read """
                if img.lower().endswith(('.png', '.jpg', '.jpeg')):
                    funcm.detect_fish_id(f"{in_dir}/{img}", out_dir)

                    """ compute the length """
                    funcm.regular_length(f"{in_dir}/{img}", writer)

        logger.info(f"prmorph finished computing regular length, find csv file at {file_name}")
    
    except Exception as e:
        logger.error(str(e))
        raise
    