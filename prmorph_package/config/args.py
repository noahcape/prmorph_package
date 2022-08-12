import argparse
import os

def arg_checker(in_dir: str, out_dir: str) -> None:
    """ check that the in_dir exists """
    if not os.path.exists(in_dir):
        raise Exception(f"{in_dir} does not exists to read from")

    """ if out_dir doesn't exists create it """
    if not os.path.exists(out_dir):
        os.mkdir(out_dir)

    temp_folder = f"{out_dir}/temp"
    if not os.path.exists(temp_folder):
        os.mkdir(temp_folder)


def main():
    """Console script for prmorph_package."""
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--in-dir", help="directory to read images from", required=True)
    parser.add_argument("-o", "--out-dir", help="directory to save output to", required=True)
    """Add argument for parser"""
    args = parser.parse_args()

    return args
