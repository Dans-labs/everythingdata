from optparse import OptionParser
from config import Config

cfg = Config('../config/prompts.ini')
#cfg = config.Config(
#cfg.addNamespace(options, 'cmdline')
print("The verbose option value is %r" % cfg['sql_generator'])
