#!/usr/bin/env python
# File created on 01 Aug 2012
from __future__ import division

__author__ = "Greg Caporaso"
__copyright__ = "Copyright 2011, The QIIME project"
__credits__ = ["Greg Caporaso"]
__license__ = "GPL"
__version__ = "1.5.0-dev"
__maintainer__ = "Greg Caporaso"
__email__ = "gregcaporaso@gmail.com"
__status__ = "Development"

import inspect
import re
from os.path import join
from site import addsitedir
from qiime.util import parse_command_line_parameters, make_option, create_dir

script_info = {}
script_info['brief_description'] = ""
script_info['script_description'] = ""
script_info['script_usage'] = [("","Autogenerate code for add_taxa.py and pick_otus_through_otu_table.py. After running this, add your top-level cmd-abstraction directory to $PYTHONPATH and call script_usage_tests.py on  ","%prog -i Qiime/scripts/ -s add_taxa,pick_otus_through_otu_table -o cmd-abstraction/autogenerated_scripts/ -f cmd-abstraction/cmd_abstraction/autogenerated_interfaces.py")]
script_info['output_description']= ""
script_info['required_options'] = [
 make_option('-i','--input_dir',type="existing_dirpath",help='the input script directory'),
 make_option('-s','--script_names',type="string",help='the script names'),
 make_option('-o','--output_dir',type="new_dirpath",help='the output script directory'),
 make_option('-f','--output_fp',type="new_filepath",help='the output interfaces file'),
]
script_info['optional_options'] = [
]
script_info['version'] = __version__

_interfaces_header_block = """
#!/usr/bin/env python
from __future__ import division

from cmd_abstraction.util import (QiimeCommand)

__author__ = "Greg Caporaso"
__copyright__ = "Copyright 2011, The QIIME project"
__credits__ = %s
__license__ = "GPL"
__version__ = "1.5.0-dev"
__maintainer__ = "Greg Caporaso"
__email__ = "gregcaporaso@gmail.com"
__status__ = "Development"
""" % str(__credits__) 
# everyone in the credits on the auto-generator code gets 
# credit on the interfaces files. the credit/maintainer on the 
# script file stays the same. 

_script_header_block = """#!/usr/bin/env python
from __future__ import division

__author__ = "%s"
__copyright__ = "%s"
__credits__ = %s
__license__ = "%s"
__version__ = "%s"
__maintainer__ = "%s"
__email__ = "%s"
__status__ = "%s"

from cmd_abstraction.util import cmd_main
from cmd_abstraction.autogenerated_interfaces import %s
from sys import argv

cmd = %s()
# script info is locally accessible for backward 
# compatibility
script_info = cmd.getScriptInfo()
if __name__ == "__main__":
    # however we only actually call the command
    # if this script is being accessed directly
    cmd_main(cmd,argv)
"""

_class_definition = """

class %s(QiimeCommand):
    \"\"\"class defining %s script interface\"\"\"
%s
"""

def get_class_name(script_name):
    return script_name.replace('_',' ').title().replace(' ','')

def format_new_script(script_name):
    module = __import__(script_name,globals(),locals())
    class_name = get_class_name(script_name)
    result = _script_header_block % (module.__author__,
                                      module.__copyright__.replace('2011','2012'),
                                      module.__credits__,
                                      module.__license__,
                                      module.__version__,
                                      module.__maintainer__,
                                      module.__email__,
                                      module.__status__,
                                      class_name,
                                      class_name)
    return result

def ignore_line(line):
    bad_prefixes = ['__author__', '__copyright__', '__credits__',
                    '__license__', '__version__', '__maintainer__',
                    '__email__', '__status__','#!/usr/bin/env',
                    '# File created on','option_parser, opts, args',
                    'from __future__ import division','script_info={}']
    stripped_line = line.strip()
    if stripped_line:
        for p in bad_prefixes:
            if stripped_line.startswith(p):
                return True
    return False

def transform_line(line):
    if line.strip() == 'def main():':
        return 'def run_command(self,opts,args):\n'
        
    # replace of script_info['x'] with _x
    m = re.match(r".*script_info\[\'(?P<si_entry>\w+)\'\]", line)
    if m:
        si_entry = m.groupdict()['si_entry']
        line = line.replace('script_info["%s"]' % si_entry, "_%s" % si_entry)
        line = line.replace("script_info['%s']" % si_entry, "_%s" % si_entry)
        return line
    
    m = re.match(r".*opts\.(?P<param_id>\w+)", line)
    if m:
        param_id = m.groupdict()['param_id']
        line = line.replace('opts.%s' % param_id, "opts['%s']" % param_id)
        return line
        
    return line

def format_interface(script_name, input_script_fp):
    class_name = get_class_name(script_name)
    code_lines = []
    for line in open(input_script_fp,'U'):
        if 'if __name__ ==' in line:
            break
        elif ignore_line(line):
            continue
        else:
            line = transform_line(line)
            code_lines.append('    %s' % line)
    
    result = _class_definition % (class_name,script_name,''.join(code_lines))
    return result
            
def main():
    option_parser, opts, args =\
       parse_command_line_parameters(**script_info)
    script_names = opts.script_names.split(',')
    addsitedir(opts.input_dir)
    create_dir(opts.output_dir)
    interfaces_f = open(opts.output_fp,'w')
    interfaces_f.write(_interfaces_header_block)
    for script_name in script_names:
        output_script_fp = join(opts.output_dir,'%s.py' % script_name)
        output_script_f = open(output_script_fp,'w')
        output_script_f.write(format_new_script(script_name))
        output_script_f.close()
        
        input_script_fp = join(opts.input_dir,'%s.py' % script_name)
        interfaces_f.write(format_interface(script_name, input_script_fp))
        interfaces_f.write('\n\n')
    interfaces_f.close()

if __name__ == "__main__":
    main()