'''
Converts file of assembly code to file of virtual machine code
'''

import sys
import argparse
from pprint import pprint

from isa import isa_inv

parser = argparse.ArgumentParser(description='Convert assembly code to machine code')
parser.add_argument('file', nargs='?', default=sys.argv[1], help='input file')
parser.add_argument('-o', '--output', default='a.out', help='output file')
args = parser.parse_args()

# open the file
with open(args.file, 'r') as f:
    lines = f.readlines()

# for each line, convert it to machine code
instructions = []
for line in lines:
    #   ignore comments and blank lines
    line = line.strip()
    if line.startswith(';') or line == '':  #   comments
        continue
    if ';' in line: #   remove trailing comments
        line = line.split(';')[0].strip()
    parts = line.split(' ')

    #   build instruction
    op, vx, vy = 0, 0, 0
    op_byte, x_byte, y_byte = 0x00, 0x00, 0x00
    #   #   get op byte
    op_name = parts[0]    
    op = isa_inv.get(op_name, None)
    if op is None:
        raise ValueError('Invalid operation name: ' + op_name)
    #   #   fetch arg bytes
    if len(parts) == 2:
        _op_, vx = parts
    elif len(parts) == 3:
        _op_, vx, vy = parts
    #   #   assemble instruction
    op_byte = op & 0xff
    x_byte = int(vx) & 0xff
    y_byte = int(vy) & 0xff
    instructions.extend([op_byte, x_byte, y_byte])

# write the file
with open(args.output, 'wb') as f:
    f.write(bytes(instructions))
