"""Main module."""
import datetime as dt
import os
from .config import logging as logs
from .functions import main as functions

logger = logs.get_logger(__name__)

""" This is the main entry point from cli to functions """
def main(in_dir: str, out_dir: str):
    """ at this point the in_dir has been checked and the out_dir has been created """
    print(in_dir, out_dir)

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
                functions.detect_fish_id(f"{in_dir}/{img}", out_dir)

                """ compute the length """
                functions.regular_length(f"{in_dir}/{img}", writer)

    logger.info(f"prmorph finished computing regular length, find csv file at {file_name}")