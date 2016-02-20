import ConfigParser
import logging
import os

# Trick to establish the directory of the actual script, even when called
# via symlink.  The purpose of this is to write output-files relative to
# the script-directory, not the current directory.
SCRIPTDIR = os.path.dirname(os.path.realpath(__file__))

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
fhd = logging.FileHandler(os.path.join(SCRIPTDIR, "debug.log"))
fhd.setLevel(logging.DEBUG)
fhi = logging.FileHandler(os.path.join(SCRIPTDIR, "info.log"))
fhi.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s %(levelname)s: %(message)s")
ch.setFormatter(formatter)
fhd.setFormatter(formatter)
fhi.setFormatter(formatter)
logger.addHandler(ch)
logger.addHandler(fhd)
logger.addHandler(fhi)

config = ConfigParser.RawConfigParser()
config.read(os.path.join(SCRIPTDIR, "ledenlijst.cfg"))
dbcfg = dict(config.items("database"))
ldapcfg = dict(config.items("ldapcfg"))
