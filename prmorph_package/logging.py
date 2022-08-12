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
  modules = [
    "matplotlib",
    "numpy",
    "opencv-python",
    "pandas",
    "scikit-image",
    "google-api-core",
    "google-cloud-vision",
    "PIL.TiffImagePlugin",
    "matplotlib.font_manager"
  ]
  
  for module in modules:
    module = str(module).split("==")[0]
    logging.getLogger(module).setLevel(logging.WARNING)