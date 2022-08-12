"""Console script for prmorph_package."""
import logging
import sys
import prmorph_package.config.args as a
import prmorph_package.config.logging as logs
import prmorph_package as prmorph

""" set up logging """
logger = logs.get_logger(__name__)

def main():
    logs.ignore_imported_loggers()

    """ get args """
    args = a.main()

    logger.info("prmorph running")
    logger.info(f"reading from {args.in_dir}, writing to {args.out_dir}")

    """ run main method """
    prmorph.main(args.in_dir, args.out_dir)
    return 0


if __name__ == "__main__":
    """ wrap everything all raised exceptions get caught """
    try:
        sys.exit(main())  # pragma: no cover
    except Exception as e:
        logger.error(str(e))
        raise
