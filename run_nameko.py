# Exact code from nameko pip shortcut - for debugging
import re
import sys
from nameko.cli import cli
if __name__ == '__main__':
    sys.argv[0] = re.sub(r'(-script\.pyw|\.exe)?$', '', sys.argv[0])
    sys.exit(cli())
