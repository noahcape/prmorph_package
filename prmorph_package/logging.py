import logging

def get_logger(module_name: str, fname: str = './logs.txt') -> logging.Logger:
  logging.basicConfig(
    format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
    datefmt='%H:%M:%S',
    level=logging.DEBUG,
    handlers=[
      logging.FileHandler(fname),
      logging.StreamHandler()
    ]
  )

  return logging.getLogger(module_name)

def ignore_imported_loggers():
  with open('./requirements.txt') as imported_modules:
    modules = imported_modules.readlines()

    for module in modules:
      module = str(module).split("==")[0]
      logging.getLogger(module).setLevel(logging.WARNING)

  """ for some reason we need to do this too """
  logging.getLogger("PIL.TiffImagePlugin").setLevel(logging.WARNING)