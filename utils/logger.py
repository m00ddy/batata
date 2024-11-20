import logging
import os


logger = logging.getLogger(__name__)
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# set up logging to file - see previous section for more details
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                    datefmt='%m-%d %H:%M',
                    filename=os.path.join(root_dir, "batata.log"),
                    filemode='w')

# define a Handler which writes INFO messages or higher to the sys.stderr
console = logging.StreamHandler()
console.setLevel(logging.INFO)
# set a format which is simpler for console use
formatter = logging.Formatter('[%(name)-12s: %(levelname)s] (%(funcName)s) %(message)s')

# tell the handler to use this format
console.setFormatter(formatter)
# add the handler to the root logger
logger.addHandler(console)
