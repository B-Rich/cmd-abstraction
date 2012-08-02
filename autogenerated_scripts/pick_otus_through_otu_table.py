#!/usr/bin/env python
from __future__ import division

__author__ = "Greg Caporaso"
__copyright__ = "Copyright 2012, The QIIME Project"
__credits__ = ['Greg Caporaso', 'Kyle Bittinger']
__license__ = "GPL"
__version__ = "1.5.0-dev"
__maintainer__ = "Greg Caporaso"
__email__ = "gregcaporaso@gmail.com"
__status__ = "Development"

from cmd_abstraction.util import cmd_main
from cmd_abstraction.autogenerated_interfaces import PickOtusThroughOtuTable
from sys import argv

cmd = PickOtusThroughOtuTable()
# script info is locally accessible for backward 
# compatibility
script_info = cmd.getScriptInfo()
if __name__ == "__main__":
    # however we only actually call the command
    # if this script is being accessed directly
    cmd_main(cmd,argv)
