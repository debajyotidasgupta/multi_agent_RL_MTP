#!/home/dawesome/multi_agent_RL_MTP/SARL/sarl/bin/python3
# -*- coding: utf-8 -*-
import re
import sys
from s2protocol.s2_cli import main
if __name__ == '__main__':
    sys.argv[0] = re.sub(r'(-script\.pyw|\.exe)?$', '', sys.argv[0])
    sys.exit(main())
