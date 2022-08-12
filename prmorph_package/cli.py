"""Console script for prmorph_package."""
import sys
from .config import args as a
from .config import logging as logs
import prmorph_package as prmorph

""" set up logging """
logger = logs.get_logger(__name__)

def main(from_cli: bool = False):
    logs.ignore_imported_loggers()

    """ get args """
    if from_cli:
        args = a.main()

        """ run main method """
        prmorph.main(args.in_dir, args.out_dir)
        
    return 0


if __name__ == "__main__":
    """ wrap everything all raised exceptions get caught """
    try:
        sys.exit(main(True))  # pragma: no cover
    except Exception as e:
        logger.error(str(e))
        raise
