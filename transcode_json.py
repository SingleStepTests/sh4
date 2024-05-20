#!/usr/bin/python3
import os
import glob
import json
from struct import unpack_from
from typing import Dict, Any

SH4_JSON_PATH = os.path.expanduser('~') + '/dev/sh4_json/'
NUMTESTS = 500

def load_state(buf, ptr) -> (int, Any):
    full_sz = unpack_from('i', buf, ptr)[0]
    state = {'R': [], 'R_': [], 'FP0': [], 'FP1': []}
    ptr += 8
    values = unpack_from('I' * 68, buf, ptr)

    # R0-R15   16
    for i in range(0, 16):
        state['R'].append(values[i])
    # R_0-R_7  8
    for i in range(0, 8):
        state['R_'].append(values[i+16])
    # FP bank 0 (16 32-bit registers) 16 +24
    for i in range(0, 16):
        state['FP0'].append(values[i+24])
    # FP bank 1  16 +40
    for i in range(0, 16):
        state['FP1'].append(values[i+40])
    # PC 56
    state['PC'] = values[56]
    # GBR 57
    state['GBR'] = values[57]
    # SR 58
    state['SR'] = values[58]
    # SSR
    state['SSR'] = values[59]
    # SPC
    state['SPC'] = values[60]
    # VBR
    state['VBR'] = values[61]
    # SGR
    state['SGR'] = values[62]
    # DBR
    state['DBR'] = values[63]
    # MACL
    state['MACL'] = values[64]
    # MACH
    state['MACH'] = values[65]
    # PR
    state['PR'] = values[66]
    # FPSCR
    state['FPSCR'] = values[67]
    return full_sz, state

def load_cycles(buf, ptr) -> (int, Dict):
    cycles = []
    full_sz = unpack_from('i', buf, ptr)[0]
    ptr += 12
    for i in range(0, 4):
        values = unpack_from('IQQQQQQ', buf, ptr)
        ptr += 52
        cycles.append({
            'actions': values[0],
            'fetch_addr': values[1],
            'fetch_val': values[2],
            'write_addr': values[3],
            'write_val': values[4],
            'read_addr': values[5],
            'read_val': values[6]
        })


    return full_sz, cycles

def load_opcodes(buf, ptr):
    full_sz = unpack_from('i', buf, ptr)[0]
    opcodes = []
    ptr += 8
    values = unpack_from('IIIII', buf, ptr)
    return full_sz, list(values)

def decode_test(buf, ptr) -> (int, Dict):
    full_sz = unpack_from('i', buf, ptr)[0]
    ptr += 4
    test = {}
    sz, test['initial'] = load_state(buf, ptr)
    ptr += sz
    sz, test['final'] = load_state(buf, ptr)
    ptr += sz
    sz, test['cycles'] = load_cycles(buf, ptr)
    ptr += sz
    sz, test['opcodes'] = load_opcodes(buf, ptr)
    ptr += sz


    return full_sz, test



def decode_file(infilename, outfilename):
    with open(infilename, 'rb') as infile:
        content = infile.read()
    ptr = 0
    tests = []
    for i in range(0, NUMTESTS):
        sz, test = decode_test(content, ptr)
        ptr += sz
        tests.append(test)
    if os.path.exists(outfilename):
        os.unlink(outfilename)
    with open(outfilename, 'w') as outfile:
        outfile.write(json.dumps(tests, indent=2))


def main():
    fs = glob.glob(SH4_JSON_PATH + '**.json.bin')
    for fname in fs:
        decode_file(fname, fname[:-4])

if __name__ == '__main__':
    main()